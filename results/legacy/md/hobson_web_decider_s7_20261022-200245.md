# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261022-200245` finished 2026-10-22 20:09:29 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene   dice           outcome                dgr nar   dec ms  nova ms        $
 1 gate    present-token  guard-suspicious         2 lite    1851     5839  0.00015

referee Decider 2B (local, MPS) · 1 turns · rulings 1851 ms Decider + 2195 ms Nova per turn · 1 unsure · Nova $0.0008 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, draft and timing is in the rows file, one JSON line per turn.
