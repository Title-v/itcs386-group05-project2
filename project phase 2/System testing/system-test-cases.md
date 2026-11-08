# System Test Cases — ITCS386 Group 5

These cases follow the supplied Project 2 template. All content is in English.

**Status: Designed / Not Run.** Actual result, Pass or fail, and Tested by and date are intentionally blank. Revision 2 adds explicit steps for all five requirement gaps. Original step numbers are retained; lettered steps identify additions and must be executed in the displayed order. See the [updated traceability matrix](api-traceability-matrix.md).

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
| Objective | Verify the complete staff-to-customer-to-staff flow for product creation, coupon validation, removal/reapplication, discounted checkout, stock reduction and order completion. |
| Preconditions | Staff can log in with Shop manager permissions. A separate customer session has an empty cart. COD is available. No product or coupon uses this run's unique name/code. Shipping/tax settings have been recorded. |
| Test data | Product: `G05 Mug {RUN_ID}`; type: simple; regular price: 200 THB; stock: 20; stock management enabled; backorders disabled. Coupon: `G05SAVE10{RUN_ID}`; percentage discount: 10%; restricted to this product. Invalid coupon: `G05INVALID{RUN_ID}`. Purchase quantity: 2. Email: `g05.st01.{RUN_ID}@example.com`. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product. Reopen its settings to check the saved values. | Product name, simple type, 200 THB, stock 20, stock management on, backorders off | Product is published with the specified price and stock settings. | | |
| 2 | Staff creates a percentage coupon restricted to this product. | Coupon code, discount type Percentage, amount 10, product restriction | Coupon is saved with the correct code, discount and product restriction. | | |
| 2a | Staff opens the Coupons list and searches for the newly created code. | Case coupon code | Exactly the intended coupon is located; its percentage type, amount 10 and product restriction match step 2. | | |
| 3 | Customer searches for the unique product name and opens its details. | `G05 Mug {RUN_ID}` | The correct product is found; details show 200 THB and that it is available to purchase. | | |
| 4 | Customer adds two units and opens the cart. | Quantity 2 | Cart contains the correct product with quantity 2 and merchandise total 400 THB. | | |
| 5 | Customer attempts to apply the nonexistent coupon. | `G05INVALID{RUN_ID}` | Coupon is rejected with a visible error. No discount is applied and merchandise total remains 400 THB. | | |
| 6 | Customer applies the valid coupon. | `G05SAVE10{RUN_ID}` | Coupon is accepted; merchandise discount is 40 THB and discounted merchandise total is 360 THB. | | |
| 6a | Customer removes the applied coupon and refreshes the cart. | Remove control beside the case coupon | Coupon and its discount disappear. Quantity remains 2; merchandise total returns to 400 THB. Shipping/tax are recalculated consistently. | | |
| 6b | Customer reapplies the same coupon before continuing to checkout. | Case coupon code | Exactly one coupon discount of 40 THB is applied; discounted merchandise total is 360 THB, with no duplicate discount. | | |
| 7 | Customer opens checkout, then returns to the cart without placing the order. | Back-to-cart link or browser Back | Product, quantity and coupon remain correct. No successfully placed order is confirmed; a system-created draft is not counted as a placed order. | | |
| 8 | Customer returns to checkout, enters complete fictional details and selects COD. | Shared address/phone, case email, Cash on delivery | Required details are accepted. Product, quantity and discount match the cart; grand total agrees with the displayed shipping/tax breakdown. | | |
| 9 | Customer clicks Place order once. Record the order number. | Completed checkout data | Order confirmation appears with an order number, quantity 2, correct discount/total and COD payment method. | | |
| 10 | Staff searches for the recorded order and opens it. | Order number from step 9 | A matching order is found. Customer details, product, quantity, coupon and totals agree with the confirmation. | | |
| 11 | Staff opens the product's stock settings. | Product created in step 1 | Remaining stock is 18. Returning from checkout did not cause an additional permanent stock deduction. | | |
| 12 | Staff changes the order status to Completed, saves and reopens the order. | Status Completed | Completed persists after reopening; product details and totals remain unchanged. | | |

## ST-G05-02

**Catalog execution prerequisites:** Confirm that the storefront exposes pagination, price sorting and minimum/maximum price controls. Do not change themes, plugins or site settings. If a required control is absent, record the affected step and R22 as Blocked and report the UI/specification mismatch; an API call is not a substitute for this UI test. Record the visible page size. If fewer than two pages exist, create only enough additional G05 catalog fixtures to reach page size + 1 products, with unique names and known prices. Use a stable catalog window; if another group changes it during comparison, record the interference and repeat the affected checks. The fixture names/prices in step 1a are additional test data.

| Field | Details |
|---|---|
| Test case ID | ST-G05-02 |
| Title | Validate quantity limits, cart changes and remaining stock |
| Objective | Verify that stock limits are enforced, catalog pagination/sorting/price filters work, cart quantities and totals update correctly, items can be removed, and a successful purchase reduces stock accurately. |
| Preconditions | Staff can log in. A separate customer session has an empty cart. COD is available. The run uses a new group-owned product. Shipping/tax settings have been recorded. Resolve the zero-quantity expectation below before execution. |
| Test data | Product: `G05 Stock Item {RUN_ID}`; type: simple; price: 150 THB; stock: 3; stock management enabled; backorders and Sold individually disabled. Quantities: 4, 1, 3, 0 and 2. Email: `g05.st02.{RUN_ID}@example.com`. |
| Tested by and date | |

