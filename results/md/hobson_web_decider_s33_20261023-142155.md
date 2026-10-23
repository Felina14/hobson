# Hobson run: referee decider, seed 33

_Run `hobson_web_decider_s33_20261023-142155` finished 2026-10-23 14:22:12 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `33`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top use*       it-is-not-there            0 pro  ok      4173     7382  0.00185

premise: A lighthouse on the Kerala coast during a storm, 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 4173 ms Decider + 4190 ms Nova per turn · 2 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0032 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_33.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
