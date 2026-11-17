# ITCS386 Group 5 — Project 2

Testing the classroom WooCommerce shop at http://157.85.102.236/shop/ with the Group 05 account. Credentials stay outside the repository.

## Current deliverables

Status below was checked against committed evidence on **18 November 2026 (Asia/Bangkok)**. This is not a new live test run.

| Part | Folder / evidence | Owner | Recorded status |
|---|---|---|---|
| API testing | [API testing](API%20testing/README.md) | Rattee Watperatam | 17/17 cases passed on 18 Nov 2026 at 00:54 Bangkok |
| System testing | [System testing overview](system%20test/README.md) | Not recorded | Three executed cases: 9, 9 and 7 steps; Test 3 includes a documented input-operation error and successful retest |
| Automated UI testing | No scripts or full-run evidence committed | Not recorded | Not present in this repository snapshot |
| Performance testing | No K6 scripts or run summaries committed | Not recorded | Not present in this repository snapshot |

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

| Case / recorded run | Scenario | Final result | Order at the end of the run | Evidence |
|---|---|---|---|---|
| ST-G05-01 / R02 | Coupon purchase and order completion | 9/9 steps passed | 692 — Completed, 360 THB | [Report and 16 images](system%20test/ST-G05-01-R02-results.md) |
| ST-G05-02 / R01 | Quantity limits, cart edits and remaining stock | 9/9 steps passed | 774 — Processing, 300 THB | [Report and 18 images](system%20test/ST-G05-02-R01-results.md) |
| ST-G05-03 / R01 | Updated price and required-address validation, guest checkout | 7/7 revised checks passed after correcting a test-operation error | 777 — Completed, 225 THB; accidental order 776 cancelled | [Report and 14 images](system%20test/ST-G05-03-R01-results.md) |

See the [complete test cases](system%20test/system-test-cases.md), [requirement traceability matrix](system%20test/api-traceability-matrix.md) and [API inventory](system%20test/api-inventory.md). All three cases use guest shopping; customer login and account history are outside the selected scope. Order statuses above are recorded results, not a fresh server query.

The repository contains **48 distinct system-test images**. Test 3's 14 include 12 step images and 2 incident/cleanup images. Email-notification failures are recorded as environment observations, not silently treated as successful mail delivery.

## Automated UI testing

No automated UI scripts or execution evidence are committed. The project requires at least three system scenarios automated with Selenium WebDriver, Robot Framework or Cypress, with result assertions, repeatable data and full-run evidence.

## Performance testing

No K6 scripts or run summaries are committed. The project requires average-load, stress, soak and spike tests with response-time/error thresholds and analysis. Do not place orders or bookings during load tests.

## Supporting snapshots and final packaging

[Supporting document status](docs/README.md) distinguishes older review exports from current evidence. In particular, the old README preview / Graphify report describe a 15-case API version; the API map is a 17-case snapshot with 11 November run evidence. Use the current API README and dated run files for the latest results.

The current working layout uses top-level `API testing/` and `system test/`. The supplied Project 2 brief requests a final `project phase 2/` folder with `API testing/`, `System testing/`, `UI testing/` and `Performance testing/`, plus its README. Reconcile final submission packaging without treating the current working layout or passing API/system results as completion of the entire project.
