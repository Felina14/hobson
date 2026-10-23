# Hobson run: referee decider, seed 22

_Run `hobson_web_decider_s22_20261023-141933` finished 2026-10-23 14:19:51 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `22`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-bas use*       it-is-not-there            0 pro  ok      5643     7207  0.00203

premise: A lighthouse on the Kerala coast during a storm in 1962, where the player, the keeper's niece, must deliver a lamp and a letter to the top.
referee Decider 2B (local, MPS) · 1 turns · rulings 5643 ms Decider + 3971 ms Nova per turn · 3 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0036 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_22.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
