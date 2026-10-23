# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261024-000101` finished 2026-10-24 00:05:12 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-the-letter            0 lite ok      3681     7754  0.00036
 2 lighthouse-top use*       it-is-not-there            0 pro  ok      4071     8987  0.00201

premise: Navigating a lighthouse during a 1962 Kerala storm.
referee Decider 2B (local, MPS) · 2 turns · rulings 3876 ms Decider + 4580 ms Nova per turn · 7 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0037 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
