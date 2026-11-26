# Control Plane

## Purpose

The control plane coordinates registered devices, eligible gateways, and time-based entitlements. It does not carry user internet traffic; the gateway handles the data plane.

## API contract

The initial API contract is in [openapi.yaml](openapi.yaml).

## Local-first development

The approved infrastructure budget is currently $0/month. The first implementation must therefore run locally in an existing development environment. No cloud deployment or paid managed database is authorized.

The implementation should begin with deterministic unit tests for:
- device public-key format validation;
- gateway registration and eligibility;
- entitlement activation and expiry;
- device revocation;
- authorization checks on tunnel configuration requests.

Use synthetic users, test keys, and local-only configuration. Keep production signing keys and credentials out of source control.

## Implementation boundary

The OpenAPI document is a contract, not a deployed service. No production API endpoint exists yet. A local development server must be clearly marked as a prototype and must not be exposed to the public internet.

## Future production requirements

Before public deployment, select persistent storage, authentication/session strategy, signing-key management, abuse controls, backups, monitoring, privacy retention, and an operational incident process. These decisions require a separate review.
