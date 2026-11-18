# ITCS386 Group 5 — Project 2

Testing the classroom WooCommerce shop at http://157.85.102.236/shop/ with the Group 05 account. Credentials stay outside the repository.

## Current deliverables

System-test evidence was refreshed on **19 November 2026 (Asia/Bangkok)**. Other sections retain their own dated run evidence.

| Part | Folder / evidence | Owner | Recorded status |
|---|---|---|---|
| API testing | [API testing](API%20testing/README.md) | Rattee Watperatam | 17/17 cases passed on 18 Nov 2026 at 00:54 Bangkok |
| System testing | [System testing overview](system%20test/README.md) | Not recorded | Rerun 19 Nov 2026: Test 1 9/9, Test 2 9/9, Test 3 7/7; 56 page-only screenshots |
| Automated UI testing | No scripts or full-run evidence committed | Not recorded | Not present in this repository snapshot |
| Performance testing | [Performance testing](Performance%20testing/README.md) | Not recorded | Four full runs completed on 17 Nov 2026; average-load and soak passed thresholds; stress and spike exceeded response-time limits; 0 failed requests |

Computer Use execution of the manual system cases is not the separate Selenium / Robot Framework / Cypress deliverable.

## API testing

Three product operations are tested with pytest using input space partitioning and Base Choice Coverage:

| API suite | Operation relative to /shop/wp-json | Cases |
|---|---|---:|
| S01 | GET /wc/store/v1/products | 7 |
| S02 | GET /wc/store/v1/products/{id} | 5 |
| S03 | POST /wc/v3/products | 5 |

After setting `SHOP_USER` and `SHOP_API_PASSWORD`, run all suites from the repository root:

```bash
python run_api_tests.py
```

Latest recorded result: **17 passed, 0 failures/errors/skips**, 18 November 2026 at 00:54 Bangkok. See the [API README](API%20testing/README.md), [console](API%20testing/results/20261117T175415Z-8f6731af/console.txt), [JUnit report](API%20testing/results/20261117T175415Z-8f6731af/junit.xml) and [latest-run metadata](API%20testing/results/latest-run.json). The latest run's source hashes match the currently committed test sources.

API suite IDs and the system document's API inventory IDs are separate namespaces: API suite **S03** (product creation) maps to inventory **A02**, not inventory S03 (categories).

## System testing

| Case / run | Scenario | Result | Order at end of run | Evidence |
|---|---|---|---|---|
| ST-G05-01 / R04 | Purchase with a coupon and complete the order | 9/9 Pass | 1252 — Completed, 360 THB | [Report and 20 images](system%20test/ST-G05-01-results.md) |
| ST-G05-02 / R02 | Validate quantity limits and remaining stock | 9/9 Pass | 1260 — Processing, 300 THB | [Report and 21 images](system%20test/ST-G05-02-results.md) |
| ST-G05-03 / R02 | Verify updated pricing and required-address validation for a guest purchase | 7/7 Pass | 1274 — Completed, 225 THB | [Report and 15 images](system%20test/ST-G05-03-results.md) |

See the [current test cases](system%20test/system-test-cases.md) and [tested-requirement matrix](system%20test/api-traceability-matrix.md). All new screenshots exclude browser tabs, URL bars and mouse-pointer overlays. Blank-form and pre-Publish screenshots make product creation explicit. The matrix contains only 14 requirements actually checked.

All three runs used guest shopping and new test products on 19 November 2026. Reported dates use Asia/Bangkok; the shop displays its server date. Mail-function errors are recorded separately from the case assertions. These results are not claims of complete specification or direct API coverage.

## Automated UI testing

No automated UI scripts or execution evidence are committed. The project requires at least three system scenarios automated with Selenium WebDriver, Robot Framework or Cypress, with result assertions, repeatable data and full-run evidence.

## Performance testing

Four k6 tests of a shopper journey through the public Store API (home page, browse a category, search, product page, add/update/remove cart item). No orders are placed, and only demo products are used:

- Average load: 10 VUs for 6 min (p95 < 1 s, errors < 1%)
- Stress: 10 → 50 VUs in steps of 10 (p95 < 2 s, errors < 5%)
- Soak: 10 VUs for 60 min (p95 < 1 s, errors < 1%)
- Spike: 5 → 50 → 5 VUs with a 5 min recovery window (p95 < 3 s, errors < 10%)

Run one test from the repository root (k6 must be installed; no credentials needed):

```bash
python "Performance testing/run_perf_test.py" average-load    # or stress / soak / spike; add --quick for a 1-minute demo
```

Results of the full runs on 17 Nov 2026: at normal load the shop is fast (p95 ≈ 0.3 s) and stays that way for an hour. It keeps p95 under 1 s up to about 30 VUs, then levels off at about 13 requests/s and slows down (p95 6–7 s at 50 VUs; the home page is the bottleneck), but **no request failed in any test**. After a 10× spike it is back to normal about 10 s after the load drops.

Each run saves its k6 summary, time series and timeline analysis in `Performance testing/results/<UTC time>-<test>/`. Thresholds, their reasons, the run log and the answers to the analysis questions are in [Performance testing/README.md](Performance%20testing/README.md).

All four full runs completed. Average-load and soak met their thresholds; stress and spike exceeded response-time thresholds while recording no failed requests.

## Supporting snapshots and final packaging

[Supporting document status](docs/README.md) distinguishes older review exports from current evidence. In particular, the old README preview / Graphify report describe a 15-case API version; the API map is a 17-case snapshot with 11 November run evidence. Use the current API README and dated run files for the latest results.

The current working layout uses top-level `API testing/` and `system test/`. The supplied Project 2 brief requests a final `project phase 2/` folder with `API testing/`, `System testing/`, `UI testing/` and `Performance testing/`, plus its README. Reconcile final submission packaging without treating the current working layout or passing API/system results as completion of the entire project.
