"""Identity material and peer records for Internet-X."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import base64
import hashlib
import json
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


DEFAULT_ALGORITHM_ID = "ed25519+x25519"


def _b64encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")



def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))



def derive_node_id(algorithm_id: str, signing_public_key_b64: str) -> str:
    material = f"{algorithm_id}||{signing_public_key_b64}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


@dataclass(slots=True)
class PeerRecord:
    name: str
    node_id: str
    algorithm_id: str
    signing_public_key: str
    locator: str

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "node_id": self.node_id,
            "algorithm_id": self.algorithm_id,
            "signing_public_key": self.signing_public_key,
            "locator": self.locator,
        }


@dataclass(slots=True)
class NodeIdentity:
    name: str
    node_id: str
    algorithm_id: str
    locator: str
    signing_public_key: str
    signing_private_key: str

    @classmethod
    def generate(
        cls,
        *,
        name: str,
        locator: str,
        algorithm_id: str = DEFAULT_ALGORITHM_ID,
    ) -> "NodeIdentity":
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        private_raw = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_raw = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        signing_public_key = _b64encode(public_raw)
        return cls(
            name=name,
            node_id=derive_node_id(algorithm_id, signing_public_key),
            algorithm_id=algorithm_id,
            locator=locator,
            signing_public_key=signing_public_key,
            signing_private_key=_b64encode(private_raw),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NodeIdentity":
        required = {
            "name",
            "node_id",
            "algorithm_id",
            "locator",
            "signing_public_key",
            "signing_private_key",
        }
        missing = sorted(required - data.keys())
        if missing:
            raise ValueError(f"Identity file missing keys: {', '.join(missing)}")
        expected_node_id = derive_node_id(data["algorithm_id"], data["signing_public_key"])
        if expected_node_id != data["node_id"]:
            raise ValueError("Identity node_id does not match algorithm_id and signing_public_key.")
        return cls(**{key: data[key] for key in required})

    def signing_private(self) -> ed25519.Ed25519PrivateKey:
        return ed25519.Ed25519PrivateKey.from_private_bytes(_b64decode(self.signing_private_key))

    def signing_public(self) -> ed25519.Ed25519PublicKey:
        return ed25519.Ed25519PublicKey.from_public_bytes(_b64decode(self.signing_public_key))

    def peer_record(self) -> PeerRecord:
        return PeerRecord(
            name=self.name,
            node_id=self.node_id,
            algorithm_id=self.algorithm_id,
            signing_public_key=self.signing_public_key,
            locator=self.locator,
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "node_id": self.node_id,
            "algorithm_id": self.algorithm_id,
            "locator": self.locator,
            "signing_public_key": self.signing_public_key,
            "signing_private_key": self.signing_private_key,
        }

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return destination

    @classmethod
    def load(cls, path: str | Path) -> "NodeIdentity":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
