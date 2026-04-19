# Internet-X Prototype

This prototype is educational. It exists to exercise the Internet-X architecture, packet structure, transcript handling, and handshake sequencing in a small readable codebase.

It is not a secure protocol implementation.

## What The Prototype Demonstrates

- identity-oriented packet metadata
- separation of `NodeID` and `Locator`
- JSON packet encoding through a shared protocol module
- the phase sequence `INIT -> INIT_ACK -> KEM_EXCHANGE -> AUTH -> DATA`
- `DATA_ACK` as a post-data acknowledgement
- transcript hashing and `FlowID` derivation

## What The Prototype Does Not Demonstrate

- real confidentiality
- real authentication
- real ML-KEM or ML-DSA integration
- production error handling
- full mobility signaling or locator migration

All cryptographic material in this directory is simulated for educational purposes. The packet flow is also simulated. The goal is architectural clarity, not security.

## Files

- `protocol.py`: shared packet constants, JSON serialization, transcript hashing, and `FlowID` derivation
- `node.py`: simple identity abstraction with stable `NodeID` and mutable locator concept
- `server.py`: UDP server responding with `INIT_ACK`, `AUTH`, and `DATA_ACK`
- `client.py`: UDP client driving the end-to-end exchange

## Run Instructions

From the repository root, start the server:

```bash
python3 prototype/server.py
```

Then, in a second terminal, run the client:

```bash
python3 prototype/client.py
```

The default transport is localhost UDP on port `8080`.

## Expected Packet Flow

The prototype should log this sequence without hanging:

1. `INIT`
2. `INIT_ACK`
3. `KEM_EXCHANGE`
4. `AUTH`
5. `DATA`
6. `DATA_ACK`

If a packet is malformed or out of sequence, the server returns `ERROR` instead of silently waiting.
