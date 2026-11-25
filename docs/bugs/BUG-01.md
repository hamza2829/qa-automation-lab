# BUG-01: Login accepts any password for a known user

| Field | Value |
|---|---|
| Severity | Critical |
| Requirement | REQ-02 |
| Environment | Synthetic shop, `BUGS=1` |
| Detected by | test_req02_login_wrong_password_rejected, test_req02_ui_login_wrong_password, req02_groovy_login_rejects_bad_password |

## Steps to reproduce
1. Start the app with `BUGS=1`.
2. POST /api/login with username alice and password wrong.

## Expected result
401 invalid credentials

## Actual result
200 with a token

## Evidence
CI artifact `test-reports/bug-matrix/bug-1/` (JUnit XML, E2E screenshots on failure).
