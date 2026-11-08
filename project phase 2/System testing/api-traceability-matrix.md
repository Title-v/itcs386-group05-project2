# API Traceability Matrix — ITCS386 Group 5

## Scope and status

เชื่อม API ทั้ง 24 operations จาก [API inventory](api-inventory.md) กับ System Test 3 เคสที่ออกแบบไว้

**Baseline:** แผน System Test เดิมก่อนเพิ่มขั้นตอนปิด gaps  
**Execution status:** Not Run ทุกเคส  
**Endpoint evidence:** ยังไม่มี Network capture หรือผล API test ยืนยันการเรียกจริง

ตารางนี้เป็น **behavioral mapping**: ขั้นตอนผ่าน UI ตรวจพฤติกรรมที่สัมพันธ์กับ API ไม่ได้ยืนยันว่า UI เรียก endpoint นั้น โดยเฉพาะ WordPress Admin อาจใช้ form submission หรือกลไกอื่น การตรวจ Network ยืนยันได้เฉพาะ endpoint ที่ปรากฏจริง; API ที่ UI ไม่ได้เรียกต้องมี direct API test แยก

ตัวเลขคือ step ของแต่ละเคสตาม baseline ในท้ายเอกสาร:
- **P (Planned):** มีขั้นตอนตรวจพฤติกรรมที่สัมพันธ์โดยชัดเจน แต่ยังไม่รัน
- **I (Indirect):** สัมพันธ์ทางอ้อม ยังไม่ตรวจ operation นั้นโดยตรง
- **C (Conditional):** ขั้นตอนขึ้นกับเงื่อนไข อาจไม่ได้ดำเนินการทุกครั้ง
- **— (Gap):** ยังไม่มีขั้นตอนชัดเจน

P ไม่ได้หมายถึง Pass และไม่ได้หมายถึง verified API coverage

## Test case index

| Short ID | Full ID | Scenario |
|---|---|---|
| ST-01 | ST-G05-01 | Staff สร้างสินค้าและคูปอง → Customer ซื้อพร้อมส่วนลด → Staff ตรวจ order/stock และปิด order |
| ST-02 | ST-G05-02 | Staff ตั้ง stock → Customer ลองจำนวนผิดปกติ แก้/ลบ cart และซื้อ → Staff ตรวจ order/stock → Customer ตรวจ stock ที่เหลือ |
| ST-03 | ST-G05-03 | Staff สร้างสินค้าและแก้ราคา → Customer สมัคร/login ซื้อ และดูประวัติ → Staff ตรวจ customer/order และปิด order → Customer ตรวจสถานะ |

## 1. Store API

Base URL: `http://157.85.102.236/shop/wp-json/wc/store/v1`

| API ID | Method / Endpoint | ST-01 steps | ST-02 steps | ST-03 steps | Mapping | Coverage / limitation |
|---|---|---|---|---|---|---|
| S01 | GET `/products` | 3 | 2 | 3 | P | ค้นหา/ดูรายการ; ยังขาด pagination, sorting, price filters และ query combinations |
| S02 | GET `/products/{id}` | 3 | 2, 12 | 3 | P | รายละเอียด ราคา และความพร้อมซื้อ; ยังขาด invalid ID และ variation coverage |
| S03 | GET `/products/categories` | — | — | 3 | I | เลือกดูตามหมวดหมู่ ไม่ได้ตรวจ category-list response |
| S04 | GET `/cart` | 4, 7 | 4–9 | 6, 8 | P | ตรวจรายการ จำนวน และยอด cart; ยังไม่ตรวจ token lifecycle โดยตรง |
| S05 | POST `/cart/add-item` | 4 | 3–4, 9, 12 | 6 | P | เพิ่มสินค้าปกติและลองเกิน stock; UI อาจป้องกัน input ก่อนส่ง request |
| S06 | POST `/cart/update-item` | — | 5–7 | — | P | เปลี่ยนจำนวน รวมศูนย์และเกิน stock; ต้องกำหนด oracle ของ quantity=0 หลังสำรวจ UI |
| S07 | POST `/cart/remove-item` | — | 8 | — | C | Remove ทำเฉพาะเมื่อสินค้ายังอยู่หลัง quantity=0 จึงอาจถูกข้าม |
| S08 | POST `/cart/apply-coupon` | 5–6 | — | — | P | คูปองไม่มีอยู่และคูปองลด 10%; ยังขาด expired/usage-limit/minimum-spend cases |
| S09 | POST `/cart/remove-coupon` | — | — | — | — | ยังไม่มีการนำคูปองออกและตรวจยอดคืน |
| S10 | GET `/checkout` | 7–8 | 10 | 6, 8 | I | เปิดหน้า checkout ไม่เท่ากับตรวจ draft-order API response |
| S11 | POST `/checkout` | 9 | 10 | 7, 9 | P | COD สำเร็จและช่องบังคับว่าง; validation อาจเกิดที่ UI ก่อนส่ง request |

