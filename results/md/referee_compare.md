# Referee comparison: Decider vs Nova Lite

_Generated 2026-10-22 23:25:30 from `results/referee_decider_7.jsonl` and `results/referee_nova_7.jsonl` (runs listed below). Script `demo/demo_turns.txt`, seed 7._

```
decider  runs=3 turns=15
  rulings latency per turn, median:    7481 ms (Decider 1899 ms + Nova 5165 ms)
  Nova cost per 100 turns: rulings $0.0268 · all calls incl. narration $0.1916
  unsure rulings re-made by Nova: 47
  claims checked against the ledger: 22, ruled not established: 11
  continuity guard: 15 paragraphs checked, 6 swapped or rewritten
  editor: swap (A/B vs B/A) disagreement 7/11 (64%); pointwise ties 7/11
  editor: where the swap agrees and scores differ, pointwise pick = swap pick 2/2
nova     runs=3 turns=15
  rulings latency per turn, median:    7515 ms (Decider 0 ms + Nova 7515 ms)
  Nova cost per 100 turns: rulings $0.0376 · all calls incl. narration $0.1987
  unsure rulings re-made by Nova: 0
  claims checked against the ledger: 23, ruled not established: 4
  continuity guard: 15 paragraphs checked, 4 swapped or rewritten

agreement, turn by turn (run i of decider vs run i of nova, same turn, same scene):
  dice     11/11  (100%)
  outcome  0/11  (0%)

per turn, decider vs nova (dice / outcome):
  run 1 t1 lighthouse-top examine vs examine | read-the-letter vs storm-disrupts-reading
  run 1 t2 lighthouse-top use vs use | key-not-found vs unlock-cabinet
  run 1 t3 lighthouse-top move vs move | staircase-blocked vs storm-hinders-descent
  run 2 t1 lighthouse-summit examine vs examine | read-letter-partially vs letter-reveals-secret
  run 2 t2 lighthouse-summit use vs use | key-does-not-fit vs key-doesnt-fit
  run 2 t3 lighthouse-summit move vs move | descend-find-locked-door vs uncle-not-found
  run 3 t1 lighthouse-top examine vs examine | read-letter vs read-family-letter
  run 3 t2 lighthouse-top use vs use | unlock-cabinet vs key-does-not-fit
  run 3 t3 lighthouse-top move vs move | find-uncle-in-control-room vs find-ghost-warning
  run 3 t4 lighthouse-top attack vs attack | lamp-shattered vs lamp-shatters-light-extinguished
  run 3 t5 lighthouse-top bluff vs bluff | uncle-refuses-to-listen vs ghost-ignores-bluff

prices (USD / 1K tokens, on-demand, us-east-1, AWS Price List API 2026-10-22): {'lite': {'in': 6e-05, 'out': 0.00024}, 'pro': {'in': 0.0008, 'out': 0.0032}}
Rulings latency excludes the editor's two calls and all narration; Nova ms in decider mode
is claim extraction plus fallbacks; in nova mode it is claim extraction plus the referee calls.
Unsure fallbacks run in parallel, so their Nova ms is wall time, not the sum of calls.
Decider runs locally: its cost here is 0 (the Mac's electricity is not counted).
```

Runs: `hobson_decider_s7_20261022-231816`, `hobson_decider_s7_20261022-231938`, `hobson_decider_s7_20261022-232101`, `hobson_nova_s7_20261022-232206`, `hobson_nova_s7_20261022-232310`, `hobson_nova_s7_20261022-232420`
