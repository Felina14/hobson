# Demo video

`demo/hobson_demo.mp4` — 2:36, 1280x800, h264 + aac.

## What it shows
Eight segments: what Hobson is; the questions Decider answers each turn; the premise typed into
the box and the world Nova builds from it; an honest turn (reading the letter); the bluff (a brass
key, an uncle and a locked cabinet, none of which exist); a zoom on the rulings panel for that
turn; the referee comparison; the end card.

## The run in it
`hobson_web_decider_s61_20261023-145034` (rows in `results/referee_decider_61.jsonl`), premise
"a lighthouse on the Kerala coast during a storm, 1962; I am the keeper's niece, sent up with a
lamp and a letter I have not read". On the bluff turn Decider refused all three claims (0.80,
0.59, 0.79), refused the brass key (0.79) and the locked cabinet (0.76) while keeping the lamp the
player really holds (0.45, yes), routed the writing to Nova Pro as contested, and the fact screen
kept "The area around the lamp is clear of any cabinet" out of the ledger. Nothing was recorded
that turn.

## How it was made
Same method as the PlayProof demo. The run above was played against the live server, its `/start`
and `/turn` responses rebuilt into `demo/capture_demo.json` by `demo/rows_from_jsonl.py`, then
replayed through the real `hobson/static/index.html` by `demo/replay_server.py` and recorded with
Playwright (`demo/record_py.py`). Voice is Kokoro (`af_heart`, speed 1.08) from the `vo` text in
`demo/narration.json`; `demo/assemble.py` renders the slides and the results card, cuts the
recording by the timeline, pads to the voice-over and burns the captions.

Every ruling on screen is the real measured one; only the pacing between turns was shortened for
the recording. The timings shown in the page footer are the originals.

## Numbers quoted
From `results/md/referee_compare.md` (same script, seed 7, three runs per referee): claims refused
11 of 22 vs 8 of 24; the brass-key bluff refused 3 of 3 vs the key believed in 2 of 3; ruling
latency 6.4 s vs 6.8 s per turn; Nova cost per 100 turns of rulings $0.025 vs $0.032.
