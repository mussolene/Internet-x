# Release Notes: v0.2-mvp-n1

## Version

`v0.2-mvp-n1`

## Summary

Internet-X `v0.2-mvp-n1` is a runnable MVP prototype of an identity-first overlay architecture built around the explicit chain `Name -> Identity -> Locator -> Path`. This release packages a minimally real authenticated control-plane service, identity-bound flow establishment, and authenticated locator rebinding into a conservative reference profile with a real classical cryptographic baseline and an explicit simulated post-quantum transition boundary.

## New

- Authenticated control-plane service for registration, `Name -> Identity` resolution, `NodeID -> Locator` resolution, and locator update.
- Real `Name -> Identity -> Locator` runtime path in the reference implementation and demo.
- Locator rebinding through the service-backed runtime and authenticated in-band `LOCATOR_UPDATE`.

## Improved

- Spec, implementation, paper, and IETF-style draft wording aligned to the current MVP-N1 repository state.
- Test coverage and validation summaries aligned to the current repository state.
- Demo and benchmark reliability improved through the current service-backed runtime path.

## Security

- Real classical baseline: Ed25519, X25519, HKDF-SHA256, HMAC-SHA256, and ChaCha20-Poly1305.
- Explicit PQ simulation boundary: the repository exercises PQ negotiation and derivation hooks, but does not claim real post-quantum security.

## Limitations

- Single-instance, locally trusted control-plane service.
- No distributed resolver or federated control-plane design in this release.
- PQ mode is simulated and not production-ready.
- Overlay-only reference profile, not a full Internet replacement.

## How To Run

Start the demo:

```bash
python3 scripts/run_demo.py
```

Run the tests:

```bash
pytest -q tests
```
