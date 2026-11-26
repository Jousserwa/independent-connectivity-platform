# Android Client

## Goal

Build a native Android application that makes connection to an authorized platform gateway straightforward. The first version targets a single test gateway and does not attempt mesh discovery or carrier-specific workarounds.

## Planned responsibilities

- Show authentication and device enrollment state.
- Generate and protect the device's WireGuard private key locally.
- Register only the public key with the control plane.
- Display eligible gateways and their health.
- Obtain a tunnel configuration after server-side entitlement checks.
- Request Android VPN permission using the supported system flow.
- Start, monitor, and stop the tunnel.
- Verify internet reachability separately from tunnel handshake.
- Display access-pass start and expiry times.
- Recover safely after network changes and report failures clearly.

## Platform constraints

- No root access.
- Use Android `VpnService` and `ConnectivityManager`.
- Respect VPN consent, foreground-service requirements, background execution limits, and user disconnect actions.
- Do not claim seamless connectivity where Android or the underlying network cannot guarantee it.
- Do not embed production API secrets, gateway private keys, or signing keys in the APK.

## WireGuard integration

Use the maintained WireGuard Android implementation or its documented embeddable integration. Before adding a dependency, record the exact upstream version, license, Android compatibility, security advisories, and integration approach in `protocols/PROTOCOL_DECISIONS.md`.

Do not create a custom cryptographic tunnel or silently fork protocol behavior.

## Current status

No Android source code, Gradle project, APK, or deployed API exists in this directory yet. The implementation begins after confirming the selected SDK/dependency compatibility and the gateway test environment.
