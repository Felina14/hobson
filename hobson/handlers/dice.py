"""Dice: what is the player attempting? A `choice` over the scene's concrete actions
({id: says}, from the world file), or, with no actions given, over the action categories
(`dice_categories`: move, talk, take, use, attack, bluff, other)."""
from __future__ import annotations

from . import ChoiceQuestion, Decision, Handler, _choice


class Dice(Handler):
    def _q(self, actions):
        if actions:
            return self.q["dice"]["question"], dict(actions)
        d = self.q["dice_categories"]
        return d["question"], d["options"]

    def build(self, state, actions=None, **ctx):
        question, options = self._q(actions)
        return {"dice": ChoiceQuestion(instructions=question, criteria=options)}

    def read(self, resp, ms, actions=None, **ctx) -> list[Decision]:
        question, options = self._q(actions)
        return [_choice("dice", resp, "dice", ms, self.threshold, question, options)]

    def decide(self, state, actions=None, **ctx) -> Decision:
        return super().decide(state, actions=actions, **ctx)[0]
