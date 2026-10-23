# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-215519` finished 2026-10-23 21:58:00 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top examine*   read-letter-safely         0 lite ok      2998     8862  0.00037
 2 lighthouse-top use*       it-is-not-there            0 pro  ok      4993     9021  0.00202

premise: During a 1962 storm, a niece delivers a letter to a lighthouse.
referee Decider 2B (local, MPS) · 2 turns · rulings 3995 ms Decider + 5692 ms Nova per turn · 5 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0038 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
