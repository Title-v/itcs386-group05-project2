# System Test Traceability Matrix — ITCS386 Group 5

## Requirement-to-test-case matrix

This matrix follows slide 40, **System Test Cases and Traceability**, in `W11-Integration, System and UI Testing_v3.pdf`: each requirement is mapped to its test cases using two columns. **No test case** identifies a gap.

Requirements below are group-defined, testable behaviors derived from the WooCommerce API Guide's features. R1–R22 are local document identifiers, not requirement numbers supplied by the instructor. They refine the earlier broad feature labels so missing behaviors remain visible.

**Status: Designed / Not Run.** A mapping identifies planned coverage, not a passing result. See [System test cases](system-test-cases.md) for actions, input data and expected results.

| Requirement | Test cases |
|---|---|
| **R1 Search for products by name** | ST-G05-01, ST-G05-02, ST-G05-03 |
| **R2 Browse products in a selected category** | ST-G05-03 |
| **R3 View product details, current price and availability** | ST-G05-01, ST-G05-02, ST-G05-03 |
| **R4 Add products to the cart and display correct quantities and totals** | ST-G05-01, ST-G05-02, ST-G05-03 |
| **R5 Change cart quantities and enforce stock limits** | ST-G05-02 |
| **R6 Remove an item and recalculate the cart** | ST-G05-02 (conditional: step 8) |
| **R7 Apply a valid coupon and reject a nonexistent coupon** | ST-G05-01 |
| **R8 Remove a coupon and restore the undiscounted total** | No test case |
| **R9 Preserve cart contents when returning from checkout** | ST-G05-01, ST-G05-03 |
| **R10 Reject checkout when required address data is missing** | ST-G05-03 |
| **R11 Place a COD order and display the correct confirmation** | ST-G05-01, ST-G05-02, ST-G05-03 |
| **R12 Register a customer account and log out/log in** | ST-G05-03 |
| **R13 View the customer's own order history and updated status** | ST-G05-03 |
| **R14 Create and publish a product with price, category and stock settings** | ST-G05-01, ST-G05-02, ST-G05-03 |
| **R15 Update a product price and show the new price to customers** | ST-G05-03 |
| **R16 Reduce stock correctly after a successful purchase** | ST-G05-01, ST-G05-02 |
| **R17 Permanently delete a group-owned product** | No test case |
| **R18 Create a product category** | No test case |
| **R19 Inspect order details and change the status to Completed** | ST-G05-01, ST-G05-03 |
| **R20 Create a product-restricted percentage coupon** | ST-G05-01 |
| **R21 List registered customers and locate a specific customer** | No test case |
| **R22 Browse catalog pages using sorting and price filters** | No test case |

## Test case key

| Test case ID | Title |
|---|---|
| ST-G05-01 | Purchase with a coupon and complete the order |
| ST-G05-02 | Validate quantity limits, cart changes and remaining stock |
| ST-G05-03 | Verify updated pricing, customer account and order history |

## Coverage notes and gaps

- R14 is covered across the cases: all three create products with price/stock settings; category assignment is explicit in ST-G05-03 step 1.
- R6 is conditional because ST-G05-02 step 8 is skipped if quantity zero already removed the item. Make removal unconditional before claiming reliable coverage on every run.
- R21 remains a gap: ST-G05-03 step 11 inspects the customer associated with an order, but does not explicitly open or check the registered-customer list.
- R8, R17 and R18 can be addressed by the proposed coupon-removal, product-deletion and category-creation steps in the API appendix.
- R22 needs explicit catalog paging, sorting and price-filter steps with expected results.
- ST-G05-02's zero-quantity expectation must be agreed before formal execution. ST-G05-03 registration may be Blocked if an approved test-email setup is unavailable.
- The current matrix includes **22 requirements: 16 with unconditional planned mappings, 1 conditional mapping and 5 with no test case**. These counts describe this requirement breakdown, not complete specification coverage or execution results.
- Other untested variants, including product variations and additional coupon types, remain outside the three-case baseline. Do not describe this plan as full coverage of every guide detail.

## Sources and scope

