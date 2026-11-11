"""One command for real API suites and dated, credential-redacted execution evidence."""

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test_paths", nargs="*", help="Optional suite paths, in the requested order")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    started = datetime.now(timezone.utc)
    run_id = uuid4().hex[:16]
    directory = Path("API testing/results") / (started.strftime("%Y%m%dT%H%M%SZ") + "-" + run_id[:8])
    (root / directory).mkdir(parents=True)
    xml_path = directory / "junit.xml"
    command = [sys.executable, "-m", "pytest", "-vv", "-s", "--tb=short", f"--junitxml={xml_path}"]
    command += args.test_paths or ["API testing/test_product_list.py", "API testing/test_product_detail.py", "API testing/test_product_create.py"]
    env = os.environ.copy()
    env["SHOP_TEST_RUN_ID"] = run_id
    password, user = env.get("SHOP_API_PASSWORD", ""), env.get("SHOP_USER", "")
    sensitive = [password, password.replace(" ", "")]
    if password and user:
        sensitive.append(base64.b64encode(f"{user}:{password}".encode()).decode())

    def redact(value):
        value = value.replace(str(root), "PROJECT_ROOT")
        for secret in sorted({s for s in sensitive if s}, key=len, reverse=True):
            value = value.replace(secret, "[REDACTED]")
        return value

    print(f"API run {run_id}; artifacts: {directory}", flush=True)
    output = []
    process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        line = redact(line)
        print(line, end="", flush=True)
        output.append(line)
    exit_code = process.wait()
    (root / directory / "console.txt").write_text("".join(output), encoding="utf-8")
    counts = {}
    if (root / xml_path).exists():
        xml = redact((root / xml_path).read_text(encoding="utf-8"))
        report = ET.fromstring(xml)
        suites = report.findall("testsuite")
        for suite in suites:
            suite.attrib.pop("hostname", None)
        ET.ElementTree(report).write(root / xml_path, encoding="utf-8", xml_declaration=True)
        counts = {key: sum(int(s.get(key, 0)) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
    sources = [*sorted((root / "API testing").glob("*.py")), root / "run_api_tests.py", root / "requirements.txt"]
    result = {
        "run_id": run_id, "started_utc": started.isoformat(),
        "started_bangkok": started.astimezone(ZoneInfo("Asia/Bangkok")).isoformat(),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "command": ["python", *command[1:]], "exit_code": exit_code,
        "counts": counts, "directory": directory.as_posix(),
        "source_sha256": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "scope": "3 product API operations only; not System/UI/Performance completion",
    }
    (root / directory / "run.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (root / "API testing/results/latest-run.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Saved console.txt, junit.xml and run.json in {directory}; exit {exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
