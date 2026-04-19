# Packet Examples

This document provides example descriptions for various packet types utilized in the communication protocol.

## INIT

### Description:
The INIT packet is the first message sent to initiate the connection. It contains the necessary information to begin handshaking between the parties.

### Example:
```
INIT:
{
  "session_id": "123456",
  "client_id": "user123",
  "timestamp": "2026-04-19T06:02:26Z"
}
```

## INIT_ACK

### Description:
The INIT_ACK packet is sent in response to an INIT packet, acknowledging the receipt and acceptance of the request.

### Example:
```
INIT_ACK:
{
  "session_id": "123456",
  "status": "accepted",
  "server_id": "server321",
  "timestamp": "2026-04-19T06:02:26Z"
}
```

## KEM_EXCHANGE

### Description:
The KEM_EXCHANGE packet is used during the key exchange process to securely share encryption keys between parties.

### Example:
```
KEM_EXCHANGE:
{
  "session_id": "123456",
  "public_key": "abcdef123456",
  "timestamp": "2026-04-19T06:02:26Z"
}
```

## AUTH

### Description:
The AUTH packet is sent to authenticate a user once the connection is established. It includes user credentials and proof of identity.

### Example:
```
AUTH:
{
  "session_id": "123456",
  "username": "user123",
  "password_hash": "hashed_password",
  "timestamp": "2026-04-19T06:02:26Z"
}
```

## DATA

### Description:
The DATA packet is used to transmit actual data after the connection has been established and authenticated.

### Example:
```
DATA:
{
  "session_id": "123456",
  "data": "Hello, this is a data message.",
  "timestamp": "2026-04-19T06:02:26Z"
}
```
