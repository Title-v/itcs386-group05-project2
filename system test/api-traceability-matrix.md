# Requirement Traceability Matrix — ITCS386 Group 5

This matrix includes **only the requirements actually checked** in the current system-test runs on **19 November 2026**. The two-column format follows the lecture's Requirement / Test cases example. Existing requirement IDs are retained to avoid breaking references; skipped numbers do not indicate additional rows.

The wording of R14 is limited to the product, price and stock checks actually performed. The matrix contains no untested or partially covered feature rows.

| Requirement | Test cases |
|---|---|
| **R23 Locate a product in the Shop list and open its details** | ST-G05-01 (step 3); ST-G05-02 (step 2); ST-G05-03 (step 2) |
| **R3 View the correct product, price and availability** | ST-G05-01 (step 3); ST-G05-02 (steps 2, 9); ST-G05-03 (step 2) |
| **R4 Add items and display correct cart quantities and totals** | ST-G05-01 (step 4); ST-G05-02 (steps 2, 6); ST-G05-03 (step 3) |
| **R5 Change cart quantities and enforce available-stock limits** | ST-G05-02 (steps 3, 4, 9) |
| **R6 Remove a cart item and recalculate the cart** | ST-G05-02 (step 5) |
| **R7 Reject a nonexistent coupon and apply the valid discount** | ST-G05-01 (step 5) |
| **R9 Preserve cart contents and coupon when returning from checkout** | ST-G05-01 (step 6) |
| **R10 Prevent checkout with an empty required Street address** | ST-G05-03 (step 4) |
| **R11 Place a COD order and show the correct confirmation** | ST-G05-01 (step 7); ST-G05-02 (step 7); ST-G05-03 (step 5) |
| **R14 Create and publish a new product with the specified price and stock settings** | ST-G05-01 (step 1); ST-G05-02 (step 1); ST-G05-03 (step 1) |
| **R15 Persist a regular-price update and use it on the storefront and checkout** | ST-G05-03 (steps 1, 2, 3, 5) |
| **R16 Reduce stock by the purchased quantity** | ST-G05-02 (step 8) |
| **R19 Inspect order details and persist a Completed status** | ST-G05-01 (steps 8, 9); ST-G05-03 (steps 6, 7) |
| **R20 Create a percentage coupon restricted to the test product** | ST-G05-01 (step 2) |

## Execution evidence

| Case | Current run | Result | Recorded order | Report |
|---|---|---|---|---|
| ST-G05-01 | R04 | 9/9 Pass | 1252, Completed, 360 THB | [Results and images](ST-G05-01-R04-results.md) |
| ST-G05-02 | R02 | 9/9 Pass | 1260, Processing, 300 THB | [Results and images](ST-G05-02-R02-results.md) |
| ST-G05-03 | R02 | 7/7 Pass | 1274, Completed, 225 THB | [Results and images](ST-G05-03-R02-results.md) |

All 14 rows are supported by the executed steps above. This is coverage of the selected behaviors, not a claim of exhaustive WooCommerce specification or REST API coverage. Direct API testing is documented separately in [API testing](../API%20testing/README.md); the [API inventory](api-inventory.md) is a reference list.

See [system-test-cases.md](system-test-cases.md) for the exact UI inputs, expected/actual results and page-only evidence.
