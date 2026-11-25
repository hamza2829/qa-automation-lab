"""Run API, E2E and Groovy suites against the shop and build the Markdown test report."""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
SUITES = ("api", "e2e", "groovy")
REQ_RE = re.compile(r"req(\d{2})")


def wait_for(base, timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if requests.get(base + "/api/health", timeout=2).ok:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"app not reachable at {base}")


def parse_junit(path, suite):
    out = []
    for tc in ET.parse(path).getroot().iter("testcase"):
        tags = {c.tag for c in tc}
        status = "failed" if tags & {"failure", "error"} else "skipped" if "skipped" in tags else "passed"
        out.append({"suite": suite, "name": tc.get("name"), "status": status, "time": float(tc.get("time") or 0)})
    return out


def run_pytest(suite, base, out, allure=None):
    junit = out / f"junit-{suite}.xml"
    cmd = [sys.executable, "-m", "pytest", str(ROOT / "tests" / suite), "-q", "--junitxml", str(junit)]
    if allure:
        cmd += ["--alluredir", str(allure)]
    if suite == "e2e":
        cmd += ["--browser", "chromium", "--screenshot", "only-on-failure", "--output", str(out / "e2e-artifacts")]
    subprocess.run(cmd, cwd=ROOT, env={**os.environ, "BASE_URL": base}, stdout=subprocess.DEVNULL)
    if not junit.exists():
        return [{"suite": suite, "name": f"{suite}_collection", "status": "failed", "time": 0}]
    return parse_junit(junit, suite)


def run_groovy(base):
    groovy = shutil.which("groovy")
    if not groovy:
        return [{"suite": "groovy", "name": "groovy_runtime_missing", "status": "skipped", "time": 0}]
    out = []
    for script in sorted((ROOT / "tests" / "groovy").glob("*.groovy")):
        t = time.perf_counter()
        p = subprocess.run([groovy, str(script)], cwd=ROOT, env={**os.environ, "BASE_URL": base},
                           capture_output=True, text=True)
        lines = [ln for ln in p.stdout.splitlines() if ln.startswith(("PASS ", "FAIL "))]
        dt = round((time.perf_counter() - t) / max(len(lines), 1), 3)
        out += [{"suite": "groovy", "name": ln.split()[1].rstrip(":"),
                 "status": "passed" if ln.startswith("PASS") else "failed", "time": dt} for ln in lines]
        if p.returncode and not any(ln.startswith("FAIL") for ln in lines):
            out.append({"suite": "groovy", "name": script.stem, "status": "failed", "time": dt})
    return out


def run_suites(base, out, suites=SUITES, allure=None):
    out.mkdir(parents=True, exist_ok=True)
    results, durations = {}, {}
    for s in suites:
        t = time.perf_counter()
        results[s] = run_groovy(base) if s == "groovy" else run_pytest(s, base, out, allure)
        durations[s] = round(time.perf_counter() - t, 2)
    return results, durations


def build_report(out=REPORTS):
    results, durations = [], {}
    for s in SUITES:
        f = out / f"results_{s}.json"
        if f.exists():
            d = json.loads(f.read_text())
            results += d["results"]
            durations[s] = d["duration_s"]
    count = lambda rs, st: sum(r["status"] == st for r in rs)
    summary = {"total": len(results), "passed": count(results, "passed"), "failed": count(results, "failed"),
               "skipped": count(results, "skipped"), "duration_s": round(sum(durations.values()), 2),
               "suites": {s: {"tests": sum(r["suite"] == s for r in results), "duration_s": durations[s]}
                          for s in durations}}
    md = ["# Test report (synthetic shop)", "",
          f"Total: {summary['total']} | Passed: {summary['passed']} | Failed: {summary['failed']} | "
          f"Skipped: {summary['skipped']} | Runtime: {summary['duration_s']} s", "",
          "## Per suite", "", "| Suite | Passed | Failed | Skipped | Runtime (s) |", "|---|---|---|---|---|"]
    for s in durations:
        rs = [r for r in results if r["suite"] == s]
        md.append(f"| {s} | {count(rs, 'passed')} | {count(rs, 'failed')} | {count(rs, 'skipped')} | {durations[s]} |")
    md += ["", "## Per requirement", "", "| Requirement | Passed | Failed | Status |", "|---|---|---|---|"]
    for req in csv.DictReader((ROOT / "data" / "requirements.csv").open()):
        rs = [r for r in results if (m := REQ_RE.search(r["name"] or "")) and f"REQ-{m.group(1)}" == req["req_id"]]
        status = "PASS" if rs and not count(rs, "failed") else "FAIL" if rs else "NO TESTS"
        md.append(f"| {req['req_id']} {req['title']} | {count(rs, 'passed')} | {count(rs, 'failed')} | {status} |")
    matrix = out / "bug_matrix.json"
    if matrix.exists():
        m = json.loads(matrix.read_text())
        summary["bugs_detected"], summary["bugs_total"] = m["detected"], m["total"]
        md += ["", "## Bug detection matrix", "", "| Bug | Description | Failing tests | Detected |", "|---|---|---|---|"]
        md += [f"| {r['bug']} | {r['description']} | {r['failed']} | {'yes' if r['detected'] else 'NO'} |" for r in m["rows"]]
    failed = [r for r in results if r["status"] == "failed"]
    if failed:
        md += ["", "## Failed tests", ""] + [f"- {r['suite']}: {r['name']}" for r in failed]
    out.mkdir(exist_ok=True)
    (out / "test_report.md").write_text("\n".join(md) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", default=os.getenv("BASE_URL", "http://127.0.0.1:8000"))
    p.add_argument("--suites", default=",".join(SUITES))
    p.add_argument("--report-only", action="store_true")
    p.add_argument("--wait", action="store_true")
    a = p.parse_args(argv)
    if a.wait:
        wait_for(a.base_url)
    if not a.report_only:
        results, durations = run_suites(a.base_url, REPORTS, a.suites.split(","), REPORTS / "allure-results")
        for s, rs in results.items():
            (REPORTS / f"results_{s}.json").write_text(json.dumps({"results": rs, "duration_s": durations[s]}))
    summary = build_report()
    print(json.dumps(summary))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
