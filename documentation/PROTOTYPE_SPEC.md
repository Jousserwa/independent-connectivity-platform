# Prototype 01 — Android to Authorized Gateway

## Purpose

Prove that an ordinary Android phone can securely connect to an internet gateway operated by or explicitly authorized for this project. This is a technical proof, not a public service launch.

## User-visible outcome

The app presents a simple flow:
1. Open the app.
2. See whether an approved gateway is available.
3. Sign in or activate a test entitlement.
4. Approve Android's VPN connection request.
5. Connect and verify internet reachability.
6. See gateway name, connection state, pass expiry, and a disconnect control.

The app must never display "Connected" solely because a tunnel interface was created. It must verify gateway reachability and an external health endpoint.

## Initial supported environment

- Android client: Kotlin.
- Android networking: `ConnectivityManager` and `VpnService`.
- Secure tunnel: maintained WireGuard implementation and compatible gateway tooling.
- Gateway: supported Linux distribution on a small cloud VM or controlled test server.
- Upstream: an internet connection whose owner and provider terms explicitly permit this test.
- Initial test devices: one physical Android phone; expand to additional Android versions after the first pass.

The minimum Android version and target SDK must be recorded in the build configuration after checking the chosen WireGuard Android integration's current requirements. Do not guess compatibility.

## Out of scope for Prototype 01

- Carrier billing workarounds or free access through restricted promotional/educational portals.
- Mesh routing, satellite connectivity, multi-gateway roaming, public user onboarding, payments, advertising, and production analytics.
- Claims of unlimited service.
- Production-grade high availability.

## Functional requirements

### Enrollment and authentication
- The test user obtains an account or one-time test credential through the control plane.
- The device creates its own WireGuard private key where the selected integration supports this model.
- The control plane stores only the public key and the minimum identity/entitlement data required.
- Credentials are short-lived, revocable, and never embedded in the APK or repository.

### Gateway selection
- The client receives a list of registered gateways from the control plane.
- A gateway is eligible only if it is registered, healthy, authorized for this service, and permitted by policy.
- The client tests reachability and chooses from eligible gateways only.
- No probing of arbitrary public gateways or carrier infrastructure.

### Tunnel lifecycle
- The user explicitly approves Android's VPN permission.
- The app starts and stops the tunnel through supported Android APIs.
- The client reports connecting, connected, reconnecting, expired, and failed states.
- Network changes trigger bounded recovery with backoff.
- Disconnect and expiry stop gateway egress according to policy.

### Connectivity verification
- Verify tunnel handshake.
- Verify DNS resolution through the intended path.
- Verify HTTPS reachability to a controlled health endpoint.
- Test that traffic follows the configured route and that no unintended traffic leaks when full-tunnel mode is selected.
- Display a clear error when the upstream gateway itself has no internet.

## Non-functional requirements

- No root required.
- No private key or token in source control, crash reports, or ordinary logs.
- Avoid collecting browsing history or payload contents.
- Stable behavior through screen-off, app backgrounding, Wi-Fi changes, and cellular handover within Android's platform limits.
- Record CPU, memory, battery, latency, throughput, packet loss, and reconnect time.
- Provide an emergency disconnect and a clear status indicator.

## Test matrix

| Test | Expected result |
|---|---|
| First-time VPN permission | Android system consent is shown; no silent VPN start |
| Valid test account | Authentication succeeds |
| Invalid or revoked credential | Gateway access denied |
| Valid entitlement | Tunnel and internet health checks pass |
| Gateway process stopped | Client reports loss and bounded recovery |
| Upstream internet removed | Tunnel may exist, but app reports no internet |
| Wi-Fi to mobile-data handover | Recovery succeeds or a clear unsupported-state error appears |
| Entitlement expires | Gateway blocks public egress; app reports expiry |
| User disconnects | Tunnel stops and gateway access ends |
| Reboot | No unexpected connection without configured user-approved behavior |

## Completion criteria

Prototype 01 is complete only when:
- the complete flow works repeatedly on a physical Android device;
- a second device can be enrolled without sharing private keys;
- invalid, revoked, and expired credentials are denied;
- connectivity checks distinguish tunnel-up from internet-up;
- reconnect and failure behavior are measured;
- no secrets are present in the repository;
- test evidence and known limitations are committed.

A successful emulator demo or a compiling APK alone is not sufficient.
