# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-235702` finished 2026-10-24 00:00:46 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   storm-distracts-reading    1 lite ok      3549     9302  0.00041
 2 lighthouse-top use*       it-is-not-there            0 pro  ok      4598     7685  0.00204

premise: A storm rages at a Kerala coast lighthouse in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 4074 ms Decider + 5278 ms Nova per turn · 8 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0039 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
