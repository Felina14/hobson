# Hobson run: referee decider, seed 23

_Run `hobson_web_decider_s23_20261023-141951` finished 2026-10-23 14:21:17 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `23`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top use*       cabinet-locked             0 pro  fix     2551     9969  0.00281

premise: A lighthouse on the Kerala coast during a storm, 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 2551 ms Decider + 5644 ms Nova per turn · 4 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0041 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_23.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
