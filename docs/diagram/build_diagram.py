"""Build the source-backed, standalone nested API map. No imports of test code."""
import ast
from datetime import datetime, timezone
import hashlib
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from case_examples import build_example

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W, H = 3000, 2440
nodes = []


def read_recorded_requests(log_path):
    """Read the existing runner's JSON lines, never import or execute API tests."""
    cases, shared, current, after_outcome = {}, [], None, False
    for line_number, line in enumerate((ROOT / log_path).read_text().splitlines(), 1):
        header = re.match(r"API testing/.*\[(S\d\d-\d\d)-[^\]]+\]", line)
        if header:
            current, after_outcome = header[1], False
            assert current not in cases, f"Duplicate console case {current}"
            cases[current] = []
        if line.startswith(("PASSED", "FAILED", "ERROR", "SKIPPED")):
            after_outcome = True
        start = line.find('{"time_utc":')
        if start < 0:
            continue
        raw = json.loads(line[start:])
        entry = {key: raw[key] for key in ("time_utc", "method", "path", "query", "input", "auth_mode", "status", "response")}
        entry["line"] = line_number
        if entry["method"] == "GET" and entry["path"] == "/wc/v3/products" and entry["query"] == {"per_page": 1}:
            shared.append(entry)
            continue
        assert current is not None, f"Request outside a case at line {line_number}"
        entry["afterOutcome"] = after_outcome
        cases[current].append(entry)
    assert len(shared) == 1, "Expected the documented session-scoped preflight exactly once"
    return cases, shared


def request_details(sid, cid, values, recorded, log_path):
    entries = recorded[cid]
    def is_target(r):
        if sid == "S01":
            return r["method"] == "GET" and r["path"] == "/wc/store/v1/products"
        if sid == "S02":
            return r["method"] == "GET" and re.fullmatch(r"/wc/store/v1/products/\d+", r["path"])
        return r["method"] == "POST" and r["path"] == "/wc/v3/products"
    positions = [i for i, entry in enumerate(entries) if is_target(entry)]
    assert len(positions) == 1, f"{cid} must have exactly one operation-under-test request"
    target_index = positions[0]
    primary = entries[target_index]
    if sid == "S01":
        assert primary["query"]["per_page"] == values["per_page"]
        if values["search_kind"] == "omitted":
            assert "search" not in primary["query"]
        elif values["search_kind"] == "match":
            assert primary["query"]["search"] == entries[0]["input"]["name"]
        else:
            assert primary["query"]["search"].startswith("nomatch")
        quantity = f"per_page={values['per_page']} คือค่าจำนวนสินค้าสูงสุดที่ส่งไป ไม่ใช่จำนวน HTTP requests"
        if primary["status"] >= 400:
            quantity += " · case นี้จงใจส่งค่านอกช่วงเพื่อให้ API ปฏิเสธ"
    elif sid == "S02":
        assert primary["path"].endswith("/" + str(entries[0]["response"]["id"]))
        expected_query = {"omitted": None, "valid": {"context": "view"}, "invalid": {"context": "not-a-context"}}[values["context_kind"]]
        assert primary["query"] == expected_query, f"{cid} recorded context query differs from the test input"
        quantity = "ขอรายละเอียดสินค้า 1 ID ไม่ใช่ขอรายการหลายหน้า"
        if primary["status"] >= 400 and values["context_kind"] == "invalid":
            quantity += " · case นี้จงใจส่ง context นอก enum เพื่อให้ API ปฏิเสธ"
    else:
        assert primary["auth_mode"] == values["auth_mode"]
        assert primary["input"]["status"] == values["status"]
        quantity = "ส่ง JSON object เพื่อขอสร้างสินค้า 1 รายการ ไม่ใช่ batch request"
    counts = dict(setup=0, underTest=0, verification=0, cleanup=0)
    steps = []
    for i, entry in enumerate(entries):
        phase = "setup" if i < target_index else "underTest" if i == target_index else "cleanup" if entry["afterOutcome"] else "verification"
        counts[phase] += 1
        steps.append({**{key: value for key, value in entry.items() if key != "afterOutcome"}, "phase": phase})
    request = {"count": 1, "method": primary["method"], "path": primary["path"],
               "query": primary["query"], "body": primary["input"], "authMode": primary["auth_mode"],
               "status": primary["status"], "response": primary["response"], "line": primary["line"], "quantity": quantity}
    return request, {"total": len(steps), "counts": counts, "steps": steps, "source": log_path}


def readme_span(start, end):
    """Line range from the README line starting with `start` up to the line before `end`."""
    lines = (ROOT / "README.md").read_text().splitlines()
    first = next(i for i, l in enumerate(lines, 1) if l.startswith(start))
    stop = next(i for i, l in enumerate(lines, 1) if i > first and l.startswith(end))
    while stop - 1 > first and not lines[stop - 2].strip():
        stop -= 1
    return first, stop - 1



def source(path, line=1, end=None):
    text = (ROOT / path).read_text().splitlines()
    return {"file": path, "line": line, "end": end or line,
            "excerpt": "\n".join(text[line-1:min(end or line+10, len(text))])}


