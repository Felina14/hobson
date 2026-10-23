# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-132400` finished 2026-10-23 13:53:38 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-the-letter            1 lite ok      4466     7438  0.00035
 2 lighthouse-top use*       nothing-happens            0 pro  ok      5440     8302  0.00209
 3 lighthouse-top move*      storm-delay                1 lite ok      3579     6441  0.00032
 4 lighthouse-top attack*    lamp-breaks                3 pro  ok      3964     7318  0.00185

premise: The player, a lighthouse keeper's niece, is sent up to the lighthouse during a storm in 1962 with a lamp and an unread letter.
referee Decider 2B (local, MPS) · 4 turns · rulings 4362 ms Decider + 4589 ms Nova per turn · 12 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0062 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
