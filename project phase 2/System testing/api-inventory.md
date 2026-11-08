# WooCommerce API Inventory — ITCS386 Group 5

API operations documented in WooCommerce_API_Guide.md, used as the basis for system testing and the API traceability matrix.

**Status:** Documented / Not verified against the live server. This inventory has not been validated through live API calls and is not an exhaustive list of every endpoint WooCommerce may support.

## Environment

| Item | Value |
|---|---|
| Shop | http://157.85.102.236/shop/ |
| Admin panel | http://157.85.102.236/shop/wp-admin/ |
| Store API base URL | http://157.85.102.236/shop/wp-json/wc/store/v1 |
| Admin REST API base URL | http://157.85.102.236/shop/wp-json/wc/v3 |
| Group username | `itcs386-g05` |
| Test data prefix | `G05` followed by a unique RUN_ID |

Several guide examples use the ITDS362 server (`157.85.104.96`). Replace it with the ITCS386 server above.

## 1. Store API — 11 operations

Base URL: `http://157.85.102.236/shop/wp-json/wc/store/v1`

No username or password is required. Do not send group credentials to this API.

| API ID | Method | Endpoint | Purpose | Cart-Token |
|---|---|---|---|---|
| S01 | GET | `/products` | List, search, filter and sort products | Not required |
| S02 | GET | `/products/{id}` | Retrieve product details | Not required |
| S03 | GET | `/products/categories` | List product categories | Not required |
| S04 | GET | `/cart` | Start a new cart or retrieve the current cart | Omit for a new token; send for an existing cart |
| S05 | POST | `/cart/add-item` | Add a product to the cart | Required |
| S06 | POST | `/cart/update-item` | Change an item's quantity | Required |
| S07 | POST | `/cart/remove-item` | Remove an item from the cart | Required |
| S08 | POST | `/cart/apply-coupon` | Apply a coupon | Required |
| S09 | POST | `/cart/remove-coupon` | Remove a coupon | Required |
| S10 | GET | `/checkout` | Retrieve the current cart's draft order | Required |
| S11 | POST | `/checkout` | Place an order | Required |

### Cart and checkout

- Start with `GET /cart` and read `Cart-Token` from the **response header**.
- Send the same token in request headers for operations on that cart.
- Each virtual user must have its own token.
- POST requests use `Content-Type: application/json`.
- If a request returns `401 woocommerce_rest_missing_nonce`, also send the `Nonce` from the `GET /cart` response and update it from subsequent responses, as described in the guide.
- `add-item` uses the product `id` and `quantity`.
- `update-item` uses the cart item `key` and `quantity`; `remove-item` uses the `key`, not the product ID.
- Coupon operations use `code`.
- Checkout uses fictional billing/shipping details and `payment_method: "cod"`. Thai addresses require a province code, such as `state: "TH-10"`.

### Product query parameters

| Parameter | Purpose / Example |
|---|---|
| `page`, `per_page` | Pagination; maximum `per_page` is 100 |
| `search` | Text search, such as `search=hoodie` |
| `category` | Filter by an ID from the category list |
| `type` | Use `type=simple` for products that do not require a variation selection |
| `orderby`, `order` | Sort by date, price, popularity, rating or title; asc/desc direction |
| `min_price`, `max_price` | Price range in minor currency units; 1000 = 10.00 THB |
| `on_sale` | For example, `on_sale=true` |

Store API prices are strings in minor currency units: `"1800"` with `currency_minor_unit: 2` means 18.00 THB.

## 2. Admin REST API — 13 operations

Base URL: `http://157.85.102.236/shop/wp-json/wc/v3`

Every request requires **HTTP Basic Auth** using `itcs386-g05` and the **Shop API password** from the accounts sheet. The browser login password does not work here. No Cart-Token is used.

Do not store real passwords or Authorization headers in the repository.

| API ID | Method | Endpoint | Purpose |
|---|---|---|---|
| A01 | GET | `/products` | List and search products |
| A02 | POST | `/products` | Create a product |
| A03 | GET | `/products/{id}` | Retrieve product details |
| A04 | PUT | `/products/{id}` | Update a product, including price or stock |
| A05 | DELETE | `/products/{id}?force=true` | Permanently delete a product |
| A06 | GET | `/products/categories` | List product categories |
| A07 | POST | `/products/categories` | Create a product category |
| A08 | GET | `/orders` | List and filter orders |
| A09 | GET | `/orders/{id}` | Retrieve order details |
| A10 | PUT | `/orders/{id}` | Update an order, including its status |
| A11 | GET | `/coupons` | List coupons |
| A12 | POST | `/coupons` | Create a coupon |
| A13 | GET | `/customers` | List registered customers |

### Relevant fields and filters

- Product list: `page`, `per_page`, `search`, `status`, `category`.
- Order list: `status`, `after`, `before`, `per_page`.
- Product creation/update: `name`, `type`, `regular_price`, `sale_price`, `manage_stock`, `stock_quantity`, `categories`.
- Admin API prices are decimal strings: `"199"` = 199 THB, unlike Store API minor units.
- Order statuses: `pending`, `processing`, `on-hold`, `completed`, `cancelled`, `refunded`, `failed`.
- Coupon creation: `code`, `discount_type`, `amount`.
- Coupon types: `percent`, `fixed_cart`, `fixed_product`.

## 3. Status codes documented in the guide

| Status | Meaning |
|---|---|
| 200 / 201 | Success |
| 400 | Invalid input, such as a missing field, unknown product or insufficient stock |
| 401 / 403 | Invalid/missing token, nonce or credentials, or insufficient permissions |
| 404 | Incorrect endpoint or ID |
| 409 | Store API: the cart changed during checkout; retrieve the cart before retrying |
| 500 / 502 / 503 / 504 | Server error or overload |

These are general descriptions from the guide. Define the expected status separately for each test case.

## 4. Scope and testing notes

- **24 operations** counted by Method + Endpoint: 11 Store and 13 Admin operations.
- IDs `S01–S11` and `A01–A13` are group-defined references for the traceability matrix.
- The guide describes registration, login and customer order history as **Web UI** features without providing endpoints for these flows.
- A UI test of related behavior does not prove that the corresponding endpoint was called. Verify requests through network evidence or direct API tests.
- Prefix test record names and codes with `G05` and use fictional personal details.
- Modify/delete only records created by the group. Do not modify demo data or other groups' records.
- **Do not create orders or bookings in performance/load tests**, as required by Project 2. Use browsing, search and cart flows instead.
- Preparing this document did not call APIs or create server-side test data.

## Sources

- [WooCommerce_API_Guide.md — MyCourses](https://mycourses.ict.mahidol.ac.th/pluginfile.php/37519/mod_resource/content/0/WooCommerce_API_Guide.md), sections 1–6 (downloaded 9 November 2026).
- Project 2: `2026 Project 2 - Descriptions_v5-3.pdf`, test data and performance testing restrictions.
