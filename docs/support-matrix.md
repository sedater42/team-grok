# Support matrix

| Surface | Status | Behavior |
|---|---|---|
| macOS, official signed Grok CLI, browser subscription login | Supported | Full subscription proof and isolated execution. |
| Grok CLI 1.0.5+ | Supported | Newer signed versions pass if required commands and result contract remain compatible. |
| New numeric subscription model | Adaptive | Highest `grok-X.Y` is selected automatically, with a Grok 4.6 floor. |
| Linux | Unsupported in 1.x | Fails closed; Linux binary provenance needs a vendor-verifiable design. |
| Windows | Unsupported in 1.x | Fails closed; process and staging semantics need a separate implementation. |
| xAI API key or custom endpoint | Forbidden | Run is refused; no API fallback. |
| Grok hooks/plugins/MCP/LSP/permission rules | Forbidden | Preflight refuses active extensions. |
| Ambient Grok skill metadata | Visible in inspect | Reported; skill tools are not exposed to the lane. |
| Bash and Grok subagents | Forbidden | Sol performs tests and side effects. |
| Web search/fetch | Opt-in | Available only with `--allow-web` and explicit privacy judgment. |
| Named Team Grok Luna role | Optional | Preferred when installed and identity-proven. |
| Explicit GPT-5.6 Luna spawn | Optional | Used when supported by the Codex runtime. |
| No Luna route | Supported | Sol completes after rejecting Grok. |
