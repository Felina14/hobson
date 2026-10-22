# Hobson run: referee decider, seed 7

_Run `hobson_web_decider_s7_20261022-183640` finished 2026-10-22 20:02:45 (arm64)._

## Arguments

- `front_end`: `web`
- `referee`: `decider`
- `seed`: `7`

## Summary

```
 # scene   dice           outcome                dgr nar   dec ms  nova ms        $
 1 gate    ask-guard      guard-asks-business      0 lite    1970     3541  0.00012
 2 gate    present-token  guard-suspicious         2 lite    2622     5277  0.00015
 3 gate    loiter         guard-stops-you          1 lite    2234     3687  0.00014
 4 gate    push-past      guard-overpowers-you     5 pro     3181     8512  0.00222
 5 jail    talk-jailer*   jailer-ignores           0 lite    1863     4370  0.00016

referee Decider 2B (local, MPS) · 5 turns · rulings 2374 ms Decider + 1638 ms Nova per turn · 8 unsure · Nova $0.0034 total
* = Decider unsure (confidence < threshold), re-made by Nova Lite
```

Rows: `results/referee_decider_7.jsonl`

## Notes

Every ruling, draft and timing is in the rows file, one JSON line per turn.
