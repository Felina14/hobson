"""Editor: which narrator draft is the better next beat?

Pointwise: each draft is scored alone (`score`, the gauntlet's Ep5 0-6 rubric) and the higher
wins; scores within `tie` (0.2) are a tie and A is kept. The pairwise pick, asked A/B and then
B/A, is the consistency check: `swap_agrees` says whether the two orders picked the same
draft. The decision is `unsure` on a tie."""
from __future__ import annotations

from . import ChoiceQuestion, Decision, Handler, ScoreQuestion


class Editor(Handler):
    def _pair(self, context, first, second):
        return f"{context}\n\nDRAFT A:\n{first}\n\nDRAFT B:\n{second}"

    def decide(self, context: str, draft_a: str = "", draft_b: str = "", **ctx) -> Decision:
        e = self.q["editor"]
        sq = ScoreQuestion(instructions=e["question"], criteria=e["levels"])
        pq = ChoiceQuestion(instructions=e["swap_question"], criteria=e["swap_options"])
        ra, ms1 = self.decider.ask_many(f"{context}\n\nPARAGRAPH:\n{draft_a}", {"s": sq})
        rb, ms2 = self.decider.ask_many(f"{context}\n\nPARAGRAPH:\n{draft_b}", {"s": sq})
        r1, ms3 = self.decider.ask_many(self._pair(context, draft_a, draft_b), {"p": pq})
        r2, ms4 = self.decider.ask_many(self._pair(context, draft_b, draft_a), {"p": pq})
        sa, sb = ra.answers["s"].score, rb.answers["s"].score
        tie = abs(sa - sb) < e.get("tie", 0.2)
        value = "A" if tie or sa > sb else "B"
        ab = r1.answers["p"].choice
        ba = {"A": "B", "B": "A"}[r2.answers["p"].choice]          # map the swapped answer back
        conf = min(ra.answers["s"].confidence, rb.answers["s"].confidence)
        d = Decision("editor", value, {"A": sa, "B": sb}, conf, tie, ms1 + ms2 + ms3 + ms4,
                     detail="tie" if tie else "", kind="score", question=e["question"], options=e["levels"])
        d.decider_value = {"score_a": sa, "score_b": sb, "tie": tie, "ab": ab, "ba": ba,
                           "swap_agrees": ab == ba, "swap_pick": ab if ab == ba else None}
        return d

    def build(self, state, **ctx):      # several states, so the editor never joins a batch
        return {}
