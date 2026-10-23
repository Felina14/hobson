# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-132151` finished 2026-10-23 13:23:43 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-the-letter            0 lite ok      3492     8264  0.00045
 2 lighthouse-sum use*       key-does-not-fit           0 pro  ok      4739     6925  0.00187
 3 lighthouse-sum move*      find-uncle-working         1 lite ok      3159     9417  0.00099
 4 lighthouse-sum attack*    lamp-still-works           2 lite ok      4352     6518  0.00037

premise: Navigating a perilous storm atop a Kerala lighthouse in 1962.
referee Decider 2B (local, MPS) · 4 turns · rulings 3936 ms Decider + 4536 ms Nova per turn · 18 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0051 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
