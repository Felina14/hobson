# Hobson run: referee decider, seed 71

_Run `hobson_web_decider_s71_20261023-161230` finished 2026-10-23 16:12:57 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `71`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-top use*       read-letter-successfully   0 lite ok      3531     8079  0.00036
 2 lighthouse-top use*       it-is-not-there            0 pro  ok      4308     6014  0.00208

premise: A lighthouse on the Kerala coast during a storm, 1962.
referee Decider 2B (local, MPS) · 2 turns · rulings 3919 ms Decider + 4670 ms Nova per turn · 8 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0039 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_71.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
