# Hobson run: referee decider, seed 91

_Run `hobson_web_decider_s91_20261023-161706` finished 2026-10-23 16:17:35 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `91`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-the-letter            0 lite ok      3166     7864  0.00037
 2 lighthouse-sum use*       locked-cabinet-missing     0 pro  ok      4892     8763  0.00216

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 4029 ms Decider + 5351 ms Nova per turn · 11 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0039 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_91.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
