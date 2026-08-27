# Architecture

The control flow is deliberately asymmetric:

```text
User -> Sol reconciles context -> signed subscription Grok CLI -> isolated stage
             |                                      |
             +----------- verifies ----------------+
                              |
            proof/status -> accept / one rework / reject
                              |
                 optional identity-proven Luna
                              |
                         Sol completes
```

The runner is a local policy enforcement point. `doctor` validates binary provenance, CLI compatibility, configuration, login, model catalog, and disabled extension surfaces. `run` requires Sol's context-coverage attestation, creates a marked temporary workspace, copies only explicit sources, creates a private prompt, applies a per-path write allowlist, and launches Grok with a minimal environment and explicit tools. A private per-run record starts before preflight and stores heartbeats, hashes, model evidence, configuration fingerprints, context receipts, source integrity, changes, and stage lifecycle. Grok completes as unaccepted; Sol records one machine-readable decision after independent review.

This is strong staging and fail-closed routing, not a complete sandbox. Sol remains responsible for data classification, semantic review, authoritative tests, selective integration, and final communication.
