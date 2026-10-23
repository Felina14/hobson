"""One game: a generated world, a ledger, and the turn loop shared by the CLI and the web view.

Nothing about the story is authored. Nova invents the setting from the player's premise and
writes every scene; Decider makes the calls. Per turn:

  1. Nova Lite extracts the claims and holdings the action relies on.
  2. Decider, on the ledger alone: is each claim established? does the player hold each item?
     With the action: which kind of action is this? (the policy dice, fixed categories)
  3. Nova Lite proposes 4 candidate outcomes for this action in this state; impossible attempts are a dice category, not an outcome.
  4. Decider picks the outcome; any `requires` condition on it is checked against the ledger.
  5. The outcome's danger routes the writer (0-2 Nova Lite, 3-5 Nova Pro). Two drafts.
  6. Decider reads each draft against the ledger and the ruling (continuity). A contradicting
     draft is dropped; if both contradict, Nova rewrites once. The editor picks between what's left.
  7. The paragraph's new facts (and the outcome's) go into the ledger. A `moves_to` outcome
     makes Nova write the next scene.
Anything Decider is unsure about (confidence < 0.6) is re-made by Nova Lite and marked so."""
from __future__ import annotations

import json
import random
import time
from dataclasses import asdict
from pathlib import Path

from .handlers import Continuity, Decision, Dice, Editor, Ledger, Ruling, ask_batch, load_questions
from .handlers.continuity import checks_for
from .narrator import Narrator
from .state import ROOT, Ledger as LedgerState, Turn, state_text

RESULTS = ROOT / "results"
NEEDS_CLAIMS = {"bluff", "talk", "use", "take", "other"}


def route_tier(danger: float) -> str:
    return "lite" if round(danger) <= 2 else "pro"


