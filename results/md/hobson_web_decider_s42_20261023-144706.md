# Hobson run: referee decider, seed 42

_Run `hobson_web_decider_s42_20261023-144706` finished 2026-10-23 14:47:32 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `42`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-the-letter            2 lite ok      2117     8138  0.00037
 2 lighthouse-top use*       it-is-not-there            0 pro  ok      3114     7777  0.00190

premise: Navigating a lighthouse during a 1962 Kerala storm.
referee Decider 2B (local, MPS) · 2 turns · rulings 2615 ms Decider + 4577 ms Nova per turn · 4 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0036 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_42.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
