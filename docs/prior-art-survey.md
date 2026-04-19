# Prior-Art Survey

## Scope

This survey focuses on the protocols and design families most likely to overlap with Internet-X's claim surface.

## HIP

Primary sources: [RFC 9063](https://www.rfc-editor.org/rfc/rfc9063.html), [RFC 7401](https://www.rfc-editor.org/rfc/rfc7401.html), [RFC 8046](https://www.rfc-editor.org/rfc/rfc8046.html), [RFC 8047](https://www.rfc-editor.org/rfc/rfc8047.html).

HIP is the closest ancestor. It introduces a public-key-based host identity layer, separates identifiers from locators, and includes authenticated exchange plus mobility and multihoming extensions. Internet-X overlaps heavily with HIP on identity-first communication and mobility semantics.

Internet-X differs mainly in presentation and composition:

- the explicit `Name -> Identity -> Locator -> Path` chain is a first-order explanatory device
- the reference implementation is intentionally packet-inspectable and overlay-oriented
- crypto agility and PQ transition semantics are given explicit architectural treatment

Conclusion: novelty risk is highest relative to HIP.

## LISP

Primary sources: [RFC 9299](https://www.rfc-editor.org/rfc/rfc9299.html), [RFC 9300](https://www.rfc-editor.org/rfc/rfc9300.html).

LISP cleanly separates endpoint identifiers and routing locators and is explicitly overlay-friendly. It also has a strong deployment story around mapping systems and encapsulation. However, classic LISP is more routing/control-plane oriented and does not itself serve as an endpoint-authenticated flow-establishment protocol.

Conclusion: heavy overlap on locator/identifier split and overlay deployment; less overlap on identity-bound flow establishment.

## ILNP

Primary source: [RFC 6740](https://www.rfc-editor.org/rfc/rfc6740).

ILNP is architectural prior art for identifier/locator separation. It is directly relevant whenever Internet-X frames the locator split as if it were new. ILNP is less focused on a public-key identity namespace and less centered on an overlay transport reference package.

Conclusion: strong overlap on the split itself, weaker overlap on the exact security and flow composition.

## QUIC + TLS 1.3

Primary sources: [RFC 9000](https://www.rfc-editor.org/rfc/rfc9000.html), [RFC 9001](https://www.rfc-editor.org/rfc/rfc9001.html).

QUIC demonstrates that a transport can separate connection continuity from the 5-tuple through connection IDs and can authenticate transport parameters through the TLS-derived handshake transcript. QUIC migration is highly relevant prior art for address change without connection loss.

What QUIC does not provide is a global identity namespace or explicit name-to-identity-to-locator architecture.

Conclusion: strong overlap on transcript binding, key schedule discipline, and migration; weaker overlap on identity architecture.

## IKEv2 / IPsec / MOBIKE

Primary sources: [RFC 7296](https://www.rfc-editor.org/rfc/rfc7296.html), [RFC 4555](https://www.rfc-editor.org/rfc/rfc4555.html).

IKEv2 and MOBIKE cover authenticated exchange, strong state machines, and address change for protected flows. They are highly relevant to any claim that authenticated mobility-aware rebinding is novel.

Internet-X differs in target layer and explicit identity/locator/path framing.

Conclusion: strong overlap on secure rebinding logic, weaker overlap on naming and endpoint identity model.

## WireGuard

Primary source: [WireGuard protocol and cryptography overview](https://www.wireguard.com/protocol/).

WireGuard is relevant because it provides a small, readable, roaming-capable secure tunnel with strong cryptographic choices. It demonstrates that packet-inspectable, compact control logic can coexist with production-quality security. Its identity model is operationally key-based, but its architectural goal is a VPN tunnel rather than an identity/locator split transport architecture.

Conclusion: overlap on small control surface and roaming; low overlap on architectural claim surface.

## Hybrid PQ TLS Design Work

Primary source: [draft-ietf-tls-hybrid-design](https://datatracker.ietf.org/doc/html/draft-ietf-tls-hybrid-design).

This work matters because it narrows Internet-X's ability to claim novelty around hybrid composition itself. The relevant lesson is not that Internet-X loses value, but that its crypto transition story must be framed as an application of established hybrid design principles at a different architectural layer.

Conclusion: do not claim hybrid composition as novel per se.

## Additional Relevant Sources

- [NIST FIPS 203 ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [NIST FIPS 204 ML-DSA](https://csrc.nist.gov/pubs/fips/204/final)
- [RFC 4218 threat analysis for locator/identifier split solutions](https://www.rfc-editor.org/rfc/rfc4218)

These sources are particularly relevant to security framing and to avoiding casual claims that stable identity and rebinding are straightforward or risk-free.

## Survey Conclusion

Internet-X overlaps substantially with established ideas. The repository should therefore position Internet-X as:

- a serious protocol composition,
- a concrete overlay transition package,
- and a defensible design point under explicit constraints,

rather than as a wholly unprecedented architecture.
