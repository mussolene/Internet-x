from pathlib import Path
import socket
import time

import pytest

from refimpl import crypto
from refimpl.directory import JSONDirectory, JSONLocatorRegistry
from refimpl.engine import InternetXClient, InternetXServer
from refimpl.identity import NodeIdentity
from refimpl.packet import DATA, DATA_ACK, build_packet
from tests.helpers import make_udp_locator, reserve_udp_port, udp_port


def fixture(tmp_path: Path):
    server_identity = NodeIdentity.generate(name="server.test", locator=make_udp_locator(reserve_udp_port()))
    client_identity = NodeIdentity.generate(name="client.test", locator=make_udp_locator(reserve_udp_port()))
    directory = JSONDirectory.load(tmp_path / "directory.json")
    registry = JSONLocatorRegistry.load(tmp_path / "registry.json")
    directory.register_identity(server_identity)
    directory.register_identity(client_identity)
    registry.register_locator(server_identity.node_id, server_identity.locator, source="test")
    registry.register_locator(client_identity.node_id, client_identity.locator, source="test")
    return server_identity, client_identity, directory, registry


def stop_server(server: InternetXServer, thread) -> None:
    server.running = False
    try:
        poke = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        poke.sendto(b"{}", (server.host, server.port))
        poke.close()
    except OSError:
        pass
    thread.join(timeout=2)


def establish_flow(client: InternetXClient) -> None:
    init_ack = client.send_with_retry(client.build_init, {"INIT_ACK"})
    client.handle_init_ack(init_ack)
    auth = client.send_with_retry(client.build_kem_exchange, {"AUTH"})
    client.handle_auth(auth)


def test_retransmission_after_dropped_init_ack(tmp_path: Path) -> None:
    server_identity, client_identity, directory, registry = fixture(tmp_path)
    server = InternetXServer(server_identity, port=udp_port(server_identity.locator), drop_once={"INIT_ACK"})
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client = InternetXClient(client_identity, peer_name="server.test", directory=directory, registry=registry, retries=4)
        result = client.run("retry me")
        assert result["first_ack"]["status"] == "delivered"
    finally:
        stop_server(server, thread)


def test_malformed_packet_is_rejected() -> None:
    with pytest.raises(Exception):
        from refimpl.packet import decode_packet

        decode_packet("not-json")


def test_client_detects_downgrade_tampering(tmp_path: Path) -> None:
    server_identity, client_identity, directory, registry = fixture(tmp_path)
    server = InternetXServer(server_identity, port=udp_port(server_identity.locator))
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client = InternetXClient(client_identity, peer_name="server.test", directory=directory, registry=registry)
        init_ack = client.send_with_retry(client.build_init, {"INIT_ACK"})
        init_ack["payload"]["selected_pq_mode"] = "none"
        client.handle_init_ack(init_ack)
        with pytest.raises(RuntimeError):
            client.send_with_retry(client.build_kem_exchange, {"AUTH"})
    finally:
        stop_server(server, thread)


def test_replay_does_not_duplicate_application_delivery(tmp_path: Path) -> None:
    server_identity, client_identity, directory, registry = fixture(tmp_path)
    server = InternetXServer(server_identity, port=udp_port(server_identity.locator))
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client = InternetXClient(client_identity, peer_name="server.test", directory=directory, registry=registry)
        establish_flow(client)
        sequence = client.next_client_sequence
        packet = build_packet(
            DATA,
            session_id=client.session_id,
            source_node_id=client.identity.node_id,
            destination_node_id=client.peer.node_id,
            locator_hint=client.identity.locator,
            flow_id=client.flow_id,
            sequence=sequence,
            payload={},
        )
        packet["payload"] = crypto.encrypt_payload(
            packet,
            client.keys.client_to_server_key,
            client.keys.client_to_server_iv,
            sequence,
            {"content": "first", "sent_at": time.time()},
        )
        client.send_packet(packet)
        ack_one = client.receive_packet({DATA_ACK})
        client.send_packet(packet)
        ack_two = client.receive_packet({DATA_ACK})
        session = server.sessions[client.session_id]
        assert session.application_messages == ["first"]
        assert ack_one == ack_two
        client.sock.close()
    finally:
        stop_server(server, thread)
