# Independent Connectivity Platform

An open, security-first platform for making reliable internet access more affordable through community connectivity, interoperable networks, and transparent time-based access.

## Mission

Build a client and infrastructure platform that helps people connect through **authorized, available networks** with as little configuration as possible. The long-term goal is to combine community Wi-Fi, mesh links, multiple backhaul providers, and approved carrier or satellite partnerships behind one simple experience.

This project does not create internet access from nothing, unlock paid carrier capacity, or bypass an operator's billing and access controls. Every route to the public internet requires an authorized upstream connection.

## Product principles

- **Access before complexity:** one clear connection experience; advanced networking stays behind the scenes.
- **Legitimate by design:** use networks with owner permission, lawful spectrum, valid ISP terms, and required regulatory approvals.
- **Time-based access where we control the gateway:** passes can grant a duration of service rather than a per-user data quota, subject to disclosed capacity and fair-use rules.
- **No false promises:** a VPN encrypts and routes traffic; it does not provide free bandwidth or change an upstream carrier's billing.
- **Privacy and security:** minimize personal data, protect credentials, isolate users, and use established cryptographic protocols.
- **Works on ordinary devices:** begin with Android without root; expand only after evidence from testing.
- **Incremental deployment:** prove a small gateway before attempting city-wide or global infrastructure.

## Initial technical direction

- Android client: Kotlin, Android Connectivity APIs, and Android `VpnService`.
- Secure tunnel: WireGuard using its maintained implementation; do not invent cryptography.
- Gateway: Linux-based, with explicit user isolation, firewall policy, traffic accounting for operations, and controlled egress.
- Control plane: authentication, gateway discovery, access-pass issuance, expiry, health, and policy.
- Community networking: evaluate OpenWrt and established mesh software after the single-gateway path works.
- Backhaul: lawful fiber, fixed wireless, mobile wholesale, satellite, or other contracted upstream service.

These are starting choices, not a commitment to integrate every component. Each dependency must pass maintenance, security, compatibility, and license review.

## Repository layout

```
android-client/       Android application
gateway-server/      Gateway provisioning and data-plane configuration
control-plane/       API, identity, entitlements, and gateway registry
mesh-network/        Community-node and mesh experiments
protocols/           Protocol decisions and interoperability notes
testing/             Test plans, fixtures, and validation records
documentation/       Product, deployment, privacy, and operations documents
```

## Development gates

1. **Secure single-gateway proof:** an Android device connects to an authorized Linux gateway using WireGuard, authenticates, and reaches the internet.
2. **Reliable user experience:** automatic network selection, reconnect, clear status, pass activation and expiry, and safe failure behavior.
3. **Operationally safe gateway:** isolation between users, firewall defaults, abuse controls, monitoring, and documented operator procedures.
4. **Community network pilot:** integrate a permitted Wi-Fi or mesh node and test real-world range, interference, throughput, and resilience.
5. **Scale and partnerships:** evaluate additional backhauls, sponsor-funded access, wholesale agreements, and regulatory requirements.

No later gate should be treated as complete until its tests and evidence are recorded.

## Development budget

The initial recurring infrastructure budget is currently **USD $0/month**. Development will proceed locally using existing equipment and free tooling. No paid server, domain, API, or subscription may be provisioned without explicit approval. See [ZERO_COST_DEVELOPMENT_PLAN.md](documentation/ZERO_COST_DEVELOPMENT_PLAN.md).

## Current status

The repository is at foundation/specification stage. No production service, Android app, gateway, carrier partnership, or free-internet capability is claimed to exist yet.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [ARCHITECTURE.md](ARCHITECTURE.md) before proposing implementation changes. Do not commit credentials, private keys, customer data, or live gateway configuration.

## License

No project-wide license has been selected yet. Until a license is added, do not assume that this repository's original code is licensed for unrestricted reuse. Third-party components retain their own licenses.
