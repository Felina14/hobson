"""Every story gets its own pictures, drawn by Amazon Nova Canvas on Bedrock.

The seven hand-drawn banners only ever fitted seven places, so any world outside that
list — a payments incident, a generation ship — opened with nothing to look at. Nova
invents the scene, so Nova Canvas draws it: one image per distinct scene, cached on
disk, so a scene is paid for once however many turns happen in it.

Amazon models only. Nothing here calls anything outside the Nova family.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import threading
from pathlib import Path

import boto3

MODEL_ID = "amazon.nova-canvas-v1:0"
GEN = Path(__file__).resolve().parent / "static" / "scenes" / "gen"
GEN.mkdir(parents=True, exist_ok=True)

# One look for the whole game, so scenes from the same story sit together.
STYLE = ("muted cinematic illustration, limited palette of deep slate blue-grey and warm amber "
         "lamplight, soft grain, painterly, atmospheric depth, no text, no lettering, no people's "
         "faces in close-up, wide establishing shot")
NEGATIVE = "text, words, letters, watermark, signature, logo, caption, ui, frame, border, blurry, distorted anatomy"

_client = None
_lock = threading.Lock()


def _bedrock():
    global _client
    if _client is None:
        _client = boto3.client("bedrock-runtime", region_name="us-east-1")
    return _client


def key_for(world_title: str, scene_name: str, description: str) -> str:
    return hashlib.sha1(f"{world_title}|{scene_name}|{description}".encode()).hexdigest()[:16]


def prompt_for(world_title: str, scene_name: str, description: str, premise: str = "") -> str:
    """A scene description written for a reader is not a prompt; trim it to the place itself."""
    place = re.sub(r"\s+", " ", str(description or scene_name)).strip()
    place = " ".join(place.split(" ")[:45])
    setting = re.sub(r"\s+", " ", str(premise or "")).strip()
    setting = " ".join(setting.split(" ")[:25])
    bits = [p for p in (place, setting) if p]
    return f"{'. '.join(bits)}. {STYLE}"


def path_for(k: str) -> Path:
    return GEN / f"{k}.png"


def draw(k: str, prompt: str, seed: int = 0) -> Path | None:
    """Generate once and cache. Returns the file, or None if Bedrock refused or is unreachable —
    the page simply shows no image in that case, which is how it behaved before."""
    out = path_for(k)
    if out.exists():
        return out
    body = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt[:1000], "negativeText": NEGATIVE},
        "imageGenerationConfig": {
            "numberOfImages": 1, "width": 1024, "height": 576,
            "quality": "standard", "cfgScale": 6.5, "seed": abs(seed) % 858993459,
        },
    }
    try:
        with _lock:                      # one at a time: a demo does not need to parallelise
            if out.exists():
                return out
            r = _bedrock().invoke_model(modelId=MODEL_ID, body=json.dumps(body))
            payload = json.loads(r["body"].read())
            if payload.get("error"):
                return None
            img = base64.b64decode(payload["images"][0])
        tmp = out.with_suffix(".part")
        tmp.write_bytes(img)
        tmp.rename(out)
        return out
    except Exception:
        return None
