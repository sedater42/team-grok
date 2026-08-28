# Changelog

All notable changes follow semantic versioning.

## 1.1.5 - 2026-08-27

- Fixed Grok CLI 1.0.5 compatibility discovery so MCP records are ignored only when both `disabled` is exactly `true` and `compatibilityStatus` is exactly `disabled`; active, malformed, and ambiguously disabled entries still fail closed.
- Added the runner-controlled `_GROK_CLAUDE_MARKER_OVERRIDE=1` isolation workaround and prevented caller values from entering the child environment.
- Ignored project instructions only when the same two-field disabled proof is present, while active and ambiguous instructions remain subject to the supplied-context gate.
- Added separate evidence for total versus active extension entries and for explicitly disabled MCP and project-instruction records that were ignored.
- Added regression coverage for the MacBook repair and superseded the one-off local runner version 1.1.4.

## 1.1.1 - 2026-08-27

- Made Team Grok invocation grant Grok the same task-scoped data authorization as the lead Codex model for xAI subscription inference.
- Required relevant personal, confidential, connector-derived, and memory-derived context to be supplied rather than silently withheld.
- Required a focused user question before dispatch whenever transmission authority for necessary context is genuinely uncertain.
- Retained exclusions for credentials, authentication secrets, irrelevant material, explicit user exclusions, and higher-priority policy boundaries.

## 1.1.0 - 2026-08-27

- Made “use Team Grok” unattended by default: Sol handles context reconciliation, dispatch, review, correction, fallback, integration, and cleanup.
- Added a context-completeness gate covering task requests, relevant files, instructions, tool findings, current state, and distilled memory without exposing raw memory or secrets.
- Added private durable run records, 15-second status heartbeats, history/status commands, proof packs, and immutable machine-readable Sol decisions.
- Added exact workspace write allowlists with post-run rejection of changes outside authorized staged sources.
- Incorporated proof-pack, lifecycle, and allowlist patterns from comparable open-source delegators while retaining subscription-only Grok and Sol acceptance boundaries.

## 1.0.0 - 2026-08-27

- First publication-ready Team Grok release candidate.
- Added signed macOS xAI binary verification and subscription-only authentication proof.
- Added adaptive newest-model selection at `xhigh` with Grok 4.6 floor.
- Added required-CLI-capability probing and corrected opt-in web environment routing found by live smoke testing.
- Added isolated hash-verified staging, exact context receipts, config stability checks, output bounds, and safe stage lifecycle commands.
- Disabled API credentials, Bash, subagents, memory, workflows, optional telemetry, and ambient extension execution.
- Embedded an identity-verified Luna fallback independent of the Team Luna skill.
- Added plugin metadata, privacy/threat documentation, CI, compatibility manifest, and release checklist.
