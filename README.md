# Internet-X: Identity-First Experimental Network Architecture

Internet-X is an experimental network architecture that separates concerns classical IP tends to conflate. Its organizing model is:

```text
Name -> Identity -> Locator -> Path
```

Where:

- `Name` is a human-readable identifier.
- `Identity` is a stable cryptographic identifier (`NodeID`).
- `Locator` is current reachability information.
- `Path` is the selected route through an overlay or future routing plane.

Internet-X is intentionally identity-first, mobility-aware, overlay-first in its initial form, and post-quantum-ready in design. It is a research repository, not a production network stack and not a claim that the current Internet can be replaced overnight.

## Architectural Position

Internet-X keeps the following separations explicit:

- A `Name` is resolved to a `NodeID`, not directly to an IP address.
- A `NodeID` is derived from cryptographic key material and remains stable across locator changes.
- A `Locator` reflects where a node is reachable now and may change over time.
- A `Path` is a routing or overlay decision that is separate from both identity and locator.

This separation is intended to make mobility, multihoming, and future routing evolution easier to reason about than in a locator-bound architecture.

## Post-Quantum-Ready Design

The architecture is designed to accommodate hybrid operation:

- ML-KEM as a candidate post-quantum KEM
- ML-DSA as a candidate post-quantum signature scheme
- hybrid classical-plus-post-quantum operation
- classical fallback where post-quantum mechanisms are unavailable

The repository prototype does not implement real post-quantum cryptography. Any key material, handshake proofs, or transcript bindings in the prototype are simulated for educational purposes.

## Repository Layers

The repository deliberately distinguishes two layers.

### Layer 1: Architecture and Specification

This layer captures the actual Internet-X idea:

- identity-first naming and routing
- `NodeID = HASH(algorithm_id || public_key)`
- explicit `Name`, `NodeID`, `Locator`, and `Path` separation
- overlay-first deployment over IPv4 and IPv6
- mobility-aware sessions and flows
- hybrid post-quantum integration goals

### Layer 2: Educational Prototype

This layer is a readable simulation used to exercise the architecture:

- localhost UDP transport
- JSON packet serialization
- the five-phase handshake: `INIT`, `INIT_ACK`, `KEM_EXCHANGE`, `AUTH`, `DATA`
- `DATA_ACK` as a post-data confirmation
- simulated cryptographic material
- transcript hashing and `FlowID` derivation helpers

The prototype exists to make the architecture concrete. It does not provide real security.

## Repository Layout

```text
internet-x/
├── README.md
├── spec/
│   ├── ixp-v0.1.md
│   ├── handshake.md
│   └── packet-format.md
├── ietf/
│   └── draft-internetx-00.md
├── paper/
│   ├── abstract.md
│   └── internetx.tex
├── examples/
│   ├── handshake-trace.txt
│   └── packet-examples.md
└── prototype/
    ├── README.md
    ├── protocol.py
    ├── node.py
    ├── server.py
    └── client.py
```

## Handshake Overview

The educational prototype keeps these phases explicit:

1. `INIT`
2. `INIT_ACK`
3. `KEM_EXCHANGE`
4. `AUTH`
5. `DATA`

The prototype then uses `DATA_ACK` to confirm application data receipt. Session and flow state are carried in JSON packets so the architecture is easy to inspect.

## Deployment Model

Internet-X is defined here as an overlay architecture first:

- initial deployment rides over IPv4 and IPv6
- current reachability is expressed as a `Locator`
- future native deployment is a research direction, not current scope

This repository does not claim native deployment today.

## Status

Current status:

- architecture draft and exploratory documentation
- IETF-style draft material
- educational Python prototype for the handshake and packet model

Not current status:

- production readiness
- complete routing plane
- real post-quantum cryptography
- full mobility implementation

## Prototype Quick Start

From the repository root:

```bash
python3 prototype/server.py
```

In a second terminal:

```bash
python3 prototype/client.py
```

See `prototype/README.md` for details.

## License

MIT License. See `LICENSE`.
