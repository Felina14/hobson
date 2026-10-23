# Hobson run: referee decider, seed 61

_Run `hobson_web_decider_s61_20261023-145034` finished 2026-10-23 14:51:54 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `61`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-letter                0 lite ok      2220    45901  0.00040
 2 lighthouse-sum use*       cabinet-not-there          0 pro  swap    3584    21838  0.00211

premise: A storm rages as a young girl ascends a lighthouse with a lamp and an unread letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 2902 ms Decider + 28715 ms Nova per turn · 8 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0040 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_61.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
