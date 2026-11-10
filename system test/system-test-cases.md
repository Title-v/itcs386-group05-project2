# System Test Cases — ITCS386 Group 5

**Revision 3 — focused scope. Status: Designed / Not Run.** These three manual scenarios use the Project 2 template and cover staff → customer → staff outcomes. Step numbers restart at 1 in each case and match the [traceability matrix](api-traceability-matrix.md). Actual result, Pass or fail and Tested by and date remain blank until execution.

## Shared execution setup

- Storefront: http://157.85.102.236/shop/
- Staff interface: http://157.85.102.236/shop/wp-admin/
- Staff account: `itcs386-g05`. Obtain the browser password from the accounts sheet; never commit credentials.
- Use separate staff/customer sessions. Each case creates its own product with a unique `RUN_ID`, such as `20261109-143000`. Prefix names/codes with G05.
- Use only group-owned records; do not change demo data or other groups' records.
- Fictional checkout details: G05 Test, 1 Test Road, Bangkok, Bangkok province, 10200, Thailand, phone 0800000000. Use the case email; use the same fictional shipping address.
- Verify merchandise arithmetic separately from shipping/tax. Record the site's price/tax display basis and shipping charges before execution, then check the grand total against that breakdown. The 10% coupon calculation assumes the stated merchandise price is the discount basis.
- Save screenshots for every step under `screenshots/<case-ID>/<RUN_ID>/`; reference their paths and observed values in Actual result.
- Enter Pass or Fail only after running a step. Use Blocked if prerequisites prevent execution. Failed steps need a defect report with reproduction steps, expected/actual results and evidence.
- ST-G05-03 needs a pre-existing group-owned fictional customer account. If unavailable, prepare one through the supported setup flow or obtain an approved test account before running; do not claim registration coverage.
- No live tests or server-side changes were performed while preparing this revision.

## Selected scope

The scenarios retain unusual inputs and actions: an invalid coupon and returning from checkout, an above-stock quantity and removing/re-adding an item, and a missing required address field followed by correction.

Category creation/browsing, permanent deletion, coupon removal, customer-list checks, catalog pagination/sorting/price filters and registration testing are outside this revision. No extra fixtures are required to exercise every API.

## ST-G05-01

| Field | Details |
|---|---|
| Test case ID | ST-G05-01 |
| Title | Purchase with a coupon and complete the order |
| Objective | Verify product/coupon setup, invalid coupon rejection, discounted purchase and staff order completion. |
| Preconditions | Staff is logged in. Customer uses a separate session with an empty cart. COD is available. |
| Test data | Product: `G05 Mug {RUN_ID}`, simple, 200 THB, stock 20, backorders disabled. Coupon: `G05SAVE10{RUN_ID}`, 10% discount restricted to this product. Invalid code: `G05INVALID{RUN_ID}`. Quantity 2. Email: `g05.st01.{RUN_ID}@example.com`. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product and verifies its saved settings. | Product name, price 200 THB, stock 20; enable stock management | Product is published with the specified price and stock. | | |
| 2 | Staff creates the product-restricted coupon. | Case coupon code; percentage 10 | Coupon is saved with the correct product restriction and discount. | | |
| 3 | Customer searches for and opens the product. | Unique product name | Correct product appears at 200 THB and is available to buy. | | |
| 4 | Customer adds two units and opens the cart. | Quantity 2 | Cart contains two units with merchandise subtotal 400 THB. | | |
| 5 | Customer tries the nonexistent coupon, then applies the valid coupon. | Invalid code, followed by the case coupon | Invalid code produces a visible error without changing the total. Valid code applies one 40 THB discount; discounted merchandise total is 360 THB. | | |
| 6 | Customer opens checkout and returns to the cart before ordering. | Back-to-cart link or browser Back | Product, quantity and coupon remain correct; no successful order confirmation appears. | | |
| 7 | Customer reopens checkout, enters fictional details and places one COD order. | Shared address/phone; case email; COD | Confirmation shows an order number, two units, the 40 THB discount and the correct grand total. | | |
| 8 | Staff locates and opens the order. | Order number from step 7 | Order details, coupon and total agree with the customer confirmation. | | |
| 9 | Staff changes the order to Completed, saves and reopens it. | Status Completed | Completed persists; order contents and totals are unchanged. | | |

## ST-G05-02