def add(id, title, parent, what, why="", inputs=None, outputs=None, sources=None, refs=None, kind="module", **extra):
    n = dict(id=id, title=title, parent=parent, what=what, why=why,
             inputs=inputs or [], outputs=outputs or [], sources=sources or [],
             graphRefs=refs or [], kind=kind, **extra)
    nodes.append(n)
    return n


def make_model():
    graph = json.loads((ROOT / "graphify-out/graph.json").read_text())
    latest = json.loads((ROOT / "API testing/results/latest-run.json").read_text())
    for path, digest in latest["source_sha256"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, f"Test source changed: {path}; review the map before rebuilding"
    learning = json.loads((HERE / "learning-content.json").read_text())
    result_file = latest["directory"] + "/junit.xml"
    recorded_cases = list(ET.parse(ROOT / result_file).getroot().iter("testcase"))
    results = {case.attrib["name"]: case for case in recorded_cases}
    assert len(results) == len(recorded_cases), "Duplicate JUnit case names; cannot map evidence unambiguously"
    console_path = latest["directory"] + "/console.txt"
    recorded_requests, shared_preflight = read_recorded_requests(console_path)
    g_ids = {n["id"] for n in graph["nodes"]}
    add("scope-api", "API Testing ของกลุ่มเรา", None,
        "ตรวจการอ่านรายการ/ค้นหา อ่านสินค้าตาม ID และสร้างสินค้า บน WooCommerce ที่อาจารย์เตรียมไว้",
        "มองจากภาพรวมก่อน แล้วเลือกกล่องเพื่อดูส่วนย่อย ไม่จำเป็นต้องเริ่มอ่านโค้ด", outputs=["3 suites / 17 distinct cases", "pytest + requests · automated API tests ไม่ใช่ UI tests"], sources=[source("README.md",*readme_span("Selected system:","One Python file is one operation suite."))])
    add("local-run", "ฝั่งเครื่องเรา · Test harness", "scope-api", "ส่วนที่เราพัฒนาเพื่อเตรียมข้อมูล ส่ง HTTP requests ตรวจคำตอบ และบันทึกหลักฐาน", sources=[source("README.md",*readme_span("### Run all three suites","### How to read the ISP design"))])
    add("api-testing", "3 operation suites", "scope-api", "แต่ละ suite ทดสอบหนึ่ง operation และมีหลาย inputs ที่มาจาก ISP", "ไม่มีลูกศรบังคับ Suite 1 → 2 → 3: แต่ละ case เตรียมข้อมูลของตัวเอง", outputs=["S01: 7 cases", "S02: 5 cases", "S03: 5 cases"], sources=[source("README.md",*readme_span("The tests call the existing","One Python file is one operation suite."))])
    add("api-runner", "Runner · สั่งรันและเก็บผล", "local-run", "คำสั่ง python run_api_tests.py เริ่ม pytest แล้วเก็บผลหลังจบ subprocess",
        "ใช้คำสั่งเดียวและเก็บหลักฐานเป็นรอบ ไม่เขียนทับผลเก่า", inputs=["suite paths (optional)", "credentials จาก environment — ไม่ใส่ค่าในกราฟ"], outputs=["pytest subprocess", "console.txt / junit.xml / run.json", "latest-run.json"], sources=[source("run_api_tests.py",17,72)], refs=["run_api_tests_main"])
    add("pytest", "pytest · ผู้รัน test cases", "local-run", "ค้นหา parametrized tests เรียก fixtures และประเมิน assertions ของแต่ละ case",
        "17 cases มาจาก 3 test functions ที่รันซ้ำด้วย input ต่างกัน ไม่ใช่ 17 ไฟล์", sources=[source("API testing/test_product_list.py",10,23), source("pyproject.toml",1,2)])
    add("api-preflight", "Configuration + preflight", "local-run", "ตรวจว่ามี credentials ของ G05 และ run ID ถูกต้อง จากนั้น Admin GET แบบอ่านอย่างเดียวต้องสำเร็จก่อนเริ่ม fixtures",
        "ถ้าตั้งค่าผิดจะรายงาน setup error ไม่ข้าม tests แล้วนับเป็นผ่าน", inputs=["SHOP_USER", "SHOP_API_PASSWORD", "SHOP_BASE_URL", "run ID"], outputs=["configuration พร้อมใช้", "Admin read preflight 200"], sources=[source("API testing/conftest.py",12,31)], refs=["api_testing_conftest_shop_config"])
    add("fixtures", "Fixtures · เตรียมและเก็บกวาด", "local-run", "pytest ให้ HTTP client และ product factory ชุดใหม่แก่ทุก case แล้ว cleanup ใน finally",
        "Case เดี่ยวหรือสลับ suites ก็ไม่ต้องรอข้อมูลจาก test ก่อนหน้า", sources=[source("API testing/conftest.py",34,47)], refs=["api_testing_conftest_api","api_testing_conftest_products"])
    add("clients", "ShopAPI · HTTP gateway", "fixtures", "แยก public Store session และ authenticated Admin session ออกจากกัน", inputs=["method + route + query / JSON body"], outputs=["HTTP response + safe evidence summary"], sources=[source("API testing/shop_support.py",50,116)], refs=["api_testing_shop_support_shopapi"])
    add("store-client", "Public Store client", "clients", "ส่ง requests ไปยัง /wc/store/v1 โดยไม่ส่ง group credentials", sources=[source("API testing/shop_support.py",75,116)], refs=["api_testing_shop_support_shopapi_store"])
    add("admin-client", "Authenticated Admin client", "clients", "ใช้ Shop API password เฉพาะ Admin requests; negative cases เลือกไม่ส่งหรือส่งรหัสผิดตาม test input",
        "ไม่ส่ง Authorization header ไปกับ Store requests และไม่ตาม redirects", sources=[source("API testing/shop_support.py",75,94)], refs=["api_testing_shop_support_shopapi_admin"])
    add("products-fixture", "ProductFactory · disposable data", "fixtures", "สร้างชื่อ/SKU เฉพาะ G05 + run marker เพื่อตั้ง preconditions ที่เรารู้คำตอบล่วงหน้า", outputs=["published / draft / absent product state ที่ควบคุมได้"], sources=[source("API testing/shop_support.py",119,177)], refs=["api_testing_shop_support_productfactory"])
    add("fixture-create", "payload → submit → create", "products-fixture", "เตรียม JSON ของสินค้า simple ราคา 100.00 THB ลงทะเบียน SKU ก่อน POST แล้วจด ID ที่ server คืนมา", sources=[source("API testing/shop_support.py",129,164)], refs=["api_testing_shop_support_productfactory_create","api_testing_shop_support_productfactory_submit"])
    add("cleanup-ownership", "Cleanup · ยืนยันเจ้าของก่อนลบ", "products-fixture", "ตรวจ exact ID + exact G05 name + run metadata ก่อน DELETE แล้วตรวจ Admin GET 404 หลังลบ",
        "ห้ามลบ demo/สินค้ากลุ่มอื่น หรือกวาดลบด้วย prefix อย่างเดียว", outputs=["ลบเฉพาะข้อมูล disposable ของ case นี้", "cleanup error ถ้ายืนยันไม่ได้"], sources=[source("API testing/shop_support.py",11,25),source("API testing/shop_support.py",179,216)], refs=["api_testing_shop_support_is_owned_product","api_testing_shop_support_productfactory_cleanup"])
    add("unknown-post", "Interrupted POST ≠ ไม่มีสินค้า", "cleanup-ownership", "ถ้า response ขาดหาย อาจสร้างสินค้าสำเร็จแล้ว จึงไม่ POST ซ้ำแบบ blind retry", "ค้นด้วย exact unique SKU เพื่อ reconcile; ถ้ายังไม่แน่ชัดจะเก็บ unknown outcome และรายงาน error", sources=[source("API testing/shop_support.py",139,155),source("API testing/shop_support.py",196,216)], refs=["api_testing_shop_support_productfactory_lookup"])
    add("offline-checks", "7 offline harness checks", "cleanup-ownership", "ตรวจ guard ว่าไม่รับสินค้า/marker/ID ที่ผิด และไม่อ้างว่า cleanup สำเร็จหลัง POST ที่ยังไม่รู้ผล", "เป็นการตรวจ test harness ไม่ใช่เพิ่มจำนวน assignment cases จาก 17 เป็น 24", sources=[source("verification/test_api_support.py",14,65)], refs=["verification_test_api_support_ownershipchecks"])
    add("assertions", "Assertions · กติกาตัดสินผล", "api-testing", "ตรวจ status code และ fields ที่สำคัญ ไม่ใช่เพียง server ตอบกลับ", inputs=["expected result จาก contract และ fixture input", "actual response จาก server"], outputs=["PASS เมื่อได้ผลที่คาดไว้ รวม HTTP 400/401/404 ที่เป็น negative cases"], sources=[source("API testing/shop_support.py",28,47)], refs=["api_testing_shop_support_assert_error","api_testing_shop_support_assert_store_product"])
    add("sut", "WooCommerce · ระบบที่ถูกทดสอบ", "scope-api", "ระบบของอาจารย์ที่รับ requests จาก test code ของเรา ไม่ใช่โค้ดที่เรากำลัง implement", "ไม่มีการเปิด browser/คลิกหน้าเว็บใน API suites เหล่านี้", sources=[source("README.md",*readme_span("## API testing: start here","One Python file is one operation suite."))])
    add("store-api", "Store API · มุมลูกค้า", "sut", "API สาธารณะสำหรับอ่านข้อมูลสินค้าที่เปิดเผยให้ลูกค้าเห็น", outputs=["GET products", "GET products/{id}"], sources=[source("API testing/test_product_list.py",23,46),source("API testing/test_product_detail.py",17,31)])
    add("admin-api", "Admin REST API · มุมพนักงาน", "sut", "API สำหรับ Shop manager: POST สร้างสินค้าเป็น subject ของ S03; GET/DELETE ยังใช้เตรียม/ตรวจ/ลบ fixtures", outputs=["POST /products — operation under test", "GET product(s) — preflight/setup/read-back", "DELETE owned product — cleanup"], sources=[source("API testing/test_product_create.py",21,47),source("API testing/shop_support.py",139,192)])
    add("product-state", "สถานะข้อมูลสินค้า (conceptual)", "sut", "การสร้าง อ่านกลับ และลบมองเห็นผ่าน API ว่าข้อมูลถูกเก็บ/เปลี่ยนสถานะแล้ว", "ไม่ได้ clone หรือ inspect implementation/database schema ภายใน WooCommerce จึงไม่อ้างโครงสร้าง DB จริง", kind="concept", confidence="INFERRED", sources=[source("API testing/test_product_create.py",36,47)])
    run_counts = latest["counts"]; run_date = latest["started_bangkok"][:16].replace("T", " ")
    run_passed = run_counts["tests"] - run_counts["failures"] - run_counts["errors"] - run_counts["skipped"]
    add("evidence", "Execution evidence · ผลที่บันทึก", "scope-api", f"ผลจริงที่บันทึกล่าสุด {run_date} Bangkok ไม่ใช่สถานะสดหรือการรันใหม่ในหน้ากราฟนี้", outputs=[f"latest full run {run_passed}/{run_counts['tests']} ผ่าน", "รอบ 15 cases วันที่ 9 พ.ย. เก็บไว้เป็นประวัติ"], sources=[source("README.md",*readme_span("### Execution results and limitations","### Sources for the design"))], runSummary={"passed": run_passed, "tests": run_counts["tests"], "date": run_date})
    add("evidence-console", "console.txt · requests + outcomes", "evidence", "เก็บ output เต็ม พร้อม query/payload และ selected response fields โดยไม่เก็บ Authorization/password", sources=[source(latest["directory"]+"/console.txt",1,10)])
    add("evidence-junit", "junit.xml · per-case result", "evidence", "ผล structured ของแต่ละ parametrized test ใช้ตรวจจำนวน pass/failure/error/skip", sources=[source("run_api_tests.py",49,58)])
    add("evidence-manifest", "run.json + source hashes", "evidence", "ผูกผลแต่ละรอบกับคำสั่ง เวลา และ SHA-256 ของ test source; latest pointer เป็นรอบ S03→S02→S01", sources=[source("run_api_tests.py",59,71),source("API testing/results/latest-run.json",1,35)])
    suites = [
        ("S01","อ่านรายการ / ค้นหาสินค้าตามชื่อ","test_product_list.py","test_list_products",["C1 · per_page: ≤0 / 1–100 / ≥101","C2 · search: ไม่ส่ง / match / no match"],"BCC 5 + boundary probes 2 = 7", "api_testing_test_product_list_test_list_products"),
        ("S02","อ่านสินค้าตาม ID","test_product_detail.py","test_product_detail",["C1 · resource state: published / draft / absent","C2 · context: ไม่ส่ง / ค่าที่ถูกต้อง / ค่านอก enum"],"BCC 1 + (3−1) + (3−1) = 5", "api_testing_test_product_detail_test_product_detail"),
        ("S03","สร้างสินค้าใหม่","test_product_create.py","test_create_product",["C1 · credentials: ถูก / ไม่ส่ง / ผิด","C2 · publication: publish / unpublished / invalid"],"BCC 1 + (3−1) + (3−1) = 5", "api_testing_test_product_create_test_create_product"),
    ]
    titles={
        "S01-01":"ค้นหาสินค้าด้วยชื่อที่ตรงกัน", "S01-02":"ค้นหาสินค้าโดยส่ง per_page=0", "S01-03":"ค้นหาสินค้าโดยส่ง per_page=101", "S01-04":"อ่านรายการสินค้าโดยไม่ระบุคำค้น", "S01-05":"ค้นหาด้วยชื่อที่ไม่ตรงกับสินค้า", "S01-06":"ค้นหาสินค้าโดยขอสูงสุด 1 รายการ", "S01-07":"ค้นหาสินค้าโดยขอสูงสุด 100 รายการ",
        "S02-01":"อ่านสินค้าที่เผยแพร่แล้วด้วย ID", "S02-02":"ขออ่าน draft ด้วย ID — ต้องไม่เปิดเผย", "S02-03":"ขอข้อมูลสินค้าที่ลบแล้วด้วย ID", "S02-04":"อ่านสินค้าโดยส่ง context=view", "S02-05":"อ่านสินค้าโดยส่ง context ที่ไม่ถูกต้อง",
        "S03-01":"สร้างและเผยแพร่สินค้าด้วยสิทธิ์ถูกต้อง", "S03-02":"ขอสร้างสินค้าโดยไม่ส่ง credentials", "S03-03":"ขอสร้างสินค้าโดยใช้ password ผิด", "S03-04":"สร้างสินค้าเป็น draft ไม่เผยแพร่", "S03-05":"ขอสร้างสินค้าด้วย status ที่ไม่ถูกต้อง",
    }
    for sid,title,file,function,partitions,criterion,ref in suites:
        path="API testing/"+file
        tree=ast.parse((ROOT/path).read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function)
        dec=next(d for d in fn.decorator_list if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=="parametrize")
        names=ast.literal_eval(dec.args[0]).split(",")
        suite=add(sid,title,"api-testing",f"{sid} ทดสอบ operation นี้ด้วย inputs ตาม ISP ไม่ต้องพึ่ง suite ก่อนหน้า", criterion,
                  inputs=partitions, outputs=[criterion],sources=[source(path,fn.lineno,fn.end_lineno)],refs=[ref],kind="suite",partitions=partitions,criterion=criterion)
        suite["isp"] = learning["suites"][sid]
        suite["sources"].append(source("README.md", *readme_span(*suite["isp"]["readmeSection"])))
        for param in dec.args[1].elts:
            values=[ast.literal_eval(a) for a in param.args]
            label=next(ast.literal_eval(k.value) for k in param.keywords if k.arg=="id")
            cid="-".join(label.split("-")[:2]); input=dict(zip(names,values))
            if sid=="S01":
                status=input["expected_status"]; p=input["per_page"]; search=input["search_kind"]
                search_block={"omitted":1,"match":2,"no-match":3}[search]
                block=f"C1-B{1 if p<=0 else 3 if p>=101 else 2} + C2-B{search_block}"
                setup="สร้าง published product ของ case นี้ ราคา 100.00 THB และรู้ชื่อ/ID ล่วงหน้า"
                summary=f"per_page={p} · search={search}"
                expected="JSON error ระบุ per_page + message + data.status" if status==400 else "รายการว่าง []" if search=="no-match" else "รายการไม่เกินจำนวนที่ขอ; ID/name เป็นชนิดถูกต้อง" if search=="omitted" else "เจอ fixture ของเรา; ID/name/ราคา 100.00 THB ตรงกัน"
                note="per_page คือจำนวนสูงสุดที่ขอ ไม่ใช่จำนวนสินค้าในร้าน ไม่ต้องมีสินค้า 100 ชิ้นเพื่อทดสอบ 100/101"
            elif sid=="S02":
                state=input["resource_state"];status=input["expected_status"];context=input["context_kind"]
                block=f"C1-B{ {'publish':1,'draft':2,'absent':3}[state] } + C2-B{ {'omitted':1,'valid':2,'invalid':3}[context] }"
                setup="สร้าง published แล้ว Admin GET ยืนยันสถานะ" if state=="publish" else "สร้าง draft แล้ว Admin GET 200 ยืนยันว่ายังมีอยู่" if state=="draft" else "สร้าง draft ของเรา → ลบ exact ID → Admin GET 404 ยืนยันว่าไม่มีอยู่แล้ว"
                summary=f"resource_state={state} · context={context}"
                expected="ID/name/ราคา ตรงกับ fixture" if status==200 else "JSON error rest_invalid_param ระบุ context + message + data.status=400" if status==400 else "JSON error มี code/message/data.status=404"
                note="context เป็น query parameter ที่ route นี้ประกาศไว้ (enum view/embed/edit, default view)" if context!="omitted" else "404 เหมือนกันไม่ได้แปลว่า test ซ้ำ: draft ต้องไม่หลุดสู่ public API ส่วน absent ตรวจทรัพยากรที่ไม่มีจริง"
            else:
                status=input["expected_status"]; auth=input["auth_mode"]; publication=input["status"]
                block=f"C1-B{ {'valid':1,'missing':2,'wrong':3}[auth] } + C2-B{1 if publication=='publish' else 2 if publication=='draft' else 3}"
                setup="JSON valid: G05 unique name/SKU, simple, regular_price=100.00, run marker"
                summary=f"auth={auth} · status={publication}"
                expected="บันทึก ID/name/SKU/type/status/ราคา ถูกต้อง; Admin อ่านกลับได้; public visibility ตรงสถานะ" if status==201 else "ปฏิเสธ + JSON error และ exact SKU lookup ยืนยันว่าไม่สร้างสินค้า"
                note="คำว่า create product คือเพิ่มข้อมูลผ่าน Admin API ที่มีอยู่ ไม่ใช่แก้ site code/settings"
            test_name = f"{function}[{label}]"
            assert test_name in results, f"No JUnit evidence for {cid}"
            result = results[test_name]
            outcome = "ERROR" if result.find("error") is not None else "FAIL" if result.find("failure") is not None else "SKIP" if result.find("skipped") is not None else "PASS"
            recorded = {"status": outcome, "testName": test_name, "startedBangkok": latest["started_bangkok"], "runId": latest["run_id"], "file": result_file}
            request, traffic = request_details(sid, cid, input, recorded_requests, console_path)
            assert request["status"] == status, f"Recorded status differs from expected for {cid}; review rather than imply PASS"
            original_parameter = source(path, param.lineno, param.end_lineno)
            original_function = source(path, fn.lineno, fn.end_lineno)
            example = {"code": build_example(tree, fn, input, cid), "language": "python",
                       "originalParameter": original_parameter["excerpt"], "originalFunction": original_function["excerpt"],
                       "file": path, "line": fn.lineno, "standalone": False, "executedInBrowser": False,
                       "method": "Bind actual pytest values, fold only known equality branches, keep runtime assertions and helper calls"}
            add(cid,titles[cid],sid,"ทดสอบ "+titles[cid],note,inputs=[summary,block],outputs=[f"HTTP {status}",expected], sources=[original_parameter,original_function],refs=[ref],kind="case",input=input,expectedStatus=status,setup=setup,summary=summary,blocks=block,expected=expected,paramId=label,explanation=learning["cases"][cid],recordedResult=recorded,request=request,traffic=traffic,exampleCode=example)
    assert set(learning["cases"]) == {n["id"] for n in nodes if n["kind"] == "case"}, "Learning content must cover exactly the implemented cases"
    assert set(learning["suites"]) == {n["id"] for n in nodes if n["kind"] == "suite"}, "Learning content must cover exactly the implemented suites"
    assert set(recorded_requests) == set(learning["cases"]), "Console evidence must map to exactly the implemented cases"
    for node in nodes:
        assert all(ref in g_ids for ref in node["graphRefs"]), node["id"]
        node["children"]=[n["id"] for n in nodes if n["parent"]==node["id"]]
    relations=[
        ("api-runner","pytest","starts","เริ่ม pytest subprocess"),("pytest","api-testing","runs","รัน case ของ 3 suites"),("pytest","api-preflight","uses","configuration gate ก่อน fixtures"),
        ("fixtures","api-testing","supplies","client + data ของแต่ละ case"),("fixtures","clients","creates","client ใหม่ต่อ case"),("fixtures","products-fixture","creates","factory ใหม่ต่อ case"),
        ("store-client","store-api","requests","GET public · ไม่ส่ง group auth"),("admin-client","admin-api","requests","authenticated requests / negative auth input"),
        ("products-fixture","admin-api","prepares","POST/GET/DELETE สำหรับ preconditions + cleanup"),
        ("S01","store-api","tests","GET list/search"),("S02","store-api","tests","GET product by ID"),("S03","admin-api","tests","POST create product"),
        ("S03","store-api","checks","ตรวจ public visibility หลังสร้าง"),("api-testing","assertions","checks","status + important response fields"),
        ("cleanup-ownership","admin-api","cleans","ตรวจ exact ownership → DELETE → GET 404"),("api-runner","evidence","writes","เก็บ output หลัง pytest จบ"),
        ("evidence","api-testing","records","ผลรอบที่บันทึก ไม่ใช่ live status"),("store-api","product-state","observes","conceptual API-visible state"),("admin-api","product-state","changes","conceptual API-visible state"),
    ]
    return {"title":"แผนที่ API Testing", "built_utc":datetime.now(timezone.utc).isoformat(),"stage":{"width":W,"height":H},"nodes":nodes,
            "relations":[dict(source=a,target=b,relation=r,label=l,confidence="INFERRED" if "product-state" in (a,b) else "EXTRACTED") for a,b,r,l in relations],
            "graph":{"nodes":len(graph["nodes"]),"edges":len(graph.get("links",graph.get("edges",[]))),"sourceFiles":18,"sha256":hashlib.sha256((ROOT/"graphify-out/graph.json").read_bytes()).hexdigest()},"latestRecordedRun":latest,
            "recordedTraffic":{"source":console_path,"sharedPreflight":shared_preflight,"total":sum(len(r) for r in recorded_requests.values())+len(shared_preflight)}}


def render(model):
    byid={n["id"]:n for n in model["nodes"]}
    def control(id,label=None):
        return f'<button class="node-pick" data-pick="{id}" type="button">{escape(label or byid[id]["title"])}</button>'
    def card(id,children="",cls=""):
        n=byid[id]
        return f'<article id="node-{id}" class="map-node {cls}" data-node-id="{id}"><header><span class="ref">{id}</span>{control(id)}</header><p class="node-what">{escape(n["what"])}</p>{children}</article>'
    def suite(id):
        n=byid[id]; cases=[byid[c] for c in n["children"] if byid[c]["kind"]=="case"]
        rows="".join(f'<article class="case-row" data-node-id="{c["id"]}" id="node-{c["id"]}"><button data-pick="{c["id"]}" class="case-title" type="button"><span>{c["id"]}</span>{escape(c["title"])}</button><span class="http-code">HTTP {c["expectedStatus"]}</span><p class="case-input">{escape(c["summary"])}</p><p class="case-blocks">{escape(c["blocks"])}</p></article>' for c in cases)
        partition="".join(f'<p>{escape(x)}</p>' for x in n["partitions"])
        return f'<section class="suite suite-{id}" data-node-id="{id}" id="node-{id}"><header><span class="ref">{id} · {len(cases)} cases</span>{control(id)}<p>{escape(n["criterion"])}</p></header><div class="overview-splash"><strong>{len(cases)}</strong><span>test cases</span><button type="button" data-focus="{id}">Zoom เข้าไปดู</button></div><div class="suite-detail"><div class="partitions">{partition}</div><p class="independent">แต่ละ case เป็นอิสระ · ไม่ใช่ลำดับขั้น</p><div class="case-list">{rows}</div></div></section>'
    def leaf(id,label):
        return f'<button class="leaf-node" data-pick="{id}" data-node-id="{id}" id="node-{id}" type="button">{escape(label)}</button>'
    tree='<div class="fixture-tree"><section class="mini-module" data-node-id="clients" id="node-clients">'+control("clients","ShopAPI · HTTP clients")+'<div class="leaf-grid">'+leaf("store-client","Public Store")+leaf("admin-client","Admin + auth")+'</div></section><section class="mini-module" data-node-id="products-fixture" id="node-products-fixture">'+control("products-fixture","ProductFactory · data")+'<div class="leaf-grid">'+leaf("fixture-create","payload / create")+leaf("cleanup-ownership","ownership / cleanup")+'</div></section></div>'
    local=card("api-runner",cls="runner-card")+'<div class="local-arrow" aria-hidden="true">↓</div>'+card("pytest",cls="pytest-card")+card("api-preflight",cls="preflight-card")+card("fixtures",tree,cls="fixture-card")
    suites=suite("S01")+'<div class="suite-stack">'+suite("S02")+suite("S03")+'</div>'
    server=card("store-api",'<div class="route"><b>GET</b> /wc/store/v1/products</div><div class="route"><b>GET</b> /wc/store/v1/products/{id}</div>')+card("admin-api",'<div class="route"><b>POST</b> /wc/v3/products <em>under test</em></div><div class="route supporting">GET product(s) · fixture/read-back</div><div class="route supporting">DELETE owned ID · cleanup only</div>')+card("product-state",cls="concept-node")
    rs=byid["evidence"]["runSummary"]
    evidence=card("evidence",f'<div class="recorded-result">{rs["passed"]} / {rs["tests"]} ผ่าน <small>บันทึก {rs["date"]}</small></div><div class="mini-children">'+control("evidence-console","console.txt")+control("evidence-junit","junit.xml")+control("evidence-manifest","run.json + hashes")+'</div>')
    return f'''<section class="diagram-content" data-node-id="scope-api" id="node-scope-api">
    <header class="map-heading"><div><div class="eyebrow">ITCS386 · OPENAI · SOURCE-BACKED REVIEW MAP</div><h1>API Testing — เห็นภาพก่อนอ่านโค้ด</h1><p>อ่าน/ค้นหา · อ่านตาม ID · สร้างสินค้า บน WooCommerce ที่อาจารย์เตรียมไว้</p></div><div class="scope-badge">เฉพาะ API Testing<br><b>3 suites · 17 cases</b></div></header>
    <section class="level-strip"><div><b>01</b><strong>ภาพรวม</strong><span>เครื่องเรา ↔ ระบบอาจารย์</span></div><div><b>02</b><strong>Modules</strong><span>runner · fixtures · clients</span></div><div><b>03</b><strong>Suites / ISP</strong><span>กลุ่ม inputs และ expected results</span></div><div><b>04</b><strong>Cases / source</strong><span>เลือก ID เพื่อดูรายละเอียด</span></div></section>
    <section class="map-columns"><section class="group local-group" data-node-id="local-run" id="node-local-run"><header class="group-heading"><span class="eyebrow">LOCAL · CODE WE OWN</span>{control("local-run")}</header>{local}</section>
    <section class="group api-group" data-node-id="api-testing" id="node-api-testing"><header class="group-heading"><span class="eyebrow">AUTOMATED API TESTS · NOT UI TESTS</span>{control("api-testing")}<p>Higher level ครอบ modules → suites → cases</p></header><div class="suite-grid">{suites}</div></section>
    <div class="remote-column"><section class="group server-group" data-node-id="sut" id="node-sut"><header class="group-heading"><span class="eyebrow">EXTERNAL · SYSTEM UNDER TEST</span>{control("sut")}</header>{server}</section>{evidence}</div></section>
    <section class="lifecycle"><strong>หนึ่ง case ทำงานอย่างไร?</strong><div><span>1 · Arrange<small>fixture เตรียม known state</small></span><b>→</b><span>2 · Act<small>ส่ง request ที่จะทดสอบ</small></span><b>→</b><span>3 · Assert<small>ตรวจ status + fields</small></span><b>→</b><span>4 · Cleanup<small>ลบเฉพาะของเราและตรวจซ้ำ</small></span></div><p>นี่คือลำดับภายใน case จาก source · เส้น connection ระหว่าง modules ไม่ได้แปลว่าต้องรัน suites ตามลำดับ</p></section>
    <footer class="map-footer"><span>Graphify: {model['graph']['nodes']} nodes / 18 input files · โค้ดและหลักฐานเดิม ไม่มี live requests จากหน้านี้</span><span>กรอบซ้อนกัน = contains · สีเทาเส้นประ = conceptual / ไม่ inspect implementation</span></footer>
    <svg id="connections" class="connections" viewBox="0 0 {W} {H}" aria-hidden="true"><defs><marker id="arrow-head" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs><g id="connection-paths"></g></svg>
    </section>'''


def main():
    model=make_model()
    (HERE/"map-model.json").write_text(json.dumps(model,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    template=(HERE/"template.html").read_text()
    template=template.replace('lang="en"','lang="th"').replace('<title>Interactive HTML Diagram</title>','<title>API Testing · Nested Review Map</title>')
    template=template.replace('const stageWidth = 1600;',f'const stageWidth = {W};').replace('const stageHeight = 900;',f'const stageHeight = {H};')
    template=template.replace('const minimumZoom = 0.50;','const minimumZoom = 0.15;').replace('const minimumFitZoom = 0.20;','const minimumFitZoom = 0.05;')
    template=template.replace('zoomValue.textContent = `${Math.round(zoom * 100)}%`;','zoomValue.textContent = `${Math.round(zoom * 100)}%`;\n        stage.dataset.lod = zoom < .52 ? "overview" : zoom < .86 ? "modules" : "detail";\n        window.dispatchEvent(new CustomEvent("diagram-view", {detail:{zoom,pan}}));')
    control_anchor='      applyView();\n    })();'
    assert template.count(control_anchor)==1, 'Diagram controls injection anchor changed'
    template=template.replace(control_anchor, '''      window.diagramControls={fit:fitView,reset:resetView,state:()=>({zoom,pan:{...pan},mode:viewMode,viewport:{width:viewport.clientWidth,height:viewport.clientHeight},stage:{width:stageWidth,height:stageHeight}}),restore:(saved)=>{
        if(!saved || !Number.isFinite(saved.zoom) || saved.zoom<minimumFitZoom || saved.zoom>maximumZoom || !Number.isFinite(saved.pan?.x) || !Number.isFinite(saved.pan?.y) || !Number.isFinite(saved.viewport?.width) || !Number.isFinite(saved.viewport?.height) || saved.viewport.width<=0 || saved.viewport.height<=0 || saved.stage?.width!==stageWidth || saved.stage?.height!==stageHeight || !['fit','manual'].includes(saved.mode))return false;
        resetWheelGesture();
        if(saved.mode==='fit'){fitView();return true;}
        zoom=saved.zoom;viewMode='manual';
        viewportSize={width:viewport.clientWidth,height:viewport.clientHeight};
        pan={x:saved.pan.x+(viewportSize.width-saved.viewport.width)/2,y:saved.pan.y+(viewportSize.height-saved.viewport.height)/2};
        applyView();return true;
      },focus:(id)=>{
        if(id==='scope-api'){fitView();return;}
        const el=document.getElementById('node-'+id); if(!el)return;
        let x=0,y=0,p=el; while(p&&p!==stage){x+=p.offsetLeft;y+=p.offsetTop;p=p.offsetParent;}
        const width=el.offsetWidth,height=el.offsetHeight; resetWheelGesture();
        viewMode='manual';viewportSize={width:viewport.clientWidth,height:viewport.clientHeight};
        const focusFloor=['S01','S02','S03','local-run','fixtures','api-testing'].includes(id)?.62:minimumFitZoom;
        zoom=Math.min(maximumZoom,Math.max(focusFloor,Math.min((viewport.clientWidth-90)/width,(viewport.clientHeight-90)/height)));
        pan={x:(viewport.clientWidth-width*zoom)/2-x*zoom,y:(height*zoom>viewport.clientHeight-90?30:(viewport.clientHeight-height*zoom)/2)-y*zoom};applyView();
      }};
      fitView();
    })();''')
    template=re.sub(r'<section class="diagram-content">.*?</section>\s*</main>',render(model)+'\n</main>',template,flags=re.S)
    controls='''<div class="app-heading" data-no-pan><a class="home-title" href="#scope-api">API Testing / Review Map</a><span id="lod-label">ภาพรวม</span><span class="hint">เลือกกล่อง · ⌘+ลาก หรือคลิกขวาลากเพื่อ pan · Ctrl/⌘+wheel เพื่อ zoom</span></div>
    <div class="jump-bar" data-no-pan><button data-focus="scope-api">ภาพรวม</button><button data-focus="local-run">Modules</button><button data-focus="S01">Suite 1</button><button data-focus="S02">Suite 2</button><button data-focus="S03">Suite 3</button><button data-focus="fixtures">Fixtures</button><button data-focus="evidence">Evidence</button><a href="../graphify-out/graph.html">Raw Graphify ↗</a></div>
    <aside id="detail-panel" data-no-pan><label for="node-search">ค้นหา ID / module / case</label><input id="node-search" type="search" placeholder="เช่น S01-02, cleanup, draft" autocomplete="off"><div id="search-results"></div><div id="node-details"></div><section class="annotation"><h3>โน้ตสำหรับให้ Codex ปรับ</h3><p class="muted">ผูกกับ ID ที่เลือก · ไม่ได้แก้โค้ดอัตโนมัติ</p><label for="node-note">สิ่งที่อยากเปลี่ยน</label><textarea id="node-note" rows="3" placeholder="เลือก node แล้วเขียนโน้ต หรือ annotate ใน Codex ได้เลย"></textarea><div class="note-actions"><button id="save-note">บันทึกโน้ต</button><button id="copy-ref">Copy ID</button><button id="export-notes">Export notes</button></div><p id="note-status" role="status"></p></section></aside>'''
    template=template.replace('</nav>', '</nav>'+controls)
    template=template.replace('</head>','<style>'+ (HERE/"map.css").read_text()+'</style></head>')
    encoded=json.dumps(model,ensure_ascii=False).replace('</','<\\/')
    template=template.replace('</body>','<script id="map-data" type="application/json">'+encoded+'</script><script>'+(HERE/"map.js").read_text()+'</script></body>')
    (ROOT/"docs/api-testing-map.html").write_text(template,encoding="utf-8")
    print(json.dumps({"nodes":len(model["nodes"]),"cases":sum(n["kind"]=="case" for n in model["nodes"]),"output":"docs/api-testing-map.html","source_test_hashes_match":True}))


if __name__=="__main__":main()
