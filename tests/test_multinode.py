from pathlib import Path
import socket
import time

from refimpl.directory import JSONDirectory, JSONLocatorRegistry
from refimpl.engine import InternetXClient, InternetXServer
from refimpl.identity import NodeIdentity
from tests.helpers import make_udp_locator, reserve_udp_port, udp_port


def stop_server(server: InternetXServer, thread) -> None:
    server.running = False
    try:
        poke = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        poke.sendto(b"{}", (server.host, server.port))
        poke.close()
    except OSError:
        pass
    thread.join(timeout=2)


def test_two_clients_establish_independent_sessions(tmp_path: Path) -> None:
    server_identity = NodeIdentity.generate(name="server.test", locator=make_udp_locator(reserve_udp_port()))
    client1_identity = NodeIdentity.generate(name="client.one", locator=make_udp_locator(reserve_udp_port()))
    client2_identity = NodeIdentity.generate(name="client.two", locator=make_udp_locator(reserve_udp_port()))
    directory = JSONDirectory.load(tmp_path / "directory.json")
    registry = JSONLocatorRegistry.load(tmp_path / "registry.json")
    for identity in (server_identity, client1_identity, client2_identity):
        directory.register_identity(identity)
        registry.register_locator(identity.node_id, identity.locator, source="test")

    server = InternetXServer(server_identity, port=udp_port(server_identity.locator))
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client1 = InternetXClient(client1_identity, peer_name="server.test", directory=directory, registry=registry)
        client2 = InternetXClient(client2_identity, peer_name="server.test", directory=directory, registry=registry)
        assert client1.run("from client one")["first_ack"]["status"] == "delivered"
        assert client2.run("from client two")["first_ack"]["status"] == "delivered"
        assert len(server.sessions) == 2
    finally:
        stop_server(server, thread)
