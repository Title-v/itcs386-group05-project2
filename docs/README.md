# Supporting Document Status

Reviewed on **18 November 2026 (Asia/Bangkok)**. These exports explain earlier source snapshots; they are not the authoritative current test results.

| Artifact | Snapshot / limitation | Current source |
|---|---|---|
| [API map](api-testing-map.html) | Built 11 Nov 2026; describes 17 cases but its evidence node points to the 11 Nov 23:10 Bangkok run | [API README](../API%20testing/README.md) and [latest-run metadata](../API%20testing/results/latest-run.json) |
| [API map PDF](api-testing-map.pdf) | Static export; not regenerated during this review. Do not use it to establish the latest run date | [API README](../API%20testing/README.md) |
| [README preview](api-testing-readme-preview.html) | Historical draft describing 15 cases and 9 Nov run evidence; does not include the later two detail cases | [Current API design and 17-case results](../API%20testing/README.md) |
| [Graphify report](../graphify-out/GRAPH_REPORT.md) and generated graph files | Historical 15-case source snapshot dated 9–10 Nov; stale references to latest-run are relative to that snapshot | [Current repository overview](../README.md) and [API README](../API%20testing/README.md) |

The map/PDF/preview were not rebuilt or relabeled as new execution evidence. Keep their original historical content and dates when referring to them. Some legacy explanatory exports contain Thai; current test-case/report Markdown is maintained in English.

## Current system-test evidence

Use the [system-testing overview](../system%20test/README.md), not these API-only exports, for the three manual cases, recorded results and 48 screenshots.

## Remaining deliverables

The repository review found no committed automated UI test scripts or K6 performance scripts/results. Passing API and manual system tests does not establish completion of those two deliverables.
