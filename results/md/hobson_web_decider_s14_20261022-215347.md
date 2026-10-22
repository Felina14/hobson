# Hobson run: referee decider, seed 14

_Run `hobson_web_decider_s14_20261022-215347` finished 2026-10-22 21:55:15 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `14`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sto examine*   read-letter-success        1 lite fix     3213    13722  0.00217
 2 lighthouse-sto use*       key-not-fit                0 pro  fix     3419    14017  0.00404

premise: You are the keeper's niece in a lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 3316 ms Decider + 7682 ms Nova per turn · 13 unsure · 2 paragraphs caught by the continuity guard · Nova $0.0075 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_14.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
