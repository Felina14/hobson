# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261023-235306` finished 2026-10-23 23:55:11 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene          dice       outcome                  dgr nar  cont  dec ms  nova ms        $
 1 lighthouse-ent examine*   read-the-letter            0 lite ok      2645     9960  0.00039
 2 lighthouse-ent use*       it-is-not-there            0 pro  ok      5138     8584  0.00211

premise: In 1962, during a raging storm, the player, the lighthouse keeper's niece, ventures into the lighthouse armed with a lamp and an unread letter.
referee Decider 2B (local, MPS) · 2 turns · rulings 3892 ms Decider + 5337 ms Nova per turn · 5 unsure · 0 paragraphs caught by the continuity guard · Nova $0.0040 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite · cont: continuity guard ok / swapped a draft / forced a rewrite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, candidate outcome, draft and timing is in the rows file, one JSON line per turn.
