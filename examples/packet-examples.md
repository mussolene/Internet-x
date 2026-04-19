# Packet Examples

These examples reflect the v0.2 reference implementation and use simplified placeholders.

## INIT

```json
{
  "version": 2,
  "packet_type": "INIT",
  "flags": [],
  "header_length": 310,
  "session_id": "<session-id>",
  "flow_id": null,
  "sequence": null,
  "source_node_id": "<client-node-id>",
  "destination_node_id": "<server-node-id>",
  "locator_hint": "udp://127.0.0.1:10080",
  "payload": {
    "sender_name": "client.demo",
    "identity_algorithm": "ed25519+x25519",
    "signing_public_key": "<client-signing-public-key-b64>",
    "client_ephemeral_key": "<client-ephemeral-x25519-pub-b64>",
    "supported_suites": ["x25519+ed25519+chacha20poly1305"],
    "supported_pq_modes": ["simulated-ml-kem-768", "none"],
    "allow_classical_fallback": true,
    "client_nonce": "<nonce>",
    "note": "Client requests identity-bound flow establishment."
  }
}
```

## AUTH

```json
{
  "version": 2,
  "packet_type": "AUTH",
  "flags": [],
  "header_length": 300,
  "session_id": "<session-id>",
  "flow_id": "<flow-id>",
  "sequence": null,
  "source_node_id": "<server-node-id>",
  "destination_node_id": "<client-node-id>",
  "locator_hint": "udp://127.0.0.1:9080",
  "payload": {
    "auth_result": "accepted",
    "selected_suite": "x25519+ed25519+chacha20poly1305",
    "selected_pq_mode": "simulated-ml-kem-768",
    "fallback_used": false,
    "transcript_hash": "<sha256>",
    "server_signature": "<ed25519-signature-b64>",
    "key_confirmation": "<hmac-sha256-hex>",
    "note": "PQ mode remains simulated if selected; baseline authentication and AEAD are real classical crypto."
  }
}
```

## DATA

```json
{
  "version": 2,
  "packet_type": "DATA",
  "flags": [],
  "header_length": 220,
  "session_id": "<session-id>",
  "flow_id": "<flow-id>",
  "sequence": 0,
  "source_node_id": "<client-node-id>",
  "destination_node_id": "<server-node-id>",
  "locator_hint": "udp://127.0.0.1:10080",
  "payload": {
    "nonce": "<nonce-b64>",
    "ciphertext": "<aead-ciphertext-b64>"
  }
}
```
