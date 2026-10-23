# Hobson run: referee decider, seed 31

_Run `hobson_web_decider_s31_20261023-142117` finished 2026-10-23 14:21:38 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `31`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow use*       find-nothing               0 pro  swap    5155    11132  0.00208

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 5155 ms Decider + 7422 ms Nova per turn · 8 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0034 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_31.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
