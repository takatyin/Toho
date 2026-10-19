#!/usr/bin/env python3
"""Conservative risk classification before implementation; no model is invoked."""
import json
import os
import re
import sys
from pathlib import Path

issue = json.loads(Path(sys.argv[1]).read_text())
labels = {x["name"].lower() if isinstance(x, dict) else str(x).lower() for x in issue.get("labels", [])}
patterns = [
    r"(?i)breaking[ -]change", r"(?i)(schema|database)[ -]migration",
    r"(?i)architecture[ -](redesign|rewrite)", r"(?i)production[ -](deploy|change)",
    r"(?i)(authentication|authorization)[ -](redesign|change)",
]
text = (issue.get("title") or "") + "\n" + (issue.get("body") or "")
reasons = sorted(labels & {"architecture","breaking-change","design-review","security-sensitive","migration"})
reasons += ["keyword:" + p for p in patterns if re.search(p,text)]
critical = bool(reasons)
approved = "codex-design-approved" in labels
summary = os.environ.get("GITHUB_STEP_SUMMARY")
lines = ["## Design preflight", f"- Critical change detected: {critical}",
         f"- Codex design review approval label: {approved}",
         "- Model: GPT-6.1 Sol / Medium (preferred policy; not enforced by Codex Cloud)."]
if reasons:
    lines.append("- Reasons: " + ", ".join(reasons))
if summary:
    with open(summary,"a") as f:
        f.write("\n".join(lines)+"\n")
if critical and not approved:
    print("::error::Critical design change. Obtain independent Codex design review and owner approval before /build.")
    sys.exit(2)
