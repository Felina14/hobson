# Hobson run: referee decider, seed 43

_Run `hobson_web_decider_s43_20261023-144732` finished 2026-10-23 14:49:16 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `43`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-sum examine*   read-letter-successfully   0 lite ok      2714    18516  0.00038
 2 lighthouse-sum use*       it-is-not-there            0 pro  ok      3509     6549  0.00212

premise: A storm rages as the player, the keeper's niece, ascends the lighthouse with a lamp and an unread letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 3112 ms Decider + 9629 ms Nova per turn · 3 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0041 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_43.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
