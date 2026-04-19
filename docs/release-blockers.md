# Release Blockers

Audit date: April 19, 2026.

This file uses the repository's requested severity labels:
- `P0`: cannot call this `MVP-N1 READY`
- `P1`: repo works but claims/docs are unsafe or misleading
- `P2`: polish / publication quality issues
- `P3`: future work

## P0

1. The control plane is still only a local JSON directory and locator registry, not a minimally real multi-process or authenticated mapping service.
Reason: the core `Name -> Identity -> Locator` chain exists, but only as local artifacts prepared for demos and tests. That is acceptable for a research demo. It is not enough to label the repository `MVP-N1 READY` without stretching the meaning of MVP.

## P1

No open P1 blockers after audit fixes.

Resolved during audit:
- demo and benchmark scripts no longer assume a fixed UDP port is free;
- quickstart now includes dependency installation and the file-backed control-plane boundary;
- spec wording now matches actual duplicate-`DATA` and retransmission behavior.

## P2

1. The direct low-level CLI path is less turnkey than `make demo` because it still requires the user to prepare matching directory and registry files.
2. The test suite is meaningful and now covers real replay and stale locator-update cases, but it remains a compact loopback suite rather than a broad adversarial campaign.
3. Publication-quality claims depend on keeping the conservative framing intact; the repo should not drift back toward stronger maturity language.

## P3

1. Replace the simulated PQ mode with a real ML-KEM / ML-DSA backend behind the current agility surface.
2. Replace local JSON directory and registry artifacts with an authenticated control-plane service if the project moves beyond research-demo scope.
3. Add broader network-environment testing such as loss, reordering, and NAT traversal if operational claims are ever desired.
4. Implement the `Path` layer more concretely if the architecture claim is expanded beyond the current overlay reference profile.

## Summary

- Research-demo release blocker status: no open blockers.
- MVP-N1 release blocker status: blocked by the intentionally minimal control-plane implementation.
