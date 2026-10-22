"""The four Hobson handlers: Dice, Ledger, Ruling, Editor. Reusable without the game:

    from hobson.handlers import Ruling, load_questions
    Ruling(load_questions()).decide(state, outcomes={"a": "...", "b": "..."})

Each handler `build()`s typed questions for a state and `read()`s the answers back into
Decisions, so several handlers can share one Decider call (`ask_batch`). `decide()` is the
standalone path: one call, that handler's questions only. A Decision below the threshold
is marked `unsure`; what to do about it (Hobson re-asks Nova Lite) is the caller's business.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml
from strands_decider.schema import ChoiceQuestion, NoulQuestion, ScoreQuestion

QUESTIONS_PATH = Path(__file__).resolve().parents[1] / "questions.yaml"
_DECIDER = None


def load_questions(path: str | Path = QUESTIONS_PATH) -> dict:
    return yaml.safe_load(Path(path).read_text())


def get_decider():
    """One local engine per process (MPS), loaded on first use."""
    global _DECIDER
    if _DECIDER is None:
        from ..decider_local import DeciderLocal
        _DECIDER = DeciderLocal(device="mps")
    return _DECIDER


@dataclass
class Decision:
    name: str                     # dice | ledger | grounds | allowed | outcome | danger | requires | editor
    value: Any                    # option label, bool, or score
    p: dict[str, float]           # per-option probabilities (empty when the model gives none)
    confidence: float | None      # choice/score: Decider's confidence; noul: |2p - 1|; None for Nova
    unsure: bool
    latency_ms: float             # the Decider call this decision rode on
    via: str = "decider"          # "decider" | "nova"  (set to nova when re-made by the fallback)
    detail: str = ""              # the claim / object / condition this decision is about
    kind: str = ""                # noul | choice | score
    question: str = ""
    options: Any = None           # choice: {label: text}; score: [levels]; noul: None
    decider_value: Any = None     # what Decider said, kept when the fallback replaces it

    def row(self) -> dict:
        d = asdict(self); d.pop("question"); d.pop("options")
        return d


def _noul(name, resp, key, ms, thr, q, detail=""):
    p = resp.answers[key].noul
    conf = abs(2 * p - 1)
    return Decision(name, p >= 0.5, {"true": p, "false": 1 - p}, conf, conf < thr, ms,
                    detail=detail, kind="noul", question=q)


def _choice(name, resp, key, ms, thr, q, options, detail=""):
    a = resp.answers[key]
    return Decision(name, a.choice, dict(a.probabilities), a.confidence, a.confidence < thr, ms,
                    detail=detail, kind="choice", question=q, options=options)


def _score(name, resp, key, ms, thr, q, levels, detail=""):
    a = resp.answers[key]
    return Decision(name, a.score, dict(a.probabilities), a.confidence, a.confidence < thr, ms,
                    detail=detail, kind="score", question=q, options=levels)


class Handler:
    prefix = ""

    def __init__(self, questions: dict | None = None, decider=None, threshold: float | None = None):
        self.q = questions or load_questions()
        self._decider = decider
        self.threshold = threshold if threshold is not None else self.q.get("threshold", 0.6)

    @property
    def decider(self):
        return self._decider or get_decider()

    def build(self, state: str, **ctx) -> dict:           # name -> Question
        raise NotImplementedError

    def read(self, resp, ms: float, **ctx) -> list[Decision]:
        raise NotImplementedError

    def decide(self, state: str, **ctx):
        qs = self.build(state, **ctx)
        if not qs:
            return []
        resp, ms = self.decider.ask_many(state, qs)
        return self.read(resp, ms, **ctx)


def ask_batch(state: str, parts: list[tuple[Handler, dict]], decider=None):
    """Several handlers' questions on one state in one Decider call.
    Returns (decisions, latency_ms, usage)."""
    qs = {}
    for h, ctx in parts:
        qs.update(h.build(state, **ctx))
    if not qs:
        return [], 0.0, None
    dec = decider or parts[0][0].decider
    resp, ms = dec.ask_many(state, qs)
    out = []
    for h, ctx in parts:
        out += h.read(resp, ms, **ctx)
    return out, ms, resp.usage


from .dice import Dice            # noqa: E402
from .ledger import Ledger        # noqa: E402
from .ruling import Ruling        # noqa: E402
from .editor import Editor        # noqa: E402

__all__ = ["Decision", "Dice", "Ledger", "Ruling", "Editor", "ask_batch", "load_questions",
           "get_decider", "ChoiceQuestion", "NoulQuestion", "ScoreQuestion"]
