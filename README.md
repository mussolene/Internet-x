# Internet-X

Internet-X is an identity-first overlay architecture organized around an explicit resolution chain:

```text
Name -> Identity -> Locator -> Path
```

This repository is the `v0.2-mvp-n1` release candidate. It is a runnable MVP prototype with a real classical cryptographic baseline, a minimally real authenticated control-plane service, authenticated locator rebinding, and an explicit simulated post-quantum transition boundary. It is not production-ready, not a full Internet replacement, and not a claim of current post-quantum security.

## Status

- Release target: `v0.2-mvp-n1`
- Repository maturity: `MVP-N1 READY`
- Scope: experimental overlay reference profile
- Trust boundary: single-instance, locally trusted control-plane service

## Architecture

```text
Human name
  -> control-plane Name -> Identity lookup
  -> control-plane Identity -> Locator lookup
  -> identity-bound UDP overlay handshake
  -> authenticated flow
  -> optional authenticated locator rebinding

Path remains architectural only in this release.
```

## What Works Now

- `refimpl/` provides a runnable Python reference implementation.
- The control plane is a separate authenticated HTTP service for registration, `Name -> Identity` resolution, `NodeID -> Locator` resolution, and locator updates.
- The handshake establishes an identity-bound flow with real classical cryptography: Ed25519, X25519, HKDF-SHA256, HMAC-SHA256, and ChaCha20-Poly1305.
- The demo shows a single handshake, authenticated locator rebinding, and post-update data delivery on the same logical flow.
- The repository includes automated tests, a local benchmark harness, a bounded invariant model, a paper draft, and an IETF-style draft aligned to the current implementation.

## What Is Simulated Or Bounded

| Area | Status | Boundary |
| --- | --- | --- |
| Classical crypto baseline | Real | Implemented in the reference code |
| PQ transition surface | Simulated / pluggable | `simulated-ml-kem-768` exercises negotiation and derivation hooks only |
| Control plane | Real, minimal | Single-instance and locally trusted; not federated or hardened |
| Path layer | Architectural only | No standalone routing or path-selection subsystem |
| Formal analysis | Bounded | Machine-checkable invariants, not a complete proof |
| Performance evidence | Local only | Loopback benchmark, not Internet-scale evaluation |

## How To Run

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run tests:

```bash
pytest -q tests
```

Run the demo:

```bash
python3 scripts/run_demo.py
```

Additional validation:

```bash
python3 scripts/benchmark.py
python3 formal/bounded_model.py
make paper-check
```

## Limitations

- The control plane is intentionally central, single-instance, and locally trusted.
- `Path` is explicit in the architecture but not implemented as a routing plane.
- PQ support is simulated and pluggable, not production post-quantum cryptography.
- The implementation is a Python UDP overlay, not a kernel-integrated transport.
- The evaluation is loopback-scale and does not establish deployment readiness.

## Roadmap

- Harden and broaden the control plane beyond the current local-trust MVP model.
- Replace the simulated PQ hook with a real backend behind the existing agility surface.
- Extend evaluation beyond loopback, including loss and WAN-like conditions.
- Decide whether the future work should remain one overlay protocol package or split into smaller components.

## Key References

- [Release notes](/Users/maxon/git/me/Internet-x/RELEASE_NOTES_v0.2.md)
- [Changelog](/Users/maxon/git/me/Internet-x/CHANGELOG.md)
- [Spec](/Users/maxon/git/me/Internet-x/spec/ixp-v0.2.md)
- [Control-plane notes](/Users/maxon/git/me/Internet-x/docs/control-plane.md)
- [What is real vs simulated](/Users/maxon/git/me/Internet-x/docs/what-is-real-vs-simulated.md)
- [Demo validation](/Users/maxon/git/me/Internet-x/docs/demo-validation.md)
- [Test results](/Users/maxon/git/me/Internet-x/docs/test-results.md)
- [Paper draft](/Users/maxon/git/me/Internet-x/paper/internetx.tex)
- [IETF-style draft](/Users/maxon/git/me/Internet-x/ietf/draft-internetx-00.md)
