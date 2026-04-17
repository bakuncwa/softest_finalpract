"""
════════════════════════════════════════════════════════════════════════════════
SOFTEST Final Exam – Group 4
Application Under Test : OWASP Juice Shop  (http://localhost:3000)
Automation Framework   : Selenium WebDriver (Python)  +  Apache JMeter (perf)
File                   : main.py — entry-point; runs all 34 tests + JMeter plan.

Usage
─────
    python main.py                   # headed browser, no JMeter
    python main.py --headless        # headless browser, no JMeter
    python main.py --jmeter          # headed + run JMeter performance plan
    python main.py --headless --jmeter

Prerequisites
─────────────
    pip install selenium webdriver-manager requests
    Chrome + ChromeDriver (auto-managed by webdriver-manager)
    Apache JMeter 5.x on PATH  (only needed for --jmeter flag)
════════════════════════════════════════════════════════════════════════════════
"""

import datetime
import sys
from typing import Optional

from test_scripts import (
    LOG_FILE,
    create_driver,
    logger,
    run_jmeter,
    # MODULE 2.1 — Registration & Login
    test_tc001_successful_registration,
    test_tc002_login_valid_credentials,
    test_tc003_duplicate_email_registration,
    test_tc004_login_incorrect_password,
    test_tc005_repetitive_registration_bypass,
    test_tc006_secure_logout,
    # MODULE 2.2 — Product Browsing & Search
    test_tc007_valid_keyword_search,
    test_tc008_product_detail_modal,
    test_tc009_invalid_search_query,
    test_tc010_item_category_filtering,
    test_tc011_admin_section_access,
    # MODULE 2.3 — Shopping Cart Management
    test_tc012_add_single_item_to_basket,
    test_tc013_increase_item_quantity,
    test_tc014_remove_item_from_basket,
    test_tc015_basket_data_persistence,
    test_tc016_view_other_users_basket_idor,
    test_tc017_zero_star_feedback,
    # MODULE 2.4 — Checkout & Payment
    test_tc018_verify_total_calculation,
    test_tc019_add_new_address_validation,
    test_tc020_delivery_speed_price,
    test_tc021_coupon_validation,
    # MODULE 2.5 — Order History & Profile Management
    test_tc022_order_history_accuracy,
    test_tc023_upload_profile_picture,
    test_tc024_update_profile_settings,
    test_tc025_write_review_in_order_history,
    # MODULE 2.6 — Security Vulnerabilities
    test_tc026_dom_xss_search,
    test_tc027_sql_injection_admin_login,
    test_tc028_sql_injection_specific_user,
    test_tc029_sql_injection_via_url,
    test_tc030_reflected_xss_search,
    test_tc031_prompt_injection_chatbot,
    test_tc032_vulnerable_components_kill_chatbot,
    test_tc033_sensitive_data_exposed_metrics,
    test_tc034_sensitive_data_exposed_ftp,
)

