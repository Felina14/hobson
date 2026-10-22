"""Continuity: does the narrator's paragraph keep to the ledger and the ruling?

Not one vague question ("does this contradict anything?": Decider sat at 0.05-0.44 on it) but
one concrete `noul` per thing that could go wrong, the shape Decider is good at:

  - for every claim the ledger ruled NOT established:  "Does the PARAGRAPH show <claim> as true or happening?"   expect no
  - for every item the player does NOT hold:           "Does the PARAGRAPH show the player using or holding <item>?"  expect no
  - if the outcome's condition was not met:            "Does the PARAGRAPH show the attempt succeeding (<effect>)?"  expect no
  - always:                                            "Does the PARAGRAPH show this happening: <ruled effect>?"      expect yes

The draft fails if any expected-no is yes or the expected-yes is no. The Decision's value is
True when the paragraph broke the rules; `p` holds the per-check answers. Reusable standalone:

    Continuity(load_questions()).decide(lstate, checks=[("c0", "Does the PARAGRAPH show ...?", False)], paragraph="...")
"""
from __future__ import annotations

from . import Decision, Handler, NoulQuestion, _noul

CRITERIA = {"true": "yes, the paragraph shows it", "false": "no, the paragraph does not show it"}


def checks_for(decisions, met: bool, outcome: dict) -> list[tuple[str, str, bool]]:
    """Build the check list from a turn's decisions. (key, question, expected answer)."""
    out = []
    for i, d in enumerate(d for d in decisions if d.name == "ledger" and not d.value):
        out.append((f"claim_{i}", f"Does the PARAGRAPH show this as true or happening: {d.detail}?", False))
    for i, d in enumerate(d for d in decisions if d.name == "grounds" and not d.value):
        out.append((f"hold_{i}", f"Does the PARAGRAPH show the player using, holding or handing over {d.detail}?", False))
    if not met:
        out.append(("fail", f"Does the PARAGRAPH show the attempt succeeding in any form ({outcome.get('effect')})?", False))
    else:
        out.append(("outcome", f"Does the PARAGRAPH show this happening: {outcome.get('effect')}?", True))
    return out[:6]


class Continuity(Handler):
    def _text(self, state, paragraph):
        return f"{state}\n\nPARAGRAPH:\n{paragraph}"

    def build(self, state, checks=(), paragraph="", **ctx):
        return {k: NoulQuestion(instructions=q, criteria=CRITERIA) for k, q, _ in checks}

    def read(self, resp, ms, checks=(), paragraph="", **ctx) -> list[Decision]:
        items = [_noul(k, resp, k, ms, self.threshold, q, detail=("expect yes" if exp else "expect no"))
                 for k, q, exp in checks]
        return items

    def decide(self, state, checks=(), paragraph="", fallback=None, **ctx) -> Decision:
        """One Decider call for all checks; `fallback(decision, text)` re-makes any unsure item
        (Hobson passes the narrator's Nova Lite fallback). Returns the combined Decision."""
        qs = self.build(state, checks=checks)
        text = self._text(state, paragraph)
        resp, ms = self.decider.ask_many(text, qs)
        items = self.read(resp, ms, checks=checks)
        for it in items:
            if it.unsure and fallback:
                fallback(it, text)
        broke = []
        for it, (k, q, exp) in zip(items, checks):
            if bool(it.value) != exp:
                broke.append(k)
        conf = min((it.confidence for it in items if it.confidence is not None), default=None)
        via = "nova" if any(it.via == "nova" for it in items) else "decider"
        p = {k: round(float(it.p.get("true", 0.0)), 3) for it, (k, _, _) in zip(items, checks)}
        d = Decision("continuity", bool(broke), p, conf, any(it.unsure for it in items) and via == "decider",
                     ms, via=via, detail="", kind="noul",
                     question="; ".join(q for _, q, _ in checks), options=None)
        d.decider_value = {"broke": broke, "checks": len(checks)}
        return d
