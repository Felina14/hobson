"""Thin web view over the same Game the CLI uses.

    uvicorn hobson.web:app --port 8000     then open http://localhost:8000

No logic lives here: /turn calls Game.turn() and reshapes its decisions into plain-English rows
for the page. One in-memory game per process (restart the server for a new one, or POST /start).
Rows go to the same results/referee_<mode>_<seed>.jsonl as the CLI, under a `hobson_web_*` run
name that the referee comparison skips; the run's markdown is written when the game is replaced,
on POST /finish, or when the server stops.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .game import Game

STATIC = Path(__file__).resolve().parent / "static"
app = FastAPI(title="Hobson")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
_lock = threading.Lock()
_game: Game | None = None

LABELS = {
    "dice":     "What did you try?",
    "ledger":   "Is that true in the story so far?",
    "requires": "Does the story back that up?",
    "grounds":  "Do you actually have that?",
    "outcome":  "What happens?",
    "continuity": "Does the writing keep to the facts?",
    "editor":   "Which draft reads better?",
}


class StartBody(BaseModel):
    seed: int = 7
    referee: str = "decider"
    premise: str = ""


class TurnBody(BaseModel):
    action: str


def _human(label: str) -> str:
    return label.replace("-", " ").replace("_", " ")


def _rows(decisions, info, effect, editor):
    """Reshape Decision objects into rows the page can render without knowing Hobson's internals."""
    rows, seen_outcome = [], None
    by = {}
    for d in decisions:
        by.setdefault(d.name, []).append(d)

    def base(d, label, answer, note=""):
        conf = None if d.confidence is None else round(float(d.confidence), 2)
        return {"key": d.name, "label": label, "answer": answer, "note": note,
                "confidence": conf, "unsure": bool(d.unsure), "via": d.via,
                "decider_said": d.decider_value if d.via == "nova" else None}

    d = by["dice"][0]
    says = (d.options or {}).get(d.value, "") if isinstance(d.options, dict) else ""
    rows.append(base(d, LABELS["dice"], _human(str(d.value)), says))
    for d in by.get("ledger", []):
        rows.append(base(d, LABELS["ledger"], "Yes" if d.value else "No, that never happened", d.detail))
    o = by["outcome"][0]; seen_outcome = o.value
    rows.append(base(o, LABELS["outcome"], _human(str(o.value)), effect))
    for d in by.get("requires", []) + by.get("grounds", []):
        if d.name == "requires" and d.detail != seen_outcome:
            continue
        what = d.detail if d.name == "grounds" else d.question.removeprefix("Does the ledger establish that ").rstrip("?")
        rows.append(base(d, LABELS[d.name], "Yes" if d.value else "No", what))
    rows.append({"key": "danger", "label": "How dangerous was that?", "answer": f"{info['danger']} of 5",
                 "note": "comes with the outcome Nova proposed, not asked", "confidence": None, "unsure": False, "via": "world"})
    rows.append({"key": "route", "label": "Who writes the next paragraph?",
                 "answer": "Nova Pro" if info["tier"] == "pro" else "Nova Lite",
                 "note": info.get("route_why", f"danger {info['danger']}"),
                 "confidence": None, "unsure": False, "via": "world"})
    for d in by.get("continuity", []):
        rows.append(base(d, LABELS["continuity"], ("No, it broke the ledger" if d.value else "Yes"),
                         d.detail or ("the paragraph Nova wrote was checked against every fact in the ledger")))
    if editor is not None:
        v = editor.decider_value if isinstance(editor.decider_value, dict) else {}
        if editor.via == "continuity":
            ans, note = "Draft A", editor.detail
        elif v.get("tie"):
            ans, note = "A tie, kept draft A", f"{v['score_a']:.1f} vs {v['score_b']:.1f} out of 6"
        elif v:
            ans, note = f"Draft {editor.value}", f"{v['score_a']:.1f} vs {v['score_b']:.1f} out of 6 · swap {'agrees' if v['swap_agrees'] else 'disagrees'}"
        else:
            ans, note = f"Draft {editor.value}", ""
        rows.append({"key": "editor", "label": LABELS["editor"], "answer": ans, "note": note,
                     "confidence": None if editor.confidence is None else round(float(editor.confidence), 2),
                     "unsure": bool(editor.unsure), "via": editor.via})
    return rows


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


def _finish():
    """Write results/md/<run>.md for the current game, as the CLI does at `quit`."""
    if _game is not None and _game.turns:
        _game.finish({"front_end": "web", "referee": _game.mode, "seed": _game.seed})


@app.post("/start")
def start(body: StartBody):
    global _game
    with _lock:
        _finish()
        _game = Game(referee=body.referee, seed=body.seed, premise=body.premise,
                     run_name=f"hobson_web_{body.referee}_s{body.seed}_{time.strftime('%Y%m%d-%H%M%S')}")
        opening = _game.begin()
        return {"scene": _game.scene.name, "opening": opening, "ledger": list(_game.ledger.facts),
                "image": _scene_image(_game.scene.art, _game.scene), "title": _game.world.title,
                "premise": _game.world.premise}


@app.post("/finish")
def finish():
    with _lock:
        _finish()
        return {"ok": True}


@app.on_event("shutdown")
def _on_shutdown():
    _finish()


@app.post("/turn")
def turn(body: TurnBody):
    if _game is None:
        return JSONResponse({"error": "call /start first"}, status_code=400)
    with _lock:
        captured = {}
        def on_rulings(decisions, info):
            captured["decisions"], captured["info"] = decisions, info
        def on_drafts(drafts, ed):
            captured["drafts"], captured["editor"] = drafts, ed
        res = _game.turn(body.action, on_rulings=on_rulings, on_drafts=on_drafts)
        t = res["turn"]
        return {
            "scene": res["scene"], "image": _scene_image(_game.scene.art, _game.scene),
            "candidates": res.get("candidates", {}),
            "rows": _rows(res["decisions"], captured["info"], res["effect"], captured.get("editor")),
            "drafts": captured.get("drafts", {}), "picked": t.picked,
            "paragraph": t.paragraph, "opening": res["opening"], "ends": res["ends"],
            "ledger": list(_game.ledger.facts), "new_facts": t.new_facts,
            "timing": {"decider_ms": round(t.decider_ms), "nova_ms": round(t.nova_rulings_ms + t.nova_narration_ms)},
            "referee": _game.mode,
        }


def _scene_image(scene_art: str, scene=None):
    """No pictures. Everything the panel shows is read from the rulings themselves."""
    return None
