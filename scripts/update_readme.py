"""Write measured CI numbers from reports/summary.json into the README results block."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(reports=ROOT / "reports"):
    s = json.loads((Path(reports) / "summary.json").read_text())
    rows = [("Test cases executed", s["total"]), ("Passed", s["passed"]), ("Failed", s["failed"]),
            ("Skipped", s["skipped"])]
    rows += [(f"{k.upper()} tests / runtime", f"{v['tests']} / {v['duration_s']} s") for k, v in s["suites"].items()]
    rows += [("Total suite runtime", f"{s['duration_s']} s"),
             ("Seeded bugs detected", f"{s.get('bugs_detected', '?')} of {s.get('bugs_total', 6)}")]
    table = "\n".join(["| Metric | Value |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows])
    readme = ROOT / "README.md"
    text = re.sub(r"<!-- RESULTS:START -->.*<!-- RESULTS:END -->",
                  f"<!-- RESULTS:START -->\n{table}\n<!-- RESULTS:END -->", readme.read_text(), flags=re.S)
    readme.write_text(text)
    print(table)


if __name__ == "__main__":
    main(*sys.argv[1:])
