# WooCommerce API Inventory — ITCS386 Group 5

รายการ API ตาม WooCommerce_API_Guide.md สำหรับใช้เป็นฐานในการจัดทำ System Test และ API Traceability Matrix

**สถานะ:** Documented / Not verified against the live server. รายการนี้รวบรวมจากคู่มือ ยังไม่ได้ยืนยันด้วยการเรียก API จริง และไม่ใช่รายการทุก endpoint ที่ WooCommerce อาจรองรับ

## Environment

| รายการ | ค่า |
|---|---|
| Shop | http://157.85.102.236/shop/ |
| Admin panel | http://157.85.102.236/shop/wp-admin/ |
| Store API base URL | http://157.85.102.236/shop/wp-json/wc/store/v1 |
| Admin REST API base URL | http://157.85.102.236/shop/wp-json/wc/v3 |
| Group username | `itcs386-g05` |
| Test data prefix | `G05` พร้อม RUN_ID ที่ไม่ซ้ำ |

ตัวอย่างหลายจุดในคู่มือใช้เซิร์ฟเวอร์ ITDS362 (`157.85.104.96`) ต้องเปลี่ยนเป็นเซิร์ฟเวอร์ ITCS386 ข้างต้น

## 1. Store API — 11 operations

Base URL: `http://157.85.102.236/shop/wp-json/wc/store/v1`

ไม่ใช้ username/password และไม่ส่งข้อมูลบัญชีกลุ่มไปยัง API ชุดนี้

| API ID | Method | Endpoint | Purpose | Cart-Token |
|---|---|---|---|---|
| S01 | GET | `/products` | ดูรายการ ค้นหา กรอง และเรียงสินค้า | ไม่ต้อง |
| S02 | GET | `/products/{id}` | ดูรายละเอียดสินค้า | ไม่ต้อง |
| S03 | GET | `/products/categories` | ดูรายการหมวดหมู่สินค้า | ไม่ต้อง |
| S04 | GET | `/cart` | เริ่มตะกร้าใหม่หรือดูตะกร้าปัจจุบัน | ไม่ส่งเพื่อรับ token ใหม่; ส่งเพื่อดูตะกร้าเดิม |
| S05 | POST | `/cart/add-item` | เพิ่มสินค้าลงตะกร้า | ต้องใช้ |
| S06 | POST | `/cart/update-item` | เปลี่ยนจำนวนสินค้าในตะกร้า | ต้องใช้ |
| S07 | POST | `/cart/remove-item` | ลบสินค้าออกจากตะกร้า | ต้องใช้ |
| S08 | POST | `/cart/apply-coupon` | ใช้คูปองกับตะกร้า | ต้องใช้ |
| S09 | POST | `/cart/remove-coupon` | นำคูปองออกจากตะกร้า | ต้องใช้ |
| S10 | GET | `/checkout` | ดู draft order ของตะกร้าปัจจุบัน | ต้องใช้ |
| S11 | POST | `/checkout` | สั่งซื้อสินค้า | ต้องใช้ |

### Cart and checkout

- เริ่มด้วย `GET /cart` แล้วอ่าน `Cart-Token` จาก **response header**
- ส่ง token เดิมใน request header ของการทำงานกับตะกร้าเดียวกัน
- แต่ละ virtual user ต้องมี token ของตนเอง
- POST requests ใช้ `Content-Type: application/json`
- หากพบ `401 woocommerce_rest_missing_nonce` ให้ส่ง `Nonce` จาก response ของ `GET /cart` และอัปเดตจากแต่ละ response ตามคู่มือ
- `add-item` ใช้ product `id` และ `quantity`
- `update-item` ใช้ cart item `key` และ `quantity`; `remove-item` ใช้ `key` ไม่ใช่ product ID
- การใช้/นำคูปองออกระบุ `code`
- Checkout ใช้ข้อมูล billing/shipping สมมติและ `payment_method: "cod"`; ที่อยู่ประเทศไทยต้องมีจังหวัด เช่น `state: "TH-10"`

### Product query parameters

| Parameter | Purpose / Example |
|---|---|
| `page`, `per_page` | แบ่งหน้า; `per_page` สูงสุด 100 |
| `search` | ค้นหาชื่อ/ข้อความ เช่น `search=hoodie` |
| `category` | กรองด้วย category ID จากรายการหมวดหมู่ |
| `type` | เช่น `type=simple` เพื่อเลือกสินค้าที่เพิ่มลงตะกร้าได้โดยไม่ต้องเลือก variation |
| `orderby`, `order` | เรียงด้วย date, price, popularity, rating หรือ title; ทิศทาง asc/desc |
| `min_price`, `max_price` | ช่วงราคาเป็นหน่วยย่อย เช่น 1000 = 10.00 THB |
| `on_sale` | เช่น `on_sale=true` |

ราคา Store API เป็น string ในหน่วยย่อย เช่น `"1800"` เมื่อ `currency_minor_unit: 2` หมายถึง 18.00 บาท

