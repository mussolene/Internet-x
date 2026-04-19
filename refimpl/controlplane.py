"""Minimal authenticated control-plane service and client for Internet-X."""

from __future__ import annotations

from dataclasses import dataclass
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time
from typing import Any
from urllib import error, parse, request

from . import crypto
from .identity import NodeIdentity, PeerRecord, derive_node_id

REGISTER_LABEL = "CONTROL_PLANE_REGISTER"
LOCATOR_UPDATE_LABEL = "CONTROL_PLANE_LOCATOR_UPDATE"


class ControlPlaneError(ValueError):
    """Raised when control-plane validation fails."""

    def __init__(self, message: str, *, status: int = HTTPStatus.BAD_REQUEST) -> None:
        super().__init__(message)
        self.status = int(status)


class ControlPlaneClientError(RuntimeError):
    """Raised when a control-plane client request fails."""

    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass(slots=True)
class ControlPlaneRecord:
    name: str
    node_id: str
    algorithm_id: str
    signing_public_key: str
    locator: str
    locator_version: int
    issued_at: float
    expires_at: float

    def peer_record(self) -> PeerRecord:
        return PeerRecord(
            name=self.name,
            node_id=self.node_id,
            algorithm_id=self.algorithm_id,
            signing_public_key=self.signing_public_key,
            locator=self.locator,
        )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "node_id": self.node_id,
            "algorithm_id": self.algorithm_id,
            "signing_public_key": self.signing_public_key,
        }

    def locator_payload(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "locator": self.locator,
            "locator_version": self.locator_version,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }

    def full_payload(self) -> dict[str, Any]:
        payload = self.identity_payload()
        payload.update(self.locator_payload())
        return payload


def build_registration_fields(
    identity: NodeIdentity,
    *,
    locator: str | None = None,
    locator_version: int,
    issued_at: float,
    lease_seconds: int,
) -> dict[str, Any]:
    return {
        "name": identity.name,
        "node_id": identity.node_id,
        "algorithm_id": identity.algorithm_id,
        "signing_public_key": identity.signing_public_key,
        "locator": locator or identity.locator,
        "locator_version": locator_version,
        "issued_at": issued_at,
        "lease_seconds": lease_seconds,
    }


def build_registration_request(
    identity: NodeIdentity,
    *,
    locator: str | None = None,
    locator_version: int = 1,
    issued_at: float | None = None,
    lease_seconds: int = 60,
) -> dict[str, Any]:
    fields = build_registration_fields(
        identity,
        locator=locator,
        locator_version=locator_version,
        issued_at=time.time() if issued_at is None else issued_at,
        lease_seconds=lease_seconds,
    )
    return {
        **fields,
        "signature": crypto.sign_fields(identity.signing_private(), REGISTER_LABEL, fields),
    }


def build_locator_update_fields(
    identity: NodeIdentity,
    *,
    previous_locator: str,
    new_locator: str,
    locator_version: int,
    issued_at: float,
    lease_seconds: int,
) -> dict[str, Any]:
    return {
        "name": identity.name,
        "node_id": identity.node_id,
        "algorithm_id": identity.algorithm_id,
        "signing_public_key": identity.signing_public_key,
        "previous_locator": previous_locator,
        "new_locator": new_locator,
        "locator_version": locator_version,
        "issued_at": issued_at,
        "lease_seconds": lease_seconds,
    }


def build_locator_update_request(
    identity: NodeIdentity,
    *,
    previous_locator: str,
    new_locator: str,
    locator_version: int,
    issued_at: float | None = None,
    lease_seconds: int = 60,
) -> dict[str, Any]:
    fields = build_locator_update_fields(
        identity,
        previous_locator=previous_locator,
        new_locator=new_locator,
        locator_version=locator_version,
        issued_at=time.time() if issued_at is None else issued_at,
        lease_seconds=lease_seconds,
    )
    return {
        **fields,
        "signature": crypto.sign_fields(identity.signing_private(), LOCATOR_UPDATE_LABEL, fields),
    }


