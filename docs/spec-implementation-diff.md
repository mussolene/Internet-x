# Spec / Implementation Diff

Audit date: April 19, 2026.

The table below compares the current spec set against the current `refimpl/` behavior.

| Area | Spec says | Code does | Status | Action |
| --- | --- | --- | --- | --- |
| Packet fields | Common envelope carries version, type, flags, header length, `session_id`, `flow_id`, `sequence`, source/destination `NodeID`, `locator_hint`, payload | `refimpl/packet.py` builds and validates exactly those fields | Match | None |
| Message order | `INIT -> INIT_ACK -> KEM_EXCHANGE -> AUTH -> DATA`; locator update is post-establishment control traffic | `refimpl/engine.py` implements exactly that order | Match | None |
| State transitions | `AUTH` establishes `FlowID`; later `DATA`, `DATA_ACK`, `LOCATOR_UPDATE`, `LOCATOR_UPDATE_ACK` operate within that flow | Server state machine follows that progression and rejects wrong `flow_id` | Match | None |
| Timeout logic | Retransmission behavior is defined, but scoped to the MVP reference profile | Client retries `INIT` and `KEM_EXCHANGE`; no automatic resend loop exists for application `DATA` | Match after audit clarification | Spec wording tightened in `spec/ixp-v0.2.md` |
| Transcript binding | `INIT_ACK`, `KEM_EXCHANGE`, and `AUTH` are transcript-bound | Transcript hashes and key confirmations are checked on both sides | Match | None |
| Flow establishment | `FlowID` is identity- and transcript-bound, not locator-bound | `derive_flow_id()` hashes session, node IDs, transcript hash, suite, and PQ mode | Match | None |
| Locator update authentication | `LOCATOR_UPDATE` requires valid signature and MAC before changing active locator | Server verifies signature and update MAC, then updates `client_locator` | Match | None |
| Replay handling | Data replay should not result in duplicate delivery | Server caches `DATA_ACK` for exact duplicate client sequence values and does not re-deliver payload | Match after audit clarification | Spec wording updated to describe idempotent duplicate handling rather than blanket rejection |
| Error handling | `ERROR` packets cover malformed packets, unsupported suite, transcript mismatch, wrong flow, stale locator update, and auth failure | Server emits `ERROR` in those cases; malformed JSON is discarded before session handling | Match | None |
| Suite negotiation | One real classical suite; responder chooses the mutually supported suite | `SUPPORTED_SUITES = ["x25519+ed25519+chacha20poly1305"]`; responder selects from client offer | Match | None |
| Downgrade behavior | Explicit PQ-mode selection and fallback state are transcript-visible; tampering should fail | `selected_pq_mode` and `fallback_used` are part of the transcript and signature/MAC contexts; downgrade-tamper test passes | Match | None |
| Real vs simulated boundary | Real classical baseline; simulated PQ extension point only | Code uses classical crypto only and simulated PQ share mixing | Match | None |
| Control plane | `Name -> Identity -> Locator -> Path` is explicit; the current reference profile may scope some layers out | `JSONDirectory` and `JSONLocatorRegistry` implement local `Name -> Identity -> Locator`; `Path` remains architectural only | Match with bounded implementation | No code change; audit documents this as a maturity limit |
| Rebinding semantics | Authenticated locator change should preserve the logical flow when accepted | Demo and tests keep the same `session_id` and `flow_id` across `LOCATOR_UPDATE` and post-update `DATA` | Match | None |
| Demo reproducibility | Documented demo path should run without hidden environmental assumptions | Before audit the script assumed the server demo port was free; after audit it allocates a free port dynamically | Match after audit fix | Updated `scripts/run_demo.py` |
| Benchmark reproducibility | Benchmark harness should be runnable from the current repo state | Before audit the harness also assumed fixed ports; after audit it allocates free ports dynamically | Match after audit fix | Updated `scripts/benchmark.py` |

## Important Notes

- The reference profile is coherent as a research demo, but its control plane remains deliberately minimal.
- `Path` is an architectural concept in the spec, not a runnable subsystem in the current code.
- Locator continuity is real at the reference-profile layer: the server updates the authenticated locator and continues the same flow instead of issuing a new handshake.
- The audited spec set now matches the current code on the previously loose points: duplicate `DATA` handling and retransmission scope.
