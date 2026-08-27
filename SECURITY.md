# Security policy

## Supported versions

Security fixes are provided for the latest tagged 1.x release.

## Reporting a vulnerability

Do not open a public issue for a suspected credential leak, sandbox escape, subscription-routing bypass, unsafe stage deletion, or arbitrary-command path. Use GitHub's private vulnerability reporting for the repository. Until a public repository is configured, contact the maintainer privately through the publishing account.

Include the Team Grok version, macOS/Python/Grok CLI versions, reproduction steps using synthetic data, and the observed versus expected result. Never include real credentials, subscription cookies, raw memory, or proprietary source.

## Scope

Particularly relevant reports include unsigned binary acceptance, API route acceptance, secret/symlink staging bypass, original-workspace mutation, forged lifecycle metadata, unsafe cleanup target acceptance, or unbounded process/output behavior.
