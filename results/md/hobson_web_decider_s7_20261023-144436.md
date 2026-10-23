# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-144436` finished 2026-10-23 14:46:38 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-letter                1 lite ok      1862    52538  0.00039
 2 lighthouse-top use*       it-is-not-there            0 pro  ok      3486     8116  0.00207
 3 lighthouse-top move       nothing-much-happens       0 lite fix     1620    20662  0.00203

premise: Exploring a lighthouse during a 1962 Kerala storm as the keeper's niece.
referee Decider 2B (local, MPS) · 3 turns · rulings 2323 ms Decider + 22538 ms Nova per turn · 11 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0059 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
