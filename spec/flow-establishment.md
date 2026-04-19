# Flow Establishment

## Overview

A flow in Internet-X is not established by seeing a locator and starting to send data. It is established only after:

1. both parties contribute to the handshake transcript,
2. both parties authenticate that transcript,
3. both parties derive the same session secrets,
4. the responder publishes an explicit `FlowID` in `AUTH`.

## FlowID Derivation

The reference implementation derives `FlowID` from:

- `session_id`
- client and server `NodeID`
- transcript hash through `KEM_EXCHANGE`
- selected classical suite
- selected PQ mode

This is intentionally identity- and transcript-bound.

## Why Flow Establishment Is Explicit

The explicit `FlowID` gives the protocol a clear transition point between:

- unauthenticated bootstrap packets tied to a provisional session,
- and authenticated data packets tied to a flow.

That boundary is central to the design.
