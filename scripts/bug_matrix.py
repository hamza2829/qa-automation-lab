"""Start the shop once per seeded bug and prove that at least one test fails for each bug."""
import json
import os
import subprocess
import sys
from pathlib import Path

from app.bugs import BUGS
from scripts.run_all import REPORTS, run_suites, wait_for

ROOT = Path(__file__).resolve().parent.parent


def run_case(bug, port):
    base = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port),
                             "--log-level", "warning"], cwd=ROOT, env={**os.environ, "BUGS": bug})
    try:
        wait_for(base)
        results, _ = run_suites(base, REPORTS / "bug-matrix" / f"bug-{bug or 'none'}")
    finally:
        proc.terminate()
        proc.wait(timeout=15)
    flat = [r for rs in results.values() for r in rs]
    return len(flat), [r["name"] for r in flat if r["status"] == "failed"]


def main():
    rows = []
    for i, bug in enumerate([""] + list(BUGS)):
        total, failed = run_case(bug, 8100 + i)
        desc = BUGS[bug][0] if bug else "baseline (no bug)"
        rows.append({"bug": bug or "none", "description": desc, "tests": total, "failed": len(failed),
                     "failing_tests": failed, "detected": bool(failed) if bug else not failed})
        print(f"bug {bug or 'none'}: {len(failed)}/{total} failed")
    detected = sum(r["detected"] for r in rows[1:])
    data = {"detected": detected, "total": len(BUGS), "baseline_clean": rows[0]["detected"], "rows": rows}
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "bug_matrix.json").write_text(json.dumps(data, indent=2))
    print(f"bug detection: {detected} of {len(BUGS)}, baseline clean: {data['baseline_clean']}")
    return 0 if detected == len(BUGS) and data["baseline_clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