## 2. Admin REST API

Base URL: `http://157.85.102.236/shop/wp-json/wc/v3`

| API ID | Method / Endpoint | ST-01 steps | ST-02 steps | ST-03 steps | Mapping | Coverage / limitation |
|---|---|---|---|---|---|---|
| A01 | GET `/products` | — | — | — | — | ยังไม่มีขั้นตอนตรวจรายการ/ค้นหาสินค้าฝั่ง staff อย่างชัดเจน |
| A02 | POST `/products` | 1 | 1 | 1 | P | Staff สร้าง simple product; ไม่ยืนยันว่า admin UI ใช้ REST endpoint นี้ |
| A03 | GET `/products/{id}` | 11 | 11 | 2 | P | Staff ตรวจข้อมูล stock/ราคาของสินค้ารายตัว |
| A04 | PUT `/products/{id}` | — | — | 2 | P | Staff แก้ราคา; stock ลดอัตโนมัติหลังซื้อไม่ใช่ coverage ของ PUT นี้ |
| A05 | DELETE `/products/{id}?force=true` | — | — | — | — | ยังไม่มีการลบสินค้าถาวร; ย้ายไป Trash อย่างเดียวไม่ตรงกับ force=true |
| A06 | GET `/products/categories` | — | — | 1 | I | เลือกหมวดหมู่เดิมขณะสร้างสินค้า ไม่ได้ตรวจ category-list response |
| A07 | POST `/products/categories` | — | — | — | — | ยังไม่มีการสร้างหมวดหมู่ |
| A08 | GET `/orders` | 10 | — | — | P | ค้นหา order ฝั่ง staff; ยังขาด status/date filters และ pagination |
| A09 | GET `/orders/{id}` | 10 | 11 | 11 | P | ตรวจ order รายตัวและความตรงกันกับฝั่งลูกค้า |
| A10 | PUT `/orders/{id}` | 12 | — | 12 | P | เปลี่ยนเป็น Completed; ยังขาดสถานะอื่นและ invalid transition cases |
| A11 | GET `/coupons` | — | — | — | — | ยังไม่มีขั้นตอนเปิดรายการ/ค้นหาคูปองโดยชัดเจน |
| A12 | POST `/coupons` | 2 | — | — | P | สร้างคูปอง percent 10%; ยังขาด fixed_cart/fixed_product |
| A13 | GET `/customers` | — | — | 11 | I | ตรวจข้อมูล customer ที่สัมพันธ์กับ order; ยังไม่ได้กำหนดการเปิดรายการ Customers โดยตรง |

## 3. Coverage summary

นับแต่ละ API ID เพียงครั้งเดียว แม้สัมพันธ์กับหลายเคส

| Mapping status | Store | Admin | Total |
|---|---|---|---|
| P — มีขั้นตอนสัมพันธ์ชัดเจน แต่ยังไม่รัน | 7 | 7 | 14 |
| I — ทางอ้อม | 2 | 2 | 4 |
| C — ขึ้นกับเงื่อนไข | 1 | 0 | 1 |
| Gap — ไม่มีขั้นตอนชัดเจน | 1 | 4 | 5 |
| **Total operations** | **11** | **13** | **24** |

- รวมการเชื่อมโยงแบบ P/I/C: **19/24 operations** เป็นเพียงความสัมพันธ์ตามแผน ไม่ใช่ผลทดสอบ
- Gaps: **S09, A01, A05, A07, A11**
- ทุกเคสยังเป็น **Not Run**; ยังไม่มีผล Pass/Fail หรือจำนวน API ที่ยืนยันว่าได้ทดสอบจริง
- การจับคู่ครบ 24 operations ในอนาคตไม่เท่ากับครอบคลุมทุก input, response, authorization rule หรือ error condition

## 4. Proposed gap-closing steps — not yet part of baseline

ข้อเสนอด้านล่างยังไม่ได้รันและยังไม่นำไปนับใน matrix ข้างต้น เมื่อยอมรับและเพิ่มลง test cases ให้ปรับเลขขั้นตอนและ matrix พร้อมกัน

