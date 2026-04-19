from pathlib import Path
import time

from refimpl.engine import InternetXClient, InternetXServer
from refimpl.identity import NodeIdentity
from tests.helpers import make_udp_locator, reserve_udp_port, start_control_plane, stop_control_plane, udp_port


def build_fixture(tmp_path: Path):
    server_identity = NodeIdentity.generate(name="server.test", locator=make_udp_locator(reserve_udp_port()))
    client_identity = NodeIdentity.generate(name="client.test", locator=make_udp_locator(reserve_udp_port()))
    service, control_plane_thread, control_plane = start_control_plane(tmp_path)
    control_plane.register_identity(server_identity, locator=server_identity.locator, locator_version=1)
    return server_identity, client_identity, service, control_plane_thread, control_plane


def test_successful_handshake_and_data_exchange(tmp_path: Path) -> None:
    server_identity, client_identity, service, control_plane_thread, control_plane = build_fixture(tmp_path)
    server = InternetXServer(
        server_identity,
        control_plane=control_plane,
        port=udp_port(server_identity.locator),
        trace_path=tmp_path / "server.log",
    )
    thread = server.serve_in_thread()
    time.sleep(0.2)
    try:
        client = InternetXClient(
            client_identity,
            peer_name="server.test",
            control_plane=control_plane,
            trace_path=tmp_path / "client.log",
        )
        result = client.run("hello world", perform_locator_update=True)
        assert result["first_ack"]["status"] == "delivered"
        assert result["locator_update_ack"]["active_locator"].startswith("udp://127.0.0.1:")
        assert result["locator_update_ack"]["control_plane_locator"] == result["locator_update_ack"]["active_locator"]
        assert result["second_ack"]["status"] == "delivered"
        session = server.sessions[client.session_id]
        assert session.application_messages[0] == "hello world"
        assert session.application_messages[1].endswith("[post-migration]")
    finally:
        server.stop()
        thread.join(timeout=2)
        stop_control_plane(service, control_plane_thread)
