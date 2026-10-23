# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-131946` finished 2026-10-23 13:21:35 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 stormy-lightho examine*   letter-tears-more          1 lite ok      4231     7310  0.00036
 2 stormy-lightho use*       key-doesnt-work            0 pro  fix     3752    16054  0.00403
 3 stormy-lightho move*      find-uncle-safe            1 lite ok      2504    11660  0.00104
 4 stormy-lightho attack*    lamp-causes-trouble        3 pro  ok      4343     7349  0.00170

premise: You are the lighthouse keeper's niece on the Kerala coast during a storm in 1962.
referee Decider 2B (local, MPS) · 4 turns · rulings 3708 ms Decider + 6231 ms Nova per turn · 12 unsure · 1 paragraphs caught by the continuity guard · Nova $0.0085 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
