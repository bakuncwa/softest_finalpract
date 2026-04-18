# SOFTEST Final Exam – Group 4
## Automated Testing of OWASP Juice Shop

OWASP Juice Shop — a well-known intentionally vulnerable web application used for security training, CTF competitions, and awareness demos. A deliberately insecure Node.js/Angular e-commerce app that contains vulnerabilities from the OWASP Top Ten (SQL injection, XSS, broken auth, etc.) and many more — used for learning and practicing web security.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Node.js + TypeScript (`server.ts`, `routes/`, `models/`) |
| **Frontend** | Angular (`frontend/src/`) |
| **Database** | SQLite via Sequelize ORM + optional MongoDB |
| **Views** | Pug / Handlebars templates |
| **Key directories** | `routes/` — 50+ Express route handlers, many with intentional vulnerabilities |
| | `models/` — Sequelize ORM models (User, Product, Basket, etc.) |
| | `data/` — Data seeding, static files, chatbot data |
| | `lib/` — Utilities including `insecurity.ts` (JWT/crypto helpers) |
| | `config/` — Multiple configuration profiles (CTF, tutorial, default, etc.) |
| | `ftp/` — Intentionally exposed "FTP" files with secrets and easter eggs |
| | `test/` — API, server, and Cypress e2e tests |
| | `frontend/` — Full Angular app (~40MB) |

---

## Test Automation Framework

| Component | Details |
|-----------|---------|
| **Selenium WebDriver** | Python — 34 functional & security test cases |
| **Apache JMeter 5.6** | Performance & security load test plan (3 thread groups) |
| **AUT** | OWASP Juice Shop `http://localhost:3000` |
| **Browser** | Google Chrome (headed or headless) |

### Run Commands

```bash
# Install dependencies
pip install selenium webdriver-manager requests

# Run Selenium suite (headed)
python main.py

# Run Selenium suite (headless)
python main.py --headless

# Run Selenium + JMeter
python main.py --jmeter
```

Output files generated per run:
- `summary.txt` — pass/fail table for all TCs + JMeter results
- `error_logs.txt` — detailed execution log (overwritten each run)

---

## Selenium Test Results

> Last run: **2026-04-18** &nbsp;|&nbsp; Pass rate: **26/34 (76.5%)**

| TC | Result | Description | Module |
|----|--------|-------------|--------|
| TC-001 | PASS | Successful User Registration | User Auth |
| TC-002 | PASS | Login with Valid Credentials | User Auth |
| TC-003 | PASS | Duplicate Email Registration | User Auth |
| TC-004 | FAIL | Login with Incorrect Password | User Auth |
| TC-005 | PASS | Repetitive Registration – Password Mismatch Bypass | User Auth |
| TC-006 | PASS | Secure Logout | User Auth |
| TC-007 | PASS | Valid Keyword Search | Product Browsing |
| TC-008 | PASS | Product Detail Modal View | Product Browsing |
| TC-009 | PASS | Invalid Search Query – No Results | Product Browsing |
| TC-010 | PASS | Item Category Filtering | Product Browsing |
| TC-011 | PASS | Administrative Section Access | Product Browsing |
| TC-012 | FAIL | Add Single Item to Basket | Shopping Cart |
| TC-013 | PASS | Increase Item Quantity in Basket | Shopping Cart |
| TC-014 | PASS | Remove Item from Basket | Shopping Cart |
| TC-015 | FAIL | Basket Data Persistence | Shopping Cart |
| TC-016 | PASS | View Other User's Basket (IDOR) | Shopping Cart |
| TC-017 | PASS | Zero-Star Feedback Submission | Shopping Cart |
| TC-018 | FAIL | Verify Total Calculation at Checkout | Checkout |
| TC-019 | FAIL | Add New Address Validation | Checkout |
| TC-020 | FAIL | Delivery Speed Price Added to Total | Checkout |
| TC-021 | FAIL | Coupon Code Validation | Checkout |
| TC-022 | PASS | Order History Accuracy | Orders & Profile |
| TC-023 | PASS | Upload Profile Picture | Orders & Profile |
| TC-024 | PASS | Update Username / Profile Settings | Orders & Profile |
| TC-025 | FAIL | Write a Review via Order History | Orders & Profile |
| TC-026 | PASS | DOM XSS via Search Bar | Security |
| TC-027 | PASS | SQL Injection – Admin Login Bypass | Security |
| TC-028 | PASS | SQL Injection – Login as Specific User | Security |
| TC-029 | PASS | SQL Injection via URL – Credential Dump | Security |
| TC-030 | PASS | Reflected XSS via Search Bar | Security |
| TC-031 | PASS | Prompt Injection – Chatbot Coupon | Security |
| TC-032 | PASS | Vulnerable Components – Kill Chatbot | Security |
| TC-033 | PASS | Sensitive Data Exposure – /metrics Endpoint | Security |
| TC-034 | PASS | Sensitive Data Exposure – FTP Directory | Security |

