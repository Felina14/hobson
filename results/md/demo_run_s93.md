# Hobson run: referee decider, seed 93

_Run `hobson_web_decider_s93_20261023-161810` finished 2026-10-23 20:48:20 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `93`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-letter-about-storm    1 lite ok      2931     7894  0.00035
 2 lighthouse-sum use*       locked-cabinet-missing     0 pro  swap    5190     9280  0.00221

premise: You, the keeper's niece, climb a lighthouse during a 1962 storm with a lamp and an unread letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 4060 ms Decider + 5289 ms Nova per turn · 5 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0040 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_93.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
