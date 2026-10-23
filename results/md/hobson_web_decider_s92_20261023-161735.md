# Hobson run: referee decider, seed 92

_Run `hobson_web_decider_s92_20261023-161735` finished 2026-10-23 16:18:10 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `92`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   storm-prevents-action      2 lite ok      3059    11627  0.00044
 2 lighthouse-sum use*       find-nothing               0 pro  swap    4307     9764  0.00195

premise: You are the lighthouse keeper's niece, sent up during a storm in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 3683 ms Decider + 6885 ms Nova per turn · 9 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0037 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_92.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
