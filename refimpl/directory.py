"""Simple JSON-backed name and locator services for the reference implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Any

from .identity import NodeIdentity, PeerRecord


@dataclass(slots=True)
class JSONDirectory:
    path: Path
    entries: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "JSONDirectory":
        file_path = Path(path)
        if file_path.exists():
            data = json.loads(file_path.read_text(encoding="utf-8"))
            entries = data.get("entries", {})
        else:
            entries = {}
        return cls(path=file_path, entries=entries)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"entries": self.entries}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def register_identity(self, identity: NodeIdentity | PeerRecord) -> None:
        if isinstance(identity, NodeIdentity):
            record = identity.peer_record().as_dict()
        else:
            record = identity.as_dict()
        self.entries[record["name"]] = record
        self.save()

    def resolve_name(self, name: str) -> PeerRecord:
        try:
            entry = self.entries[name]
        except KeyError as exc:
            raise KeyError(f"Unknown name: {name}") from exc
        return PeerRecord(**entry)


@dataclass(slots=True)
class JSONLocatorRegistry:
    path: Path
    locators: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "JSONLocatorRegistry":
        file_path = Path(path)
        if file_path.exists():
            data = json.loads(file_path.read_text(encoding="utf-8"))
            locators = data.get("locators", {})
        else:
            locators = {}
        return cls(path=file_path, locators=locators)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"locators": self.locators}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def register_locator(self, node_id: str, locator: str, *, epoch: int | None = None, source: str = "local") -> None:
        current = self.locators.get(node_id, {})
        next_epoch = epoch if epoch is not None else int(current.get("epoch", 0)) + 1
        self.locators[node_id] = {
            "locator": locator,
            "epoch": next_epoch,
            "source": source,
        }
        self.save()

    def lookup(self, node_id: str) -> dict[str, Any]:
        try:
            return self.locators[node_id]
        except KeyError as exc:
            raise KeyError(f"Unknown node_id locator mapping: {node_id}") from exc