| Proposal | Insert at | Action | Expected result | API IDs |
|---|---|---|---|---|
| GAP-01 | ST-01 หลัง step 2 | เปิด Coupons และค้นหารหัสที่สร้าง | พบคูปองและค่าประเภท/ส่วนลดถูกต้อง | A11 |
| GAP-02 | ST-01 หลัง step 6 | Remove coupon แล้ว apply ใหม่ | ยอดสินค้าหลังลบกลับเป็น 400 บาท; หลังใช้ใหม่เป็น 360 บาท โดยแยกค่าจัดส่ง/ภาษี | S09, S08 |
| GAP-03 | ST-03 ก่อน step 1 | สร้าง category ชื่อ G05 พร้อม RUN_ID และตรวจรายการ | พบ category ใหม่ตามข้อมูลที่สร้าง แล้วใช้กับสินค้าของเคส | A07, A06 |
| GAP-04 | ST-03 หลัง step 1 | เปิด Products ค้นหาชื่อเฉพาะ แล้วเปิดสินค้า | พบสินค้าถูกตัว รายละเอียดตรงกับที่สร้าง | A01, A03 |
| GAP-05 | ST-03 ช่วงท้าย | สร้างสินค้าทิ้งแยกจากสินค้าที่อยู่ใน order แล้วลบถาวร | ไม่พบสินค้าที่ลบในรายการ staff/customer; สินค้าของ order เดิมยังอยู่ | A02, A05, A01, S01 |
| REFINE-01 | ST-02 step 8 | หาก cart ว่างให้เพิ่มสินค้า 1 ชิ้นก่อน แล้วกด Remove เสมอ | ทดสอบ Remove จริงทุกรอบ และ cart ว่างหลังลบ | S07 |
| REFINE-02 | ST-03 step 11 | ระบุให้เปิด Customers แล้วค้นหาด้วยอีเมลทดสอบ | พบ customer ที่ถูกต้องและสัมพันธ์กับ order | A13 |

ข้อเสนอเหล่านี้ปิด behavioral gaps ได้ แต่ยังต้องมี direct API tests หรือ Network evidence เพื่ออ้าง endpoint coverage

## 5. Baseline step reference

อ้างอิงแผนที่ออกแบบในบทสนทนา ณ 9 November 2026 ตารางย่อนี้ทำให้เลขขั้นตอนใน matrix อ่านได้โดยไม่ต้องย้อนบทสนทนา **ไม่ใช่สิ่งทดแทน manual test case ฉบับเต็ม** ซึ่งต้องมี preconditions, test data, expected/actual result รายขั้นตอน, tester/date และ screenshots

ใช้ข้อมูลชื่อขึ้นต้น G05 และ RUN_ID ไม่ซ้ำ สินค้าทุกชิ้นเป็นข้อมูลที่กลุ่มสร้างเอง

### ST-G05-01 — Coupon purchase and order completion

Test data: simple product ราคา 200 บาท stock 20; คูปอง percent 10% จำกัดเฉพาะสินค้านี้; ซื้อ 2 ชิ้น

| Step | Planned action / checkpoint |
|---|---|
| 1 | Staff สร้างและ publish สินค้า เปิด manage stock ปิด backorders |
| 2 | Staff สร้างคูปอง 10% จำกัดเฉพาะสินค้า |
| 3 | Customer ค้นหาและเปิดสินค้า ตรวจราคา 200 บาทและพร้อมซื้อ |
| 4 | เพิ่ม 2 ชิ้น ตรวจยอดสินค้า 400 บาท |
| 5 | ใช้คูปองที่ไม่มีอยู่ ต้องถูกปฏิเสธและยอดไม่เปลี่ยน |
| 6 | ใช้คูปองที่สร้าง ตรวจส่วนลด 40 บาท ยอดสินค้าหลังลด 360 บาท |
| 7 | ไป checkout แล้วกลับ cart ตรวจสินค้า/จำนวน/คูปอง และยังไม่มี order ที่สั่งซื้อสำเร็จ |
| 8 | กลับ checkout กรอกข้อมูลสมมติครบ เลือก COD ตรวจยอดรวมตามค่าจัดส่งและภาษีที่แสดง |
| 9 | Place order ครั้งเดียว ตรวจ confirmation และ order number |
| 10 | Staff ค้นหา order และตรวจข้อมูลกับ confirmation |
| 11 | Staff ตรวจ stock เหลือ 18 |
| 12 | Staff เปลี่ยนเป็น Completed และเปิดตรวจสถานะอีกครั้ง |

### ST-G05-02 — Quantity, stock and cart changes

Test data: simple product ราคา 150 บาท stock 3; manage stock enabled; backorders และ sold individually disabled

