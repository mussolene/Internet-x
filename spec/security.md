# Security

## Threat Model

In scope:

- off-path spoofing of control packets
- replay of previously seen data packets
- transcript tampering and downgrade attempts
- locator hijack attempts during a live flow
- malformed packet injection

Out of scope:

- endpoint compromise
- malicious or fully compromised control-plane infrastructure
- large-scale denial-of-service resistance
- side-channel resistance
- traffic analysis and metadata privacy against a global observer

## Security Goals

1. Bind session establishment to stable cryptographic identities.
2. Detect transcript tampering and downgrade attempts.
3. Protect application data confidentiality and integrity after `AUTH`.
4. Reject unauthenticated locator changes.
5. Keep claim boundaries explicit when PQ is simulated.

## Mechanisms

- Ed25519 signatures authenticate handshake and locator update control fields.
- Ed25519 signatures authenticate control-plane registration and control-plane locator updates.
- X25519 plus HKDF-SHA256 derives the base session secret.
- ChaCha20-Poly1305 protects application data.
- sequence numbers provide replay protection for data packets.
- HMAC-based key confirmation proves possession of the derived session keys.

## Limitations

- common headers remain visible, which leaks metadata
- no production anti-DoS measures are implemented
- PQ support is architectural and simulated, not real
- the control plane is a single minimal service and remains a local trust anchor for availability and admission policy
