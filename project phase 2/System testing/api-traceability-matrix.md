# System Test Traceability Matrix — ITCS386 Group 5

## Requirement-to-test-case matrix

Revision 2 follows slide 40 of `W11-Integration, System and UI Testing_v3.pdf`: two columns, **Requirement** and **Test cases**. R1–R22 are group-defined behaviors derived from the WooCommerce guide, not instructor-assigned IDs.

**Status: Designed / Not Run.** All 22 requirements now have explicit planned steps in the [three system test cases](system-test-cases.md). This closes the five previous **design gaps**, not execution gaps. No test results or successful endpoint calls are claimed.

Original numeric steps are retained; lettered additions are executed in the order displayed in the test document, including ST-G05-03 step 0a before step 1.

| Requirement | Test cases |
|---|---|
| **R1 Search for products by name** | ST-G05-01 (steps 3); ST-G05-02 (steps 2); ST-G05-03 (steps 3) |
| **R2 Browse products in a selected category** | ST-G05-03 (steps 3) |
| **R3 View product details, current price and availability** | ST-G05-01 (steps 3); ST-G05-02 (steps 2, 12); ST-G05-03 (steps 3) |
| **R4 Add products to the cart and display correct quantities and totals** | ST-G05-01 (steps 4); ST-G05-02 (steps 4, 9); ST-G05-03 (steps 6) |
| **R5 Change cart quantities and enforce stock limits** | ST-G05-02 (steps 3, 5, 6, 7, 12) |
| **R6 Remove an item and recalculate the cart** | ST-G05-02 (steps 8) |
| **R7 Apply a valid coupon and reject a nonexistent coupon** | ST-G05-01 (steps 5, 6, 6b) |
| **R8 Remove a coupon and restore the undiscounted total** | ST-G05-01 (steps 6a) |
| **R9 Preserve cart contents when returning from checkout** | ST-G05-01 (steps 7); ST-G05-03 (steps 8) |
| **R10 Reject checkout when required address data is missing** | ST-G05-03 (steps 7) |
| **R11 Place a COD order and display the correct confirmation** | ST-G05-01 (steps 9); ST-G05-02 (steps 10); ST-G05-03 (steps 9) |
| **R12 Register a customer account and log out/log in** | ST-G05-03 (steps 4, 5, 14) |
| **R13 View the customer's own order history and updated status** | ST-G05-03 (steps 10, 13, 14) |
| **R14 Create and publish a product with price, category and stock settings** | ST-G05-01 (steps 1); ST-G05-02 (steps 1, 1a); ST-G05-03 (steps 1) |
| **R15 Update a product price and show the new price to customers** | ST-G05-03 (steps 2, 3, 6, 9) |
| **R16 Reduce stock correctly after a successful purchase** | ST-G05-01 (steps 11); ST-G05-02 (steps 11) |
| **R17 Permanently delete a group-owned product** | ST-G05-03 (steps 15, 16, 17) |
| **R18 Create a product category** | ST-G05-03 (steps 0a, 1, 3) |
| **R19 Inspect order details and change the status to Completed** | ST-G05-01 (steps 10, 12); ST-G05-03 (steps 11, 12, 13) |
| **R20 Create a product-restricted percentage coupon** | ST-G05-01 (steps 2, 2a) |
| **R21 List registered customers and locate a specific customer** | ST-G05-03 (steps 11a) |
| **R22 Browse catalog pages using sorting and price filters** | ST-G05-02 (steps 1a, 1b, 1c, 1d, 1e) |

## Changes that close the previous gaps

| Requirement | Added steps | Expected evidence after execution |
|---|---|---|
| R8 Remove coupon | ST-G05-01: 6a–6b | Coupon removed, merchandise total restored to 400 THB, then one 40 THB discount after reapplication |
| R17 Permanently delete product | ST-G05-03: 15–17 | Disposable product exists before deletion, is absent from staff lists/Trash/search afterwards, and cannot be purchased at its old URL; purchased product/order remain intact |
| R18 Create category | ST-G05-03: 0a, 1, 3 | Category appears in staff list, is assigned to the product, and supports customer browsing |
| R21 List registered customers | ST-G05-03: 11a | New account found in the customer list by exact email and matched to the order |
| R22 Paging, sorting and price filtering | ST-G05-02: 1a–1e | Known-price fixtures; page navigation, ascending/descending order, inclusive 150–250 THB filtering and reset checks |

