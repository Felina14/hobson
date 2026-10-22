# Hobson demo video — brief for Claude Code (run on the Mac, in ~/Documents/Hobson)

Same method as the PlayProof demo: real app recorded with Playwright, voice-over, captions burned in, assembled with ffmpeg. The voice is **Kokoro** (local, free), voice `af_heart`; the 18 MP3s are already generated and included in `vo/`. Only regenerate if the wording changes. Current length 5:40 (see note below).

## Files in this kit → copy into `~/Documents/Hobson/demo/`

- `narration.json` — every scene: slide text, the caption burned into the picture, and the voice-over text. **Edit the VO text here if Felina wants different wording; nothing else needs to change.**
- `vo/*.mp3` — the finished Kokoro voice-over, one per scene. `make_vo_kokoro.py [voice] [speed]` regenerates any missing one (`pip install kokoro-onnx soundfile`, and download `kokoro-v1.0.onnx` + `voices-v1.0.bin` from https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 into `demo/`). Delete an MP3 to re-synthesise that scene after a wording change.
- `record.mjs` — Playwright drives `http://localhost:8000/?seed=7`, types the five demo lines for real (55 ms per key), waits for each turn's rulings, saves `rec/run.webm`, `rec/timeline.json`, per-turn `t0N_full.png` / `t0N_panel.png`, `t05_drafts.png`.
- `assemble.py` — renders the five opening slides and the results card, cuts the recording by the timeline, zooms on the rulings panel after each turn, pads video to the VO length, burns the caption bar, concatenates → `demo/hobson_demo.mp4` (1280×800, h264+aac).

## Run order

```bash
cd ~/Documents/Hobson
mkdir -p demo && cp <kit>/* demo/
pip install pillow                      # if missing
npm i playwright && npx playwright install chromium   # once
which ffmpeg ffprobe                    # brew install ffmpeg if missing

# 1. voice-over: already in demo/vo/. Only if a VO line changed:
#    rm demo/vo/<id>.mp3 && python3 demo/make_vo_kokoro.py af_heart 0.95

# 2. start the web view and record the real run
uvicorn hobson.web:app --port 8000 &      # wait until it answers
SEED=7 node demo/record.mjs
kill %1

# 3. assemble
python3 demo/assemble.py
open demo/hobson_demo.mp4
```

## Checks before calling it done

1. Watch the whole thing once. The seed-7 run should show: turn 2 ledger row **"No, that never happened"** at ~80%, turn 3 outcome **not sure** (~56%), turn 4 **danger 5 → Nova Pro** and the move to the jail. If a run drifts from that (Nova is not deterministic), re-run `record.mjs`; the rulings are Decider's and are stable, the prose will vary.
2. The VO must not say a number the screen contradicts. If turn 3's outcome confidence comes out different from 56%, fix the `t03_panel` VO/caption in `narration.json` to match, delete `vo/t03_panel.mp3`, re-run `make_vo_kokoro.py` and `assemble.py`.
3. The panel zoom PNGs (`rec/t0N_panel.png`) must include the timing line at the bottom. If the clip is cut off, widen the `clip` height in `record.mjs`.
4. Write `results/md/demo_video.md` afterwards: which run was recorded (the `hobson_web_*` run name), the final duration, and any VO numbers you changed. Add `demo/rec/`, `demo/vo/`, `demo/_build/` to `.gitignore`; commit `demo/*.py`, `demo/*.mjs`, `demo/*.sh`, `demo/narration.json`, and the finished `demo/hobson_demo.mp4` (about 10–20 MB) or upload the MP4 to YouTube unlisted and put the link in the README.

## Known limits

- `assemble.py` falls back to the still screenshots in `rec/` when `rec/run.webm` is absent; that is how `hobson_demo_v3_voiced.mp4` was built. The Playwright recording replaces the stills with real typing and rows animating in.
- `record.mjs` records the Playwright Chromium, not Felina's Chrome; the page looks identical.
