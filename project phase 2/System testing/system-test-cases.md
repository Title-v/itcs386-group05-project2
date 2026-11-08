# System Test Cases — ITCS386 Group 5

These cases follow the supplied Project 2 template. All content is in English.

**Status: Designed / Not Run.** Actual result, Pass or fail, and Tested by and date are intentionally blank. Step numbers match the original baseline in the [traceability matrix's API appendix](api-traceability-matrix.md). Proposed gap-closing steps in that document are not included here.

## Shared execution setup

- Storefront: http://157.85.102.236/shop/
- Staff interface: http://157.85.102.236/shop/wp-admin/
- Staff username: `itcs386-g05`; obtain the browser login password from the group accounts sheet. Do not put credentials in this document or screenshots.
- Use separate browser sessions for staff and customer. Start each case with its own customer session and empty cart.
- Set a unique `RUN_ID`, such as `20261109-143000`, for each run. Prefix created names/codes with `G05`.
- Use only group-created products and fictional personal data. Do not change demo data or other groups' records.
- Fictional checkout data: first name `G05`, last name `Test`, address `1 Test Road`, city `Bangkok`, province `Bangkok`, postcode `10200`, country `Thailand`, phone `0800000000`. Use the case-specific email below. Use the same fictional shipping address.
- Merchandise totals below exclude separately displayed shipping and tax. Record the site's tax display configuration and shipping charges before execution, and verify the grand total against the displayed breakdown. The discount calculations assume the stated merchandise prices are the discount basis.
- Save a screenshot for each executed step under `screenshots/<test-case-ID>/<RUN_ID>/`, named `S01.png`, `S02.png`, etc. Record the path and observed values in Actual result.
- After execution, enter Pass or Fail. Use Blocked when a prerequisite failure prevents execution; use Not Applicable only for an explicitly conditional step and explain why.
- For each failed step, record a defect ID, reproduction steps, expected/actual results and evidence. Distinguish a product defect from a test/setup problem.
- These are manual UI tests. Their related API mappings do not prove that the UI calls those endpoints.

## ST-G05-01

| Field | Details |
|---|---|
| Test case ID | ST-G05-01 |
| Title | Purchase with a coupon and complete the order |
| Objective | Verify the complete staff-to-customer-to-staff flow for product creation, coupon validation, discounted checkout, stock reduction and order completion. |
| Preconditions | Staff can log in with Shop manager permissions. A separate customer session has an empty cart. COD is available. No product or coupon uses this run's unique name/code. Shipping/tax settings have been recorded. |
| Test data | Product: `G05 Mug {RUN_ID}`; type: simple; regular price: 200 THB; stock: 20; stock management enabled; backorders disabled. Coupon: `G05SAVE10{RUN_ID}`; percentage discount: 10%; restricted to this product. Invalid coupon: `G05INVALID{RUN_ID}`. Purchase quantity: 2. Email: `g05.st01.{RUN_ID}@example.com`. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product. Reopen its settings to check the saved values. | Product name, simple type, 200 THB, stock 20, stock management on, backorders off | Product is published with the specified price and stock settings. | | |
| 2 | Staff creates a percentage coupon restricted to this product. | Coupon code, discount type Percentage, amount 10, product restriction | Coupon is saved with the correct code, discount and product restriction. | | |
| 3 | Customer searches for the unique product name and opens its details. | `G05 Mug {RUN_ID}` | The correct product is found; details show 200 THB and that it is available to purchase. | | |
| 4 | Customer adds two units and opens the cart. | Quantity 2 | Cart contains the correct product with quantity 2 and merchandise total 400 THB. | | |
| 5 | Customer attempts to apply the nonexistent coupon. | `G05INVALID{RUN_ID}` | Coupon is rejected with a visible error. No discount is applied and merchandise total remains 400 THB. | | |
| 6 | Customer applies the valid coupon. | `G05SAVE10{RUN_ID}` | Coupon is accepted; merchandise discount is 40 THB and discounted merchandise total is 360 THB. | | |
| 7 | Customer opens checkout, then returns to the cart without placing the order. | Back-to-cart link or browser Back | Product, quantity and coupon remain correct. No successfully placed order is confirmed; a system-created draft is not counted as a placed order. | | |
| 8 | Customer returns to checkout, enters complete fictional details and selects COD. | Shared address/phone, case email, Cash on delivery | Required details are accepted. Product, quantity and discount match the cart; grand total agrees with the displayed shipping/tax breakdown. | | |
| 9 | Customer clicks Place order once. Record the order number. | Completed checkout data | Order confirmation appears with an order number, quantity 2, correct discount/total and COD payment method. | | |
| 10 | Staff searches for the recorded order and opens it. | Order number from step 9 | A matching order is found. Customer details, product, quantity, coupon and totals agree with the confirmation. | | |
| 11 | Staff opens the product's stock settings. | Product created in step 1 | Remaining stock is 18. Returning from checkout did not cause an additional permanent stock deduction. | | |
| 12 | Staff changes the order status to Completed, saves and reopens the order. | Status Completed | Completed persists after reopening; product details and totals remain unchanged. | | |

## ST-G05-02

| Field | Details |
|---|---|
| Test case ID | ST-G05-02 |
| Title | Validate quantity limits, cart changes and remaining stock |
| Objective | Verify that stock limits are enforced, cart quantities and totals update correctly, items can be removed, and a successful purchase reduces stock accurately. |
| Preconditions | Staff can log in. A separate customer session has an empty cart. COD is available. The run uses a new group-owned product. Shipping/tax settings have been recorded. Resolve the zero-quantity expectation below before execution. |
| Test data | Product: `G05 Stock Item {RUN_ID}`; type: simple; price: 150 THB; stock: 3; stock management enabled; backorders and Sold individually disabled. Quantities: 4, 1, 3, 0 and 2. Email: `g05.st02.{RUN_ID}@example.com`. |
| Tested by and date | |

**Open test-design decision:** Before the formal run, inspect the quantity control and agree on one expected behavior for zero: removal, or prevention because the UI minimum is one. Record the chosen expectation and its basis. Do not choose an expectation after seeing the formal test result. Step 8 remains conditional to preserve the traceability baseline; see REFINE-01 in the matrix for a proposal to make removal unconditional.

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product, then verifies its settings. | Product name, 150 THB, stock 3, manage stock on, backorders off, Sold individually off | Product is published with the specified price and stock settings. | | |
| 2 | Customer searches for the product and opens its details. | Unique product name | Correct product appears at 150 THB and is available to purchase. | | |
| 3 | Customer attempts to select/add four units using the UI. | Quantity 4 | UI limits the quantity or visibly rejects the attempt. The cart does not accept more than three units. | | |
| 4 | Customer sets the quantity to one and adds the product to the cart. | Quantity 1 | Cart contains one unit of the correct product; merchandise total is 150 THB. | | |
| 5 | Customer changes the cart quantity to three. | Quantity 3 | Updated cart contains three units and merchandise total is 450 THB, with no stock error. | | |
| 6 | Customer attempts to change the cart quantity to four. | Quantity 4 | The excessive quantity is prevented or rejected. Cart does not retain more than three units; totals match the retained valid quantity. | | |
| 7 | Customer attempts to enter zero using the quantity control. | Quantity 0 | Matches the expectation agreed before execution: either the item is removed and totals recalculated, or zero is prevented and the valid cart state remains intact. | | |
| 8 | If the item remains, customer clicks Remove. If already removed in step 7, record Not Applicable with evidence. | Remove control for the test product | After removal, the cart contains no test product and no residual quantity or charge for it. | | |
| 9 | Customer returns to the product and adds two units. | Quantity 2 | Cart contains two units, merchandise total 300 THB and no duplicate line left from earlier actions. | | |
| 10 | Customer checks out with complete fictional details and COD. Record the order number. | Shared address/phone, case email, COD | Confirmation appears with an order number, two units and merchandise total 300 THB; grand total matches displayed shipping/tax. | | |
| 11 | Staff opens the order and checks the product's stock. | Recorded order number and test product | Order quantity is two and remaining stock is one. Earlier cart changes did not permanently deduct additional stock. | | |
| 12 | Customer reopens the product in a fresh cart and attempts to add two units. | Quantity 2 | The system prevents purchasing more than the one unit remaining. | | |

## ST-G05-03

| Field | Details |
|---|---|
| Test case ID | ST-G05-03 |
| Title | Verify updated pricing, customer account and order history |
| Objective | Verify that staff price changes reach the storefront and checkout, customer registration/login works, required checkout data is validated, and order details/status remain consistent across staff and customer views. |
| Preconditions | Staff can log in. Customer registration is available through My account. Any required email verification can be completed with an instructor-approved test setup. Start a separate customer session with an empty cart. Use a unique test account and product. An existing category can be selected without changing it. Shipping/tax settings have been recorded. |
| Test data | Product: `G05 Account Item {RUN_ID}`; simple type; initial price: 250 THB; updated regular price: 225 THB; stock: 10; stock management enabled; backorders disabled. Record the selected existing category. Username if requested: `G05User{RUN_ID}`; email: `g05.st03.{RUN_ID}@example.com`; test password meeting site rules, stored outside the repository. Quantity 1. Invalid checkout input: empty Address line 1. |
| Tested by and date | |

If registration requires verification that the fictional address cannot receive, mark the affected steps Blocked and ask the instructor for a suitable test-account setup. Do not use real personal details or skip registration and report Pass.

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product, assigning it to an existing category. | Unique name, price 250 THB, stock 10, selected category | Product is published with the specified price/stock and category assignment. The existing category itself is unchanged. | | |
| 2 | Staff changes the regular price, saves and reopens the product. | Price 225 THB | Saved price is 225 THB after reopening. | | |
| 3 | Customer locates the product through the selected category and through search, then opens its details. | Selected category and unique product name | Both routes locate the correct product; product details show the current price of 225 THB. | | |
| 4 | Customer registers a new account through My account, completing the supported setup flow. | Unique username if required, case email, test password | Registration succeeds and the customer can access My account after any required setup/verification. | | |
| 5 | Customer logs out and logs back in. | Newly created account credentials | Login succeeds and My account belongs to the correct test customer. | | |
| 6 | Customer adds one unit and opens checkout while logged in. | Quantity 1 | Correct product and quantity appear at 225 THB; the customer session remains authenticated. | | |
| 7 | Customer leaves Address line 1 empty, fills the other required fields and attempts to place the order. | Empty Address line 1; other fictional details complete; COD | Required-field validation is visible. No successful order confirmation appears, and the customer can correct the form. | | |
| 8 | Customer returns to the cart and opens checkout again. | Navigation back to cart and checkout | Product, quantity and price remain correct; the customer remains logged in. | | |
| 9 | Customer completes the missing details and places the COD order. Record its number. | Complete fictional address/phone, case email, COD | Confirmation appears with an order number and merchandise price 225 THB, not the old 250 THB price. Grand total matches displayed shipping/tax. | | |
| 10 | Customer opens My account → Orders and views the new order. | Recorded order number | The customer's order appears; product, quantity and totals match the confirmation. | | |
| 11 | Staff opens the order and inspects its associated customer details. | Recorded order number and case email | Order is associated with the newly registered customer, and details agree with the customer view. | | |
| 12 | Staff changes the order to Completed and saves. | Status Completed | Updated status is saved successfully. | | |
| 13 | Customer refreshes order history and opens the order details. | Same customer account and order | Status is Completed; product details and totals remain unchanged. | | |
| 14 | Customer logs out, logs in again and reopens Orders. | Same account credentials | The order remains accessible with the correct details and Completed status. | | |

## Related documentation

- [API inventory](api-inventory.md)
- [System requirement traceability matrix and API appendix](api-traceability-matrix.md)

The linked traceability document contains the slide-style requirement matrix followed by the supporting API behavioral mapping. Execution evidence and defect reports must be added after real manual runs; this document does not claim any completed testing.
