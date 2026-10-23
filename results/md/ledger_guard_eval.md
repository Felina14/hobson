# Ledger guard: held-out claims, Decider vs Nova

_Run `ledger_guard_eval` finished 2026-10-24 03:42:13 (arm64)._

## Arguments

- `claims`: `96`
- `threshold`: `0.6`
- `nova_repeats`: `3`

## Summary

```
96 held-out claims (48 true, 48 false), 12 records, 4 domains; threshold 0.6

decider (record only: what LedgerGuard asks)
  right side of 0.5        95/96 (99%)
  unsure (conf < 0.6)      8/96 (8%): 2 true claims, 6 false
  when sure, right         88/88 (100%)
  as a guard (unsure -> deny): false claims let through 0/48, true claims refused outright 0/48, true claims held as unsure 2/48
  determinism: 96/96 probabilities identical on a second ask; guard batch call agrees on 96/96
  latency: 177 ms median per claim; 581 ms median per record (8 claims, one call, the guard's real path); cost $0 (local)

decider + the customer's sentence in the state (ablation)
  right side of 0.5        90/96 (94%)
  unsure (conf < 0.6)      31/96 (32%): 2 true claims, 29 false
  when sure, right         65/65 (100%)
  as a guard (unsure -> deny): false claims let through 0/48, true claims refused outright 0/48, true claims held as unsure 2/48

nova-lite (x3 per claim, 288 answers)
  right                    288/288 (100%)
  as a guard: false claims let through 0/144, true claims refused 0/144; no confidence, so nothing is ever unsure
  same answer all 3 times on 96/96 claims
  latency: 615 ms median per claim; $0.0010 per 100 claims

nova-pro (x3 per claim, 288 answers)
  right                    285/288 (99%)
  as a guard: false claims let through 3/144, true claims refused 0/144; no confidence, so nothing is ever unsure
  same answer all 3 times on 96/96 claims
  latency: 665 ms median per claim; $0.0137 per 100 claims

nova-lite+message (x3 per claim, 288 answers)
  right                    282/288 (98%)
  as a guard: false claims let through 0/144, true claims refused 6/144; no confidence, so nothing is ever unsure
  same answer all 3 times on 96/96 claims
  latency: 610 ms median per claim; $0.0011 per 100 claims

hybrid (Decider when sure, Nova Lite on the unsure ones: the game's policy)
  right                    96/96 (100%)
  false claims let through 0/48, true claims refused 0/48
  Nova Lite consulted on 8/96 claims; $0.0001 per 100 claims

by kind of claim, right side of 0.5 (decider) / right (nova-lite, nova-pro: first answer)
  true / direct          n=15  decider 15/15 (0 unsure)   nova-lite 15/15   nova-pro 15/15
  true / paraphrase      n=33  decider 33/33 (2 unsure)   nova-lite 33/33   nova-pro 33/33
  false / contradicted   n=16  decider 15/16 (3 unsure)   nova-lite 16/16   nova-pro 15/16
  false / invented       n=13  decider 13/13 (1 unsure)   nova-lite 13/13   nova-pro 13/13
  false / near-miss      n=19  decider 19/19 (2 unsure)   nova-lite 19/19   nova-pro 19/19

by domain, decider right side of 0.5 / unsure
  clinic     24/24  unsure 3
  warehouse  24/24  unsure 0
  bank       23/24  unsure 5
  airline    24/24  unsure 0

Every claim Decider got wrong or was unsure of:
  unsure p=0.39 F/contradicted patient P-551 has collected both refills
  unsure p=0.75 T/paraphrase   the MRI pre-authorisation for patient P-090 is valid until the end of November
  unsure p=0.31 F/invented     StarCare approved knee surgery for patient P-090
  unsure p=0.78 T/paraphrase   the card ending 4471 was reported lost
  WRONG  p=0.71 F/contradicted the card ending 4471 was reported lost before the Voltix payment
  unsure p=0.26 F/near-miss    account A-60021 belongs to Sunil Rao
  unsure p=0.21 F/near-miss    the Voltix payment was 1,840 rupees
  unsure p=0.27 F/contradicted the October EMI for loan L-9045 was paid
```

Rows: `results/ledger_guard_eval.jsonl`

## Notes

Claim set: eval/ledger_claims.yaml, committed before the first run (b8f8c72). Prices: AWS Price List API, us-east-1, 2026-10-22.
