# What Is Real Vs Simulated

## Real In This Repository

- identity-derived `NodeID`
- live authenticated control-plane service
- `Name -> Identity` and `NodeID -> Locator` resolution through that service
- Ed25519, X25519, HKDF-SHA256, HMAC-SHA256, and ChaCha20-Poly1305
- authenticated `LOCATOR_UPDATE` and `LOCATOR_UPDATE_ACK`
- end-to-end demo with post-update flow continuation

## Simulated Or Architectural Only

- `simulated-ml-kem-768` transition mode
- full `Path` layer beyond locator resolution
- federated or production-hardened control-plane infrastructure
- Internet-scale mobility, NAT traversal, or anti-DoS behavior

## Honest Boundary

The repository now clears the old nominal-control-plane blocker by using a live authenticated service. It still does not claim production readiness or real post-quantum security.
