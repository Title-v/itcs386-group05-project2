# System Test Traceability Matrix — ITCS386 Group 5

**Revision 3 — focused scope. Status: Designed / Not Run.**

This matrix follows slide 40 of `W11-Integration, System and UI Testing_v3.pdf`: **Requirement | Test cases**. It maps observable behavior to the [three revised system scenarios](system-test-cases.md), each with nine steps.

The group-defined R1–R22 identifiers are retained for continuity. Features deliberately removed from this revision remain visible as **No test case — outside selected scope**. Partial mappings are stated explicitly. A mapped requirement is planned, not passed; there is no claim of complete guide or API coverage.

## Requirement-to-test-case matrix

| Requirement | Test cases |
|---|---|
| **R1 Search for products by name** | ST-G05-01 (steps 3); ST-G05-02 (steps 2); ST-G05-03 (steps 2) |
| **R2 Browse products in a selected category** | No test case — outside selected scope |
| **R3 View product details, current price and availability** | ST-G05-01 (steps 3); ST-G05-02 (steps 2, 9); ST-G05-03 (steps 2) |
| **R4 Add products to the cart and display correct quantities and totals** | ST-G05-01 (steps 4); ST-G05-02 (steps 2, 6); ST-G05-03 (steps 3) |
| **R5 Change cart quantities and enforce stock limits** | ST-G05-02 (steps 3, 4, 9) |
| **R6 Remove an item and recalculate the cart** | ST-G05-02 (steps 5) |
| **R7 Apply a valid coupon and reject a nonexistent coupon** | ST-G05-01 (steps 5) |
| **R8 Remove a coupon and restore the undiscounted total** | No test case — outside selected scope |
| **R9 Preserve cart contents when returning from checkout** | ST-G05-01 (steps 6) |
| **R10 Reject checkout when required address data is missing** | ST-G05-03 (steps 4) |
| **R11 Place a COD order and display the correct confirmation** | ST-G05-01 (steps 7); ST-G05-02 (steps 7); ST-G05-03 (steps 5) |
| **R12 Register a customer account and log out/log in** | Partial: ST-G05-03 (step 2) checks login using an existing account. Registration and logout are outside selected scope. |
| **R13 View the customer's own order history and updated status** | ST-G05-03 (steps 6, 9) |
| **R14 Create and publish a product with price, category and stock settings** | Partial: ST-G05-01 (step 1), ST-G05-02 (step 1), ST-G05-03 (step 1) check product creation, price and stock settings. Category assignment is outside selected scope. |
| **R15 Update a product price and show the new price to customers** | ST-G05-03 (steps 1, 2, 3, 5) |
| **R16 Reduce stock correctly after a successful purchase** | ST-G05-02 (steps 8) |
| **R17 Permanently delete a group-owned product** | No test case — outside selected scope |
| **R18 Create a product category** | No test case — outside selected scope |
| **R19 Inspect order details and change the status to Completed** | ST-G05-01 (steps 8, 9); ST-G05-03 (steps 7, 8, 9) |
| **R20 Create a product-restricted percentage coupon** | ST-G05-01 (steps 2) |
| **R21 List registered customers and locate a specific customer** | No test case — outside selected scope |
| **R22 Browse catalog pages using sorting and price filters** | No test case — outside selected scope |

## Scenario summary

| Test case | End-to-end scenario | Unusual input/action |
|---|---|---|
| ST-G05-01 | Staff creates product/coupon → customer purchases with discount → staff verifies and completes order | Invalid coupon; return from checkout before ordering |
| ST-G05-02 | Staff sets stock → customer changes/removes/re-adds cart items and purchases → staff checks remaining stock → customer checks availability | Quantity above stock; removal and re-addition |
| ST-G05-03 | Staff updates price → existing customer logs in and purchases → staff completes order → customer checks history/status | Missing required address field, then correction |

## Scope summary

- **14 requirements have full planned mappings within their stated behavior; 2 have partial mappings; 6 have no test case in the selected scope.**
- Outside scope: R2, R8, R17, R18, R21 and R22, plus registration/logout under R12 and category assignment under R14.
- All execution results remain **Not Run**. Record actual results, screenshots and defects after manual execution.
- This is the group's reduced scope; it is not a claim that every guide feature or grading expectation is satisfied. The assignment asks for coverage of the main staff/customer features and a matrix that exposes omissions.
- No additional system steps are required merely to map every documented endpoint. The separate API Testing deliverable still requires at least three operations, including one that creates or changes data.

## Appendix — API behavioral mapping

