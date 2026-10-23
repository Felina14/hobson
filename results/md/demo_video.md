# The demo video

`demo/hobson_demo.mp4` — 2:19, 1280x800, voiced with Kokoro (`af_heart`, speed 1.08).

## What is in it

Nine scenes:

1. `s01_title` — what Hobson is: Nova writes, Decider 2B decides what is true.
2. `s02_agenda` — the four things the video shows.
3. `s04_questions` — the five questions Decider answers every turn, and the 60% rule.
4. `t00_open` — a premise typed into the box; Nova builds the world and the opening ledger.
5. `t01` — a fair turn: a lamp and a letter, both in the ledger, both confirmed.
6. `t02` — the bluff: a brass key, an uncle and a locked cabinet, none of which exist.
7. `t02_panel` — the panel zoomed: the verdict, each claim's confidence dial, and the
   record underneath, unchanged.
8. `s90_results` — Decider 2B vs Nova Lite as referee, three runs each.
9. `s99_end` — repo, models, decision pattern.

## Which run

A live session captured straight from the running server into
`demo/capture_demo.json` (POST `/capture`), after the deterministic fact gate in
`b26c001`. Both bluff claims are refused — 81% and 78% — and `new_facts` is empty.

## How it was made

The browser is driven against a replay of that run, not a live model, so the
pixels are the real `web/index.html` and the rows are the real rulings.

```
# play a session in the browser, then POST the responses to /capture
python demo/replay_server.py    hobson/static  demo/capture_demo.json  8031
python demo/record_py.py        demo/rec  "http://127.0.0.1:8031/?seed=7"  demo/narration.json
python demo/assemble.py
```

`demo/slides.py` draws the title, agenda, question and results slides as SVG at
the app's own palette; `demo/assemble.py` cuts the recording on the marks in
`demo/rec/timeline.json`, lays the voice-over over each scene and burns the
captions. A turn that waited on a model runs longer than the line spoken over
it, so those clips are sped up to the narration, never past 1.8x.
