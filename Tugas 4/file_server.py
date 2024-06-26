import socket
import threading
import logging
import signal
import sys

from file_protocol import FileProtocol
fp = FileProtocol()

shutdown_event = threading.Event()

class ClientHandler(threading.Thread):
    def __init__(self, connection, address):
        super().__init__()
        self.connection = connection
        self.address = address

    def run(self):
        received_data = ""
        try:
            while not shutdown_event.is_set():
                data = self.connection.recv(1024)
                if data:
                    received_data += data.decode()
                    if "\r\n\r\n" in received_data:
                        break
                else:
                    break
            if received_data:
                logging.warning(f"Complete data received: {received_data}")
                response = fp.process_string(received_data.strip())
                response += "\r\n\r\n"
                self.connection.sendall(response.encode())
        except Exception as e:
            logging.warning(f"Error: {e}")
        finally:
            self.connection.close()

class TCPServer(threading.Thread):
    def __init__(self, ip_address, port):
        super().__init__()
        self.server_address = (ip_address, port)
        self.client_threads = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.active = True

    def run(self):
        logging.warning(f"Server running at {self.server_address}")
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(1)
        while self.active and not shutdown_event.is_set():
            try:
                self.server_socket.settimeout(1.0)
                connection, client_address = self.server_socket.accept()
                logging.warning(f"Connection from {client_address}")

                client_thread = ClientHandler(connection, client_address)
                client_thread.start()
                self.client_threads.append(client_thread)
            except socket.timeout:
                continue
            except socket.error:
                if not self.active:
                    break

    def shutdown(self):
        logging.warning("Shutting down server...")
        self.active = False
        shutdown_event.set()
        self.server_socket.close()
        for client_thread in self.client_threads:
            client_thread.join()
        logging.warning("Server has been shut down.")

def signal_handler(signal, frame):
    logging.warning("Signal received, shutting down server...")
    server.shutdown()
    sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    server = TCPServer(ip_address='0.0.0.0', port=3000)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    server.start()
