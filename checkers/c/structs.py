import os
from ctypes import *

state32_lib = cdll.LoadLibrary(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libcheckers32.so'))

samserver_lib = cdll.LoadLibrary(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libmysockets.so'))

printf = state32_lib.printf

class BOARD(Structure):
    _fields_ = [("b", c_uint),
            ("w", c_uint),
            ("k", c_uint),
            ("plyr", c_ushort)]

class MOVE(Structure):
    _fields_ = [("route", POINTER(c_ushort)),
            ("length", c_int)]

state32_lib.actions.restype = POINTER(POINTER(MOVE))
state32_lib.result.restype = POINTER(BOARD)
state32_lib.Board_alloc.restype = POINTER(BOARD)
state32_lib.Move_alloc.restype = POINTER(MOVE)
state32_lib.Move_copy.restype = POINTER(MOVE)
state32_lib.Board_from_string.restype = POINTER(BOARD)
state32_lib.Move_from_string.restype = POINTER(MOVE)
state32_lib.Board_to_string.restype = c_void_p
state32_lib.Move_to_string.restype = c_void_p
state32_lib.player.restype = c_void_p

samserver_lib.send_move.restype = c_void_p
