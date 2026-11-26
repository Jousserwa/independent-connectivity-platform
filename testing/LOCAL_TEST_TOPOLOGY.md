# Local Test Topology

## Goal

Test the first client-to-gateway connection without renting cloud infrastructure or purchasing new hardware.

## Required existing equipment

- An Android phone that supports the selected Android client.
- An existing computer capable of running a supported Linux environment (native Linux or a local VM).
- A local Wi-Fi/router network that the tester is authorized to use.
- An existing internet connection if testing public internet reachability.

If any item is unavailable, do not purchase it automatically. Continue with the parts that can be tested offline.

## Network layout

```text
[Android phone]
       |
       | local Wi-Fi
       |
[Existing Linux host]
  - local API
  - WireGuard server
  - health-check endpoint
       |
[Existing router / authorized ISP]
       |
    Internet
```

## Test modes

### Mode A — Offline development

- Validate API schemas and local unit tests.
- Build Android screens and state handling.
- Test enrollment and entitlement logic with mock data.
- No external internet or gateway is required.

### Mode B — Local tunnel

- Run the gateway on an existing Linux host.
- Connect the Android phone over a permitted local network.
- Confirm WireGuard handshake and gateway reachability.
- Verify DNS and HTTPS health checks.
- Confirm disconnect, expiry, and revocation behavior.

### Mode C — Internet egress

- Forward authorized traffic through the Linux host's existing upstream.
- Confirm public reachability through an HTTPS health endpoint.
- Measure latency, throughput, packet loss, and host resource use.
- Make clear that the upstream ISP/mobile provider still supplies and bills the internet connection according to its terms.

## Safety

- Do not expose the local gateway's management ports to the public internet.
- Do not use a third-party Wi-Fi network without owner permission.
- Do not publish local IP addresses, private keys, or test credentials in public issues.
- Use test accounts and synthetic data only.
- Remove test peers and credentials after the test.
