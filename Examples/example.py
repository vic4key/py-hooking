import ctypes
from PyHooking import *

print(f"PyHooking with `{os_type}-{os_bits}:{os_name}-{os_arch}`")

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
