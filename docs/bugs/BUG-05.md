# BUG-05: Discount code SAVE10 is not applied

| Field | Value |
|---|---|
| Severity | Medium |
| Requirement | REQ-04 |
| Environment | Synthetic shop, `BUGS=5` |
| Detected by | test_req04_discount_applied |

## Steps to reproduce
1. Start the app with `BUGS=5`.
2. Add product 3, POST /api/orders with SAVE10.

## Expected result
total 44.91

## Actual result
total 49.90

## Evidence
CI artifact `test-reports/bug-matrix/bug-5/` (JUnit XML, E2E screenshots on failure).
