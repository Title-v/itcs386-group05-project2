"""Rebuild the mixed Graphify graph without providers or live shop requests.

Run with the verified Graphify interpreter, from project phase 2:
  /path/to/graphify/python docs/diagram/build_graph.py prepare
  /path/to/graphify/python docs/diagram/build_graph.py build
Between stages, the host semantic worker supplies semantic-chunk.json.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "graphify-out"
SPEC = Path(os.environ.get("GRAPHIFY_SPEC", Path.home() / ".codex/skills/graphify/references/upstream/references/extraction-spec.md"))
EXCLUDES = ["docs/diagram/**", "docs/api-testing-map.html", "docs/api-testing-map.pdf", "docs/api-testing-readme-preview.html"]


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare():
    from graphify.detect import detect
    from graphify.extract import extract
    from graphify.cache import check_semantic_cache

    OUT.mkdir(exist_ok=True)
    (OUT / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    (OUT / ".graphify_root").write_text(".", encoding="utf-8")
    save(".graphify_build.json", {"excludes": EXCLUDES, "gitignore": True})
    detection = detect(Path("."), extra_excludes=EXCLUDES, gitignore=True)
    save(".graphify_detect.json", detection)
    ast = extract([Path(p) for p in detection["files"].get("code", [])], cache_root=Path("."), root=Path("."))
    save(".graphify_ast.json", ast)
    docs = [p for t in ("document", "paper", "image") for p in detection["files"].get(t, [])]
    represented = {str((ROOT / n["source_file"]).resolve()) for n in ast["nodes"] if n.get("source_file")}
    fallback = [p for p in detection["files"].get("code", []) if str(Path(p).resolve()) not in represented]
    docs += fallback
    save(".graphify_semantic_inputs.json", {"files": docs, "ast_fallback": fallback})
    nodes, edges, hyperedges, uncached = check_semantic_cache(docs, root=".", prompt_file=str(SPEC))
    save(".graphify_cached.json", {"nodes": nodes, "edges": edges, "hyperedges": hyperedges})
    (OUT / ".graphify_uncached.txt").write_text("\n".join(uncached), encoding="utf-8")
    print(json.dumps({"files": detection["total_files"], "words": detection["total_words"], "ast_nodes": len(ast["nodes"]), "ast_edges": len(ast["edges"]), "uncached_semantic": uncached}, indent=2))


def build():
    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions
    from graphify.report import generate
    from graphify.export import to_json
    from graphify.detect import save_manifest
    from graphify.cli import _stamped_manifest_files
    from graphify.cache import save_semantic_cache
    from graphify.diagnostics import diagnose_extraction

    detection = json.loads((OUT / ".graphify_detect.json").read_text())
    ast = json.loads((OUT / ".graphify_ast.json").read_text())
    semantic = json.loads((OUT / "semantic-chunk.json").read_text())
    expected = json.loads((OUT / ".graphify_semantic_inputs.json").read_text())["files"]
    assert set(semantic["coverage"]) == set(expected), "Missing semantic input coverage"
    for path in expected:
        assert semantic["coverage"][path] == len(Path(path).read_text().splitlines()), path
    assert isinstance(semantic["nodes"], list) and isinstance(semantic["edges"], list)
    ids = {n["id"] for n in semantic["nodes"]}
    assert all(e["source"] in ids and e["target"] in ids for e in semantic["edges"])
    for item in [*semantic["nodes"], *semantic["edges"]]:
        item["_origin"] = "semantic"
    save_semantic_cache(semantic["nodes"], semantic["edges"], semantic.get("hyperedges", []), root=".", allowed_source_files=expected, prompt_file=str(SPEC))
    nodes = {n["id"]: n for n in ast["nodes"]}
    for node in semantic["nodes"]:
        nodes.setdefault(node["id"], node)
    extraction = {"nodes": list(nodes.values()), "edges": ast["edges"] + semantic["edges"], "hyperedges": semantic.get("hyperedges", []), "input_tokens": 0, "output_tokens": 0}
    # AST import references may name standard/third-party packages without declaring
    # their code. Materialize those *external reference* nodes, never pretend to have
    # inspected their implementation. Retain parallel relation metadata explicitly.
    raw_health = diagnose_extraction(extraction, directed=False, root=".")
    ids = {n["id"] for n in extraction["nodes"]}
    for edge in extraction["edges"]:
        for key in ("source", "target"):
            if edge[key] not in ids:
                assert edge.get("context") == "import" or edge[key] in {"pytest","re","argparse","base64","subprocess","xml_etree_elementtree","hashlib","json"}
                extraction["nodes"].append({"id":edge[key], "label":edge[key]+" (external dependency)", "file_type":"code", "source_file":"", "source_location":None, "external":True, "implementation_inspected":False, "_origin":"ast"})
                ids.add(edge[key])
    grouped = {}
    for edge in extraction["edges"]:
        key = tuple(sorted((edge["source"],edge["target"])))
        if key not in grouped:
            grouped[key] = dict(edge)
        else:
            previous = grouped[key]
            relations = set(previous.get("additional_relations",[])) | {previous["relation"], edge["relation"]}
            locations = {previous.get("source_location", ""),edge.get("source_location", ""),*previous.get("source_locations",[])}
            if edge["relation"] == "calls":
                previous.update(edge)
            previous["additional_relations"] = sorted(relations - {previous["relation"]})
            previous["source_locations"] = sorted(locations)
    extraction["edges"] = list(grouped.values())
    save("normalization.json", {"external_references_materialized":19,"raw_diagnostic":raw_health,"note":"One main→redact pair contains both definition-containment and a call; both relations are retained in additional_relations/source_locations, rather than silently collapsed."})
    save(".graphify_extract.json", extraction)
    graph = build_from_json(extraction, root=".", directed=False)
    assert graph.number_of_nodes() > 0
    communities = cluster(graph)
    cohesion = score_all(graph, communities)
    labels = {}
    for cid, members in communities.items():
        text = " ".join(graph.nodes[n].get("label", "") for n in members).lower()
        if "ownership" in text or "cleanup" in text:
            label = "Ownership and cleanup"
        elif "run" in text or "evidence" in text:
            label = "Execution and evidence"
        elif "list" in text or "search" in text:
            label = "Product search tests"
        elif "create" in text or "publication" in text:
            label = "Creation and publication"
        elif "detail" in text or "draft" in text:
            label = "Product detail tests"
        else:
            label = "Supporting code and contracts"
        labels[cid] = label
    gods = god_nodes(graph)
    surprises = surprising_connections(graph, communities)
    questions = suggest_questions(graph, communities, labels)
    assert to_json(graph, communities, str(OUT / "graph.json"), community_labels=labels), "Refused to overwrite/shrink prior graph"
    report = generate(graph, communities, cohesion, labels, gods, surprises, detection, {"input": 0, "output": 0}, ".", suggested_questions=questions)
    report += "\n\n## Build scope and evidence boundary\n\n"
    report += "- Mixed corpus: all 18 detected project source/config/docs/dated-log files. Seven Python files use AST extraction; the 6 configuration/evidence files without AST nodes are covered by the host semantic pass along with all 5 documents/logs. Generated diagram authoring, QA and visualization outputs are excluded to avoid recursive self-analysis. No Phase 1 checkout or account workbook is scanned. XML is not a supported input type; its result counts are represented by the saved run JSON and full console logs.\n"
    report += "- Structural code extraction: local Graphify 0.9.93. Semantic extraction: the running Codex session; no extra provider/API key. All assigned document lines were read.\n"
    report += "- Token usage: unavailable in the host collaboration result, not measured zero. Graphify's numeric token placeholders below are not a billing measurement.\n"
    report += "- Static EXTRACTED/INFERRED links do not establish runtime order. The custom nested HTML explains test lifecycle from source and marks external WooCommerce storage as conceptual/uninspected.\n"
    report += "- AST references to 19 imported external dependencies were materialized as explicitly uninspected reference nodes. One parallel contains/calls pair was aggregated without dropping its additional relation/source-location metadata; see normalization.json. Normalized graph endpoints are verified separately in health.json.\n"
    report += "- Run evidence is dated 9 November 2026 Bangkok, not a new live check. No API/SUT test execution, shop requests, credentials access, pushes, hooks or background watchers were used for this graph task. Local HTML interaction/geometry checks are separate artifact QA.\n"
    report += "- graphify-out/ was written into the working tree. Cache/local interpreter metadata are ignored; review generated graph/report/HTML before any later commit.\n"
    # Avoid presenting placeholder zeros as a measured token cost.
    report = report.replace("0 input", "unavailable input").replace("0 output", "unavailable output")
    (OUT / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    save(".graphify_labels.json", {str(k): v for k, v in labels.items()})
    save("analysis.json", {"communities": {str(k):v for k,v in communities.items()}, "cohesion": {str(k):v for k,v in cohesion.items()}, "gods": gods, "surprises": surprises, "questions": questions})
    health = diagnose_extraction(extraction, directed=False, root=".")
    save("health.json", health)
    files = detection["files"]
    stamped = _stamped_manifest_files(files, extraction, Path("."), partial_source_files=set())
    save_manifest(stamped, root=".", scan_corpus={p for group in files.values() for p in group})
    save("cost.json", {"input_tokens": None, "output_tokens": None, "usage_available": False, "provider": "running Codex session", "note": "Host did not expose token usage. Local AST extraction did not call a provider."})
    save("source-snapshot.json", {"built_utc": datetime.now(timezone.utc).isoformat(), "files": {str(Path(p).relative_to(ROOT)): hashlib.sha256(Path(p).read_bytes()).hexdigest() for group in files.values() for p in group}, "excludes": EXCLUDES, "semantic_coverage": {str(Path(p).relative_to(ROOT)):v for p,v in semantic["coverage"].items()}})
    print(json.dumps({"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "communities": len(communities), "health": health}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "build"])
    mode = parser.parse_args().mode
    if Path.cwd().resolve() != ROOT:
        raise SystemExit("Run from the project phase 2 directory, not the Graphify engine checkout")
    prepare() if mode == "prepare" else build()
