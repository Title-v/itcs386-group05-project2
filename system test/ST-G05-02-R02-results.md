# ST-G05-02 — R02 Execution Report

| Item | Recorded value |
|---|---|
| Date and time | 19 November 2026, 03:08–03:12 Asia/Bangkok |
| Product | `G05 Cap R02`, ID 1253 |
| Order | 1260, 300 THB, Cash on delivery |
| Recorded order status | Processing |
| Result | **9/9 Pass** |
| Screenshots | 21 page-only captures |

## Execution and capture method

- Staff account: `itcs386-g05`; use the browser password from D15 of the Group 5 accounts sheet. No password is stored in this repository.
- Staff and guest roles were separated by logging out before each customer flow and signing back in for staff verification. These were sequential sessions in the in-app browser, not simultaneous isolated browser profiles.
- Use new G05 names/codes for each rerun. The IDs and orders below are recorded outputs, not IDs to reuse for creation.
- Customer product discovery used the Shop list and Next Page links. Storefront Search and direct product URLs were not used to locate the test items.
- **Screenshots capture web-page content only:** no browser tabs, address bar, desktop or mouse pointer. They are direct browser captures, not retouched evidence. Text insertion carets/focus outlines may appear where a field was active.
- New-product evidence includes the blank Add new product form, completed inputs before Publish, and Product published after creation. WordPress then changes the heading to Edit product; the blank and pre-Publish captures establish creation.
- Inputs use the field labels actually displayed. Optional fields are left blank/unchecked as stated. No customer account is required.
- Dates/times in this document use **Asia/Bangkok, 19 November 2026**. The shop screens display the server's date (18 November during these runs); this timezone difference is not a different run.
- Expected results were retained from the approved scenarios. Outcomes below are from the new execution, not copied from prior screenshots.
- Email-notification failures (mail function could not be instantiated) appeared in staff order notes. Mail delivery is outside these cases; no notification success is claimed.
- These are manual system tests through Computer Use. They do not replace the separate automated UI deliverable or establish direct REST endpoint coverage.

## Step results

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | Create a new cap through Add new product; capture blank and completed forms, Publish, then verify saved Inventory values. | Product name = G05 Cap R02; Simple product; Regular price (฿) = 150; Sale price blank; Stock management checked; Quantity = 3; Allow backorders? = Do not allow; Sold individually unchecked. | Product is published at 150 THB with stock 3 and no backorders. | Product 1253 was newly published at 150 THB with stock 3, backorders disabled and Sold individually unchecked. Before/after creation evidence captured. | Pass |
| 2 | Log out as staff, open Shop as guest, locate the cap in the list, open it and add one unit. | Target G05 Cap R02; Next Page as needed; Product quantity = 1; Add to cart; View cart. | Correct product appears at 150 THB; cart contains one unit with merchandise subtotal 150 THB. | Found the cap on Shop page 13, verified 150 THB / 3 in stock, and added one. Cart quantity was 1 and total 150 THB. | Pass |
| 3 | Attempt to change the cart quantity to four and leave the field. | Quantity of G05 Cap R02 in your cart. = attempted 4; press Tab; stock before attempt = 3. | The excessive quantity is prevented or rejected with visible feedback; cart does not retain more than stock 3. | The UI capped the value at 3, disabled Increase quantity, and displayed total 450 THB. No error banner appeared; limiting the value was the visible feedback. | Pass |
| 4 | Change the cart quantity to two. | Quantity of G05 Cap R02 in your cart. = 2; Tab. No Update cart button was used. | Cart updates to two units and merchandise subtotal 300 THB. | Quantity became 2 and total 300 THB. | Pass |
| 5 | Remove the product from the cart. | Trash control labelled Remove G05 Cap R02 from cart. | Cart becomes empty with no remaining merchandise charge for the product. | The cart displayed Your cart is currently empty!; no test-product charge remained. | Pass |
| 6 | Return to the product with browser Back and add two units again. | Product quantity = 2; Add to cart; View cart. | Cart contains exactly two units with merchandise subtotal 300 THB and no duplicate line. | Exactly one cart line with quantity 2 and total 300 THB; no duplicate item or coupon. | Pass |
| 7 | Fill the guest checkout form and place a COD order. | Complete checkout table below: g05.cap.r02@example.com; G05 Test; 1 Test Road; Bangkok / Bangkok; 10200; Thailand; 0800000000; COD; no note. | Confirmation shows an order number, two units and merchandise total 300 THB; grand total matches displayed shipping/tax. | Order 1260 confirmed for two caps at 150 THB each, total 300 THB, COD. No separate shipping/tax charge displayed. | Pass |
| 8 | Sign in as staff, find the order, then inspect the product Inventory. | Search orders: = 1260; open #1260 G05 Test; open G05 Cap R02 (#1253); Inventory > Quantity. | Order quantity is two and remaining stock is one. Earlier cart changes did not cause extra permanent stock deductions. | Order 1260 matched the purchase and remained Processing. Notes recorded 3→1; saved Quantity was 1. Cart edits had not permanently reduced additional stock. | Pass |
| 9 | Log out, verify an empty guest cart, reopen the cap through Shop and attempt a total of two units. | At 1 in stock the Product quantity field is absent. Click Add to cart once, then again. Open View cart after the second attempt. | The system prevents adding more than the one unit remaining. | First click added one. Second was rejected because stock was 1 and one was already in the cart. Cart retained quantity 1 and 150 THB; Increase quantity disabled. The unpurchased item was removed after evidence capture. | Pass |

### Checkout inputs used

