# Graph Report - project phase 2  (2026-11-10)

## Corpus Check
- Corpus is ~9,746 words - fits in a single context window. You may not need a graph.

## Summary
- 107 nodes · 173 edges · 11 communities (8 shown, 3 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.87)
- Token cost: unavailable input · unavailable output

## Community Hubs (Navigation)
- Product search tests
- Ownership and cleanup
- Supporting code and contracts
- Ownership and cleanup
- Execution and evidence
- Product search tests
- Ownership and cleanup
- Supporting code and contracts
- Execution and evidence
- Creation and publication
- Product search tests

## God Nodes (most connected - your core abstractions)
1. `Project Phase 2 design, scope, execution guidance, and result summary` - 13 edges
2. `ProductFactory` - 11 edges
3. `ShopAPI` - 10 edges
4. `test_create_product()` - 10 edges
5. `assert_error()` - 9 edges
6. `OwnershipChecks` - 9 edges
7. `assert_store_product()` - 8 edges
8. `test_product_detail()` - 8 edges
9. `main()` - 8 edges
10. `shop_config()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Run metadata: 2026-11-08T17:36:06Z UTC, reversed suite order, 15 tests, exit code 0, no failures/errors/skips` --references--> `15 distinct API cases, not 31: repeated full runs and one isolated run test repeatability/order, not additional cases`  [EXTRACTED]
  API testing/results/20261108T173606Z-0e33c528/run.json → README.md
- `Project Phase 2 design, scope, execution guidance, and result summary` --references--> `Observed first live full run: 15 passed in 8.96s; S01, S02, S03; no failures, errors, or skips`  [EXTRACTED]
  README.md → API testing/results/20261108T173522Z-fbc1f0d3/console.txt
- `Project Phase 2 design, scope, execution guidance, and result summary` --references--> `Observed isolated S02-02 existing-draft rerun: 1 passed in 1.16s`  [EXTRACTED]
  README.md → API testing/results/20261108T173605Z-0a164b81/console.txt
- `Project Phase 2 design, scope, execution guidance, and result summary` --references--> `Observed reverse-order live full run: 15 passed in 8.80s; S03, S02, S01; no failures, errors, or skips`  [EXTRACTED]
  README.md → API testing/results/20261108T173606Z-0e33c528/console.txt
- `Run metadata: 2026-11-08T17:35:22Z UTC, 15 tests, exit code 0, no failures/errors/skips, scope limited to three product API operations` --references--> `15 distinct API cases, not 31: repeated full runs and one isolated run test repeatability/order, not additional cases`  [EXTRACTED]
  API testing/results/20261108T173522Z-fbc1f0d3/run.json → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three WooCommerce API suites partition 15 distinct cases as 7 + 3 + 5** — readme_s01, readme_s02, readme_s03 [EXTRACTED 1.00]
- **Two full passing runs and one isolated passing case evidence repeatability without increasing the distinct-case count** — api_testing_results_20261108t173522z_fbc1f0d3_run, api_testing_results_20261108t173605z_0a164b81_run, api_testing_results_20261108t173606z_0e33c528_run [EXTRACTED 1.00]

## Communities (11 total, 3 thin omitted)

### Community 0 - "Product search tests"
Cohesion: 0.14
Nodes (4): assert_error(), assert_store_product(), test_product_detail(), test_list_products()

### Community 2 - "Supporting code and contracts"
Cohesion: 0.24
Nodes (3): api(), shop_config(), ShopAPI

### Community 3 - "Ownership and cleanup"
Cohesion: 0.25
Nodes (4): products(), is_owned_product(), ProductFactory, test_create_product()

### Community 5 - "Product search tests"
Cohesion: 0.33
Nodes (7): Base Choice Coverage: feasible normal base plus one-characteristic changes; counts 5, 3, and 5 across S01–S03, Boundary probes at per_page 1 and 100 are extra representatives, not new ISP blocks, S01 — GET /wc/store/v1/products list/search suite; 7 cases, S01 ISP blocks: per_page integer ≤0, 1–100, ≥101; search omitted, matching fixture, or nonmatching query, S02 — GET /wc/store/v1/products/{id} detail suite; 3 cases, S02 resource-state blocks: existing published, existing draft, verified absent; scoped to positive IDs of simple products, WooCommerce Store API product-list and product-detail endpoints

