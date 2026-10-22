"""Copied from decider-gauntlet/gauntlet/adapters/base.py. Every model answers through this
interface, so every episode runs unchanged against any of them.

A Decision is what the harness records per question: the pick, the per-option
probabilities (when the model gives them), a confidence in [0, 1], latency and tokens.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Decision:
    kind: str                         # "noul" | "choice" | "score"
    answer: Any                       # bool-ish prob for noul, option name for choice, float for score
    confidence: float                 # 0..1; for noul this is |2p-1|
    probabilities: dict[str, float] = field(default_factory=dict)
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    raw: Any = None


class Adapter(Protocol):
    name: str

    def noul(self, state: str, question: str, criteria: dict[str, str] | None = None) -> Decision: ...
    def choice(self, state: str, question: str, options: dict[str, str]) -> Decision: ...
    def score(self, state: str, question: str, levels: list[str]) -> Decision: ...


def timed(fn):
    """Wrap a call, return (result, elapsed_ms)."""
    t = time.perf_counter()
    r = fn()
    return r, (time.perf_counter() - t) * 1000
