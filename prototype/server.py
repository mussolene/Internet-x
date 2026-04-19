import socket
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def start_udp_server(host='localhost', port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        logging.info(f'UDP server listening on {host}:{port}')

        while True:
            try:
                data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                message = data.decode('utf-8')
                logging.info(f'Received message: {message} from {addr}')
                
                if message == 'INIT':
                    response = 'INIT_ACK'
                    sock.sendto(response.encode('utf-8'), addr)
                    logging.info(f'Sent response: {response} to {addr}')

                elif message == 'KEM_EXCHANGE':
                    response = 'AUTH'
                    sock.sendto(response.encode('utf-8'), addr)
                    logging.info(f'Sent response: {response} to {addr}')

                elif message == 'DATA':
                    logging.info(f'Processing data from {addr}')

                else:
                    logging.warning(f'Unknown message type: {message} from {addr}')

            except Exception as e:
                logging.error(f'Error handling request: {e}')

if __name__ == '__main__':
    start_udp_server()