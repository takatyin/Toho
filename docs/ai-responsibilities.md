# AI development responsibility policy

## Defaults
- **Codex**: initial architectural design where needed; independent PR review after implementation.
- **Codex preferred model**: GPT-6.1 Sol, medium reasoning effort.
- **Claude Code**: implementation and self-test, Opus model alias, medium effort.
- **Human**: original requirements and AC, critical design approvals, final merge.
- No automatic merge; do not use separately billed OpenAI API tokens without explicit permission.

## Critical design decisions
The `design_preflight.py` check runs before Claude. Small changes proceed normally; no independent design review is required.

The following require design review and explicit owner approval:
- breaking public interfaces or data contracts;
- schema/database migrations;
- architectural redesign or dependency-direction changes;
- changes affecting authentication, production operations, or high-impact security controls;
- an explicit `design-review`, `architecture`, `breaking-change`, `security-sensitive`, or `migration` Issue label.

For these cases:
1. Codex drafts a design proposal from the *original Issue*: alternatives, decision, affected interfaces, migration strategy, risks and AC.
2. Obtain a **separate critical review** of the proposal. Codex must not regard its own proposal as independently validated; seek counterexamples (Claude review or human review for highest-impact decisions).
3. Owner records approval in the Issue, then applies `codex-design-approved` label. This is a **manual attestation**, not proof the model ran or passed. No bot adds the label.
4. Re-run `/build`. Claude proceeds under the approved design, and the final PR is reviewed by Codex against the original requirements.

## What is and isn't automated today
- Implemented: conservative rule-based risk check on Toho's /build pipeline; block critical tasks lacking approval; normal Claude Opus/medium implementation and PR publishing unchanged.
- Verified previously: Codex PR review can be invoked from GitHub via `@codex review`; check repo settings for automatic PR reviews.
- **Not yet implemented**: automatically invoking Codex for design work under the ChatGPT subscription, automatically feeding design artifacts into Claude, machine-enforced verification that Codex reviewed the design, or setting a specific model/effort in Codex Cloud PR reviews. The preferred model and effort above are policy, not enforced settings.
- The central cross-repository pilot is also not yet connected to this gate. Apply centrally after a tested execution path exists.

## Limitations
The keyword/label check is only a guardrail. It can miss high-risk changes. Any agent should halt and escalate when encountering critical consequences even if preflight classifies the request as small.
