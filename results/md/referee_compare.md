# Referee comparison: Decider vs Nova Lite

_Generated 2026-10-22 17:35:51 from `results/referee_decider_7.jsonl` and `results/referee_nova_7.jsonl` (runs listed below). Script `demo/demo_turns.txt`, seed 7._

```
decider  runs=3 turns=15
  rulings latency per turn, median:    2667 ms (Decider 741 ms + Nova 1905 ms)
  Nova cost per 100 turns: rulings $0.0044 · all calls incl. narration $0.0569
  unsure rulings re-made by Nova: 9
  editor: swap (A/B vs B/A) disagreement 6/15 (40%); pointwise ties 8/15
  editor: where the swap agrees and scores differ, pointwise pick = swap pick 6/6
nova     runs=3 turns=15
  rulings latency per turn, median:    2926 ms (Decider 0 ms + Nova 2926 ms)
  Nova cost per 100 turns: rulings $0.0131 · all calls incl. narration $0.0899
  unsure rulings re-made by Nova: 0

agreement, turn by turn (run i of decider vs run i of nova, same turn, same scene):
  dice     12/12  (100%)
  outcome  6/12  (50%)

per turn, decider vs nova (dice / outcome):
  run 1 t1 gate   ask-guard vs ask-guard | guard-asks-business vs guard-chats
  run 1 t2 gate   present-token vs present-token | guard-suspicious vs guard-waves-through
  run 1 t4 gate   push-past vs push-past | guard-overpowers-you vs guard-overpowers-you
  run 1 t5 jail   talk-jailer vs talk-jailer | jailer-ignores vs jailer-ignores
  run 2 t1 gate   ask-guard vs ask-guard | guard-asks-business vs guard-chats
  run 2 t2 gate   present-token vs present-token | guard-suspicious vs guard-waves-through
  run 2 t4 gate   push-past vs push-past | guard-overpowers-you vs guard-overpowers-you
  run 2 t5 jail   talk-jailer vs talk-jailer | jailer-ignores vs jailer-ignores
  run 3 t1 gate   ask-guard vs ask-guard | guard-asks-business vs guard-chats
  run 3 t2 gate   present-token vs present-token | guard-suspicious vs guard-waves-through
  run 3 t4 gate   push-past vs push-past | guard-overpowers-you vs guard-overpowers-you
  run 3 t5 jail   talk-jailer vs talk-jailer | jailer-ignores vs jailer-ignores

prices (USD / 1K tokens, on-demand, us-east-1, AWS Price List API 2026-10-22): {'lite': {'in': 6e-05, 'out': 0.00024}, 'pro': {'in': 0.0008, 'out': 0.0032}}
Rulings latency excludes the editor's two calls and all narration; Nova ms in decider mode
is claim extraction plus fallbacks; in nova mode it is claim extraction plus the referee calls.
Unsure fallbacks run in parallel, so their Nova ms is wall time, not the sum of calls.
Decider runs locally: its cost here is 0 (the Mac's electricity is not counted).
```

Runs: `hobson_decider_s7_20261022-173132`, `hobson_decider_s7_20261022-173219`, `hobson_decider_s7_20261022-173317`, `hobson_nova_s7_20261022-173356`, `hobson_nova_s7_20261022-173434`, `hobson_nova_s7_20261022-173513`
