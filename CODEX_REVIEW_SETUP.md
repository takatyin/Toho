# Codex automatic PR review setup (ChatGPT subscription)

The Claude runner uses `--model opus` and `CLAUDE_CODE_EFFORT_LEVEL=medium`.
This uses the existing `CLAUDE_CODE_OAUTH_TOKEN`; no Anthropic API key is added.

## Enable Codex automatic review (one-time, account-side)

1. Open [Codex](https://chatgpt.com/codex) and ensure the GitHub connector is authorized for `takatyin/Toho`.
2. In Codex's repository/code-review settings, select `takatyin/Toho` and turn on **automatic code reviews for new pull requests**.
3. Open a new PR to verify Codex posts a review. PRs created by `github-actions[bot]` may be treated differently depending on the provider's trigger policy; verify this behavior explicitly.
4. If automatic review is not enabled or does not trigger, the fallback is a human-authored `@codex review` PR comment.

**Important:** The GitHub Actions workflow cannot change a user's Codex Cloud account review preferences. Do not add a bot-generated `@codex review` comment as a substitute: it is not a verified automatic-review trigger.

The Codex independent review is not an Actions job and requires no OpenAI API key. Merge is always manual.
