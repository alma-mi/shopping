"""
Protocol for socket communication
Handles sending and receiving messages with length prefixing
"""
import socket
import json

MAX = 4
DATA_SIZE = 0


class Protocol(object):

    @staticmethod
    def send(my_socket, data):
        """Send string data over socket with length prefix"""
        encoded_msg = data.encode()
        length = len(encoded_msg)
        length_str = str(length).zfill(MAX)
        length_bytes = length_str.encode()
        my_socket.send(length_bytes + encoded_msg)

    @staticmethod
    def recv(my_socket):
        """Receive string data from socket using length prefix"""
        size = MAX
        tot_data = b''

        # Read length prefix
        while size > DATA_SIZE:
            data = my_socket.recv(size)
            if not data:
                return b''
            size -= len(data)
            tot_data += data
        
        # Parse length
        size = int(tot_data.decode())
        tot_data = b''
        
        # Read actual data
        while size > DATA_SIZE:
            data = my_socket.recv(size)
            if not data:
                return b''
            size -= len(data)
            tot_data += data
        
        return tot_data
