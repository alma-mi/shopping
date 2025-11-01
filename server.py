"""
Shopping App Socket Server
Handles client connections and routes commands to appropriate methods
"""
import sys
import socket
import threading
import json
import methods
import protocol
from constants import IP, PORT


NUM_OF_LISTEN = 5
REQUEST_PLACE = 0
EXIT = 1


class ShoppingServer(object):
    def __init__(self, ip, port):
        """Initialize server socket"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(NUM_OF_LISTEN)
            print(f"Shopping Server started on {ip}:{port}")
        except socket.error as msg:
            print(f'Connection failure: {msg}\nTerminating program')
            sys.exit(EXIT)

    def handle_clients(self):
        """Accept and handle multiple client connections"""
        try:
            print("Waiting for clients...")
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Client connected from {address}")
                
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_single_client,
                    args=(client_socket, address)
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
        try:
            request = None
            while request != 'EXIT':
                # Receive and parse request
                request, params = self.receive_client_request(client_socket, address)
                
                if not request:
                    break
                
                print(f"[{address}] Command: {request} {params if params else ''}")
                
                # Handle request and get response
                response = self.handle_client_request(request, params, client_socket, address)
                
                # Send response
                self.send_response_to_client(response, client_socket)
                
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
    def receive_client_request(client_socket, address):
        """
        Receive request from client and parse command/parameters
        Returns: (command, params_list)
        """
        try:
            request = protocol.Protocol.recv(client_socket)
            
            if not request:
                return None, None
            
            request_str = request.decode().strip()
            
            if not request_str:
                return None, None
            
            # Split into command and parameters
            parts = request_str.split()
            
            if len(parts) > 1:
                return parts[0].upper(), parts[1:]
            else:
                return parts[0].upper(), None
                
        except socket.error as msg:
            print(f"Socket error receiving from {address}: {msg}")
            return None, None
        except Exception as msg:
            print(f"Error receiving from {address}: {msg}")
            return None, None

    @staticmethod
    def handle_client_request(request, params, client_socket, address):
        """
        Route request to appropriate method
        Returns: response string (JSON)
        """
        try:
            # Get the method from Methods class
            if hasattr(methods.Methods, request):
                method = getattr(methods.Methods, request)
                return method(client_socket, params, address)
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
    def send_response_to_client(response, client_socket):
        """Send response to client"""
        try:
            protocol.Protocol.send(client_socket, response)
        except socket.error as msg:
            print(f"Socket error sending response: {msg}")
        except Exception as msg:
            print(f"Error sending response: {msg}")


def main():
    server = ShoppingServer(IP, PORT)
    print("=" * 50)
    print("Shopping App Server")
    print("=" * 50)
    print("Available commands:")
    print("  - LOGIN username password")
    print("  - SEARCH_PRODUCT session_id query")
    print("  - LOGOUT session_id")
    print("  - EXIT")
    print("=" * 50)
    server.handle_clients()


if __name__ == '__main__':
    main()
