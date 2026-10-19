#!/usr/bin/env python3
"""Issue -> Claude implementation -> Codex review -> up to two repairs.

This script does not have GitHub write credentials. Publication is a separate CI step.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path.cwd()
TEMP = Path(os.environ["RUNNER_TEMP"])
REPORT = TEMP / "ai_result.json"
SCHEMA = ROOT / "scripts" / "review_schema.json"
MAX_REPAIRS = 2
PROTECTED = (
    ".github/", "AGENTS.md", "CLAUDE.md",
    "scripts/ai_pipeline.py", "scripts/review_schema.json", "scripts/verify.sh",
)
SENSITIVE = (".env", ".env.", ".pem", ".key", "id_rsa", "credentials.json")

def command(args, *, env=None, input_text=None, timeout=600):
    return subprocess.run(
        args, text=True, input=input_text, capture_output=True,
        env=env, timeout=timeout, check=False,
    )

def git(*args):
    out = command(["git", *args], timeout=30)
    if out.returncode:
        raise RuntimeError("git " + " ".join(args) + ": " + out.stderr[-700:])
    return out.stdout.strip()

def write_report(status, summary, findings=None, verification=""):
    REPORT.write_text(json.dumps({
        "status": status, "summary": summary,
        "findings": findings or [], "verification": verification,
    }, ensure_ascii=False, indent=2) + "\n")

def stage_and_guard(original_head):
    if git("rev-parse", "HEAD") != original_head:
        raise RuntimeError("Agent modified git history. Refusing to publish.")
    git("add", "-A")
    paths = git("diff", "--cached", "--name-only", "-z").split("\x00")
    for path in filter(None, paths):
        lower = path.lower()
        base = Path(lower).name
        if (any(path == p or path.startswith(p) for p in PROTECTED)
                or base == ".env" or base.startswith(".env.")
                or base in ("id_rsa", "credentials.json")
                or lower.endswith((".pem", ".key"))):
            raise RuntimeError("Protected or sensitive file changed: " + path)
    if command(["git", "diff", "--cached", "--check"]).returncode:
        raise RuntimeError("git diff --check failed")
    return list(filter(None, paths))

def invoke_claude(prompt, round_num):
    environment = os.environ.copy()
    environment.pop("OPENAI_API_KEY", None)
    out = command(
        ["claude", "-p", prompt, "--permission-mode", "acceptEdits",
         "--allowedTools", "Bash,Read,Edit,Write,Glob,Grep",
         "--max-turns", "22", "--output-format", "text"],
        env=environment, timeout=800,
    )
    (TEMP / f"claude-{round_num}.log").write_text(
        out.stdout[-20000:] + "\nSTDERR:\n" + out.stderr[-5000:]
    )
    if out.returncode:
        raise RuntimeError(
            f"Claude execution failed (round {round_num}); see workflow logs/artifacts."
        )
    return out.stdout[-3000:]

def verify(round_num):
    environment = os.environ.copy()
    environment.pop("OPENAI_API_KEY", None)
    environment.pop("ANTHROPIC_API_KEY", None)
    out = command(["bash", "scripts/verify.sh"], env=environment, timeout=300)
    log = (out.stdout + "\n" + out.stderr)[-5000:]
    (TEMP / f"verify-{round_num}.log").write_text(log)
    return out.returncode == 0, log

def invoke_codex(issue_text, verification_ok, verification_log, round_num):
    review_path = TEMP / f"review-{round_num}.json"
    review_prompt = (
        "You are an INDEPENDENT verification agent. The original user requirements "
        "are your source of truth, not Claude's explanation. Review the staged "
        "changes using git diff --cached and the repository. Examine functionality, "
        "architectural risks, missing edge cases, and test adequacy. Do not edit files "
        "or call external network services. Return status 'fail' for concrete "
        "fixable defects, 'needs_human' for ambiguous requirements, breaking changes, "
        "unsafe operations, or unverified critical outcomes; 'pass' only if the "
        "changes meet requirements and checks are adequate. Do not invent findings.\n\n"
        + "ORIGINAL ISSUE:\n" + issue_text[:25000] + "\n\n"
        + "AUTOMATED VERIFICATION PASSED: " + str(verification_ok) + "\n"
        + "VERIFICATION LOG (tail):\n" + verification_log[-3500:] + "\n"
        + "Write the JSON summary and each findings item in Japanese for human-facing reporting. Keep internal reasoning and code analysis in English. Return ONLY JSON conforming to the provided schema."
    )
    environment = os.environ.copy()
    environment.pop("ANTHROPIC_API_KEY", None)
    out = command(
        ["codex", "exec", "--sandbox", "read-only",
         "--output-schema", str(SCHEMA), "--output-last-message", str(review_path), "-"],
        env=environment, input_text=review_prompt, timeout=650,
    )
    (TEMP / f"codex-{round_num}.log").write_text(
        out.stdout[-10000:] + "\nSTDERR:\n" + out.stderr[-5000:]
    )
    if out.returncode:
        raise RuntimeError(f"Codex execution failed (round {round_num}).")
    try:
        review = json.loads(review_path.read_text())
    except (FileNotFoundError, ValueError) as exc:
        raise RuntimeError("Codex did not produce valid structured review") from exc
    if review.get("status") not in ("pass", "fail", "needs_human"):
        raise RuntimeError("Invalid Codex review status")
    if not isinstance(review.get("findings"), list):
        raise RuntimeError("Invalid Codex findings")
    return review

def main():
    if not os.getenv("ANTHROPIC_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Missing ANTHROPIC_API_KEY or OPENAI_API_KEY GitHub Actions secret."
        )
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    owner = os.environ["GITHUB_REPOSITORY_OWNER"]
    issue = event["issue"]
    comment = event["comment"]
    if (issue["user"]["login"] != owner or comment["user"]["login"] != owner
            or comment["body"].strip() != "/build" or "pull_request" in issue):
        raise RuntimeError("Unauthorized or unsupported Issue command")
    issue_text = f"Title: {issue['title']}\n\n{issue.get('body') or ''}"
    branch = f"ai/issue-{issue['number']}-{os.environ['GITHUB_RUN_ID']}"
    git("switch", "-c", branch)
    original_head = git("rev-parse", "HEAD")

    feedback = ""
    last_review = None
    for attempt in range(MAX_REPAIRS + 1):
        prompt = (
            "Implement the following original GitHub Issue in this repository. "
            "Read CLAUDE.md and keep changes tightly scoped. You may design, write "
            "code, write tests and run local commands. Do not touch automation files, "
            "commit, push or create PRs. Avoid production operations and secret access. "
            "If the requirements are critically ambiguous or require dangerous changes, "
            "do not execute those changes; say so instead.\n\n"
            + issue_text[:25000]
            + ("\n\nINDEPENDENT REVIEW / REPAIR REQUEST:\n" + feedback if feedback else "")
        )
        invoke_claude(prompt, attempt)
        changed = stage_and_guard(original_head)
        if not changed:
            write_report("needs_human", "Claude made no file changes; unable to create a PR.")
            return
        verification_ok, verification_log = verify(attempt)
        # Re-stage legitimate edits by test scripts, and guard them too.
        stage_and_guard(original_head)
        review = invoke_codex(issue_text, verification_ok, verification_log, attempt)
        last_review = review
        if review["status"] == "needs_human":
            write_report("needs_human", review["summary"], review["findings"], verification_log)
            return
        if review["status"] == "pass" and verification_ok:
            write_report("pass", review["summary"], review["findings"], verification_log)
            return
        feedback = (
            "Independent review status: " + review["status"] +
            "\nFindings:\n" + "\n".join(review["findings"]) +
            "\nTest passed: " + str(verification_ok) +
            "\nTest log tail:\n" + verification_log[-3000:]
        )
    write_report(
        "needs_human", "Automated repair limit reached after two retries.",
        (last_review or {}).get("findings", []),
        "See GitHub Actions logs for verification failures.",
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        write_report("error", str(exc))
        print("AI pipeline error:", str(exc), file=sys.stderr)
        sys.exit(1)
