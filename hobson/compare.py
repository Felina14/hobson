"""Referee comparison: the demo script through both referees, N repeats each, same seed.
Writes results/md/referee_compare.md from the rows of exactly those runs: median ruling
latency per turn, cost per 100 turns, agreement on dice/outcome, and the editor's swap check."""
from __future__ import annotations

import json
import statistics
import time
from argparse import Namespace
from pathlib import Path

from .game import RESULTS
from .mdlog import MD
from .narrator import PRICES

FIELDS = ("dice", "outcome")


def _rows(mode, seed, runs=None):
    p = RESULTS / f"referee_{mode}_{seed}.jsonl"
    rows = [json.loads(l) for l in p.open()] if p.exists() else []
    # web-view games share the rows file but are free play, not the demo script
    return [r for r in rows if (runs is None or r["run"] in runs) and not r["run"].startswith("hobson_web_")]


def _by_run(rows):
    out = {}
    for r in rows:
        out.setdefault(r["run"], []).append(r)
    return [sorted(v, key=lambda r: r["n"]) for _, v in sorted(out.items())]


def _pick(r, name):
    return next((x["value"] for x in r["rulings"] if x["name"] == name), None)


def report(seed, runs=None, script=""):
    dec, nov = _rows("decider", seed, runs), _rows("nova", seed, runs)
    L = []
    for mode, rows in (("decider", dec), ("nova", nov)):
        if not rows:
            L.append(f"{mode}: no rows"); continue
        rul = [r["decider_ms"] - _editor_ms(r) + r["nova_rulings_ms"] for r in rows]
        dec_only = [r["decider_ms"] - _editor_ms(r) for r in rows]
        nova_rul = [r["nova_rulings_ms"] for r in rows]
        cost = statistics.mean(r["cost_usd"] for r in rows) * 100
        rcost = statistics.mean(r.get("ruling_cost_usd", 0.0) for r in rows) * 100
        unsure = sum(1 for r in rows for x in r["rulings"] if x["unsure"] and x["name"] != "editor")
        L.append(f"{mode:8s} runs={len(_by_run(rows))} turns={len(rows)}")
        L.append(f"  rulings latency per turn, median: {statistics.median(rul):7.0f} ms "
                 f"(Decider {statistics.median(dec_only):.0f} ms + Nova {statistics.median(nova_rul):.0f} ms)")
        L.append(f"  Nova cost per 100 turns: rulings ${rcost:.4f} · all calls incl. narration ${cost:.4f}")
        L.append(f"  unsure rulings re-made by Nova: {unsure}")
        claims = [x for r in rows for x in r["rulings"] if x["name"] == "ledger"]
        caught = sum(1 for x in claims if not x["value"])
        cont = [x for r in rows for x in r["rulings"] if x["name"] == "continuity"]
        fixed = sum(1 for x in cont if x.get("detail"))
        L.append(f"  claims checked against the ledger: {len(claims)}, ruled not established: {caught}")
        L.append(f"  continuity guard: {len(cont)} paragraphs checked, {fixed} swapped or rewritten")
        eds = [x for r in rows for x in r["rulings"] if x["name"] == "editor" and isinstance(x.get("decider_value"), dict)]
        if eds:
            v = [x["decider_value"] for x in eds]
            dis = sum(1 for e in v if not e["swap_agrees"])
            ties = sum(1 for e in v if e["tie"])
            both = [e for e in v if e["swap_agrees"] and not e["tie"]]
            match = sum(1 for e in both if e["swap_pick"] == ("A" if e["score_a"] > e["score_b"] else "B"))
            L.append(f"  editor: swap (A/B vs B/A) disagreement {dis}/{len(v)} ({dis / len(v):.0%}); "
                     f"pointwise ties {ties}/{len(v)}")
            L.append(f"  editor: where the swap agrees and scores differ, pointwise pick = swap pick {match}/{len(both)}")
    L.append("")
    L.append("agreement, turn by turn (run i of decider vs run i of nova, same turn, same scene):")
    pairs = []
    for a, b in zip(_by_run(dec), _by_run(nov)):
        for ra, rb in zip(a, b):
            if ra["scene"] == rb["scene"] and ra["action"] == rb["action"]:
                pairs.append((ra, rb))
    for f in FIELDS:
        same = sum(1 for ra, rb in pairs if _pick(ra, f) == _pick(rb, f))
        L.append(f"  {f:8s} {same}/{len(pairs)}" + (f"  ({same / len(pairs):.0%})" if pairs else ""))
    L.append("")
    L.append("per turn, decider vs nova (dice / outcome):")
    for ra, rb in pairs:
        L.append(f"  run {_by_run(dec).index(next(x for x in _by_run(dec) if ra in x)) + 1} t{ra['n']} "
                 f"{ra['scene']:6s} " + " | ".join(f"{_pick(ra, f)} vs {_pick(rb, f)}" for f in FIELDS))
    L.append("")
    L.append(f"prices (USD / 1K tokens, on-demand, us-east-1, AWS Price List API 2026-10-22): {PRICES}")
    L.append("Rulings latency excludes the editor's two calls and all narration; Nova ms in decider mode")
    L.append("is claim extraction plus fallbacks; in nova mode it is claim extraction plus the referee calls.")
    L.append("Unsure fallbacks run in parallel, so their Nova ms is wall time, not the sum of calls.")
    L.append("Decider runs locally: its cost here is 0 (the Mac's electricity is not counted).")
    text = "\n".join(L) + "\n"
    out = MD / "referee_compare.md"
    out.write_text(f"# Referee comparison: Decider vs Nova Lite\n\n_Generated {time.strftime('%Y-%m-%d %H:%M:%S')} "
                   f"from `results/referee_decider_{seed}.jsonl` and `results/referee_nova_{seed}.jsonl`"
                   f"{' (runs listed below)' if runs else ''}. Script `{script}`, seed {seed}._\n\n```\n{text}```\n"
                   + (("\nRuns: " + ", ".join(f"`{r}`" for r in sorted(runs)) + "\n") if runs else ""))
    print(text)
    print(f"report -> {out}")
    return out


def _editor_ms(r):
    return next((x["latency_ms"] for x in r["rulings"] if x["name"] == "editor" and x["via"] == "decider"), 0.0)


def main(args):
    if args.report_only:
        return report(args.seed, script=args.script)
    from .cli import play
    runs = set()
    for mode in ("decider", "nova"):
        for i in range(args.repeats):
            g = play(Namespace(referee=mode, seed=args.seed, script=args.script, show_drafts=False, premise=args.premise))
            runs.add(g.run)
    return report(args.seed, runs, args.script)
