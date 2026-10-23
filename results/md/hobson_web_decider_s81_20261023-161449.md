# Hobson run: referee decider, seed 81

_Run `hobson_web_decider_s81_20261023-161449` finished 2026-10-23 16:15:19 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `81`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   storm-interferes           3 pro  ok      3514     8594  0.00185
 2 lighthouse-top use*       nothing-happens            0 pro  ok      4753     8110  0.00192

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 4133 ms Decider + 4650 ms Nova per turn · 6 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0051 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_81.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
