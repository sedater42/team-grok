# Threat model

## Assets

- user source files and curated context
- Grok subscription session state
- original workspace integrity
- Sol's acceptance authority
- truthful model/auth/usage reporting

## Trust assumptions

The local user, Codex/Sol lead, macOS kernel, Apple code-signing tools, and official xAI-signed Grok CLI are trusted within their documented roles. Grok model output, staged edits, source-file instructions, web content, and ambient local extensions are untrusted.

## Defenses

- fixed executable location plus pinned xAI Team ID
- subscription marker and API/provider exclusion on every run
- minimal child environment and optional telemetry controls disabled
- extension/config discovery with fail-closed checks
- explicit, non-overlapping regular-file context only; symlinks, hard links, and common secret paths refused
- hash-before/copy/hash-after staging with original-source recheck
- no Bash, subagents, memory, workflows, or default web
- bounded turns, timeout, response size, and exact model-usage evidence
- exact receipt syntax plus independent Sol review
- marked and owner-checked stage cleanup
- one rework and one Luna escalation ceiling to prevent retry loops

## Residual risks

- secret heuristics cannot classify every sensitive string
- xAI receives delegated content and may process it under its service policies
- the Grok CLI can enumerate ambient skill metadata even though skill tools are not exposed
- vendor sandbox or CLI behavior may change after an update
- a receipt is model self-attestation
- malicious source text can still influence model reasoning
- `HOME` is required for subscription state, so the signed CLI retains whatever access the OS and its own sandbox permit
- workspace stages persist until cleanup

Team Grok therefore reduces blast radius; it is not a security boundary suitable for secrets or hostile multi-tenant code.
