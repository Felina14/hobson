"""Nova, the writer. Scene openings, two drafts per turn, claim extraction, and the fallback
rulings for anything Decider is unsure of. Bedrock Converse only; Nova Lite and Nova Pro only."""
from __future__ import annotations

import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import boto3

from .base import timed
from .nova import MODELS, NovaAdapter

# On-demand list prices, USD per 1K tokens, us-east-1. Read from the AWS Price List API
# (service AmazonBedrock, usagetypes USE1-NovaLite-*/USE1-NovaPro-*-tokens) on 2026-10-22.
PRICES = {
    "lite": {"in": 0.00006, "out": 0.00024},
    "pro": {"in": 0.0008, "out": 0.0032},
}
TIERS = ("lite", "pro")

def voice(world) -> str:
    return (f"You narrate a text adventure. Setting: {world.premise}. Second person, present tense, "
            "plain and concrete, a little dry. Stay inside the setting's own logic. Never invent items "
            "the player holds, people they know, or events the rulings do not allow; the LEDGER is the "
            "only record of what is true.")


class Meter:
    """Tokens, milliseconds and dollars per Nova tier, for one turn or a whole run."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.tok = {t: {"in": 0, "out": 0} for t in TIERS}
        self.rtok = {t: {"in": 0, "out": 0} for t in TIERS}     # the part spent on rulings
        self.ms = 0.0

    def add(self, tier, i, o, ms, ruling=False):
        self.tok[tier]["in"] += i; self.tok[tier]["out"] += o; self.ms += ms
        if ruling:
            self.rtok[tier]["in"] += i; self.rtok[tier]["out"] += o

    @staticmethod
    def _cost(tok):
        return sum(tok[t]["in"] / 1000 * PRICES[t]["in"] + tok[t]["out"] / 1000 * PRICES[t]["out"] for t in TIERS)

    @property
    def cost(self):
        return self._cost(self.tok)

    @property
    def ruling_cost(self):
        return self._cost(self.rtok)


class _FallbackNova(NovaAdapter):
    """The gauntlet's constrained-answer adapter, with room for hyphenated outcome labels."""

    def _converse(self, system, user):
        def call():
            return self.client.converse(
                modelId=self.model_id, system=[{"text": system}],
                messages=[{"role": "user", "content": [{"text": user}]}],
                inferenceConfig={"maxTokens": 24, "temperature": 0.0})
        r, ms = timed(call)
        u = r["usage"]
        return r["output"]["message"]["content"][0]["text"].strip(), ms, u["inputTokens"], u["outputTokens"], r


def parse_json(text):
    m = re.search(r"[\[{].*[\]}]", text, re.S)
    if not m:
        raise ValueError(f"no JSON in: {text[:120]!r}")
    return json.loads(m.group(0))


