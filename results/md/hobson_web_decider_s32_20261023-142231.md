# Hobson run: referee decider, seed 32

_Run `hobson_web_decider_s32_20261023-142231` finished 2026-10-23 14:22:48 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `32`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top use*       it-is-not-there            0 pro  ok      3372     8211  0.00208

premise: Navigating a perilous storm within a lighthouse on the Kerala coast in 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 3372 ms Decider + 4791 ms Nova per turn · 3 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0035 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_32.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