---

## JMeter Performance / Security Results

> 3 thread groups — Login load, Product search, Smoke/Security

| Status | Sampler | Pass/Total | Avg (ms) |
|--------|---------|-----------|---------|
| PASS | POST /rest/user/login — valid credentials | 10/10 | ~90 |
| PASS | POST /rest/user/login — SQL injection bypass | 10/10 | ~85 |
| PASS | GET /rest/products/search — keyword: apple | 15/15 | ~40 |
| PASS | GET /metrics — Prometheus exposure (TC-033) | 1/1 | ~5 |
| PASS | GET / — Application Health Check | 1/1 | ~10 |
| FAIL | GET /rest/products/search — UNION SQLi (TC-029) | 0/15 | — |
| FAIL | GET /ftp/ — Exposed FTP directory (TC-034) | 0/1 | — |
| FAIL | GET /api/Users — Unauthenticated enumeration | 0/1 | — |

> **Note on JMeter "failures":** All 3 failing samplers reflect *expected* security behaviour — the UNION SQLi crashes the search endpoint (HTTP 500 confirming the vulnerability), `/ftp/` closes the connection on non-browser clients, and `/api/Users` correctly returns 401 for unauthenticated access. These are intentional outcomes, not application regressions.

---

## Bug / Defect Report — OWASP Juice Shop — After Testing

| Bug/Defect ID | Severity | Linked Test Case | Summary | Status |
|---------------|----------|-----------------|---------|--------|
| **WORKFLOW 1 — User Registration & Login** | | | | |
| BUG-001 | Minor | TC-004 | Login error snack-bar obscured by language-change notification on first load — invalid-password message not captured | In Progress |
| **WORKFLOW 2 — Product Browsing & Search** | | | | |
| — | — | — | No defects recorded — all test cases passed | — |
| **WORKFLOW 3 — Shopping Cart Management** | | | | |
| BUG-002 | Major | TC-012 | Add to Basket snack-bar confirmation not consistently rendered within timeout — item addition unverifiable | In Progress |
| BUG-003 | Major | TC-015 | Basket contents not persisted after navigating away and returning — basket found empty on reload | In Progress |
| **WORKFLOW 4 — Checkout & Payment** | | | | |
| BUG-004 | Minor | TC-018 | Total price DOM element ambiguous — selector matches parent container and concatenates all child price values into unparseable string | In Progress |
| BUG-005 | Major | TC-019 | Checkout button intercepted by overlay — address selection step unreachable | In Progress |
| BUG-006 | Major | TC-020 | Delivery speed selection button intercepted — delivery pricing step unreachable | In Progress |
| BUG-007 | Minor | TC-021 | Submitting invalid coupon code returns HTTP 500 instead of a client-facing validation error | In Progress |
| **WORKFLOW 5 — Order History & Profile** | | | | |
| BUG-008 | Minor | TC-025 | Review input field inside product detail modal not locatable — selector times out across multiple CSS and placeholder strategies | In Progress |
| **WORKFLOW 6 — Security Vulnerabilities** | | | | |
| — | — | — | No defects recorded — all test cases passed | — |