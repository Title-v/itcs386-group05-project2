"""Turn a k6 CSV time series into a timeline table and the numbers the project questions ask for.

Usage: python analyze_timeline.py <timeseries.csv[.gz]> <average-load|stress|soak|spike> [--bucket SECONDS]
"""

import argparse
import csv
import gzip
from pathlib import Path
import statistics
import sys

SLOW_MS = 1000  # the brief's "response time above 1 second"
ERROR_LIMIT = 0.01  # more than 1% failed requests counts as a problem
MIN_REQUESTS = 10  # ignore buckets with too few requests to judge


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round(p / 100 * len(ordered) + 0.5) - 1))
    return ordered[index]


class Bucket:
    def __init__(self, start):
        self.start = start
        self.vus = 0
        self.durations = []
        self.failed = 0
        self.checks_total = 0
        self.checks_passed = 0

    @property
    def requests(self):
        return len(self.durations)

    @property
    def p95(self):
        return percentile(self.durations, 95)

    @property
    def avg(self):
        return statistics.fmean(self.durations) if self.durations else None

    @property
    def error_rate(self):
        return self.failed / self.requests if self.requests else 0.0

    @property
    def check_rate(self):
        return self.checks_passed / self.checks_total if self.checks_total else None


def load(path, bucket_seconds):
    opener = gzip.open if str(path).endswith(".gz") else open
    buckets, t0 = {}, None
    with opener(path, "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if "endpoint=setup" in (row.get("extra_tags") or "") or row.get("group") == "::setup":
                continue
            ts = float(row["timestamp"])
            if t0 is None:
                t0 = ts
            key = int((ts - t0) // bucket_seconds)
            bucket = buckets.setdefault(key, Bucket(key * bucket_seconds))
            name, value = row["metric_name"], float(row["metric_value"])
            if name == "vus":
                bucket.vus = max(bucket.vus, int(value))
            elif name == "http_req_duration":
                bucket.durations.append(value)
            elif name == "http_req_failed":
                bucket.failed += int(value)
            elif name == "checks":
                bucket.checks_total += 1
                bucket.checks_passed += int(value)
    # Fill in VUs for buckets that had requests but no vus sample.
    ordered = [buckets[k] for k in sorted(buckets)]
    for previous, current in zip(ordered, ordered[1:]):
        if current.vus == 0 and current.requests:
            current.vus = previous.vus
    return ordered


def clock(seconds):
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"


def ms(value):
    return "-" if value is None else f"{value:.0f}"


def judged(buckets):
    return [b for b in buckets if b.requests >= MIN_REQUESTS]


def capacity_findings(buckets):
    """Q1 and Q2: highest VUs with p95 <= 1 s, and the first point where problems appear."""
    lines = []
    good = judged(buckets)
    first_slow = next((b for b in good if b.p95 > SLOW_MS), None)
    if first_slow is None:
        top = max((b.vus for b in good), default=0)
        lines.append(f"- p95 stayed at or under {SLOW_MS} ms in every {BUCKET}s window, up to **{top} VUs**.")
    else:
        before = [b.vus for b in good if b.start < first_slow.start and b.p95 <= SLOW_MS]
        lines.append(
            f"- p95 first went above {SLOW_MS} ms at **{clock(first_slow.start)}** with **{first_slow.vus} VUs** "
            f"(p95 {ms(first_slow.p95)} ms). Highest load before that with p95 <= {SLOW_MS} ms: "
            f"**{max(before, default=0)} VUs**."
        )
    first_problem = next((b for b in good if b.p95 > SLOW_MS or b.error_rate > ERROR_LIMIT), None)
    if first_problem is None:
        lines.append(f"- No window had p95 > {SLOW_MS} ms or errors > {ERROR_LIMIT:.0%}.")
    else:
        lines.append(
            f"- First sign of problems (p95 > {SLOW_MS} ms or errors > {ERROR_LIMIT:.0%}) at "
            f"**{clock(first_problem.start)}** with **{first_problem.vus} VUs**: p95 {ms(first_problem.p95)} ms, "
            f"errors {first_problem.error_rate:.1%}."
        )
    return lines


def soak_findings(buckets):
    """Q3: compare the first and last third of the steady part of the test."""
    peak = max((b.vus for b in buckets), default=0)
    steady = [b for b in judged(buckets) if b.vus >= 0.9 * peak]
    if len(steady) < 3:
        return ["- Not enough steady-load windows to compare (run longer, or use a smaller --bucket)."]
    third = len(steady) // 3
    first, last = steady[:third], steady[-third:]

    def describe(part):
        durations = [d for b in part for d in b.durations]
        failed = sum(b.failed for b in part)
        return percentile(durations, 95), statistics.fmean(durations), failed / len(durations)

    p95_a, avg_a, err_a = describe(first)
    p95_b, avg_b, err_b = describe(last)
    xs = [b.start / 60 for b in steady]
    ys = [b.p95 for b in steady]
    slope = statistics.linear_regression(xs, ys).slope if len(set(xs)) > 1 else 0.0
    change = (p95_b - p95_a) / p95_a if p95_a else 0.0
    verdict = "got worse" if change > 0.2 or err_b > err_a + ERROR_LIMIT else "stayed stable"
    return [
        f"- Steady part: {clock(steady[0].start)} to {clock(steady[-1].start + BUCKET)} at {peak} VUs.",
        f"- First third: p95 {ms(p95_a)} ms, avg {ms(avg_a)} ms, errors {err_a:.2%}.",
        f"- Last third: p95 {ms(p95_b)} ms, avg {ms(avg_b)} ms, errors {err_b:.2%} (p95 change {change:+.0%}).",
        f"- Trend of window p95: {slope:+.1f} ms per minute. Verdict: response time and errors **{verdict}**.",
    ]


def spike_findings(buckets):
    """Q4: time from the end of the spike until p95 and errors are back near the baseline."""
    peak = max((b.vus for b in buckets), default=0)
    spike = [b for b in buckets if b.vus > 0.5 * peak]
    if not spike:
        return ["- No spike found in the VU series."]
    spike_start, spike_end = spike[0].start, spike[-1].start + BUCKET
    pre = [b for b in judged(buckets) if b.start + BUCKET <= spike_start]
    baseline = pre[1:] if len(pre) > 2 else pre  # skip the warm-up window
    if not baseline:
        return ["- No baseline windows before the spike."]
    base_p95 = statistics.median(b.p95 for b in baseline)
    base_err = statistics.fmean(b.error_rate for b in baseline)
    limit = max(base_p95 * 1.5, base_p95 + 200)
    during = [b for b in judged(buckets) if spike_start <= b.start < spike_end]
    after = [b for b in judged(buckets) if b.start >= spike_end and b.vus > 0]

    def normal(b):
        return b.p95 <= limit and b.error_rate <= base_err + ERROR_LIMIT

    recovered = next((a for a, b in zip(after, after[1:] + [None]) if normal(a) and (b is None or normal(b))), None)
    lines = [
        f"- Baseline before the spike: p95 {ms(base_p95)} ms, errors {base_err:.2%}. "
        f"\"Normal\" means p95 <= {ms(limit)} ms and errors <= {base_err + ERROR_LIMIT:.2%} for two windows in a row.",
        f"- Spike: {clock(spike_start)} to {clock(spike_end)}, up to {peak} VUs. Worst window p95 "
        f"{ms(max((b.p95 for b in during), default=None))} ms, worst errors "
        f"{max((b.error_rate for b in during), default=0):.1%}.",
    ]
    if recovered is None:
        lines.append("- **Did not return to normal** before the test ended.")
    else:
        lines.append(
            f"- Back to normal at {clock(recovered.start)}: about **{max(0, recovered.start - spike_end):.0f} s** "
            f"after the spike ended (window size {BUCKET} s, so the answer is accurate to about {BUCKET} s)."
        )
    return lines


def metric_notes(buckets):
    """Q5 inputs: overall http_req_failed, http_req_duration and peak VUs for this run."""
    durations = [d for b in buckets for d in b.durations]
    failed = sum(b.failed for b in buckets)
    return [
        f"- Requests: {len(durations)}; http_req_failed: {failed / len(durations):.2%}; "
        f"http_req_duration avg {ms(statistics.fmean(durations))} ms, p95 {ms(percentile(durations, 95))} ms, "
        f"max {ms(max(durations))} ms; peak VUs: {max(b.vus for b in buckets)}.",
    ]


def report(path, test, bucket_seconds):
    global BUCKET
    BUCKET = bucket_seconds
    buckets = load(path, bucket_seconds)
    if not any(b.requests for b in buckets):
        return f"# Timeline analysis: {test}\n\nNo HTTP requests found in {path}.\n"
    out = [f"# Timeline analysis: {test}", "", f"Source: `{Path(path).name}`, {bucket_seconds} s windows.", ""]
    out += ["## Overall", ""] + metric_notes(buckets) + [""]
    out += ["## Load vs response time (Q1, Q2)", ""] + capacity_findings(buckets) + [""]
    if test == "soak":
        out += ["## Soak trend (Q3)", ""] + soak_findings(buckets) + [""]
    if test == "spike":
        out += ["## Spike recovery (Q4)", ""] + spike_findings(buckets) + [""]
    out += [
        "## Timeline",
        "",
        "| Time | VUs | Requests | Req/s | Avg ms | p95 ms | Errors | Checks passed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for b in buckets:
        checks = "-" if b.check_rate is None else f"{b.check_rate:.1%}"
        out.append(
            f"| {clock(b.start)} | {b.vus} | {b.requests} | {b.requests / bucket_seconds:.1f} | {ms(b.avg)} | "
            f"{ms(b.p95)} | {b.error_rate:.1%} | {checks} |"
        )
    return "\n".join(out) + "\n"


BUCKET = 30


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_path")
    parser.add_argument("test", choices=["average-load", "stress", "soak", "spike"])
    parser.add_argument("--bucket", type=int, help="window size in seconds (default 10 for spike, 30 otherwise)")
    args = parser.parse_args()
    bucket = args.bucket or (10 if args.test == "spike" else 30)
    sys.stdout.write(report(args.csv_path, args.test, bucket))


if __name__ == "__main__":
    main()
