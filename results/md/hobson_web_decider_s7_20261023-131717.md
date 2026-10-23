# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-131717` finished 2026-10-23 13:19:29 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-letter                0 lite ok      4040     7890  0.00035
 2 lighthouse-sum use*       key-doesnt-fit             0 pro  fix     4294    13058  0.00417
 3 lighthouse-sum move*      descend-struggling         3 pro  fix      689    15684  0.00400
 4 lower-levels   attack*    lamp-shatters              2 lite swap    2698     6779  0.00037

premise: The player is the lighthouse keeper's niece, atop a Kerala lighthouse during a storm in 1962, carrying a lamp and an unread letter.
referee Decider 2B (local, MPS) · 4 turns · rulings 2930 ms Decider + 5716 ms Nova per turn · 12 unsure · 3 paragraphs caught by the continuity guard · Nova $0.0103 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
