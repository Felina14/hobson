# Hobson run: referee decider, seed 13

_Run `hobson_web_decider_s13_20261022-215040` finished 2026-10-22 21:53:38 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `13`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow examine*   receive-cryptic-warning    3 pro  fix     2808    16807  0.00343
 2 lighthouse-tow use*       locked-cabinet-remains     0 pro  fix     3446    17266  0.00348
 3 lighthouse-tow move*      find-keeper-spectral       0 pro  fix     2833    15693  0.00340

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 3 turns · rulings 3029 ms Decider + 8041 ms Nova per turn · 19 unsure · 3 paragraphs caught by the continuity guard · Nova $0.0117 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_13.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
