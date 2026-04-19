# Evaluation Methodology

## What Was Evaluated

1. Functional correctness of the reference implementation
2. State-machine sanity for handshake and locator update
3. Small local latency envelope for loopback runs
4. Claim-positioning quality relative to prior art

## What Was Held Fixed

- single-machine loopback environment
- Python 3.14 runtime
- reference implementation using Ed25519, X25519, HKDF-SHA256, and ChaCha20-Poly1305
- JSON packet encoding

## Baselines Used

The repository uses two kinds of baselines.

### Functional Baselines

- prior repository state with a fully simulated UDP/JSON prototype
- protocol families from the literature: HIP, LISP, ILNP, QUIC+TLS, IKEv2/MOBIKE, WireGuard

### Measurement Baseline

- repeated local loopback runs of the same reference implementation

## What The Evaluation Optimizes For

This evaluation optimizes for:

- technical coherence
- explicit identity and locator separation
- inspectability
- authenticated rebinding
- transition-friendly crypto agility

It does not optimize for:

- minimum latency
- minimum overhead
- production throughput
- privacy minimization

## Why The Results Are Still Useful

The evidence is enough to support claims about design coherence and runnable behavior. It is not enough to settle wide-area deployment questions or to rank Internet-X universally against production systems.
