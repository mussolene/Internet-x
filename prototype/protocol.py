import json
import hashlib

# Packet Type Constants
PACKET_TYPE_HANDSHAKE = 'handshake'
PACKET_TYPE_DATA = 'data'
PACKET_TYPE_ACK = 'ack'

class Protocol:
    @staticmethod
    def encode(packet_type, data):
        """Encodes the packet into a JSON format."""
        packet = {
            'type': packet_type,
            'data': data
        }
        return json.dumps(packet)

    @staticmethod
    def decode(encoded_packet):
        """Decodes a JSON encoded packet back into its dictionary form."""
        return json.loads(encoded_packet)

    @staticmethod
    def compute_transcript_hash(data):
        """Computes a SHA256 hash of the given data to ensure validity of the handshake material."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def derive_flow_id(info):
        """Derives a unique flow ID from the provided info."""
        return hashlib.md5(info.encode('utf-8')).hexdigest()