ST-G05-02 step 8 now always exercises Remove, even if the zero-quantity attempt already emptied the cart. ST-G05-01 step 2a also explicitly checks the coupon list; ST-G05-03 step 1 explicitly checks the staff product list.

## Execution dependencies and remaining scope

- **R22 is planned, not verified:** storefront pagination, price sorting and price-filter controls have not been inspected. Missing controls make the affected steps Blocked and must be reported; direct API calls must not be substituted to claim UI coverage. Do not change site settings/themes/plugins to make the test pass.
- Create only the minimum additional group-owned fixtures needed for two pages. Shared catalog changes can invalidate ordering comparisons; record interference and repeat affected checks.
- Agree the quantity-zero expectation before the formal run. Customer registration depends on an approved test-email setup if verification is required.
- Record screenshots, actual results and Pass/Fail only after execution. A blocked prerequisite does not make its requirement covered in execution.
- The 22 mapped requirements are this document's selected behavioral breakdown, not every variation in the complete specification. Product variations, other coupon types, authorization failures and additional input partitions remain outside this baseline.
- No live requests, purchases, deletions or other server mutations were performed when revising these documents.

## Test case key

| ID | Title |
|---|---|
| ST-G05-01 | Purchase with a coupon and complete the order |
| ST-G05-02 | Validate quantity limits, cart changes and remaining stock |
| ST-G05-03 | Verify updated pricing, customer account and order history |

## Appendix — API behavioral mapping

See [API inventory](api-inventory.md) for authentication, base URLs and operation details. This appendix maps related observable behavior, not verified API calls. WordPress Admin may use mechanisms other than these REST endpoints.

**P:** An explicit related behavior is planned. **I:** The UI behavior relates indirectly to the operation. Neither means Pass. Direct API tests or captured requests with response assertions are needed to verify endpoint coverage.

### Store API

Base URL: `http://157.85.102.236/shop/wp-json/wc/store/v1`

| API ID | Method / Endpoint | System test steps | Mapping | Scope / limitation |
|---|---|---|---|---|
| S01 | `GET /products` | ST-G05-01 (steps 3); ST-G05-02 (steps 1b, 1c, 1d, 1e, 2); ST-G05-03 (steps 3, 17) | P | Search, pagination, sorting and price filtering are explicitly planned; arbitrary query combinations are not covered. |
| S02 | `GET /products/{id}` | ST-G05-01 (steps 3); ST-G05-02 (steps 2, 12); ST-G05-03 (steps 3, 15, 17) | P | Product details, price and availability; no direct response-field checks. |
| S03 | `GET /products/categories` | ST-G05-03 (steps 3) | I | Customer category browsing does not directly inspect the category-list API response. |
| S04 | `GET /cart` | ST-G05-01 (steps 4, 6a, 7); ST-G05-02 (steps 4, 5, 6, 7, 8, 9); ST-G05-03 (steps 6, 8) | P | Cart contents and totals; token lifecycle remains outside the UI assertions. |
| S05 | `POST /cart/add-item` | ST-G05-01 (steps 4); ST-G05-02 (steps 3, 4, 8, 9, 12); ST-G05-03 (steps 6) | P | Valid and excessive quantities; UI may prevent invalid requests. |
| S06 | `POST /cart/update-item` | ST-G05-02 (steps 5, 6, 7) | P | Quantity changes; zero-quantity expectation must be agreed before execution. |
| S07 | `POST /cart/remove-item` | ST-G05-02 (steps 8) | P | Remove control is exercised every run, re-adding an item first if needed. |
| S08 | `POST /cart/apply-coupon` | ST-G05-01 (steps 5, 6, 6b) | P | Invalid coupon, valid coupon and reapplication. |
| S09 | `POST /cart/remove-coupon` | ST-G05-01 (steps 6a) | P | Remove coupon, refresh and verify the restored merchandise total. |
| S10 | `GET /checkout` | ST-G05-01 (steps 7, 8); ST-G05-02 (steps 10); ST-G05-03 (steps 6, 8) | I | Opening checkout does not directly inspect the draft-order response. |
| S11 | `POST /checkout` | ST-G05-01 (steps 9); ST-G05-02 (steps 10); ST-G05-03 (steps 7, 9) | P | COD purchase and required-field validation; validation may happen before a request. |

