import os, sys
from struct import calcsize
from platform import system, machine

arch  = machine().lower()
bits  = calcsize("P") * 8 # 32/64

WINNT = system() in ["Windows"]
POSIX = system() in ["Linux", "Darwin"]
PLATFORM_SHARED_EXTENSION = { "Windows": ".dll", "Linux": ".so", "Darwin": ".dylib" }

def _ifdef_decorator_impl(platforms, func, frame):
    if system() in platforms:
        return func
    elif func.__name__ in frame.f_locals:
        return frame.f_locals[func.__name__]
    else:
        def _not_implemented(*args, **kwargs):
            raise NotImplementedError(
                f"Function `{func.__name__}` is not defined for `{system()}` platform.")
        return _not_implemented

def winnt(func):
    return _ifdef_decorator_impl(["Windows"], func, sys._getframe().f_back)

def posix(func):
    return _ifdef_decorator_impl(["Linux", "Darwin"], func, sys._getframe().f_back)

def load_external_shared_library(file):
    '''
    Load an external shared library (Eg. "file_name", "file_name.ext", "path/to/file_name.ext")
    '''
    from ctypes import CDLL
    try: result = CDLL(file)
    except:
        file_name = file
        l = os.path.splitext(file_name)
        assert len(l) > 0, "invalid input file"
        if l[-1] == "":
            file_ext   = PLATFORM_SHARED_EXTENSION.get(system())
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