- `W11-Integration, System and UI Testing_v3.pdf`, slides 33 and 40: observable system behavior and the Requirement / Test cases format.
- WooCommerce API Guide, section 3: shop features; sections 4–5: related API operations.
- [Current manual system test cases](system-test-cases.md).

The requirement matrix is the primary system-testing view. The API mapping below is supporting technical traceability; UI behavior does not prove that a particular endpoint was called.

---

# Appendix — API Behavioral Traceability

## Scope and status

Maps all 24 operations in the [API inventory](api-inventory.md) to the three planned system test cases.

**Baseline:** Original system test plan, before adding gap-closing steps.  
**Execution status:** Not Run for every case.  
**Endpoint evidence:** No network capture or API test results confirm actual endpoint calls.

This is a **behavioral mapping**: UI steps exercise behavior related to an API operation, but do not prove that the UI calls that endpoint. WordPress Admin may use form submissions or other mechanisms. Network inspection can confirm only requests actually observed; endpoints not called by the UI need separate direct API tests.

Numbers refer to the baseline steps reproduced later in this document:

- **P (Planned):** An explicit step checks related behavior, but has not been executed.
- **I (Indirect):** Related behavior is exercised indirectly; the operation itself is not checked.
- **C (Conditional):** The step depends on a condition and may not run every time.
- **— (Gap):** No explicit step exists.

P does not mean Pass or verified API coverage.

## Test case index

| Short ID | Full ID | Scenario |
|---|---|---|
| ST-01 | ST-G05-01 | Staff creates a product and coupon → Customer purchases with the discount → Staff checks the order/stock and completes the order |
| ST-02 | ST-G05-02 | Staff sets stock → Customer tries unusual quantities, changes/removes cart items and purchases → Staff checks order/stock → Customer checks remaining availability |
| ST-03 | ST-G05-03 | Staff creates a product and changes its price → Customer registers/logs in, purchases and views history → Staff checks customer/order and completes it → Customer checks status |

## 1. Store API

Base URL: `http://157.85.102.236/shop/wp-json/wc/store/v1`

| API ID | Method / Endpoint | ST-01 steps | ST-02 steps | ST-03 steps | Mapping | Coverage / limitation |
|---|---|---|---|---|---|---|
| S01 | GET `/products` | 3 | 2 | 3 | P | Search/list products; pagination, sorting, price filters and query combinations remain untested |
| S02 | GET `/products/{id}` | 3 | 2, 12 | 3 | P | Details, price and availability; invalid IDs and variations remain untested |
| S03 | GET `/products/categories` | — | — | 3 | I | Browse by category; does not inspect the category-list response |
| S04 | GET `/cart` | 4, 7 | 4–9 | 6, 8 | P | Check items, quantities and totals; token lifecycle is not checked directly |
| S05 | POST `/cart/add-item` | 4 | 3–4, 9, 12 | 6 | P | Normal and excessive quantities; UI validation may prevent a request |
| S06 | POST `/cart/update-item` | — | 5–7 | — | P | Change quantities, including zero and above-stock values; finalize the expected zero-quantity behavior after UI inspection |
| S07 | POST `/cart/remove-item` | — | 8 | — | C | Remove is used only if the item remains after quantity=0, so this step may be skipped |
| S08 | POST `/cart/apply-coupon` | 5–6 | — | — | P | Nonexistent and valid 10% coupons; expired, usage-limit and minimum-spend cases remain untested |
| S09 | POST `/cart/remove-coupon` | — | — | — | — | No coupon-removal or restored-total check |
| S10 | GET `/checkout` | 7–8 | 10 | 6, 8 | I | Opening checkout does not directly check the draft-order API response |
| S11 | POST `/checkout` | 9 | 10 | 7, 9 | P | Successful COD and a missing required field; UI validation may prevent a request |

## 2. Admin REST API

Base URL: `http://157.85.102.236/shop/wp-json/wc/v3`

