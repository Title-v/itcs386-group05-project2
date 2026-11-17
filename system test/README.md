# System Testing — ITCS386 Group 5

## Recorded execution status

| Case | Run | Steps | Result | Recorded order | Images |
|---|---|---:|---|---|---:|
| [ST-G05-01](ST-G05-01-R02-results.md) | R02 | 9 | Pass | 692, Completed, 360 THB | 16 |
| [ST-G05-02](ST-G05-02-R01-results.md) | R01 | 9 | Pass | 774, Processing, 300 THB | 18 |
| [ST-G05-03](ST-G05-03-R01-results.md) | R01 | 7 | Pass after correcting an input-operation error | 777, Completed, 225 THB | 14 |

All runs were executed on 17 November 2026 using Computer Use/browser UI, with a Group 5 staff session and a separate guest shopping session. These are recorded manual system-test results, not the separate automated UI testing deliverable.

## Documents

- [System test cases](system-test-cases.md): actual UI labels, inputs, expected/actual results and embedded screenshots.
- [Requirement traceability matrix](api-traceability-matrix.md): selected requirement coverage and exclusions.
- [API inventory](api-inventory.md): documented operations and cross-reference to the separate API suites.
- [Test 1 report](ST-G05-01-R02-results.md), [Test 2 report](ST-G05-02-R01-results.md), [Test 3 report](ST-G05-03-R01-results.md).
- [Screenshots](screenshots/): 48 original files; Test 3 includes two incident/cleanup captures.

## Important interpretation

- Test 3 is a seven-step **guest** scenario. Login, registration and My account history are not tested.
- Test 3's first address-clearing operation left text in the field and created order 776. That order was cancelled and stock restored. The empty-field check was repeated correctly; the final order is 777. The report retains both the incident and retest evidence.
- Test 2 deliberately ends with order 774 in Processing. Completing that order is not part of its case.
- New order / Processing order emails failed in the recorded runs; Completed order email failures were also observed where completion was tested. The reports document the server mail-function error. Email delivery is outside the assertions.
- Staff screenshots may include requester IP data; Safari captures include browser chrome. No passwords are recorded.
- A related UI action does not prove which REST endpoint was called. API execution evidence is maintained separately in the [API testing README](../API%20testing/README.md).

This overview was reconciled with the committed reports on 18 November 2026. No new live test was run during that document review.
