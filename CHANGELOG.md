# Changelog

All notable changes follow semantic versioning.

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
