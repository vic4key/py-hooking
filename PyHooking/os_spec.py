import os, sys
from struct import calcsize
from platform import system, machine

'''
os_bits = [32, 64]
'''
os_bits = calcsize("P") * 8

'''
os_arch = [i686, x86_64, aarch64]
'''
os_arch = machine().lower()
if os_arch == "amd64": os_arch = "x86_64"
if os_arch.find("iphone") != -1: os_arch = "aarch64"

'''
os_type = [windows, linux, darwin]
'''
os_type = system().lower()

'''
os_name = [windows, linux, android, macos, ios]
'''
os_name = os_type
if os_name == "linux":  os_name = "android" if os_arch == "aarch64" else os_name
if os_name == "darwin": os_name = "ios" if os_arch == "aarch64" else "macos"

__list_winnt = ["windows"]
__list_posix = ["linux", "darwin"]

def is_winnt(): return os_type in ["windows"]
def is_posix(): return os_type in ["linux", "darwin"]

def __ifdef_decorator_impl(platforms, func, frame):
    if os_type in platforms:
        return func
    elif func.__name__ in frame.f_locals:
        return frame.f_locals[func.__name__]
    else:
        def _not_implemented(*args, **kwargs):
            raise NotImplementedError(
                f"Function `{func.__name__}` is not defined for `{os_type}` platform.")
        return _not_implemented

def winnt(func):
    return __ifdef_decorator_impl(__list_winnt, func, sys._getframe().f_back)

def posix(func):
    return __ifdef_decorator_impl(__list_posix, func, sys._getframe().f_back)

def load_external_shared_library(file):
    '''
    Load an external shared library (Eg. "file_name", "file_name.ext", "path/to/file_name.ext")
    '''
    OS_TYPE_SHARED_EXTENSIONS = { "windows": ".dll", "linux": ".so", "darwin": ".dylib" }
    from ctypes import CDLL
    try: result = CDLL(file)
    except:
        file_name = file
        l = os.path.splitext(file_name)
        assert len(l) > 0, "invalid input file"
        if l[-1] == "":
            file_ext   = OS_TYPE_SHARED_EXTENSIONS.get(os_type)
            file_name += file_ext
        try: result = CDLL(file_name)
        except:
            file_dir  = os.getcwd()
            file_path = os.path.join(file_dir, file_name)
            result = CDLL(file_path)
    return result

def print_hexlify(data):
    import binascii
    if type(data) is bytes: print(binascii.hexlify(data))
    elif type(data) is str: print(binascii.hexlify(data.encode()))
    elif type(data) is int: print("0x%016X" % data)
    else: assert False, "unknown data"
