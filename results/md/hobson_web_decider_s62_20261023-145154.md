# Hobson run: referee decider, seed 62

_Run `hobson_web_decider_s62_20261023-145154` finished 2026-10-23 16:12:30 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `62`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-the-letter            0 lite ok      1847    12145  0.00035
 2 lighthouse-sum use*       nothing-happens            0 pro  swap    3236    18825  0.00195

premise: Exploring a lighthouse on the Kerala coast during a storm in 1962 as the keeper's niece.
referee Decider 2B (local, MPS) · 2 turns · rulings 2542 ms Decider + 11529 ms Nova per turn · 6 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0037 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_62.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
