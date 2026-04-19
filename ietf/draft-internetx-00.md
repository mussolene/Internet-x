# Internet-Draft: Internet-X Identity-First Overlay Transport

Intended status: Experimental  
Expires: October 2026

## Abstract

This document describes Internet-X, an identity-first overlay architecture that separates names, stable endpoint identities, mutable locators, and selected paths. The current repository draft defines an experimental MVP reference profile with an explicit flow-establishment sequence, authenticated locator update, a minimally real authenticated control-plane service, and a crypto-agility surface for hybrid and fallback operation.

## Status Of This Memo

This document is a repository draft for discussion. It is not an IETF working group item.

## 1. Introduction

Internet-X aims to make explicit a four-step communication model:

```text
Name -> Identity -> Locator -> Path
```

The design goal is not to prove that this split is new, but to package it into an overlay transport reference profile with explicit mobility and rebinding semantics.

## 2. Terminology

- `Name`: human-readable lookup token
- `NodeID`: stable cryptographic identity token
- `Locator`: current overlay reachability token
- `Path`: forwarding or policy choice relative to the locator
- `SessionID`: bootstrap context identifier
- `FlowID`: authenticated post-establishment flow identifier

## 3. Architecture

A node resolves a peer name to a peer identity, resolves that identity to a current locator, and then establishes an authenticated flow. Locator change does not imply identity change.

## 4. Packet Format

All packets share a common envelope containing:

- version
- packet type
- flags
- header length
- session ID
- flow ID
- sequence number
- source `NodeID`
- destination `NodeID`
- locator hint
- payload

The current reference profile serializes packets as JSON for inspectability.

## 5. Handshake Procedure

### 5.1 INIT

The initiator sends identity material, supported suites, supported PQ modes, and an ephemeral classical key.

### 5.2 INIT_ACK

The responder returns its identity material, selected suite, selected PQ mode, transcript hash, and ephemeral classical key.

### 5.3 KEM_EXCHANGE

The initiator proves possession of the initiator identity key, contributes any selected hybrid-transition material, and confirms the transcript.

### 5.4 AUTH

The responder authenticates the transcript, confirms possession of the session keys, and publishes `FlowID`.

### 5.5 DATA

Data packets use `FlowID` and a per-sender sequence number. Payloads are encrypted in the current reference profile.

## 6. Locator Update

A peer that changes locator sends `LOCATOR_UPDATE` carrying the new locator, previous locator, a monotonic counter, a signature, and a MAC. The peer MUST NOT accept a locator update unless the session is already established and both the signature and MAC validate.

## 7. Cryptographic Agility

The current reference profile supports one real classical secure suite and two PQ-mode states:

- `x25519+ed25519+chacha20poly1305`
- `simulated-ml-kem-768`
- `none`

When fallback occurs, that fact is explicit in the control packets. The current implementation does not claim real ML-KEM or ML-DSA support.

## 8. Error Handling

Peers send `ERROR` when they detect malformed packets, unsupported suites, transcript mismatch, failed authentication, wrong `FlowID`, or stale locator update counters.

## 9. Security Considerations

The protocol aims to bind flows to stable identities rather than locators alone, detect transcript tampering, resist basic replay on data packets, and require authentication for locator rebinding. The current reference profile does not attempt to hide all metadata, and the repository implementation relies on a single-instance, locally trusted authenticated control-plane service rather than a distributed or hardened deployment.

## 10. Deployment Considerations

Internet-X is defined here as an overlay-first design. It is intended to coexist with current IPv4/IPv6 infrastructure. This document does not specify a global naming service, routing plane, or deployment-grade locator service, and it does not claim to replace the existing Internet.

## 11. IANA Considerations

None in this repository draft.

## 12. References

Informative references used in the repository include RFC 9063, RFC 7401, RFC 8046, RFC 9299, RFC 9300, RFC 6740, RFC 9000, RFC 9001, RFC 7296, RFC 4555, the WireGuard protocol overview, the hybrid TLS design draft, and NIST FIPS 203/204.
