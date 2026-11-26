# Initial Architecture

## 1. Objective

Provide a simple client experience over a collection of authorized access networks and gateways. The platform coordinates discovery, authentication, secure transport, access duration, and recovery. The gateway and its upstream provider supply the actual path to the internet.

## 2. System view

```text
                 CONTROL PLANE
       identity | gateway registry | access passes
                 | policy | health
                        |
                        v
ANDROID CLIENT ---> AUTHENTICATED GATEWAY ---> AUTHORIZED BACKHAUL ---> INTERNET
     |                      ^
     |                      |
     +-- network selection  |
     +-- WireGuard tunnel --+
     +-- status / recovery
                            |
                  COMMUNITY ACCESS NODE
                  Wi-Fi / OpenWrt / mesh
```

The community access node may be integrated with the gateway or may forward traffic to a gateway over a permitted mesh or wired link. A mesh transports packets between nodes; it does not itself create external internet connectivity.

## 3. Components

### Android client

Responsibilities:
- Discover available transports through Android's supported connectivity APIs.
- Evaluate only networks and gateways the platform is authorized to use.
- Authenticate with the control plane and obtain short-lived connection material.
- Request Android's VPN permission and establish a WireGuard tunnel.
- Report connection state, gateway health, pass expiry, and actionable errors.
- Recover safely after network changes, sleep, loss of signal, or gateway failure.
- Minimize battery, data, and personal-data use.

Constraints:
- No root requirement for the initial Android experience.
- The app must not silently route traffic or conceal its VPN behavior.
- Android's VPN consent and platform restrictions must be respected.
- Cellular traffic still uses the subscriber's carrier plan unless a valid carrier agreement says otherwise.

### Control plane

Responsibilities:
- User and device identity, with minimal collection.
- Gateway registration, capabilities, location granularity, and health.
- Access-pass issuance, activation, expiry, revocation, and audit events.
- Policy distribution and short-lived tunnel configuration.
- Abuse prevention, rate controls, and operational status.

The control plane should not store WireGuard private keys in plaintext. Prefer device-generated keys and narrowly scoped, short-lived authorization.

### Gateway and data plane

Responsibilities:
- Terminate authenticated tunnels.
- Enforce per-user network isolation and least-privilege firewall policy.
- Route authorized traffic to the contracted upstream.
- Apply transparent capacity controls and fair-use policy where required.
- Expose health and aggregate operational metrics without unnecessary browsing logs.
- Support safe revocation and incident response.

The gateway must have a real upstream connection with sufficient capacity. Its bandwidth has a cost even when a user pass is time-based.

### Community access and mesh

Candidate technologies include OpenWrt and established mesh-routing projects. Selection is deferred until the single-gateway prototype is measured. Mesh links require node-owner consent, appropriate radio settings, lawful spectrum use, and a permitted upstream arrangement.

## 4. Connection lifecycle

1. Client discovers a candidate access network or registered community gateway.
2. Client checks reachability and obtains gateway metadata from the control plane.
3. User authenticates and presents a valid pass or sponsored entitlement.
4. Device establishes an authenticated WireGuard tunnel.
5. Gateway verifies entitlement and applies policy.
6. Client monitors tunnel and underlying network health.
7. On loss or handover, client retries within bounded limits and does not claim connectivity until verified.
8. At pass expiry or revocation, the gateway blocks public egress and the client explains the next step.

## 5. Time-based access

A duration pass is feasible on infrastructure operated by, or contracted to, the platform. The entitlement can grant access until a timestamp rather than deducting a per-user data allowance. It does not mean unlimited physical capacity: congestion management, speed tiers, fair-use terms, and upstream costs must be disclosed.

A pass cannot transform a metered cellular connection into unmetered service. Carrier-sponsored or zero-rated access requires explicit agreement and technical provisioning by the carrier.

## 6. Network selection

Candidate scoring may consider:
- authorization and policy eligibility (hard requirement);
- gateway availability and health;
- latency, packet loss, and measured throughput;
- user-visible cost and entitlement;
- battery impact and stability;
- privacy and trust level.

Do not select a network solely because it appears to be unmetered or reachable through a restricted carrier portal.

## 7. Security boundaries

- Treat access networks as untrusted.
- Authenticate gateways and clients; rotate and revoke credentials.
- Use established cryptographic implementations.
- Isolate users at the gateway and prevent lateral access by default.
- Restrict management interfaces to authenticated administrators.
- Keep secrets out of source control, logs, crash reports, and client bundles.
- Rate-limit authentication and control-plane endpoints.
- Maintain patching, backup, monitoring, and incident-response procedures.

## 8. Deployment evolution

**Stage A:** one test Android device, one Linux gateway, one authorized upstream.

**Stage B:** multiple devices, automated enrollment, pass lifecycle, reconnect, and gateway monitoring.

**Stage C:** one community Wi-Fi/OpenWrt node with owner permission and measured backhaul.

**Stage D:** multiple gateways and mesh links, failover, capacity planning, and operational tooling.

**Stage E:** carrier, ISP, school, NGO, business, and satellite partnerships where commercially and legally approved.

## 9. Explicit non-goals

- Evading carrier billing, quota enforcement, captive portals, or access restrictions.
- Reusing educational or promotional access outside the provider's stated terms.
- Reproducing HTTP payload, SNI, proxy, or tunnel tricks to disguise unauthorized traffic.
- Claiming that VPN, DNS, mesh, or software alone can generate free internet.
- Building a global network before local reliability and unit economics are demonstrated.