# ──────────────────────────────────────────────────────────────────────────────
# Test suite registry
#
# Each entry is a dict with:
#   fn           – test function reference
#   tc_id        – test case ID string
#   workflow     – module / workflow label
#   needs_driver – False for pure-requests tests (TC-029, TC-033)
#
# Tests marked needs_driver=False are called with driver=None.
# All others receive a fresh Chrome WebDriver instance.
# ──────────────────────────────────────────────────────────────────────────────
TEST_SUITE = [
    # ── MODULE 2.1 ────────────────────────────────────────────────────────────
    {"fn": test_tc001_successful_registration,
     "tc_id": "TC-001", "workflow": "User Registration & Login",
     "needs_driver": True},
    {"fn": test_tc002_login_valid_credentials,
     "tc_id": "TC-002", "workflow": "User Registration & Login",
     "needs_driver": True},
    {"fn": test_tc003_duplicate_email_registration,
     "tc_id": "TC-003", "workflow": "User Registration & Login",
     "needs_driver": True},
    {"fn": test_tc004_login_incorrect_password,
     "tc_id": "TC-004", "workflow": "User Registration & Login",
     "needs_driver": True},
    {"fn": test_tc005_repetitive_registration_bypass,
     "tc_id": "TC-005", "workflow": "User Registration & Login",
     "needs_driver": True},
    {"fn": test_tc006_secure_logout,
     "tc_id": "TC-006", "workflow": "User Registration & Login",
     "needs_driver": True},
    # ── MODULE 2.2 ────────────────────────────────────────────────────────────
    {"fn": test_tc007_valid_keyword_search,
     "tc_id": "TC-007", "workflow": "Product Browsing & Search",
     "needs_driver": True},
    {"fn": test_tc008_product_detail_modal,
     "tc_id": "TC-008", "workflow": "Product Browsing & Search",
     "needs_driver": True},
    {"fn": test_tc009_invalid_search_query,
     "tc_id": "TC-009", "workflow": "Product Browsing & Search",
     "needs_driver": True},
    {"fn": test_tc010_item_category_filtering,
     "tc_id": "TC-010", "workflow": "Product Browsing & Search",
     "needs_driver": True},
    {"fn": test_tc011_admin_section_access,
     "tc_id": "TC-011", "workflow": "Product Browsing & Search",
     "needs_driver": True},
    # ── MODULE 2.3 ────────────────────────────────────────────────────────────
    {"fn": test_tc012_add_single_item_to_basket,
     "tc_id": "TC-012", "workflow": "Shopping Cart Management",
     "needs_driver": True},
    {"fn": test_tc013_increase_item_quantity,
     "tc_id": "TC-013", "workflow": "Shopping Cart Management",
     "needs_driver": True},
    {"fn": test_tc014_remove_item_from_basket,
     "tc_id": "TC-014", "workflow": "Shopping Cart Management",
     "needs_driver": True},
    {"fn": test_tc015_basket_data_persistence,
     "tc_id": "TC-015", "workflow": "Shopping Cart Management",
     "needs_driver": True},
    {"fn": test_tc016_view_other_users_basket_idor,
     "tc_id": "TC-016", "workflow": "Shopping Cart Management",
     "needs_driver": True},
    {"fn": test_tc017_zero_star_feedback,
     "tc_id": "TC-017", "workflow": "Shopping Cart Management",
     "needs_driver": True},
    # ── MODULE 2.4 ────────────────────────────────────────────────────────────
    {"fn": test_tc018_verify_total_calculation,
     "tc_id": "TC-018", "workflow": "Checkout & Payment",
     "needs_driver": True},
    {"fn": test_tc019_add_new_address_validation,
     "tc_id": "TC-019", "workflow": "Checkout & Payment",
     "needs_driver": True},
    {"fn": test_tc020_delivery_speed_price,
     "tc_id": "TC-020", "workflow": "Checkout & Payment",
     "needs_driver": True},
    {"fn": test_tc021_coupon_validation,
     "tc_id": "TC-021", "workflow": "Checkout & Payment",
     "needs_driver": True},
    # ── MODULE 2.5 ────────────────────────────────────────────────────────────
    {"fn": test_tc022_order_history_accuracy,
     "tc_id": "TC-022", "workflow": "Order History & Profile Management",
     "needs_driver": True},
    {"fn": test_tc023_upload_profile_picture,
     "tc_id": "TC-023", "workflow": "Order History & Profile Management",
     "needs_driver": True},
    {"fn": test_tc024_update_profile_settings,
     "tc_id": "TC-024", "workflow": "Order History & Profile Management",
     "needs_driver": True},
    {"fn": test_tc025_write_review_in_order_history,
     "tc_id": "TC-025", "workflow": "Order History & Profile Management",
     "needs_driver": True},
    # ── MODULE 2.6 ────────────────────────────────────────────────────────────
    {"fn": test_tc026_dom_xss_search,
     "tc_id": "TC-026", "workflow": "Security Vulnerabilities",
     "needs_driver": True},
    {"fn": test_tc027_sql_injection_admin_login,
     "tc_id": "TC-027", "workflow": "Security Vulnerabilities",
     "needs_driver": True},
    {"fn": test_tc028_sql_injection_specific_user,
     "tc_id": "TC-028", "workflow": "Security Vulnerabilities",
     "needs_driver": True},
    {"fn": test_tc029_sql_injection_via_url,
     "tc_id": "TC-029", "workflow": "Security Vulnerabilities",
     "needs_driver": False},   # uses requests — no browser needed
    {"fn": test_tc030_reflected_xss_search,
     "tc_id": "TC-030", "workflow": "Security Vulnerabilities",
     "needs_driver": True},
    {"fn": test_tc031_prompt_injection_chatbot,
     "tc_id": "TC-031", "workflow": "Security Vulnerabilities",
     "needs_driver": True},
    {"fn": test_tc032_vulnerable_components_kill_chatbot,
     "tc_id": "TC-032", "workflow": "Security Vulnerabilities",
     "needs_driver": True},
    {"fn": test_tc033_sensitive_data_exposed_metrics,
     "tc_id": "TC-033", "workflow": "Security Vulnerabilities",
     "needs_driver": False},   # uses requests — no browser needed
    {"fn": test_tc034_sensitive_data_exposed_ftp,
     "tc_id": "TC-034", "workflow": "Security Vulnerabilities",
     "needs_driver": True},
]


