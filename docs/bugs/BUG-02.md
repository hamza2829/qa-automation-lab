# BUG-02: Cart line total ignores quantity

| Field | Value |
|---|---|
| Severity | High |
| Requirement | REQ-03 |
| Environment | Synthetic shop, `BUGS=2` |
| Detected by | test_req03_total_uses_quantity[2], [5], test_req03_ui_cart_total_with_quantity |

## Steps to reproduce
1. Start the app with `BUGS=2`.
2. Login, POST /api/cart/items product 1 quantity 2.

## Expected result
total 39.98

## Actual result
total 19.99

## Evidence
CI artifact `test-reports/bug-matrix/bug-2/` (JUnit XML, E2E screenshots on failure).
