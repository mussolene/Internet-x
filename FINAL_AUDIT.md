# Final Audit

Audit date: April 19, 2026.

## Verdict

`RESEARCH-DEMO READY`

## Why This Is The Verdict

The repository is internally coherent, runnable, technically honest, and fairly positioned as a research demo after the audit fixes.

It is not `MVP-N1 READY` because the control plane remains a local JSON abstraction rather than a minimally real service layer, and the repository's own strongest honest framing is still that of a research architecture plus runnable reference implementation.

## Commands And Results

```bash
pytest -q tests
python3 scripts/run_demo.py
python3 scripts/benchmark.py
python3 formal/bounded_model.py
make paper-check
```

Observed results on the audited repository state:
- `pytest -q tests` -> `11 passed`
- `python3 scripts/run_demo.py` -> successful handshake, locator update, and post-update data delivery
- `python3 scripts/benchmark.py` -> 10 loopback runs, median latency `75.908 ms`
- `python3 formal/bounded_model.py` -> `{'checked_traces': 145, 'max_depth': 6}`
- `make paper-check` -> passed

## Answers To The Primary Audit Questions

1. Is the prototype actually runnable from a clean clone?
Yes for the audited path, after installing dependencies with `python3 -m pip install -r requirements.txt`. `make test` and `make demo` are runnable. The low-level CLI path is less turnkey because it depends on prebuilt directory and registry JSON files.

2. Do the specs and the code describe the same protocol?
Yes after minimal audit corrections. The main mismatches were loose wording around control-path retransmission scope and duplicate `DATA` handling. Those are now aligned.

3. Does the demo actually prove locator rebinding, or is it secretly reconnecting?
It demonstrates genuine flow-preserving rebinding within the overlay reference profile. The trace shows one handshake, then `LOCATOR_UPDATE`, then post-update `DATA` on the same `session_id` and `flow_id`.

4. Are the crypto claims supported by the implementation?
Yes for the classical baseline. The code implements Ed25519 signatures, X25519 ephemeral exchange, HKDF-SHA256 key derivation, HMAC-SHA256 key confirmation / update MAC, and ChaCha20-Poly1305 payload protection.

5. Are the PQ claims honestly bounded?
Yes. The repository consistently presents PQ support as simulated transition logic, not real post-quantum security.

6. Is the resolver/control plane real and necessary, or only nominal?
It is necessary to the architecture, but nominal in implementation terms. The repo uses local JSON-backed directory and locator registry artifacts, not a live control-plane service.

7. Are tests meaningful, or mostly superficial?
They are meaningful but modest. They cover handshake success, malformed packets, downgrade detection, retransmission, duplicate-data replay suppression, stale locator-update rejection, locator continuity, and multi-session behavior. They do not amount to a broad adversarial or wide-area test campaign.

8. Is the paper aligned with the code/spec, or does it overstate maturity?
It is aligned and conservative. The paper explicitly says the repository is a runnable reference profile with a real classical baseline and simulated PQ mode, not a production-ready system.

9. Is the IETF draft consistent with the implementation?
Yes. It reads like an experimental repo draft and stays within the implemented message set and documented claim boundaries.

10. Is the contribution positioning honest relative to prior art?
Yes. The repo now frames Internet-X as a narrow compositional contribution: identity-first overlay flow establishment plus authenticated locator rebinding plus explicit crypto-agility semantics.

## Minimal Fixes Applied During Audit

- Fixed audit tests so they validate real duplicate-data replay and stale locator-update behavior.
- Removed hidden fixed-port assumptions from the demo and benchmark scripts.
- Tightened README quickstart and control-plane wording.
- Tightened spec wording so retransmission scope and duplicate-`DATA` handling match the code.
- Updated test-results content to reflect the current audited run.

## Remaining Risks

- The control plane is intentionally minimal and local.
- `Path` remains architectural rather than implemented.
- PQ remains simulated.
- The evaluation remains loopback-scale and research-oriented.

## Bottom Line

The repository clears a conservative research-demo release gate.

It does not clear an MVP-N1 release gate without redefining MVP downward or ignoring the fact that the control plane is still a local artifact layer rather than a minimally real subsystem.
