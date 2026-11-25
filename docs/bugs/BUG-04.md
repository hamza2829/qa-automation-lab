# BUG-04: Out-of-stock products can be added to cart

| Field | Value |
|---|---|
| Severity | High |
| Requirement | REQ-03 |
| Environment | Synthetic shop, `BUGS=4` |
| Detected by | test_req03_out_of_stock_rejected, test_req03_quantity_above_stock_rejected |

## Steps to reproduce
1. Start the app with `BUGS=4`.
2. Login, POST /api/cart/items product 4 (stock 0).

## Expected result
409 insufficient stock

## Actual result
201

## Evidence
CI artifact `test-reports/bug-matrix/bug-4/` (JUnit XML, E2E screenshots on failure).
