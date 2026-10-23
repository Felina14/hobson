# Hobson run: referee decider, seed 21

_Run `hobson_web_decider_s21_20261023-141832` finished 2026-10-23 14:19:33 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `21`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-letter                0 lite ok      3571     7104  0.00038
 2 lighthouse-sum use*       it-is-not-there            0 pro  ok      4664     7938  0.00220

premise: A young girl navigates a stormy night in a lighthouse on the Kerala coast in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 4117 ms Decider + 4152 ms Nova per turn · 6 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0040 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_21.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
