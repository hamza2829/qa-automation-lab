# BUG-06: Product list omits the last product

| Field | Value |
|---|---|
| Severity | High |
| Requirement | REQ-01 |
| Environment | Synthetic shop, `BUGS=6` |
| Detected by | test_req01_list_returns_all_products, test_req01_ui_shows_all_products, req01_groovy_products_complete |

## Steps to reproduce
1. Start the app with `BUGS=6`.
2. GET /api/products.

## Expected result
5 products

## Actual result
4 products, Headphones missing

## Evidence
CI artifact `test-reports/bug-matrix/bug-6/` (JUnit XML, E2E screenshots on failure).
