from winreg import *
from constants import *


VALUES_COUNT = 2


class Registry(object):

    @staticmethod
    def read_reg():
        ip = IP
        port = PORT
        """open registry keyVALUES_COUNT = 2"""
        RawKey = OpenKey(HKEY_LOCAL_MACHINE, r"SOFTWARE\\TechnicianServer")
        for i in range(VALUES_COUNT):
            try:
                name, value, type = EnumValue(RawKey, i)
                if name == "IP":
                    ip = value
                if name == "PORT":
                    port = value
                print(i, name, value, type)
            except EnvironmentError:
                print("You have ", i, " values")
                break
        CloseKey(RawKey)
        return ip, port
