# API testing

Automated tests for three WooCommerce product API operations. Owner: Rattee Watperatam.

## Overview

Paths are relative to `http://157.85.102.236/shop/wp-json`.

| Suite | Operation | Cases | Test file |
| --- | --- | ---: | --- |
| S01 | `GET /wc/store/v1/products` — list/search products | 7 | [test_product_list.py](test_product_list.py) |
| S02 | `GET /wc/store/v1/products/{id}` — read one product | 5 | [test_product_detail.py](test_product_detail.py) |
| S03 | `POST /wc/v3/products` — create a product | 5 | [test_product_create.py](test_product_create.py) |

Each `pytest.param` row is one test case and has a `# Goal:` comment above it. Every test checks the HTTP status and the important response fields.

## How to run

From the repository root, with the Group 05 username and its **Shop API password** (not the browser login password):

```zsh
python3 -m venv .venv && source .venv/bin/activate && python -m pip install -r requirements.txt
export SHOP_USER="itcs386-g05"
read -s "SHOP_API_PASSWORD?Shop API password: "; export SHOP_API_PASSWORD
python run_api_tests.py
```

The runner runs all 17 cases with pytest and saves `console.txt`, `junit.xml` and `run.json` in `results/<UTC time>-<run>/`. Credentials stay in environment variables and are redacted from saved output.

## ISP design

- **Characteristic**: a property used to split the inputs (interface-based = one parameter on its own; functionality-based = what the input means for the operation).
- **Block**: one group of a characteristic. Blocks do not overlap and cover the stated scope.
- **Base Choice Coverage (BCC)**: start from one normal base case, then change one characteristic at a time to each other block. Cases = `1 + Σ(blocks − 1)`.

### S01 — list/search products

| Characteristic | Type | Blocks | Base |
| --- | --- | --- | --- |
| C1: `per_page` | Interface-based | B1: ≤0; B2: 1–100; B3: ≥101 | B2 (`10`) |
| C2: search vs. prepared data | Functionality-based | B1: no search; B2: matches our product; B3: matches nothing | B2 |

BCC = 1 + 2 + 2 = 5 cases, plus boundary values 1 and 100 = 7. The range 1–100 comes from the server's route schema. `per_page` is the maximum number of products returned, not the shop's size.

| Case | Blocks | Input | Expected |
| --- | --- | --- | --- |
| S01-01 | C1-B2, C2-B2 | `per_page=10`, our product's name | 200; exactly our product (ID, name, 100.00 THB) |
| S01-02 | C1-B1, C2-B2 | `per_page=0` | 400 `rest_invalid_param` for `per_page` |
| S01-03 | C1-B3, C2-B2 | `per_page=101` | 400 `rest_invalid_param` for `per_page` |
| S01-04 | C1-B2, C2-B1 | `per_page=10`, no search | 200; non-empty list, at most 10 |
| S01-05 | C1-B2, C2-B3 | `per_page=10`, unmatched term | 200; empty list `[]` |
| S01-06 | C1-B2, C2-B2 | `per_page=1` | 200; our product, at most 1 |
| S01-07 | C1-B2, C2-B2 | `per_page=100` | 200; our product, at most 100 |

### S02 — read one product

| Characteristic | Type | Blocks | Base |
| --- | --- | --- | --- |
| C1: state of the product the ID points to | Functionality-based | B1: published; B2: draft; B3: deleted (absent) | B1 |
| C2: `context` query parameter | Interface-based | B1: omitted; B2: allowed value (`view`); B3: not allowed | B1 |

BCC = 1 + 2 + 2 = 5 cases. `context` allows `view`/`embed`/`edit` according to the route schema.

| Case | Blocks | Setup / input | Expected |
| --- | --- | --- | --- |
| S02-01 | C1-B1, C2-B1 | published product | 200; same ID, name, price |
| S02-02 | C1-B2, C2-B1 | draft product | 404; draft is not shown to shoppers |
| S02-03 | C1-B3, C2-B1 | our product, deleted and confirmed gone | 404 |
| S02-04 | C1-B1, C2-B2 | published, `context=view` | 200; same product |
| S02-05 | C1-B1, C2-B3 | published, `context=not-a-context` | 400 `rest_invalid_param` for `context` |

S02-02 and S02-03 both expect 404 for different reasons: a draft that exists must stay hidden, and an absent product cannot be returned.

### S03 — create a product

| Characteristic | Type | Blocks | Base |
| --- | --- | --- | --- |
| C1: credentials | Interface-based | B1: correct; B2: none; B3: wrong password | B1 |
| C2: requested `status` | Functionality-based | B1: `publish`; B2: valid but unpublished (`draft`); B3: unknown value | B1 |

BCC = 1 + 2 + 2 = 5 cases. Every request uses a unique `G05-…` name and SKU, type `simple` and price `100.00`.

| Case | Blocks | Input | Expected |
| --- | --- | --- | --- |
| S03-01 | C1-B1, C2-B1 | valid auth, `publish` | 201; saved data correct; visible in the Store API |
| S03-02 | C1-B2, C2-B1 | no auth | 401; no product created |
| S03-03 | C1-B3, C2-B1 | wrong password | 401; no product created |
| S03-04 | C1-B1, C2-B2 | valid auth, `draft` | 201; hidden from the Store API (404) |
| S03-05 | C1-B1, C2-B3 | valid auth, `not-a-status` | 400 `rest_invalid_param` for `status`; no product created |

## Test independence and cleanup

Each case creates the products it needs, with a unique `G05-<run>-<random>` name, and deletes only those products afterwards (checked by ID, name and run marker). No case depends on another case, suite order, or data owned by other groups. Offline checks of this cleanup code: `python -m unittest discover -s verification`.

## Results

| Run (Bangkok) | Cases | Result | Evidence |
| --- | --- | --- | --- |
| 11 Nov 2026 23:10 | all 17 | 17 passed | [console](results/20261111T161042Z-a85697bb/console.txt), [JUnit](results/20261111T161042Z-a85697bb/junit.xml), [run.json](results/20261111T161042Z-a85697bb/run.json) |
| 9 Nov 2026 00:35 | 15 (before S02-04/05 were added) | 15 passed | [console](results/20261108T173522Z-fbc1f0d3/console.txt) |
| 9 Nov 2026 00:36 | 15, reverse suite order | 15 passed | [console](results/20261108T173606Z-0e33c528/console.txt) |

No test failed, so there are no defects to report yet. If a test fails, record whether it is a system defect or a test mistake; for a defect, give the request, expected result and actual result.

The review map [`docs/api-testing-map.html`](../docs/api-testing-map.html) shows how the suites, fixtures and requests connect.
