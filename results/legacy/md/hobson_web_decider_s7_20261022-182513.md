# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261022-182513` finished 2026-10-22 18:31:16 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene   dice           outcome                dgr nar   dec ms  nova ms        $
 1 gate    ask-guard      guard-asks-business      0 lite    2098     3307  0.00012
 2 gate    present-token  guard-suspicious         2 lite    2570     4361  0.00014
 3 gate    loiter         guard-stops-you          1 lite    2186     4714  0.00014
 4 gate    push-past      guard-overpowers-you     5 pro     2515     7347  0.00221
 5 jail    talk-jailer    jailer-ignores           0 lite    2823     3975  0.00015

referee Decider 2B (local, MPS) · 5 turns · rulings 2438 ms Decider + 1418 ms Nova per turn · 7 unsure · Nova $0.0034 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, draft and timing is in the rows file, one JSON line per turn.
