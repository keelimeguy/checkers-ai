import os
from ctypes import *

gameState32 = cdll.LoadLibrary(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libtest.so'))

gameState32.setup.argtypes = [c_uint, c_uint, c_uint, c_ushort]
gameState32.player.argtypes = [c_char_p]
gameState32.actions.argtypes = [c_char_p]
gameState32.result.argtypes = [c_char_p]
