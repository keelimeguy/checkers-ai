from ctypes import cdll
import os
md = cdll.LoadLibrary(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libtest.so'))