### Admin REST API

Base URL: `http://157.85.102.236/shop/wp-json/wc/v3`

| API ID | Method / Endpoint | System test steps | Mapping | Scope / limitation |
|---|---|---|---|---|
| A01 | `GET /products` | ST-G05-02 (steps 1a); ST-G05-03 (steps 1, 15, 17) | P | Staff product-list search and deletion verification. |
| A02 | `POST /products` | ST-G05-01 (steps 1); ST-G05-02 (steps 1, 1a); ST-G05-03 (steps 1, 15) | P | Create group-owned simple products and catalog fixtures. |
| A03 | `GET /products/{id}` | ST-G05-01 (steps 1, 11); ST-G05-02 (steps 1, 11); ST-G05-03 (steps 1, 2, 15) | P | Inspect saved product details. |
| A04 | `PUT /products/{id}` | ST-G05-03 (steps 2) | P | Explicit price update; automatic stock reduction is not counted as this operation. |
| A05 | `DELETE /products/{id}?force=true` | ST-G05-03 (steps 16, 17) | P | Permanent deletion of a separate disposable product; Trash alone is insufficient. |
| A06 | `GET /products/categories` | ST-G05-03 (steps 0a) | P | Explicit staff category-list search; REST request/response remains unverified. |
| A07 | `POST /products/categories` | ST-G05-03 (steps 0a) | P | Create the group-owned category and verify it in the list. |
| A08 | `GET /orders` | ST-G05-01 (steps 10) | P | Staff searches the order list; status/date filters remain outside scope. |
| A09 | `GET /orders/{id}` | ST-G05-01 (steps 10); ST-G05-02 (steps 11); ST-G05-03 (steps 11, 17) | P | Inspect order details and confirm the existing order survives disposable-product deletion. |
| A10 | `PUT /orders/{id}` | ST-G05-01 (steps 12); ST-G05-03 (steps 12) | P | Set Completed; other status transitions remain outside scope. |
| A11 | `GET /coupons` | ST-G05-01 (steps 2a) | P | Explicit staff coupon-list search. |
| A12 | `POST /coupons` | ST-G05-01 (steps 2) | P | Create a percentage coupon restricted to the test product. |
| A13 | `GET /customers` | ST-G05-03 (steps 11a) | P | Explicit registered-customer list lookup and comparison with the order account. |

### API mapping summary

| Mapping | Store | Admin | Total |
|---|---|---|---|
| P — Explicit related behavior planned | 9 | 13 | 22 |
| I — Indirect UI relationship | 2 | 0 | 2 |
| No related planned step | 0 | 0 | 0 |
| **Total operations** | **11** | **13** | **24** |

All 24 operations have a planned behavioral relationship; two remain indirect. **No verified API execution coverage is available.** Registration/login and customer order history remain Web UI features without invented endpoints.

Keep credentials and cart tokens out of screenshots/repository evidence. Only group-owned records may be changed or deleted. These functional checkout steps must not be used in performance/load tests, where orders/bookings are prohibited.

The Project 2 API Testing requirement remains at least three operations, including one that creates or changes data; this appendix does not impose a requirement to directly test all 24.

## Sources

- `W11-Integration, System and UI Testing_v3.pdf`, slides 33 and 40.
- WooCommerce API Guide, sections 3–5; [documented inventory](api-inventory.md).
- [System test cases — Revision 2](system-test-cases.md), the authoritative step definitions. Duplicate baseline step lists have been removed to prevent drift.
