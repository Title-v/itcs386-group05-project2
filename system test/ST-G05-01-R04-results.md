# ST-G05-01 — R04 Execution Report

| Item | Recorded value |
|---|---|
| Date and time | 19 November 2026, 03:01–03:07 Asia/Bangkok |
| Product | `G05 Mug R04`, ID 1250 |
| Order | 1252, 360 THB, Cash on delivery |
| Recorded order status | Completed |
| Result | **9/9 Pass** |
| Screenshots | 20 page-only captures |

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
| 1 | Open Add new product, capture the blank form, fill the product fields, capture the form before Publish, then publish and verify saved price/stock. | Product name = G05 Mug R04; Product data = Simple product; Regular price (฿) = 200; Sale price (฿) blank; Stock management checked; Quantity = 20; Allow backorders? = Do not allow; Publish. | Product is published with the specified price and stock. | New product 1250 was created. Blank Add new product, completed form with Draft/Publish, Product published and saved stock 20 were captured. Price persisted at 200 THB. | Pass |
| 2 | Create and publish a new percentage coupon restricted to the newly created mug. | Coupon code = G05SAVE10-R04; Discount type = Percentage discount; Coupon amount = 10; Usage restriction > Products = G05 Mug R04 (#1250); Minimum spend = 0; maximum/expiry/usage-limit fields blank. | Coupon is saved with the correct product restriction and discount. | Coupon 1251 was published at 10% and its saved product restriction contained only G05 Mug R04 (#1250). | Pass |
| 3 | Log out of the staff account, open Shop as a guest, find the mug through the product list and click its name. | Start at http://157.85.102.236/shop/; exact name G05 Mug R04; follow Next Page as needed. No storefront search or direct product URL. | Correct product appears at 200 THB and is available to buy. | Guest cart was empty. Located G05 Mug R04 in the Shop list on page 15, opened it, and observed 200 THB / 20 in stock. | Pass |
| 4 | Set Product quantity to two, click Add to cart and open View cart. | Product quantity = 2 for G05 Mug R04; Add to cart; View cart. | Cart contains two units with merchandise subtotal 400 THB. | Cart contained one line, quantity 2, unit price 200 THB and subtotal 400 THB. | Pass |
| 5 | Try the nonexistent coupon, then apply the valid coupon. | Add coupons > Enter code = G05BAD-R04; Apply. Then Enter code = G05SAVE10-R04; Apply. | Invalid code produces a visible error without changing the total. Valid code applies one 40 THB discount; discounted merchandise total is 360 THB. | Invalid code was rejected as nonexistent with total unchanged at 400 THB. Valid coupon applied a 40 THB discount and total became 360 THB. | Pass |
| 6 | Open checkout, then return through Cart without placing an order. | Proceed to Checkout; click Cart; do not click Place Order. | Product, quantity and coupon remain correct; no successful order confirmation appears. | Quantity 2, applied coupon and 360 THB total remained after returning to the cart. | Pass |
| 7 | Reopen checkout, fill the guest form and place one COD order. | Use the complete checkout-input table below: g05.mug.r04@example.com; G05 Test; 1 Test Road; Bangkok / Bangkok; 10200; Thailand; 0800000000; Cash on delivery; note unchecked; Place Order once. | Confirmation shows an order number, two units, the 40 THB discount and the correct grand total. | Guest order 1252 confirmed: quantity 2, subtotal 400 THB, discount 40 THB, total 360 THB, Cash on delivery. No separate shipping/tax charge displayed. | Pass |
| 8 | Sign back in as staff, search Orders and compare the new order with the guest confirmation. | Search orders: = 1252; open #1252 G05 Test; verify product 1250, coupon 1251 and email g05.mug.r04@example.com. | Order details, coupon and total agree with the customer confirmation. | Staff order details matched the guest confirmation: two mugs, coupon discount 40 THB, total 360 THB. Notes recorded stock 20→18. | Pass |
| 9 | Change the order to Completed, save and reload. | Order 1252; Status = Completed; Update; reload. | Completed persists; order contents and totals are unchanged. | Completed persisted after reload; items and total remained 360 THB. | Pass |

### Checkout inputs used

| UI field / control | Value / action |
|---|---|
| Checkout mode | Guest, after staff logout |
| Email address | `g05.mug.r04@example.com` |
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
| Recorded total | 360.00 THB; no separate shipping/tax charge shown |

The form fields were filled for this run. No real customer account or real personal details were used. The staff order showed shipping details matching billing; that is an observed saved value, not evidence of a shipping checkbox.

### Run observations

During initial catalog navigation, one click opened an unrelated demo-product page. Returned to the catalog without adding or changing that product, then continued through Next Page with navigation checks. The tested mug was opened from its own list entry on page 15. No extra order was placed.

## Screenshots by step

### Step 1 — Pass

**Add new product — blank form before entering data**

![ST-G05-01 step 1: Add new product — blank form before entering data](screenshots/ST-G05-01/R04/S01a-blank.jpg)

**Add new product — inventory entered, before Publish**

![ST-G05-01 step 1: Add new product — inventory entered, before Publish](screenshots/ST-G05-01/R04/S01b-before-publish-stock.jpg)

**Add new product — price entered, before Publish**

![ST-G05-01 step 1: Add new product — price entered, before Publish](screenshots/ST-G05-01/R04/S01c-before-publish-price.jpg)

**Product published — confirmation after creating the new product**

![ST-G05-01 step 1: Product published — confirmation after creating the new product](screenshots/ST-G05-01/R04/S01d-published.jpg)

**Saved stock settings after creation**

![ST-G05-01 step 1: Saved stock settings after creation](screenshots/ST-G05-01/R04/S01e-saved-stock.jpg)

### Step 2 — Pass

**New coupon configured before Publish**

![ST-G05-01 step 2: New coupon configured before Publish](screenshots/ST-G05-01/R04/S02a-before-publish.jpg)

**Saved 10% discount**

![ST-G05-01 step 2: Saved 10% discount](screenshots/ST-G05-01/R04/S02b-discount.jpg)

**Saved restriction to the newly created mug**

![ST-G05-01 step 2: Saved restriction to the newly created mug](screenshots/ST-G05-01/R04/S02c-restriction.jpg)

### Step 3 — Pass

**Guest Shop list at the start of browsing**

![ST-G05-01 step 3: Guest Shop list at the start of browsing](screenshots/ST-G05-01/R04/S03a-shop-start.jpg)

**Matching mug located in the Shop list**

![ST-G05-01 step 3: Matching mug located in the Shop list](screenshots/ST-G05-01/R04/S03b-found-in-list.jpg)

**Mug details opened from its list entry**

![ST-G05-01 step 3: Mug details opened from its list entry](screenshots/ST-G05-01/R04/S03c-product.jpg)

### Step 4 — Pass

**Two mugs, subtotal 400 THB**

![ST-G05-01 step 4: Two mugs, subtotal 400 THB](screenshots/ST-G05-01/R04/S04-cart-two.jpg)

### Step 5 — Pass

**Invalid coupon rejected**

![ST-G05-01 step 5: Invalid coupon rejected](screenshots/ST-G05-01/R04/S05a-invalid-coupon.jpg)

**Valid coupon applied: 40 THB discount**

![ST-G05-01 step 5: Valid coupon applied: 40 THB discount](screenshots/ST-G05-01/R04/S05b-valid-coupon.jpg)

### Step 6 — Pass

**Checkout opened before returning to Cart**

![ST-G05-01 step 6: Checkout opened before returning to Cart](screenshots/ST-G05-01/R04/S06a-checkout-before-return.jpg)

**Returned cart retains quantity and discount**

![ST-G05-01 step 6: Returned cart retains quantity and discount](screenshots/ST-G05-01/R04/S06b-returned-cart.jpg)

### Step 7 — Pass

**Completed guest checkout inputs**

![ST-G05-01 step 7: Completed guest checkout inputs](screenshots/ST-G05-01/R04/S07a-checkout-inputs.jpg)

**Customer order confirmation**

![ST-G05-01 step 7: Customer order confirmation](screenshots/ST-G05-01/R04/S07b-confirmation.jpg)

### Step 8 — Pass

**Staff order details**

![ST-G05-01 step 8: Staff order details](screenshots/ST-G05-01/R04/S08-staff-order.jpg)

### Step 9 — Pass

**Completed status persisted after reload**

![ST-G05-01 step 9: Completed status persisted after reload](screenshots/ST-G05-01/R04/S09-completed.jpg)


## Related documents

- [Current system test cases](system-test-cases.md#st-g05-01)
- [Tested requirements](api-traceability-matrix.md)