# ──────────────────────────────────────────────────────────────────────────────
# Summary writer
# ──────────────────────────────────────────────────────────────────────────────
def _write_summary(
    selenium_results: list,
    jmeter_result: Optional[dict],
    total_seconds: float,
) -> None:
    passed  = [r for r in selenium_results if r["status"] == "PASS"]
    failed  = [r for r in selenium_results if r["status"] == "FAIL"]
    errored = [r for r in selenium_results if r["status"] == "ERROR"]
    pass_rt = (len(passed) / len(selenium_results) * 100) if selenium_results else 0.0

    sep  = "=" * 72
    dash = "─" * 72

    # Group results by workflow
    workflow_map: dict[str, list] = {}
    for r in selenium_results:
        wf = r.get("workflow", "Unknown")
        workflow_map.setdefault(wf, []).append(r)

    lines = [
        "",
        sep,
        "  SOFTEST FINAL EXAM – GROUP 4 | COMPLETE TEST EXECUTION SUMMARY",
        sep,
        f"  Timestamp              : {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        f"  AUT                    : OWASP Juice Shop  (http://localhost:3000)",
        f"  Automation Frameworks  : Selenium WebDriver (Python) + JMeter (perf)",
        dash,
        f"  Selenium Tests Run     : {len(selenium_results)}",
        f"  PASSED                 : {len(passed)}",
        f"  FAILED                 : {len(failed)}",
        f"  ERRORS                 : {len(errored)}",
        f"  Pass Rate              : {pass_rt:.1f}%",
        f"  Total Execution Time   : {total_seconds:.2f} s",
    ]

    if jmeter_result:
        lines += [
            dash,
            f"  JMeter Result          : {jmeter_result['status']}",
            f"  JMeter Message         : {jmeter_result['message']}",
        ]

    lines += [dash, "  DETAILED RESULTS BY WORKFLOW", dash]

    for wf, results in workflow_map.items():
        wf_pass = sum(1 for r in results if r["status"] == "PASS")
        lines.append(f"  ▸ {wf}  ({wf_pass}/{len(results)} passed)")
        for r in results:
            icon = "✓" if r["status"] == "PASS" else ("✗" if r["status"] == "FAIL" else "!")
            lines.append(
                f"    [{icon}] {r['test_id']:8s} | {r['status']:5s} | "
                f"{r['duration_sec']:5.2f}s | {r['description']}"
            )
            if r["status"] != "PASS":
                for i, seg in enumerate(r["message"].split("\n")):
                    prefix = "           └─ " if i == 0 else "              "
                    lines.append(f"{prefix}{seg}")

    verdict = (
        "ALL SELENIUM TESTS PASSED"
        if not failed and not errored
        else f"{len(failed)} FAILED  |  {len(errored)} ERROR(S)"
    )
    lines += [dash, f"  VERDICT  :  {verdict}", sep, ""]

    block = "\n".join(lines)
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(block)
    print(block)


def _write_simple_summary(
    selenium_results: list,
    total_seconds: float,
    jmeter_result: Optional[dict] = None,
) -> None:
    """Write a plain pass/fail summary to summary.txt (overwritten each run)."""
    passed  = [r for r in selenium_results if r["status"] == "PASS"]
    failed  = [r for r in selenium_results if r["status"] != "PASS"]
    total   = len(selenium_results)
    rate    = (len(passed) / total * 100) if total else 0.0

    W = 62
    lines = [
        "=" * W,
        "  SOFTEST Final Exam – Group 4 | Test Summary",
        "=" * W,
        f"  Run         : {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        f"  AUT         : OWASP Juice Shop  (http://localhost:3000)",
        f"  Total TCs   : {total}",
        f"  Passed      : {len(passed)}",
        f"  Failed      : {len(failed)}",
        f"  Pass Rate   : {rate:.1f}%",
        f"  Duration    : {total_seconds:.1f}s",
        "-" * W,
        f"  {'TC':<8}  {'Result':<6}  Description",
        "-" * W,
    ]
    for r in selenium_results:
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        lines.append(f"  {r['test_id']:<8}  {icon:<6}  {r['description']}")
    lines += [
        "=" * W,
        f"  SELENIUM VERDICT: {len(passed)} PASSED  |  {len(failed)} FAILED",
        "=" * W,
        "",
    ]

    # ── JMeter section ────────────────────────────────────────────────────────
    if jmeter_result:
        samplers = jmeter_result.get("samplers", [])
        jm_total  = sum(s["total"]  for s in samplers)
        jm_passed = sum(s["passed"] for s in samplers)
        jm_failed = sum(s["failed"] for s in samplers)
        jm_rate   = (jm_passed / jm_total * 100) if jm_total else 0.0

        lines += [
            "=" * W,
            "  Apache JMeter Performance / Security Results",
            "=" * W,
            f"  Status      : {jmeter_result.get('status', 'N/A')}",
            f"  Message     : {jmeter_result.get('message', '')}",
            f"  Requests    : {jm_total}  ({jm_passed} passed, {jm_failed} failed)",
            f"  Pass Rate   : {jm_rate:.1f}%",
            "-" * W,
            f"  {'Status':<6}  {'Pass/Total':<11}  {'Avg ms':<7}  Sampler",
            "-" * W,
        ]
        for s in samplers:
            icon = "PASS" if s["status"] == "PASS" else "FAIL"
            ratio = f"{s['passed']}/{s['total']}"
            label = s["label"][:46]
            lines.append(
                f"  {icon:<6}  {ratio:<11}  {s['avg_ms']:<7}  {label}"
            )
        lines += [
            "=" * W,
            f"  JMETER VERDICT: {jm_passed} PASSED  |  {jm_failed} FAILED",
            "=" * W,
            "",
        ]
    else:
        lines += [
            "=" * W,
            "  JMeter: NOT RUN  (add --jmeter flag to enable)",
            "=" * W,
            "",
        ]

    summary_path = "summary.txt"
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"\n[summary.txt written → {summary_path}]")


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    headless     = "--headless" in sys.argv
    run_jmeter_f = "--jmeter"   in sys.argv

    logger.info("=" * 72)
    logger.info("  SOFTEST Final Exam – Group 4 | Automated Test Run Starting")
    logger.info(f"  Date/Time   : {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    logger.info(f"  AUT         : OWASP Juice Shop  (http://localhost:3000)")
    logger.info(f"  Browser     : Google Chrome ({'headless' if headless else 'headed'})")
    logger.info(f"  Selenium TC : {len(TEST_SUITE)}")
    logger.info(f"  JMeter      : {'YES – jmeter_test_plan.jmx' if run_jmeter_f else 'NO (pass --jmeter to enable)'}")
    logger.info("=" * 72)

    selenium_results: list = []
    suite_start = datetime.datetime.now()

    for entry in TEST_SUITE:
        test_fn      = entry["fn"]
        tc_id        = entry["tc_id"]
        workflow     = entry["workflow"]
        needs_driver = entry["needs_driver"]
        driver       = None

        try:
            if needs_driver:
                logger.info(f"  Launching browser for {tc_id} …")
                driver = create_driver(headless=headless)

            result = test_fn(driver)
            result["workflow"] = workflow
            selenium_results.append(result)

        except Exception as exc:
            logger.exception(f"Fatal error running {tc_id}: {exc}")
            selenium_results.append({
                "test_id":      tc_id,
                "description":  tc_id,
                "workflow":     workflow,
                "status":       "ERROR",
                "message":      str(exc),
                "duration_sec": 0.0,
            })
        finally:
            if driver:
                driver.quit()
                logger.info(f"  Browser closed after {tc_id}.")

    total_selenium = (datetime.datetime.now() - suite_start).total_seconds()

    # ── Optional JMeter run ────────────────────────────────────────────────────
    jmeter_result = None
    if run_jmeter_f:
        logger.info("")
        logger.info("─" * 72)
        logger.info("  Starting Apache JMeter performance test …")
        jmeter_result = run_jmeter(
            jmx_path="jmeter_test_plan.jmx",
            results_dir="jmeter_results",
        )
        logger.info(f"  JMeter status : {jmeter_result['status']}")
        logger.info("─" * 72)

    total_time = (datetime.datetime.now() - suite_start).total_seconds()
    _write_summary(selenium_results, jmeter_result, total_time)
    _write_simple_summary(selenium_results, total_time, jmeter_result)

    failures = [r for r in selenium_results if r["status"] != "PASS"]
    if jmeter_result and jmeter_result["status"] == "FAIL":
        failures.append(jmeter_result)

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()