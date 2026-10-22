"""Copied from decider-gauntlet/gauntlet/adapters/decider_local.py. One model, one engine, MPS."""
from __future__ import annotations

from strands_decider.infer import load_engine
from strands_decider.schema import ChoiceQuestion, NoulQuestion, ScoreQuestion

from .base import Decision, timed

CKPT = "StrandsAgents/strands-decider-2B-hobson-v19"


class DeciderLocal:
    def __init__(self, checkpoint: str = CKPT, device: str = "mps"):
        self.name = f"decider-local-{device}"
        self.engine = load_engine(checkpoint, device=device)

    def _ask(self, state, questions):
        resp, ms = timed(lambda: self.engine.ask(state, questions))
        return resp, ms

    def noul(self, state, question, criteria=None):
        q = NoulQuestion(instructions=question, criteria=criteria)
        resp, ms = self._ask(state, {"q": q})
        p = resp.answers["q"].noul
        return Decision("noul", p, abs(2 * p - 1), {"true": p, "false": 1 - p}, ms,
                        resp.usage.input_tokens, resp.usage.output_tokens, resp.model_dump())

    def choice(self, state, question, options):
        q = ChoiceQuestion(instructions=question, criteria=options)
        resp, ms = self._ask(state, {"q": q})
        a = resp.answers["q"]
        return Decision("choice", a.choice, a.confidence, a.probabilities, ms,
                        resp.usage.input_tokens, resp.usage.output_tokens, resp.model_dump())

    def score(self, state, question, levels):
        q = ScoreQuestion(instructions=question, criteria=levels)
        resp, ms = self._ask(state, {"q": q})
        a = resp.answers["q"]
        return Decision("score", a.score, a.confidence, a.probabilities, ms,
                        resp.usage.input_tokens, resp.usage.output_tokens, resp.model_dump())

    def ask_many(self, state, questions: dict):
        """Several questions on one state in one call (the multi-question cost test)."""
        resp, ms = self._ask(state, questions)
        return resp, ms
