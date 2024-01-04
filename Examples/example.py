import ctypes
# from PyHooking import PyHooking, load_external_shared_library, os_arch, os_bits
from PyHooking import *

print(f"PyHooking with `{os_arch}-{os_bits}`")



# Example with `mylib.print_message`

mylib = load_external_shared_library(f"Examples/mylib_{os_arch}_{os_bits}")

@PyHooking.CPrototype(ctypes.CFUNCTYPE(None, ctypes.c_char_p))
def hk_print_message(message):
    message = f"Invoked `hk_print_message('{message.decode('utf-8')}')`"
    PyHooking().invoke(mylib.print_message, message.encode())

# perform hooking

PyHooking().hook(mylib.print_message, hk_print_message)

mylib.print_message(b"This is a string from Python code")
mylib.c_invoke_print_message()

# perform unhooking

PyHooking().unhook(mylib.print_message)

mylib.print_message(b"This is a string from Python code")
mylib.c_invoke_print_message()

# result

'''
Invoked `hk_print_message('This is a string from Python code')`
Invoked `hk_print_message('This is a string from C code')`
This is a string from Python code
This is a string from C code
'''



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
