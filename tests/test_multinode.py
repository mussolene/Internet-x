from pathlib import Path
import time

from refimpl.engine import InternetXClient, InternetXServer
from refimpl.identity import NodeIdentity
from tests.helpers import make_udp_locator, reserve_udp_port, start_control_plane, stop_control_plane, udp_port


def stop_server(server: InternetXServer, thread) -> None:
    server.stop()
    thread.join(timeout=2)


def test_two_clients_establish_independent_sessions(tmp_path: Path) -> None:
    server_identity = NodeIdentity.generate(name="server.test", locator=make_udp_locator(reserve_udp_port()))
    client1_identity = NodeIdentity.generate(name="client.one", locator=make_udp_locator(reserve_udp_port()))
    client2_identity = NodeIdentity.generate(name="client.two", locator=make_udp_locator(reserve_udp_port()))
    service, control_plane_thread, control_plane = start_control_plane(tmp_path)
    control_plane.register_identity(server_identity, locator=server_identity.locator, locator_version=1)

    server = InternetXServer(server_identity, control_plane=control_plane, port=udp_port(server_identity.locator))
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client1 = InternetXClient(client1_identity, peer_name="server.test", control_plane=control_plane)
        client2 = InternetXClient(client2_identity, peer_name="server.test", control_plane=control_plane)
        assert client1.run("from client one")["first_ack"]["status"] == "delivered"
        assert client2.run("from client two")["first_ack"]["status"] == "delivered"
        assert len(server.sessions) == 2
    finally:
        stop_server(server, thread)
        stop_control_plane(service, control_plane_thread)