This is a supporting mapping to the [API inventory](api-inventory.md). **Planned** means related UI behavior is explicitly checked; **Indirect** means only a related page/flow is exercised. Neither proves that the endpoint is called. WordPress Admin may use other mechanisms; direct API tests or network evidence with response assertions are required for verified API coverage.

### Store API

Base URL: `http://157.85.102.236/shop/wp-json/wc/store/v1`

| API ID | Method / Endpoint | System test steps | Scope |
|---|---|---|---|
| S01 | `GET /products` | ST-G05-01 (steps 3); ST-G05-02 (steps 2); ST-G05-03 (steps 2) | Planned |
| S02 | `GET /products/{id}` | ST-G05-01 (steps 3); ST-G05-02 (steps 2, 9); ST-G05-03 (steps 2) | Planned |
| S03 | `GET /products/categories` | No test case — outside selected scope | Outside scope |
| S04 | `GET /cart` | ST-G05-01 (steps 4, 6); ST-G05-02 (steps 2, 3, 4, 5, 6); ST-G05-03 (steps 3) | Planned |
| S05 | `POST /cart/add-item` | ST-G05-01 (steps 4); ST-G05-02 (steps 2, 6, 9); ST-G05-03 (steps 3) | Planned |
| S06 | `POST /cart/update-item` | ST-G05-02 (steps 3, 4) | Planned |
| S07 | `POST /cart/remove-item` | ST-G05-02 (steps 5) | Planned |
| S08 | `POST /cart/apply-coupon` | ST-G05-01 (steps 5) | Planned |
| S09 | `POST /cart/remove-coupon` | No test case — outside selected scope | Outside scope |
| S10 | `GET /checkout` | ST-G05-01 (steps 6, 7); ST-G05-02 (steps 7); ST-G05-03 (steps 3) | Indirect |
| S11 | `POST /checkout` | ST-G05-01 (steps 7); ST-G05-02 (steps 7); ST-G05-03 (steps 4, 5) | Planned |

### Admin REST API

Base URL: `http://157.85.102.236/shop/wp-json/wc/v3`

| API ID | Method / Endpoint | System test steps | Scope |
|---|---|---|---|
| A01 | `GET /products` | No test case — outside selected scope | Outside scope |
| A02 | `POST /products` | ST-G05-01 (steps 1); ST-G05-02 (steps 1); ST-G05-03 (steps 1) | Planned |
| A03 | `GET /products/{id}` | ST-G05-01 (steps 1); ST-G05-02 (steps 1, 8); ST-G05-03 (steps 1) | Planned |
| A04 | `PUT /products/{id}` | ST-G05-03 (steps 1) | Planned |
| A05 | `DELETE /products/{id}?force=true` | No test case — outside selected scope | Outside scope |
| A06 | `GET /products/categories` | No test case — outside selected scope | Outside scope |
| A07 | `POST /products/categories` | No test case — outside selected scope | Outside scope |
| A08 | `GET /orders` | ST-G05-01 (steps 8) | Planned |
| A09 | `GET /orders/{id}` | ST-G05-01 (steps 8); ST-G05-02 (steps 8); ST-G05-03 (steps 7) | Planned |
| A10 | `PUT /orders/{id}` | ST-G05-01 (steps 9); ST-G05-03 (steps 8) | Planned |
| A11 | `GET /coupons` | No test case — outside selected scope | Outside scope |
| A12 | `POST /coupons` | ST-G05-01 (steps 2) | Planned |
| A13 | `GET /customers` | No test case — outside selected scope | Outside scope |

### API scope notes

- 15 operations have explicit related behavioral steps, 1 is indirect and 8 are outside scope. These are design mappings, not executed coverage.
- S10 is indirect because opening checkout does not inspect the draft-order API response.
- A01 and A11 have no explicit list assertions; navigating through a list is not counted as testing it.
- Inspecting the customer attached to an order does not test A13, the registered-customer list.
- Automatic stock reduction does not count as calling A04.
- UI validation can block an invalid input before an API request is sent.
- Registration, login and customer order history are Web UI features in the guide; no undocumented endpoints are invented.
- Price filters, pagination, sorting, deletion, category creation, coupon removal and customer-list checks are intentionally excluded from this revision.
- No live system tests were run while updating these documents.

## Sources

- `W11-Integration, System and UI Testing_v3.pdf`, slides 33 and 40.
- WooCommerce API Guide, sections 3–5.
- [System test cases — Revision 3](system-test-cases.md), the authoritative step definitions.
