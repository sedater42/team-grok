# Embedded Luna fallback contract

Team Grok must work even when the separate Team Luna skill is absent. Sol uses this self-contained capability ladder only after rejecting Grok for a substantive quality defect.

## Identity-verified routing order

1. Prefer a callable custom role named `team_grok_luna_worker`.
2. Otherwise use a callable runtime role named `luna_worker`.
3. Otherwise spawn with explicit `model: gpt-5.6-luna`, `reasoning_effort: xhigh`, and `fork_turns: none`.
4. If none is callable, report Luna unavailable and have Sol finish.

Count a Luna attempt only when spawn/runtime evidence proves GPT-5.6 Luna. A task name, prompt, worker self-description, or generic child is not identity evidence. Never substitute Terra, Sol, a GPT-4/5 default, Grok, or a role-played Luna.

## Lane contract

- Spawn one fresh, bounded Luna brief containing Sol's acceptance criteria, supplied files/context, the observed Grok defect, authorization boundary, and required evidence.
- The worker is not alone in the workspace and must not revert unrelated changes.
- Use one Luna attempt. Allow one focused follow-up only when the defect is narrow and the worker is demonstrably progressing.
- Do not launch nested Codex CLI sessions unless the user explicitly asks.
- Sol independently verifies all output and decides whether to integrate it.

## Terminal states

- `Grok rejected; Luna accepted`
- `Grok rejected; Luna unavailable; Sol completed`
- `Grok and Luna rejected; Sol completed`

The optional repository file `codex-agents/team-grok-luna-worker.toml` makes the preferred named role easy to install, but it is not required. The explicit-model route keeps the skill portable on Codex runtimes that expose GPT-5.6 Luna without an installed Team Luna skill.
