# Test Results

Test date: April 19, 2026.

## Automated Suite

Command:

```bash
pytest -q tests
```

Observed result:

- `11 passed`

Covered behaviors:

- packet encode/decode and malformed packet rejection
- successful authenticated handshake
- encrypted data exchange
- retransmission after dropped `INIT_ACK`
- downgrade/tamper detection through transcript failure
- replay of an identical `DATA` packet without duplicate application delivery
- locator update and post-migration continuity
- stale locator update rejection
- multi-node independent session establishment
- bounded machine-checkable invariants

## Demo

Command:

```bash
python3 scripts/run_demo.py
```

Observed result:

- successful `INIT -> INIT_ACK -> KEM_EXCHANGE -> AUTH -> DATA`
- successful `LOCATOR_UPDATE -> LOCATOR_UPDATE_ACK`
- successful post-migration `DATA -> DATA_ACK`
- same logical `session_id` and `flow_id` across pre-update and post-update traffic

## Benchmark

Command:

```bash
python3 scripts/benchmark.py
```

Observed local loopback summary from this repository state:

- runs: 10
- latency min: 71.349 ms
- latency median: 75.908 ms
- latency max: 80.928 ms

Interpretation:

These numbers are local-process and Python-runtime measurements. They are useful as reproducibility evidence, not as Internet-scale performance claims.
