# System Test Cases — ITCS386 Group 5

**Revision 3.1 — focused scope with concrete test inputs. Status: Designed / Not Run.** These three manual scenarios use the Project 2 template and cover staff → customer → staff outcomes. Step numbers restart at 1 in each case and match the [traceability matrix](api-traceability-matrix.md). Actual result, Pass or fail and Tested by and date remain blank until execution.

## Shared execution setup

- Storefront: http://157.85.102.236/shop/
- Staff interface: http://157.85.102.236/shop/wp-admin/
- Staff account: `itcs386-g05`, verified against Group 5 in `ITCS386_Group_Accounts.xlsx`, sheet `ITCS386`, row 15. Use the browser login password in cell D15; never commit its value.
- Use separate staff/customer sessions. The concrete dataset below uses `RUN_ID = 20261117-01`. Before a repeat run, replace this suffix consistently in every product name, coupon and case email with a fresh value such as `20261117-02`. These are planned inputs, not records confirmed to exist. Prefix names/codes with G05.
- Use only group-owned records; do not change demo data or other groups' records.
- Fictional checkout details: G05 Test, 1 Test Road, Bangkok, Bangkok province, 10200, Thailand, phone 0800000000. Use the case email; use the same fictional shipping address.
- Verify merchandise arithmetic separately from shipping/tax. Record the site's price/tax display basis and shipping charges before execution, then check the grand total against that breakdown. The 10% coupon calculation assumes the stated merchandise price is the discount basis.
- Save screenshots for every step under `screenshots/<case-ID>/<RUN_ID>/`; reference their paths and observed values in Actual result.
- Enter Pass or Fail only after running a step. Use Blocked if prerequisites prevent execution. Failed steps need a defect report with reproduction steps, expected/actual results and evidence.
- ST-G05-03 uses the designated fictional customer `g05.st03.20261117-01@example.com`. Confirm this account exists and can log in before execution, or prepare it through the supported setup flow. Its password must be obtained from the tester's private credential store, not this document. No working account or password is claimed to have been created. If email verification blocks setup, record Blocked and obtain an instructor-approved test account; record any substituted test email consistently. Registration remains outside the tested scope.
- No live tests or server-side changes were performed while preparing this revision.

## Group 5 account values

Verified source: `ITCS386_Group_Accounts.xlsx`, sheet `ITCS386`, row 15.

| Purpose | Group 5 value / source | Use in these tests |
|---|---|---|
| Shop staff username | `itcs386-g05` — B15 | Staff signs in to `http://157.85.102.236/shop/wp-admin/` before each case |
| Shop browser login password | Private value in D15, column Password (shop + hotel) | Enter locally for staff browser login; do not copy it into GitHub or evidence |
| Shop API password | Private value in F15, column Shop API password | Only for separate Admin REST API tests; not used for these manual browser logins |
| Hotel email | `itcs386-g05@itcs386.com` — C15 | Hotel login only; this is not a WooCommerce customer account supplied by the sheet |
| Hotel API key | Private value in E15 | Not used in the selected WooCommerce scenarios |

The sheet supplies the Group 5 **staff** account, not a separate shopper account. All staff actions below use that Group 5 account. The `G05` product/coupon prefixes and `g05.st01...`, `g05.st02...`, `g05.st03...` emails are fictional **Group 5 test data**, not credentials taken from the sheet. Keep the separate customer session so the tests exercise the shopper role.

For ST-G05-03, prepare or use a group-owned fictional customer account before execution; do not substitute the hotel email or Shop manager account for that customer. No working customer password is supplied by this document.

## Runtime values and expected amounts

- `ORDER_ST01`, `ORDER_ST02` and `ORDER_ST03` are the real order numbers to record after each successful checkout. Do not enter invented order numbers. Product IDs are also assigned by the server; select records by the exact names above.
- Passwords are the only intentionally private inputs. All other manually entered values are specified in the step tables.
- ST-G05-01: 200.00 × 2 = 400.00 THB; 10% discount = 40.00 THB; merchandise after discount = 360.00 THB.
- ST-G05-02: 150.00 × 1 = 150.00 THB; 150.00 × 2 = 300.00 THB; stock after purchase = 3 − 2 = 1.
- ST-G05-03: 225.00 × 1 = 225.00 THB; the old 250.00 THB price must not be charged.
- Grand totals use the actual displayed shipping and tax configuration. Do not assume these charges are zero or double-count tax already included in prices.
- Before execution, confirm that `G05INVALID20261117-01` does not exist and that the run's product/coupon names are unused.

## Selected scope

The scenarios retain unusual inputs and actions: an invalid coupon and returning from checkout, an above-stock quantity and removing/re-adding an item, and a missing required address field followed by correction.

Category creation/browsing, permanent deletion, coupon removal, customer-list checks, catalog pagination/sorting/price filters and registration testing are outside this revision. No extra fixtures are required to exercise every API.

