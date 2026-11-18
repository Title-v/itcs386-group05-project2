# Performance testing

Four k6 load tests on the WooCommerce shop at http://157.85.102.236/shop/: average load, stress, soak and spike.

## What a virtual user does

Each virtual user (VU) acts as one shopper. It repeats this visit, pausing 1–4 s between steps the way a real person reads a page:

| Step | Request | Checks |
| --- | --- | --- |
| 1 Home page | `GET /shop/` (HTML) | status 200, the shop page is rendered |
| 2 Browse a category | `GET /wc/store/v1/products/categories`, then `GET /products?category={id}&orderby=…` | status 200, products returned, all in the chosen category |
| 3 Search | `GET /products?search={term}` (hoodie, beanie, shirt, …) | status 200, at least one result |
| 4 Product page | `GET /products/{id}` | status 200, same id, price in THB |
| 5 Cart (half of visits) | `POST /cart/add-item` → `update-item` (qty 2) → `remove-item` | product added, quantity changed, line removed |

The scripts follow the brief's rules for a shared server:

- **No orders are placed.** Every cart is emptied again at the end of the visit, so no stock or orders are touched.
- **Only demo products are used.** `setup()` reads the demo categories and keeps simple, purchasable products. It skips anything named `G01…`, `G05…` or `Product`, so other groups' data is never read or changed.
- **One cart per VU.** Each VU gets its own `Cart-Token` once and reuses it, as the API guide asks. A run creates at most one cart session per VU.
- **No credentials.** The Store API is public, and no group password appears in the scripts.

## Files

| File | Purpose |
| --- | --- |
| [average-load.js](average-load.js), [stress.js](stress.js), [soak.js](soak.js), [spike.js](spike.js) | The four k6 tests (load shape and thresholds) |
| [lib/shopper.js](lib/shopper.js) | The shopper visit and checks shared by all tests |
| [lib/config.js](lib/config.js) | Target URL, think time, `QUICK` mode, summary writer |
| [run_perf_test.py](run_perf_test.py) | Runs one test and saves dated evidence |
| [analyze_timeline.py](analyze_timeline.py) | Turns the k6 time series into a per-window timeline and the answers below |
| `results/<UTC time>-<test>/` | One folder per run (see below) |

Each run folder contains:

- `summary.txt`: the k6 end-of-test summary. Each threshold is marked ✓ or ✗.
- `summary.json`: the same summary, plus the run's start and end time in UTC and Bangkok time.
- `timeseries.csv.gz`: every k6 metric sample from the run.
- `analysis.md`: a 30 s (spike: 10 s) timeline of VUs, requests per second, average and p95 response time, error rate and checks passed, plus the derived answers.
- `console.txt` and `run.json`: the k6 console output, plus the k6 version, command and exit code.

## How to run

Install k6 (`winget install k6`, `choco install k6` or `brew install k6`) and Python 3.10+. From the repository root:

```bash
python "Performance testing/run_perf_test.py" average-load   # ~9 min
python "Performance testing/run_perf_test.py" stress         # ~17 min
python "Performance testing/run_perf_test.py" spike          # ~10 min
python "Performance testing/run_perf_test.py" soak           # ~64 min (-e SOAK_HOLD=90m to lengthen)
```

`--quick` runs any test at one tenth of its length with the same VU targets (about 1 minute for average-load or spike). Use it for the progress presentation demo or a smoke check. Quick runs are saved in `-quick` folders and are **not** used for the answers below.

The runner exits with k6's exit code: `0` means all thresholds were met, and `99` means at least one threshold was crossed. You can also run plain k6 from this folder, for example `k6 run average-load.js`; the summary then goes to `results/` but there is no time series or analysis.

## Test design

| Test | VUs | Shape and duration | Thresholds |
| --- | --- | --- | --- |
| Average load | 10 | 2 m ramp, **6 m at 10 VUs**, 1 m down (9 m) | p95 < 1 s, p99 < 2 s, errors < 1%, checks > 99% |
| Stress | 10 → 50 | 5 steps of +10 VUs (1 m ramp + 2 m hold each), 2 m down (17 m) | p95 < 2 s, errors < 5%, checks > 95%; **abort** if errors > 30% |
| Soak | 10 | 2 m ramp, **60 m at 10 VUs**, 2 m down (64 m) | same as average load |
| Spike | 5 → 50 → 5 | 2.5 m baseline at 5, jump to 50 in 20 s, hold 1 m, drop to 5 in 20 s, **5 m recovery**, 30 s down (≈10 m) | p95 < 3 s, errors < 10%, checks > 90%; **abort** if errors > 50% |

Every test also sets the same p95 limit on each endpoint (`http_req_duration{endpoint:…}`), so the summary shows which step is slowest.

### Why these numbers