class ControlPlaneState:
    def __init__(
        self,
        *,
        max_lease_seconds: int = 300,
        max_clock_skew: float = 30.0,
        state_path: str | Path | None = None,
        trace_path: str | Path | None = None,
    ) -> None:
        self.max_lease_seconds = max_lease_seconds
        self.max_clock_skew = max_clock_skew
        self.state_path = Path(state_path) if state_path else None
        self.trace_path = Path(trace_path) if trace_path else None
        self._lock = threading.Lock()
        self._by_name: dict[str, ControlPlaneRecord] = {}
        self._by_node: dict[str, ControlPlaneRecord] = {}
        if self.trace_path:
            self.trace_path.parent.mkdir(parents=True, exist_ok=True)
            self.trace_path.write_text("", encoding="utf-8")

    def _write_trace(self, event: str, payload: dict[str, Any]) -> None:
        if not self.trace_path:
            return
        rendered = json.dumps({"event": event, "payload": payload}, ensure_ascii=True, sort_keys=True)
        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(rendered + "\n")

    def _persist_locked(self) -> None:
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "records": [record.full_payload() for record in sorted(self._by_node.values(), key=lambda item: item.name)],
        }
        self.state_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _prune_expired_locked(self, *, now: float | None = None) -> None:
        current_time = time.time() if now is None else now
        expired = [node_id for node_id, record in self._by_node.items() if record.expires_at <= current_time]
        for node_id in expired:
            record = self._by_node.pop(node_id)
            self._by_name.pop(record.name, None)
            self._write_trace("expire", record.full_payload())

    def _validate_identity_fields(self, data: dict[str, Any]) -> PeerRecord:
        required = ("name", "node_id", "algorithm_id", "signing_public_key")
        missing = [field for field in required if field not in data]
        if missing:
            raise ControlPlaneError(f"Missing control-plane fields: {', '.join(missing)}")
        expected_node_id = derive_node_id(str(data["algorithm_id"]), str(data["signing_public_key"]))
        if expected_node_id != str(data["node_id"]):
            raise ControlPlaneError("node_id does not match algorithm_id and signing_public_key.")
        return PeerRecord(
            name=str(data["name"]),
            node_id=str(data["node_id"]),
            algorithm_id=str(data["algorithm_id"]),
            signing_public_key=str(data["signing_public_key"]),
            locator=str(data.get("locator") or data.get("new_locator") or ""),
        )

    def _validate_timing(self, *, issued_at: float, lease_seconds: int) -> float:
        current_time = time.time()
        if lease_seconds <= 0 or lease_seconds > self.max_lease_seconds:
            raise ControlPlaneError(
                f"lease_seconds must be between 1 and {self.max_lease_seconds}.",
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        if issued_at < current_time - self.max_clock_skew:
            raise ControlPlaneError("Control-plane request is stale.", status=HTTPStatus.UNPROCESSABLE_ENTITY)
        if issued_at > current_time + self.max_clock_skew:
            raise ControlPlaneError("Control-plane request is too far in the future.", status=HTTPStatus.UNPROCESSABLE_ENTITY)
        return issued_at + lease_seconds

    def register(self, data: dict[str, Any]) -> dict[str, Any]:
        required = ("locator", "locator_version", "issued_at", "lease_seconds", "signature")
        missing = [field for field in required if field not in data]
        if missing:
            raise ControlPlaneError(f"Missing registration fields: {', '.join(missing)}")
        peer = self._validate_identity_fields(data)
        fields = build_registration_fields(
            NodeIdentity(
                name=peer.name,
                node_id=peer.node_id,
                algorithm_id=peer.algorithm_id,
                locator=str(data["locator"]),
                signing_public_key=peer.signing_public_key,
                signing_private_key="",
            ),
            locator=str(data["locator"]),
            locator_version=int(data["locator_version"]),
            issued_at=float(data["issued_at"]),
            lease_seconds=int(data["lease_seconds"]),
        )
        try:
            crypto.verify_fields(peer, REGISTER_LABEL, fields, str(data["signature"]))
        except crypto.CryptoError as exc:
            raise ControlPlaneError(str(exc), status=HTTPStatus.UNAUTHORIZED) from exc
        expires_at = self._validate_timing(issued_at=float(data["issued_at"]), lease_seconds=int(data["lease_seconds"]))
        locator_version = int(data["locator_version"])
        locator = str(data["locator"])
        with self._lock:
            self._prune_expired_locked()
            existing_name = self._by_name.get(peer.name)
            existing_node = self._by_node.get(peer.node_id)
            if existing_name and existing_name.node_id != peer.node_id:
                raise ControlPlaneError("Name is already bound to a different identity.", status=HTTPStatus.CONFLICT)
            if existing_node and (
                existing_node.name != peer.name
                or existing_node.algorithm_id != peer.algorithm_id
                or existing_node.signing_public_key != peer.signing_public_key
            ):
                raise ControlPlaneError("Identity binding mismatch for existing node.", status=HTTPStatus.CONFLICT)
            if existing_node:
                if locator_version < existing_node.locator_version:
                    raise ControlPlaneError("Stale registration locator_version.", status=HTTPStatus.CONFLICT)
                if locator_version == existing_node.locator_version and locator != existing_node.locator:
                    raise ControlPlaneError("Registration locator_version reuses an older locator slot.", status=HTTPStatus.CONFLICT)
            record = ControlPlaneRecord(
                name=peer.name,
                node_id=peer.node_id,
                algorithm_id=peer.algorithm_id,
                signing_public_key=peer.signing_public_key,
                locator=locator,
                locator_version=locator_version,
                issued_at=float(data["issued_at"]),
                expires_at=expires_at,
            )
            self._by_name[record.name] = record
            self._by_node[record.node_id] = record
            self._persist_locked()
            self._write_trace("register", record.full_payload())
            return {
                "status": "registered",
                "record": record.full_payload(),
            }

    def resolve_name(self, name: str) -> dict[str, Any]:
        with self._lock:
            self._prune_expired_locked()
            record = self._by_name.get(name)
            if record is None:
                raise ControlPlaneError(f"Unknown name: {name}", status=HTTPStatus.NOT_FOUND)
            return {
                "peer": record.identity_payload(),
            }

    def resolve_node(self, node_id: str) -> dict[str, Any]:
        with self._lock:
            self._prune_expired_locked()
            record = self._by_node.get(node_id)
            if record is None:
                raise ControlPlaneError(f"Unknown node_id: {node_id}", status=HTTPStatus.NOT_FOUND)
            return {
                "locator": record.locator_payload(),
            }

    def update_locator(self, data: dict[str, Any]) -> dict[str, Any]:
        required = ("previous_locator", "new_locator", "locator_version", "issued_at", "lease_seconds", "signature")
        missing = [field for field in required if field not in data]
        if missing:
            raise ControlPlaneError(f"Missing locator-update fields: {', '.join(missing)}")
        peer = self._validate_identity_fields(data)
        fields = build_locator_update_fields(
            NodeIdentity(
                name=peer.name,
                node_id=peer.node_id,
                algorithm_id=peer.algorithm_id,
                locator=str(data["new_locator"]),
                signing_public_key=peer.signing_public_key,
                signing_private_key="",
            ),
            previous_locator=str(data["previous_locator"]),
            new_locator=str(data["new_locator"]),
            locator_version=int(data["locator_version"]),
            issued_at=float(data["issued_at"]),
            lease_seconds=int(data["lease_seconds"]),
        )
        try:
            crypto.verify_fields(peer, LOCATOR_UPDATE_LABEL, fields, str(data["signature"]))
        except crypto.CryptoError as exc:
            raise ControlPlaneError(str(exc), status=HTTPStatus.UNAUTHORIZED) from exc
        expires_at = self._validate_timing(issued_at=float(data["issued_at"]), lease_seconds=int(data["lease_seconds"]))
        locator_version = int(data["locator_version"])
        previous_locator = str(data["previous_locator"])
        new_locator = str(data["new_locator"])
        with self._lock:
            self._prune_expired_locked()
            record = self._by_node.get(peer.node_id)
            if record is None:
                raise ControlPlaneError("Unknown node_id for locator update.", status=HTTPStatus.NOT_FOUND)
            if (
                record.name != peer.name
                or record.algorithm_id != peer.algorithm_id
                or record.signing_public_key != peer.signing_public_key
            ):
                raise ControlPlaneError("Identity binding mismatch for locator update.", status=HTTPStatus.CONFLICT)
            if locator_version <= record.locator_version:
                if locator_version == record.locator_version and new_locator == record.locator:
                    return {
                        "status": "updated",
                        "record": record.full_payload(),
                    }
                raise ControlPlaneError("Stale locator update.", status=HTTPStatus.CONFLICT)
            if record.locator != previous_locator:
                raise ControlPlaneError("Locator update previous_locator does not match the active locator.", status=HTTPStatus.CONFLICT)
            updated = ControlPlaneRecord(
                name=record.name,
                node_id=record.node_id,
                algorithm_id=record.algorithm_id,
                signing_public_key=record.signing_public_key,
                locator=new_locator,
                locator_version=locator_version,
                issued_at=float(data["issued_at"]),
                expires_at=expires_at,
            )
            self._by_name[updated.name] = updated
            self._by_node[updated.node_id] = updated
            self._persist_locked()
            self._write_trace("update_locator", updated.full_payload())
            return {
                "status": "updated",
                "record": updated.full_payload(),
            }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._prune_expired_locked()
            return {
                "records": [record.full_payload() for record in sorted(self._by_node.values(), key=lambda item: item.name)],
            }


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b"{}"
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ControlPlaneError(f"Invalid JSON body: {exc}") from exc
    if not isinstance(decoded, dict):
        raise ControlPlaneError("Control-plane request body must be a JSON object.")
    return decoded


def _write_json(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def build_handler(state: ControlPlaneState):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = parse.urlparse(self.path)
            parts = [parse.unquote(part) for part in parsed.path.split("/") if part]
            try:
                if parts == ["v1", "health"]:
                    _write_json(self, HTTPStatus.OK, {"status": "ok"})
                    return
                if len(parts) == 4 and parts[:3] == ["v1", "resolve", "name"]:
                    _write_json(self, HTTPStatus.OK, state.resolve_name(parts[3]))
                    return
                if len(parts) == 4 and parts[:3] == ["v1", "resolve", "node"]:
                    _write_json(self, HTTPStatus.OK, state.resolve_node(parts[3]))
                    return
                raise ControlPlaneError(f"Unknown GET path: {parsed.path}", status=HTTPStatus.NOT_FOUND)
            except ControlPlaneError as exc:
                _write_json(self, exc.status, {"error": str(exc)})

        def do_POST(self) -> None:  # noqa: N802
            parsed = parse.urlparse(self.path)
            try:
                data = _read_json_body(self)
                if parsed.path == "/v1/register":
                    _write_json(self, HTTPStatus.OK, state.register(data))
                    return
                if parsed.path == "/v1/update-locator":
                    _write_json(self, HTTPStatus.OK, state.update_locator(data))
                    return
                raise ControlPlaneError(f"Unknown POST path: {parsed.path}", status=HTTPStatus.NOT_FOUND)
            except ControlPlaneError as exc:
                _write_json(self, exc.status, {"error": str(exc)})

    return Handler


class ControlPlaneService:
    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 0,
        max_lease_seconds: int = 300,
        max_clock_skew: float = 30.0,
        state_path: str | Path | None = None,
        trace_path: str | Path | None = None,
    ) -> None:
        self.state = ControlPlaneState(
            max_lease_seconds=max_lease_seconds,
            max_clock_skew=max_clock_skew,
            state_path=state_path,
            trace_path=trace_path,
        )
        self.server = ThreadingHTTPServer((host, port), build_handler(self.state))
        self.server.daemon_threads = True

    @property
    def host(self) -> str:
        return str(self.server.server_address[0])

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def serve_forever(self) -> None:
        self.server.serve_forever(poll_interval=0.1)

    def serve_in_thread(self) -> threading.Thread:
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


class ControlPlaneClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 2.0,
        lease_seconds: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.lease_seconds = lease_seconds

    def _request(self, method: str, path: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = request.Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                payload = json.loads(raw)
                message = str(payload.get("error", raw))
            except json.JSONDecodeError:
                message = raw or str(exc)
            raise ControlPlaneClientError(message, status=exc.code) from exc
        except error.URLError as exc:
            raise ControlPlaneClientError(f"Control-plane request failed: {exc}") from exc
        decoded = json.loads(raw)
        if not isinstance(decoded, dict):
            raise ControlPlaneClientError("Control-plane response must be a JSON object.")
        return decoded

    def register_identity(
        self,
        identity: NodeIdentity,
        *,
        locator: str | None = None,
        locator_version: int = 1,
        lease_seconds: int | None = None,
        issued_at: float | None = None,
    ) -> dict[str, Any]:
        payload = build_registration_request(
            identity,
            locator=locator,
            locator_version=locator_version,
            issued_at=issued_at,
            lease_seconds=self.lease_seconds if lease_seconds is None else lease_seconds,
        )
        return self._request("POST", "/v1/register", payload=payload)

    def resolve_name(self, name: str) -> PeerRecord:
        response = self._request("GET", f"/v1/resolve/name/{parse.quote(name, safe='')}")
        peer = response["peer"]
        return PeerRecord(
            name=str(peer["name"]),
            node_id=str(peer["node_id"]),
            algorithm_id=str(peer["algorithm_id"]),
            signing_public_key=str(peer["signing_public_key"]),
            locator="",
        )

    def resolve_locator(self, node_id: str) -> dict[str, Any]:
        response = self._request("GET", f"/v1/resolve/node/{parse.quote(node_id, safe='')}")
        locator = response["locator"]
        if not isinstance(locator, dict):
            raise ControlPlaneClientError("Control-plane locator response must be an object.")
        return locator

    def resolve_peer(self, name: str) -> PeerRecord:
        peer = self.resolve_name(name)
        locator = self.resolve_locator(peer.node_id)
        peer.locator = str(locator["locator"])
        return peer

    def update_locator(
        self,
        identity: NodeIdentity,
        *,
        previous_locator: str,
        new_locator: str,
        locator_version: int,
        lease_seconds: int | None = None,
        issued_at: float | None = None,
    ) -> dict[str, Any]:
        payload = build_locator_update_request(
            identity,
            previous_locator=previous_locator,
            new_locator=new_locator,
            locator_version=locator_version,
            issued_at=issued_at,
            lease_seconds=self.lease_seconds if lease_seconds is None else lease_seconds,
        )
        return self._request("POST", "/v1/update-locator", payload=payload)