## ST-G05-01

| Field | Details |
|---|---|
| Test case ID | ST-G05-01 |
| Title | Purchase with a coupon and complete the order |
| Objective | Verify product/coupon setup, invalid coupon rejection, discounted purchase and staff order completion. |
| Preconditions | Staff is logged in as `itcs386-g05` using the private browser password from D15. Customer uses a separate session with an empty cart. COD is available. |
| Test data | Product: `G05 Mug 20261117-01`, simple, 200 THB, stock 20, backorders disabled. Coupon: `G05SAVE1020261117-01`, 10% discount restricted to this product. Invalid code: `G05INVALID20261117-01`. Quantity 2. Email: `g05.st01.20261117-01@example.com`. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product and verifies its saved settings. | Name = G05 Mug 20261117-01; type = Simple product; regular price = 200.00 THB; sale price = empty; manage stock = enabled; stock = 20; backorders = Do not allow; status = Published | Product is published with the specified price and stock. | | |
| 2 | Staff creates the product-restricted coupon. | Code = G05SAVE1020261117-01; discount type = Percentage discount; amount = 10; product restriction = G05 Mug 20261117-01; expiry = unset; minimum spend = 0; maximum spend = unset; usage limits = unset | Coupon is saved with the correct product restriction and discount. | | |
| 3 | Customer searches for and opens the product. | Search = G05 Mug 20261117-01 | Correct product appears at 200 THB and is available to buy. | | |
| 4 | Customer adds two units and opens the cart. | Product = G05 Mug 20261117-01; quantity = 2 | Cart contains two units with merchandise subtotal 400 THB. | | |
| 5 | Customer tries the nonexistent coupon, then applies the valid coupon. | First code = G05INVALID20261117-01; second code = G05SAVE1020261117-01 | Invalid code produces a visible error without changing the total. Valid code applies one 40 THB discount; discounted merchandise total is 360 THB. | | |
| 6 | Customer opens checkout and returns to the cart before ordering. | Open Checkout, then click Back to cart (or browser Back) once; do not click Place order | Product, quantity and coupon remain correct; no successful order confirmation appears. | | |
| 7 | Customer reopens checkout, enters fictional details and places one COD order. | First name = G05; last name = Test; address line 1 = 1 Test Road; address line 2 = empty; city = Bangkok; province = Bangkok; postcode = 10200; country = Thailand; phone = 0800000000; email = g05.st01.20261117-01@example.com; shipping address = same as billing; payment = Cash on delivery (cod) | Confirmation shows an order number, two units, the 40 THB discount and the correct grand total. | | |
| 8 | Staff locates and opens the order. | Search using ORDER_ST01 captured from the confirmation in step 7; expected product = G05 Mug 20261117-01; customer email = g05.st01.20261117-01@example.com | Order details, coupon and total agree with the customer confirmation. | | |
| 9 | Staff changes the order to Completed, saves and reopens it. | Order = ORDER_ST01; new status = Completed | Completed persists; order contents and totals are unchanged. | | |

## ST-G05-02

| Field | Details |
|---|---|
| Test case ID | ST-G05-02 |
| Title | Validate quantity limits and remaining stock |
| Objective | Verify stock-limit validation, cart quantity changes/removal and stock reduction after a successful purchase. |
| Preconditions | Staff is logged in as `itcs386-g05` using the private browser password from D15. Customer uses a separate session with an empty cart. COD is available. |
| Test data | Product: `G05 Stock Item 20261117-01`, simple, 150 THB, stock 3. Enable stock management; disable backorders and Sold individually. Quantities 1, 4 and 2. Email: `g05.st02.20261117-01@example.com`. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates and publishes the product, then verifies the saved stock settings. | Name = G05 Stock Item 20261117-01; type = Simple product; regular price = 150.00 THB; sale price = empty; manage stock = enabled; stock = 3; backorders = Do not allow; Sold individually = disabled; status = Published | Product is published at 150 THB with stock 3 and no backorders. | | |
| 2 | Customer searches for the product, opens it and adds one unit to the cart. | Search = G05 Stock Item 20261117-01; quantity = 1 | Correct product appears at 150 THB; cart contains one unit with merchandise subtotal 150 THB. | | |
| 3 | Customer attempts to change the cart quantity to four. | Product = G05 Stock Item 20261117-01; attempted quantity = 4; available stock = 3 | The excessive quantity is prevented or rejected with visible feedback; cart does not retain more than stock 3. | | |
| 4 | Customer changes the cart quantity to two. | Product = G05 Stock Item 20261117-01; quantity = 2 | Cart updates to two units and merchandise subtotal 300 THB. | | |
| 5 | Customer removes the product from the cart. | Click Remove for G05 Stock Item 20261117-01 | Cart becomes empty with no remaining merchandise charge for the product. | | |
| 6 | Customer returns to the product and adds two units again. | Product = G05 Stock Item 20261117-01; quantity = 2 | Cart contains exactly two units with merchandise subtotal 300 THB and no duplicate line. | | |
| 7 | Customer completes checkout with fictional details and COD. | First name = G05; last name = Test; address line 1 = 1 Test Road; address line 2 = empty; city = Bangkok; province = Bangkok; postcode = 10200; country = Thailand; phone = 0800000000; email = g05.st02.20261117-01@example.com; shipping address = same as billing; payment = Cash on delivery (cod) | Confirmation shows an order number, two units and merchandise total 300 THB; grand total matches displayed shipping/tax. | | |
| 8 | Staff opens the order and the product's stock settings. | Order = ORDER_ST02 captured in step 7; product = G05 Stock Item 20261117-01; expected purchased quantity = 2; expected remaining stock = 1 | Order quantity is two and remaining stock is one. Earlier cart changes did not cause extra permanent stock deductions. | | |
| 9 | Customer opens the product in a fresh cart and tries to add two units. | Fresh empty cart; product = G05 Stock Item 20261117-01; attempted quantity = 2; remaining stock = 1 | The system prevents adding more than the one unit remaining. | | |

