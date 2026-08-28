# Team Grok CLI contract

The Python runner is the executable trust boundary. It uses the user's existing Grok Build browser/subscription login; it neither asks for nor accepts xAI API credentials.

## Supported baseline

- macOS only in Team Grok 1.x
- Python 3.9 or newer
- official executable at `~/.grok/bin/grok`, signed by X.AI Corporation Team ID `5Y6N3AJ54S`
- Grok CLI 1.0.5 or newer
- `grok models` must say `You are logged in with grok.com.`
- newest numeric `grok-X.Y` model in that subscription catalog, with a Grok 4.6 floor
- `xhigh` reasoning; no silent downgrade

The model selector is adaptive: if the subscription catalog later offers Grok 4.7, 5.0, or another higher numeric release, the next run selects it automatically. The runner accepts usage keys only for that exact selected model and its `-build` serving variant. It also hashes `grok --help` and requires every documented CLI flag the isolation contract depends on. Hidden compatibility flags such as `--no-memory` and `--no-auto-update` are exercised by every inference run and fail closed if the CLI stops accepting them; the controlled environment independently disables memory and the updater. New reasoning quality is inherited automatically. New tools or ambient skills are not auto-enabled because doing so would expand permissions; they require a reviewed Team Grok release.

The CLI is invoked with `--no-auto-update` so a binary is never replaced mid-run. A user-installed signed upgrade is used on the next invocation after the compatibility and subscription checks pass.

Grok CLI 1.0.5 can import Claude permission rules even when the documented Claude compatibility environment switches are disabled. Team Grok therefore injects `_GROK_CLAUDE_MARKER_OVERRIDE` as the exact string `1` into its sanitized child environment and never inherits a caller-supplied value. This is a compatibility workaround, not trust evidence: `grok inspect --json` must still prove zero ambient permission rules and no active compatibility surfaces. A future CLI that changes the behavior remains fail-closed at those postconditions.

## Commands

```bash
python3 /absolute/path/to/scripts/run_grok.py doctor --cwd /absolute/workspace
python3 /absolute/path/to/scripts/run_grok.py run \
  --prompt-file /absolute/brief.md \
  --context-file /absolute/curated-context.md \
  --context-path /absolute/required-source \
  --cwd /absolute/workspace \
  --context-complete \
  --record-dir /absolute/work/team-grok-runs \
  --mode read-only
python3 /absolute/path/to/scripts/run_grok.py run-status --run-dir /absolute/run-directory
python3 /absolute/path/to/scripts/run_grok.py list-runs --record-dir /absolute/work/team-grok-runs
python3 /absolute/path/to/scripts/run_grok.py record-decision \
  --run-dir /absolute/run-directory \
  --decision accepted \
  --note-file /absolute/sol-review.md
python3 /absolute/path/to/scripts/run_grok.py stage-inspect --stage /absolute/stage
python3 /absolute/path/to/scripts/run_grok.py stage-cleanup --stage /absolute/stage
```

`check` is retained as an alias-compatible preflight. `doctor` is the preferred public command.

## Handoff and staging

The runner rejects unreadable paths, raw Codex memory roots, common credential locations/names, symlinks, hard links, overlapping sources, control characters, and oversized trees. It hashes each source, copies it into `workspace/sources/NNN-name`, re-hashes the copy, and never gives Grok the original workspace.

Curated context is embedded under anonymous IDs such as `context-file-001`; original absolute context/source paths are kept in Sol's local JSON handoff manifest but omitted from the prompt sent to Grok. Filenames and supplied content still go to xAI. Temporary handoff prompts are mode 0600 and deleted after use.

`--context-complete` is Sol's explicit assertion that the task working set was reconciled before dispatch: current instructions, acceptance gates, relevant files, applicable project instructions, transient tool findings, current state, and distilled task-relevant memory are supplied or intentionally excluded. It does not authorize bulk transmission. The runner still refuses raw memory and common secret paths. For a supplied directory, repeat `--must-read-path` for every nested file or directory Sol materially relied on; each receives an exact receipt requirement.

