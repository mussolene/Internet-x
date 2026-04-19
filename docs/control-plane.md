# Control Plane

Internet-X now includes a minimally real authenticated control-plane service for the explicit `Name -> Identity -> Locator` part of the architecture.

## What It Does

- accepts signed registration for `Name`, `NodeID`, algorithm, signing public key, and current locator
- serves `Name -> Identity` resolution over HTTP
- serves `NodeID -> Locator` resolution over HTTP
- accepts signed locator updates bound to the same identity
- enforces bounded lease expiry and monotonic locator versions

## Runtime Shape

- service process: `python3 -m refimpl.controlplane_service`
- write authentication: Ed25519 signature over canonical JSON fields
- read path: simple HTTP JSON responses
- state model: single in-process registry with optional JSON snapshot for diagnostics

## Freshness Model

The service uses two simple freshness controls:

1. lease expiry: every registration or locator update carries `issued_at` plus `lease_seconds`
2. locator version monotonicity: locator updates must use a higher `locator_version` than the currently active record

This is enough to reject obviously stale writes in the current local-trust MVP scope without turning the control plane into a broad distributed system.

## Trust Boundary

What is real:

- the service is a separate networked process
- registration and locator updates are authenticated against the node identity
- stale or incorrectly signed updates are rejected
- demo and runtime resolution go through the service

What is still limited:

- the service is single-instance and locally trusted
- reads are not access-controlled
- there is no federation, external PKI, or hardened persistence layer
- lease refresh is caller-driven rather than managed by a background agent

## Relationship To Flow Rebinding

The control plane and the in-band locator update serve different purposes:

- `LOCATOR_UPDATE` preserves an already established flow
- the control-plane locator update ensures future resolution reflects the new locator

That split preserves the repository's identity-first and mobility-aware semantics without widening the scope into a full routing system.