| Step | Planned action / checkpoint |
|---|---|
| 1 | Staff สร้างและ publish สินค้าตามข้อมูลทดสอบ |
| 2 | Customer ค้นหาและเปิดสินค้า ตรวจราคา/พร้อมซื้อ |
| 3 | ลองเพิ่ม 4 ชิ้น ต้องไม่ยอมให้ cart มีเกิน stock 3 |
| 4 | เพิ่ม 1 ชิ้น ตรวจยอดสินค้า 150 บาท |
| 5 | เปลี่ยนเป็น 3 ชิ้น ตรวจยอดสินค้า 450 บาท |
| 6 | ลองเปลี่ยนเป็น 4 ชิ้น ต้องไม่บันทึกจำนวนเกิน stock |
| 7 | ลอง quantity=0; สำรวจว่าระบบลบรายการหรือ UI ป้องกันศูนย์ แล้วกำหนด expected behavior ให้แน่นอนก่อน automation |
| 8 | หากสินค้ายังอยู่ กด Remove และตรวจ cart ว่าง |
| 9 | กลับสินค้าแล้วเพิ่ม 2 ชิ้น ตรวจยอดสินค้า 300 บาทและไม่มีรายการซ้ำ |
| 10 | Checkout ด้วยข้อมูลสมมติและ COD ตรวจ confirmation |
| 11 | Staff ตรวจ order 2 ชิ้นและ stock เหลือ 1 |
| 12 | Customer เปิดสินค้าใหม่แล้วลองเพิ่ม 2 ชิ้น ต้องไม่ยอมให้เกิน stock ที่เหลือ |

### ST-G05-03 — Updated price, customer account and order history

Test data: simple product ราคาเริ่ม 250 บาท เปลี่ยนเป็น 225 บาท stock 10; category ที่มีอยู่; customer ใหม่ใช้อีเมลสมมติเฉพาะ RUN_ID

| Step | Planned action / checkpoint |
|---|---|
| 1 | Staff สร้างสินค้าและเลือก category ที่มีอยู่ |
| 2 | Staff เปลี่ยนราคา 250 → 225 บาท บันทึกและเปิดตรวจใหม่ |
| 3 | Customer เลือกหมวดหมู่ ค้นหา และเปิดสินค้า ตรวจราคาปัจจุบัน |
| 4 | Customer สมัครบัญชีใหม่ผ่าน My account |
| 5 | Logout/login และตรวจว่าเป็นบัญชีที่ถูกต้อง |
| 6 | เพิ่มสินค้า 1 ชิ้น ไป checkout ตรวจราคา 225 บาท |
| 7 | เว้น Address line 1 แล้วลองสั่งซื้อ ต้องแจ้งช่องบังคับและไม่แสดงการซื้อสำเร็จ |
| 8 | กลับ cart แล้วเข้า checkout อีกครั้ง ตรวจข้อมูล cart และ login session |
| 9 | กรอกครบและสั่งซื้อ COD ตรวจ confirmation และราคา 225 บาท |
| 10 | Customer เปิด My account → Orders ตรวจ order ของตน |
| 11 | Staff เปิด order และตรวจข้อมูล customer ที่สัมพันธ์กัน |
| 12 | Staff เปลี่ยน order เป็น Completed |
| 13 | Customer refresh ประวัติ ตรวจสถานะ Completed |
| 14 | Logout/login อีกครั้ง ตรวจว่า order และสถานะยังอยู่ |

หากการสมัครต้องยืนยันอีเมลที่บัญชีสมมติรับไม่ได้ ให้บันทึก Blocked และสอบถามผู้สอนเรื่องบัญชีทดสอบ ห้ามข้ามแล้วรายงานว่า Pass

## 6. Evidence and limitations

- บันทึก actual result และ screenshot รายขั้นตอนเมื่อรันจริง; ขั้นตอนที่ทำต่อไม่ได้ให้ใช้ Blocked
- หากตรวจ Network ให้ผูก API ID กับ test case/step, method, path, status และหลักฐาน โดยไม่เผย password, Authorization, Cart-Token หรือข้อมูลส่วนบุคคล
- Network capture ที่แสดงว่า request ถูกส่ง ยังไม่เพียงพอสำหรับยืนยันว่า response ถูกต้อง ต้องตรวจ expected status และ fields ด้วย
- Account registration/login และ customer order history เป็น Web UI features ใน Guide ไม่เพิ่ม endpoint ที่คู่มือไม่ได้ระบุ
- Basic Auth ผิด, Cart-Token/Nonce ผิด, ID ไม่พบ, malformed input และ query boundaries ยังต้องออกแบบใน API Testing suites
- ห้ามแก้หรือลบ demo data หรือข้อมูลกลุ่มอื่น
- ห้ามสร้าง orders/bookings ระหว่าง performance/load testing; checkout ในเอกสารนี้เป็น functional system testing
- เอกสารนี้ไม่ได้เปลี่ยนข้อกำหนด Project 2 ให้ต้องทดสอบ API ครบ 24 operations: โจทย์ API Testing กำหนดขั้นต่ำ 3 operations โดยอย่างน้อย 1 operation สร้าง/เปลี่ยนข้อมูล
