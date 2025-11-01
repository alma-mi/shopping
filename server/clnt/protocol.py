import socket

IP = "0.0.0.0"
MAX = 4
DATA_SIZE = 0


class Protocol(object):

    @staticmethod
    def send(my_socket, data):
        """the function gets socket and data and sent the data"""
        encoded_msg = data.encode()
        l1 = len(encoded_msg)
        l2 = str(l1)
        l3 = l2.zfill(MAX)
        l4 = l3.encode()
        l5 = l4 + encoded_msg
        my_socket.send(l5)

    @staticmethod
    def recv(my_socket):
        """the function get socket and read from the socket"""
        size = MAX
        tot_data = b''

        while size > DATA_SIZE:
            data = my_socket.recv(size)
            size -= len(data)
            tot_data += data
        size = int(tot_data.decode())
        tot_data = b''
        while size > DATA_SIZE:
            data = my_socket.recv(size)
            size -= len(data)
            tot_data += data
        return tot_data

    @staticmethod
    def send_bin(my_socket, data):
        """the function gets socket and data and sent the data"""
        l1 = len(data)
        l2 = str(l1)
        l3 = l2.zfill(MAX)
        l4 = l3.encode()

        my_socket.send(l4 + data)

    @staticmethod
    def recv_bin(my_socket):
        """the function get socket and read from the socket"""
        size = MAX
        tot_data = b''

        while size > DATA_SIZE:
            data = my_socket.recv(size)
            size -= len(data)
            tot_data += data
        size = int(tot_data.decode())
        tot_data = b''
        while size > DATA_SIZE:
            data = my_socket.recv(size)
            size -= len(data)
            tot_data += data
        return tot_data
