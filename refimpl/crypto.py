"""Cryptographic helpers for the Internet-X reference implementation."""

from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
import hmac
import json
import os
from typing import Any, Iterable, Mapping

from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization

from .identity import PeerRecord
from .packet import canonical_json, packet_aad


CLASSICAL_SUITE = "x25519+ed25519+chacha20poly1305"
SIMULATED_PQ_MODE = "simulated-ml-kem-768"
NO_PQ_MODE = "none"
SUPPORTED_SUITES = [CLASSICAL_SUITE]
SUPPORTED_PQ_MODES = [SIMULATED_PQ_MODE, NO_PQ_MODE]


@dataclass(slots=True)
class SessionKeys:
    handshake_key: bytes
    update_key: bytes
    client_to_server_key: bytes
    server_to_client_key: bytes
    client_to_server_iv: bytes
    server_to_client_iv: bytes


class CryptoError(ValueError):
    """Raised when cryptographic validation fails."""



def b64encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")



def b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))



def random_token(size: int = 16) -> str:
    return os.urandom(size).hex()



def transcript_hash(messages: Iterable[Any]) -> str:
    rendered = "||".join(canonical_json(message) for message in messages)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()



def sha256_hex(*parts: str) -> str:
    material = "||".join(parts).encode("utf-8")
    return hashlib.sha256(material).hexdigest()



def generate_ephemeral_keypair() -> tuple[x25519.X25519PrivateKey, str]:
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private_key, b64encode(public_key)



def compute_shared_secret(private_key: x25519.X25519PrivateKey, peer_public_b64: str) -> bytes:
    peer_public = x25519.X25519PublicKey.from_public_bytes(b64decode(peer_public_b64))
    return private_key.exchange(peer_public)



def mix_secret(
    classical_secret: bytes,
    *,
    selected_pq_mode: str,
    client_pq_share: str | None,
    server_pq_share: str | None,
) -> bytes:
    if selected_pq_mode == SIMULATED_PQ_MODE:
        if not client_pq_share or not server_pq_share:
            raise CryptoError("Hybrid mode selected but simulated PQ shares are missing.")
        pq_material = hashlib.sha256(
            b"pq-simulated||" + b64decode(client_pq_share) + b64decode(server_pq_share)
        ).digest()
    else:
        pq_material = b""
    return hashlib.sha256(classical_secret + pq_material).digest()



def derive_keys(
    mixed_secret: bytes,
    *,
    session_id: str,
    client_node_id: str,
    server_node_id: str,
    transcript_digest: str,
) -> SessionKeys:
    info = canonical_json(
        {
            "context": "internet-x-v0.2",
            "session_id": session_id,
            "client_node_id": client_node_id,
            "server_node_id": server_node_id,
            "transcript_hash": transcript_digest,
        }
    ).encode("utf-8")
    hkdf = HKDF(algorithm=hashes.SHA256(), length=144, salt=None, info=info)
    output = hkdf.derive(mixed_secret)
    return SessionKeys(
        handshake_key=output[0:32],
        update_key=output[32:64],
        client_to_server_key=output[64:96],
        server_to_client_key=output[96:128],
        client_to_server_iv=output[128:136],
        server_to_client_iv=output[136:144],
    )



def derive_flow_id(
    *,
    session_id: str,
    client_node_id: str,
    server_node_id: str,
    transcript_digest: str,
    selected_suite: str,
    selected_pq_mode: str,
) -> str:
    return sha256_hex(
        "flow",
        session_id,
        client_node_id,
        server_node_id,
        transcript_digest,
        selected_suite,
        selected_pq_mode,
    )



def _signature_context(label: str, fields: Mapping[str, Any]) -> bytes:
    return canonical_json({"label": label, "fields": fields}).encode("utf-8")



def sign_fields(private_key: ed25519.Ed25519PrivateKey, label: str, fields: Mapping[str, Any]) -> str:
    return b64encode(private_key.sign(_signature_context(label, fields)))



def verify_fields(peer: PeerRecord, label: str, fields: Mapping[str, Any], signature_b64: str) -> None:
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(b64decode(peer.signing_public_key))
    try:
        public_key.verify(b64decode(signature_b64), _signature_context(label, fields))
    except Exception as exc:  # pragma: no cover - cryptography raises multiple exception types
        raise CryptoError(f"Signature verification failed for {label}.") from exc



def compute_mac(key: bytes, label: str, fields: Mapping[str, Any]) -> str:
    return hmac.new(key, _signature_context(label, fields), hashlib.sha256).hexdigest()



def verify_mac(key: bytes, label: str, fields: Mapping[str, Any], provided: str) -> None:
    expected = compute_mac(key, label, fields)
    if not hmac.compare_digest(expected, provided):
        raise CryptoError(f"MAC verification failed for {label}.")



def packet_nonce(iv_seed: bytes, sequence: int) -> bytes:
    return iv_seed + sequence.to_bytes(4, "big")



def encrypt_payload(packet: Mapping[str, Any], key: bytes, iv_seed: bytes, sequence: int, plaintext: Mapping[str, Any]) -> dict[str, str]:
    cipher = ChaCha20Poly1305(key)
    nonce = packet_nonce(iv_seed, sequence)
    ciphertext = cipher.encrypt(nonce, canonical_json(plaintext).encode("utf-8"), packet_aad(packet))
    return {
        "nonce": b64encode(nonce),
        "ciphertext": b64encode(ciphertext),
    }



def decrypt_payload(packet: Mapping[str, Any], key: bytes, payload: Mapping[str, Any]) -> dict[str, Any]:
    cipher = ChaCha20Poly1305(key)
    try:
        plaintext = cipher.decrypt(
            b64decode(str(payload["nonce"])),
            b64decode(str(payload["ciphertext"])),
            packet_aad(packet),
        )
    except Exception as exc:  # pragma: no cover - cryptography raises multiple exception types
        raise CryptoError("AEAD authentication failed.") from exc
    decoded = json.loads(plaintext.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise CryptoError("Encrypted payload must decode to a JSON object.")
    return decoded
