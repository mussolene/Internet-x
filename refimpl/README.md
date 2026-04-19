# Internet-X Reference Implementation

The `refimpl/` package is the current runnable baseline for Internet-X.

## What It Demonstrates

- stable identity independent of locator
- live authenticated control-plane service
- explicit flow establishment
- real classical authenticated session establishment
- encrypted data packets
- authenticated locator update
- inspectable JSON packet headers
- explicit hybrid/fallback negotiation surface for future PQ integration

## What It Does Not Demonstrate

- real ML-KEM or ML-DSA
- federated or hardened mapping infrastructure
- congestion control or NAT traversal
- kernel or socket API integration

## Key Commands

Install dependencies first:

```bash
python3 -m pip install -r requirements.txt
```

Generate identities:

```bash
python3 -m refimpl.keygen --name server.demo --locator udp://127.0.0.1:9080 --out examples/identities/server.json
python3 -m refimpl.keygen --name client.demo --locator udp://127.0.0.1:10080 --out examples/identities/client.json
```

Run tests:

```bash
make test
```

Run demo:

```bash
make demo
```

Run the control plane directly:

```bash
python3 -m refimpl.controlplane_service --port 9081
```

The current reference implementation includes a separate resolver/control-plane service process. It is intentionally minimal and central: authenticated writes are real, but there is no federation, external PKI, or production hardening.
