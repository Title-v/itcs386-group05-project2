# itcs386-group05-project2
ITCS386 Group 5 — Project 2: API, system, automated UI, and performance testing of WooCommerce.

System under test: the classroom WooCommerce shop at http://157.85.102.236/shop/ (Group 05 account). Never commit passwords or API keys; pass them as environment variables.

## Parts

| Part | Folder | Owner | Status |
| --- | --- | --- | --- |
| API testing | [`API testing/`](API%20testing/) | Rattee Watperatam | 17/17 passed (11 Nov 2026) |
| System testing | [`system test/`](system%20test/) | | |
| UI testing | | | |
| Performance testing | [`Performance testing/`](Performance%20testing/) | | Scripts ready; full runs pending |

Each owner fills in their row and their section below, and keeps the details in their own folder's README.

## API testing

Three product API operations, tested with pytest. Inputs come from input space partitioning with Base Choice Coverage (17 cases):

- S01 `GET /wc/store/v1/products` — list/search products (7 cases)
- S02 `GET /wc/store/v1/products/{id}` — read one product (5 cases)
- S03 `POST /wc/v3/products` — create a product (5 cases)

Run all suites with one command from the repository root (set `SHOP_USER` and `SHOP_API_PASSWORD` first):

```bash
python run_api_tests.py
```

Latest full run: 17 passed on 11 Nov 2026. Characteristics, blocks, test values, setup and results are in [API testing/README.md](API%20testing/README.md).

## System testing

<!-- Owner: scope, the 3+ manual test cases, traceability matrix, screenshots, results and defects. -->

See [`system test/`](system%20test/).

## UI testing

<!-- Owner: tool (Selenium / Robot Framework / Cypress), the 3+ automated cases from the system tests, how to run them in one command, and the full-run screenshots or recording. -->

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

Each run saves its k6 summary, time series and timeline analysis in `Performance testing/results/<UTC time>-<test>/`. Thresholds, their reasons, the run log and the answers to the analysis questions are in [Performance testing/README.md](Performance%20testing/README.md).
