# Changelog

## Unreleased

No entries yet.

## v0.2-mvp-n1 - 2026-04-19

### New

- Minimal authenticated control-plane service with signed registration, signed locator update, `Name -> Identity` resolution, `NodeID -> Locator` resolution, and lease expiry.
- Service-backed control-plane tests for authenticated registration, resolution, locator update, stale update rejection, invalid signature rejection, and lease expiry.
- Release notes for the `v0.2-mvp-n1` MVP packaging pass.

### Improved

- `refimpl.client` and `refimpl.server` use the live control-plane service instead of file-backed directory and registry inputs.
- Demo and benchmark scripts start and use the control-plane service as the authoritative runtime control plane.
- README, specs, docs, paper materials, and the IETF-style draft now use a consistent MVP-N1 claim boundary and control-plane description.
- Release-facing validation summaries now reflect the current repository state.

### Security

- The release is anchored to a real classical baseline: Ed25519, X25519, HKDF-SHA256, HMAC-SHA256, and ChaCha20-Poly1305.
- The post-quantum surface remains explicitly simulated and pluggable; no real ML-KEM or ML-DSA security is claimed.

### Limitations

- The control plane remains single-instance and locally trusted.
- `Path` remains architectural only.
- The evaluation package remains loopback-scale and overlay-only.

## v0.1 - 2026-04-19

### Added

- New `refimpl/` reference implementation with real classical authenticated session establishment and encrypted data exchange.
- JSON-backed name directory and locator registry abstractions.
- Authenticated locator update control packets.
- Automated tests for parsing, handshake success, retransmission, downgrade detection, locator update, formal invariants, and multi-node sessions.
- Benchmark and demo scripts.
- Complete spec set under `spec/`.
- Prior-art, novelty, positioning, crypto, test, evaluation, evidence, and publication docs.
- Paper draft, bibliography, figures, and Internet-Draft.
- Formal bounded invariant model.

### Changed

- Root README rewritten around the current implementation and explicit claim boundaries.
- `examples/` updated to represent the current v0.2 protocol story.
- `prototype/README.md` reframed as legacy context.

### Deprecated

- `prototype/` as the primary runnable artifact. It remains for historical comparison only.
