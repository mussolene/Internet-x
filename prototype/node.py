"""Identity abstraction for the educational Internet-X prototype."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib


@dataclass(frozen=True, slots=True)
class NodeIdentity:
    """Stable node identity plus current locator information.

    The prototype mirrors the architectural rule:
    NodeID = HASH(algorithm_id || public_key)

    The digest and public material are simulated for educational purposes.
    """

    name: str
    node_id: str
    algorithm_id: str
    locator: str

    @classmethod
    def from_public_material(
        cls,
        *,
        name: str,
        algorithm_id: str,
        locator: str,
        public_key_material: str,
    ) -> "NodeIdentity":
        node_id = hashlib.sha256(f"{algorithm_id}|{public_key_material}".encode("utf-8")).hexdigest()
        return cls(name=name, node_id=node_id, algorithm_id=algorithm_id, locator=locator)

    def with_locator(self, locator: str) -> "NodeIdentity":
        """Return the same identity at a new locator."""

        return replace(self, locator=locator)

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "node_id": self.node_id,
            "algorithm_id": self.algorithm_id,
            "locator": self.locator,
        }