## 2. Admin REST API — 13 operations

Base URL: `http://157.85.102.236/shop/wp-json/wc/v3`

ทุก request ใช้ **HTTP Basic Auth** ด้วย username `itcs386-g05` และ **Shop API password** จากไฟล์บัญชี ไม่ใช่ Password สำหรับ login ผ่านเว็บ และไม่ใช้ Cart-Token

ไม่เก็บ password หรือ Authorization header จริงไว้ใน repository

| API ID | Method | Endpoint | Purpose |
|---|---|---|---|
| A01 | GET | `/products` | ดูรายการและค้นหาสินค้า |
| A02 | POST | `/products` | สร้างสินค้า |
| A03 | GET | `/products/{id}` | ดูรายละเอียดสินค้า |
| A04 | PUT | `/products/{id}` | แก้สินค้า เช่น ราคาและ stock |
| A05 | DELETE | `/products/{id}?force=true` | ลบสินค้าถาวร |
| A06 | GET | `/products/categories` | ดูรายการหมวดหมู่สินค้า |
| A07 | POST | `/products/categories` | สร้างหมวดหมู่สินค้า |
| A08 | GET | `/orders` | ดูและกรองรายการคำสั่งซื้อ |
| A09 | GET | `/orders/{id}` | ดูรายละเอียดคำสั่งซื้อ |
| A10 | PUT | `/orders/{id}` | แก้คำสั่งซื้อ เช่น เปลี่ยนสถานะ |
| A11 | GET | `/coupons` | ดูรายการคูปอง |
| A12 | POST | `/coupons` | สร้างคูปอง |
| A13 | GET | `/customers` | ดูลูกค้าที่ลงทะเบียน |

### Relevant fields and filters

- Product list: `page`, `per_page`, `search`, `status`, `category`
- Order list: `status`, `after`, `before`, `per_page`
- Product creation/update: เช่น `name`, `type`, `regular_price`, `sale_price`, `manage_stock`, `stock_quantity`, `categories`
- Admin API ใช้ราคาเป็น decimal string เช่น `"199"` = 199 บาท ต่างจากหน่วยราคาของ Store API
- Order statuses: `pending`, `processing`, `on-hold`, `completed`, `cancelled`, `refunded`, `failed`
- Coupon creation: `code`, `discount_type`, `amount`
- Coupon types: `percent`, `fixed_cart`, `fixed_product`

## 3. Status codes documented in the guide

| Status | Meaning |
|---|---|
| 200 / 201 | สำเร็จ |
| 400 | ข้อมูลไม่ถูกต้อง เช่น ขาด field, สินค้าไม่รู้จัก หรือ stock ไม่พอ |
| 401 / 403 | Token/Nonce หรือ credentials ไม่ถูกต้อง หรือสิทธิ์ไม่พอ |
| 404 | Endpoint หรือ ID ไม่ถูกต้อง |
| 409 | Store API: cart เปลี่ยนระหว่างสั่งซื้อ ให้ดึง cart ใหม่ก่อน retry |
| 500 / 502 / 503 / 504 | Server error หรือ overload |

ตารางนี้เป็นแนวทางทั่วไปจากคู่มือ ไม่ใช่ expected status ที่ใช้แทนข้อกำหนดราย test case ได้ทุกกรณี

## 4. Scope and testing notes

- รวม **24 operations** โดยนับตามคู่ Method + Endpoint: Store 11 และ Admin 13
- IDs `S01–S11` และ `A01–A13` ตั้งขึ้นสำหรับเอกสารกลุ่ม เพื่ออ้างอิงต่อใน traceability matrix
- การสมัครบัญชี, login และดู order ของลูกค้า คู่มือระบุเป็น **Web UI** โดยไม่ได้ให้ endpoints สำหรับ flow เหล่านี้
- System Test ผ่าน UI ที่ครอบคลุมพฤติกรรมเดียวกัน ไม่ใช่หลักฐานว่าเรียก endpoint นี้จริง ต้องตรวจ Network หรือทดสอบ API โดยตรง
- ใช้ชื่อและรหัสข้อมูลทดสอบขึ้นต้น `G05` และใช้ข้อมูลบุคคลสมมติ
- แก้/ลบเฉพาะข้อมูลที่กลุ่มสร้างเอง ไม่แก้ demo data หรือข้อมูลของกลุ่มอื่น
- **Performance/load tests ห้ามสร้าง orders หรือ bookings** ตาม Project 2; ใช้ browsing/search/cart flows แทน
- ไม่มีการเรียก API หรือสร้างข้อมูลบนเซิร์ฟเวอร์จากการจัดทำเอกสารฉบับนี้

## Sources

- [WooCommerce_API_Guide.md — MyCourses](https://mycourses.ict.mahidol.ac.th/pluginfile.php/37519/mod_resource/content/0/WooCommerce_API_Guide.md), sections 1–6 (downloaded 9 November 2026).
- Project 2: `2026 Project 2 - Descriptions_v5-3.pdf`, restrictions for test data and performance testing.
