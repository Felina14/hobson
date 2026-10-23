# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-213236` finished 2026-10-23 21:55:19 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sto examine*   open-letter-read           0 lite ok      3176     8393  0.00038
 2 lighthouse-sto use*       it-is-not-there            0 pro  ok      4561     8354  0.00205

premise: As the keeper's niece in 1962, you're sent to the lighthouse during a storm with a lamp and an unread letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 3868 ms Decider + 4878 ms Nova per turn · 6 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0039 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
