# Demo Validation

Audit date: April 19, 2026.

## Commands Run

```bash
python3 scripts/run_demo.py
```

## What the Demo Actually Does

The demo script:
1. generates fresh server and client identities;
2. starts a separate control-plane service process;
3. starts the UDP server, which registers its `Name`, `NodeID`, and locator with the control plane;
4. runs a client that registers itself, resolves `server.demo` through the service, and completes handshake and encrypted data exchange;
5. performs `LOCATOR_UPDATE` from a new client socket/port;
6. updates the control-plane locator record for the same client identity with a higher locator version;
7. sends another encrypted `DATA` packet after the locator change.

Important boundary:
- The control plane is real enough to clear the old nominal-JSON blocker, but it remains a single minimal service under local trust assumptions.
- Authenticated writes are real; global discovery, federation, and production hardening are still out of scope.

## Validation Checklist

| Check | Result | Evidence |
| --- | --- | --- |
| Control-plane service starts | PASS | `scripts/run_demo.py` starts `refimpl.controlplane_service` and waits for `/v1/health` |
| Name resolution works | PASS | Client resolves `server.demo` through the control-plane `Name -> Identity` API before the handshake |
| NodeID to locator resolution works | PASS | Client resolves the server locator through the control-plane `NodeID -> Locator` API before sending `INIT` |
| Handshake succeeds | PASS | Demo output includes `INIT`, `INIT_ACK`, `KEM_EXCHANGE`, `AUTH` |
| Encrypted data exchange succeeds | PASS | Demo output includes `DATA` and `DATA_ACK` with delivered status |
| Locator update occurs | PASS | Demo output includes `LOCATOR_UPDATE` and `LOCATOR_UPDATE_ACK` |
| Control-plane locator update occurs | PASS | Demo output reports `control_plane_locator_version = 2` and `examples/demo-control-plane-state.json` reflects the new locator |
| Flow continues after locator update | PASS | Demo output includes a second `DATA` and `DATA_ACK` after locator update |
| Demo secretly reconnects | FAIL for reconnect hypothesis | Trace shows only one `INIT` and one `AUTH`; no second handshake occurs after `LOCATOR_UPDATE` |

## Rebinding Verdict

The demo performs real flow-preserving locator rebinding within the scope of the reference overlay profile.

Evidence from the current validated run:
- the client resolved `server.demo` through the control-plane service before sending `INIT`
- server trace contains exactly one `INIT`, one `KEM_EXCHANGE`, one `AUTH`, one `LOCATOR_UPDATE`, and post-update `DATA`
- the post-update `DATA` packet carries `sequence=1`, which is continuation of the established flow rather than a new flow bootstrap
- the `LOCATOR_UPDATE_ACK` returns the new active locator and the control-plane update reports the same locator at version `2`
- the next `DATA` is accepted on the new locator without a second handshake

## What This Does Not Prove

The demo does not prove:
- a federated or hardened resolver/control-plane service;
- path validation beyond the current session-authenticated overlay exchange;
- NAT traversal or Internet-scale mobility robustness;
- real post-quantum security.

## Conclusion

The demo is not secretly reconnecting and calling it rebinding. Within the repository's explicit scope, it demonstrates authenticated locator update that preserves the same logical session and flow.
