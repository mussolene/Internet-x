# Internet-X

Internet-X is an identity-first experimental overlay transport architecture organized around an explicit resolution chain:

```text
Name -> Identity -> Locator -> Path
```

The repository now contains a runnable reference implementation, a coherent specification set, an Internet-Draft-style document, a paper draft, tests, traces, and an evidence pack. The project remains experimental. It is not a production stack, not a claim that the public Internet should be replaced wholesale, and not a proof of universal optimality.

## Status And Scope

Current status on April 19, 2026:

- Runnable Python reference implementation in `refimpl/`
- Packet-by-packet specification in `spec/`
- Reproducible tests and demos in `tests/`, `scripts/`, and `examples/`
- Prior-art, novelty, security, and evidence documents in `docs/`
- Publication package in `paper/` and `ietf/`
- Bounded machine-checkable invariant model in `formal/`

Not in scope today:

- global deployment infrastructure
- a full routing or path-selection plane
- a federated or production-grade control-plane service
- real post-quantum cryptography in the reference implementation
- congestion control, NAT traversal, or kernel integration

## Strongest Defensible Contribution

Internet-X should be read as a protocol composition and transition design, not as a claim of absolute novelty. The strongest defensible contribution in this repository is the explicit combination of:

1. `Name -> Identity -> Locator -> Path` separation as a first-class protocol model
2. identity-bound flow establishment rather than locator-bound sessions
3. authenticated locator rebinding as a control-path primitive
4. packet-inspectable overlay deployment over today's Internet
5. crypto agility with explicit hybrid and fallback semantics for post-quantum transition

The prior-art analysis in [`docs/positioning.md`](/Users/maxon/git/me/Internet-x/docs/positioning.md) and [`docs/novelty-matrix.md`](/Users/maxon/git/me/Internet-x/docs/novelty-matrix.md) is intentionally conservative.

## What Is Real Vs Simulated

| Component | Status | Notes |
| --- | --- | --- |
| Identity model (`NodeID = SHA-256(algorithm_id || signing_public_key)`) | Real in repo | Implemented in the reference code and used consistently in docs |
| Control plane | Real, minimal | Separate HTTP service with authenticated registration, resolution, locator update, and lease expiry; trust remains local to the demo environment |
| Handshake state machine | Real | `INIT -> INIT_ACK -> KEM_EXCHANGE -> AUTH -> DATA`, plus `DATA_ACK` and locator update control packets |
| Classical authenticated session establishment | Real | Ed25519 signatures, X25519 key agreement, HKDF-SHA256, ChaCha20-Poly1305 |
| Encrypted data exchange | Real | AEAD-protected data packets in the reference implementation |
| Replay detection for data sequence numbers | Real | Duplicate `DATA` sequences are not re-delivered |
| Locator update authentication | Real | Signed and MACed locator update control packets |
| Post-quantum component | Simulated | Hybrid mode mixes simulated PQ shares into transcript and derivation context; it is not real ML-KEM/ML-DSA security |
| Global path selection plane | Conceptual | Documented architecture only |
| Formal verification | Partial | Bounded machine-checkable invariants, not a complete proof |

## Quickstart

From a clean clone in the audited environment:

```bash
python3 -m pip install -r requirements.txt
make test
make demo
```

`make demo` generates demo identities, starts the control-plane service and UDP server, runs a client handshake, performs an authenticated locator update, and prints the delivery result.

The audited demo path is `make demo`. The lower-level CLI commands are also usable, but they now require a running control-plane service. The reference implementation ships a minimal resolver/control-plane daemon for loopback and local-network evaluation; it is intentionally central and simple rather than federated or hardened.

For direct CLI use:

```bash
python3 -m refimpl.keygen --name server.demo --locator udp://127.0.0.1:9080 --out examples/identities/server.json
python3 -m refimpl.keygen --name client.demo --locator udp://127.0.0.1:10080 --out examples/identities/client.json
python3 -m refimpl.controlplane_service --port 9081
python3 -m refimpl.server --identity examples/identities/server.json --control-plane http://127.0.0.1:9081
python3 -m refimpl.client \
  --identity examples/identities/client.json \
  --control-plane http://127.0.0.1:9081 \
  --peer-name server.demo \
  --message "Hello from Internet-X." \
  --migrate
```

See [`docs/control-plane.md`](/Users/maxon/git/me/Internet-x/docs/control-plane.md) and [`docs/what-is-real-vs-simulated.md`](/Users/maxon/git/me/Internet-x/docs/what-is-real-vs-simulated.md) for the exact control-plane and crypto trust boundaries.

## How To Evaluate The Claims

Use these commands from the repository root:

```bash
make test
make demo
python3 scripts/benchmark.py
python3 formal/bounded_model.py
make paper-check
```

Then read, in order:

1. [`docs/positioning.md`](/Users/maxon/git/me/Internet-x/docs/positioning.md)
2. [`spec/ixp-v0.2.md`](/Users/maxon/git/me/Internet-x/spec/ixp-v0.2.md)
3. [`security.md`](/Users/maxon/git/me/Internet-x/spec/security.md)
4. [`docs/evidence-pack.md`](/Users/maxon/git/me/Internet-x/docs/evidence-pack.md)
5. [`paper/internetx.tex`](/Users/maxon/git/me/Internet-x/paper/internetx.tex)
6. [`ietf/draft-internetx-00.md`](/Users/maxon/git/me/Internet-x/ietf/draft-internetx-00.md)

## Repository Map

```text
.
├── README.md
├── RESEARCH_LOG.md
├── PROJECT_STATUS.md
├── GAP_ANALYSIS.md
├── CHANGELOG.md
├── RELEASE_NOTES_v0.1.md
├── docs/
├── spec/
├── refimpl/
├── tests/
├── scripts/
├── examples/
├── formal/
├── paper/
├── ietf/
└── prototype/
```

## Legacy Material

The older `prototype/` directory is preserved as the earlier educational JSON-only v0.1 artifact. The current reference implementation and current specification baseline are `refimpl/` and `spec/ixp-v0.2.md`.

## Limitations

Internet-X in this repository still has hard limits:

- the control plane is a single minimal service, not a federated or hardened deployment subsystem
- the prototype uses a user-space Python UDP overlay and does not integrate with host sockets or routing tables
- hybrid PQ mode is not cryptographically real
- privacy properties are limited because locator metadata remains visible in control packets
- no congestion control, PMTU discovery, NAT traversal, or large-scale operational evidence is provided
- the evaluation package demonstrates a strong design point under explicit assumptions; it does not prove universal optimality

## License

MIT. See [`LICENSE`](/Users/maxon/git/me/Internet-x/LICENSE).
