"""Held-out evaluation of the ledger guard (patterns/ledger_guard.py).

    python scripts/eval_ledger_guard.py            # needs AWS creds for the Nova baselines

The claim set is eval/ledger_claims.yaml: 96 claims over 12 records in four domains Hobson
never ran, committed before the first run. For every claim, the same question on the same
record ("Has the following been established earlier in this record: <claim>?") is put to:

  decider          Strands Decider 2B, record only: exactly what LedgerGuard.check() asks
  decider+message  the same, but with the customer's sentence asserting the claim appended
                   to the state: the ablation behind "ask against the record alone"
  nova-lite        Amazon Nova Lite, constrained true/false, same question and criteria
  nova-pro         Amazon Nova Pro, the same
  nova-lite+message  Nova Lite with the customer's sentence in the state too: what an agent
                   model actually sees when it decides on its own
  hybrid           Decider, with Nova Lite answering only the claims Decider is unsure of
                   (the policy the game uses), computed from the two runs above

Nova is asked three times per claim (temperature 0); Decider is deterministic and is asked
twice to show that. Writes results/ledger_guard_eval.jsonl and results/md/ledger_guard_eval.md.
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from strands_decider.schema import NoulQuestion  # noqa: E402

from hobson.mdlog import finish_run  # noqa: E402
from hobson.narrator import PRICES, _FallbackNova  # noqa: E402
from patterns.ledger_guard import CRITERIA, QUESTION, LedgerGuard, get_engine  # noqa: E402

THR = 0.6
NOVA_REPEATS = 3
ROWS = ROOT / "results" / "ledger_guard_eval.jsonl"


def p_true(engine, state, claim):
    q = {"c": NoulQuestion(instructions=QUESTION.format(claim=claim), criteria=CRITERIA)}
    t = time.perf_counter()
    r = engine.ask(state, q)
    return float(r.answers["c"].noul), (time.perf_counter() - t) * 1000


def add_message_condition():
    """Add nova-lite+message to an existing rows file and rebuild the report (no other calls)."""
    data = yaml.safe_load((ROOT / "eval" / "ledger_claims.yaml").read_text())
    facts = {rid: rec["facts"] for rid, rec in data["records"].items()}
    lite = _FallbackNova("lite")
    rows = [json.loads(l) for l in ROWS.open()]
    for r in rows:
        guard = LedgerGuard(record=lambda f=facts[r["record"]]: f, claims={}, engine=object())
        said = f"{guard.state()}\n\nCUSTOMER SAYS: {r['claim'][0].upper() + r['claim'][1:]}."
        r["nova-lite+message"] = []
        for _ in range(NOVA_REPEATS):
            d = lite.noul(said, QUESTION.format(claim=r["claim"]), CRITERIA)
            r["nova-lite+message"].append({"true": d.answer >= 0.5, "raw": d.raw, "ms": d.latency_ms,
                                           "in": d.input_tokens, "out": d.output_tokens})
    with ROWS.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    report(rows, json.loads((ROOT / "results" / "ledger_guard_eval_batch_ms.json").read_text()))


def main():
    data = yaml.safe_load((ROOT / "eval" / "ledger_claims.yaml").read_text())
    engine = get_engine()
    lite, pro = _FallbackNova("lite"), _FallbackNova("pro")
    rows, batch_ms = [], []
    for _ in range(3):                                   # warm-up, not measured
        engine.ask("RECORD:\n- warm-up", {"c": NoulQuestion(instructions="Is this a warm-up?")})

    for rid, rec in data["records"].items():
        guard = LedgerGuard(record=lambda rec=rec: rec["facts"], claims={}, engine=engine, threshold=THR)
        state = guard.state()
        claims = [c["claim"] for c in rec["claims"]]
        t = time.perf_counter()
        batch = guard.check(claims)                      # the guard's real path: one call per record
        batch_ms.append((time.perf_counter() - t) * 1000)
        for c, chk in zip(rec["claims"], batch):
            p, ms = p_true(engine, state, c["claim"])
            p2, _ = p_true(engine, state, c["claim"])
            said = f"{state}\n\nCUSTOMER SAYS: {c['claim'][0].upper() + c['claim'][1:]}."
            pm, _ = p_true(engine, said, c["claim"])
            nova = {}
            for name, model, st in (("nova-lite", lite, state), ("nova-pro", pro, state),
                                    ("nova-lite+message", lite, said)):
                answers = []
                for _ in range(NOVA_REPEATS):
                    d = model.noul(st, QUESTION.format(claim=c["claim"]), CRITERIA)
                    answers.append({"true": d.answer >= 0.5, "raw": d.raw, "ms": d.latency_ms,
                                    "in": d.input_tokens, "out": d.output_tokens})
                nova[name] = answers
            rows.append({"record": rid, "domain": rid.split("-")[0], "claim": c["claim"], "truth": c["truth"],
                         "kind": c["kind"], "decider_p": p, "decider_p_repeat": p2, "decider_ms": ms,
                         "batch_established": chk.established, "batch_confidence": chk.confidence,
                         "decider_message_p": pm, **nova})
    with ROWS.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (ROOT / "results" / "ledger_guard_eval_batch_ms.json").write_text(json.dumps(batch_ms))
    report(rows, batch_ms)


def conf(p):
    return abs(2 * p - 1)


def report(rows, batch_ms):
    n = len(rows)
    T = [r for r in rows if r["truth"]]; F = [r for r in rows if not r["truth"]]
    out = [f"{n} held-out claims ({len(T)} true, {len(F)} false), 12 records, 4 domains; threshold {THR}", ""]

    def decider_line(name, key):
        right = sum((r[key] >= 0.5) == r["truth"] for r in rows)
        unsure = [r for r in rows if conf(r[key]) < THR]
        sure = [r for r in rows if conf(r[key]) >= THR]
        sure_right = sum((r[key] >= 0.5) == r["truth"] for r in sure)
        let_through = sum(1 for r in F if r[key] >= 0.5 and conf(r[key]) >= THR)
        refused_true = sum(1 for r in T if r[key] < 0.5 and conf(r[key]) >= THR)
        out.append(f"{name}")
        out.append(f"  right side of 0.5        {right}/{n} ({right / n:.0%})")
        out.append(f"  unsure (conf < {THR})      {len(unsure)}/{n} ({len(unsure) / n:.0%}): "
                   f"{sum(r['truth'] for r in unsure)} true claims, {sum(not r['truth'] for r in unsure)} false")
        out.append(f"  when sure, right         {sure_right}/{len(sure)}" + (f" ({sure_right / len(sure):.0%})" if sure else ""))
        out.append(f"  as a guard (unsure -> deny): false claims let through {let_through}/{len(F)}, "
                   f"true claims refused outright {refused_true}/{len(T)}, "
                   f"true claims held as unsure {sum(1 for r in T if conf(r[key]) < THR)}/{len(T)}")

    decider_line("decider (record only: what LedgerGuard asks)", "decider_p")
    same = sum(abs(r["decider_p"] - r["decider_p_repeat"]) < 1e-9 for r in rows)
    agree = sum((r["decider_p"] >= 0.5) == r["batch_established"] for r in rows)
    out.append(f"  determinism: {same}/{n} probabilities identical on a second ask; "
               f"guard batch call agrees on {agree}/{n}")
    dm = statistics.median(r["decider_ms"] for r in rows)
    out.append(f"  latency: {dm:.0f} ms median per claim; {statistics.median(batch_ms):.0f} ms median per record "
               f"(8 claims, one call, the guard's real path); cost $0 (local)")
    out.append("")
    decider_line("decider + the customer's sentence in the state (ablation)", "decider_message_p")
    out.append("")

    for name in ("nova-lite", "nova-pro", "nova-lite+message"):
        votes = [a["true"] for r in rows for a in r[name]]
        right = sum(a["true"] == r["truth"] for r in rows for a in r[name])
        stable = sum(len({a["true"] for a in r[name]}) == 1 for r in rows)
        let_through = sum(1 for r in F for a in r[name] if a["true"])
        refused = sum(1 for r in T for a in r[name] if not a["true"])
        ms = statistics.median(a["ms"] for r in rows for a in r[name])
        tier = name.split("-")[1].split("+")[0]
        cost = sum(a["in"] / 1000 * PRICES[tier]["in"] + a["out"] / 1000 * PRICES[tier]["out"]
                   for r in rows for a in r[name]) / len(votes) * 100
        out.append(f"{name} (x{NOVA_REPEATS} per claim, {len(votes)} answers)")
        out.append(f"  right                    {right}/{len(votes)} ({right / len(votes):.0%})")
        out.append(f"  as a guard: false claims let through {let_through}/{len(F) * NOVA_REPEATS}, "
                   f"true claims refused {refused}/{len(T) * NOVA_REPEATS}; no confidence, so nothing is ever unsure")
        out.append(f"  same answer all {NOVA_REPEATS} times on {stable}/{n} claims")
        out.append(f"  latency: {ms:.0f} ms median per claim; ${cost:.4f} per 100 claims")
        out.append("")

    # hybrid: Decider when sure, Nova Lite's first answer when unsure
    def hyb(r):
        return (r["decider_p"] >= 0.5) if conf(r["decider_p"]) >= THR else r["nova-lite"][0]["true"]
    right = sum(hyb(r) == r["truth"] for r in rows)
    handed = [r for r in rows if conf(r["decider_p"]) < THR]
    cost = sum(r["nova-lite"][0]["in"] / 1000 * PRICES["lite"]["in"] + r["nova-lite"][0]["out"] / 1000 * PRICES["lite"]["out"]
               for r in handed) / n * 100
    out.append("hybrid (Decider when sure, Nova Lite on the unsure ones: the game's policy)")
    out.append(f"  right                    {right}/{n} ({right / n:.0%})")
    out.append(f"  false claims let through {sum(1 for r in F if hyb(r))}/{len(F)}, true claims refused {sum(1 for r in T if not hyb(r))}/{len(T)}")
    out.append(f"  Nova Lite consulted on {len(handed)}/{n} claims; ${cost:.4f} per 100 claims")
    out.append("")

    out.append("by kind of claim, right side of 0.5 (decider) / right (nova-lite, nova-pro: first answer)")
    for truth, kind in [(True, "direct"), (True, "paraphrase"), (False, "contradicted"), (False, "invented"), (False, "near-miss")]:
        g = [r for r in rows if r["truth"] == truth and r["kind"] == kind]
        d = sum((r["decider_p"] >= 0.5) == truth for r in g)
        du = sum(conf(r["decider_p"]) < THR for r in g)
        l = sum(r["nova-lite"][0]["true"] == truth for r in g)
        pr = sum(r["nova-pro"][0]["true"] == truth for r in g)
        out.append(f"  {('true' if truth else 'false') + ' / ' + kind:22} n={len(g):2}  decider {d:2}/{len(g)} ({du} unsure)   "
                   f"nova-lite {l:2}/{len(g)}   nova-pro {pr:2}/{len(g)}")
    out.append("")
    out.append("by domain, decider right side of 0.5 / unsure")
    for dom in ("clinic", "warehouse", "bank", "airline"):
        g = [r for r in rows if r["domain"] == dom]
        out.append(f"  {dom:10} {sum((r['decider_p'] >= 0.5) == r['truth'] for r in g):2}/{len(g)}  unsure {sum(conf(r['decider_p']) < THR for r in g)}")
    out.append("")
    out.append("Every claim Decider got wrong or was unsure of:")
    for r in rows:
        wrong = (r["decider_p"] >= 0.5) != r["truth"]
        if wrong or conf(r["decider_p"]) < THR:
            out.append(f"  {'WRONG ' if wrong else 'unsure'} p={r['decider_p']:.2f} {'T' if r['truth'] else 'F'}/{r['kind']:12} {r['claim']}")
    print("\n".join(out))
    finish_run("ledger_guard_eval", "Ledger guard: held-out claims, Decider vs Nova", {"claims": n, "threshold": THR,
               "nova_repeats": NOVA_REPEATS}, out, ROWS,
               notes="Claim set: eval/ledger_claims.yaml, committed before the first run (b8f8c72). Prices: AWS Price List API, us-east-1, 2026-10-22.")


if __name__ == "__main__":
    add_message_condition() if "--add-message" in sys.argv else main()
