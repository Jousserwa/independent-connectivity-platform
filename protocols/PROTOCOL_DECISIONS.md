# Protocol and Dependency Decisions

This file records provisional choices. Every dependency must be checked for current maintenance, security advisories, Android compatibility, license obligations, and integration cost before production use.

## Decision 001 — Secure tunnel

**Provisional choice:** WireGuard using the maintained WireGuard Android implementation and standard Linux WireGuard tooling.

**Reasoning:** established protocol, small attack surface, modern cryptography, and existing Android/Linux implementations.

**Constraints:**
- Do not implement cryptographic primitives or a new VPN protocol.
- Keep private keys on the device where practical.
- Authenticate and authorize peers through the control plane.
- Document key rotation, revocation, routing, DNS, and MTU behavior.
- Verify the selected Android integration's license and supported Android versions before vendoring or depending on it.

## Decision 002 — Android platform integration

**Provisional choice:** Kotlin with Android `VpnService` and `ConnectivityManager`.

**Reasoning:** native platform APIs provide the correct user consent and network lifecycle integration without requiring root.

**Constraints:**
- Respect Android VPN consent and foreground-service requirements.
- Do not promise uninterrupted background operation beyond OS guarantees.
- Test on physical devices across supported Android versions.

## Decision 003 — Gateway operating system

**Provisional choice:** a maintained Linux server distribution for the first gateway.

**Reasoning:** simplest path to a measurable server-side WireGuard proof, firewall policy, and operational monitoring.

**Constraints:**
- Do not select a cloud provider or deploy billable infrastructure until the owner approves cost and region.
- Use a dedicated non-root service account where possible.
- Restrict management access; default-deny inbound firewall policy.

## Decision 004 — Mesh

**Status:** deferred.

OpenWrt and mature community mesh projects are candidates for a later phase. We will compare project health, device support, routing behavior, security, licensing, and field maintainability after the single-gateway proof passes.

## Decision 005 — Time-based entitlement

**Provisional model:** a signed or server-validated entitlement with a start time, expiry time, device binding, and revocation state. The gateway is authoritative for allowing or denying egress.

The exact token format and signing approach must be selected after defining the control-plane threat model and key-rotation process. Do not place signing secrets in the Android application.

## Review rule

A provisional decision is not permission to copy source code or deploy a dependency. Record the exact version, upstream source, license, security review, and reason for adoption before integration.
