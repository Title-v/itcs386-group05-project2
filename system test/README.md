# System Testing — ITCS386 Group 5

## Current results

All three scenarios were rerun on **19 November 2026 (Asia/Bangkok)**. Screenshots capture only webpage content: no browser tabs, URL bar or mouse pointer.

| Case | Run | Steps | Result | Recorded order | Images |
|---|---|---:|---|---|---:|
| [ST-G05-01](ST-G05-01-results.md) | R04 | 9 | Pass | 1252, Completed, 360 THB | 20 |
| [ST-G05-02](ST-G05-02-results.md) | R02 | 9 | Pass | 1260, Processing, 300 THB | 21 |
| [ST-G05-03](ST-G05-03-results.md) | R02 | 7 | Pass | 1274, Completed, 225 THB | 15 |

There are **56 current screenshots**. Every product has evidence from Add new product before input, completed inputs before Publish, and the saved result. Tests 1–2 verify creation; Test 3 creates at 250 THB before changing the regular price to 225 THB.

## Documents

- [System test cases](system-test-cases.md): current plans, UI inputs, expected/actual results and screenshots.
- [Requirement traceability matrix](api-traceability-matrix.md): 14 requirements actually checked; no untested rows.
- [API inventory](api-inventory.md): reference operations, separate from system-test coverage.
- [ST-G05-01 report](ST-G05-01-results.md), [ST-G05-02 report](ST-G05-02-results.md), [ST-G05-03 report](ST-G05-03-results.md).
- [Screenshots](screenshots/): current page-only evidence.

## Interpretation

Staff and guest sessions were separated by logout/login in the in-app browser. These are manual system tests, not the separate automated UI testing deliverable. All customer purchases were guest COD test orders.

Test 2 ends with order 1260 in Processing and stock 1; completion is not a step of that case. Test 3's current run verified the empty address before submission, then created only the corrected successful order. Order statuses refer to the recorded runs.

Mail-function errors appeared in staff order notes; no email-delivery success is claimed. No passwords appear in the reports. Browser chrome and mouse-pointer overlays are absent; normal page focus outlines/carets may remain.

Only the latest run for each case is kept in this folder: ST-G05-01 R04, ST-G05-02 R02 and ST-G05-03 R02.