**Normal load is 10 VUs.** This is a small classroom shop on one server. Ten shoppers at once, each with 1–4 s think time, send roughly 4–5 requests per second. The average-load run measured 6.6 requests per visit and 14.7 s per visit, which is 4.4 requests per second at a steady 10 VUs. That is a realistic busy hour for a shop of 14 products, and it leaves room on the server for the other groups.

**p95 < 1 s for average load and soak.** About 1 s is the limit before a shopper notices the site is slow. It is also the limit the brief's first question uses. A single unloaded request to the home page took about 0.55 s on 12 Nov 2026, so 1 s gives a realistic margin. p99 < 2 s keeps the slowest 1% in check. We use p95 rather than the average, because the average hides the slow requests that users actually feel.

**Errors < 1%, checks > 99%.** At normal load the shop should almost never fail. The 1% allows for rare network glitches on a shared server. The checks confirm the pages return the right content (the right category, the right product, a working cart), not just a 200 status.

**Stress: 10 → 50 VUs, p95 < 2 s, errors < 5%.** Stress is expected to slow the shop down. These thresholds mark the most degradation we would still accept. Each step holds for 2 minutes so every load level has enough samples, which lets us name the VU count where problems start. Fifty VUs is 5× normal load. The abort at 30% errors protects the shared server from a test that has already shown its result.

**Soak: 60 minutes at normal load.** An hour is long enough for slow problems to show, such as growing session tables, PHP worker or memory exhaustion, and log growth. It is short enough to be fair to other groups on the shared server. Running it at normal load means any slowdown comes from time, not from extra load.

**Spike: 5 → 50 VUs in 20 s.** This simulates a flash sale (10× the baseline). The 2-minute baseline gives the "normal" response time to compare against. The 5-minute window after the spike is long enough to measure recovery. The looser limits (p95 < 3 s, errors < 10%) accept a short slowdown, but not a collapse.

## Run log

All groups share one server, so every run is recorded with its date and time (Bangkok, UTC+7). The exact times are in each run's `run.json` and `summary.json`.

| Date and time (Bangkok) | Test | Result folder | Outcome | p95 | Errors | Notes (other activity, changes) |
| --- | --- | --- | --- | ---: | ---: | --- |
| 17 Nov 2026 16:05–16:06 | average-load `--quick` | [20261117T090525Z-average-load-quick](results/20261117T090525Z-average-load-quick/) | ✓ passed | 323 ms | 0.00% | Smoke run for the demo. Not used for the answers. |
| 17 Nov 2026 16:06–16:15 | average-load | [20261117T090645Z-average-load](results/20261117T090645Z-average-load/) | ✓ passed | 304 ms | 0.00% | |
| 17 Nov 2026 16:15–16:33 | stress | [20261117T091557Z-stress](results/20261117T091557Z-stress/) | ✗ p95 < 2 s crossed (overall and `home`) | 2.87 s | 0.00% | Expected for a stress test. No abort: errors stayed at 0. |
| 17 Nov 2026 16:33–16:42 | spike | [20261117T093314Z-spike](results/20261117T093314Z-spike/) | ✗ p95 < 3 s crossed (overall and `home`) | 3.81 s | 0.00% | Expected during a 10× spike. No abort. |
| 17 Nov 2026 16:42–17:47 | soak | [20261117T094257Z-soak](results/20261117T094257Z-soak/) | ✓ passed | 317 ms | 0.00% | One short bump at 41:30–43:30 (≈17:24–17:27): window p95 up to 875 ms, then straight back to ~300 ms. Our load was flat, so it was most likely another group using the server. |

The four full runs ran one after another, so they never overlapped each other. The normal-load response time was the same in every run that had a normal-load phase: p95 304 ms (average load), 317 ms (soak), 303–355 ms per window in the 10-VU step of the stress test, and a 314 ms baseline in the spike test. So the runs are consistent with each other. Apart from the soak bump above, nothing suggests other groups were loading the server during our runs. If a repeated run gives different numbers, write down the likely cause. Typical causes on this server: other groups running load or UI tests at the same time (check their timestamps), WordPress caches being cold on the first run, or time of day.

The request counts in `analysis.md` are a few lower than in `summary.txt`, because the analysis leaves out the catalogue requests made once in `setup()`.

## Results and answers

All numbers come from the full runs above. The overall figures are from each run's `summary.txt`, and the per-window figures are from its `analysis.md`.

**1. How many virtual users can the system serve before the response time goes above 1 second?**

**About 30 VUs.** In the stress run, every 30 s window up to and including the 30-VU step had p95 ≤ 1 s (the 30-VU hold: 628–778 ms). p95 first went above 1 s at **34 VUs**, while ramping from 30 to 40 (window 09:00, p95 1.31 s). At the 40-VU step it was 2.3–4.1 s. The spike test agrees: the window with 25 VUs had p95 371 ms, and the next one, at 48 VUs, had 3.4 s. At the normal load of 10 VUs the shop is fast: p95 304 ms.

