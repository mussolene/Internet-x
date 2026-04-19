# Cryptographic Agility

## Why Agility Is Explicit

Internet-X treats algorithm selection as part of the protocol surface because the repository's claim includes PQ transition readiness and fallback discipline.

## Current Negotiation Surface

Classical secure suite:

- `x25519+ed25519+chacha20poly1305`

PQ modes:

- `simulated-ml-kem-768`
- `none`

## Fallback Semantics

Fallback is not silent.

- the initiator advertises whether classical fallback is allowed
- the responder sets `fallback_used`
- the chosen PQ mode is carried in `INIT_ACK` and `AUTH`
- transcript mismatch or control-field tampering causes failure, not downgrade acceptance

## Future Evolution

A future implementation could replace the simulated PQ mode with real ML-KEM while preserving the same negotiation and documentation surface.
