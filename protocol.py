"""
Protocol for socket communication
Handles sending and receiving messages with length prefixing
"""
import socket
import json
from constants import PROTOCOL_LENGTH_PREFIX, ZERO
import aes_cipher

MAX = PROTOCOL_LENGTH_PREFIX
DATA_SIZE = ZERO
KEY = 1
SOCK = 0


class Protocol(object):

    @staticmethod
    def send(conn, data):
        """Send string data over socket with length prefix"""
        encoded_msg = data.encode()
        if conn[KEY] is not None:
            encoded_msg = aes_cipher.AESCipher.encrypt(
                conn[KEY], encoded_msg)
        length = len(encoded_msg)
        length_str = str(length).zfill(MAX)
        length_bytes = length_str.encode()
        conn[SOCK].send(length_bytes + encoded_msg)

    @staticmethod
    def recv(conn):
        """Receive string data from socket using length prefix"""
        size = MAX
        tot_data = b''
        data = b' '

        # Read length prefix
        while size > DATA_SIZE and data != b'':
            data = conn[SOCK].recv(size)
            size -= len(data)
            tot_data += data
        if tot_data.isdigit():
            size = int(tot_data)
        else:
            print("illegal massage:", tot_data)
            if isinstance(tot_data, bytes):
                return tot_data.decode()
            return tot_data
        # Parse length

        tot_data = b''
        data = b' '
        # Read actual data
        while size > DATA_SIZE and data != b'':
            data = conn[SOCK].recv(size)
            size -= len(data)
            tot_data += data

        if conn[KEY] is not None:
            tot_data = aes_cipher.AESCipher.decrypt(conn[KEY], tot_data)

        # Ensure we return string
        if isinstance(tot_data, bytes):
            return tot_data.decode()
        return tot_data

    @staticmethod
    def send_bin(conn, data):
        """Send binary data over socket with length prefix"""
        if conn[KEY] is not None:
            data = aes_cipher.AESCipher.encrypt(conn[KEY], data)
        length = len(data)
        length_str = str(length).zfill(MAX)
        length_bytes = length_str.encode()
        conn[SOCK].send(length_bytes + data)

    @staticmethod
    def recv_bin(conn):
        """Receive binary data from socket using length prefix"""
        size1 = MAX
        tot_data = b''
        data = b' '

        # Read length prefix
        while size1 > DATA_SIZE and data != b'':
            data = conn[SOCK].recv(size1)
            size1 -= len(data)
            tot_data += data
        if tot_data.isdigit():
            size = int(tot_data)
        else:
            print("illegal massage:", tot_data)
            return tot_data
        # Parse length

        tot_data = b''
        data = b' '
        # Read actual data
        while size > DATA_SIZE and data != b'':
            data = conn[SOCK].recv(size)
            size -= len(data)
            tot_data += data

        if conn[KEY] is not None:
            tot_data = aes_cipher.AESCipher.decrypt(conn[KEY], tot_data)

        return tot_data
