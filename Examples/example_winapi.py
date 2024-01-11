import ctypes
from PyHooking import *

print(f"PyHooking with `{os_type}-{os_bits}:{os_name}-{os_arch}`")

# Example with `user32.MessageBoxA`

user32 = ctypes.CDLL(ctypes.util.find_library("user32"))

@PyHooking.CPrototype(ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong))
def hk_MessageBoxA(hWnd, lpText, lpCaption, uType):
    lpText = f"Invoked `hk_MessageBoxA({hWnd}, '{lpText.decode('utf-8')}', '{lpCaption.decode('utf-8')}', {uType})`"
    return PyHooking().invoke(user32.MessageBoxA, hWnd, lpText.encode(), lpCaption, uType)

# perform hooking

PyHooking().hook(user32.MessageBoxA, hk_MessageBoxA)

user32.MessageBoxA(0, b"text 1", b"", 0)

# perform unhooking

PyHooking().unhook(user32.MessageBoxA)

user32.MessageBoxA(0, b"text 2", b"", 0)

# result

'''
Invoked `hk_MessageBoxA(None, 'text 1', '', 0)`
<empty>
'''
