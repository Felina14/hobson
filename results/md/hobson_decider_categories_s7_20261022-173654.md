# Hobson run: referee decider, seed 7

_Run `hobson_decider_categories_s7_20261022-173654` finished 2026-10-22 17:37:48 (arm64)._

## Arguments

- `cmd`: `play`
- `referee`: `decider`
- `seed`: `7`
- `script`: `demo/demo_turns.txt`
- `show_drafts`: `False`
- `dice`: `categories`

## Summary

```
 # scene   dice           outcome                dgr nar   dec ms  nova ms        $
 1 gate    talk           guard-asks-business      0 lite    2241     4321  0.00013
 2 gate    use*           guard-unimpressed        0 lite    2639     5608  0.00020
 3 gate    move*          enter-market             0 lite    2344     6348  0.00079
 4 market  attack*        merchant-cries-thief     4 pro     3298     9348  0.00237
 5 jail    talk*          jailer-ignores           0 lite    3103     5126  0.00018

referee Decider 2B (local, MPS) · 5 turns · rulings 2725 ms Decider + 2092 ms Nova per turn · 12 unsure · Nova $0.0043 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite
```

Rows: `results/referee_decider_categories_7.jsonl`

## Notes

Every ruling, draft and timing is in the rows file, one JSON line per turn.
