# Internet-X Protocol Draft v0.2

## Abstract

Internet-X is an identity-first overlay architecture that separates naming, stable endpoint identity, current locator state, and path selection. This draft specifies the current MVP-N1 runnable reference profile in which endpoints establish an identity-bound flow over a UDP overlay, authenticate control packets, protect application data, and support authenticated locator rebinding.

## Motivation

Classical IP addressing overloads topology and endpoint naming. That makes mobility, rebinding, and policy separation harder to reason about. Internet-X responds by making the resolution chain explicit:

```text
Name -> Identity -> Locator -> Path
```

The repository does not claim this split is new. It claims that packaging the split with explicit flow establishment, authenticated rebinding, and crypto-agile transition semantics remains useful and technically defensible.

## Terminology

- `Name`: human-meaningful handle used for lookup
- `Identity`: stable cryptographic node identity represented by `NodeID`
- `Locator`: current reachability token used to deliver overlay packets
- `Path`: route or policy-selected forwarding choice relative to a locator
- `Session`: handshake context created by `INIT`
- `Flow`: authenticated post-`AUTH` communication context identified by `FlowID`

## Identity Model

The reference profile uses:

```text
NodeID = SHA-256(algorithm_id || signing_public_key_b64)
```

The `NodeID` is stable across locator changes. Locator change alone must never imply identity change.

## Architectural Overview

1. A node registers its `Name`, `NodeID`, and current locator with the control plane using an identity-bound signed request and a bounded lease.
2. A client resolves a `Name` to an identity record through the control plane.
3. The client resolves that identity to a current locator through the control plane.
3. The client establishes an authenticated flow against the resolved identity.
4. The client and server may later authenticate a new locator for the same identity-bound flow.
5. A node that changes locator updates the control plane with a higher locator version so future resolution reflects the new endpoint.

## Packet Model

The common packet envelope is described in [`spec/packet-format.md`](/Users/maxon/git/me/Internet-x/spec/packet-format.md). The reference implementation uses JSON serialization for inspectability.

## Handshake Model

The handshake is defined in [`spec/handshake.md`](/Users/maxon/git/me/Internet-x/spec/handshake.md). The required phase sequence is:

- `INIT`
- `INIT_ACK`
- `KEM_EXCHANGE`
- `AUTH`
- `DATA`

The responder returns `DATA_ACK` after receiving application data.

## Flow Model

A flow exists only after `AUTH` succeeds. `FlowID` is derived from transcript and identity context. Data packets prior to `AUTH` are invalid.

## Mobility Model

Locator change is handled through an authenticated `LOCATOR_UPDATE` exchange. The design intent is:

- identity remains stable
- locator changes explicitly
- flow continuity survives locator rebinding when the rebinding is authenticated

## Cryptographic Profile

The current reference profile is:

- Ed25519 for signatures
- X25519 for classical ephemeral key agreement
- HKDF-SHA256 for key derivation
- ChaCha20-Poly1305 for AEAD-protected data
- optional simulated hybrid PQ context using `simulated-ml-kem-768`

This is a real classical baseline with a simulated PQ extension point.

## Timeout And Retransmission

The reference implementation includes built-in client retry logic for the early control path (`INIT` and `KEM_EXCHANGE`). On the server side, cached responses allow idempotent handling of duplicate `INIT`, `KEM_EXCHANGE`, and `DATA` packets if a caller retransmits them. The current client does not automatically retry application `DATA` on timeout.

## Deployment Model

Internet-X is overlay-first in this repository release. Packets ride over UDP on current IPv4/IPv6 networks. No claim is made that native deployment or routing-plane replacement is complete.

## Threat Model And Security Considerations

The security model is defined in [`spec/security.md`](/Users/maxon/git/me/Internet-x/spec/security.md). The important claim boundary is that the repository supports real authenticated and encrypted classical flows, but not real PQ security.

## Limitations

- single minimal authenticated control-plane service only
- no full path-selection plane
- JSON packet overhead
- limited privacy for visible control metadata
- no Internet-scale evaluation

## Example Trace

A successful run includes:

```text
INIT -> INIT_ACK -> KEM_EXCHANGE -> AUTH -> DATA -> DATA_ACK
```

and optionally:

```text
LOCATOR_UPDATE -> LOCATOR_UPDATE_ACK -> DATA -> DATA_ACK
```
