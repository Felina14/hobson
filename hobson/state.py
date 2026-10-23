"""Scene, Ledger and Turn. Nothing here is authored: the World is a premise plus fixed,
setting-free rules; every Scene is written by Nova when the player arrives in it.
`state_text()` renders what Decider reads (rules, scene, ledger, action) in a fixed order."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Setting-free rules. These are the only hand-written sentences in the game.
RULES = [
    "The player has only what the ledger says they hold.",
    "Nothing is true in the story until the ledger says so; a player saying it does not make it so.",
    "Characters remember what the player did earlier.",
    "Violence has consequences: after a very dangerous act, trouble arrives the next turn.",
    "The player cannot do what the setting makes impossible (fly, teleport, pay with money they do not hold).",
]

# Where a scene's banner can come from: the six line drawings in static/scenes, or none.
ART = ["gate", "market", "inn", "jail", "temple", "road", "lighthouse", "none"]


@dataclass
class Scene:
    name: str                 # short kebab-case id Nova gives it, e.g. "harbour-steps"
    description: str
    characters: list[str]
    exits: dict[str, str]     # name -> one line
    established: list[str]    # facts true on arrival
    art: str = "none"


@dataclass
class World:
    premise: str              # whatever the player typed, or Nova's invention
    title: str
    rules: list[str]
    established: list[str]    # opening facts Nova chose (what the player carries, who they are)
    trouble_arrives: str      # the alert line after a very dangerous act


@dataclass
class Ledger:
    facts: list[str] = field(default_factory=list)

    def add(self, *facts: str) -> list[str]:
        """Add facts; a fact starting with '~' retires the matching ledger fact instead (the
        narrator lists facts a paragraph has made false as NOW FALSE). Returns the new facts."""
        new = []
        for f in facts:
            f = f.strip().strip("-• ").strip()
            if f.startswith("~"):
                self.retire(f[1:]); continue
            if f and f.lower() not in (x.lower() for x in self.facts):
                self.facts.append(f); new.append(f)
        return new

    def retire(self, text: str) -> bool:
        t = text.strip().strip("-• ").strip().lower().rstrip(".")
        for x in list(self.facts):
            xl = x.lower().rstrip(".")
            if xl == t or (len(t) > 20 and (t in xl or xl in t)):
                self.facts.remove(x); return True
        return False


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
    danger: int = 0                  # the picked outcome's danger (Nova proposes it with the outcome)
    decider_ms: float = 0.0
    nova_rulings_ms: float = 0.0     # Nova time spent on rulings: claims, candidates, fallbacks, or the referee
    nova_narration_ms: float = 0.0
    tokens: dict[str, dict[str, int]] = field(default_factory=dict)
    cost_usd: float = 0.0
    ruling_cost_usd: float = 0.0
    rewrites: int = 0                # paragraphs Decider sent back for contradicting the ledger


def state_text(world: World, scene: Scene, ledger: Ledger, action: str | None, alert: str = "") -> str:
    """With `action=None` the state stops at the ledger: that is what ledger questions read,
    so the player's own wording ("the pass the merchant gave me") cannot vouch for itself."""
    lines = ["WORLD RULES:"] + [f"- {r}" for r in world.rules]
    lines += ["", f"SETTING: {world.premise}", "", f"SCENE: {scene.name}", scene.description]
    if scene.characters:
        lines.append("Characters here: " + "; ".join(scene.characters) + ".")
    lines.append("Exits: " + ("; ".join(f"{k} ({v})" for k, v in scene.exits.items()) if scene.exits else "none"))
    if alert:
        lines.append(alert)
    lines += ["", "LEDGER (established so far):"] + [f"- {f}" for f in ledger.facts]
    if action is not None:
        lines += ["", "PLAYER ACTION (attempted now; anything it claims is not established by saying it):", action]
    return "\n".join(lines)
