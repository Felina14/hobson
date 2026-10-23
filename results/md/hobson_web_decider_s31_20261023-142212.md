# Hobson run: referee decider, seed 31

_Run `hobson_web_decider_s31_20261023-142212` finished 2026-10-23 14:22:31 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `31`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow use*       nothing-happens            0 pro  ok      4468     8749  0.00192

premise: You, the lighthouse keeper's niece, carry a lamp and an unread letter amid a raging storm in 1962 Kerala.
referee Decider 2B (local, MPS) · 1 turns · rulings 4468 ms Decider + 5321 ms Nova per turn · 3 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0035 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_31.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
