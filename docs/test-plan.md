# Test Plan

## Goals

The test plan checks that the repository's strongest claims are backed by runnable artifacts.

## Automated Test Categories

- packet parsing and validation
- successful handshake and encrypted data transfer
- retransmission after a dropped control response
- downgrade/tampering detection via transcript mismatch
- locator update and post-update data continuity
- multi-node independent sessions
- bounded machine-checkable invariants for state-machine safety properties

## Manual / Scripted Checks

- `make demo` for a full end-to-end run with authenticated locator update
- `python3 scripts/benchmark.py` for local loopback latency observations
- `make paper-check` for unfinished boilerplate removal across docs and publication artifacts

## Acceptance Conditions

- tests pass in the current environment
- demo completes without manual intervention
- locator update is accepted only after authenticated session establishment
- docs, code, and examples use the same packet names and field model
