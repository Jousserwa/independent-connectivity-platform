# Gateway Acceptance Test Plan — Prototype 01

## Preconditions

- A Linux server or VM is controlled by the project team.
- The upstream connection is authorized for this use.
- Administrative access is secured.
- No production user data is present.
- A test Android device and test identity are available.

## Setup evidence to record

- Linux distribution and version.
- CPU, RAM, storage, region, and network interface details.
- Upstream provider and applicable permission/terms reference (do not publish account secrets).
- WireGuard package/version.
- Firewall implementation and ruleset revision.
- Android model, Android version, app build, and WireGuard integration version.

## Acceptance checks

| ID | Check | Pass condition |
|---|---|---|
| GW-01 | Server baseline | Patched OS, non-root service, firewall enabled |
| GW-02 | Tunnel handshake | Registered test device completes authenticated handshake |
| GW-03 | Client isolation | One client cannot access another client's private tunnel address |
| GW-04 | Egress policy | Only explicitly permitted routes can reach the upstream |
| GW-05 | DNS behavior | DNS follows documented tunnel policy |
| GW-06 | Expiry enforcement | Expired entitlement loses gateway egress |
| GW-07 | Revocation | Revoked device loses access within documented revocation interval |
| GW-08 | Upstream outage | Client distinguishes tunnel connectivity from internet availability |
| GW-09 | Recovery | Client reconnects within measured bounds after controlled interruption |
| GW-10 | Secret hygiene | No private keys, tokens, or passwords in repository or logs |
| GW-11 | Resource baseline | CPU, RAM, throughput, latency, and packet loss recorded under test load |
| GW-12 | Operational recovery | Gateway can be safely restarted and configuration restored from documented backup |

## Measurements

Record at minimum:
- handshake success rate;
- median and p95 latency;
- throughput in both directions;
- packet loss;
- reconnect duration;
- concurrent test clients;
- gateway CPU and memory;
- device battery impact over a defined test period.

Do not invent targets before a baseline is measured. Set acceptance thresholds after the first controlled run and state the test conditions.

## Test report template

- Date/time and test operator:
- Gateway environment:
- Client device/build:
- Test IDs executed:
- Results (pass/fail/blocked):
- Measurements:
- Logs or sanitized evidence:
- Defects:
- Security observations:
- Known limitations:
- Reviewer:
- Follow-up decision:

Never include passwords, private keys, access tokens, subscriber identifiers, or personal browsing data in the report.
