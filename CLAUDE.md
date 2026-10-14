# Claude development policy

- The original GitHub Issue, especially its Acceptance Criteria, is the source of truth.
- Design, implement, and run appropriate tests independently; keep scope minimal.
- Never claim a check passed unless it actually ran.
- Do not edit .github workflows, secrets, or agent-automation configuration as part of ordinary feature work.
- Create a feature branch and PR targeting main; never merge automatically.
- Escalate irreversible operations, production changes, security-sensitive work, breaking APIs, or material ambiguity.
- Codex is a separate independent PR reviewer, not part of this action.
