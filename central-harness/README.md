# Central AI Harness — rollout plan

## Goal
When a new repository is created under `takatyin`, make it eligible for:
Issue → Claude Opus (medium) implementation → GitHub PR → Codex independent review.
No workflow files or Claude OAuth secrets need to be copied into target repositories.

## Implemented in this branch
`.github/workflows/central-ai-development.yml` is an opt-in `workflow_dispatch` pilot that:
- accepts a target repository **name** and Issue number;
- uses a central GitHub App installation token scoped to that repository;
- checks out that repository, runs Claude Opus / medium with the existing subscription OAuth token;
- validates changes and opens a PR in the target repository using GitHub App credentials;
- never automatically merges.

This is **not yet automatic for newly created repositories**. No live run has been tested.

## Required secrets in the central repository (never commit values)
- `CLAUDE_CODE_OAUTH_TOKEN`: the existing Claude Pro OAuth token.
- `CENTRAL_GITHUB_APP_ID`: your custom GitHub App ID.
- `CENTRAL_GITHUB_APP_PRIVATE_KEY`: your custom GitHub App private key.

## GitHub App configuration — manual one-time setup
1. Create a GitHub App for `takatyin`; configure repository access to **All repositories**, including newly created ones.
2. Request least-privilege repository permissions: Contents read/write, Issues read, Pull requests read/write, Metadata read.
3. Install the App on `takatyin`; put App ID and its private key into the central repository Actions secrets (not in source files).
4. Keep the OAuth token only in the central runner, not copied to each target repository.
5. Create a harmless test repository/Issue and manually dispatch the central workflow from the Toho Actions tab, entering repository name and Issue number.
6. Confirm PR publication, manual merge, and Codex GitHub review before enabling any unattended trigger.

## True new-repository automatic provisioning — next phase
A GitHub App can receive installation/repository events. Build an authenticated webhook receiver (or equivalent controlled scheduler) that detects repositories under takatyin, records enrollment, and handles subsequent Issue events by dispatching the central runner. The GitHub App's webhook signature must be validated. Explicit trust and allowed repository policy is mandatory. No always-on webhook service is currently deployed.

The Codex cloud **code-review enablement** is a separate account-side setting, not implied by GitHub App access. Before claiming end-to-end zero-touch enrollment, verify that Codex automatic review actually triggers in a newly created repository. If not, a separate authorized review trigger is required.

## Security and implementation limits
- The pilot permits only manual workflow dispatch by `takatyin`; it is not a complete security boundary against malicious code or prompt injection.
- The central workflow runs generated code on a GitHub-hosted runner and has access to a Claude OAuth token. Use only trusted repositories, audit tool permissions, and isolate execution further before broad unattended rollout.
- The CLI model alias `opus` can change over time; `medium` is explicitly selected.
- The pilot expects a repository whose base branch is named `main`.
- No API-based Codex invocation or extra API billing is introduced.
- Target repositories do not need per-repository YAML with this central runner, but authentication, webhook infrastructure, and Codex automatic review configuration still need completion.

## Acceptance criteria for production rollout
- New repo under takatyin is discovered without manual copying.
- Owner-created AI Issue triggers Claude exactly once (or explicit /build trigger until removed).
- No secrets are written into target repository settings or source.
- Claude produces a PR in the target repository or a clear failure report.
- Codex independently reviews the PR.
- Neither the model nor automation automatically merges.