| Field | Details |
|---|---|
| Test case ID | ST-G05-02 |
| Title | Validate quantity limits and remaining stock |
| Objective | Verify stock-limit validation, cart quantity changes/removal and stock reduction after a successful purchase. |
| Preconditions | Staff is logged in. Customer uses a separate session with an empty cart. COD is available. |
| Test data | Product: `G05 Stock Item {RUN_ID}`, simple, 150 THB, stock 3. Enable stock management; disable backorders and Sold individually. Quantities 1, 4 and 2. Email: `g05.st02.{RUN_ID}@example.com`. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product, then verifies the saved stock settings. | Price 150 THB; stock 3; backorders disabled | Product is published at 150 THB with stock 3 and no backorders. | | |
| 2 | Customer searches for the product, opens it and adds one unit to the cart. | Unique product name; quantity 1 | Correct product appears at 150 THB; cart contains one unit with merchandise subtotal 150 THB. | | |
| 3 | Customer attempts to change the cart quantity to four. | Quantity 4 | The excessive quantity is prevented or rejected with visible feedback; cart does not retain more than stock 3. | | |
| 4 | Customer changes the cart quantity to two. | Quantity 2 | Cart updates to two units and merchandise subtotal 300 THB. | | |
| 5 | Customer removes the product from the cart. | Remove control | Cart becomes empty with no remaining merchandise charge for the product. | | |
| 6 | Customer returns to the product and adds two units again. | Quantity 2 | Cart contains exactly two units with merchandise subtotal 300 THB and no duplicate line. | | |
| 7 | Customer completes checkout with fictional details and COD. | Shared address/phone; case email; COD | Confirmation shows an order number, two units and merchandise total 300 THB; grand total matches displayed shipping/tax. | | |
| 8 | Staff opens the order and the product's stock settings. | Order number from step 7; test product | Order quantity is two and remaining stock is one. Earlier cart changes did not cause extra permanent stock deductions. | | |
| 9 | Customer opens the product in a fresh cart and tries to add two units. | Quantity 2 | The system prevents adding more than the one unit remaining. | | |

## ST-G05-03

| Field | Details |
|---|---|
| Test case ID | ST-G05-03 |
| Title | Verify updated pricing and customer order history |
| Objective | Verify that a staff price update is used for a logged-in purchase and that the completed order appears correctly in customer history. |
| Preconditions | Staff is logged in. A group-owned fictional customer account already exists and can log in. Account creation is setup, not a tested requirement. Customer cart is empty; COD is available. |
| Test data | Product: `G05 Account Item {RUN_ID}`, simple, initial price 250 THB, new price 225 THB, stock 10, backorders disabled. Quantity 1. Use the existing test account email and credentials, stored outside the repository. Invalid input: leave Address line 1 empty. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates a new group-owned product, changes its price and saves it. | Initial price 250 THB; updated price 225 THB; stock 10; enable stock management | Published product retains the updated regular price of 225 THB after reopening. | | |
| 2 | Customer logs in, searches for the product and opens its details. | Existing test account; unique product name | Correct account is active and the product displays the new price 225 THB. | | |
| 3 | Customer adds one unit and opens checkout. | Quantity 1 | Cart/checkout shows one unit at 225 THB and retains the authenticated session. | | |
| 4 | Customer fills other required fields but leaves Address line 1 blank and attempts to order. | Empty Address line 1; other fictional details complete; COD | Required-field validation is visible; no successful order confirmation appears and the form can be corrected. | | |
| 5 | Customer corrects the address and places one COD order. | Shared fictional address/phone; test account email | Confirmation shows an order number and merchandise price 225 THB, not 250 THB; grand total matches displayed shipping/tax. | | |
| 6 | Customer opens My account → Orders and views the order. | Order number from step 5 | The customer's order appears with the correct product, quantity and totals. | | |
| 7 | Staff opens the same order and verifies the customer and purchase details. | Order number and test account email | Order is associated with the logged-in test customer and agrees with the customer confirmation. | | |
| 8 | Staff changes the order to Completed and saves it. | Status Completed | Completed is saved successfully. | | |
| 9 | Customer refreshes order history and reopens the order. | Same customer account and order number | Order status is Completed; product details and totals remain unchanged. | | |

## Related documents

- [Requirement traceability matrix and API appendix](api-traceability-matrix.md)
- [API inventory](api-inventory.md): a reference list, not a requirement to test every endpoint.

These are UI system tests. Related API behavior does not prove that a particular endpoint was called. Performance/load tests must not place orders or bookings.
