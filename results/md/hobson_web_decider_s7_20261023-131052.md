# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-131052` finished 2026-10-23 13:16:52 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-the-letter            0 lite ok      3083    12332  0.00037
 2 lighthouse-top use*       find-nothing               0 pro  fix     3817    17071  0.00395
 3 lighthouse-top move*      find-uncle-in-interior     0 lite ok      2677     9700  0.00104
 4 lighthouse-int attack*    lamp-shatters-no-light     3 pro  ok      4669     7426  0.00193
 5 lighthouse-int bluff*     uncle-dismisses-claim      1 pro  fix     2151    12331  0.00320

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 5 turns · rulings 3280 ms Decider + 7003 ms Nova per turn · 17 unsure · 2 paragraphs caught by the continuity guard · Nova $0.0119 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
