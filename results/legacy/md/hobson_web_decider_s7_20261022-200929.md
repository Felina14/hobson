# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261022-200929` finished 2026-10-22 21:36:50 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene   dice           outcome                dgr nar   dec ms  nova ms        $
 1 gate    ask-guard      guard-asks-business      0 lite    1420     2880  0.00010
 2 gate    present-token  guard-suspicious         2 lite    2044     5999  0.00013
 3 gate    loiter         guard-stops-you          1 lite    1481     4988  0.00014
 4 gate    push-past      guard-overpowers-you     5 pro     1784     8596  0.00213
 5 jail    talk-jailer*   jailer-ignores           0 lite    1720     4803  0.00015

referee Decider 2B (local, MPS) · 5 turns · rulings 1690 ms Decider + 1875 ms Nova per turn · 8 unsure · Nova $0.0033 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, draft and timing is in the rows file, one JSON line per turn.
