# Referee comparison: Decider vs Nova Lite

_Generated 2026-10-23 13:59:42 from `results/referee_decider_7.jsonl` and `results/referee_nova_7.jsonl` (runs listed below). Script `demo/demo_turns.txt`, seed 7._

```
decider  runs=3 turns=15
  rulings latency per turn, median:    6393 ms (Decider 1872 ms + Nova 4782 ms)
  Nova cost per 100 turns: rulings $0.0247 · all calls incl. narration $0.1243
  unsure rulings re-made by Nova: 43
  claims checked against the ledger: 22, ruled not established: 11
  continuity guard: 15 paragraphs checked, 1 swapped or rewritten
  editor: swap (A/B vs B/A) disagreement 9/14 (64%); pointwise ties 11/14
  editor: where the swap agrees and scores differ, pointwise pick = swap pick 2/2
nova     runs=3 turns=15
  rulings latency per turn, median:    6758 ms (Decider 0 ms + Nova 6758 ms)
  Nova cost per 100 turns: rulings $0.0322 · all calls incl. narration $0.1364
  unsure rulings re-made by Nova: 0
  claims checked against the ledger: 24, ruled not established: 8
  continuity guard: 15 paragraphs checked, 2 swapped or rewritten

agreement, turn by turn (run i of decider vs run i of nova, same turn, same scene):
  dice     4/5  (80%)
  outcome  0/5  (0%)

per turn, decider vs nova (dice / outcome):
  run 1 t1 lighthouse-top examine vs examine | read-letter-successfully vs read-the-letter
  run 1 t2 lighthouse-top use vs use | find-nothing vs no-cabinet
  run 1 t3 lighthouse-top move vs move | find-uncle-missing vs uncle-not-there
  run 1 t4 lighthouse-base attack vs impossible | trouble-follows vs not-possible-here
  run 1 t5 lighthouse-base bluff vs bluff | nothing-much-happens vs guard-refuses-order

prices (USD / 1K tokens, on-demand, us-east-1, AWS Price List API 2026-10-22): {'lite': {'in': 6e-05, 'out': 0.00024}, 'pro': {'in': 0.0008, 'out': 0.0032}}
Rulings latency excludes the editor's two calls and all narration; Nova ms in decider mode
is claim extraction plus fallbacks; in nova mode it is claim extraction plus the referee calls.
Unsure fallbacks run in parallel, so their Nova ms is wall time, not the sum of calls.
Decider runs locally: its cost here is 0 (the Mac's electricity is not counted).
```

Runs: `hobson_decider_s7_20261023-135339`, `hobson_decider_s7_20261023-135450`, `hobson_decider_s7_20261023-135552`, `hobson_nova_s7_20261023-135700`, `hobson_nova_s7_20261023-135757`, `hobson_nova_s7_20261023-135851`
