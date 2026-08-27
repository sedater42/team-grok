# Contributing

Keep changes clean-room, portable within the support matrix, and fail closed on authentication or provenance uncertainty.

1. Create a focused branch.
2. Update tests for every behavior change.
3. Run `python3 -m unittest discover -s skills/team-grok/tests -v` and `python3 -m unittest discover -s tests -v`.
4. Run the skill and plugin validators.
5. Update the changelog, compatibility manifest, privacy/threat-model docs, and support matrix when applicable.
6. Use synthetic fixtures. Never commit Grok sessions, credentials, raw Codex memory, personal paths, staged user source, or live model output containing private data.

Live subscription smokes run only on a trusted local Mac. CI remains offline and credential-free.
