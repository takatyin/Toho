# Claude development contract

- Implement the requirements and acceptance criteria in the original GitHub Issue.
- Autonomously choose design and implementation approaches. Keep scope minimal.
- Self-test where feasible; do not claim unrun checks have passed.
- Never change the AI automation system (`.github/`, `scripts/ai_pipeline.py`, `scripts/review_schema.json`), this file, or `AGENTS.md` during a normal task.
- Escalate material ambiguity, irreversible changes, secrets, production operations, and breaking interfaces; do not make those decisions silently.
- Do not commit, push, merge, or open pull requests; the workflow handles Git operations.
