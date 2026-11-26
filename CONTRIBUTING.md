# Contributing

Thank you for helping build a reliable and accessible connectivity platform.

## Before opening a change

1. Read [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [SECURITY.md](SECURITY.md).
2. Check existing issues and discussions to avoid duplicating work.
3. For major changes, propose the design and trade-offs before implementation.
4. Keep changes focused and document how they were tested.

## Engineering standards

- Prefer maintained, well-reviewed protocols and libraries over custom cryptography.
- Do not weaken Android platform security or bypass user consent.
- Do not implement carrier billing evasion, unauthorized tunneling, captive-portal circumvention, or disguised traffic.
- Keep platform-specific code isolated and document supported versions.
- Make failure states explicit; never report a connection as online until reachability is verified.
- Include tests for authentication, expiry, revocation, network handover, and failure recovery.
- Record performance and battery measurements on real hardware where possible.
- Document deployment assumptions and rollback steps.

## Repository hygiene

- Never commit secrets, personal data, private gateway configuration, generated credentials, or large build artifacts.
- Use example configuration files with clearly fake values.
- Check third-party licenses and attribution requirements before adding dependencies or copied code.
- Do not add a project-wide license or claim third-party code is relicensed without approval.

## Pull requests

A good pull request includes:
- problem and intended outcome;
- architecture or API impact;
- security and privacy considerations;
- tests performed and results;
- known limitations and follow-up work.

Small, reviewable changes are preferred over large unverified rewrites.
