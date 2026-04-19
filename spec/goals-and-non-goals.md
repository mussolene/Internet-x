# Goals And Non-Goals

## Goals

1. Keep stable identity distinct from mutable locator state.
2. Make `Name -> Identity -> Locator -> Path` explicit in both documents and packets.
3. Support overlay deployment over today's IPv4/IPv6 Internet.
4. Make flow establishment explicit and packet-inspectable.
5. Support authenticated locator rebinding without changing identity.
6. Expose crypto agility, hybrid mode selection, and fallback semantics explicitly.
7. Remain honest about maturity and scope.

## Non-Goals

1. Replace the global Internet architecture in this repository release.
2. Specify a full routing plane or path-discovery protocol.
3. Ship a production-grade directory or locator mapping service.
4. Claim real PQ security in the current reference implementation.
5. Optimize for minimum header size or maximum raw throughput.
