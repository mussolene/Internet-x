from pathlib import Path
import socket
import time

from refimpl.directory import JSONDirectory, JSONLocatorRegistry
from refimpl.engine import InternetXClient, InternetXServer
from refimpl.identity import NodeIdentity
from tests.helpers import make_udp_locator, reserve_udp_port, udp_port


def build_fixture(tmp_path: Path):
    server_identity = NodeIdentity.generate(name="server.test", locator=make_udp_locator(reserve_udp_port()))
    client_identity = NodeIdentity.generate(name="client.test", locator=make_udp_locator(reserve_udp_port()))
    directory = JSONDirectory.load(tmp_path / "directory.json")
    registry = JSONLocatorRegistry.load(tmp_path / "registry.json")
    directory.register_identity(server_identity)
    directory.register_identity(client_identity)
    registry.register_locator(server_identity.node_id, server_identity.locator, source="test")
    registry.register_locator(client_identity.node_id, client_identity.locator, source="test")
    return server_identity, client_identity, directory, registry


def test_successful_handshake_and_data_exchange(tmp_path: Path) -> None:
    server_identity, client_identity, directory, registry = build_fixture(tmp_path)
    server = InternetXServer(server_identity, port=udp_port(server_identity.locator), trace_path=tmp_path / "server.log")
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client = InternetXClient(
            client_identity,
            peer_name="server.test",
            directory=directory,
            registry=registry,
            trace_path=tmp_path / "client.log",
        )
        result = client.run("hello world", perform_locator_update=True)
        assert result["first_ack"]["status"] == "delivered"
        assert result["locator_update_ack"]["active_locator"].startswith("udp://127.0.0.1:")
        assert result["second_ack"]["status"] == "delivered"
        session = server.sessions[client.session_id]
        assert session.application_messages[0] == "hello world"
        assert session.application_messages[1].endswith("[post-migration]")
    finally:
        server.running = False
        try:
            poke = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            poke.sendto(b"{}", (server.host, server.port))
            poke.close()
        except OSError:
            pass
        thread.join(timeout=2)
