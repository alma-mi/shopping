"""
Shopping App Socket Server
Handles client connections and routes commands to appropriate methods
"""
import sys
import socket
import threading
import json
import methods
from db import create_tables
import protocol
from constants import PORT, MAX_LISTEN_BACKLOG, ONE, ZERO
import key_exchange

IP = "0.0.0.0"
NUM_OF_LISTEN = MAX_LISTEN_BACKLOG
REQUEST_PLACE = 0
EXIT_CODE = PHARAMS_FIRST = 0
PHARAMS_SECOND = 1
MAX = ONE


class ShoppingServer(object):
    def __init__(self, ip, port):
        """Initialize server socket"""
        try:
            self.server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self.server_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )
            self.server_socket.bind((ip, port))
            self.server_socket.listen(NUM_OF_LISTEN)
            msg = f"Shopping Server started on {ip}:{port}"
            print(msg)
        except socket.error as msg:
            err = f'Connection failure: {msg}\nTerminating program'
            print(err)
            sys.exit(EXIT_CODE)

    def handle_clients(self):
        """Accept and handle multiple client connections"""
        try:
            print("Waiting for clients...")
            while True:
                conn, address = self.server_socket.accept()
                print(f"Client connected from {address}")

                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_single_client,
                    args=(conn, address)
                )
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\nServer shutting down...")
            self.server_socket.close()
        except socket.error as msg:
            print(f"Socket error: {msg}")
        except Exception as msg:
            print(f"General error: {msg}")

    def handle_single_client(self, client_socket, address):
        """Handle a single client connection"""
        key = key_exchange.KeyExchange.recv_send_key((client_socket, None))
        conn = (client_socket, key)
        try:
            request = None
            while request != 'EXIT':
                # Receive and parse request
                request, params = self.receive_client_request(
                    conn, address)

                if not request:
                    break

                print(
                    f"[{address}] Command: {request} "
                    f"{params if params else ''}"
                )

                # Handle request and get response
                response = self.handle_client_request(
                    request, params, conn, address)

                # Send response
                self.send_response_to_client(response, conn)

                if request == 'EXIT':
                    break

        except socket.error as msg:
            print(f"Socket error with {address}: {msg}")
        except Exception as msg:
            print(f"Error handling client {address}: {msg}")
        finally:
            print(f"Client {address} disconnected")
            client_socket.close()

    @staticmethod
    def receive_client_request(conn, address):
        """
        Receive request from client and parse command/parameters
        Returns: (command, params_list)
        """
        try:
            request = protocol.Protocol.recv(conn)

            if not request:
                return None, None

            request_str = request.strip()

            if not request_str:
                return None, None

            # Split into command and parameters
            parts = request_str.split()

            if len(parts) > MAX:
                return parts[PHARAMS_FIRST].upper(), parts[PHARAMS_SECOND:]
            else:
                return parts[PHARAMS_FIRST].upper(), None

        except socket.error as msg:
            print(f"Socket error receiving from {address}: {msg}")
            return None, None
        except Exception as msg:
            print(f"Error receiving from {address}: {msg}")
            return None, None

    @staticmethod
    def handle_client_request(request, params, conn, address):
        """
        Route request to appropriate method
        Returns: response string (JSON)
        """
        try:
            # Get the method from Methods class
            if hasattr(methods.Methods, request):
                method = getattr(methods.Methods, request)
                return method(conn, params, address)
            else:
                return json.dumps({
                    "status": "error",
                    "message": f"Unknown command: {request}"
                })
        except Exception as msg:
            print(f"Error handling request {request}: {msg}")
            return json.dumps({
                "status": "error",
                "message": f"Server error: {str(msg)}"
            })

    @staticmethod
    def send_response_to_client(response, conn):
        """Send response to client"""
        try:
            protocol.Protocol.send(conn, response)
        except socket.error as msg:
            print(f"Socket error sending response: {msg}")
        except Exception as msg:
            print(f"Error sending response: {msg}")


def main():
    # Ensure database tables exist before accepting clients
    try:
        create_tables()
    except Exception:
        pass

    server = ShoppingServer("0.0.0.0", PORT)
    server.handle_clients()


if __name__ == '__main__':
    main()
