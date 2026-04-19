# Handshake Protocol Description

This document outlines the detailed packet-by-packet description for the handshake procedure in the handshake protocol implemented in this repository. The handshake consists of five main phases: INIT, INIT_ACK, KEM_EXCHANGE, AUTH, and DATA.

## Phase 1: INIT
- **Packet Purpose**: Initiate the handshake process.
- **Sender/Receiver Behavior**: The initiator sends this packet to start the handshake. The receiver prepares to respond.
- **Fields**: 
  - `session_id`: Unique identifier for this handshake session.
  - `nonce`: Random value used to ensure uniqueness of this handshake.
- **Transcript Hash**: A hash is calculated over the fields in this packet to ensure integrity.
- **Key Derivation**: Derive initial secrets using a KDF (Key Derivation Function) based on the nonce and session_id.
- **Hybrid Mode Behavior**: In hybrid mode, the sender includes additional metadata associated with both key types.
- **Fallback Behavior**: If the receiver is not in the appropriate state to handle this packet, it sends an error response.

## Phase 2: INIT_ACK
- **Packet Purpose**: Acknowledge the INIT packet and proceed.
- **Sender/Receiver Behavior**: The receiver responds to the INIT with this packet. The sender continues the process.
- **Fields**:
  - `session_id`: Echo of the session ID from the INIT.
  - `status`: Status of the handshake initialization.
- **Transcript Hash**: Updated to include the INIT packet's hash.
- **Key Derivation**: Further secrets derived using information from INIT and this packet.
- **Hybrid Mode Behavior**: Depending on the mode, additional keys may be included.
- **Fallback Behavior**: If unexpected fields are encountered, the handshake aborts with an error.

## Phase 3: KEM_EXCHANGE
- **Packet Purpose**: Key Encapsulation Mechanism exchange.
- **Sender/Receiver Behavior**: Both parties exchange key material to establish a shared secret.
- **Fields**:
  - `public_key`: The public key of the sender.
  - `encapsulated_key`: Encrypted session key.
- **Transcript Hash**: Includes hashes of all previous packets.
- **Key Derivation**: Derive shared secrets from exchanged key material.
- **Hybrid Mode Behavior**: Handles both classical and post-quantum keys.
- **Fallback Behavior**: In case of decryption failure, send a failure notice.

## Phase 4: AUTH
- **Packet Purpose**: Authenticate the handshake environment.
- **Sender/Receiver Behavior**: The sender authenticates itself to the receiver using this packet.
- **Fields**:
  - `auth_token`: Token for authentication.
  - `signature`: Digital signature to verify sender identity.
- **Transcript Hash**: Now includes all previous messages.
- **Key Derivation**: Update the keying material based on successful authentication.
- **Hybrid Mode Behavior**: Supports additional checks for hybrid authentication.
- **Fallback Behavior**: If authentication fails, a warning is issued to the sender.

## Phase 5: DATA
- **Packet Purpose**: Start transferring encrypted data.
- **Sender/Receiver Behavior**: The protocol transitions to data transfer mode.
- **Fields**:
  - `data`: The encrypted payload for transmission.
- **Transcript Hash**: Finalization hash after authentication.
- **Key Derivation**: Establish final encryption keys for data transfer.
- **Hybrid Mode Behavior**: Data packets may need special handling depending on the already established keys.
- **Fallback Behavior**: If the data link layer fails, an error is reported.

---
This document serves as the authoritative reference for the handshake protocol implemented in this repository. For further discussions, please refer to the documentation or contact the maintainers directly.
