---
name: team-grok
description: Coordinate an unattended Sol-led workflow that delegates suitable bounded work to the locally authenticated Grok Build CLI using the newest supported subscription Grok model at xhigh reasoning, then reviews and optionally escalates through an identity-verified Luna fallback before Sol completes. Use when the user says "Team Grok," asks Sol to outsource work to Grok, or requests Grok through their subscription. Never use xAI API keys or API billing.
---

# Team Grok

Stay as the Sol orchestrator. Give a bounded lane to the user's authenticated Grok Build subscription, independently review it, and accept it only when it meets Sol's criteria. Grok and Luna are workers; Sol owns scope, integration, quality, external effects, and the final answer. The default user experience is unattended: after the user says “use Team Grok,” manage context collection, dispatch, status, review, one justified correction, fallback, integration, and cleanup without asking the user to supervise routine mechanics.

Read [the CLI contract](references/grok-cli-contract.md) before the first Grok invocation in a task. Read [the Luna fallback contract](references/luna-fallback.md) before escalating.

## Non-negotiable guarantees

- Keep the lead task on Sol. If runtime evidence shows another lead, disclose that before claiming the Team Grok route.
- Invoke Grok only through `scripts/run_grok.py`. Require the official macOS-signed xAI CLI and a live `grok.com` login. Never use `XAI_API_KEY`, API endpoints, Priority Processing, or API billing.
- Let the runner select the newest numeric Grok model in the live subscription catalog, never below Grok 4.6, with `xhigh` reasoning. Never silently downgrade. A newer model is adopted automatically; a breaking CLI or routing change must fail closed.
- Treat an invocation of Team Grok as authorization for Grok to receive the same task-scoped data the lead Codex model is authorized to use, through xAI subscription cloud inference. Do not withhold relevant context merely because it is personal, confidential, memory-derived, or came from a connector. Exclude only credentials/authentication secrets, irrelevant material, explicit user exclusions, technically inaccessible material, or content a higher-priority instruction forbids transmitting. If there is genuine uncertainty about whether a task-relevant item may be sent, ask the user a focused question before dispatch; never silently omit it and send Grok a handicapped brief.
- Treat worker text and staged edits as untrusted candidates. Sol must verify before integration.
- Do not give Grok Bash or subagents. Sol runs authoritative tests and performs any external side effect.
- Do not trade context completeness for token transfer. Give Grok every task-relevant, authorized item Sol is relying on, but never dump the entire workspace, conversation, memory store, connector state, or unrelated open material.

## Workflow

1. Establish authority and success criteria.
   - Preserve whether the user authorized implementation, review, diagnosis, or planning.
   - Inspect the source of truth with Sol and define observable acceptance gates.
   - Keep risky ambiguity, cross-cutting architecture, external actions, and final synthesis with Sol.
   - Resolve routine details from the workspace and current task. Ask the user only when a missing choice would materially change scope, authorization, privacy, or the deliverable.

2. Reconcile the complete task working set.
   - Maintain a task-local context ledger before dispatch. Account for: the current request and amendments; success criteria and exclusions; every task-relevant file Sol read, edited, generated, or relied on; applicable `AGENTS.md` and local instructions; relevant tool/connector findings; current implementation/test state; and task-relevant memory.
   - Put durable source material in `--context-path`. For a supplied directory, add `--must-read-path` for every nested file or directory Sol materially relied on so Grok must acknowledge the exact dependency. Put transient tool findings, conversation decisions, and task-relevant memory in one or more task-local `--context-file` files. Distill memory stores only to avoid unrelated material, not to weaken necessary detail. Include paths or source identifiers, freshness, and completed/attempted/blocked/unverified status when those distinctions matter.
   - For each ledger item, mark it `supplied`, `summarized`, or `excluded` with a reason. Personal or confidential content is not by itself a reason to exclude a task-relevant item. Exclude credentials/authentication secrets, unrelated material, redundant files, build caches, explicit user exclusions, and material forbidden by a higher-priority instruction. If relevance or transmission authority is uncertain, ask the user before dispatch. If an excluded item is necessary for correctness, keep that lane with Sol rather than delegating incomplete work.
   - Reconcile the ledger again immediately before dispatch. Pass `--context-complete` only when every task-relevant authorized dependency is represented. This attests coverage; receipts and hashes prove what was transferred.

