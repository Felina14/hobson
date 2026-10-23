# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-215800` finished 2026-10-23 21:59:36 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-bas examine*   storm-distraction          0 lite ok      3354     7710  0.00040
 2 lighthouse-bas use*       it-is-not-there            0 pro  ok      3655     8877  0.00203

premise: Exploring a lighthouse during a 1962 Kerala storm as the keeper's niece.
referee Decider 2B (local, MPS) · 2 turns · rulings 3505 ms Decider + 5160 ms Nova per turn · 9 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0038 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
