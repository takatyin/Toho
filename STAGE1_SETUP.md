# Stage 1: subscription-oriented mobile AI development

This branch **replaces** the earlier API-billed prototype. Do not merge both workflow proposals.

Workflow: owner opens a GitHub Issue -> posts exactly `/build` -> Claude Code (Pro OAuth token) designs/implements/tests and opens PR -> Codex (ChatGPT Pro, GitHub Cloud code review) reviews the PR -> owner checks it on GitHub Mobile.

## One-time manual steps

1. Merge this setup PR to `main`. GitHub runs Issue-comment workflows only when the workflow file is on the default branch.
2. Install/authorize the [Claude GitHub App](https://github.com/apps/claude) for Toho, as described in the [official setup guide](https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md).
3. On a trusted computer authenticated to Claude Pro, run `claude setup-token`. Store the returned token **only** as the repository Actions secret `CLAUDE_CODE_OAUTH_TOKEN`. Never paste it in a chat, issue or source file.
4. Connect Toho to [Codex](https://chatgpt.com/codex) via ChatGPT Pro and enable its GitHub pull-request code review for this repository. Automatic review availability/settings are controlled in Codex; they cannot be enabled by this workflow. If automatic reviews are unavailable, request `@codex review` in the PR.
5. In GitHub Actions settings, ensure permitted Actions can create pull requests and have the permissions requested in the workflow.

## Daily use (iPhone / GitHub Mobile)

1. Create an Issue using the AI開発依頼 form, entering Goal and Acceptance Criteria.
2. Comment exactly `/build` on the Issue.
3. On the resulting PR, inspect Claude's implementation summary, checks, and Codex review. Merge manually once satisfied.

## Limitations

- This stage **does not** automatically return Codex findings to Claude. That is Stage 2.
- Claude OAuth token expiry, GitHub App authorization, available Pro usage, Actions runner limits and Codex integration settings can interrupt execution.
- No separate OpenAI API key is used in this workflow; an Anthropic API key is not used either. Cloud review depends on Codex account entitlement/settings.
- No live end-to-end subscription-authenticated run has been performed yet. This is a configuration proposal until validated.
- This repository currently has no established application test suite. Claude must state which checks it could or could not execute.
- Treat generated code and reported test results as untrusted until verified. Do not use this initial prototype for production secrets or deployments.
