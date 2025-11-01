import socket
from PIL import ImageGrab
import glob
import os
import shutil
import subprocess
import protocol
from constants import *
import importlib
import sys
import threading

SCREENSHOT_PATH = 'C:\\test_folder\\server\\screen.jpg'
RECEIED_FILE_LOCATION = 'C:\\test_folder\\client'

READ_SIZE = 1024
FILE_P = 0
FOLDER = 1


class Methods(object):
    hist = {}
    lock = threading.Lock()

    @staticmethod
    def QUIT(my_socket, request, address):
        """close clnt"""
        return "QUIT"

    @staticmethod
    def EXIT(my_socket, request, address):
        """close clnt and server"""
        return "EXIT"

    @staticmethod
    def TAKE_SCREENSHOT(my_socket, params, address):
        """take screenshot"""
        im = ImageGrab.grab()
        im.save(SCREENSHOT_PATH)
        return "screenshot taken"

    @staticmethod
    def DIR(my_socket, params, address):
        """gets folder name and return to the clnt all the files in folder"""
        files_list = glob.glob(params[FILE_P] + "\\*.*")
        return str(files_list)

    @staticmethod
    def DELETE(my_socket, params, address):
        """gets name of file and delete the file"""
        os.remove(params[FILE_P])
        return 'file deleted'

    @staticmethod
    def COPY(my_socket, params, address):
        """gets name of folder and file and copies the file into the folder"""
        shutil.copy(params[FILE_P], params[FOLDER])
        return 'file copied'

    @staticmethod
    def EXECUTE(my_socket, params, address):
        """gets name of program and performs it on the server"""
        subprocess.call(params[FILE_P])
        return 'program executed'

    @staticmethod
    def receive_file(answer_file, my_socket):
        """gets file and socket and read from
        the socket and write into the file"""
        done = False
        with open(answer_file, "wb") as f:
            while not done:
                data = protocol.Protocol.recv_bin(my_socket)
                if data == EOF:
                    done = True
                else:
                    f.write(data)

    @staticmethod
    def receive_file_request(my_socket, request):
        """receive the request of SEND_FILE and create the name
        of the file and receive receive_file """
        splite1 = request.split("\\")
        answer_file = RECEIED_FILE_LOCATION + '\\' + splite1[-1]
        return Methods.receive_file(answer_file, my_socket)

    @staticmethod
    def SEND_FILE(my_socket, params, address):
        """gets socket and params and pulls out the name of
        the file from the params and calls to send_file"""
        Methods.send_file(params[FILE_P], my_socket)
        return 'file sent'

    @staticmethod
    def send_file(my_file, my_socket):
        """gets name of file and socket and sent the file on socket (1024)"""
        txt = ''
        file1 = open(my_file, 'rb')
        while txt != b'':
            txt = file1.read(READ_SIZE)
            protocol.Protocol.send_bin(my_socket, txt)
        protocol.Protocol.send_bin(my_socket, EOF)
        file1.close()
        return 'file sent'

    @staticmethod
    def RELOAD(my_socket, params, address):
        """receives a new version of procs.py in
        chunk saves it and reloads it"""
        Methods.receive_file("methods.py", my_socket)
        importlib.reload(sys.modules[__name__])
        return 'module reloaded'

    @staticmethod
    def new_hist(address):
        """ insert ne entry to dict """
        Methods.lock.acquire()
        Methods.hist[address] = []
        Methods.lock.release()

    @staticmethod
    def add_to_hist(address, request):
        """ add a request to dict"""
        Methods.lock.acquire()
        Methods.hist[address].append(request)
        Methods.lock.release()

    @staticmethod
    def HISTORY(params, sock, address):
        """return history for the given address"""
        Methods.lock.acquire()
        rsp = str(Methods.hist[address])
        Methods.lock.release()
        return rsp
