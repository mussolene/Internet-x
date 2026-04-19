# Research Log

## Repository Audit Baseline

Audit date: April 19, 2026.

Initial repository state before this task:

- `README.md` described the high-level idea but not a full engineering package.
- `spec/ixp-v0.1.md`, `spec/handshake.md`, and `spec/packet-format.md` covered the architecture in a narrow, mostly educational form.
- `prototype/` contained a readable UDP/JSON handshake simulation with simulated cryptographic material.
- `paper/internetx.tex` was still placeholder LaTeX.
- `ietf/draft-internetx-00.md` was empty.
- No prior-art survey, novelty matrix, formal model, evaluation method, or reproducible evidence pack existed.
- No real classical cryptographic baseline existed in the runnable code.

## Contradictions Found During Audit

1. The repository wanted to sound like a serious architecture but still anchored itself to a purely simulated prototype.
2. The paper and I-D artifacts did not reflect the actual code or specs.
3. The project implied novelty more broadly than the prior art justified.
4. Mobility and locator update semantics were discussed architecturally but not implemented in the runnable prototype.
5. Post-quantum readiness was described, but the repo did not clearly distinguish real security from transition-oriented simulation.

## Prior-Art Anchors Used

Primary references used for positioning:

- HIP architecture and base exchange: RFC 9063 and RFC 7401
- HIP mobility and multihoming: RFC 8046 and RFC 8047
- LISP architecture and protocol: RFC 9299 and RFC 9300
- ILNP architecture: RFC 6740
- QUIC transport and TLS binding: RFC 9000 and RFC 9001
- IKEv2 and MOBIKE: RFC 7296 and RFC 4555
- WireGuard protocol overview: [wireguard.com/protocol](https://www.wireguard.com/protocol/)
- IETF hybrid PQ TLS design: [draft-ietf-tls-hybrid-design](https://datatracker.ietf.org/doc/html/draft-ietf-tls-hybrid-design)
- NIST PQ standards: [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) and [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final)
- Limited patent scan: [US8516243B2](https://patents.google.com/patent/US8516243B2/en) and related locator/identity mobility families

## Design Decisions Made

1. Keep Python for speed and readability.
2. Add a new `refimpl/` package instead of mutating the earlier educational prototype into something it was not designed to support.
3. Use a real classical baseline: Ed25519, X25519, HKDF-SHA256, ChaCha20-Poly1305.
4. Preserve explicit packet inspectability by keeping JSON packets and clear headers while encrypting data payloads.
5. Treat PQ support as a documented agility surface and simulated hybrid context, not as fake real PQ security.
6. Implement authenticated locator update to make mobility first-class in the runnable code.
7. Narrow the novelty claim to composition, control semantics, and transition packaging.

## Implementation Milestones

- Added a new `refimpl/` package with identity, directory, packet, crypto, and engine modules.
- Added CLI tools for key generation, server, and client.
- Added locator update and replay-aware data handling.
- Added tests for parsing, retransmission, downgrade detection, locator update, and multi-node sessions.
- Added a bounded machine-checkable invariant model in `formal/`.
- Rewrote the documentation set, paper, and I-D around the actual implementation.

## Remaining Research Risks

- Novelty is still compositional rather than primitive-level.
- The evaluation is small-scale and local.
- Privacy implications of stable identity and locator exposure remain significant.
- The current directory and registry abstractions are intentionally weak compared with a deployment-grade system.
