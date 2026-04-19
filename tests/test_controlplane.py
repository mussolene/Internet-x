from pathlib import Path
import time

import pytest

from refimpl.controlplane import (
    ControlPlaneClientError,
    build_locator_update_request,
    build_registration_request,
)
from refimpl.identity import NodeIdentity
from tests.helpers import make_udp_locator, reserve_udp_port, start_control_plane, stop_control_plane


def test_authenticated_registration_and_resolution(tmp_path: Path) -> None:
    service, control_plane_thread, control_plane = start_control_plane(tmp_path)
    identity = NodeIdentity.generate(name="node.test", locator=make_udp_locator(reserve_udp_port()))
    try:
        registered = control_plane.register_identity(identity, locator=identity.locator, locator_version=1)
        peer = control_plane.resolve_name(identity.name)
        locator = control_plane.resolve_locator(identity.node_id)
        assert registered["status"] == "registered"
        assert peer.node_id == identity.node_id
        assert locator["locator"] == identity.locator
        assert locator["locator_version"] == 1
    finally:
        stop_control_plane(service, control_plane_thread)


def test_authenticated_locator_update(tmp_path: Path) -> None:
    service, control_plane_thread, control_plane = start_control_plane(tmp_path)
    identity = NodeIdentity.generate(name="node.test", locator=make_udp_locator(reserve_udp_port()))
    next_locator = make_udp_locator(reserve_udp_port())
    try:
        control_plane.register_identity(identity, locator=identity.locator, locator_version=1)
        updated = control_plane.update_locator(
            identity,
            previous_locator=identity.locator,
            new_locator=next_locator,
            locator_version=2,
        )
        resolved = control_plane.resolve_locator(identity.node_id)
        assert updated["status"] == "updated"
        assert updated["record"]["locator"] == next_locator
        assert resolved["locator"] == next_locator
        assert resolved["locator_version"] == 2
    finally:
        stop_control_plane(service, control_plane_thread)


def test_invalid_locator_update_signature_is_rejected(tmp_path: Path) -> None:
    service, control_plane_thread, control_plane = start_control_plane(tmp_path)
    identity = NodeIdentity.generate(name="node.test", locator=make_udp_locator(reserve_udp_port()))
    try:
        control_plane.register_identity(identity, locator=identity.locator, locator_version=1)
        tampered = build_locator_update_request(
            identity,
            previous_locator=identity.locator,
            new_locator=make_udp_locator(reserve_udp_port()),
            locator_version=2,
        )
        tampered["signature"] = tampered["signature"][:-4] + "AAAA"
        with pytest.raises(ControlPlaneClientError):
            control_plane._request("POST", "/v1/update-locator", payload=tampered)
    finally:
        stop_control_plane(service, control_plane_thread)


def test_stale_locator_update_is_rejected(tmp_path: Path) -> None:
    service, control_plane_thread, control_plane = start_control_plane(tmp_path)
    identity = NodeIdentity.generate(name="node.test", locator=make_udp_locator(reserve_udp_port()))
    try:
        control_plane.register_identity(identity, locator=identity.locator, locator_version=1)
        with pytest.raises(ControlPlaneClientError):
            control_plane.update_locator(
                identity,
                previous_locator=identity.locator,
                new_locator=make_udp_locator(reserve_udp_port()),
                locator_version=1,
            )
    finally:
        stop_control_plane(service, control_plane_thread)


def test_lease_expiry_removes_locator_resolution(tmp_path: Path) -> None:
    service, control_plane_thread, control_plane = start_control_plane(tmp_path, lease_seconds=1)
    identity = NodeIdentity.generate(name="node.test", locator=make_udp_locator(reserve_udp_port()))
    try:
        request_payload = build_registration_request(identity, locator_version=1, lease_seconds=1)
        control_plane._request("POST", "/v1/register", payload=request_payload)
        time.sleep(1.2)
        with pytest.raises(ControlPlaneClientError):
            control_plane.resolve_locator(identity.node_id)
    finally:
        stop_control_plane(service, control_plane_thread)