| API ID | Method / Endpoint | ST-01 steps | ST-02 steps | ST-03 steps | Mapping | Coverage / limitation |
|---|---|---|---|---|---|---|
| A01 | GET `/products` | — | — | — | — | No explicit staff product-list/search check |
| A02 | POST `/products` | 1 | 1 | 1 | P | Staff creates a simple product; does not confirm that Admin UI uses this REST endpoint |
| A03 | GET `/products/{id}` | 11 | 11 | 2 | P | Staff checks an individual product's stock/price |
| A04 | PUT `/products/{id}` | — | — | 2 | P | Staff changes the price; automatic stock reduction after purchase is not coverage of this PUT operation |
| A05 | DELETE `/products/{id}?force=true` | — | — | — | — | No permanent deletion; moving a product to Trash does not match force=true |
| A06 | GET `/products/categories` | — | — | 1 | I | Select an existing category when creating a product; no direct category-list response check |
| A07 | POST `/products/categories` | — | — | — | — | No category creation |
| A08 | GET `/orders` | 10 | — | — | P | Staff searches for an order; status/date filters and pagination remain untested |
| A09 | GET `/orders/{id}` | 10 | 11 | 11 | P | Inspect an order and compare it with the customer confirmation |
| A10 | PUT `/orders/{id}` | 12 | — | 12 | P | Change status to Completed; other statuses and invalid transitions remain untested |
| A11 | GET `/coupons` | — | — | — | — | No explicit coupon-list/search check |
| A12 | POST `/coupons` | 2 | — | — | P | Create a 10% coupon; fixed_cart and fixed_product remain untested |
| A13 | GET `/customers` | — | — | 11 | I | Inspect the customer associated with an order; opening the Customers list is not explicitly required yet |

## 3. Coverage summary

Count each API ID once, even if it maps to multiple cases.

| Mapping status | Store | Admin | Total |
|---|---|---|---|
| P — Explicit related steps, not executed | 7 | 7 | 14 |
| I — Indirect | 2 | 2 | 4 |
| C — Conditional | 1 | 0 | 1 |
| Gap — No explicit steps | 1 | 4 | 5 |
| **Total operations** | **11** | **13** | **24** |

- P/I/C mappings total **19/24 operations**. These are planned relationships, not test results.
- Gaps: **S09, A01, A05, A07, A11**.
- All cases are **Not Run**. No Pass/Fail results or verified API coverage count is available.
- Mapping all 24 operations would not cover every input, response, authorization rule or error condition.

## 4. Proposed gap-closing steps — not yet part of baseline

These proposals have not been executed and are not counted in the matrix above. When incorporated into the test cases, update the step references and matrix together.

| Proposal | Insert at | Action | Expected result | API IDs |
|---|---|---|---|---|
| GAP-01 | ST-01 after step 2 | Open Coupons and search for the created code | The coupon appears with the correct type and discount | A11 |
| GAP-02 | ST-01 after step 6 | Remove the coupon, then apply it again | Merchandise total returns to 400 THB, then becomes 360 THB after reapplication; account for shipping/tax separately | S09, S08 |
| GAP-03 | ST-03 before step 1 | Create a G05 category with RUN_ID and inspect the list | The new category matches the input and can be assigned to the case's product | A07, A06 |
| GAP-04 | ST-03 after step 1 | Open Products, search for the unique name and open the result | The correct product appears with matching details | A01, A03 |
| GAP-05 | Near the end of ST-03 | Create a disposable product separate from the ordered product, then permanently delete it | The deleted product is absent from staff/customer listings; the ordered product remains intact | A02, A05, A01, S01 |
| REFINE-01 | ST-02 step 8 | If the cart is empty, add one item first; always click Remove | Remove is exercised every run and leaves an empty cart | S07 |
| REFINE-02 | ST-03 step 11 | Explicitly open Customers and search by the test email | The correct customer appears and matches the order | A13 |

These changes address behavioral gaps. Direct API tests or network evidence are still required to claim endpoint coverage.

## 5. Baseline step reference

Based on the test plan designed on 9 November 2026. This reference makes the matrix self-contained. **It does not replace full manual test cases**, which need preconditions, test data, expected/actual results for every step, tester/date and screenshots.

Prefix test data names with G05 and a unique RUN_ID. All products must be created by this group.

### ST-G05-01 — Coupon purchase and order completion

Test data: simple product priced at 200 THB, stock 20; a 10% coupon restricted to this product; purchase quantity 2.

