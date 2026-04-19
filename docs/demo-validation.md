# Demo Validation

Audit date: April 19, 2026.

## Commands Run

```bash
python3 scripts/run_demo.py
```

## What the Demo Actually Does

The demo script:
1. generates fresh server and client identities;
2. writes a local JSON directory and locator registry;
3. starts the UDP server;
4. runs a client handshake and encrypted data exchange;
5. performs `LOCATOR_UPDATE` from a new client socket/port;
6. sends another encrypted `DATA` packet after the locator change.

Important boundary:
- There is no standalone resolver or locator-service process to start.
- The demo uses file-backed `JSONDirectory` and `JSONLocatorRegistry` artifacts.
- That is sufficient for the repository's research-demo claim, but it is not a deployment-grade control plane.

## Validation Checklist

| Check | Result | Evidence |
| --- | --- | --- |
| Directory / registry artifacts exist | PASS | `scripts/run_demo.py` generated `examples/demo-directory.json` and `examples/demo-registry.json` before running the client |
| Name resolution works | PASS | Client resolves `server.demo` via the JSON directory and registry and completes the handshake |
| Handshake succeeds | PASS | Demo output includes `INIT`, `INIT_ACK`, `KEM_EXCHANGE`, `AUTH` |
| Encrypted data exchange succeeds | PASS | Demo output includes `DATA` and `DATA_ACK` with delivered status |
| Locator update occurs | PASS | Demo output includes `LOCATOR_UPDATE` and `LOCATOR_UPDATE_ACK` |
| Flow continues after locator update | PASS | Demo output includes a second `DATA` and `DATA_ACK` after locator update |
| Demo secretly reconnects | FAIL for reconnect hypothesis | Trace shows only one `INIT` and one `AUTH`; no second handshake occurs after `LOCATOR_UPDATE` |

## Rebinding Verdict

The demo performs real flow-preserving locator rebinding within the scope of the reference overlay profile.

Evidence from the audited trace:
- the same `session_id` appears before and after locator update: `3a37d4e8b4e3...`
- the same `flow_id` appears before and after locator update: `c63d448ef439...`
- server trace contains exactly one `INIT`, one `KEM_EXCHANGE`, one `AUTH`, one `LOCATOR_UPDATE`, and post-update `DATA`
- the post-update `DATA` packet carries `sequence=1`, which is continuation of the established flow rather than a new flow bootstrap
- the `LOCATOR_UPDATE_ACK` returns the new active locator and the next `DATA` is accepted on that locator

## What This Does Not Prove

The demo does not prove:
- a production resolver or locator service;
- path validation beyond the current session-authenticated overlay exchange;
- NAT traversal or Internet-scale mobility robustness;
- real post-quantum security.

## Conclusion

The demo is not secretly reconnecting and calling it rebinding. Within the repository's explicit scope, it demonstrates authenticated locator update that preserves the same logical session and flow.