**Open test-design decision:** Before the formal run, inspect the quantity control and agree on one expected behavior for zero: removal, or prevention because the UI minimum is one. Record the chosen expectation and its basis. Do not choose an expectation after seeing the formal test result. Step 8 below always exercises the Remove control, regardless of the zero-quantity behavior.

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product, then verifies its settings. | Product name, 150 THB, stock 3, manage stock on, backorders off, Sold individually off | Product is published with the specified price and stock settings. | | |
| 1a | Staff creates three additional published, in-stock simple products for catalog checks. Open Products, search for the run prefix and verify their saved prices. | G05 Catalog Low {RUN_ID}: 100 THB; G05 Catalog Mid {RUN_ID}: 200 THB; G05 Catalog High {RUN_ID}: 300 THB; no sale prices; stock 10 each | All three records appear with the correct names, prices and stock. Record their IDs and storefront links. | | |
| 1b | Customer opens Shop with filters cleared. Record page 1 product IDs/names; navigate to page 2 and return to page 1. | Visible pagination controls; stable selected sort; at least two pages of products | Page indicator and product list change on page 2. With no concurrent catalog changes, adjacent pages do not repeat product IDs and returning restores page 1. Record concurrent changes if they prevent a reliable comparison. | | |
| 1c | Customer selects price low-to-high, checks every displayed price and continues to subsequent pages as needed to locate the three fixtures. Repeat with price high-to-low. | Visible sort control; Low 100, Mid 200, High 300 THB | Prices follow the selected direction across inspected pages. Low/Mid/High appear in ascending order for low-to-high and reverse order for high-to-low. Equal-priced items may appear in either order. | | |
| 1d | Customer sets the visible minimum and maximum price filters, applies them and inspects all result pages. | Inclusive price range 150–250 THB; the 150 THB stock product plus the three catalog fixtures | Displayed prices fall within 150–250 THB; the stock product at 150 and Mid at 200 are included. Low at 100 and High at 300 are excluded. Filtering is retained during pagination, if multiple result pages exist. | | |
| 1e | Customer clears the price filter and restores the default sort, then locates the fixture products again. | Clear/reset filter and default sort controls | Low and High are visible again; no stale filter remains. Continue with the stock product in step 2; do not add catalog fixtures to the cart. | | |
| 2 | Customer searches for the product and opens its details. | Unique product name | Correct product appears at 150 THB and is available to purchase. | | |
| 3 | Customer attempts to select/add four units using the UI. | Quantity 4 | UI limits the quantity or visibly rejects the attempt. The cart does not accept more than three units. | | |
| 4 | Customer sets the quantity to one and adds the product to the cart. | Quantity 1 | Cart contains one unit of the correct product; merchandise total is 150 THB. | | |
| 5 | Customer changes the cart quantity to three. | Quantity 3 | Updated cart contains three units and merchandise total is 450 THB, with no stock error. | | |
| 6 | Customer attempts to change the cart quantity to four. | Quantity 4 | The excessive quantity is prevented or rejected. Cart does not retain more than three units; totals match the retained valid quantity. | | |
| 7 | Customer attempts to enter zero using the quantity control. | Quantity 0 | Matches the expectation agreed before execution: either the item is removed and totals recalculated, or zero is prevented and the valid cart state remains intact. | | |
| 8 | Ensure the cart contains the test product: if step 7 removed it, add one unit again. Then always click Remove and refresh the cart. | Test product; quantity 1 only if re-adding; Remove control | The Remove control is exercised on every run. The product disappears and no residual quantity or merchandise charge remains after refresh. | | |
| 9 | Customer returns to the product and adds two units. | Quantity 2 | Cart contains two units, merchandise total 300 THB and no duplicate line left from earlier actions. | | |
| 10 | Customer checks out with complete fictional details and COD. Record the order number. | Shared address/phone, case email, COD | Confirmation appears with an order number, two units and merchandise total 300 THB; grand total matches displayed shipping/tax. | | |
| 11 | Staff opens the order and checks the product's stock. | Recorded order number and test product | Order quantity is two and remaining stock is one. Earlier cart changes did not permanently deduct additional stock. | | |
| 12 | Customer reopens the product in a fresh cart and attempts to add two units. | Quantity 2 | The system prevents purchasing more than the one unit remaining. | | |

## ST-G05-03

