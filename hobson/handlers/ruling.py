"""Ruling: which prepared outcome happens (`choice`), plus a `noul` for each outcome that
carries a `requires` condition, so "buy-key-if-three-coppers" is decided against the ledger
rather than taken on trust.

Impossible attempts are not a separate question: every outcome group includes an authored
`not-possible-here`, so the outcome choice covers them. Danger is not asked either: it is
authored on each outcome in the world file.

`parts` picks which to ask, so a caller can split them across calls (Hobson asks the
conditions against the ledger alone, and the outcome once the action is known)."""
from __future__ import annotations

from . import ChoiceQuestion, Decision, Handler, NoulQuestion, _choice, _noul

ALL = ("outcome", "requires")
REQ_CRITERIA = {"true": "the ledger says so", "false": "the ledger does not say so"}


class Ruling(Handler):
    def _req_q(self, cond):
        return f"Does the ledger establish that {cond}?"

    def build(self, state, outcomes=None, requires=None, parts=ALL, **ctx):
        qs = {}
        if "outcome" in parts and outcomes:
            qs["outcome"] = ChoiceQuestion(instructions=self.q["outcome"]["question"], criteria=dict(outcomes))
        if "requires" in parts:
            for i, (label, cond) in enumerate((requires or {}).items()):
                qs[f"requires_{i}"] = NoulQuestion(instructions=self._req_q(cond), criteria=REQ_CRITERIA)
        return qs

    def read(self, resp, ms, outcomes=None, requires=None, parts=ALL, **ctx) -> list[Decision]:
        t, out = self.threshold, []
        if "outcome" in parts and outcomes:
            out.append(_choice("outcome", resp, "outcome", ms, t, self.q["outcome"]["question"], dict(outcomes)))
        if "requires" in parts:
            for i, (label, cond) in enumerate((requires or {}).items()):
                out.append(_noul("requires", resp, f"requires_{i}", ms, t, self._req_q(cond), detail=label))
        return out