### Community 6 - "Ownership and cleanup"
Cohesion: 0.33
Nodes (6): Observed reverse-order live full run: 15 passed in 8.80s; S03, S02, S01; no failures, errors, or skips, Run metadata: 2026-11-08T17:36:06Z UTC, reversed suite order, 15 tests, exit code 0, no failures/errors/skips, Read-only audit: 25 disposable products created and deleted; zero remaining exact-run matches; zero credential matches; six source/reference files unchanged, Latest-run pointer selects reverse-order run 0e33c52878d54e09 with 15 tests and exit code 0, Each test case prepares its own disposable product and removes it afterward; cases do not depend on suite predecessors, Cleanup ownership guard verifies returned ID, exact name, and run marker; ambiguous POST is reconciled by exact unique SKU, never blindly retried

### Community 7 - "Supporting code and contracts"
Cohesion: 0.33
Nodes (5): Project Phase 2 design, scope, execution guidance, and result summary, Credential environment variable names SHOP_USER and SHOP_API_PASSWORD; optional SHOP_BASE_URL; values excluded, Input Space Partitioning: a deliberately limited input-domain model; no pair-wise or all-combinations claim, Store API price uses minor units: 100.00 THB is represented as price string 10000 with currency_minor_unit 2, Selected system: WooCommerce shop, ITCS386 Group 05 (OpenAI)

### Community 8 - "Execution and evidence"
Cohesion: 0.40
Nodes (5): Observed first live full run: 15 passed in 8.96s; S01, S02, S03; no failures, errors, or skips, Run metadata: 2026-11-08T17:35:22Z UTC, 15 tests, exit code 0, no failures/errors/skips, scope limited to three product API operations, Observed isolated S02-02 existing-draft rerun: 1 passed in 1.16s, Run metadata: 2026-11-08T17:36:05Z UTC, isolated S02-02, 1 test, exit code 0, no failures/errors/skips, 15 distinct API cases, not 31: repeated full runs and one isolated run test repeatability/order, not additional cases

### Community 9 - "Creation and publication"
Cohesion: 0.67
Nodes (3): WooCommerce Admin REST API product-creation endpoint, S03 — POST /wc/v3/products create suite; 5 cases, S03 ISP blocks: valid Group 05 credentials, absent credentials, wrong password; publish/default, draft representative, invalid status

## Knowledge Gaps
- **12 isolated node(s):** `Pinned Python dependencies: pytest 9.2.0, requests 2.34.2, selenium 4.52.0`, `Pytest configuration searches API testing and UI testing`, `Latest-run pointer selects reverse-order run 0e33c52878d54e09 with 15 tests and exit code 0`, `Selected system: WooCommerce shop, ITCS386 Group 05 (OpenAI)`, `WooCommerce Admin REST API product-creation endpoint` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 47 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProductFactory` connect `Ownership and cleanup` to `Product search tests`, `Supporting code and contracts`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `ShopAPI` (e.g. with `api()` and `shop_config()`) actually correct?**
  _`ShopAPI` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Pinned Python dependencies: pytest 9.2.0, requests 2.34.2, selenium 4.52.0`, `Pytest configuration searches API testing and UI testing`, `Latest-run pointer selects reverse-order run 0e33c52878d54e09 with 15 tests and exit code 0` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Product search tests` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Why does `ShopAPI` connect `Supporting code and contracts` to `Product search tests`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `test_create_product()` (e.g. with `.lookup()` and `.payload()`) actually correct?**
  _`test_create_product()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Ownership and cleanup` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._

## Build scope and evidence boundary

- Mixed corpus: all 18 detected project source/config/docs/dated-log files. Seven Python files use AST extraction; the 6 configuration/evidence files without AST nodes are covered by the host semantic pass along with all 5 documents/logs. Generated diagram authoring, QA and visualization outputs are excluded to avoid recursive self-analysis. No Phase 1 checkout or account workbook is scanned. XML is not a supported input type; its result counts are represented by the saved run JSON and full console logs.
- Structural code extraction: local Graphify 0.9.93. Semantic extraction: the running Codex session; no extra provider/API key. All assigned document lines were read.
- Token usage: unavailable in the host collaboration result, not measured zero. Graphify's numeric token placeholders below are not a billing measurement.
- Static EXTRACTED/INFERRED links do not establish runtime order. The custom nested HTML explains test lifecycle from source and marks external WooCommerce storage as conceptual/uninspected.
- AST references to 19 imported external dependencies were materialized as explicitly uninspected reference nodes. One parallel contains/calls pair was aggregated without dropping its additional relation/source-location metadata; see normalization.json. Normalized graph endpoints are verified separately in health.json.
- Run evidence is dated 9 November 2026 Bangkok, not a new live check. No API/SUT test execution, shop requests, credentials access, pushes, hooks or background watchers were used for this graph task. Local HTML interaction/geometry checks are separate artifact QA.
- graphify-out/ was written into the working tree. Cache/local interpreter metadata are ignored; review generated graph/report/HTML before any later commit.
