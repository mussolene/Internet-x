# Formal Analysis

## Artifact

The repository includes a bounded machine-checkable invariant model at [`formal/bounded_model.py`](/Users/maxon/git/me/Internet-x/formal/bounded_model.py).

## What It Models

The model abstracts the control state for:

- `INIT`
- `INIT_ACK`
- `KEM_EXCHANGE`
- `AUTH`
- `DATA`
- `LOCATOR_UPDATE`
- reset/error transitions

## Invariants Checked

- data is not accepted before authentication establishes a flow
- a reachable bad KEM / downgrade event must trigger downgrade detection
- locator update is only valid after flow establishment

## What It Does Not Model

- concrete cryptographic security
- network reordering or concurrency in full detail
- timer behavior and retransmission races
- resource exhaustion attacks
- directory or registry compromise

## Interpretation

This is not full formal verification. It is a bounded sanity check on the intended state-machine invariants. That level of formality is appropriate for the current repository scope and is explicitly weaker than a proof.
