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

VOICE = ("You narrate a small text adventure in a market town at dusk. Second person, present "
         "tense, plain and concrete, a little dry. No magic, no anachronisms. Never invent items "
         "the player holds or events the rulings do not allow.")


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
    def opening(self, world, scene, ledger):
        user = (f"WORLD RULES: {' '.join(world.rules)}\nSCENE: {scene.description}\n"
                f"LEDGER: {'; '.join(ledger.facts)}\n\n"
                "Write the opening of this scene for the player in 60-90 words. End on a moment "
                "that invites an action. Plain prose, no headings.")
        text, _ = self.converse("pro", VOICE, user, temperature=0.7, max_tokens=220)
        return text

    def prepare_outcomes(self, scene, action_types):
        """Fill gaps only: prepared outcomes for action types the world YAML leaves empty.
        Called once on scene entry, before any player input."""
        if not action_types:
            return {}
        user = (f"SCENE: {scene.description}\nFor each action type in {list(action_types)}, give 2-3 "
                "possible outcomes as short kebab-case labels with a one-line effect. Return JSON: "
                '{"<type>": {"<label>": "<effect>"}}')
        text, _ = self.converse("lite", "You design game outcomes. Reply with JSON only.", user, max_tokens=500)
        try:
            d = parse_json(text)
            return {t: {k: {"effect": v} for k, v in d.get(t, {}).items()} for t in action_types}
        except Exception:
            return {}

    # -- rulings support ------------------------------------------------------------------
    def extract_claims(self, action, ledger):
        """Nova Lite: the claims an action relies on, and any objects/quantities it names."""
        # The ledger is deliberately not shown (given it, Nova lists ledger facts back as claims);
        # few-shot examples keep it from inventing claims for ordinary actions.
        user = ("List what this player ACTION relies on having been established earlier: specific "
                "items the player claims to hold, people they claim to know, past events or promises "
                "they refer to. At most 3 short claims. Ordinary talking, looking, moving or fighting "
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
    def drafts(self, tier, world, scene, ledger, action, brief):
        """Two drafts of the next paragraph (two Converse calls, temperature 0.8). Each ends
        with a FACTS: block of new established facts. Returns [(paragraph, facts), (..)]."""
        user = (f"WORLD RULES: {' '.join(world.rules)}\nSCENE: {scene.description}\n"
                f"LEDGER (what is true so far): {'; '.join(ledger.facts)}\n"
                f"PLAYER ACTION: {action}\n\nRULINGS YOU MUST HONOUR:\n{brief}\n\n"
                "Write the next beat: one paragraph of 60-100 words showing what happens. The outcome "
                "is fixed: show exactly it, nothing more. The player stays in this scene unless the "
                "outcome moves them; claims marked NOT established are false and characters treat "
                "them so. Then a line "
                "'FACTS:' followed by 0-3 short bullet facts newly established by this paragraph that "
                "matter later (items gained or lost, people met, promises made, where the player is). "
                "Write 'FACTS: none' if nothing new.")
        out = []
        for _ in range(2):
            text, _ = self.converse(tier, VOICE, user, temperature=0.8, max_tokens=320)
            out.append(split_facts(text))
        return out


def split_facts(text):
    parts = re.split(r"\s*\**FACTS\**\s*:", "\n" + text, maxsplit=1, flags=re.I)
    para = parts[0].strip()
    para = re.sub(r"^\**PARAGRAPH\**\s*:\s*", "", para, flags=re.I)
    facts = []
    if len(parts) > 1:
        for line in parts[1].splitlines():
            line = line.strip().lstrip("-•* ").strip()
            if line and line.lower() not in ("none", "none."):
                facts.append(line)
    return para, facts[:3]
