# Hobson run: referee decider, seed 15

_Run `hobson_web_decider_s15_20261022-215551` finished 2026-10-22 21:58:45 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `15`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sto examine*   read-letter-warning        1 lite ok      2871     8146  0.00036
 2 lighthouse-sto use*       open-cabinet-unsuccessfu   0 pro  fix     2032    14388  0.00309
 3 lighthouse-sto move*      descend-stairs             0 lite ok      3282    10283  0.00102
 4 lighthouse-bas attack*    lamp-shatters              2 lite ok      4315     6995  0.00033

premise: Navigate a perilous storm in a lighthouse on the Kerala coast, 1962.
referee Decider 2B (local, MPS) · 4 turns · rulings 3125 ms Decider + 5704 ms Nova per turn · 14 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0062 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_15.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