| UI field / control | Value / action |
|---|---|
| Checkout mode | Guest, after staff logout |
| Email address | `g05.cap.r02@example.com` |
| First name | `G05` |
| Last name | `Test` |
| Country / Region | `Thailand` (verified selected) |
| Street address | `1 Test Road` |
| + Add apartment, suite, unit, etc. | Left closed; second address line blank |
| Town / City | `Bangkok` |
| State / County | `Bangkok` selected from the dropdown |
| Postcode / ZIP | `10200` |
| Phone (optional) | `0800000000` |
| Payment | Cash on delivery selected |
| Add a note to your order | Unchecked |
| Separate shipping form / same-as-billing checkbox | Not displayed; no such input was made |
| Shipping method / Company field | Not displayed |
| Submission | Place Order clicked once for the successful order |
| Recorded total | 300.00 THB; no separate shipping/tax charge shown |

The form fields were filled for this run. No real customer account or real personal details were used. The staff order showed shipping details matching billing; that is an observed saved value, not evidence of a shipping checkbox.

### Run observations and cleanup

Attempted cart quantity 4 was capped at 3 with no error banner. At remaining stock 1 the product page hid quantity input; two Add to cart clicks tested the total-of-two attempt. The second click was rejected. The unpurchased unit was removed after capture and the cart was confirmed empty. Order 1260 remains Processing as recorded; completing it is not a Test 2 step.

## Screenshots by step

### Step 1 — Pass

**Add new product — blank form before entering data**

![ST-G05-02 step 1: Add new product — blank form before entering data](screenshots/ST-G05-02/R02/S01a-blank.jpg)

**Add new product — inventory entered, before Publish**

![ST-G05-02 step 1: Add new product — inventory entered, before Publish](screenshots/ST-G05-02/R02/S01b-before-publish-stock.jpg)

**Add new product — price entered, before Publish**

![ST-G05-02 step 1: Add new product — price entered, before Publish](screenshots/ST-G05-02/R02/S01c-before-publish-price.jpg)

**Product published — confirmation after creating the new product**

![ST-G05-02 step 1: Product published — confirmation after creating the new product](screenshots/ST-G05-02/R02/S01d-published.jpg)

**Saved stock settings after creation**

![ST-G05-02 step 1: Saved stock settings after creation](screenshots/ST-G05-02/R02/S01e-saved-stock.jpg)

### Step 2 — Pass

**Guest Shop list with an empty cart**

![ST-G05-02 step 2: Guest Shop list with an empty cart](screenshots/ST-G05-02/R02/S02a-shop-start.jpg)

**Cap located in the Shop list**

![ST-G05-02 step 2: Cap located in the Shop list](screenshots/ST-G05-02/R02/S02b-found-in-list.jpg)

**Cap detail: 150 THB and 3 in stock**

![ST-G05-02 step 2: Cap detail: 150 THB and 3 in stock](screenshots/ST-G05-02/R02/S02c-product.jpg)

**One cap in cart, total 150 THB**

![ST-G05-02 step 2: One cap in cart, total 150 THB](screenshots/ST-G05-02/R02/S02d-cart-one.jpg)

### Step 3 — Pass

**Attempted 4 capped at 3; total 450 THB**

![ST-G05-02 step 3: Attempted 4 capped at 3; total 450 THB](screenshots/ST-G05-02/R02/S03-stock-limit.jpg)

### Step 4 — Pass

**Quantity changed to 2; total 300 THB**

![ST-G05-02 step 4: Quantity changed to 2; total 300 THB](screenshots/ST-G05-02/R02/S04-quantity-two.jpg)

### Step 5 — Pass

**Remove leaves the cart empty**

![ST-G05-02 step 5: Remove leaves the cart empty](screenshots/ST-G05-02/R02/S05-empty-cart.jpg)

### Step 6 — Pass

**Two caps re-added, one cart line**

![ST-G05-02 step 6: Two caps re-added, one cart line](screenshots/ST-G05-02/R02/S06-readded-cart.jpg)

### Step 7 — Pass

**Completed Test 2 checkout inputs**

![ST-G05-02 step 7: Completed Test 2 checkout inputs](screenshots/ST-G05-02/R02/S07a-inputs.jpg)

**Customer order confirmation**

![ST-G05-02 step 7: Customer order confirmation](screenshots/ST-G05-02/R02/S07b-confirmation.jpg)

### Step 8 — Pass

**Staff verification of the 300 THB order**

![ST-G05-02 step 8: Staff verification of the 300 THB order](screenshots/ST-G05-02/R02/S08a-staff-order.jpg)

**Saved inventory after purchase: 1**

![ST-G05-02 step 8: Saved inventory after purchase: 1](screenshots/ST-G05-02/R02/S08b-stock-one.jpg)

### Step 9 — Pass

**Empty post-purchase cart**

![ST-G05-02 step 9: Empty post-purchase cart](screenshots/ST-G05-02/R02/S09a-empty-cart.jpg)

**Product page at stock 1: no quantity field**

![ST-G05-02 step 9: Product page at stock 1: no quantity field](screenshots/ST-G05-02/R02/S09b-one-in-stock.jpg)

**Second Add to cart attempt rejected**

![ST-G05-02 step 9: Second Add to cart attempt rejected](screenshots/ST-G05-02/R02/S09c-second-unit-rejected.jpg)

**Cart retains one unit with Increase quantity disabled**

![ST-G05-02 step 9: Cart retains one unit with Increase quantity disabled](screenshots/ST-G05-02/R02/S09d-cart-limit.jpg)


## Related documents

- [Current system test cases](system-test-cases.md#st-g05-02)
- [Tested requirements](api-traceability-matrix.md)