**2. In the stress test, at how many virtual users does the system start to show problems?**

**Between 30 and 40 VUs: the first problem window was at 34 VUs** (p95 > 1 s). The problem is **slowness, not errors**. All 10,075 requests succeeded (`http_req_failed` 0.00%) and all 23,985 checks passed. The cause is visible in the timeline:

| Stress step | Requests/s | p95 per window |
| --- | ---: | ---: |
| 10 VUs | 4.3–4.4 | 0.30–0.36 s |
| 20 VUs | 8.5–9.1 | 0.42–0.62 s |
| 30 VUs | 12.3–12.9 | 0.63–0.78 s |
| 40 VUs | 12.3–14.6 | 2.3–4.1 s |
| 50 VUs | 11.6–13.1 | 5.8–6.9 s |

Throughput grows with the VUs up to 30, then **stays at about 13 requests/s** however many VUs are added. That is the server's capacity for this traffic mix. Beyond it, extra requests wait in a queue (probably for a free PHP worker), so response time climbs while nothing fails. The full-HTML **home page is the bottleneck**. Its p95 reached 6.61 s and crossed the per-endpoint limit, while every JSON Store API call stayed under 2 s (p95 1.3–1.9 s). The test crossed its p95 < 2 s threshold (overall 2.87 s), but not the error or check thresholds.

**3. In the soak test, do the response time or the error rate get worse as the test goes on?**

**No.** Over the hour at 10 VUs (steady part 01:30–63:00):

| Part of the hour | p95 | Average | Errors |
| --- | ---: | ---: | ---: |
| First third | 318 ms | 128 ms | 0.00% |
| Last third | 323 ms | 130 ms | 0.00% |

That is a +2% change, and the trend of the window p95 is +0.2 ms per minute, which is within normal variation. There were no failed requests in 16,602 (`http_req_failed` 0.00%), and all thresholds passed. The only bump (≈17:24–17:27, see the run log) recovered by itself. So within one hour there is no sign of a memory leak, of growing sessions or of a gradual slowdown.

**4. In the spike test, how long does the system take to return to normal service after the spike?**

**About 10 seconds after the load starts to fall.**
- **Baseline at 5 VUs:** p95 314 ms.
- **During the spike to 50 VUs (02:40–04:00):** the worst 10 s window had p95 7.3 s, but there were no errors.
- **Load starts to fall:** 04:00. The 04:00–04:10 window was still slow (p95 2.8 s) while the queue cleared.
- **Back to normal:** from the 04:10 window on, p95 was 151 ms, then about 280 ms, which is within "normal" (p95 ≤ 514 ms, that is, 1.5× the baseline, for two windows in a row).

A 5 s breakdown shows the same thing: p95 was 4.4 s at 04:00–04:05 and 337 ms at 04:05–04:10. After that, p95 stayed at its baseline level (250–460 ms) for the rest of the 5-minute recovery window. So the shop recovers almost at once and there is no lasting harm. It slows down a lot during a spike, but it does not fail.

**5. What do `http_req_failed`, `http_req_duration` and `vus_max` tell you about the system in each test?**

| Test | `http_req_failed` | `http_req_duration` (avg / p95 / max) | `vus_max` | What it means |
| --- | --- | --- | --- | --- |
| Average load | 0.00% (0 of 2,056) | 122 ms / 304 ms / 506 ms | 10 | At normal load the shop is fully available and fast. Even the slowest request was about 0.5 s. |
| Stress | 0.00% (0 of 10,075) | 776 ms / 2.87 s / 9.8 s | 50 | It stays available up to 5× normal load, but it gets slow. The high p95 and max come from the 40–50 VU steps, beyond the ~30 VU capacity. |
| Soak | 0.00% (0 of 16,602) | 128 ms / 317 ms / 1.55 s | 10 | Same speed as average load, for a whole hour. One slow request (1.55 s, home page) during the bump. No wear-out over time. |
| Spike | 0.00% (0 of 2,417) | 796 ms / 3.81 s / 8.4 s | 50 | A sudden 10× jump makes the shop slow for about 1.5 minutes but causes no errors. Speed returns about 10 s after the load drops. |

- `http_req_failed` is the share of requests with an error status (4xx/5xx) or no response. It shows whether the shop stayed **available**.
- `http_req_duration` is the time to complete a request. It shows how **fast** the shop felt; p95 is the experience of the slowest 5% of requests.
- `vus_max` is the most VUs k6 allocated in the run. It shows how much **concurrent load** the other two numbers were measured under.
