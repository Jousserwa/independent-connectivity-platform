# Development Roadmap

This roadmap is evidence-driven. Dates are intentionally omitted until the first prototype's scope and available test infrastructure are confirmed.

## Phase 0 — Foundation

- [x] Create separate public repository.
- [x] Define mission, legitimacy boundary, and initial architecture.
- [x] Establish security and contribution rules.
- [ ] Select project license after dependency and ownership review.
- [ ] Record target Android SDK/minimum supported Android version.
- [ ] Choose a reproducible development and test environment.

**Exit evidence:** documented decisions, clean repository, no secrets, and an agreed prototype specification.

## Phase 1 — Single authorized gateway

- [ ] Provision a small Linux gateway with an authorized upstream.
- [ ] Deploy and harden WireGuard using maintained upstream packages.
- [ ] Define a minimal authentication and device enrollment flow.
- [ ] Build a minimal Android app using Kotlin and Android `VpnService`.
- [ ] Establish tunnel, verify DNS and public reachability, and disconnect cleanly.
- [ ] Test on Android 10 and a current Android release.
- [ ] Record throughput, latency, packet loss, battery use, memory, and reconnect behavior.

**Exit evidence:** repeatable end-to-end test on physical devices, with logs and a documented threat model.

## Phase 2 — Control plane and duration passes

- [ ] Implement user/device identity with data minimization.
- [ ] Register gateways and publish health/capabilities.
- [ ] Issue, activate, expire, and revoke signed access entitlements.
- [ ] Enforce expiry at the gateway, not only in the app UI.
- [ ] Test clock drift, offline expiry, replay, token theft, and revocation.
- [ ] Add transparent speed/fair-use policy and capacity monitoring.

**Exit evidence:** automated tests demonstrate that valid passes work for their duration and expired/revoked passes cannot continue using gateway egress.

## Phase 3 — Automatic connectivity and resilience

- [ ] Discover eligible Wi-Fi and registered gateways.
- [ ] Score networks using authorization, health, latency, loss, and user cost.
- [ ] Handle Wi-Fi/cellular handover and Android background restrictions.
- [ ] Add bounded retry, backoff, and clear failure states.
- [ ] Verify no traffic leaks outside the intended tunnel when policy requires tunnel-only routing.

**Exit evidence:** repeatable handover and recovery tests under controlled network interruption.

## Phase 4 — Community node pilot

- [ ] Select an OpenWrt-capable router and compatible radio hardware.
- [ ] Obtain explicit site-owner and upstream-provider permission.
- [ ] Evaluate mesh software and license/maintenance status.
- [ ] Add node enrollment, monitoring, isolation, and remote update safeguards.
- [ ] Measure real coverage, interference, throughput, and backhaul contention.

**Exit evidence:** a small permitted field pilot with documented operating cost and support procedure.

## Phase 5 — Partnerships and expansion

- [ ] Assess Uganda Communications Commission requirements for the intended service model.
- [ ] Obtain legal review for ISP resale, public Wi-Fi, spectrum, consumer terms, and data protection.
- [ ] Explore wholesale bandwidth, sponsored access, schools, NGOs, businesses, and community hosts.
- [ ] Model cost per active user, peak concurrency, gateway utilization, and subsidy requirements.
- [ ] Expand to additional regions only after reliability and unit economics are proven.

**Exit evidence:** signed/approved upstream arrangements, regulatory pathway, sustainable operating model, and measured service quality.

## Release rule

A phase is not complete because code compiles or a demo works once. Completion requires repeatable tests, security review, documented limitations, and a rollback plan.
