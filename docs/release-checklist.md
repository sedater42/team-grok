# Release checklist

- [ ] Unit tests pass on Python 3.9, 3.11, and 3.13.
- [ ] Skill and plugin validators pass.
- [ ] Secret scan and static syntax checks pass.
- [ ] `doctor` passes on a trusted Mac with the current signed Grok CLI.
- [ ] Read-only live smoke passes with receipt, usage, and source-integrity evidence.
- [ ] Workspace live smoke preserves edits, originals remain unchanged, and cleanup succeeds.
- [ ] Context-complete and must-read gates cover nested task dependencies.
- [ ] Durable preflight/run status, heartbeat, proof pack, changes record, immutable Sol decision, and history commands agree.
- [ ] Workspace smoke allows only exact descendant/new output paths and rejects another staged edit.
- [ ] Negative smokes reject API env/config, symlinks, secrets, overlaps, missing login, model downgrade, active/malformed/ambiguous extensions, invalid usage, invalid receipts, and unsafe cleanup targets.
- [ ] Exact disabled-compatibility MCP and instruction records are ignored and separately reported; incomplete disabled evidence still fails closed or remains gated.
- [ ] `_GROK_CLAUDE_MARKER_OVERRIDE` is runner-controlled as the exact string `1` and cannot be inherited from the caller.
- [ ] README support matrix and privacy notice match current behavior.
- [ ] `compatibility.json`, plugin version, runner version, and changelog agree.
- [ ] Git working tree contains no credentials, session data, test stages, or personal paths.
- [ ] Tag is signed or otherwise provenance-verified; release archive checksum is published.
- [ ] Live subscription credentials are never used in CI.
