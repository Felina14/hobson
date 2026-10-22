"""Ledger: is each claim the action relies on actually established? One `noul` per claim
(at most 3), plus a grounding `noul` per object/quantity the action names
("does the player hold {object} in at least {amount}?").

Pass a state that ends at the ledger (no ACTION line): with the action in the state, the
player's own words ("the pass the merchant gave me") pull the answer towards "established"."""
from __future__ import annotations

from . import Decision, Handler, NoulQuestion, _noul

MAX_CLAIMS = 3


class Ledger(Handler):
    def build(self, state, claims=(), holdings=(), **ctx):
        qs = {}
        for i, c in enumerate(list(claims)[:MAX_CLAIMS]):
            qs[f"ledger_{i}"] = NoulQuestion(instructions=self.q["ledger_claim"]["question"].format(claim=c),
                                             criteria=self.q["ledger_claim"].get("criteria"))
        for i, h in enumerate(list(holdings)[:MAX_CLAIMS]):
            qs[f"grounds_{i}"] = NoulQuestion(instructions=self.q["grounding"]["question"].format(
                object=h["object"], amount=h.get("amount") or "one"), criteria=self.q["grounding"].get("criteria"))
        return qs

    def read(self, resp, ms, claims=(), holdings=(), **ctx) -> list[Decision]:
        out = []
        for i, c in enumerate(list(claims)[:MAX_CLAIMS]):
            q = self.q["ledger_claim"]["question"].format(claim=c)
            out.append(_noul("ledger", resp, f"ledger_{i}", ms, self.threshold, q, detail=c))
        for i, h in enumerate(list(holdings)[:MAX_CLAIMS]):
            amt = h.get("amount") or "one"
            q = self.q["grounding"]["question"].format(object=h["object"], amount=amt)
            out.append(_noul("grounds", resp, f"grounds_{i}", ms, self.threshold, q,
                             detail=f"{amt} {h['object']}".strip()))
        return out
