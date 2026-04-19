# Internet-X: Identity-First Experimental Network Architecture

Internet-X is an experimental protocol architecture designed to separate and decouple fundamental network concepts that the classical IP model conflates: human-readable naming, cryptographic identity, network location, and route selection.

## Core Model

The Internet-X architecture is built on a simple but powerful mapping:

```
Name -> Identity -> Locator -> Path
```

Where:
- **Name**: Human-readable, application-level identifier (e.g., user@service)
- **Identity (NodeID)**: Cryptographic identifier derived from public key material
- **Locator**: Current reachability information (IP address, port, endpoint)
- **Path**: Selected route through the network overlay

## Why the Current IP Model Is Insufficient

The classical Internet Protocol binds identity to location. An IP address simultaneously represents:
1. Who you are (identity)
2. Where you are (location)
3. Your path to the Internet

This coupling creates fundamental problems:
- **Mobility breaks connections**: Moving networks changes your address, severing sessions
- **Multihoming is complex**: Multiple addresses complicate identity verification
- **Scalability issues**: DNS and routing operate on the same address space
- **Security is location-dependent**: Endpoint authentication tied to topology
- **Privacy concerns**: Your location is your identity to observers

## What Internet-X Changes

Internet-X decouples these concerns:

1. **Separation of concerns**: Name, identity, location, and path are independent layers
2. **Identity-first design**: Cryptographic identity is the stable anchor
3. **Transparent mobility**: Change locators without disrupting sessions
4. **Post-quantum ready**: Handshake designed with hybrid ML-KEM/ML-DSA support
5. **Overlay deployment**: Runs over existing IPv4/IPv6 infrastructure initially
6. **Future path**: Designed for eventual native deployment

## Repository Layout

```
internet-x/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .gitignore                   # Python and LaTeX ignores
├── spec/                        # Technical specifications
│   ├── ixp-v0.1.md             # Core protocol specification
│   ├── handshake.md            # Detailed handshake phases
│   └── packet-format.md        # Wire protocol format
├── ietf/                        # IETF Internet-Draft style
│   └── draft-internetx-00.md
├── paper/                       # Academic paper materials
│   ├── abstract.md             # arXiv abstract
│   └── internetx.tex           # LaTeX paper source
├── examples/                    # Protocol examples and traces
│   ├── handshake-trace.txt     # Realistic handshake transcript
│   └── packet-examples.md      # Packet format examples
└── prototype/                   # Educational reference implementation
    ├── README.md               # Prototype documentation
    ├── protocol.py             # Protocol definitions and helpers
    ├── node.py                 # Node identity abstraction
    ├── server.py               # Reference UDP server
    └── client.py               # Reference UDP client
```

## Handshake Overview

Internet-X uses a five-phase handshake:

1. **INIT**: Client initiates connection with ephemeral key material
2. **INIT_ACK**: Server responds with its own key material and session identifier
3. **KEM_EXCHANGE**: Client sends encapsulated key material (classical + PQ candidates)
4. **AUTH**: Server sends authentication confirmation and initial flow key material
5. **DATA**: Regular encrypted data exchange

The handshake transcript is hashed and bound into the session key, ensuring mutual authentication and perfect forward secrecy properties.

## Hybrid Post-Quantum Design

Internet-X handshake is designed to operate in hybrid mode:
- **Primary track**: Classical cryptography (X25519 / Ed25519)
- **Secondary track**: Post-quantum candidates (ML-KEM / ML-DSA)
- **Fallback**: If either mechanism is unavailable, single-track operation is supported

This allows deployment today while supporting future quantum-resistant operation.

## Status and Roadmap

**Current Status**: Experimental specification and educational prototype (v0.1)

**Roadmap**:
- v0.1: Core specification and basic prototype
- v0.2: Extended mobility handling and path selection
- v0.3: Full hybrid PQ evaluation and performance analysis
- v1.0: Candidate for standardization consideration

## Disclaimer

**This is an experimental project.** Internet-X is:
- Not production-ready
- Not approved for critical infrastructure
- A research platform for exploring identity-first network design
- Intended for educational and academic study

The prototype implementation includes simulated cryptography for demonstration purposes only. Do not use it for real security-sensitive applications.

## Author

**mussolene**

## License

MIT License. See LICENSE file for details.