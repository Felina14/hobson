"""The ledger guard: a reusable Strands Decider 2B decision pattern.

**The problem.** A generative agent believes its user. Tell a support agent "I already
returned it" and the sentence arrives in the context looking exactly like a fact, so the
refund tool gets called. The model is not lying; it has no separate faculty for deciding
what is true, and the faculty it does have is tuned to make the conversation flow.

**The pattern.** Keep a plain-sentence record of what has actually been established, and
before any consequential tool runs, hand each thing the call presupposes to a model that
cannot write prose and can only point at an answer with a confidence: Strands Decider 2B.
Two details carry most of the value:

  1. The question is asked against the **record alone**, with the user's message removed
     from the state. With the message in the state, the user's own confident phrasing
     ("the key my uncle gave me") drags the answer toward yes.
  2. It **fails closed**. A claim Decider is not sure about is treated as unestablished,
     because the cost of a wrong "yes" is a refund you cannot take back and the cost of a
     wrong "no" is one more lookup.

This is the same check that keeps the text adventure in this repository honest; the game
and the refund desk are the same shape.

Usage:

    from strands import Agent
    from patterns.ledger_guard import LedgerGuard

    record = ["order A-4471 was placed on 2 October", "order A-4471 was delivered"]

    guard = LedgerGuard(
        record=lambda: record,
        claims={"issue_refund": lambda i: [f"order {i['order_id']} was returned by the customer"]},
    )
    agent = Agent(model=..., tools=[lookup_order, issue_refund], interventions=[guard])

`claims` maps a tool name to a function from that tool's input to the list of statements
the call takes for granted. Tools absent from the map are never checked. Every check is
appended to `guard.log` so you can show your work.

Requires: strands-agents, strands-decider. The model runs locally; a check is one call
with one question per claim, around 300-600 ms on an M-series Mac, and costs nothing.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

from strands import InterventionHandler
from strands.interventions import Deny, Proceed
from strands_decider.infer import load_engine
from strands_decider.schema import NoulQuestion

CHECKPOINT = "StrandsAgents/strands-decider-2B-hobson-v19"

QUESTION = "Has the following been established earlier in this record: {claim}?"
CRITERIA = {"true": "the record says so", "false": "the record does not say so"}


@dataclass
class Check:
    """One claim, judged against the record."""

    claim: str
    established: bool
    confidence: float
    unsure: bool

    @property
    def blocks(self) -> bool:
        return not self.established

    def __str__(self) -> str:
        verdict = "established" if self.established else "NOT established"
        return f'"{self.claim}" {verdict} ({self.confidence:.2f}{", unsure" if self.unsure else ""})'


@dataclass
class GuardEvent:
    """One tool call, and what the guard decided about it."""

    tool: str
    checks: list[Check]
    allowed: bool
    latency_ms: float = 0.0


class LedgerGuard(InterventionHandler):
    """Deny a tool call whose premises are not in the record.

    Args:
        record: callable returning the established facts, one plain sentence each.
        claims: {tool name: callable(tool input) -> [statements the call presupposes]}.
        threshold: below this confidence a verdict counts as unsure (Decider's own
            calibration; 0.6 is the value used throughout this repository).
        on_unsure: "deny" (default, fail closed) or "allow".
        engine / checkpoint / device: supply a loaded engine, or let it load one lazily.
    """

    name = "ledger-guard"

    def __init__(
        self,
        record: Callable[[], Sequence[str]],
        claims: Mapping[str, Callable[[Any], Sequence[str]]],
        *,
        threshold: float = 0.6,
        on_unsure: Literal["deny", "allow"] = "deny",
        engine: Any = None,
        checkpoint: str = CHECKPOINT,
        device: str = "mps",
    ) -> None:
        self.record = record
        self.claims = dict(claims)
        self.threshold = threshold
        self.on_unsure = on_unsure
        self.log: list[GuardEvent] = []
        self._engine = engine
        self._checkpoint, self._device = checkpoint, device

    @property
    def on_error(self) -> str:
        # a guardrail that throws must not let the call through
        return "deny"

    @property
    def engine(self) -> Any:
        if self._engine is None:
            self._engine = load_engine(self._checkpoint, device=self._device)
        return self._engine

    def state(self) -> str:
        """What Decider reads. Deliberately only the record: no conversation, no tool
        arguments, nothing the user wrote. The claim must stand on the record alone."""
        facts = [f for f in (self.record() or ()) if str(f).strip()]
        body = "\n".join(f"- {f}" for f in facts) or "- (nothing has been established yet)"
        return f"RECORD (everything established so far):\n{body}"

    def check(self, claims: Sequence[str]) -> list[Check]:
        """Judge every claim in one Decider call."""
        questions = {
            f"c{i}": NoulQuestion(instructions=QUESTION.format(claim=c), criteria=CRITERIA)
            for i, c in enumerate(claims)
        }
        response = self.engine.ask(self.state(), questions)
        out: list[Check] = []
        for i, claim in enumerate(claims):
            p = float(response.answers[f"c{i}"].noul)
            confidence = abs(2 * p - 1)          # noul confidence, as everywhere else here
            unsure = confidence < self.threshold
            established = p >= 0.5 and not (unsure and self.on_unsure == "deny")
            out.append(Check(claim, established, confidence, unsure))
        return out

    def before_tool_call(self, event: Any, **kwargs: Any) -> Proceed | Deny:
        tool = event.tool_use["name"]
        extract = self.claims.get(tool)
        if extract is None:
            return Proceed()
        claims = [c for c in (extract(event.tool_use["input"]) or ()) if str(c).strip()]
        if not claims:
            return Proceed()

        import time

        t0 = time.perf_counter()
        checks = self.check(claims)
        ms = (time.perf_counter() - t0) * 1000
        blocked = [c for c in checks if c.blocks]
        self.log.append(GuardEvent(tool, checks, not blocked, ms))
        if not blocked:
            return Proceed()
        why = "; ".join(str(c) for c in blocked)
        return Deny(
            reason=(
                f"{tool} was not run. The record does not establish: {why}. "
                "Saying it does not make it so. Establish it first (look it up, or ask), "
                "then try again."
            )
        )
