# Protocol Header Model

## Diagram
```
+-------------------------------+
|         Protocol Header       |
+-------------------------------+
| Version        | 1 byte      |
| PacketType     | 1 byte      |
| Flags          | 1 byte      |
| HeaderLength   | 2 bytes     |
| FlowID         | 4 bytes     |
| SourceNodeID   | 4 bytes     |
| DestinationNodeID | 4 bytes  |
| LocatorHint    | 4 bytes     |
| Payload        | Variable    |
+-------------------------------+
```

## Field Explanations
1. **Version**: 1 byte indication of the protocol version in use.
2. **PacketType**: 1 byte field indicating the type of packet (e.g., request, response).
3. **Flags**: 1 byte field for various flags (e.g., reserved bits, control bits).
4. **HeaderLength**: 2 bytes indicating the length of the header.
5. **FlowID**: 4 bytes uniquely identifying the packet flow.
6. **SourceNodeID**: 4 bytes identifying the source node.
7. **DestinationNodeID**: 4 bytes identifying the destination node.
8. **LocatorHint**: 4 bytes providing hints for routing to the payload.
9. **Payload**: A variable-length field that contains the actual data of the packet.