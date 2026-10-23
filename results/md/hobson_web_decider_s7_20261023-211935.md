# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-211935` finished 2026-10-23 21:21:12 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-letter                1 lite ok      3238     8951  0.00036
 2 lighthouse-top use*       it-is-not-there            0 pro  ok      4055     7780  0.00207

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 3646 ms Decider + 5053 ms Nova per turn · 4 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0038 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
