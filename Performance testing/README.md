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

**Normal load is 10 VUs.** This is a small classroom shop on one server. Ten shoppers at once, each with 1–4 s think time, send roughly 5 requests per second (estimated from the visit: about 8 requests per ~17 s). That is a realistic busy hour for a shop of 14 products, and it leaves room on the server for the other groups.

**p95 < 1 s for average load and soak.** About 1 s is the limit before a shopper notices the site is slow. It is also the limit the brief's first question uses. A single unloaded request to the home page took about 0.55 s on 12 Nov 2026, so 1 s gives a realistic margin. p99 < 2 s keeps the slowest 1% in check. We use p95 rather than the average, because the average hides the slow requests that users actually feel.

**Errors < 1%, checks > 99%.** At normal load the shop should almost never fail. The 1% allows for rare network glitches on a shared server. The checks confirm the pages return the right content (the right category, the right product, a working cart), not just a 200 status.

**Stress: 10 → 50 VUs, p95 < 2 s, errors < 5%.** Stress is expected to slow the shop down. These thresholds mark the most degradation we would still accept. Each step holds for 2 minutes so every load level has enough samples, which lets us name the VU count where problems start. Fifty VUs is 5× normal load. The abort at 30% errors protects the shared server from a test that has already shown its result.

**Soak: 60 minutes at normal load.** An hour is long enough for slow problems to show, such as growing session tables, PHP worker or memory exhaustion, and log growth. It is short enough to be fair to other groups on the shared server. Running it at normal load means any slowdown comes from time, not from extra load.

**Spike: 5 → 50 VUs in 20 s.** This simulates a flash sale (10× the baseline). The 2-minute baseline gives the "normal" response time to compare against. The 5-minute window after the spike is long enough to measure recovery. The looser limits (p95 < 3 s, errors < 10%) accept a short slowdown, but not a collapse.

## Run log

All groups share one server, so every run is recorded with its date and time (Bangkok, UTC+7). The exact times are in each run's `run.json` and `summary.json`.

| Date and time (Bangkok) | Test | Result folder | Outcome | p95 | Errors | Notes (other activity, changes) |
| --- | --- | --- | --- | ---: | ---: | --- |
| _to fill_ | average-load | | | | | |
| _to fill_ | stress | | | | | |
| _to fill_ | soak | | | | | |
| _to fill_ | spike | | | | | |

If a repeated run gives different numbers, write down the likely cause. Typical causes on this server: other groups running load or UI tests at the same time (check their timestamps), WordPress caches being cold on the first run, or time of day.

## Results and answers

_To be filled from the full runs: each answer quotes the numbers in that run's `summary.txt` and `analysis.md`._

**1. How many virtual users can the system serve before the response time goes above 1 second?**
Source: the stress run's `analysis.md`, "Load vs response time". It gives the highest VU count whose 30 s windows still had p95 ≤ 1 s.

**2. In the stress test, at how many virtual users does the system start to show problems?**
Source: the stress run's `analysis.md`, "First sign of problems" (the first window with p95 > 1 s or errors > 1%). Compare it with the failed checks and thresholds in `summary.txt`.

**3. In the soak test, do the response time or the error rate get worse as the test goes on?**
Source: the soak run's `analysis.md`, "Soak trend". It compares the first and last third of the hour, with the p95 trend in ms per minute.

**4. In the spike test, how long does the system take to return to normal service after the spike?**
Source: the spike run's `analysis.md`, "Spike recovery". It gives the seconds from the end of the spike until p95 and errors are back near the baseline for two 10 s windows in a row.

**5. What do `http_req_failed`, `http_req_duration` and `vus_max` tell you about the system in each test?**

| Test | `http_req_failed` | `http_req_duration` (avg / p95 / max) | `vus_max` | What it means |
| --- | --- | --- | --- | --- |
| Average load | | | | |
| Stress | | | | |
| Soak | | | | |
| Spike | | | | |

- `http_req_failed` is the share of requests with an error status (4xx/5xx) or no response. It shows whether the shop stayed **available**.
- `http_req_duration` is the time to complete a request. It shows how **fast** the shop felt; p95 is the experience of the slowest 5% of requests.
- `vus_max` is the most VUs k6 allocated in the run. It shows how much **concurrent load** the other two numbers were measured under.
