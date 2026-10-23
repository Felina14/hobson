# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-142355` finished 2026-10-23 14:44:36 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-the-letter            0 lite ok      2395     7524  0.00036
 2 lighthouse-top use*       cabinet-locked             0 pro  ok      3549     7870  0.00219
 3 lighthouse-top move       descend-to-quarters        0 lite ok      2552     8457  0.00095

premise: As the keeper's niece, you're at a storm-tossed Kerala lighthouse with an unread letter.
referee Decider 2B (local, MPS) · 3 turns · rulings 2832 ms Decider + 4151 ms Nova per turn · 8 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0049 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
