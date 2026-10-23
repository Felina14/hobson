# Hobson run: referee decider, seed 82

_Run `hobson_web_decider_s82_20261023-161519` finished 2026-10-23 16:17:06 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `82`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-tow examine*   read-the-letter            1 lite ok      2663     8657  0.00038
 2 lighthouse-tow use*       cabinet-locked             0 pro  swap    1672     8597  0.00187

premise: A lighthouse on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 2167 ms Decider + 5906 ms Nova per turn · 6 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0035 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_82.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
