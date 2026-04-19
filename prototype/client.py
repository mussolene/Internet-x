import socket
import time
import struct

class UDPClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_init(self):
        message = b'INIT'
        self.sock.sendto(message, (self.server_address, self.server_port))
        print(f'[SEND] {message.decode()}')
        self.process_init_ack()

    def process_init_ack(self):
        try:
            data, _ = self.sock.recvfrom(4096)
            print(f'[RECEIVE] {data.decode()}')
            if data == b'INIT_ACK':
                self.send_kem_exchange()
            else:
                print('[ERROR] Unexpected message received: {data.decode()}')
        except socket.error as e:
            print(f'[ERROR] Socket error: {e}')

    def send_kem_exchange(self):
        message = b'KEM_EXCHANGE'
        self.sock.sendto(message, (self.server_address, self.server_port))
        print(f'[SEND] {message.decode()}')
        self.process_auth()

    def process_auth(self):
        try:
            data, _ = self.sock.recvfrom(4096)
            print(f'[RECEIVE] {data.decode()}')
            if data == b'AUTH':
                self.send_data()
            else:
                print('[ERROR] Unexpected message received: {data.decode()}')
        except socket.error as e:
            print(f'[ERROR] Socket error: {e}')

    def send_data(self):
        message = b'DATA'
        self.sock.sendto(message, (self.server_address, self.server_port))
        print(f'[SEND] {message.decode()}')
        self.receive_data()

    def receive_data(self):
        try:
            data, _ = self.sock.recvfrom(4096)
            print(f'[RECEIVE] {data.decode()}')
        except socket.error as e:
            print(f'[ERROR] Socket error: {e}')

if __name__ == '__main__':
    client = UDPClient('localhost', 9999)  # Replace with actual server address and port
    client.send_init()