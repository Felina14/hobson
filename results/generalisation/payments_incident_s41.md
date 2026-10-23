# Hobson run: referee decider, seed 41

_Run `hobson_web_decider_s41_20261023-204820` finished 2026-10-23 20:49:51 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `41`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 server-room-ch examine*   deploy-logs-revealed       0 lite ok      2782     7430  0.00028
 2 server-room-ch use*       it-is-not-there            0 pro  ok      4757     9834  0.00225

premise: Handle a critical production incident at 3am in a Bengaluru-based payments company.
referee Decider 2B (local, MPS) · 2 turns · rulings 3769 ms Decider + 5044 ms Nova per turn · 7 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0040 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_41.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