class Game:
    def __init__(self, referee="decider", seed=7, premise="", run_name=None):
        self.mode, self.seed, self.premise = referee, seed, premise
        self.rng = random.Random(seed)
        self.q = load_questions()
        self.narrator = Narrator()
        self.narrator.start_turn()
        if referee == "decider":
            self.dice, self.ledger_h, self.ruling, self.editor, self.continuity = (
                Dice(self.q), Ledger(self.q), Ruling(self.q), Editor(self.q), Continuity(self.q))
        else:
            from .referee_nova import NovaReferee
            self.referee = NovaReferee(self.narrator, self.q)
        self.world = None
        self.scene = None
        self.ledger = LedgerState()
        self.turns: list[Turn] = []
        self.alert = ""
        self.over = False
        self.run = run_name or f"hobson_{referee}_s{seed}_{time.strftime('%Y%m%d-%H%M%S')}"
        RESULTS.mkdir(exist_ok=True)
        self.rows_path = RESULTS / f"referee_{referee}_{seed}.jsonl"

    # -- scenes ---------------------------------------------------------------------------
    def begin(self) -> str:
        self.world, scene = self.narrator.make_world(self.premise)
        self.ledger.add(*self.world.established)
        return self._enter(scene)

    def _enter(self, scene) -> str:
        self.scene = scene
        self.ledger.add(*scene.established)
        return self.narrator.opening(self.world, self.scene, self.ledger)

    # -- one turn -------------------------------------------------------------------------
    def turn(self, action: str, on_rulings=None, on_drafts=None) -> dict:
        n = self.narrator
        n.start_turn()
        scene = self.scene
        state = state_text(self.world, scene, self.ledger, action, self.alert)
        lstate = state_text(self.world, scene, self.ledger, None, self.alert)   # ends at the ledger
        claims, holdings = n.extract_claims(action, self.ledger)
        decider_ms = 0.0

        # calls A (ledger alone: claims, holdings) and B (with the action: the policy dice)
        if self.mode == "decider":
            dA, msA, _ = ask_batch(lstate, [(self.ledger_h, {"claims": claims, "holdings": holdings})])
            dB, msB, _ = ask_batch(state, [(self.dice, {})])
            decider_ms += msA + msB
            n.fallback_many([(d, lstate) for d in dA if d.unsure] + [(d, state) for d in dB if d.unsure])
            d1 = dB + dA
        else:
            d1, _ = self.referee.call1(state, claims, self.q["dice"]["options"])
            # the Nova referee also answers holdings in call2; keep parity by asking here
            d1 += self.referee.holdings(lstate, holdings)
        dice = next(d for d in d1 if d.name == "dice")
        atype = dice.value
        claim_lines = [f'- "{d.detail}": {"established" if d.value else "NOT established"}' for d in d1 if d.name == "ledger"]
        claim_lines += [f'- the player {"does" if d.value else "does NOT"} hold {d.detail}' for d in d1 if d.name == "grounds"]

        # the outcome is decided on a state that also carries the claim rulings
        ostate = state + ("\n\nRULINGS SO FAR (decided against the ledger):\n" + "\n".join(claim_lines) if claim_lines else "")
        # what Nova is told the player did: the player's words, plus what the ledger says is not so.
        # Without this both Nova Lite (candidates) and Nova Pro (prose) keep anchoring on the words
        # ("the brass key does not fit") even after the ruling says there is no key.
        missing = [d.detail for d in d1 if d.name == "grounds" and not d.value and d.via == "decider"]
        false_c = [d.detail for d in d1 if d.name == "ledger" and not d.value and d.via == "decider"]
        if missing or false_c:
            note = "(NOTE from the referee: "
            if missing: note += "the player does NOT have: " + "; ".join(missing) + ". "
            if false_c: note += "Not established, so false: " + "; ".join(false_c) + ". "
            note += "The player only believes or pretends these; nothing of them exists in the story.)"
            action_for_nova = f"{action}\n{note}"
            state = state_text(self.world, scene, self.ledger, action_for_nova, self.alert)
            ostate = state + "\n\nRULINGS SO FAR (decided against the ledger):\n" + "\n".join(claim_lines)
        else:
            action_for_nova = action
        # call C: Nova proposes the candidates, Decider picks (impossible needs no proposal)
        if atype == "impossible":
            prepared = {"not-possible-here": {"effect": "That cannot be done here or with what the player holds; the attempt fails.", "danger": 0, "goto": None, "requires": None, "adds": []}}
        else:
            prepared = n.propose_outcomes(state, atype, claim_lines)
        outcomes = {k: v["effect"] for k, v in prepared.items()}
        requires = {k: v["requires"] for k, v in prepared.items() if v.get("requires")}
        if len(outcomes) == 1:
            label = next(iter(outcomes))
            d2 = [Decision("outcome", label, {label: 1.0}, None, False, 0.0, via="dice",
                           kind="choice", question="", options=outcomes)]
        elif self.mode == "decider":
            parts = [(self.ruling, {"parts": ("outcome",), "outcomes": outcomes})]
            d2, msC, _ = ask_batch(ostate, parts)
            decider_ms += msC
            if requires:
                dR, msR, _ = ask_batch(lstate, [(self.ruling, {"parts": ("requires",), "requires": requires})])
                decider_ms += msR; d2 += dR
            n.fallback_many([(d, ostate if d.name == "outcome" else lstate) for d in d2 if d.unsure])
        else:
            d2, _ = self.referee.call2(ostate, outcomes, requires, [])
        ask_for = self.q["grounding"].get("ask_for", [])
        decisions = [d for d in d1 + d2 if not (d.name == "grounds" and atype not in ask_for)]
        outcome = next(d for d in d2 if d.name == "outcome")

        # resolve the ruling into an effect the writer must honour
        o = prepared[outcome.value]
        req = next((d for d in decisions if d.name == "requires" and d.detail == outcome.value), None)
        met = req is None or bool(req.value)
        if not met:
            effect, goto, adds = f"The condition is not met ({o['requires']}); it does not happen.", None, []
        else:
            effect, goto, adds = o["effect"], o.get("goto"), o.get("adds", [])
        dval = int(o.get("danger", 0)) if met else 0
        # contested: the ruling says no to something the player asserted. The writer has to push
        # back against the player's own words, which Nova Lite does badly; use the stronger writer.
        contested = (not met) or any(not d.value for d in decisions if d.name in ("ledger", "grounds"))
        tier = "pro" if contested else route_tier(dval)
        route_why = ("contested ruling: the stronger writer" if contested and round(dval) <= 2
                     else f"danger {dval}: {'high stakes, the stronger writer' if tier == 'pro' else 'low stakes, the faster one'}")

        brief = self._brief(atype, decisions, outcome.value, effect, dval, met, o)
        if on_rulings:
            on_rulings(decisions, {"tier": tier, "danger": dval, "atype": atype, "decider_ms": decider_ms,
                                   "route_why": route_why, "contested": contested})

        # two drafts; the continuity guard reads each against the ledger; the editor picks
        drafts = n.drafts(tier, self.world, scene, self.ledger, action_for_nova, brief)
        if self.rng.random() < 0.5:
            drafts.reverse()
        context = state + "\n\nRULINGS:\n" + brief
        clist = checks_for(decisions, met, o)
        checks, rewrites = [], 0
        for i, (p, _) in enumerate(drafts):
            c = self._check(lstate, clist, p, "AB"[i])
            checks.append(c)
        decider_ms += sum(c.latency_ms for c in checks if c.via == "decider")
        bad = [i for i, c in enumerate(checks) if c.value]            # True = contradicts
        problem = self._problem(decisions, met, o)
        while len(bad) == 2 and rewrites < 2:
            rewrites += 1
            fixed = n.drafts("pro", self.world, scene, self.ledger, action_for_nova, brief, n_drafts=1,
                             problem=f"both drafts broke the ledger. {problem}")[0]
            drafts = [fixed, drafts[0]]
            c = self._check(lstate, clist, fixed[0], "A"); checks = [c, checks[0]]
            decider_ms += c.latency_ms if c.via == "decider" else 0
            bad = [i for i, c in enumerate(checks) if c.value]
        if len(bad) == 1:
            keep = 1 - bad[0]
            pa, fa = drafts[keep]; pb, fb = drafts[bad[0]]
            ed = Decision("editor", "A", {"A": 1.0, "B": 0.0}, None, False, 0.0, via="continuity",
                          detail="the other draft contradicted the ledger", kind="choice",
                          question=self.q["editor"]["question"], options={"A": "Draft A", "B": "Draft B"})
            drafts = [(pa, fa), (pb, fb)]
            checks = [checks[keep], checks[bad[0]]]          # keep the checks aligned with the drafts
        else:
            (pa, fa), (pb, fb) = drafts
            if self.mode == "decider":
                ed = self.editor.decide(context, pa, pb)
                decider_ms += ed.latency_ms
            else:
                ed = self.referee.editor(context, pa, pb)
        paragraph, facts = (pa, fa) if ed.value == "A" else (pb, fb)
        # one continuity row for the page: about the paragraph that was kept
        kept = checks[0 if ed.value == "A" else 1]
        still_bad = bool(kept.value)
        what = ", ".join((kept.decider_value or {}).get("broke", [])) if isinstance(kept.decider_value, dict) else ""
        kept.detail = (f"still breaks {what or 'a rule'} after {rewrites} rewrites; its facts were NOT recorded" if still_bad
                       else (f"rewritten {'once' if rewrites == 1 else 'twice'}" if rewrites
                             else ("the other draft was dropped" if len(bad) == 1 else "")))
        decisions = decisions + [kept]
        if on_drafts:
            on_drafts({"A": pa, "B": pb}, ed)

        # the ledger only learns from prose the guard accepted; the outcome's own facts always count
        new = self.ledger.add(*adds, *([] if still_bad else facts))
        self.alert = self.world.trouble_arrives if dval >= 4 else ""
        opening = ""
        if goto:
            scene_new = n.make_scene(self.world, goto, self.ledger, effect)
            opening = self._enter(scene_new)

        t = Turn(n=len(self.turns) + 1, scene=scene.name, action=action,
                 rulings=[d.row() for d in decisions + [ed]], drafts={"A": pa, "B": pb}, picked=ed.value,
                 paragraph=paragraph, new_facts=new, narrator=tier, danger=dval, decider_ms=decider_ms,
                 nova_rulings_ms=n.ruling_ms, nova_narration_ms=n.narration_ms,
                 tokens={k: dict(v) for k, v in n.meter.tok.items()}, cost_usd=n.meter.cost,
                 ruling_cost_usd=n.meter.ruling_cost, rewrites=rewrites)
        self.turns.append(t)
        self._write_row(t, effect, goto, outcomes)
        return {"turn": t, "decisions": decisions, "editor": ed, "effect": effect, "goto": goto,
                "opening": opening, "ends": False, "scene": self.scene.name, "ledger": list(self.ledger.facts),
                "candidates": outcomes}

    def _check(self, lstate, clist, paragraph, which):
        if self.mode == "decider":
            c = self.continuity.decide(lstate, checks=clist, paragraph=paragraph,
                                       fallback=lambda d, text: self.narrator.fallback_ruling(d, text))
        else:
            c = self.referee.continuity(lstate, clist, paragraph)
        c.question = f"draft {which}: " + c.question
        return c

    def _problem(self, decisions, met, o):
        parts = [f'the claim "{d.detail}" is NOT established, so it is false' for d in decisions if d.name == "ledger" and not d.value]
        parts += [f"the player does NOT hold {d.detail}" for d in decisions if d.name == "grounds" and not d.value]
        if not met:
            parts.append(f"the condition '{o.get('requires')}' is not met, so the outcome does NOT happen")
        return "; ".join(parts) or "a paragraph contradicted the ledger or the ruling"

    def _brief(self, atype, decisions, outcome, effect, danger, met=True, o=None):
        lines = [f"- Action type: {atype}.",
                 f"- Outcome ({outcome}): {effect}",
                 f"- Danger: {danger} of 5."]
        if not met and o:
            lines.append(f"- The attempt FAILS. Do not show it succeeding in any form. Not: {o.get('effect')}")
        for d in decisions:
            if d.name == "ledger":
                lines.append(f"- Claim \"{d.detail}\": {'established' if d.value else 'NOT established; it is not true'}.")
            elif d.name == "grounds":
                lines.append(f"- The player {'does' if d.value else 'does NOT'} hold {d.detail}.")
        if self.alert:
            lines.append(f"- {self.alert}")
        return "\n".join(lines)

    def _write_row(self, t: Turn, effect, goto, candidates):
        row = {"run": self.run, "mode": self.mode, "seed": self.seed, "premise": self.world.premise,
               "ts": time.time(), **asdict(t), "effect": effect, "goto": goto, "candidates": candidates}
        with self.rows_path.open("a") as f:
            f.write(json.dumps(row, default=str) + "\n")

    # -- the end --------------------------------------------------------------------------
    def summary_lines(self) -> list[str]:
        L = [f"{'#':>2} {'scene':14} {'dice':10} {'outcome':24} {'dgr':>3} {'nar':4} {'cont':4} {'dec ms':>7} "
             f"{'nova ms':>8} {'$':>8}"]
        for t in self.turns:
            r = {x["name"]: x for x in t.rulings}
            dice = str(r["dice"]["value"]) + ("*" if r["dice"]["via"] == "nova" and self.mode == "decider" else "")
            cont = "fix" if t.rewrites else ("swap" if r.get("continuity", {}).get("detail") else "ok")
            L.append(f"{t.n:>2} {t.scene[:14]:14} {dice[:10]:10} {str(r['outcome']['value'])[:24]:24} "
                     f"{t.danger:>3} {t.narrator:4} {cont:4} {t.decider_ms:7.0f} "
                     f"{t.nova_rulings_ms + t.nova_narration_ms:8.0f} {t.cost_usd:8.5f}")
        L.append("")
        L.append(f"premise: {self.world.premise}")
        L.append(self.referee_line())
        if self.mode == "decider":
            L.append("* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite")
        return L

    def referee_line(self) -> str:
        n = len(self.turns) or 1
        dec = sum(t.decider_ms for t in self.turns)
        nr = sum(t.nova_rulings_ms for t in self.turns)
        unsure = sum(1 for t in self.turns for r in t.rulings if r["unsure"])
        caught = sum(1 for t in self.turns for r in t.rulings if r["name"] == "continuity" and r["detail"])
        cost = self.narrator.total.cost
        who = "Decider 2B (local, MPS)" if self.mode == "decider" else "Nova Lite"
        return (f"referee {who} · {len(self.turns)} turns · rulings {dec / n:.0f} ms Decider + "
                f"{nr / n:.0f} ms Nova per turn · {unsure} unsure · {caught} paragraphs caught by the continuity guard · Nova ${cost:.4f} total")

    def finish(self, args: dict) -> Path:
        from .mdlog import finish_run
        return finish_run(self.run, f"Hobson run: referee {self.mode}, seed {self.seed}", args,
                          self.summary_lines(), self.rows_path,
                          notes="Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.")
