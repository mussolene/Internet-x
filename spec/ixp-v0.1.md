# Internet-X Protocol Draft v0.1

## Introduction

Internet-X is an experimental network architecture built around a deliberate separation of naming, identity, reachability, and forwarding. The architecture treats stable identity as the primary anchor and models network communication as:

```text
Name -> Identity -> Locator -> Path
```

The goal is not to replace the Internet in its present form, nor to claim a deployment-ready stack. The goal is to define a technically serious research architecture that can be explored first as an overlay over IPv4 and IPv6 and later, if justified, through more native forms of deployment.

The repository includes an educational prototype that simulates the packet flow and handshake logic in a readable way. That prototype is intentionally not a secure implementation and must not be presented as real post-quantum or production-grade cryptography.

## Design Goals

Internet-X is designed around the following goals:

1. Preserve a stable cryptographic identity even when network attachment changes.
2. Keep human-readable naming distinct from the cryptographic identity used for protocol state.
3. Treat locator information as mutable reachability data rather than as identity.
4. Allow path-selection mechanisms to evolve independently of identity and locator semantics.
5. Support overlay-first deployment over existing IPv4 and IPv6 infrastructure.
6. Accommodate post-quantum and hybrid cryptographic mechanisms without pretending they are already deployed in the prototype.
7. Remain academically serious, explicit about assumptions, and conservative about operational claims.

## Architectural Model

The Internet-X architecture resolves communication state through four layers.

- `Name`: a human-meaningful label such as a service handle or endpoint name.
- `NodeID`: a cryptographic identity bound to key material.
- `Locator`: current information needed to reach the node over an underlying transport substrate.
- `Path`: the chosen route through an overlay or future routing plane.

The critical architectural claim is that these are not interchangeable fields.

A `Name` MAY change without changing a `NodeID`.
A `Locator` MAY change without changing the `NodeID`.
A `Path` MAY change without changing either `NodeID` or `Locator`.

Session continuity is intended to be anchored in identity and flow state rather than in a single locator.

## Identity Model

Internet-X models node identity as a digest over algorithm identity and public key material:

```text
NodeID = HASH(algorithm_id || public_key)
```

The exact digest function and serialization rules are protocol parameters, but the architecture requires:

- explicit identification of the public-key algorithm family
- a deterministic mapping from algorithm identifier and public key to `NodeID`
- a `NodeID` size large enough to be cryptographically meaningful

In the architectural design, the following algorithm families are relevant:

- ML-KEM as a candidate post-quantum KEM
- ML-DSA as a candidate post-quantum signature scheme
- hybrid classical-plus-post-quantum operation
- classical fallback where post-quantum mechanisms are unavailable

The educational prototype in this repository simulates key material and uses standard-library hashing only to make identity and transcript handling observable. It does not implement ML-KEM, ML-DSA, or any equivalent secure primitive.

## Name / Identity / Locator / Path Separation

Internet-X treats the resolution chain explicitly:

1. A `Name` is resolved to a `NodeID`.
2. A `NodeID` is resolved to one or more `Locator` values.
3. A `Path` is selected relative to policy, topology, or overlay routing conditions.

This separation matters because the classical IP model often forces an address to serve simultaneously as identity, current attachment point, and routing token. Internet-X rejects that overloading.

Implications include:

- a node can preserve identity while moving between locators
- multihomed nodes can advertise multiple locators without identity ambiguity
- path selection can change without requiring a new identity
- applications can bind to identity-level state without exposing topology as identity

## Packet Model

Internet-X packets conceptually include both identity context and current reachability hints. The architecture does not assume 32-bit identifiers for `NodeID`, `Locator`, or `FlowID`.

At a high level, a packet contains:

- `Version`
- `PacketType`
- `Flags`
- `HeaderLength`
- `FlowID`
- `SourceNodeID`
- `DestinationNodeID`
- `LocatorHint`
- `Payload`

