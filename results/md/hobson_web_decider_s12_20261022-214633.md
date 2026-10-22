# Hobson run: referee decider, seed 12

_Run `hobson_web_decider_s12_20261022-214633` finished 2026-10-22 21:47:51 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `12`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow use*       unlock-cabinet             0 pro  fix     3650    15365  0.00371

premise: Navigating a lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 3650 ms Decider + 7214 ms Nova per turn · 5 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0051 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_12.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
