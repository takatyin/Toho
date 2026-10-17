#!/usr/bin/env python3
"""Summarize Claude execution metadata without printing raw tool input/output."""
import json
import os
from pathlib import Path
import re

path = Path(os.environ.get("CLAUDE_EXECUTION_FILE", ""))
if not path.is_file() or not path.resolve().is_relative_to(Path(os.environ["RUNNER_TEMP"]).parent):
    print("Claude execution detail file unavailable; no tool transcript was published.")
    raise SystemExit(0)

# Only metadata; never print error content, prompts, command arguments, paths, or responses.
categories = {"Bash": 0, "Read": 0, "Write": 0, "Edit": 0, "Other": 0}
denials = 0
try:
    data = path.read_text(encoding="utf-8", errors="replace")
    try:
        events = json.loads(data)
        if not isinstance(events, list):
            events = [events]
    except json.JSONDecodeError:
        events = [json.loads(line) for line in data.splitlines() if line.strip().startswith("{")]
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("type") == "result":
            count = event.get("permission_denials_count")
            if isinstance(count, int):
                denials = max(denials, count)
        msg = event.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict):
                continue
            # A denied tool-use event may be marked directly in a tool result.
            if item.get("type") != "tool_result" or not item.get("is_error"):
                continue
            value = item.get("content")
            # Never emit this text. Only recognize explicit permission-denied markers.
            plain = value if isinstance(value, str) else ""
            if re.search(r"permission\s+denied|permission to use|not allowed|was rejected", plain, re.I):
                denials += 1
except Exception:
    print("Execution metadata not parseable; raw transcript remains hidden.")
    raise SystemExit(0)

print(f"Permission denial signals: {denials}")
print("Individual denied tool names: not reliably available in safe metadata.")
