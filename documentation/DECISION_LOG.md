# Decision Log

Record consequential architecture, security, deployment, and product decisions here. Include date, context, alternatives, decision, consequences, and revisit conditions.

## D-001 — Separate platform repository

**Status:** Accepted

**Decision:** Develop the connectivity platform in its own repository, separate from unrelated applications and creative projects.

**Reason:** Keeps ownership, release history, security review, and contributor scope independent.

## D-002 — Authorized connectivity only

**Status:** Accepted

**Decision:** The platform may connect users only through networks and gateways that the project is authorized to use. It will not disguise traffic or bypass carrier billing, quotas, captive portals, or restricted access programs.

**Reason:** The product must be technically sustainable, lawful, safe for users, and acceptable to upstream providers.

## D-003 — Single gateway before mesh

**Status:** Accepted

**Decision:** Prove Android-to-gateway connectivity before adding mesh routing, multiple backhauls, or satellite integration.

**Reason:** A measured single-gateway service is the smallest end-to-end proof of the core product.

## D-004 — No paid infrastructure without owner approval

**Status:** Accepted

**Decision:** Do not create cloud resources, subscriptions, domains, or other billable services without explicit approval of provider, region, budget, and spending limit.

**Reason:** Prototype work must not create unapproved recurring costs.

## D-005 — Time-based access at controlled gateways

**Status:** Accepted

**Decision:** Prototype duration-based entitlements only where the platform controls the gateway or has an explicit wholesale/sponsored agreement.

**Reason:** A VPN cannot change how a mobile operator meters its upstream service. Time-based access is enforceable only where the service operator controls or contracts the access path.
