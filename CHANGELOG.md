# Changelog

## Unreleased

### Added

- Minimal authenticated control-plane service with signed registration, signed locator update, `Name -> Identity` resolution, `NodeID -> Locator` resolution, and lease expiry.
- Service-backed control-plane tests for authenticated registration, resolution, locator update, stale update rejection, invalid signature rejection, and lease expiry.

### Changed

- `refimpl.client` and `refimpl.server` now use the live control-plane service instead of file-backed directory and registry inputs.
- Demo and benchmark scripts now start and use the control-plane service as the authoritative runtime control plane.
- Documentation and specs now describe the live service and its remaining local trust assumptions honestly.

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