| Field | Details |
|---|---|
| Test case ID | ST-G05-03 |
| Title | Verify updated pricing, customer account and order history |
| Objective | Verify category creation, customer-list lookup and permanent deletion of a separate disposable product, and that staff price changes reach the storefront and checkout, customer registration/login works, required checkout data is validated, and order details/status remain consistent across staff and customer views. |
| Preconditions | Staff can log in. Customer registration is available through My account. Any required email verification can be completed with an instructor-approved test setup. Start a separate customer session with an empty cart. Use a unique test account and product. Staff can create a new group-owned category and access the registered-customer list. Shipping/tax settings have been recorded. |
| Test data | Product: `G05 Account Item {RUN_ID}`; simple type; initial price: 250 THB; updated regular price: 225 THB; stock: 10; stock management enabled; backorders disabled. New category: `G05 Category {RUN_ID}` with unique slug `g05-category-{RUN_ID}`. Disposable product: `G05 Disposable {RUN_ID}`, simple, 50 THB, stock 1; never purchase it. Record all created IDs. Username if requested: `G05User{RUN_ID}`; email: `g05.st03.{RUN_ID}@example.com`; test password meeting site rules, stored outside the repository. Quantity 1. Invalid checkout input: empty Address line 1. |
| Tested by and date | |

If registration requires verification that the fictional address cannot receive, mark the affected steps Blocked and ask the instructor for a suitable test-account setup. Do not use real personal details or skip registration and report Pass.

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 0a | Staff opens Products → Categories, creates the run-specific category, then searches the category list. | G05 Category {RUN_ID}; slug g05-category-{RUN_ID} | Exactly the intended new category appears with the correct name/slug. Record its ID; existing categories are unchanged. | | |
| 1 | Staff creates and publishes the product in the new category. Open the Products list, search its unique name and reopen its details. | Unique name, price 250 THB, stock 10, category created in step 0a | The intended product appears in the staff list, is published, and has the specified price, stock and new category assignment. | | |

| 2 | Staff changes the regular price, saves and reopens the product. | Price 225 THB | Saved price is 225 THB after reopening. | | |
| 3 | Customer locates the product through the newly created category and through search, then opens its details. | New category and unique product name | Both routes locate the correct product; product details show the current price of 225 THB. | | |
| 4 | Customer registers a new account through My account, completing the supported setup flow. | Unique username if required, case email, test password | Registration succeeds and the customer can access My account after any required setup/verification. | | |
| 5 | Customer logs out and logs back in. | Newly created account credentials | Login succeeds and My account belongs to the correct test customer. | | |
| 6 | Customer adds one unit and opens checkout while logged in. | Quantity 1 | Correct product and quantity appear at 225 THB; the customer session remains authenticated. | | |
| 7 | Customer leaves Address line 1 empty, fills the other required fields and attempts to place the order. | Empty Address line 1; other fictional details complete; COD | Required-field validation is visible. No successful order confirmation appears, and the customer can correct the form. | | |
| 8 | Customer returns to the cart and opens checkout again. | Navigation back to cart and checkout | Product, quantity and price remain correct; the customer remains logged in. | | |
| 9 | Customer completes the missing details and places the COD order. Record its number. | Complete fictional address/phone, case email, COD | Confirmation appears with an order number and merchandise price 225 THB, not the old 250 THB price. Grand total matches displayed shipping/tax. | | |
| 10 | Customer opens My account → Orders and views the new order. | Recorded order number | The customer's order appears; product, quantity and totals match the confirmation. | | |
| 11 | Staff opens the order and inspects its associated customer details. | Recorded order number and case email | Order is associated with the newly registered customer, and details agree with the customer view. | | |
| 11a | Staff opens the registered-customer list and locates the new account by its exact email. Compare it with the account associated with the order. | Case email and recorded order number | The registered customer is found in the list, not only in the order details. Identity/email matches the account created in step 4 and linked to the order; no unrelated customer is edited. | | |
| 12 | Staff changes the order to Completed and saves. | Status Completed | Updated status is saved successfully. | | |
| 13 | Customer refreshes order history and opens the order details. | Same customer account and order | Status is Completed; product details and totals remain unchanged. | | |
| 14 | Customer logs out, logs in again and reopens Orders. | Same account credentials | The order remains accessible with the correct details and Completed status. | | |
| 15 | Staff creates and publishes a disposable product in the new category. Customer opens its storefront page to establish that it exists. | G05 Disposable {RUN_ID}; price 50 THB; stock 1; simple; new category | The separate disposable product appears in the staff list and storefront with correct details. Record its exact ID/URL. It has not been added to any order. | | |
| 16 | Staff verifies the disposable product ID, moves only that product to Trash, then uses Delete permanently on that record. | Disposable product ID from step 15; never the purchased product | The specified disposable product is permanently removed, not merely left in Trash. Other products are unchanged. | | |
| 17 | Staff searches Products, including Trash. Customer searches the catalog and opens the recorded disposable-product URL, then rechecks the purchased product and order. | Deleted product name/URL; purchased product ID and order number | Deleted product is absent from staff lists, Trash and customer search; its former URL no longer offers it for purchase. Purchased product and completed order remain accessible with unchanged details. | | |

## Related documentation

- [API inventory](api-inventory.md)
- [System requirement traceability matrix and API appendix](api-traceability-matrix.md)

The linked traceability document contains the slide-style requirement matrix followed by the supporting API behavioral mapping. Execution evidence and defect reports must be added after real manual runs; this document does not claim any completed testing.