## ST-G05-03

| Field | Details |
|---|---|
| Test case ID | ST-G05-03 |
| Title | Verify updated pricing and customer order history |
| Objective | Verify that a staff price update is used for a logged-in purchase and that the completed order appears correctly in customer history. |
| Preconditions | Staff is logged in as `itcs386-g05` using the private browser password from D15. A group-owned fictional customer account already exists and can log in. Account creation is setup, not a tested requirement. Customer cart is empty; COD is available. |
| Test data | Product: `G05 Account Item 20261117-01`, simple, initial price 250 THB, new price 225 THB, stock 10, backorders disabled. Quantity 1. Login email: `g05.st03.20261117-01@example.com`; obtain the actual password from the private test credential store. Invalid input: leave Address line 1 empty. |
| Tested by and date | |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Staff creates a new group-owned product, changes its price and saves it. | Name = G05 Account Item 20261117-01; type = Simple product; initial regular price = 250.00 THB; updated regular price = 225.00 THB; sale price = empty; manage stock = enabled; stock = 10; backorders = Do not allow; status = Published | Published product retains the updated regular price of 225 THB after reopening. | | |
| 2 | Customer logs in, searches for the product and opens its details. | Login email = g05.st03.20261117-01@example.com; password = actual password from private test credential store; search = G05 Account Item 20261117-01 | Correct account is active and the product displays the new price 225 THB. | | |
| 3 | Customer adds one unit and opens checkout. | Product = G05 Account Item 20261117-01; quantity = 1 | Cart/checkout shows one unit at 225 THB and retains the authenticated session. | | |
| 4 | Customer fills other required fields but leaves Address line 1 blank and attempts to order. | First name = G05; last name = Test; address line 1 = empty (clear any saved/autofilled value); address line 2 = empty; city = Bangkok; province = Bangkok; postcode = 10200; country = Thailand; phone = 0800000000; email = g05.st03.20261117-01@example.com; shipping address = same as billing; payment = Cash on delivery (cod) | Required-field validation is visible; no successful order confirmation appears and the form can be corrected. | | |
| 5 | Customer corrects the address and places one COD order. | First name = G05; last name = Test; address line 1 = 1 Test Road; address line 2 = empty; city = Bangkok; province = Bangkok; postcode = 10200; country = Thailand; phone = 0800000000; email = g05.st03.20261117-01@example.com; shipping address = same as billing; payment = Cash on delivery (cod) | Confirmation shows an order number and merchandise price 225 THB, not 250 THB; grand total matches displayed shipping/tax. | | |
| 6 | Customer opens My account → Orders and views the order. | Open My account > Orders; select ORDER_ST03 captured in step 5 | The customer's order appears with the correct product, quantity and totals. | | |
| 7 | Staff opens the same order and verifies the customer and purchase details. | Order = ORDER_ST03; customer email = g05.st03.20261117-01@example.com; product = G05 Account Item 20261117-01; quantity = 1 | Order is associated with the logged-in test customer and agrees with the customer confirmation. | | |
| 8 | Staff changes the order to Completed and saves it. | Order = ORDER_ST03; new status = Completed | Completed is saved successfully. | | |
| 9 | Customer refreshes order history and reopens the order. | Account = g05.st03.20261117-01@example.com; order = ORDER_ST03; refresh My account > Orders and reopen the order | Order status is Completed; product details and totals remain unchanged. | | |

## Related documents

- [Requirement traceability matrix and API appendix](api-traceability-matrix.md)
- [API inventory](api-inventory.md): a reference list, not a requirement to test every endpoint.

These are UI system tests. Related API behavior does not prove that a particular endpoint was called. Performance/load tests must not place orders or bookings.
