"""Run one k6 test and save dated evidence: console log, k6 summary, time series and timeline analysis.

Usage (from anywhere):
    python "Performance testing/run_perf_test.py" average-load
    python "Performance testing/run_perf_test.py" spike --quick        # about 1 minute, for demos
    python "Performance testing/run_perf_test.py" soak -e SOAK_HOLD=90m
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from analyze_timeline import report

HERE = Path(__file__).resolve().parent
TESTS = ["average-load", "stress", "soak", "spike"]
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
PROGRESS = re.compile(r"^\s*(running \(|default\s+[\[↓✓✗])")
EXIT_MEANING = {0: "passed: all thresholds met", 99: "thresholds crossed (see summary.txt)", 107: "script error"}


def bangkok(moment):
    return (moment + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S +07:00")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("test", choices=TESTS)
    parser.add_argument("--quick", action="store_true", help="every stage at 1/10 length (demo or smoke run)")
    parser.add_argument("--k6", default=os.environ.get("K6", "k6"), help="path to the k6 executable")
    parser.add_argument("-e", "--env", action="append", default=[], metavar="KEY=VALUE", help="extra k6 -e variable")
    args = parser.parse_args()

    k6 = shutil.which(args.k6) or args.k6
    if not Path(k6).exists() and not shutil.which(k6):
        sys.exit("k6 not found. Install it (winget install k6 / choco install k6 / brew install k6) or pass --k6 PATH.")

    started = datetime.now(timezone.utc)
    name = f"{started.strftime('%Y%m%dT%H%M%SZ')}-{args.test}{'-quick' if args.quick else ''}"
    out_dir = Path("results") / name
    (HERE / out_dir).mkdir(parents=True)
    csv_path = out_dir / "timeseries.csv.gz"

    command = [k6, "run", "--out", f"csv={csv_path.as_posix()}", "-e", f"OUT_DIR={out_dir.as_posix()}"]
    if args.quick:
        command += ["-e", "QUICK=1"]
    for item in args.env:
        command += ["-e", item]
    command.append(f"{args.test}.js")

    version = subprocess.run([k6, "version"], capture_output=True, text=True).stdout.strip()
    print(f"{args.test}: started {bangkok(started)} (Bangkok); evidence in Performance testing/{out_dir.as_posix()}", flush=True)

    saved, progress_seen = [], 0
    process = subprocess.Popen(command, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               encoding="utf-8", errors="replace")
    for line in process.stdout:
        print(line, end="", flush=True)
        clean = ANSI.sub("", line)
        if PROGRESS.match(clean):
            progress_seen += 1
            if progress_seen % 30:  # keep one progress line in 30 so the saved log stays readable
                continue
        saved.append(clean)
    exit_code = process.wait()
    ended = datetime.now(timezone.utc)
    (HERE / out_dir / "console.txt").write_text("".join(saved), encoding="utf-8")

    analysis = None
    if (HERE / csv_path).exists():
        bucket = 5 if args.quick else (10 if args.test == "spike" else 30)
        analysis = report(HERE / csv_path, args.test, bucket)
        (HERE / out_dir / "analysis.md").write_text(analysis, encoding="utf-8")
        print("\n" + analysis)

    run = {
        "test": args.test,
        "quick_mode": args.quick,
        "started_utc": started.isoformat(timespec="seconds"),
        "ended_utc": ended.isoformat(timespec="seconds"),
        "started_bangkok": bangkok(started),
        "ended_bangkok": bangkok(ended),
        "k6_version": version,
        "command": " ".join(command[1:]),
        "k6_exit_code": exit_code,
        "outcome": EXIT_MEANING.get(exit_code, "k6 stopped with an error (see console.txt)"),
        "files": sorted(p.name for p in (HERE / out_dir).iterdir()),
    }
    (HERE / out_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    print(f"Outcome: {run['outcome']} (exit {exit_code}). Saved in Performance testing/{out_dir.as_posix()}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
