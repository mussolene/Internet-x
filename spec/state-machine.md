# State Machine

## Client State Machine

```text
START
  -> INIT_SENT
  -> INIT_ACKED
  -> KEM_SENT
  -> ESTABLISHED
  -> LOCATOR_UPDATING (optional)
  -> ESTABLISHED
```

## Server State Machine

```text
LISTEN
  -> INIT_ACK_SENT
  -> ESTABLISHED
  -> LOCATOR_UPDATED (logical substate)
```

## Illegal Transitions

- `DATA` before `AUTH`
- `LOCATOR_UPDATE` before `AUTH`
- `DATA` with the wrong `flow_id`
- `DATA` with an unexpected sequence number that cannot be matched to the established flow state
- `LOCATOR_UPDATE` with a stale counter

## Retransmission Rules

The reference implementation caches:

- `INIT_ACK` for duplicate `INIT`
- `AUTH` for duplicate `KEM_EXCHANGE`
- `DATA_ACK` for exact duplicate `DATA` sequences that were already acknowledged

This provides simple reliability without redesigning the core state machine.
