# Hobson run: referee decider, seed 41

_Run `hobson_web_decider_s41_20261023-144638` finished 2026-10-23 14:47:06 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `41`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow examine*   read-letter-danger         2 lite swap    1130     8789  0.00037
 2 lighthouse-tow use*       open-cabinet-fail          0 pro  ok      2853     7482  0.00185

premise: A young girl navigates a stormy lighthouse with a crucial letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 1991 ms Decider + 5284 ms Nova per turn · 5 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0036 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_41.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
