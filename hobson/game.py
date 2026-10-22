"""One game: scene, ledger, and the turn loop shared by the CLI and the web view.

Per turn: Nova Lite extracts claims -> Decider call A on the ledger alone (claims, holdings,
outcome conditions) -> call B with the action (dice over the scene's actions) -> call C (the
outcome, from the picked action's group; `impossible` goes straight to not-possible-here) -> Nova Lite re-makes
anything unsure -> the outcome's authored danger routes the narrator (0-2 Lite, 3-5 Pro) ->
two drafts -> the editor scores each (pointwise) and checks with an A/B swap -> ledger."""
from __future__ import annotations

import json
import random
import time
from dataclasses import asdict
from pathlib import Path

from .handlers import Decision, Dice, Editor, Ledger, Ruling, ask_batch, load_questions
from .narrator import Narrator
from .state import ACTION_TYPES, ROOT, Ledger as LedgerState, Turn, World, state_text

RESULTS = ROOT / "results"


def route_tier(danger: float) -> str:
    return "lite" if round(danger) <= 2 else "pro"


class Game:
    def __init__(self, referee="decider", seed=7, world_path=None, run_name=None, dice="actions"):
        self.mode, self.seed, self.dice_mode = referee, seed, dice
        self.rng = random.Random(seed)
        self.q = load_questions()
        self.world = World.load(world_path) if world_path else World.load()
        self.narrator = Narrator()
        self.narrator.start_turn()
        if referee == "decider":
            self.dice, self.ledger_h, self.ruling, self.editor = (
                Dice(self.q), Ledger(self.q), Ruling(self.q), Editor(self.q))
        else:
            from .referee_nova import NovaReferee
            self.referee = NovaReferee(self.narrator, self.q)
        self.ledger = LedgerState(list(self.world.established))
        self.scene = None
        self.turns: list[Turn] = []
        self.alert = ""
        self.over = False
        tag = "" if dice == "actions" else f"_{dice}"
        self.run = run_name or f"hobson_{referee}{tag}_s{seed}_{time.strftime('%Y%m%d-%H%M%S')}"
        RESULTS.mkdir(exist_ok=True)
        self.rows_path = RESULTS / f"referee_{referee}{tag}_{seed}.jsonl"

    # -- scenes ---------------------------------------------------------------------------
    def enter(self, name: str) -> str:
        self.scene = self.world.scenes[name]
        self.ledger.add(*self.scene.established)
        gaps = [t for t in ACTION_TYPES if not self.scene.outcomes.get(t)]
        for t, opts in self.narrator.prepare_outcomes(self.scene, gaps).items():
            if opts:
                self.scene.outcomes[t] = opts
        return self.narrator.opening(self.world, self.scene, self.ledger)

    def begin(self) -> str:
        return self.enter(self.world.start)

    # -- one turn -------------------------------------------------------------------------
    def turn(self, action: str, on_rulings=None, on_drafts=None) -> dict:
        n = self.narrator
        n.start_turn()
        scene = self.scene
        state = state_text(self.world, scene, self.ledger, action, self.alert)
        lstate = state_text(self.world, scene, self.ledger, None, self.alert)   # ends at the ledger
        claims, holdings = n.extract_claims(action, self.ledger)
        # every conditional outcome in this scene, so conditions can be asked before the dice
        requires = {k: v["requires"] for opts in scene.outcomes.values() for k, v in opts.items() if v.get("requires")}
        decider_ms = 0.0

        actions = ({k: v["says"] for k, v in scene.actions.items()}
                   if self.dice_mode == "actions" and scene.actions else None)
        dice_opts = actions or self.q["dice_categories"]["options"]

        if self.mode == "decider":
            # call A, the ledger alone: claims, holdings, outcome conditions
            dA, msA, _ = ask_batch(lstate, [(self.ledger_h, {"claims": claims, "holdings": holdings}),
                                            (self.ruling, {"parts": ("requires",), "requires": requires})])
            # call B, with the action: the dice
            dB, msB, _ = ask_batch(state, [(self.dice, {"actions": actions})])
            decider_ms += msA + msB
            n.fallback_many([(d, lstate) for d in dA if d.unsure] + [(d, state) for d in dB if d.unsure])
            d1 = dB + dA
        else:
            d1, _ = self.referee.call1(state, claims, dice_opts)
        dice = next(d for d in d1 if d.name == "dice")
        atype = scene.actions[dice.value]["type"] if actions else dice.value

        # call C: the outcome, from the picked action's group
        prepared = scene.options_for(atype, self.world.default_outcomes, self.world.not_possible)
        outcomes = {k: v["effect"] for k, v in prepared.items()}
        if len(outcomes) == 1:
            # a one-outcome group (`impossible`): the dice already decided it, nothing to ask
            label = next(iter(outcomes))
            d2 = [Decision("outcome", label, {label: 1.0}, None, False, 0.0, via="dice",
                           kind="choice", question="", options=outcomes)]
        elif self.mode == "decider":
            d2, msC, _ = ask_batch(state, [(self.ruling, {"parts": ("outcome",), "outcomes": outcomes})])
            decider_ms += msC
            n.fallback_many([(d, state) for d in d2 if d.unsure])
        else:
            req_here = {k: v for k, v in requires.items() if k in prepared}
            d2, _ = self.referee.call2(state, outcomes, req_here, holdings)
        # grounding is shown only for the action types it applies to
        ask_for = self.q["grounding"].get("ask_for", [])
        decisions = [d for d in d1 + d2 if not (d.name == "grounds" and atype not in ask_for)]
        outcome = next(d for d in d2 if d.name == "outcome")

        # resolve the ruling into an effect the narrator must honour
        o = prepared[outcome.value]
        req = next((d for d in decisions if d.name == "requires" and d.detail == outcome.value), None)
        met = req is None or bool(req.value)
        if not met:
            effect, goto, adds, ends = o.get("otherwise", "The condition is not met; it does not happen."), None, [], False
        else:
            effect, goto, adds, ends = o["effect"], o.get("goto"), o.get("adds", []), bool(o.get("ends"))
        # danger is authored on the outcome, not asked (see README, "why danger is authored")
        dval = int(o.get("danger", 0)) if met else 0
        tier = route_tier(dval)

        brief = self._brief(atype, decisions, outcome.value, effect, dval)
        if on_rulings:
            on_rulings(decisions, {"tier": tier, "danger": dval, "atype": atype, "decider_ms": decider_ms})

        # two drafts, the editor picks
        drafts = n.drafts(tier, self.world, scene, self.ledger, action, brief)
        if self.rng.random() < 0.5:           # seed decides which draft is labelled A
            drafts.reverse()
        (pa, fa), (pb, fb) = drafts
        context = state + "\n\nRULINGS:\n" + brief
        if self.mode == "decider":
            ed = self.editor.decide(context, pa, pb)
            decider_ms += ed.latency_ms
        else:
            ed = self.referee.editor(context, pa, pb)
        paragraph, facts = (pa, fa) if ed.value == "A" else (pb, fb)
        if on_drafts:
            on_drafts({"A": pa, "B": pb}, ed)

        new = self.ledger.add(*adds, *facts)
        self.alert = self.world.guards_arrive if dval >= 4 else ""
        opening = ""
        if ends:
            self.over = True
        elif goto and goto in self.world.scenes:
            opening = self.enter(goto)

        t = Turn(n=len(self.turns) + 1, scene=scene.name, action=action,
                 rulings=[d.row() for d in decisions + [ed]], drafts={"A": pa, "B": pb}, picked=ed.value,
                 paragraph=paragraph, new_facts=new, narrator=tier, danger=dval, decider_ms=decider_ms,
                 nova_rulings_ms=n.ruling_ms, nova_narration_ms=n.narration_ms,
                 tokens={k: dict(v) for k, v in n.meter.tok.items()}, cost_usd=n.meter.cost,
                 ruling_cost_usd=n.meter.ruling_cost)
        self.turns.append(t)
        self._write_row(t, effect, goto)
        return {"turn": t, "decisions": decisions, "editor": ed, "effect": effect, "goto": goto,
                "opening": opening, "ends": ends, "scene": self.scene.name, "ledger": list(self.ledger.facts)}

    def _brief(self, atype, decisions, outcome, effect, danger):
        lines = [f"- Action type: {atype}.",
                 f"- Outcome ({outcome}): {effect}",
                 f"- Danger: {danger} of 5."]
        for d in decisions:
            if d.name == "ledger":
                lines.append(f"- Claim \"{d.detail}\": {'established' if d.value else 'NOT established; it is not true'}.")
            elif d.name == "grounds":
                lines.append(f"- The player {'does' if d.value else 'does NOT'} hold {d.detail}.")
        if self.alert:
            lines.append(f"- {self.alert}")
        return "\n".join(lines)

    def _write_row(self, t: Turn, effect, goto):
        row = {"run": self.run, "mode": self.mode, "seed": self.seed, "ts": time.time(), **asdict(t),
               "effect": effect, "goto": goto}
        with self.rows_path.open("a") as f:
            f.write(json.dumps(row, default=str) + "\n")

    # -- the end --------------------------------------------------------------------------
    def summary_lines(self) -> list[str]:
        L = [f"{'#':>2} {'scene':7} {'dice':14} {'outcome':22} {'dgr':>3} {'nar':4} {'dec ms':>7} "
             f"{'nova ms':>8} {'$':>8}"]
        for t in self.turns:
            r = {x["name"]: x for x in t.rulings}
            dice = str(r["dice"]["value"]) + ("*" if r["dice"]["via"] == "nova" and self.mode == "decider" else "")
            L.append(f"{t.n:>2} {t.scene:7} {dice[:14]:14} {str(r['outcome']['value'])[:22]:22} "
                     f"{t.danger:>3} {t.narrator:4} {t.decider_ms:7.0f} "
                     f"{t.nova_rulings_ms + t.nova_narration_ms:8.0f} {t.cost_usd:8.5f}")
        L.append("")
        L.append(self.referee_line())
        if self.mode == "decider":
            L.append("* = Decider unsure (confidence < threshold), re-made by Nova Lite")
        return L

    def referee_line(self) -> str:
        n = len(self.turns) or 1
        dec = sum(t.decider_ms for t in self.turns)
        nr = sum(t.nova_rulings_ms for t in self.turns)
        unsure = sum(1 for t in self.turns for r in t.rulings if r["unsure"])
        cost = self.narrator.total.cost
        who = "Decider 2B (local, MPS)" if self.mode == "decider" else "Nova Lite"
        return (f"referee {who} · {len(self.turns)} turns · rulings {dec / n:.0f} ms Decider + "
                f"{nr / n:.0f} ms Nova per turn · {unsure} unsure · Nova ${cost:.4f} total")

    def finish(self, args: dict) -> Path:
        from .mdlog import finish_run
        return finish_run(self.run, f"Hobson run: referee {self.mode}, seed {self.seed}", args,
                          self.summary_lines(), self.rows_path,
                          notes="Every ruling, draft and timing is in the rows file, one JSON line per turn.")
