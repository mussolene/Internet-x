# Final Audit

Audit date: April 19, 2026.

## Verdict

`MVP-N1 READY`

## Why This Is The Verdict

The repository is internally coherent, runnable, technically honest, and fairly positioned after the targeted control-plane remediation pass.

The former P0 blocker is now cleared:

- the control plane is a separate live service process rather than local JSON artifacts
- node registration is authenticated against the node identity
- `Name -> Identity` and `NodeID -> Locator` resolution run through the service
- locator updates are authenticated, freshness-bounded, and rejected when stale or incorrectly signed
- the demo and runtime path now use the service as the authoritative control plane

The repo remains experimental and locally trusted in operational terms, but those remaining limitations do not invalidate an `MVP-N1 READY` verdict.

## Commands And Results

```bash
pytest -q tests
python3 scripts/run_demo.py
python3 scripts/benchmark.py
python3 formal/bounded_model.py
make paper-check
```

Observed results on the remediated repository state:
- `pytest -q tests` -> `17 passed`
- `python3 scripts/run_demo.py` -> successful control-plane startup, service-backed resolution, locator update, control-plane locator version `2`, and post-update data delivery
- `python3 scripts/benchmark.py` -> 10 loopback runs, min `108.277 ms`, median `110.067 ms`, max `136.208 ms`
- `python3 formal/bounded_model.py` -> `{'checked_traces': 145, 'max_depth': 6}`
- `make paper-check` -> passed

## Answers To The Primary Audit Questions

1. Is the prototype actually runnable from a clean clone?
Yes for the audited path, after installing dependencies with `python3 -m pip install -r requirements.txt`. `make test` and `make demo` are runnable. The low-level CLI path now requires a running control-plane service rather than prebuilt JSON control-plane files.

2. Do the specs and the code describe the same protocol?
Yes after minimal audit corrections. The main mismatches were loose wording around control-path retransmission scope and duplicate `DATA` handling. Those are now aligned.

3. Does the demo actually prove locator rebinding, or is it secretly reconnecting?
It demonstrates genuine flow-preserving rebinding within the overlay reference profile. The trace shows one handshake, then `LOCATOR_UPDATE`, then post-update `DATA` on the same `session_id` and `flow_id`.

4. Are the crypto claims supported by the implementation?
Yes for the classical baseline. The code implements Ed25519 signatures, X25519 ephemeral exchange, HKDF-SHA256 key derivation, HMAC-SHA256 key confirmation / update MAC, and ChaCha20-Poly1305 payload protection.

5. Are the PQ claims honestly bounded?
Yes. The repository consistently presents PQ support as simulated transition logic, not real post-quantum security.

6. Is the resolver/control plane real and necessary, or only nominal?
It is necessary to the architecture and now minimally real in implementation terms. The repo uses a live authenticated control-plane service for registration, resolution, and locator updates. It is intentionally central and locally trusted, not federated or production-hardened.

7. Are tests meaningful, or mostly superficial?
They are meaningful but modest. They cover authenticated registration, service-backed resolution, authenticated locator update, invalid signature rejection, stale update rejection, handshake success, malformed packets, downgrade detection, retransmission, duplicate-data replay suppression, locator continuity, and multi-session behavior. They do not amount to a broad adversarial or wide-area test campaign.

8. Is the paper aligned with the code/spec, or does it overstate maturity?
It is aligned and conservative. The paper continues to describe a runnable reference profile with a real classical baseline and simulated PQ mode, not a production-ready system.

9. Is the IETF draft consistent with the implementation?
Yes. It reads like an experimental repo draft and stays within the implemented message set and documented claim boundaries.

10. Is the contribution positioning honest relative to prior art?
Yes. The repo now frames Internet-X as a narrow compositional contribution: identity-first overlay flow establishment plus authenticated locator rebinding plus explicit crypto-agility semantics.

## Minimal Fixes Applied During Audit

- Preserved the audited research-demo baseline with commit `chore: snapshot audited research-demo baseline before control-plane remediation` and tag `v0.1-research-demo`.
- Added a live authenticated control-plane service with signed registration, service-backed resolution, signed locator updates, lease expiry, and stale update rejection.
- Rewired client, server, demo, benchmark, and tests to use the control-plane service as the authoritative runtime control plane.
- Tightened README, status, claims, spec, and release-blocker wording so the repository no longer describes the control plane as only local JSON.

## Remaining Risks

- The control plane is intentionally minimal, central, and locally trusted.
- `Path` remains architectural rather than implemented.
- PQ remains simulated.
- The evaluation remains loopback-scale and research-oriented.

## Bottom Line

The repository clears the former MVP-N1 blocker without widening scope beyond the narrow remediation target.

It is still not a production system, a federated naming infrastructure, or a real PQ-secure transport stack. Within its stated scope, however, `MVP-N1 READY` is now the defensible maturity verdict.