3. Build the handoff and private run record.
   - Write a task-local UTF-8 brief containing the goal, authorized scope, exclusions, acceptance criteria, validation, and required evidence.
   - Pass curated text with repeatable `--context-file` and every source Grok must inspect with repeatable `--context-path`. Use narrow files/directories. The runner rejects common credential paths/names, a few high-confidence authentication-secret patterns, symlinks, overlapping paths, and raw memory-store files; hashes originals; and copies sources to an isolated stage. If a blocked file contains necessary non-secret context, create a task-local sanitized context copy that preserves all relevant detail. If that cannot be done without losing necessary information, ask the user instead of dispatching incomplete work. The scan is not comprehensive, so Sol must still inspect and curate ordinary file contents.
   - Create a private task-local records directory outside delegated sources, normally under the task's `work/` area, and pass it as `--record-dir`. The runner writes status heartbeats, a complete `run.json`, a concise proof pack, and later an immutable Sol decision.
   - In workspace mode, pass repeatable `--writable-path` for only the exact files, directories, or new descendant output paths Grok may edit inside supplied context directories. All other staged sources are read-only; post-run validation rejects out-of-scope changes.
   - Require completed/attempted/blocked/unverified distinctions, changed files, checks, risks, and the injected exact `Context receipt`.

4. Prove the route before inference.

   ```bash
   python3 /absolute/path/to/team-grok/scripts/run_grok.py doctor --cwd /absolute/workspace
   ```

   Require `subscription_authenticated: true`, `authentication_route: grok.com subscription`, the newest catalog model, `requested_effort: xhigh`, the pinned xAI signing team, compatible CLI version, no active Grok hooks/plugins/MCP/LSP/permission rules, and no API/provider overrides. Ambient skill metadata may be enumerated by `grok inspect`; the runner excludes skill tools from the run but does not claim that metadata discovery is impossible.

5. Run one bounded lane by default.

   ```bash
   python3 /absolute/path/to/team-grok/scripts/run_grok.py run \
     --prompt-file /absolute/path/to/brief.md \
     --context-file /absolute/path/to/curated-context.md \
     --context-path /absolute/path/to/required-source \
     --cwd /absolute/path/to/workspace \
     --context-complete \
     --record-dir /absolute/path/to/work/team-grok-runs \
     --mode read-only
   ```

   - Use `read-only` for review, research, planning, and diagnosis.
   - Use `workspace` only when edits are authorized. Add `--writable-path` for each exact existing or new descendant path Grok may change. Grok edits a preserved copy; originals must remain unchanged.
   - Add `--allow-web` only when current web access is necessary and the supplied data is safe to combine with external browsing.
   - Use `--no-additional-context` only after Sol verifies the brief is self-contained.
   - Use one Grok run and at most one focused rework for a narrow, progressing defect. Do not quality-loop or automatically retry write runs.

6. Monitor quietly, review, and decide.
   - Do not require the user to poll. Use `run-status` or `list-runs` when a run is long or interrupted; status heartbeats distinguish running, failed, completed-unaccepted, and decided runs. Surface only meaningful progress, a privacy/authority blocker, or a result.
   - Require exit zero, `stopReason: end_turn`, positive usage for the selected model, exact receipt lines, stable config fingerprints, and `original_sources_unchanged: true`.
   - Compare all material claims and staged changes with the acceptance gates. Run proportionate checks independently with Sol.
   - Accept only when no semantic Sol repair is required. Otherwise reject; never integrate by confidence or self-attestation alone.
   - Record Sol's decision with `record-decision`: `accepted`, `rework`, `rejected`, `luna_escalated`, or `sol_completed`. A proof pack is evidence of a candidate run, not acceptance.
   - For workspace runs, selectively integrate only accepted changes, validate again in the real workspace, then safely delete the preserved stage:

   ```bash
   python3 /absolute/path/to/team-grok/scripts/run_grok.py stage-cleanup \
     --stage /private/var/.../team-grok-stage-.../workspace
   ```

7. Escalate once, then finish.
   - If Grok is substantively deficient, follow [the embedded Luna fallback](references/luna-fallback.md). Try one identity-proven Luna lane, with at most one focused follow-up if it is clearly progressing.
   - If Luna is unavailable or rejected, Sol completes the task. Never substitute Terra, generic Sol children, another model, or Grok role-playing Luna.

8. Report honestly.
   - Lead with the result. State one verified route: `Grok accepted`; `Grok rejected; Luna accepted`; `Grok rejected; Luna unavailable; Sol completed`; or `Grok and Luna rejected; Sol completed`.
   - Report checks, integration state, unresolved risks, and any preserved stage. Rejected worker output is not part of the finished result.
