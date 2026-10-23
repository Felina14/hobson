# Hobson run: referee decider, seed 33

_Run `hobson_web_decider_s33_20261023-142248` finished 2026-10-23 14:23:55 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `33`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-bas use*       locked-cabinet-not-exist   0 pro  swap    3327     7985  0.00203

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 3327 ms Decider + 4962 ms Nova per turn · 4 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0035 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_33.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
