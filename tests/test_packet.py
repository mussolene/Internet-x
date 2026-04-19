from refimpl.packet import INIT, build_packet, decode_packet, encode_packet, PacketError


def test_packet_round_trip() -> None:
    packet = build_packet(
        INIT,
        session_id="session-1",
        source_node_id="source",
        destination_node_id="dest",
        locator_hint="udp://127.0.0.1:9080",
        payload={"hello": "world"},
    )
    assert decode_packet(encode_packet(packet)) == packet


def test_packet_validation_rejects_missing_fields() -> None:
    try:
        decode_packet("{}")
    except PacketError as exc:
        assert "Missing packet fields" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("decode_packet should reject malformed packets")
