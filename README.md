# Team Grok for Codex

Team Grok lets a Sol-led Codex task delegate bounded work to the user's existing Grok Build subscription—without xAI API keys or API billing—while Sol keeps requirements, review, integration, and final-answer ownership. Its normal interface is simply: `Use Team Grok.` Sol handles the mechanics in the background.

It is intentionally more than a prompt. Sol reconciles all task-relevant authorized context, while a Python runner proves the subscription route, selects the newest numeric Grok model in the live catalog at `xhigh` effort, stages only supplied sources, refuses common credential paths/names and high-confidence secret-content patterns, rejects ambient extensions or incompatible inspection schemas, enforces explicit write scope, records progress/evidence, verifies model usage and context receipts, and leaves edits unaccepted until Sol audits them. If Grok is not good enough, an embedded identity-verified Luna contract is available; otherwise Sol finishes.

## Requirements

- macOS (Team Grok 1.x; Linux and Windows fail closed)
- Codex with Sol as the lead model
- Python 3.9+
- the official [Grok Build CLI](https://docs.x.ai/build/overview) installed at `~/.grok/bin/grok`
- an active browser/subscription login from `grok login`; no `XAI_API_KEY`
- Grok CLI 1.0.5+

Team Grok is not affiliated with, endorsed by, or sponsored by xAI or OpenAI. “Grok,” “xAI,” “Codex,” and “OpenAI” are marks of their respective owners.

## Install

### Standalone skill with GitHub CLI

```bash
gh skill install sedater42/team-grok team-grok --agent codex --scope user
```

GitHub CLI tracks the source and can update an installed skill. Prefer a tagged release for reproducibility. Codex discovers personal skills under `~/.codex/skills`; restart Codex after installation if it was already running.

### Local plugin development

This repository is also a Codex plugin package: `.codex-plugin/plugin.json` points at `skills/`. Validate it before installation:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py /path/to/team-grok
```

The optional named Luna role can be copied to `~/.codex/agents/team-grok-luna-worker.toml`. It is not required; the skill also supports an explicit GPT-5.6 Luna route when the runtime exposes that model.

## Use

Tell Codex: `Use Team Grok for this task.` Sol should then reconcile the request, relevant files, project instructions, tool findings, current state, and distilled memory; dispatch Grok; quietly monitor it; independently verify the result; correct or fall back when warranted; integrate only accepted work; and report which route was actually accepted. Routine setup and polling should not be pushed back to the user.

Manual diagnostics:

```bash
python3 skills/team-grok/scripts/run_grok.py doctor --cwd /path/to/workspace
python3 -m unittest discover -s skills/team-grok/tests -v
python3 -m unittest discover -s tests -v
```

For unattended runs, Sol supplies `--context-complete` and a private `--record-dir`. Status and proof remain locally inspectable:

```bash
python3 skills/team-grok/scripts/run_grok.py list-runs --record-dir /path/to/work/team-grok-runs
python3 skills/team-grok/scripts/run_grok.py run-status --run-dir /path/to/work/team-grok-runs/<run-id>
```

A workspace-edit run preserves a private temporary stage. Sol can inspect and remove it safely:

```bash
python3 skills/team-grok/scripts/run_grok.py stage-inspect --stage /path/to/stage
python3 skills/team-grok/scripts/run_grok.py stage-cleanup --stage /path/to/stage
```

## Adaptive upgrades

Team Grok automatically selects the highest numeric `grok-X.Y` model returned by the authenticated subscription catalog, never below Grok 4.6. Improvements inside that model arrive without editing the skill. A signed CLI update installed by the user is accepted on the next run if all compatibility checks pass.

Permissions do not expand automatically. New Grok tools, ambient skills, subagents, or auth paths require a reviewed Team Grok release. This preserves the quality/safety contract while still inheriting newer-model intelligence.

## Privacy and trust boundary

Delegated prompt text, curated context, filenames, and staged source content are sent to xAI for cloud inference through the user's subscription. Team Grok is not local inference. The runner disables its own use of telemetry/trace upload environment switches, but that does not change xAI's service-side handling of subscription traffic.

Never delegate secrets, credentials, raw Codex memory, or information that is not authorized to leave the machine. Secret detection is best-effort, not complete. See [Privacy](docs/privacy.md), [Threat model](docs/threat-model.md), and [Support matrix](docs/support-matrix.md).

## Project status

Version 1.1.0 is the macOS-first unattended-orchestration release. Offline tests run in CI; live subscription tests must run manually on a trusted, logged-in Mac and must never place session state in CI.

- [Architecture](docs/architecture.md)
- [Research and precedents](docs/research-and-precedents.md)
- [Release checklist](docs/release-checklist.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

Licensed under Apache-2.0.
