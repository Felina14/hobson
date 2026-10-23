# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-235511` finished 2026-10-23 23:56:42 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-asc examine*   open-letter-successful     0 lite ok      2890    10367  0.00043
 2 lighthouse-asc use*       it-is-not-there            0 pro  ok      4583     9520  0.00216

premise: In 1962, during a storm, you, the keeper's niece, climb a lighthouse on the Kerala coast with a lamp and an unread letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 3736 ms Decider + 5241 ms Nova per turn · 7 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0041 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
