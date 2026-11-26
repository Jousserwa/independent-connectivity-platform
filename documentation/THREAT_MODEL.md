# Initial Threat Model

## Assets to protect

- Device private keys and session credentials.
- User identity and access entitlements.
- Gateway administrative access and signing keys.
- User traffic confidentiality and isolation.
- Gateway availability and upstream capacity.
- Control-plane integrity and entitlement records.

## Trust boundaries

1. Android app and operating system.
2. Untrusted local access network (Wi-Fi or cellular).
3. Public control-plane API.
4. WireGuard tunnel endpoint on the gateway.
5. Gateway operating system and firewall.
6. Upstream ISP or backhaul provider.
7. Other users sharing the same gateway.

## Threats and required controls

| Threat | Initial control |
|---|---|
| Stolen device credential | Short-lived credentials, device revocation, rate limits |
| Private-key exposure | Device-side key generation; never commit keys; protected storage |
| Rogue gateway | Authenticated gateway identity and pinned/verified configuration |
| Replay of access token | Short expiry, nonce or one-time redemption where appropriate |
| Pass expiry bypass | Enforce expiry at gateway, not only in app |
| Cross-user traffic access | Per-client isolation and default-deny firewall |
| Control-plane compromise | Least privilege, MFA for administrators, secret manager, audit events |
| Denial of service | Rate limits, capacity controls, monitoring, abuse response |
| DNS or traffic leakage | Explicit routing policy and leak tests |
| Malicious community node | Treat nodes as untrusted; authenticate links; isolate clients |
| Supply-chain compromise | Pin dependencies, review updates, verify release artifacts |
| Excessive data collection | Data minimization, documented retention, avoid browsing logs |

## Privacy baseline

The prototype should collect only what it needs to authenticate a device, enforce an entitlement, operate a gateway, and diagnose service health. Prefer aggregate counters and short-lived operational events over destination histories. Publish a clear notice before any external pilot.

## Residual risks

A secure tunnel protects traffic between the client and gateway; it does not make the gateway, upstream provider, DNS resolver, destination website, or device inherently trustworthy. The gateway operator can observe metadata needed to route traffic. HTTPS remains important. A compromised phone can expose data before encryption.

## Authorization boundary

Only test gateways, devices, accounts, and networks for which the project has explicit permission. Do not test carrier portals, restricted educational bundles, third-party Wi-Fi, or provider infrastructure without written authorization.
