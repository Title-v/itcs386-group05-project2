# itcs386-group05-project2
ITCS386 Group 5 — Project 2: API, system, automated UI, and performance testing of WooCommerce.

Selected system: WooCommerce shop, ITCS386 Group 05 (OpenAI).

API implementation: 3 operation suites / 17 parametrized test cases. On 11 November 2026, S02 gained an interface-based characteristic (2 new cases) and every case gained its own goal comment. Verified against the real classroom shop on 11 November 2026 (Bangkok): 17/17 pass in one full run. The 9 November runs below cover the earlier 15 cases. System test documents are in [`system test/`](system%20test/). UI testing and Performance testing are not in this repository yet; this is NOT a claim that Phase 2 is complete.

## API testing: start here

The tests call the existing classroom system; they do not edit site code, plugins, themes or settings. Creating products is an existing Shop manager operation in the instructor's WooCommerce API guide, sections 1 and 5.3.

| Suite | Operation, relative to `/shop/wp-json` | Cases | Source |
| --- | --- | ---: | --- |
| S01 | `GET /wc/store/v1/products` — list/search products | 7 | [test_product_list.py](API%20testing/test_product_list.py) |
| S02 | `GET /wc/store/v1/products/{id}` — one product | 5 | [test_product_detail.py](API%20testing/test_product_detail.py) |
| S03 | `POST /wc/v3/products` — create a simple product | 5 | [test_product_create.py](API%20testing/test_product_create.py) |

One Python file is one operation suite. Parametrization executes each row below as a separate test case, and each `pytest.param` row has its own `# Goal:` comment directly above it. The 7 offline ownership/recovery checks under `verification/` are harness verification, NOT additional assignment API cases.

### Run all three suites with one command

From the repository root, use the project's Python environment. Set `SHOP_USER` to your assigned Group 05 username and `SHOP_API_PASSWORD` to its **Shop API password**, not the browser login password. Supply credentials privately as environment variables; never put them in source, screenshots or Git. `SHOP_BASE_URL` is optional and defaults to `http://157.85.102.236/shop`.

```bash
source .venv/bin/activate
python run_api_tests.py
```

On this Mac's zsh, set credentials without putting the password in command history:

```zsh
export SHOP_USER="itcs386-g05"
read -s "SHOP_API_PASSWORD?Shop API password (hidden input): "
export SHOP_API_PASSWORD
python run_api_tests.py
```

Paste the assigned Shop API password at the hidden-input prompt. It is held in the terminal environment, not saved in a source file. Other shells can set the same two environment variables using their own syntax.

The runner uses pytest and saves the full console output, JUnit XML and dated run metadata under `API testing/results/<UTC timestamp>-<run>/`. [latest-run.json](API%20testing/results/latest-run.json) points to the latest execution. HTTP evidence records query/payload inputs and selected response fields, but never Authorization headers or passwords. The runner also redacts configured credentials and local project-root paths from saved output.

To run a particular suite, pass its quoted path, for example:

```bash
python run_api_tests.py "API testing/test_product_list.py"
```

Plain `python -m pytest -v "API testing"` also executes all 17 cases, but use the runner when saving presentation/submission evidence. Missing credentials are reported as setup errors, not silently skipped or counted as passes.

### How to read the ISP design

- **Characteristic**: one property used to classify inputs or their preconditions.
- **Block**: one group within that characteristic. Blocks must be disjoint and cover the declared domain.
- **Base Choice Coverage (BCC)**: one compatible normal base combination, then change one characteristic at a time to each non-base block. Count: `1 + sum(block_count - 1)`, when those combinations are feasible.
- **Boundary probe**: an additional representative at an edge; it is not automatically a new block.
- **Fixture**: code that prepares each case's own data and removes it afterward. API inputs include existing resource state, not just strings in the request.

This is a deliberately limited input-domain model, not all possible inputs/filters or all combinations. We do not claim Pair-Wise or All Combinations Coverage. The Phase 2 brief requires ISP-derived inputs, not every ISP coverage criterion from Phase 1.

### S01 — list/search products

Scope: `page=1` by default, an explicitly supplied integer `per_page`, and either an omitted search parameter or a nonempty, plain ASCII product-name query. Other filters, malformed/non-integer query values and empty/whitespace-only searches are outside this first model. A run-unique name determines whether a query matches; we do not classify a query using the server's actual answer afterward.

| Characteristic | Type | Blocks | Base |
| --- | --- | --- | --- |
| C1: `per_page` range | Interface-based | B1: integer ≤0; B2: 1–100; B3: integer ≥101 | B2, value `10` |
| C2: query's relationship to prepared data | Functionality-based | B1: search omitted; B2: a query matching our published fixture; B3: a run-unique query matching no product | B2, fixture's exact unique name |

