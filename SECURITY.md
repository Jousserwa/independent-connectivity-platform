# Security Policy

## Scope

Security matters across the Android client, control plane, gateways, mesh nodes, build pipeline, and operational infrastructure.

## Reporting a vulnerability

Do not publish exploitable details, credentials, private keys, personal data, or live gateway addresses in public issues.

Until a dedicated private security contact is established, report suspected vulnerabilities privately to the repository owner through GitHub's private vulnerability reporting feature if it is enabled. If it is not enabled, request a private contact route without posting exploit details publicly.

Include:
- affected component and version/commit;
- impact and realistic attack conditions;
- minimal reproduction steps or a proof of concept that does not access third-party systems;
- suggested mitigation, if known.

Please allow time for triage and remediation before public disclosure.

## Security requirements

- Never commit passwords, API tokens, private keys, signing keys, recovery codes, or production configuration.
- Use device-generated WireGuard private keys where practical; do not transmit private keys to the control plane.
- Keep secrets in a dedicated secret manager or protected deployment environment.
- Authenticate and authorize every control-plane and gateway management operation.
- Use short-lived credentials, replay protection, revocation, and rate limiting.
- Isolate client traffic and block lateral access by default.
- Apply least privilege to services, containers, users, and firewall rules.
- Keep dependencies pinned and review advisories before upgrades.
- Log security events with care; avoid collecting browsing history or payload contents.
- Provide secure update, rollback, backup, and incident-response procedures.

## Privacy

Collect the minimum data required to provide and secure the service. Define retention periods before collecting identifiable telemetry. Explain clearly what connection metadata is collected and who can access it.

## Testing boundary

Only test systems, networks, and accounts for which you have explicit authorization. Do not probe carrier infrastructure, captive portals, or third-party gateways without permission.
