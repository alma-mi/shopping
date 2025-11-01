"""
alma miller
client
"""
import socket
import sys
from Registry import *
import protocol
from constants import *
import methods


IP = "127.0.0.1"
MIN_LEN = 1
PARAMS_ONE = 2
PARAMS_TWO = 3
REQUEST_PLACE = 0
EXIT = 1


"""def initate_client_socket(ip, port):
    the function gets ip and port and create socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((ip, port))
    return my_socket"""


class Client(object):
    def __init__(self, ip, port):
        try:
            """the function gets ip and port and create socket"""
            self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.my_socket.connect((Registry.read_reg()))
        except socket.error as msg:
            print('Connection failure: %s\n terminating program' % msg)
            sys.exit(EXIT)

    def handle_user_input(self):
        """the function gets request and print it in bytes"""
        try:
            request = None
            while request != 'EXIT' and request != 'QUIT':
                request = input("please enter a request ")
                request = request.upper()

                if self.valid_request(request):
                    self.send_request_to_server(request)
                    self.handle_server_response(request)
                else:
                    print("illegal request")
            self.my_socket.close()
        except socket.error as msg:
            print("socket error5: ", msg)
        except Exception as msg:
            print("general error5: ", msg)

    @staticmethod
    def valid_request(request):
        """check if the request is legal"""
        split1 = request.split()
        if split1[REQUEST_PLACE].upper() == 'EXIT' and len(split1) == MIN_LEN:
            return request
        elif (split1[REQUEST_PLACE].upper() ==
              'QUIT' and len(split1) == MIN_LEN):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'TAKE_SCREENSHOT' and
              len(split1) == MIN_LEN):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'DIR' and
              len(split1) == PARAMS_ONE):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'EXECUTE' and
              len(split1) == PARAMS_ONE):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'DELETE' and
              len(split1) == PARAMS_ONE):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'COPY' and
              len(split1) == PARAMS_TWO):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'RELOAD' and
              len(split1) == MIN_LEN):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'SEND_FILE' and
              len(split1) == PARAMS_ONE):
            return request
        elif (split1[REQUEST_PLACE].upper() == 'HISTORY' and
              len(split1) == MIN_LEN):
            return True
        return False

    def send_request_to_server(self, request):
        """function that sent the request to the server"""
        protocol.Protocol.send(self.my_socket, request)
        # if the request is reload then send this to server
        if request == 'RELOAD':
            methods.Methods.send_file('methods.py', self.my_socket)

    def handle_server_response(self, request):
        """function that gets the """
        req_prms = request.split()
        if req_prms[REQUEST_PLACE] == 'SEND_FILE':
            methods.Methods.receive_file_request(self.my_socket, request)
        data = protocol.Protocol.recv(self.my_socket)
        return data.decode()

    def send_command(self, request):
        try:
            rsp = ""
            if self.valid_request(request):
                self.send_request_to_server(request)
                rsp = self.handle_server_response(request)
            return rsp
        except socket.error as msg:
            print("send_command: the server has been closed", msg)
            return "server is down"
        except Exception as msg:
            print("server is down", msg)


def main():
    client = Client(IP, PORT)
    client.handle_user_input()


if __name__ == '__main__':
    main()
