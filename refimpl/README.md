# Internet-X Reference Implementation

The `refimpl/` package is the current runnable baseline for Internet-X.

## What It Demonstrates

- stable identity independent of locator
- explicit flow establishment
- real classical authenticated session establishment
- encrypted data packets
- authenticated locator update
- inspectable JSON packet headers
- explicit hybrid/fallback negotiation surface for future PQ integration

## What It Does Not Demonstrate

- real ML-KEM or ML-DSA
- production-grade mapping infrastructure
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

Note: the current reference implementation uses file-backed directory and locator-registry inputs. It does not include a separate resolver service process.
