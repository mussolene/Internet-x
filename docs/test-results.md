# Test Results

Test date: April 19, 2026.

## Automated Suite

Command:

```bash
pytest -q tests
```

Observed result:

- `17 passed`

Covered behaviors:

- packet encode/decode and malformed packet rejection
- successful authenticated handshake
- encrypted data exchange
- retransmission after dropped `INIT_ACK`
- downgrade/tamper detection through transcript failure
- replay of an identical `DATA` packet without duplicate application delivery
- locator update and post-migration continuity
- stale locator update rejection
- invalid control-plane registration rejection
- lease expiry removes stale locator resolution
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
- latency min: 108.277 ms
- latency median: 110.067 ms
- latency max: 136.208 ms

Interpretation:

These numbers are local-process and Python-runtime measurements. They are useful as reproducibility evidence, not as Internet-scale performance claims.

## Bounded Model

Command:

```bash
python3 formal/bounded_model.py
```

Observed result:

- `{'checked_traces': 145, 'max_depth': 6}`

## Paper Check

Command:

```bash
make paper-check
```

Observed result:

- passed
