#!/usr/bin/env python3
"""Publish the completed run with GitHub credentials (agents never get this token)."""
import json
import os
from pathlib import Path
import subprocess
import sys

def run(args, *, input_text=None, check=True):
    p = subprocess.run(args, input=input_text, text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(" ".join(args[:3]) + ": " + p.stderr[-1200:])
    return p

def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    issue_no = os.environ["ISSUE_NUMBER"]
    run_id = os.environ["GITHUB_RUN_ID"]
    report_path = Path(os.environ["RUNNER_TEMP"]) / "ai_result.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {
        "status": "error",
        "summary": "Setup or execution failed before the AI pipeline produced a result.",
        "findings": [],
        "verification": "",
    }
    status = report.get("status", "error")
    summary = str(report.get("summary", ""))[:1000]
    findings = report.get("findings") or []
    run_link = f"https://github.com/{repo}/actions/runs/{run_id}"
    issue_link = ""
    branch = f"ai/issue-{issue_no}-{run_id}"
    staged = run(["git", "diff", "--cached", "--quiet"], check=False).returncode == 1

    if status in ("pass", "needs_human") and staged:
        run(["git", "config", "user.name", "github-actions[bot]"])
        run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
        run(["git", "commit", "-m", f"AI: implement issue #{issue_no}"])
        # Credentials are only provided in this publishing step, after both agents exit.
        run(["gh", "auth", "setup-git"])
        run(["git", "push", "--set-upstream", "origin", branch])
        pr_body = (
            f"Automated implementation for #{issue_no}.\n\n"
            f"Claude developed the changes; Codex independently reviewed them.\n\n"
            f"**Result:** {status}\n\n**Review:** {summary}\n\n"
            + ("**Findings:**\n" + "\n".join("- " + str(x)[:400] for x in findings[:8]) + "\n\n" if findings else "")
            + f"**Actions run:** {run_link}\n\n"
            + "Merge requires a human decision. Do not assume tests passed without checking the verification log."
        )
        args = ["gh", "pr", "create", "--repo", repo, "--base", "main",
                "--head", branch, "--title", f"AI implementation: issue #{issue_no}",
                "--body", pr_body]
        if status != "pass":
            args.append("--draft")
        issue_link = run(args).stdout.strip()

    label = {
        "pass": "AI implementation and independent verification completed",
        "needs_human": "Human review required",
        "error": "AI pipeline failed",
    }.get(status, "AI pipeline stopped")
    comment = (
        f"### {label}\n\n"
        f"{summary}\n\n"
        + (f"Pull request: {issue_link}\n\n" if issue_link else "")
        + (("Codex findings:\n" + "\n".join("- " + str(x)[:400] for x in findings[:8]) + "\n\n") if findings else "")
        + f"Actions log: {run_link}\n\n"
        + ("No automatic merge was performed." if issue_link else "No pull request was created.")
    )
    run(["gh", "issue", "comment", issue_no, "--repo", repo, "--body", comment])
    print(comment)
    if status != "pass":
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Publishing failed:", str(error), file=sys.stderr)
        sys.exit(1)