The deployed route's read-only OPTIONS schema was checked before implementation: integer/default 10/minimum 1/maximum 100. BCC gives `1+(3-1)+(3-1)=5` cases; valid boundaries 1 and 100 add 2 probes, total 7. Each case creates its own published simple product at 100.00 THB, even when testing an invalid `per_page`, so C2's matching precondition remains true.

| ID / pytest parameter ID | Blocks | Test values | Goal and expected result |
| --- | --- | --- | --- |
| S01-01 `base-valid-and-match` | C1-B2, C2-B2 | `per_page=10`, exact unique name | HTTP 200; JSON list contains exactly our matching product, correct ID/name/100.00 THB price; size ≤10. |
| S01-02 `below-minimum` | C1-B1, C2-B2 | `per_page=0`, same kind of matching query | HTTP 400; `rest_invalid_param`, meaningful message, error identifies `per_page`. |
| S01-03 `above-maximum` | C1-B3, C2-B2 | `per_page=101`, matching query | HTTP 400; `rest_invalid_param`, message and `per_page` error. |
| S01-04 `search-omitted` | C1-B2, C2-B1 | `per_page=10`, no `search` | HTTP 200; nonempty JSON product list, typed ID/name fields, size ≤10; no fixed catalog count. |
| S01-05 `search-no-match` | C1-B2, C2-B3 | `per_page=10`, fresh unmatched marker | HTTP 200 and an empty JSON list `[]`, not a 404. |
| S01-06 `lower-valid-boundary` | C1-B2, C2-B2 | `per_page=1`, matching query | HTTP 200; correct matching product, size ≤1. |
| S01-07 `upper-valid-boundary` | C1-B2, C2-B2 | `per_page=100`, matching query | HTTP 200; correct matching product, size ≤100, NOT exactly 100 products. |

`per_page` is the requested maximum, not the catalog's size. No 100-product fixture is needed. Store API price strings use minor units: `"10000"` with `currency_minor_unit=2` is 100.00 THB.

### S02 — read one product

Scope: positive integer product IDs of simple products, and the route's documented optional `context` query parameter. Slug routing, malformed/zero/negative IDs and password-protected products are excluded. The deployed route's read-only schema (`/wp-json/wc/store/v1` route index) declares `context` as a string enum `view`/`embed`/`edit` with default `view`.

| Characteristic | Type | Blocks | Base |
| --- | --- | --- | --- |
| C1: state of the product the ID refers to | Functionality-based | B1: exists and published; B2: exists but unpublished (draft); B3: absent | B1 |
| C2: `context` query parameter | Interface-based | B1: omitted (server default `view`); B2: supplied with a documented enum value; B3: supplied with a value outside the enum | B1 |

C2 is classified from the request parameter alone, so it is interface-based; C1 depends on what the product means to a shopper, so it is functionality-based. For B2 we choose `view` as the representative, not claim that `embed`/`edit` were tested. BCC gives `1+(3-1)+(3-1)=5` cases.

| ID / pytest parameter ID | Blocks and prepared precondition | Goal and expected result |
| --- | --- | --- |
| S02-01 `existing-published` | C1-B1, C2-B1: existing published product; Admin GET confirms existence/status; no `context` | Store GET returns HTTP 200 and the exact fixture ID/name/100.00 THB price. |
| S02-02 `existing-draft` | C1-B2, C2-B1: existing draft; Admin GET confirms it still exists as draft | Store GET returns HTTP 404 with JSON error code/message/status; draft data must not be publicly exposed. |
| S02-03 `verified-absent` | C1-B3, C2-B1: create our own draft, delete that exact ID, then verify Admin GET returns 404 | Store GET returns HTTP 404 with meaningful JSON error fields. No guessed unused ID. |
| S02-04 `context-explicit-valid` | C1-B1, C2-B2: existing published product; `context=view` | Store GET returns HTTP 200 and the same exact fixture ID/name/100.00 THB price. |
| S02-05 `context-invalid-value` | C1-B1, C2-B3: existing published product; `context=not-a-context` | HTTP 400; `rest_invalid_param` identifies `context`, with message and status fields. |

S02-02 and S02-03 both expect 404 for different reasons. The known setup differentiates them: a missing-ID test alone would not detect accidental public exposure of a real draft. The invalid-`context` oracle follows the documented enum and WordPress schema validation, not a result copied from a run.

### S03 — create a product

