"""python -m hobson play [--referee decider|nova] [--seed N] [--script demo.txt] [--show-drafts]
                        [--dice actions|categories]"""
from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.text import Text

from .game import Game

W = 90
console = Console(width=W, highlight=False)
LABEL, MID = 9, 68          # label column, middle column; confidence sits at the right edge


def _conf(d):
    return "" if d.confidence is None else f"{d.confidence:.2f}"


def _row(label, body, conf="", style="", note_style="bold white"):
    t = Text("  ")
    t.append(f"{label:<{LABEL}}", style="bold cyan")
    t.append(f"{body[:MID]:<{MID}}", style=style or note_style)
    t.append(f"{conf:>5}", style="bold white")
    console.print(t)


def _cut(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def _unsure_body(prefix, d, shown):
    return f"{prefix}? ({d.confidence:.2f}) → via Nova: {shown}"


def print_rulings(decisions, info):
    by = {}
    for d in decisions:
        by.setdefault(d.name, []).append(d)
    console.print()
    d = by["dice"][0]
    shown = d.value if d.value == info["atype"] else f"{d.value} ({info['atype']})"
    if d.via == "nova" and d.confidence is not None:
        _row("dice", _unsure_body("action: ", d, shown), style="bold yellow")
    else:
        _row("dice", f"action: {shown}", _conf(d))
    for d in by.get("ledger", []):
        verdict = "established" if d.value else "not established"
        if d.via == "nova" and d.confidence is not None:
            _row("ledger", f"\"{_cut(d.detail, 26)}\" ? ({d.confidence:.2f}) → via Nova: {verdict}", style="bold yellow")
        else:
            _row("ledger", f"\"{_cut(d.detail, 40)}\"  {verdict}", _conf(d), style="bold red" if not d.value else "")
    o = by["outcome"][0]
    if o.via == "dice":
        _row("ruling", f"outcome: {o.value}  (the only outcome for this action)", style="bold red")
    elif o.via == "nova" and o.confidence is not None:
        _row("ruling", f"outcome: ? ({o.confidence:.2f}) → via Nova: {o.value}", style="bold yellow")
    else:
        _row("ruling", f"outcome: {o.value}", _conf(o),
             style="bold red" if o.value == "not-possible-here" else "")
    for d in by.get("requires", []) + by.get("grounds", []):
        if d.name == "requires" and d.detail != o.value:
            continue                    # only show the condition of the outcome that happened
        what = d.detail if d.name == "grounds" else d.question.removeprefix("Does the ledger establish that ").rstrip("?")
        verdict = ("held per ledger" if d.value else "NOT held per ledger") if d.name == "grounds" else \
                  ("met per ledger" if d.value else "NOT met per ledger")
        tag = "  (via Nova)" if d.via == "nova" and d.confidence is not None else ""
        _row("grounds", f"\"{_cut(what, 34)}\" {verdict}{tag}", "" if tag else _conf(d),
             style="bold red" if not d.value else "")
    _row("danger", f"{info['danger']} / 5  (authored on the outcome)", style="bold red" if info["danger"] >= 4 else "")
    _row("route", f"narrator: {info['tier'].title()} (danger {info['danger']})")


def print_editor(drafts, ed, show):
    if show:
        for k in ("A", "B"):
            mark = "◀ picked" if k == ed.value else ""
            console.print(Text(f"\n  draft {k} {mark}", style="bold magenta" if mark else "dim"))
            console.print(Text(drafts[k], style="white" if mark else "dim"), width=W - 4)
    v = ed.decider_value if isinstance(ed.decider_value, dict) else None
    if v is None:                       # Nova referee: one pairwise call, no scores
        _row("editor", f"narrator {ed.value}")
        return
    swap = "swap agrees" if v["swap_agrees"] else "swap disagrees"
    if v["tie"]:
        body = f"tie ({v['score_a']:.1f} vs {v['score_b']:.1f}) → A · {swap}"
    else:
        body = f"narrator {ed.value} ({v['score_a']:.1f} vs {v['score_b']:.1f}) · {swap}"
    _row("editor", body, style="bold yellow" if v["tie"] or not v["swap_agrees"] else "")


def timing(t):
    nova = (t.nova_rulings_ms + t.nova_narration_ms) / 1000
    return Text(f"  ⟲ {t.decider_ms:.0f} ms on Decider · {nova:.1f} s on Nova", style="dim")


def story(text):
    console.print()
    console.print(Text(text, style="bold white"), width=W - 2)
    console.print()


def play(args):
    g = Game(referee=args.referee, seed=args.seed, dice=getattr(args, "dice", "actions"))
    extra = "" if g.dice_mode == "actions" else f" · dice {g.dice_mode}"
    console.rule(Text(f"HOBSON · referee {args.referee} · seed {args.seed}{extra}", style="bold"), style="cyan")
    story(g.begin())
    lines = None
    if args.script:
        lines = [l.strip() for l in open(args.script) if l.strip() and not l.lstrip().startswith("#")]
    while not g.over:
        if lines is not None:
            if not lines:
                break
            action = lines.pop(0)
            console.print(Text(f"> {action}", style="bold green"))
        else:
            try:
                action = console.input("[bold green]> [/]").strip()
            except (EOFError, KeyboardInterrupt):
                break
        if not action:
            continue
        if action.lower() in ("quit", "exit"):
            break
        res = g.turn(action, on_rulings=print_rulings,
                     on_drafts=lambda d, ed: print_editor(d, ed, args.show_drafts))
        console.print(timing(res["turn"]))
        story(res["turn"].paragraph)
        if res["opening"]:
            console.rule(Text(res["scene"].upper(), style="bold"), style="cyan")
            story(res["opening"])
        if res["ends"]:
            console.print(Text("  THE END", style="bold"))
    console.rule(style="cyan")
    console.print(Text("  " + g.referee_line(), style="bold"), width=W)
    g.finish(vars(args))
    return g


def main(argv=None):
    p = argparse.ArgumentParser(prog="hobson")
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("play", help="play in the terminal")
    pl.add_argument("--referee", choices=["decider", "nova"], default="decider")
    pl.add_argument("--seed", type=int, default=7)
    pl.add_argument("--script", help="file of player actions, one per line")
    pl.add_argument("--show-drafts", action="store_true", help="print both narrator drafts")
    pl.add_argument("--dice", choices=["actions", "categories"], default="actions",
                    help="dice over the scene's concrete actions (default) or the old action categories")
    cp = sub.add_parser("compare", help="run the demo through both referees and write referee_compare.md")
    cp.add_argument("--script", default="demo/demo_turns.txt")
    cp.add_argument("--seed", type=int, default=7)
    cp.add_argument("--repeats", type=int, default=3)
    cp.add_argument("--report-only", action="store_true", help="rebuild the report from existing rows")
    args = p.parse_args(argv)
    if args.cmd == "play":
        play(args)
    else:
        from .compare import main as compare
        compare(args)


if __name__ == "__main__":
    sys.exit(main())
