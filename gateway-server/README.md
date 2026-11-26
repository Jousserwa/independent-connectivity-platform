# Gateway Server

## Role

The gateway is the first controlled internet egress point for the prototype. It terminates authorized WireGuard peers, enforces device and entitlement policy, isolates clients, and forwards permitted traffic through an upstream connection that is explicitly authorized for this service.

## Do not deploy yet

This directory is a design placeholder. No server has been provisioned, no provider selected, and no production firewall or WireGuard configuration is present. Do not paste private keys, provider credentials, or live IP addresses into this repository.

A cloud VM may incur recurring charges. Provisioning must wait until the project owner approves the provider, region, monthly budget, and operating limits.

## Required capabilities

- Maintained Linux distribution with security updates.
- WireGuard kernel module or supported userspace implementation.
- Default-deny host firewall.
- Separate management access from client tunnel traffic.
- Per-device peer registration and revocation.
- Client-to-client isolation by default.
- Controlled DNS policy.
- Egress policy tied to current entitlement state.
- Health endpoint and aggregate resource metrics.
- Secure configuration backup and tested recovery.
- Rate limiting and abuse response.

## Network policy

The initial prototype should use a documented full-tunnel route only when the user explicitly chooses that mode and the Android client has established the VPN. The gateway must reject unregistered peers and deny forwarding between client peers. Management ports must never be exposed to the client tunnel network.

## Entitlement enforcement

The gateway must deny new sessions without a valid entitlement and terminate or block egress when an entitlement expires or is revoked. The control plane is authoritative for entitlement state; the gateway must fail closed if it cannot validate a new authorization. Existing sessions need a bounded revalidation interval.

A time-based entitlement is not a claim of infinite bandwidth. Capacity limits, speed policies, fair-use rules, and upstream costs remain real and must be explained to users.

## Provisioning checklist

- [ ] Owner approves provider, region, budget, and spending limit.
- [ ] Upstream service terms permit the intended gateway use.
- [ ] OS is patched and administrative access hardened.
- [ ] Firewall defaults to deny inbound traffic.
- [ ] WireGuard peer policy and key rotation documented.
- [ ] Client isolation verified.
- [ ] Entitlement expiry and revocation tested.
- [ ] Monitoring, backup, and incident response tested.
- [ ] No secrets committed to this repository.