class Narrator:
    def __init__(self, region="us-east-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.meter = Meter()          # per turn; the game resets it
        self.total = Meter()          # whole run
        self.fallback = _FallbackNova("lite", region)
        self._lock = threading.Lock()

    # -- plumbing -------------------------------------------------------------------------
    def converse(self, tier, system, user, temperature=0.0, max_tokens=400, ruling=False):
        t = time.perf_counter()
        r = self.client.converse(
            modelId=MODELS[tier], system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": user}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature})
        ms = (time.perf_counter() - t) * 1000
        u = r["usage"]
        self._count(tier, u["inputTokens"], u["outputTokens"], ms, ruling)
        return r["output"]["message"]["content"][0]["text"].strip(), ms

    def _count(self, tier, i, o, ms, ruling, wall=True):
        with self._lock:
            self.meter.add(tier, i, o, ms, ruling); self.total.add(tier, i, o, ms, ruling)
            if not wall:
                return                    # time accounted for by the caller (parallel calls)
            if ruling:
                self.ruling_ms += ms
            else:
                self.narration_ms += ms

    def start_turn(self):
        self.meter.reset(); self.ruling_ms = 0.0; self.narration_ms = 0.0

    # -- world ----------------------------------------------------------------------------
    def make_world(self, premise: str):
        """Nova Pro invents the setting from the player's premise (or from nothing) and the
        opening facts. Returns (World, Scene). Nothing is read from a file."""
        from .state import RULES, Scene, World
        ask = premise.strip() or "surprise me: any time, any place, no magic unless the premise asks for it"
        user = (f"PREMISE from the player: {ask}\n\n"
                "Design the start of a text adventure for this premise. Return JSON only:\n"
                '{"title": "<4-6 words>", "premise": "<one sentence restating the setting plainly>", '
                '"established": ["<2-3 short facts true at the start: who the player is, what they carry (name amounts), one thing about the place>"], '
                '"trouble": "<one line: what arrives after a very dangerous act in this setting>", '
                '"scene": {"name": "<kebab-case id>", "description": "<2-3 sentences, concrete, present tense>", '
                '"characters": ["<who is here, 1-3>"], "exits": {"<name>": "<where it leads>"}}}')
        text, _ = self.converse("pro", "You design text adventures. Reply with JSON only.", user,
                                temperature=0.8, max_tokens=600)
        d = parse_json(text)
        sc = d.get("scene", {})
        scene = Scene(name=str(sc.get("name", "start")).strip().lower().replace(" ", "-")[:40] or "start",
                      description=str(sc.get("description", "")).strip(), characters=list(sc.get("characters", []))[:3],
                      exits={str(k): str(v) for k, v in (sc.get("exits") or {}).items()},
                      established=[])
        world = World(premise=str(d.get("premise", ask)), title=str(d.get("title", "Hobson")), rules=list(RULES),
                      established=[str(x) for x in d.get("established", [])][:3],
                      trouble_arrives=str(d.get("trouble", "Trouble is arriving, drawn by the violence of the last turn.")))
        return world, scene

    def make_scene(self, world, name: str, ledger, reason: str):
        """A new scene when an outcome moves the player. Nova Lite writes it from the ledger."""
        from .state import Scene
        user = (f"SETTING: {world.premise}\nLEDGER: {'; '.join(ledger.facts)}\n"
                f"The player is now moving to: {name}. Why: {reason}\n"
                "Describe this new place. Return JSON only:\n"
                '{"description": "<2-3 sentences, concrete, present tense>", "characters": ["<0-3>"], '
                '"exits": {"<name>": "<where it leads>"}, "established": ["<0-2 facts true on arrival>"]}')
        text, _ = self.converse("lite", "You design text adventures. Reply with JSON only.", user,
                                temperature=0.7, max_tokens=400)
        try:
            d = parse_json(text)
        except Exception:
            d = {"description": f"You arrive at {name}."}
        return Scene(name=name, description=str(d.get("description", "")).strip(),
                     characters=list(d.get("characters", []))[:3],
                     exits={str(k): str(v) for k, v in (d.get("exits") or {}).items()},
                     established=[str(x) for x in d.get("established", [])][:2])

    def opening(self, world, scene, ledger):
        user = (f"SETTING: {world.premise}\nSCENE: {scene.description}\n"
                f"LEDGER: {'; '.join(ledger.facts)}\n\n"
                "Write the opening of this scene for the player in 60-90 words. End on a moment "
                "that invites an action. Plain prose, no headings.")
        text, _ = self.converse("pro", voice(world), user, temperature=0.7, max_tokens=220)
        return text

    def propose_outcomes(self, state: str, atype: str, claim_lines: list[str], absent=()):
        """Nova Lite proposes 4 candidate outcomes for THIS action in THIS state. Decider picks.
        Each: label, effect (one line, what Decider reads and the writer must honour), danger 0-5,
        optional moves_to (a new place), optional requires (a ledger condition), adds (facts).
        Impossible attempts are not an option here: the dice category `impossible` handles them."""
        cl = ("\n".join(claim_lines) or "(none)")
        gone = ""
        if absent:
            gone = ("\n\nTHESE DO NOT EXIST IN THIS STORY: " + "; ".join(absent) + ".\n"
                    "Every outcome must treat them as simply not there. None of them can fit or fail to fit, "
                    "be empty or full, be found, be dropped, be the wrong one, or be anywhere at all: there is "
                    "nothing to describe. Outcomes say what the player discovers instead, and what follows.")
        user = (f"{state}\n\nACTION TYPE (already decided): {atype}\n"
                f"CLAIM CHECKS (already decided against the ledger):\n{cl}{gone}\n\n"
                "Propose 4 distinct, plausible outcomes of this action, from best to worst for the player. "
                "Stay inside the setting's own realism: no ghosts, magic or new characters unless the ledger "
                "or the premise already has them. Judge strictly from the ledger: a claim marked NOT "
                "established is false and characters treat it so; an action that only needs what the ledger "
                "gives the player should have at least one outcome where it simply works. Return JSON only: "
                '[{"label": "<kebab-case, 2-4 words>", "effect": "<one sentence of what happens>", '
                '"danger": <0-5>, "moves_to": "<kebab-case new place or null>", '
                '"requires": "<a ledger condition this outcome depends on, or null>", '
                '"adds": ["<0-2 short facts this outcome would establish>"]}]')
        text, _ = self.converse("lite", "You design game outcomes. Reply with JSON only.", user,
                                temperature=0.6, max_tokens=600, ruling=True)
        out = {}
        try:
            for i, o in enumerate(parse_json(text)):
                if not isinstance(o, dict) or not o.get("effect"):
                    continue
                label = re.sub(r"[^a-z0-9-]", "-", str(o.get("label") or f"outcome-{i+1}").lower()).strip("-")[:40] or f"outcome-{i+1}"
                while label in out:
                    label += "-2"
                try:
                    danger = max(0, min(5, int(o.get("danger", 0))))
                except Exception:
                    danger = 0
                def clean(v):
                    v = str(v).strip() if v is not None else ""
                    return None if v.lower() in ("", "null", "none", "n/a", "nil", "false", "no") else v
                goto = clean(o.get("moves_to"))
                out[label] = {"effect": str(o["effect"]).strip(), "danger": danger,
                              "goto": (re.sub(r"[^a-z0-9-]", "-", goto.lower()).strip("-")[:40] or None) if goto else None,
                              "requires": clean(o.get("requires")),
                              "adds": [str(a) for a in (o.get("adds") or []) if clean(a)][:2]}
                if len(out) == 4:
                    break
        except Exception:
            pass
        if len(out) < 2:
            out.setdefault("nothing-much-happens", {"effect": "The attempt changes little; the scene carries on and someone notices.", "danger": 0, "goto": None, "requires": None, "adds": []})
            out.setdefault("it-backfires", {"effect": "The attempt goes wrong in a small, awkward way that a character remembers.", "danger": 1, "goto": None, "requires": None, "adds": []})
        return out

    # -- rulings support ------------------------------------------------------------------
    def extract_claims(self, action, ledger):
        """Nova Lite: the claims an action relies on, and any objects/quantities it names."""
        # The ledger is deliberately not shown (given it, Nova lists ledger facts back as claims);
        # few-shot examples keep it from inventing claims for ordinary actions.
        user = ("List what this player ACTION relies on having been established earlier: specific "
                "items the player claims to hold, people they claim to know, past events or promises "
                "they refer to. What the player DOES in this action (setting something down, climbing, "
                "shouting) is not a claim; only what must already be true for it. At most 3 short claims. Ordinary talking, looking, moving or fighting "
                "relies on nothing: []. Also list objects the action names as held, shown, given or "
                "used by the player (not things to take or buy), with any amount.\n\n"
                "ACTION: I ask the guard what the town is called\n"
                '{"claims": [], "holdings": []}\n'
                "ACTION: I give the sergeant the letter from my uncle\n"
                '{"claims": ["the player holds a letter from their uncle", "the player knows the sergeant"], '
                '"holdings": [{"object": "letter from my uncle", "amount": ""}]}\n'
                "ACTION: I pay the innkeeper two silver coins\n"
                '{"claims": ["the player holds two silver coins"], "holdings": [{"object": "silver coins", "amount": "two"}]}\n'
                "ACTION: I run down the lane\n"
                '{"claims": [], "holdings": []}\n'
                "ACTION: I set the lamp down and open the letter\n"
                '{"claims": ["the player holds a lamp", "the player holds a letter"], "holdings": [{"object": "lamp", "amount": ""}, {"object": "letter", "amount": ""}]}\n'
                "ACTION: I climb onto the table and shout for help\n"
                '{"claims": [], "holdings": []}\n'
                f"ACTION: {action}\n")
        text, _ = self.converse("lite", "You extract facts. Reply with JSON only.", user,
                                max_tokens=200, ruling=True)
        try:
            d = parse_json(text)
            claims = [str(c) for c in d.get("claims", [])][:3]
            holdings = [h for h in d.get("holdings", []) if isinstance(h, dict) and h.get("object")][:3]
            return claims, holdings
        except Exception:
            return [], []

    def fallback_many(self, items):
        """Re-make several unsure decisions at once; they are independent, so in parallel.
        `items` is [(decision, state)]. Wall time is what the turn waits for."""
        if not items:
            return
        t = time.perf_counter()
        with ThreadPoolExecutor(max_workers=len(items)) as ex:
            list(ex.map(lambda it: self.fallback_ruling(it[0], it[1], wall=False), items))
        self.ruling_ms += (time.perf_counter() - t) * 1000

    def fallback_ruling(self, decision, state, wall=True):
        """Re-make one unsure Decider decision with Nova Lite (same question, same options)."""
        f = self.fallback
        if decision.kind == "noul":
            r = f.noul(state, decision.question)
            value = r.answer >= 0.5
        elif decision.kind == "choice":
            r = f.choice(state, decision.question, decision.options)
            value = r.answer if r.answer in decision.options else decision.value
        else:
            r = f.score(state, decision.question, decision.options)
            value = decision.value if r.answer != r.answer else r.answer   # NaN -> keep Decider's
        self._count("lite", r.input_tokens, r.output_tokens, r.latency_ms, ruling=True, wall=wall)
        decision.decider_value, decision.value, decision.via = decision.value, value, "nova"
        return decision

    # -- the turn's prose -----------------------------------------------------------------
    def drafts(self, tier, world, scene, ledger, action, brief, n_drafts=2, problem=""):
        """Two drafts of the next paragraph (two Converse calls, temperature 0.8). Each ends
        with a FACTS: block of new established facts. Returns [(paragraph, facts), (..)].
        With `problem` set (Decider found a contradiction), one corrected draft is written."""
        fix = (f"\nA previous draft was rejected because it contradicted the ledger or the rulings: {problem}. "
               "Do not repeat that mistake.") if problem else ""
        user = (f"WORLD RULES: {' '.join(world.rules)}\nSETTING: {world.premise}\nSCENE: {scene.description}\n"
                f"LEDGER (what is true so far): {'; '.join(ledger.facts)}\n"
                f"PLAYER ACTION: {action}\n\nRULINGS YOU MUST HONOUR:\n{brief}\n\n"
                "Write the next beat: one paragraph of 60-100 words showing what happens. The outcome "
                "is fixed: show exactly it, nothing more. The player stays in this scene unless the "
                "outcome moves them. Claims marked NOT established are false: the player does not have "
                "the item, does not know the person, the event never happened; show them finding that out "
                "(an empty pocket, a blank look, a lock that stays shut), never the claim coming true. "
                "If the rulings say the attempt FAILS, nothing of it succeeds. Then a line "
                "'FACTS:' followed by 0-3 bullet facts newly established by this paragraph, each a full "
                "sentence of durable state (what the player now holds or has lost, where they are, what they "
                "have learned or done: 'You have read the letter; it warns of a danger it does not name'). "
                "Write 'FACTS: none' if nothing new. Then a line 'NOW FALSE:' listing any LEDGER facts above "
                "that this paragraph makes no longer true, copied exactly, or 'NOW FALSE: none'." + fix)
        out = []
        for _ in range(n_drafts):
            text, _ = self.converse(tier, voice(world), user, temperature=0.8, max_tokens=320)
            out.append(split_facts(text))
        return out


def split_facts(text):
    """-> (paragraph, facts). `facts` is a list of new facts; retired ledger facts, if any, are
    appended as strings starting with '~' so Ledger.add can retire them."""
    parts = re.split(r"\s*\**FACTS\**\s*:", "\n" + text, maxsplit=1, flags=re.I)
    para = parts[0].strip()
    para = re.sub(r"^\**PARAGRAPH\**\s*:\s*", "", para, flags=re.I)
    facts, retire = [], []
    if len(parts) > 1:
        rest = re.split(r"\s*\**NOW FALSE\**\s*:", parts[1], maxsplit=1, flags=re.I)
        for line in rest[0].splitlines():
            line = line.strip().lstrip("-•* ").strip()
            if line and line.lower() not in ("none", "none."):
                facts.append(line)
        if len(rest) > 1:
            for line in rest[1].splitlines():
                line = line.strip().lstrip("-•* ").strip()
                if line and line.lower() not in ("none", "none."):
                    retire.append("~" + line)
    return para, facts[:3] + retire[:3]
