"""Derive the test case list per requirement from data/requirements.csv and the test sources."""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports"
PATTERNS = [re.compile(r"def (test_req(\d{2})\w*)"), re.compile(r"check\('(req(\d{2})\w*)'")]


def scan():
    cases = []
    for f in sorted(ROOT.glob("tests/**/*")):
        if f.suffix not in (".py", ".groovy"):
            continue
        for pat in PATTERNS:
            for name, num in pat.findall(f.read_text()):
                cases.append({"req_id": f"REQ-{num}", "test_case": name, "file": str(f.relative_to(ROOT))})
    return cases


def main():
    OUT.mkdir(exist_ok=True)
    reqs = list(csv.DictReader((ROOT / "data" / "requirements.csv").open()))
    cases = scan()
    with (OUT / "test_cases.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["req_id", "title", "test_scope", "test_case", "file"])
        w.writeheader()
        for r in reqs:
            for c in (c for c in cases if c["req_id"] == r["req_id"]):
                w.writerow({**c, "title": r["title"], "test_scope": r["test_scope"]})
    md = ["# Test cases per requirement", "", "| Requirement | Scope | Test functions |", "|---|---|---|"]
    uncovered = []
    for r in reqs:
        n = sum(c["req_id"] == r["req_id"] for c in cases)
        uncovered += [r["req_id"]] if n == 0 else []
        md.append(f"| {r['req_id']} {r['title']} | {r['test_scope']} | {n} |")
    (OUT / "test_cases.md").write_text("\n".join(md) + "\n")
    print(f"{len(cases)} test functions mapped to {len(reqs)} requirements; uncovered: {uncovered or 'none'}")
    return 1 if uncovered else 0


if __name__ == "__main__":
    sys.exit(main())