`SourceNodeID` and `DestinationNodeID` identify principals, not addresses.
`LocatorHint` carries current reachability information and may be absent, partial, or updated over time.
`FlowID` binds packets to a session or sub-session context and must be stronger than a trivial 32-bit token.

The educational prototype serializes this model as JSON for readability, not as a production wire format.

## Session and Flow Model

A session is established between stable identities and may persist across locator changes. A `FlowID` identifies a concrete communication instance derived from handshake context.

Architecturally:

- session state is identity-bound
- locator state is mutable
- flow state is derived from authenticated handshake context

The prototype approximates this with:

- a handshake `session_id`
- a transcript hash derived from exchanged packets
- a `FlowID` derived from the session identifier, transcript context, and node identities

The prototype uses SHA-256-derived hex strings for `FlowID` to avoid the misleading signal of short or weak identifiers. This remains an educational stand-in for a real design.

## Handshake Model

Internet-X v0.1 keeps a five-phase handshake:

1. `INIT`
2. `INIT_ACK`
3. `KEM_EXCHANGE`
4. `AUTH`
5. `DATA`

In the architecture, these phases provide:

- session bootstrap
- mode negotiation
- exchange of key-establishment material
- identity-bound authentication
- transition to flow-associated data transfer

The educational prototype preserves the phase names exactly and represents each phase as a JSON packet. `DATA_ACK` is used after application data transfer as an acknowledgement packet. It is not a replacement for any of the required five phases.

The prototype simulates hybrid post-quantum behavior by carrying algorithm and mode metadata such as `hybrid-simulated` and `classical-simulated`. These strings are descriptive only.

## Mobility Model

Internet-X assumes that identity is stable while locator information may change.

The architecture therefore treats mobility as a locator-management problem rather than as an identity reset. In a fuller system, a locator update would allow subsequent packets in the same identity-bound flow to continue over a new attachment point or overlay ingress.

This repository does not fully implement locator migration, but the model it preserves is:

- `NodeID` remains stable across movement
- `Locator` may change
- the flow concept should survive locator changes

Any implementation that collapses `NodeID` and `Locator` would violate the architecture.

## Deployment Model

Internet-X is defined here as overlay-first.

Initial deployment assumptions:

- the protocol rides over existing IPv4 and IPv6 networks
- overlay nodes exchange Internet-X packets inside conventional transport envelopes
- locator values may describe current overlay ingress or UDP reachability

Possible future direction:

- more native deployment models that reduce dependence on the overlay substrate

This draft does not claim native deployment today. It does not claim replacement of the current Internet. It defines a research direction that can be evaluated incrementally.

## Security Considerations

Internet-X is identity-oriented, but this repository must be read with care.

Architectural security goals include:

- binding session state to cryptographic identity rather than locator alone
- supporting transcript-bound flow derivation
- enabling hybrid classical-plus-post-quantum negotiation
- permitting locator change without losing identity continuity

Repository limitations include:

- the prototype uses simulated key material
- the prototype does not implement real confidentiality or authentication
- JSON packets are used for readability, not wire efficiency or hardened parsing
- the prototype must not be used for operational security claims

Security discussion in this repository is therefore partly architectural and partly educational. Those layers must not be conflated.

## Post-Quantum Integration

Internet-X is post-quantum-ready in design, not post-quantum-complete in implementation.

The intended direction is:

- ML-KEM for key establishment
- ML-DSA for signatures
- hybrid operation with classical mechanisms during transition
- classical fallback for environments that cannot yet support post-quantum mechanisms

The educational prototype simulates these roles through metadata and transcript handling so the surrounding architecture can be exercised before real cryptographic integration.

## Future Work

Important future directions include:

- explicit locator update packets and mobility procedures
- path-selection and overlay routing semantics
- multi-locator and multihoming behavior
- real cryptographic profiles for classical and post-quantum operation
- binary wire encoding beyond the educational JSON representation
- stronger interoperability language in a more mature Internet-Draft

Internet-X should be judged here as a serious exploratory architecture with a readable prototype, not as a completed secure protocol stack.
