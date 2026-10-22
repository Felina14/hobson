"""Scene, Ledger and Turn. `state_text()` renders what Decider reads: world rules, the scene,
the ledger and the action, in a fixed order so the same game state always gives the same text."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTION_TYPES = ["move", "talk", "take", "use", "attack", "bluff"]   # `impossible` and `other` need no outcomes in the world file


@dataclass
class Scene:
    name: str
    description: str
    characters: list[str]
    exits: dict[str, str]
    established: list[str]
    outcomes: dict[str, dict[str, dict[str, Any]]]   # action type -> label -> {effect, goto, danger, ...}
    actions: dict[str, dict[str, str]] = field(default_factory=dict)   # id -> {says, type}

    def options_for(self, action_type: str, defaults: dict, not_possible: dict) -> dict[str, dict[str, Any]]:
        """Prepared outcomes for an action type. `impossible` has exactly one: not-possible-here.
        Any other group is topped up with the world defaults so a `choice` always has at least
        two options (Decider requires >= 2)."""
        if action_type == "impossible":
            return dict(not_possible)
        opts = dict(self.outcomes.get(action_type, {}))
        if len(opts) < 2:
            for k, v in defaults.items():
                opts.setdefault(k, v)
        return opts


@dataclass
class World:
    title: str
    start: str
    rules: list[str]
    established: list[str]
    default_outcomes: dict[str, dict]
    not_possible: dict[str, dict]
    guards_arrive: str
    scenes: dict[str, Scene]

    @classmethod
    def load(cls, path: str | Path = ROOT / "world" / "town.yaml") -> "World":
        d = yaml.safe_load(Path(path).read_text())
        scenes = {n: Scene(name=n, description=s["description"].strip(),
                           characters=s.get("characters", []), exits=s.get("exits", {}) or {},
                           established=s.get("established", []) or [], outcomes=s.get("outcomes", {}),
                           actions=s.get("actions", {}) or {})
                  for n, s in d["scenes"].items()}
        return cls(d["title"], d["start"], d["rules"], d["established"], d["default_outcomes"],
                   d.get("not_possible", {}), d["guards_arrive"], scenes)


@dataclass
class Ledger:
    facts: list[str] = field(default_factory=list)

    def add(self, *facts: str) -> list[str]:
        new = []
        for f in facts:
            f = f.strip().strip("-• ").strip()
            if f and f.lower() not in (x.lower() for x in self.facts):
                self.facts.append(f); new.append(f)
        return new


@dataclass
class Turn:
    n: int
    scene: str
    action: str
    rulings: list[dict] = field(default_factory=list)
    drafts: dict[str, str] = field(default_factory=dict)
    picked: str = ""
    paragraph: str = ""
    new_facts: list[str] = field(default_factory=list)
    narrator: str = ""
    danger: int = 0                  # the picked outcome's authored danger
    decider_ms: float = 0.0
    nova_rulings_ms: float = 0.0     # Nova time spent on rulings: claims, fallbacks, or the referee
    nova_narration_ms: float = 0.0
    tokens: dict[str, dict[str, int]] = field(default_factory=dict)   # tier -> {in, out}
    cost_usd: float = 0.0
    ruling_cost_usd: float = 0.0     # the Nova part of cost_usd spent on rulings (claims, fallbacks, referee)


def state_text(world: World, scene: Scene, ledger: Ledger, action: str | None, alert: str = "") -> str:
    """With `action=None` the state stops at the ledger: that is what ledger questions read,
    so the player's own wording ("the pass the merchant gave me") cannot vouch for itself."""
    lines = ["WORLD RULES:"] + [f"- {r}" for r in world.rules]
    lines += ["", f"SCENE: {scene.name}", scene.description]
    if scene.characters:
        lines.append("Characters here: " + "; ".join(scene.characters) + ".")
    lines.append("Exits: " + ("; ".join(f"{k} ({v})" for k, v in scene.exits.items()) if scene.exits else "none"))
    if alert:
        lines.append(alert)
    lines += ["", "LEDGER (established so far):"] + [f"- {f}" for f in ledger.facts]
    if action is not None:
        lines += ["", "PLAYER ACTION (attempted now; anything it claims is not established by saying it):", action]
    return "\n".join(lines)
