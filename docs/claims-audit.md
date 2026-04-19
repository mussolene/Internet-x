# Claims Audit

Audit date: April 19, 2026.

Method:
- Read README, specs, docs, paper, IETF draft, demo scripts, and implementation.
- Ran `pytest -q tests`, `python3 scripts/run_demo.py`, `python3 scripts/benchmark.py`, `python3 formal/bounded_model.py`, and `make paper-check`.
- Classified claims against current code and current command results.

Classification labels:
- `Supported by code and test evidence`
- `Partially supported`
- `Speculative / conceptual only`
- `Unsupported / should be downgraded`

## Claim Inventory

| Source | Claim | Classification | Evidence / audit action |
| --- | --- | --- | --- |
| `README.md` | Runnable reference implementation exists | Supported by code and test evidence | `pytest -q tests` passed; `python3 scripts/run_demo.py` completed successfully after audit reproducibility fixes. |
| `README.md` | Internet-X is identity-first and preserves `Name -> Identity -> Locator -> Path` | Partially supported | `Name -> Identity -> Locator` is real in code through `JSONDirectory` and `JSONLocatorRegistry`; `Path` remains architectural only and is documented as out of scope. |
| `README.md` | Real classical authenticated and encrypted flows | Supported by code and test evidence | Code uses Ed25519, X25519, HKDF-SHA256, HMAC-SHA256, and ChaCha20-Poly1305 in `refimpl/crypto.py`; handshake and data tests pass. |
| `README.md` | Authenticated locator rebinding | Supported by code and test evidence | Demo and tests show `LOCATOR_UPDATE` and `LOCATOR_UPDATE_ACK` on the same `session_id` and `flow_id`, followed by successful post-update `DATA`. |
| `README.md` | Post-quantum support is simulated only | Supported by code and test evidence | `SIMULATED_PQ_MODE = "simulated-ml-kem-768"`; no ML-KEM or ML-DSA library use exists. |
| `README.md` | No long-running resolver daemon in the repo | Supported by code and test evidence | The implementation uses file-backed JSON abstractions only; audit kept the wording explicit. |
| `spec/ixp-v0.2.md` | Packet-by-packet runnable reference profile | Supported by code and test evidence | Packet envelope, handshake messages, and locator update are implemented and exercised. |
| `spec/ixp-v0.2.md` | Timeout and retransmission behavior is defined | Partially supported | Control-path retry is real for `INIT` and `KEM_EXCHANGE`; application `DATA` is not automatically retried by the client. Spec wording was tightened to match code. |
| `spec/handshake.md` | Duplicate data does not duplicate delivery | Supported by code and test evidence | Server caches `DATA_ACK` by client sequence and resends it on exact duplicate packets; replay test now sends the same `DATA` packet twice. |
| `spec/state-machine.md` | Flow continuity survives authenticated locator rebinding | Supported by code and test evidence | Demo traces show one handshake, then `LOCATOR_UPDATE`, then post-update `DATA` on the same logical flow. |
| `spec/security.md` | Real classical security baseline, simulated PQ, local trusted directory/registry | Supported by code and test evidence | Matches current implementation and observed behavior. |
| `refimpl/README.md` | Reference implementation demonstrates explicit flow establishment and authenticated locator update | Supported by code and test evidence | Verified in tests and demo. |
| `refimpl/README.md` | No production-grade mapping infrastructure | Supported by code and test evidence | Only local JSON-backed mapping exists. |
| `scripts/run_demo.py` | End-to-end demo is runnable | Supported by code and test evidence | Audit fixed a reproducibility issue by removing the hardcoded server port assumption. |
| `scripts/run_demo.py` | Demo proves rebinding rather than reconnect | Supported by code and test evidence | Demo trace contains one `INIT`, one `AUTH`, one `LOCATOR_UPDATE`, and post-update `DATA` with unchanged `session_id` and `flow_id`. |
| `scripts/benchmark.py` | Local benchmark harness exists | Supported by code and test evidence | Benchmark ran successfully after the same fixed-port reproducibility issue was removed. |
| `docs/positioning.md` | Novelty claim is narrow and compositional | Supported by code and test evidence | Prior-art survey and novelty matrix are conservative and do not claim absolute novelty. |
| `docs/positioning.md` | Strong or near-optimal only under explicit constraints | Supported by code and test evidence | The repository evidence is sufficient for a conditional tradeoff claim, not a universal one. |
| `docs/evidence-pack.md` | Implementation is a strong design point under stated constraints | Partially supported | Evidence supports coherence, inspectability, and rebinding; it does not support deployment-grade claims. The document already states that boundary. |
| `paper/internetx.tex` | Runnable implementation with real classical baseline and simulated PQ transition logic | Supported by code and test evidence | Matches the code and audit results. |
| `paper/internetx.tex` | Repository is not production-ready and not universally optimal | Supported by code and test evidence | Wording is conservative and aligned. |
| `ietf/draft-internetx-00.md` | Experimental repo draft with authenticated locator update and explicit agility surface | Supported by code and test evidence | Message formats, control flow, and limitations match the reference profile. |
| Code comments and packet notes | Classical security is real; PQ remains simulated | Supported by code and test evidence | Notes in `INIT_ACK` and `AUTH` payloads match the actual crypto boundary. |

## Claim Surface By Topic

### Implemented and supported

- Identity-derived `NodeID` and explicit `Name -> Identity -> Locator` lookup chain.
- `INIT -> INIT_ACK -> KEM_EXCHANGE -> AUTH -> DATA` flow establishment.
- AEAD-protected application data.
- Authenticated locator update with signature and MAC.
- Duplicate `DATA` suppression with cached `DATA_ACK` replay.
- Downgrade/tamper detection through transcript-bound handshake material.
- Minimal reproducible demo, test suite, benchmark harness, and bounded invariant checker.

### Implemented but bounded

- Retries are built in for the control path, not for general application `DATA` retransmission.
- Replay handling is meaningful for duplicate data sequence numbers, but not a complete anti-replay story for all traffic classes.
- Mobility is demonstrated at the overlay UDP flow layer, not as a production mobility subsystem.
- The resolver/control plane is necessary to the model, but the current implementation is a local JSON abstraction rather than a live service.

### Conceptual only

- `Path` selection beyond locator resolution.
- Global or authenticated directory / locator service.
- Real post-quantum cryptography.
- Production deployment hardening such as anti-DoS, NAT traversal, and congestion control.

### Unsupported claims after audit

No material unsupported claim remains in the audited source set. The audit downgraded or clarified the places that were previously too loose:

- quickstart and CLI docs now state the dependency-install step and the file-backed control-plane boundary;
- spec text now matches actual duplicate-`DATA` behavior and control-path retransmission scope;
- audited runtime scripts no longer depend on a fixed UDP port being free.

## Crypto Honesty Summary

What is real:
- Ed25519 signatures.
- X25519 ephemeral key exchange.
- HKDF-SHA256 session derivation.
- HMAC-SHA256 key confirmation and locator-update MAC.
- ChaCha20-Poly1305 application-data and ack protection.

What is simulated:
- `simulated-ml-kem-768` hybrid-transition mode.
- PQ share mixing as an architectural transition hook.

What is architectural intent only:
- Replacing the simulated mode with a real ML-KEM / ML-DSA backend.
- Deployment-grade control-plane infrastructure.

## Bottom Line

The current claim surface is technically honest after the audit fixes. The repository supports a runnable research demo with a real classical baseline, authenticated rebinding, and a clearly bounded simulated PQ transition hook. It does not support stronger claims than that.
