from ctypes import cdll
import os
md = cdll.LoadLibrary(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libtest.so'))

# import os
# import ctypes
# folder = os.path.dirname(os.path.abspath(__file__))
# dll_path = os.path.join(folder, "libtest.dll")

# kernel = ctypes.windll.kernel32
# kernel.SetDllDirectoryW(folder)
# md = ctypes.cdll.LoadLibrary(dll_path)
