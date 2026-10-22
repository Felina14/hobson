# Hobson run: referee decider, seed 11

_Run `hobson_web_decider_s11_20261022-214344` finished 2026-10-22 21:46:13 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `11`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow use*       unlock-cabinet             0 lite fix     3742    12430  0.00050

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 3742 ms Decider + 7640 ms Nova per turn · 5 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0019 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_11.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