| Step | Planned action / checkpoint |
|---|---|
| 1 | Staff creates and publishes the product, enables stock management and disables backorders |
| 2 | Staff creates the product-restricted 10% coupon |
| 3 | Customer searches for and opens the product; checks the 200 THB price and availability |
| 4 | Add two items; verify a 400 THB merchandise total |
| 5 | Apply a nonexistent coupon; expect rejection with no change in total |
| 6 | Apply the created coupon; verify a 40 THB discount and 360 THB discounted merchandise total |
| 7 | Open checkout and return to the cart; check product/quantity/coupon and that no order has been successfully placed |
| 8 | Return to checkout, enter complete fictional details, select COD and verify the total including displayed shipping/tax |
| 9 | Click Place order once; verify confirmation and order number |
| 10 | Staff searches for the order and compares its details with the confirmation |
| 11 | Staff verifies that remaining stock is 18 |
| 12 | Staff changes the order to Completed and reopens it to verify the status |

### ST-G05-02 — Quantity, stock and cart changes

Test data: simple product priced at 150 THB, stock 3; stock management enabled; backorders and sold individually disabled.

| Step | Planned action / checkpoint |
|---|---|
| 1 | Staff creates and publishes the product using the specified test data |
| 2 | Customer searches for and opens the product; checks price and availability |
| 3 | Try adding four items; the cart must not accept more than the available stock of three |
| 4 | Add one item; verify a 150 THB merchandise total |
| 5 | Change the quantity to three; verify a 450 THB merchandise total |
| 6 | Try changing the quantity to four; the cart must not retain a quantity above stock |
| 7 | Try quantity=0; inspect whether it removes the item or is blocked by the UI, then finalize the expected behavior before automation |
| 8 | If the item remains, click Remove and verify that the cart is empty |
| 9 | Return to the product and add two items; verify a 300 THB merchandise total with no duplicate lines |
| 10 | Check out with fictional details and COD; verify confirmation |
| 11 | Staff verifies an order quantity of two and remaining stock of one |
| 12 | Customer reopens the product and tries adding two; the remaining stock limit must be enforced |

### ST-G05-03 — Updated price, customer account and order history

Test data: simple product initially priced at 250 THB, changed to 225 THB, stock 10; an existing category; a new customer with a fictional email unique to RUN_ID.

| Step | Planned action / checkpoint |
|---|---|
| 1 | Staff creates the product and selects an existing category |
| 2 | Staff changes the price from 250 to 225 THB, saves and reopens the product to verify |
| 3 | Customer browses the category, searches for and opens the product; verifies the current price |
| 4 | Customer registers a new account through My account |
| 5 | Log out and log in; verify that the correct account is active |
| 6 | Add one item and open checkout; verify the 225 THB price |
| 7 | Leave Address line 1 empty and attempt to order; expect required-field validation and no successful order confirmation |
| 8 | Return to the cart and reopen checkout; verify cart contents and the login session |
| 9 | Complete the details and place a COD order; verify confirmation and the 225 THB price |
| 10 | Customer opens My account → Orders and checks their order |
| 11 | Staff opens the order and checks its associated customer details |
| 12 | Staff changes the order to Completed |
| 13 | Customer refreshes order history and verifies the Completed status |
| 14 | Log out and log in again; verify that the order and status remain available |

If registration requires email verification that the fictional account cannot receive, mark the case Blocked and ask the instructor about test accounts. Do not skip the step and report Pass.

## 6. Evidence and limitations

- Record actual results and screenshots for each executed step. Mark steps that cannot proceed as Blocked.
- When inspecting network traffic, associate API ID with case/step, method, path, status and evidence. Do not expose passwords, Authorization headers, Cart-Tokens or personal data.
- A captured request alone does not prove response correctness. Check expected status and response fields too.
- Account registration/login and customer order history are Web UI features in the guide. Do not invent undocumented endpoints.
- Invalid Basic Auth, invalid Cart-Token/Nonce, unknown IDs, malformed input and query boundaries still need API test suite designs.
- Do not modify/delete demo data or records owned by other groups.
- Do not create orders/bookings during performance/load tests. Checkout here is functional system testing.
- This document does not change Project 2 into a requirement to test all 24 API operations. The API Testing assignment requires at least three operations, including at least one that creates or changes data.
