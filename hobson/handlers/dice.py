"""Dice: what kind of action is the player attempting? A `choice` over fixed, setting-free
categories (questions.yaml `dice`). This is the policy pattern: the category decides which
checks follow and which outcomes Nova is asked to propose. Nothing in it names a setting."""
from __future__ import annotations

from . import ChoiceQuestion, Decision, Handler, _choice


class Dice(Handler):
    def build(self, state, **ctx):
        d = self.q["dice"]
        return {"dice": ChoiceQuestion(instructions=d["question"], criteria=d["options"])}

    def read(self, resp, ms, **ctx) -> list[Decision]:
        d = self.q["dice"]
        return [_choice("dice", resp, "dice", ms, self.threshold, d["question"], d["options"])]

    def decide(self, state, **ctx) -> Decision:
        return super().decide(state, **ctx)[0]
