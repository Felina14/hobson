"""Copied from decider-gauntlet/gauntlet/mdlog.py. Every run ends by writing markdown into results/md/:
  <run-name>.md          what ran, the per-knob summary lines, where the rows are
  <episode>_report.md    the full episode report regenerated from all rows so far
Call `finish_run(...)` at the end of a runner; `capture_report(...)` from a report script."""
from __future__ import annotations

import io, platform, subprocess, sys, time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "results" / "md"
MD.mkdir(parents=True, exist_ok=True)


def finish_run(run_name: str, title: str, args: dict, summary_lines: list[str], rows_path: Path,
               report_script: str | None = None, notes: str = "") -> Path:
    out = MD / f"{run_name}.md"
    lines = [f"# {title}", "",
             f"_Run `{run_name}` finished {time.strftime('%Y-%m-%d %H:%M:%S')} ({platform.machine()})._", "",
             "## Arguments", ""]
    lines += [f"- `{k}`: `{v}`" for k, v in args.items()]
    lines += ["", "## Summary", "", "```"] + summary_lines + ["```", "",
              f"Rows: `{Path(rows_path).resolve().relative_to(ROOT.resolve())}`", ""]
    if notes:
        lines += ["## Notes", "", notes, ""]
    out.write_text("\n".join(lines))
    print(f"summary -> {out.relative_to(ROOT)}")
    if report_script:
        try:
            subprocess.run([sys.executable, str(ROOT / report_script)], check=False, cwd=ROOT,
                           stdout=subprocess.DEVNULL)
        except Exception as e:  # the report is a convenience; never fail the run on it
            print(f"report script failed: {e}")
    return out


def capture_report(name: str, title: str, main) -> None:
    """Run a report's `main()`, echo to stdout, and also save it as results/md/<name>.md."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    text = buf.getvalue()
    sys.stdout.write(text)
    out = MD / f"{name}.md"
    out.write_text(f"# {title}\n\n_Regenerated {time.strftime('%Y-%m-%d %H:%M:%S')} from all rows in `results/`._\n\n```\n{text}```\n")
    sys.stdout.write(f"\nreport -> {out.relative_to(ROOT)}\n")
