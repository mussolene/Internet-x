# Novelty Matrix

## Summary Matrix

| Property | Internet-X | HIP | LISP | ILNP | QUIC+TLS 1.3 | IKEv2/MOBIKE | WireGuard | Novelty Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stable cryptographic endpoint identity | Yes | Yes | Partial, via EID namespace but not identity-bound host auth in same way | Identifier split, not public-key-first in the same style | Connection ID, not cryptographic endpoint identity | SA-bound identity, not general endpoint namespace | Static keys, but VPN-oriented | High overlap with HIP |
| Explicit `Name -> Identity -> Locator -> Path` chain | Yes | Partial | Partial (`EID -> RLOC`) | Identifier/locator split | No explicit chain | No explicit chain | No | Moderate |
| Overlay-first deployment | Yes | Yes | Yes | Can coexist but not framed the same way | Runs over UDP but not as identity/locator overlay | Runs over IP/IPsec | Yes | High overlap |
| Packet-inspectable flow establishment | Yes, by design | Yes | Control plane separate | Mostly architectural | Handshake integrated with transport | Exchange-driven | Yes, but tunnel-oriented | Moderate |
| Authenticated locator rebinding in same flow model | Yes | Yes | Partially in endpoint LISP variants | Conceptually yes | Connection migration | Yes via MOBIKE | Roaming support | High overlap |
| Hybrid/fallback PQ transition semantics at this layer | Yes, explicit in design | No native PQ transition framing | No | No | Strong hybrid TLS work exists | Draft work exists in IPsec/IKE | Optional PSK only | Moderate |
| Human-readable reference overlay package | Yes | Less so in modern runnable form | Mostly standards and deployments | Mostly architectural RFCs | Production stacks exist but different problem | Production security stack, different problem | Production-oriented VPN | Lower |

## Feature-Level Comparison

| Feature | Internet-X delta | Overlap | Difference | Risk of “not novel” |
| --- | --- | --- | --- | --- |
| Identity-first anchor | Very close to HIP | HIP | Internet-X keeps the chain explicit and packages it as an inspectable overlay transport package | High |
| Locator split | Overlaps with LISP and ILNP | LISP, ILNP | Internet-X binds it directly to endpoint-authenticated flow logic and rebinding procedure | High |
| Explicit flow establishment | Overlaps with HIP/IKEv2/QUIC/WireGuard | Many | Internet-X makes identity, locator, and flow semantics visible in one packet model | Medium |
| Mobility control path | Overlaps with HIP UPDATE and MOBIKE | HIP, MOBIKE | Internet-X keeps rebinding close to the endpoint flow layer and makes locator updates directly inspectable | High |
| PQ transition framing | Overlaps with hybrid TLS and IKE drafts | TLS hybrid design work | Internet-X exposes hybrid/fallback semantics at its own overlay layer | Medium |
| Transition story | Overlaps with LISP overlay deployment and HIP overlays | HIP, LISP | Internet-X aims at a narrower deployable reference package with identity-bound flow semantics | Medium |

## Bottom Line

Internet-X is not defensibly novel because it invented identity/locator split, mobility support, or authenticated flow establishment. The strongest defensible novelty lies in the protocol composition, document coherence, and transition packaging of those ideas under one explicit architectural chain.
