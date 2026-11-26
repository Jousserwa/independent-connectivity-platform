# Zero-Cost Development Plan

## Budget constraint

The approved recurring infrastructure budget for the initial development stage is **USD $0 per month**.

Until the project owner explicitly approves a different limit:
- Do not create, activate, or upgrade cloud resources.
- Do not purchase domains, hosting, VPS instances, certificates, paid APIs, or subscriptions.
- Do not enable paid usage tiers or leave billable resources running.
- Prefer local development, emulators, open-source tooling, and existing equipment.
- Clearly identify any optional tool that could incur charges before recommending its use.

## What can be built at $0

1. Repository architecture, API contracts, Android source, gateway configuration templates, and automated tests.
2. A local control-plane service running on an existing computer or development environment.
3. A local Linux gateway using an existing Linux machine or VM, if available.
4. Android client development and build verification using the Android SDK and a compatible local build environment.
5. WireGuard tunnel tests between devices on an authorized local network, provided a suitable Linux host and Android device are available.
6. Security reviews, threat modelling, static analysis, and documentation using free tools.

## What cannot be claimed yet

- A public internet gateway available to users around the world.
- Free or unmetered cellular data.
- A functioning mesh or satellite network without compatible hardware, authorized upstream service, and operational nodes.
- Production availability, public user onboarding, or unlimited bandwidth.

A local gateway still uses its upstream connection. If that connection is cellular, the carrier's normal data plan and charges still apply. The prototype must never present a VPN tunnel as a way to avoid those charges.

## Local development topology

Preferred topology when an existing computer is available:

```text
Android phone
    |
    | Wi-Fi on a network the owner is authorized to use
    |
Existing Linux computer / local VM
    |-- local control-plane API
    |-- WireGuard gateway
    |-- test health endpoint
    |
Existing authorized internet connection
```

If no suitable Linux computer is available, continue with source development, unit tests, API contract validation, and Android build setup until one is available. Do not rent a server to fill the gap.

## Cost gate

Before any future paid deployment, obtain explicit approval for:
- provider and service;
- region;
- monthly and one-time cost;
- bandwidth/egress pricing;
- automatic renewal and spending cap;
- shutdown and deletion procedure.

## Next engineering sequence

1. Confirm the available local development environment and Android build path.
2. Build a minimal local control-plane service against `control-plane/openapi.yaml`.
3. Add unit tests for enrollment validation, gateway eligibility, entitlement expiry, and revocation.
4. Build the Android client shell and VPN permission/status flow.
5. Integrate the maintained WireGuard Android implementation only after its current license and compatibility are checked.
6. Test against a local gateway when an authorized Linux host is available.
7. Record repeatable test evidence before expanding scope.