Scope: a syntactically valid JSON object with a unique `G05-…` name/SKU, `type="simple"`, fixed `regular_price="100.00"`, visible catalog setting and a run metadata marker. `status` is a string or omitted; authentication is valid Basic-auth credentials for our assigned Shop manager, absent, or the same username with a deliberately wrong password. Malformed JSON, other product types, price validation and other users/roles are outside this model.

| Characteristic | Type | Blocks | Base |
| --- | --- | --- | --- |
| C1: credentials supplied | Interface-based | B1: correct Group 05; B2: no credentials; B3: incorrect password | B1 |
| C2: intended publication | Functionality-based | B1: `publish` or its documented default; B2: valid but unpublished (`draft`, `pending`, `private`); B3: unrecognised status string | B1, explicit `publish` |

For this publication-focused model, omitted status and explicit `publish` share a block; draft/pending/private share the unpublished block. We choose `draft` as its representative, not claim all those values were tested. BCC gives `1+(3-1)+(3-1)=5` cases; interactions such as wrong credentials + invalid status are not claimed as covered.

| ID / pytest parameter ID | Blocks and input | Goal and expected result |
| --- | --- | --- |
| S03-01 `base-valid-published` | C1-B1, C2-B1: valid auth + publish | HTTP 201; positive ID, exact name/SKU/type/status/price; Admin read-back confirms saved data and Store GET exposes the product. |
| S03-02 `credentials-absent` | C1-B2, C2-B1: no auth + publish | HTTP 401 and meaningful JSON error fields; exact unique SKU lookup confirms no product was created. |
| S03-03 `credentials-wrong` | C1-B3, C2-B1: wrong password + publish | HTTP 401, JSON error fields and no product created; no assumption of one fixed auth error-code string. |
| S03-04 `valid-unpublished` | C1-B1, C2-B2: valid auth + draft | HTTP 201; correct stored fields/status, Admin read-back succeeds, public Store GET returns 404. |
| S03-05 `invalid-publication-status` | C1-B1, C2-B3: valid auth + `not-a-status` | HTTP 400; `rest_invalid_param` identifies `status`, and no product is created. |

The invalid-status oracle follows the documented enum and WordPress schema validation, not a result copied from a run. If the deployed server differs, the failure must be investigated, not changed to “any 4xx” or silently skipped.

### Data isolation and safe cleanup

Each case has a fresh public/admin session and its own product factory. No case depends on an earlier suite. Public Store calls receive no group credentials. Admin calls use the supplied API password; redirects and automatic POST retries are disabled. The instructor's classroom server uses HTTP, so this is a controlled course environment, not a production security recommendation.

Products use exact unique names `G05-<run>-<random>` and `itcs386_test_run` metadata. Teardown verifies the exact returned ID, exact name and matching run marker before deleting, then confirms Admin 404. Only records created by the current test are eligible; demo and other groups' data are never cleanup targets. An ambiguous POST is reconciled by its exact unique SKU, never by a broad G05 search, and is not blindly retried. An empty lookup after an interrupted/unknown POST remains an explicit cleanup error, not proof that nothing was created. Cleanup failure is reported as an error, not hidden. This cleanup is permanent only for our disposable test records.

Offline harness check:

```bash
python -m unittest discover -s verification -v
```

The ownership guard was test-driven: first observed 1 failing/5 passing checks with the guard unimplemented, then all 6 passing after implementation. A seventh regression first reproduced a false cleanup claim after an interrupted POST and empty lookup, then passed after the guard was hardened. This is test-harness validation, not a claim that WooCommerce was developed using TDD.

### Execution results and limitations

Latest full run: **11 November 2026, 23:10 Asia/Bangkok**, all 17 cases. Earlier runs on **9 November 2026** cover the 15 cases that existed then. Directory timestamps use UTC, while `run.json` also records the corresponding Bangkok time. These are real pytest runs, not example output or screenshots of simulated results.

