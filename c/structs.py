import os
from ctypes import *

gameState32 = cdll.LoadLibrary(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libtest.so'))

printf = gameState32.printf

class BOARD(Structure):
    _fields_ = [("b", c_uint),
            ("w", c_uint),
            ("k", c_uint),
            ("plyr", c_ushort)]

class MOVE(Structure):
    _fields_ = [("route", POINTER(c_ushort)),
            ("length", c_int)]

gameState32.actions.restype = POINTER(POINTER(POINTER(c_ushort)))
