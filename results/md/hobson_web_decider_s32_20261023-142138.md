# Hobson run: referee decider, seed 32

_Run `hobson_web_decider_s32_20261023-142138` finished 2026-10-23 14:21:55 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `32`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow use*       nothing-happens            0 pro  swap    4783     7527  0.00191

premise: A storm rages at a lighthouse on the Kerala coast in 1962.
referee Decider 2B (local, MPS) · 1 turns · rulings 4783 ms Decider + 4073 ms Nova per turn · 4 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0033 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_32.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
