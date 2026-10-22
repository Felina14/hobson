# Hobson run: referee decider, seed 12

_Run `hobson_web_decider_s12_20261022-214900` finished 2026-10-22 21:50:19 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `12`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   not-possible-here          0 pro  fix     3390    17678  0.00358

premise: In 1962, a storm rages at a Kerala coast lighthouse.
referee Decider 2B (local, MPS) · 1 turns · rulings 3390 ms Decider + 9546 ms Nova per turn · 8 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0050 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_12.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