| Bangkok start | Execution | Actual result | Full output / structured evidence |
| --- | --- | --- | --- |
| 11 Nov 23:10:42 | S01 → S02 → S03, all 17 cases | 17 passed, 0 failures/errors/skips; 10.13s | [console](API%20testing/results/20261111T161042Z-a85697bb/console.txt), [JUnit XML](API%20testing/results/20261111T161042Z-a85697bb/junit.xml), [run/source hashes](API%20testing/results/20261111T161042Z-a85697bb/run.json) |
| 9 Nov 00:35:22 | S01 → S02 → S03 | 15 passed, 0 failures/errors/skips; 8.96s | [console](API%20testing/results/20261108T173522Z-fbc1f0d3/console.txt), [JUnit XML](API%20testing/results/20261108T173522Z-fbc1f0d3/junit.xml), [run/source hashes](API%20testing/results/20261108T173522Z-fbc1f0d3/run.json) |
| 9 Nov 00:36:05 | S02-02 existing-draft alone | 1 passed; 1.16s | [console](API%20testing/results/20261108T173605Z-0a164b81/console.txt), [JUnit XML](API%20testing/results/20261108T173605Z-0a164b81/junit.xml), [run metadata](API%20testing/results/20261108T173605Z-0a164b81/run.json) |
| 9 Nov 00:36:06 | S03 → S02 → S01 (reverse suite order) | 15 passed, 0 failures/errors/skips; 8.80s | [console](API%20testing/results/20261108T173606Z-0e33c528/console.txt), [JUnit XML](API%20testing/results/20261108T173606Z-0e33c528/junit.xml), [run/source hashes](API%20testing/results/20261108T173606Z-0e33c528/run.json) |

Those 9 November runs had **15 distinct cases**, not 31: the extra executions check repeatability and suite-order independence. In each of those full runs, S01 passed 7/7, S02 3/3 and S03 5/5. S02-04 and S02-05 were added on 11 November; the 11 November run covers all 17 cases with S01 7/7, S02 5/5 and S03 5/5. In that run 14 disposable products were created and the same 14 were deleted, each confirmed by an Admin 404. No failures were suppressed, skipped or marked xfail; no failing SUT behavior was observed within this limited model.

[Verification audit](API%20testing/results/20261108T173606Z-0e33c528/verification-audit.json): all recorded Python source hashes match the tested files; 25 disposable products created across the three runs were deleted (12 + 1 + 12). A separate read-only Admin query for each exact run marker found zero remaining products. Credential scan found zero matches in project files; all 6 original source/reference files still match their download hashes. The source hashes identify the tested scripts; this README can be updated separately without changing their execution.

Offline harness verification also passes 7/7. Those checks and the three live runs do not prove every possible order, every input or every WooCommerce feature; they support the stated small scope.

For any failure, preserve the dated output and distinguish a system defect from a test/configuration mistake. A defect report must record request, expected result and actual result. Successful API cases do not establish UI correctness, complete system scenarios, performance or absence of all bugs.

### Sources for the design and expected results

- Instructor's Phase 2 description, API Testing items 1–6 (MyCourses Phase 2 section linked below).
- Instructor's `WooCommerce_API_Guide.md`, sections 1–5: assigned Shop manager, separate Store/Admin authentication, product operations, ownership rule and price formats. Original reference/account files stay outside Git.
- Midterm Module 5 ISP, slides 8–14: disjoint/complete blocks, interface- and functionality-based characteristics; Module 6 ISP, slides 24–27: feasible base choices and BCC.
- Week 11 lecture, slides 23–29, and API lab pages 13–17: status + field assertions, ISP, independent fixtures and complete execution evidence.
- [Store Products API and visibility](https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/products/), [Store pagination](https://developer.woocommerce.com/docs/apis/store-api/#pagination), [Admin product properties](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/#product-properties), [WordPress request validation](https://developer.wordpress.org/reference/classes/wp_rest_request/has_valid_params/).

## Python setup

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Python dependencies are local to this project (`.venv/` is gitignored).

Historical tooling setup, 8 November 2026: Python 3.14.6, pytest 9.2.0, requests 2.34.2, Selenium 4.52.0 and k6 2.3.0. That setup did not test the classroom APIs; the real API executions on 9 and 11 November are recorded above. No UI/system/performance result is inferred from tooling readiness.

## Repository layout

| Folder / file | Contents |
| --- | --- |
| `API testing/` | Three operation suites (pytest), fixtures/helpers and dated full-run results |
| `run_api_tests.py` | One-command runner that saves console output, JUnit XML and run metadata |
| `verification/` | Offline checks of the test harness (not assignment cases) |
| `docs/` | Nested review map of the API tests (`docs/api-testing-map.html`) and its build scripts |
| `graphify-out/` | Generated code/document graph used by the review map |
| `system test/` | Manual system test cases and traceability matrices |

The Phase 2 description names the submission folders "API testing", "System testing", "UI testing" and "Performance testing" inside a folder named "project phase 2" in the group's course repository. The final location and folder names still need team agreement before the 25 November 2026 17:00 deadline.

## Credentials

The downloaded account workbook stays outside this repository. Supply credentials through environment variables only; never put them in code, screenshots or commits.

Source requirements: [MyCourses Phase 2 section](https://mycourses.ict.mahidol.ac.th/course/section.php?id=8448).
