# Positioning

## One-Sentence Positioning

Internet-X is an identity-first overlay transport architecture that combines explicit `Name -> Identity -> Locator -> Path` separation, identity-bound flow establishment, authenticated locator rebinding, and crypto-agile transition hooks into a packet-inspectable reference system.

## What Internet-X Is NOT

- not a replacement claim for the current Internet
- not a full routing architecture like SCION or a complete locator-mapping system like LISP deployment infrastructure
- not merely QUIC with a new name
- not a VPN product in the style of WireGuard
- not HIP, although HIP is the closest architectural ancestor in several respects
- not a proof that hybrid PQ transition should happen at this exact layer for every deployment
- not a production-ready post-quantum secure stack

## Strongest Distinct Contribution

The strongest distinct contribution is the explicit composition of four things that are often split across separate systems or documents:

1. stable identity as the anchor for communication state
2. an explicit locator-management control path for mobility and rebinding
3. readable, packet-inspectable flow establishment
4. explicit crypto agility and fallback semantics that are visible at the transport-overlay layer

The novelty is therefore narrow and compositional. The value is in how the pieces are packaged and made operational together.

## Claims We Can Defend

- Internet-X is identity-first by construction.
- The repository demonstrates authenticated locator rebinding in a runnable overlay implementation.
- The spec and code preserve the resolution chain `Name -> Identity -> Locator -> Path` rather than collapsing it into a single address token.
- The architecture is deployable as an overlay over current IPv4/IPv6 infrastructure.
- The implementation demonstrates a real classical security baseline and a clearly delimited simulated PQ transition hook.
- Under the repository's stated assumptions, the design is a strong design point for mobility-aware, inspectable, identity-bound overlay flows.

## Claims We Must Not Make

- Internet-X is wholly novel in the presence of HIP, LISP, ILNP, QUIC migration, MOBIKE, and other prior art.
- The current repository delivers real post-quantum security.
- The current code is production-ready or audited.
- The design is universally optimal across latency, complexity, deployability, and privacy.
- The directory and locator abstractions here are sufficient for real-world deployment.

## Why Near-Optimal Can Only Be Conditional

A design like Internet-X can only be argued as near-optimal after constraining the optimization target. In this repository, the defensible constraints are:

- overlay deployment over today's Internet
- stable identity independent of locator change
- explicit and inspectable control packets
- authenticated rebinding
- crypto agility with transition semantics

If those are the optimization criteria, then Internet-X is a strong or near-optimal composition. If the goal is minimal overhead, maximal installed-base compatibility, or zero new control plane concepts, then QUIC, WireGuard, or simpler secure overlays may dominate instead.
