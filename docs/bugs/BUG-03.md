# BUG-03: Negative quantity accepted in cart

| Field | Value |
|---|---|
| Severity | High |
| Requirement | REQ-03 |
| Environment | Synthetic shop, `BUGS=3` |
| Detected by | test_req03_invalid_quantity_rejected[-1] |

## Steps to reproduce
1. Start the app with `BUGS=3`.
2. Login, POST /api/cart/items quantity -1.

## Expected result
422

## Actual result
201, negative line in cart

## Evidence
CI artifact `test-reports/bug-matrix/bug-3/` (JUnit XML, E2E screenshots on failure).
