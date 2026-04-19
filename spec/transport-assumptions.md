# Transport Assumptions

## Underlay

The current reference implementation assumes a UDP overlay over IPv4/IPv6. It does not require changes to the underlay network.

## Path Layer

The repository keeps `Path` explicit in the architecture but does not implement a routing-plane path-selection algorithm. In this release:

- the locator determines the current overlay destination
- the path is effectively the underlay route chosen by the network plus local endpoint policy

## Deployment Assumption

Internet-X should be evaluated here as an endpoint protocol package that can be deployed incrementally in an overlay, not as a clean-slate network-layer replacement.
