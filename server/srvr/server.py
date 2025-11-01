import sys

import methods
import protocol
import socket
from constants import *
import threading


IP = "0.0.0.0"
NUM_OF_LISTEN = 1
REQUEST_PLACE = 0
PARAMS = 1
EXIT = 1

"""def initiate_server_socket(ip, port):
    the function gets ip and port and create socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(NUM_OF_LISTEN)
        return server_socket
    except socket.error as msg:
        print("socket error12: ", msg)
    except Exception as msg:
        print("general error12: ", msg)"""


class Server(object):
    def __init__(self, ip, port):
        """the function gets ip and port and create socket"""
        try:
            self.server_socket = (socket.socket
                                  (socket.AF_INET, socket.SOCK_STREAM))
            self.server_socket.bind((ip, port))
            self.server_socket.listen(NUM_OF_LISTEN)
        except socket.error as msg:
            print('Connection failure: %s\n terminating program' % msg)
            sys.exit(EXIT)

    def handle_clients(self):
        """the function get the socket from the server and wait for client"""
        try:
            done = False
            while not done:
                # calls for the function handle_single_client
                # until the client disconnects
                client_socket, address = self.server_socket.accept()
                methods.Methods.new_hist(address)
                clnt_thread = \
                    threading.Thread(target=self.handle_single_client,
                                     args=(client_socket, address))
                clnt_thread.start()
        except socket.error as msg:
            print("socket error11: ", msg)
        except Exception as msg:
            print("general error11: ", msg)

    @staticmethod
    def handle_single_client(client_socket, address):
        """the function return true if the client send EXIT"""
        try:
            request = None
            while request != '' and request != 'EXIT' and request != 'exit':
                request, params = Server.receive_client_request(client_socket,
                                                                address)
                response = (Server.handle_client_request
                            (request, params, client_socket, address))
                Server.send_response_to_client(response, client_socket)
            client_socket.close()
            return request == 'EXIT'
        except socket.error as msg:
            print("socket error10: ", msg)
        except Exception as msg:
            print("general error10: ", msg)

    @staticmethod
    def receive_client_request(client_socket, address):
        """the function receive the request from the client
        and split the request and the params """
        try:
            request = protocol.Protocol.recv(client_socket)
            request = request.decode().upper()
            if request == '':
                return None
            req_and_prms = request.split()
            if len(req_and_prms) > PARAMS:
                return (req_and_prms[REQUEST_PLACE].upper(),
                        req_and_prms[PARAMS:])
            else:
                return req_and_prms[REQUEST_PLACE].upper(), None
        except socket.error as msg:
            print("socket error9: ", msg)
        except Exception as msg:
            print("general error9: ", msg)

    @staticmethod
    def handle_client_request(request, params, client_socket, address):
        """the function check what the request that the
        client send and activates the function by it"""
        try:
            methods.Methods.add_to_hist(address, request)
            cls = getattr(methods, "Methods")
            return getattr(cls, request)(client_socket, params, address)
        except Exception as msg:
            print("handle_client_request", msg)
            if request == 'SEND_FILE':
                Server.send_response_to_client(EOF.decode(), client_socket)
            return "illegal command"

    @staticmethod
    def send_response_to_client(response, client_socket):
        """the function send string to the client in binary array"""
        try:
            protocol.Protocol.send(client_socket, response)
        except socket.error as msg:
            print("socket error: ", msg)
        except Exception as msg:
            print("general error: ", msg)


def main():
    server = Server(IP, PORT)
    server.handle_clients()


if __name__ == '__main__':
    main()
