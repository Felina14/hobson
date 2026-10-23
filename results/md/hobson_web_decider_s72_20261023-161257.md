# Hobson run: referee decider, seed 72

_Run `hobson_web_decider_s72_20261023-161257` finished 2026-10-23 16:14:49 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `72`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-the-letter            0 lite ok      3033     8200  0.00046
 2 lighthouse-sum use*       it-is-not-there            0 pro  ok      4446    11046  0.00208

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 3740 ms Decider + 7207 ms Nova per turn · 10 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0039 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_72.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
