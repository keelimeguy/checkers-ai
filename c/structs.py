from ctypes import cdll

md = cdll.LoadLibrary('libtest.so')

# import os
# import ctypes
# folder = os.path.dirname(os.path.abspath(__file__))
# dll_path = os.path.join(folder, "libtest.dll")

# kernel = ctypes.windll.kernel32
# kernel.SetDllDirectoryW(folder)
# md = ctypes.cdll.LoadLibrary(dll_path)