The response must end with whole-line `EMBEDDED`, `OPENED`, and `INSPECTED` receipts after a `Context receipt` heading. Lines inside code fences, partial-line matches, missing items, and contradictory `ACCESS DENIED` receipts fail. This proves a structured acknowledgment, not truth; Sol must still audit the work.

Read-only stages must remain unchanged and are deleted. Workspace stages are preserved after inference for review, including failed post-inference validation. Each preserved stage has a marker, owner check, run ID, and safe inspect/cleanup commands. Pre-inference validation failures are cleaned automatically.

Workspace runs require at least one `--writable-path`. It may be an exact supplied context path, a descendant of a supplied directory, or an explicit new path inside a supplied directory. The prompt marks the mapped staged scope, and the runner rejects any candidate that changes another path. This is post-run enforcement inside an isolated copy; originals remain unchanged.

`--record-dir` is required. The runner creates the private record before binary resolution/preflight and writes mode-0600 status heartbeats, the complete local `run.json`, `changes.json`, an anonymous-path `diff.patch`, and `proof-pack.md`. The record directory must not overlap delegated context. `run-status` reports runner-process/heartbeat evidence, and `list-runs` supports interrupted or long-running orchestration. Sol then writes one immutable decision using `record-decision`: `accepted`, `rework`, `rejected`, `luna_escalated`, or `sol_completed`. Decisions require matching `completed_unaccepted` status/run evidence and bind hashes of `run.json`, `changes.json`, and `diff.patch`; non-rejection routes require a review note. A completed Grok run always starts as `completed_unaccepted`.

## Subscription and configuration proof

Each run:

1. resolves only the official home-path binary and validates its Apple signature with `/usr/bin/codesign`;
2. creates a minimal environment, removes `GROK_*`, `XAI_*`, `OTEL_*`, common API keys, and endpoint overrides, then installs controlled no-memory/no-subagent/no-workflow/no-telemetry settings;
3. runs `grok inspect --json` and refuses active hooks, plugins, MCP/LSP servers, permission rules, remote compatibility settings, non-session Claude/Cursor/Codex compatibility surfaces, or applicable project instructions not explicitly supplied; an MCP record or project instruction is ignored only when `disabled` is exactly `true` and `compatibilityStatus` is exactly `disabled`, while malformed or ambiguous MCP records fail and ambiguous instructions remain supplied-context gated; known enabled `sessions` metadata may be enumerated but is not exposed as a tool or imported into the run;
4. scans discovered Grok TOML for quoted, dotted, inline, or table-form API/provider/model overrides;
5. fingerprints configuration before and after inference;
6. proves the `grok.com` login and adaptive model selection; and
7. requires `end_turn`, bounded output, positive numeric model usage, receipt success, and original-source integrity.

`grok inspect` may enumerate bundled and user skill metadata. Team Grok does not expose a skill tool in `--tools`, injects an explicit no-ambient-skill rule, and reports any non-bundled metadata. Doctor/run evidence separately reports total and active extension counts plus explicitly disabled MCP and project-instruction records that were ignored. This is defense in depth, not a claim that the CLI is a complete security sandbox.

## Permission boundary

Public v1 exposes only `Read` and `Grep`, plus `Edit` in an authorized workspace stage. `WebSearch` and `WebFetch` are opt-in. Bash, Grok subagents, ambient skill execution, memory, workflows, hooks, plugins, MCP, LSP, and compatibility imports are unavailable or cause refusal.

The strict stage, permission list, credential path/name heuristics, bounded high-confidence content scan, and receipt reduce risk; the runner cannot prove that supplied source text contains no secrets or that a vendor sandbox has no defect. Sol must curate inputs and review outputs. Never pass credentials, proprietary material that may not be sent to xAI, or raw personal memory.

The authenticated CLI may report nominal `costUSD` bookkeeping even on the subscription route. That field does not prove API billing; the live `grok.com` marker plus API-exclusion checks establish the permitted route. There is no verified Fast/priority CLI switch, so Team Grok never claims one.
