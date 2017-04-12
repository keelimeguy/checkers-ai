import os
from ctypes import *

state32 = cdll.LoadLibrary(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libtest.so'))

printf = state32.printf

class BOARD(Structure):
    _fields_ = [("b", c_uint),
            ("w", c_uint),
            ("k", c_uint),
            ("plyr", c_ushort)]

class MOVE(Structure):
    _fields_ = [("route", POINTER(c_ushort)),
            ("length", c_int)]

state32.actions.restype = POINTER(POINTER(MOVE))
state32.Board_alloc.restype = POINTER(BOARD)
state32.Move_alloc.restype = POINTER(MOVE)
state32.Board_from_string.restype = POINTER(BOARD)
state32.Board_to_string.restype = c_char_p
state32.Move_to_string.restype = c_char_p
state32.player.restype = c_char_p
