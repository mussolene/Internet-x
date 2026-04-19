# Internet-X Packet Examples

These examples follow the educational JSON prototype, not a production wire format.

## Common Envelope

Every packet uses:

```json
{
  "version": 1,
  "packet_type": "INIT",
  "flags": [],
  "header_length": 239,
  "flow_id": null,
  "source_node_id": "<source NodeID>",
  "destination_node_id": "<destination NodeID>",
  "locator_hint": "udp://localhost:8080",
  "payload": {}
}
```

## INIT

```json
{
  "version": 1,
  "packet_type": "INIT",
  "flags": [],
  "header_length": 239,
  "flow_id": null,
  "source_node_id": "<client NodeID>",
  "destination_node_id": "<server NodeID>",
  "locator_hint": "udp://localhost:8080",
  "payload": {
    "session_id": "7c942c5f7af7454f9c8458f29242a0ea",
    "sender_name": "client.demo",
    "algorithm_id": "hybrid-simulated",
    "supported_modes": ["hybrid-simulated", "classical-simulated"],
    "client_nonce": "b6ab18e63e214c83956d0f5620ef557a",
    "client_key_material": "simulated-client-ephemeral-key",
    "note": "Educational INIT packet only."
  }
}
```

## INIT_ACK

```json
{
  "version": 1,
  "packet_type": "INIT_ACK",
  "flags": [],
  "header_length": 243,
  "flow_id": null,
  "source_node_id": "<server NodeID>",
  "destination_node_id": "<client NodeID>",
  "locator_hint": "udp://localhost:8080",
  "payload": {
    "session_id": "7c942c5f7af7454f9c8458f29242a0ea",
    "selected_mode": "hybrid-simulated",
    "server_nonce": "d940f693dc0e4cb4b446decefc54f1d4",
    "server_key_material": "simulated-server-ephemeral-key",
    "transcript_hash": "<hash of transcript through INIT>",
    "note": "Educational INIT_ACK packet only."
  }
}
```

## KEM_EXCHANGE

```json
{
  "version": 1,
  "packet_type": "KEM_EXCHANGE",
  "flags": [],
  "header_length": 248,
  "flow_id": null,
  "source_node_id": "<client NodeID>",
  "destination_node_id": "<server NodeID>",
  "locator_hint": "udp://localhost:8080",
  "payload": {
    "session_id": "7c942c5f7af7454f9c8458f29242a0ea",
    "encapsulated_key_material": "simulated-kem-ciphertext",
    "classical_share": "simulated-classical-share",
    "pq_share": "simulated-pq-share",
    "transcript_hash": "<hash of transcript through INIT_ACK>",
    "note": "Simulated KEM exchange material for architecture testing."
  }
}
```

## AUTH

```json
{
  "version": 1,
  "packet_type": "AUTH",
  "flags": [],
  "header_length": 292,
  "flow_id": "<derived FlowID>",
  "source_node_id": "<server NodeID>",
  "destination_node_id": "<client NodeID>",
  "locator_hint": "udp://localhost:8080",
  "payload": {
    "session_id": "7c942c5f7af7454f9c8458f29242a0ea",
    "auth_result": "accepted",
    "flow_id": "<derived FlowID>",
    "transcript_hash": "<hash of transcript through KEM_EXCHANGE>",
    "auth_proof": "simulated-server-auth-binding",
    "note": "Educational AUTH packet only; no real cryptographic assurance."
  }
}
```

## DATA

```json
{
  "version": 1,
  "packet_type": "DATA",
  "flags": [],
  "header_length": 286,
  "flow_id": "<derived FlowID>",
  "source_node_id": "<client NodeID>",
  "destination_node_id": "<server NodeID>",
  "locator_hint": "udp://localhost:8080",
  "payload": {
    "session_id": "7c942c5f7af7454f9c8458f29242a0ea",
    "content": "Hello from the educational Internet-X client.",
    "transcript_hash": "<hash of transcript through AUTH>"
  }
}
```

## DATA_ACK

```json
{
  "version": 1,
  "packet_type": "DATA_ACK",
  "flags": [],
  "header_length": 296,
  "flow_id": "<derived FlowID>",
  "source_node_id": "<server NodeID>",
  "destination_node_id": "<client NodeID>",
  "locator_hint": "udp://localhost:8080",
  "payload": {
    "session_id": "7c942c5f7af7454f9c8458f29242a0ea",
    "status": "delivered",
    "flow_id": "<derived FlowID>",
    "received_bytes": 45,
    "transcript_hash": "<hash of transcript through DATA>",
    "note": "Educational DATA_ACK packet only."
  }
}
```
