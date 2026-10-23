# Hobson run: referee decider, seed 51

_Run `hobson_web_decider_s51_20261023-144916` finished 2026-10-23 14:50:34 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `51`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-letter-content        0 lite ok      2016     8198  0.00039
 2 lighthouse-sum use        nothing-to-open            0 pro  ok      3493     7322  0.00210

premise: The player is the niece of a lighthouse keeper on the Kerala coast during a storm in 1962, carrying a lamp and an unread letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 2754 ms Decider + 4734 ms Nova per turn · 7 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0040 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_51.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
