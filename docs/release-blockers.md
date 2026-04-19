# Release Blockers

Audit date: April 19, 2026.

This file uses the repository's requested severity labels:
- `P0`: cannot call this `MVP-N1 READY`
- `P1`: repo works but claims/docs are unsafe or misleading
- `P2`: polish / publication quality issues
- `P3`: future work

## P0

No open P0 blockers after the control-plane remediation pass.

## P1

No open P1 blockers after audit fixes.

Resolved during the audit and remediation passes:
- demo and benchmark scripts no longer assume a fixed UDP port is free;
- quickstart now includes dependency installation and the live control-plane boundary;
- spec wording now matches actual duplicate-`DATA` and retransmission behavior;
- the runtime and demo control plane are now backed by a separate authenticated service.

## P2

1. The control plane is intentionally central and minimal; it is suitable for MVP-N1 but not a hardened or federated deployment substrate.
2. The test suite is meaningful and now covers authenticated control-plane behavior, but it remains a compact loopback suite rather than a broad adversarial campaign.
3. Publication-quality claims depend on keeping the conservative framing intact; the repo should not drift toward stronger production or novelty language.

## P3

1. Replace the simulated PQ mode with a real ML-KEM / ML-DSA backend behind the current agility surface.
2. Add lease refresh, persistence hardening, and tighter admission policy if the control plane moves beyond local-trust MVP scope.
3. Add broader network-environment testing such as loss, reordering, and NAT traversal if operational claims are ever desired.
4. Implement the `Path` layer more concretely if the architecture claim is expanded beyond the current overlay reference profile.

## Summary

- Research-demo release blocker status: no open blockers.
- MVP-N1 release blocker status: no open P0 blockers in the current repository state.
