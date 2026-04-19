from pathlib import Path
import socket
import time

import pytest

from refimpl import crypto
from refimpl.controlplane import build_locator_update_request
from refimpl.engine import InternetXClient, InternetXServer
from refimpl.identity import NodeIdentity
from refimpl.packet import AUTH, ERROR, INIT_ACK, LOCATOR_UPDATE, build_packet, decode_packet
from tests.helpers import make_udp_locator, reserve_udp_port, start_control_plane, stop_control_plane, udp_port


def fixture(tmp_path: Path):
    server_identity = NodeIdentity.generate(name="server.test", locator=make_udp_locator(reserve_udp_port()))
    client_identity = NodeIdentity.generate(name="client.test", locator=make_udp_locator(reserve_udp_port()))
    service, control_plane_thread, control_plane = start_control_plane(tmp_path)
    control_plane.register_identity(server_identity, locator=server_identity.locator, locator_version=1)
    return server_identity, client_identity, service, control_plane_thread, control_plane


def stop_server(server: InternetXServer, thread) -> None:
    server.stop()
    thread.join(timeout=2)


def establish_flow(client: InternetXClient) -> None:
    init_ack = client.send_with_retry(client.build_init, {INIT_ACK})
    client.handle_init_ack(init_ack)
    auth = client.send_with_retry(client.build_kem_exchange, {AUTH})
    client.handle_auth(auth)


def test_locator_update_changes_server_view(tmp_path: Path) -> None:
    server_identity, client_identity, service, control_plane_thread, control_plane = fixture(tmp_path)
    server = InternetXServer(server_identity, control_plane=control_plane, port=udp_port(server_identity.locator))
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client = InternetXClient(client_identity, peer_name="server.test", control_plane=control_plane)
        original_locator = client.identity.locator
        result = client.run("before move", perform_locator_update=True)
        session = server.sessions[client.session_id]
        assert session.client_locator != original_locator
        resolved_locator = control_plane.resolve_locator(client.identity.node_id)
        assert resolved_locator["locator"] == result["locator_update_ack"]["active_locator"]
    finally:
        stop_server(server, thread)
        stop_control_plane(service, control_plane_thread)


def test_stale_locator_update_counter_is_rejected(tmp_path: Path) -> None:
    server_identity, client_identity, service, control_plane_thread, control_plane = fixture(tmp_path)
    server = InternetXServer(server_identity, control_plane=control_plane, port=udp_port(server_identity.locator))
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client = InternetXClient(client_identity, peer_name="server.test", control_plane=control_plane)
        establish_flow(client)
        original_locator = client.identity.locator
        update_result = client.perform_locator_update()
        stale_fields = {
            "session_id": client.session_id,
            "flow_id": client.flow_id,
            "new_locator": update_result["active_locator"],
            "previous_locator": original_locator,
            "update_counter": 0,
        }
        stale_packet = build_packet(
            LOCATOR_UPDATE,
            session_id=client.session_id,
            source_node_id=client.identity.node_id,
            destination_node_id=client.peer.node_id,
            locator_hint=update_result["active_locator"],
            flow_id=client.flow_id,
            sequence=0,
            payload={
                "new_locator": update_result["active_locator"],
                "previous_locator": original_locator,
                "update_counter": 0,
                "signature": crypto.sign_fields(client.identity.signing_private(), "LOCATOR_UPDATE", stale_fields),
                "update_mac": crypto.compute_mac(client.keys.update_key, "LOCATOR_UPDATE", stale_fields),
            },
        )
        client.send_packet(stale_packet)
        raw, _ = client.sock.recvfrom(65535)
        error_packet = decode_packet(raw)
        session = server.sessions[client.session_id]
        assert error_packet["packet_type"] == ERROR
        assert "Stale locator update counter" in error_packet["payload"]["message"]
        assert session.last_locator_update_counter == 0
        client.sock.close()
    finally:
        stop_server(server, thread)
        stop_control_plane(service, control_plane_thread)


def test_control_plane_rejects_invalid_locator_update_signature(tmp_path: Path) -> None:
    server_identity, client_identity, service, control_plane_thread, control_plane = fixture(tmp_path)
    try:
        control_plane.register_identity(client_identity, locator=client_identity.locator, locator_version=1)
        tampered = build_locator_update_request(
            client_identity,
            previous_locator=client_identity.locator,
            new_locator=make_udp_locator(reserve_udp_port()),
            locator_version=2,
        )
        tampered["signature"] = tampered["signature"][:-4] + "AAAA"
        with pytest.raises(Exception):
            control_plane._request("POST", "/v1/update-locator", payload=tampered)
    finally:
        stop_control_plane(service, control_plane_thread)
