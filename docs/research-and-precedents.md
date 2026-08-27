# Research and precedents

This implementation uses clean-room code and draws design lessons from primary documentation and public orchestration projects. No third-party code or binary is redistributed.

## Primary platform sources

- [xAI Grok Build overview](https://docs.x.ai/build/overview): official CLI installation, browser login, and supported systems.
- [xAI enterprise/authentication documentation](https://docs.x.ai/build/enterprise): subscription proxy and authentication precedence; this motivated explicit API-key exclusion.
- [xAI CLI reference](https://docs.x.ai/build/cli/reference): headless arguments, tools, permissions, model, and output controls.
- [xAI settings reference](https://docs.x.ai/build/settings): configuration precedence and telemetry-related environment controls.
- [xAI Grok Build source](https://github.com/xai-org/grok-build): official Apache-2.0 CLI source and release provenance.
- [OpenAI building skills](https://learn.chatgpt.com/docs/build-skills): compact skill instructions, progressive disclosure, and plugin packaging.
- [OpenAI Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): custom agent locations and explicit model/reasoning configuration.
- [GitHub CLI skill install](https://cli.github.com/manual/gh_skill_install): cross-device installation, source tracking, and tagged-release workflow.

## Comparable implementations and lessons

- [delegate-agent](https://github.com/treygoff24/delegate-agent): staged copies, symlink escape handling, bounded output, process groups, and honest non-sandbox language.
- [grok-in-codex](https://github.com/stdevMac/grok-in-codex): the closest public Codex/Grok integration; useful setup/status/result lifecycle separation.
- [Grok-Skill](https://github.com/gitguffaw/Grok-Skill): CLI probing, model inspection, JSON output, and allowlists.
- [agent-cli-skills](https://github.com/philipbankier/agent-cli-skills): disposable CLI delegation and session evidence; its low turn ceiling is not copied.
- [grok-orchestra](https://github.com/Sora-bluesky/grok-orchestra): explicit prompt contracts, mechanical verification, and adversarial failure catalog.
- [codex-grok-orchestrator](https://github.com/MaxxxDong/codex-grok-orchestrator): preflight, leases, and disposable lifecycle patterns.
- [stringbean](https://github.com/ZenulAbidin/stringbean): durable state and event-log thinking.
- [awo](https://github.com/ystepanoff/awo): deterministic proof packs, isolated worktrees, and configured verification evidence; this directly informed Team Grok 1.1's local proof record.
- [codex-agy-delegator](https://github.com/swjturay/codex-agy-delegator): asynchronous run lifecycle, allowed/forbidden file scopes, test commands, and explicit apply/cleanup phases; this informed status/history and descendant write allowlists.
- [codex-orchestrator](https://github.com/zm2231/codex-orchestrator): supervisor rejection of filler and explicit approval/change-request states; this reinforced the single focused correction and machine-readable Sol decision.

The resulting state model distinguishes preflight failure, infrastructure failure, running with heartbeats, completed-unaccepted work, accepted work, rejected work, Luna escalation, Sol completion, timeout, and cleanup. Quality failures receive at most one focused Grok rework and one Luna escalation; infrastructure failures do not trigger a quality loop.
