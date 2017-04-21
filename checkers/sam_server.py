from checkers.c.structs import samserver_lib
from ctypes import *

class SamServer:
    """Simple methods to communicate with server"""

    def __init__(self, opponent=0, is_B_client=False):
        self.is_B_client = is_B_client
        self.opponent = opponent
        self.connected = False
        self.player = None

    def __str__(self):
        return ("<SamServer: connected=" + str(self.connected)
                + ", is_B_client=" + str(self.is_B_client)
                + ", player=" + str(self.player)
                + ", opponent=" + str(self.opponent) + ">")

    def connect(self, verbose=False):
        self.disconnect()
        player = samserver_lib.setup(c_int(self.is_B_client), c_int(self.opponent), c_int(verbose))
        if player:
            self.player = "White"
        else:
            self.player = "Black"
        self.connected = True
        return player

    def disconnect(self):
        if self.connected:
            samserver_lib.end_connection()
            self.connected = False
            self.player = None

    def send_and_receive(self, msg=""):
        if self.connected:
            error = c_int(0)
            response = samserver_lib.send_move(msg.encode("utf-8"), byref(error))
            if response and not error:
                ptr = response
                string = cast(ptr, c_char_p).value.decode("utf-8")
                samserver_lib.free(ptr)
                return string
            elif response:
                return cast(response, c_char_p).value.decode("utf-8")
            else:
                return None
