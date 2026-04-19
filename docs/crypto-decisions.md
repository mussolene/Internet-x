# Crypto Decisions

## Decision 1: Keep The Reference Implementation In Python

Reason:

- faster path to a coherent research package
- easier packet inspection and demo tooling
- acceptable for a reference implementation where clarity matters more than raw speed

## Decision 2: Use Real Classical Crypto Instead Of Full Simulation

Reason:

- the repository needed to move beyond conceptual security claims
- a real classical baseline materially improves technical credibility
- the available environment already supported the needed `cryptography` primitives

## Decision 3: Keep PQ Mode Explicitly Simulated

Reason:

- real ML-KEM/ML-DSA would add complexity and environmental assumptions
- the repository goal is honest transition design, not false PQ claims
- simulated PQ shares are sufficient to exercise negotiation and fallback semantics

## Decision 4: Keep JSON Packets

Reason:

- packet inspectability is a semantic invariant for this repository
- a research package benefits from transparent control messages
- the implementation remains debuggable and traceable packet by packet

Tradeoff:

- more overhead than a compact binary format
- weaker privacy properties for visible metadata

## Decision 5: Authenticate Locator Update At The Session Layer

Reason:

- mobility is central to the design
- locator update must be bound to the identity-authenticated flow, not trusted as a naked network event
- this choice aligns the code with the architecture's main claim surface
