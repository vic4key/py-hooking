from __future__ import annotations
from dataclasses import dataclass
from struct import pack
import ctypes

from .os_spec import *
from .c_mem import *

# Capstone (archs & modes) `site-packages\capstone\__init__.py` - manual pre-defined here to avoid auto-import
if "CS_ARCH_ALL" not in globals().keys():
    # arch
    CS_ARCH_ARM        = 0
    CS_ARCH_ARM64      = 1
    CS_ARCH_MIPS       = 2
    CS_ARCH_X86        = 3
    CS_ARCH_ALL        = 0xFFFF
    # disasm mode
    CS_MODE_ARM = 0                # ARM mode
    CS_MODE_16 = (1 << 1)          # 16-bit mode (for X86)
    CS_MODE_32 = (1 << 2)          # 32-bit mode (for X86)
    CS_MODE_64 = (1 << 3)          # 64-bit mode (for X86, PPC)

__ARCH_TEMPLATE_LIST = {
    # FF 25 ?? ?? ?? ??         jmp dword ptr ds:[<pointer of address>]
    # ?? ?? ?? ??               <address>
    "i686_32":   ((CS_ARCH_X86, CS_MODE_32), (10, [0xFF, 0x25], lambda inst, fr, to: bytes(inst) + pack("L", fr + 6) + pack("L" , to))),
    "x86_64_32": ((CS_ARCH_X86, CS_MODE_32), (10, [0xFF, 0x25], lambda inst, fr, to: bytes(inst) + pack("L", fr + 6) + pack("L" , to))),
    # FF 25 00 00 00 00         jmp qword ptr [rip]
    # ?? ?? ?? ?? ?? ?? ?? ??   <address>
    "x86_64_64": ((CS_ARCH_X86, CS_MODE_64), (14, [0xFF, 0x25, 0x00, 0x00, 0x00, 0x00], None)),
    # 70 00 00 10               adr x16, #0xc
    # 10 02 40 F9               ldr x16, [x16]
    # 00 02 1F D6               br  x16
    # ?? ?? ?? ?? ?? ?? ?? ??   <address>
    "aarch64_64": ((CS_ARCH_ARM64, CS_MODE_ARM), (20, [0x70, 0x00, 0x00, 0x10, 0x10, 0x02, 0x40, 0xF9, 0x00, 0x02, 0x1F, 0xD6], None)),
}

arch_template = __ARCH_TEMPLATE_LIST.get(f"{os_arch}_{os_bits}", None)
assert not arch_template is None, "unsupported architecture"
# print(arch_template)

def default_generate_opcodes(inst, fr, to):
    return bytes(inst) + pack("Q" if os_bits == 64 else "L", to)

class PyHooking:
    '''
    Python Hooking
    '''

    @staticmethod
    def CPrototype(decorator):
        def wrapper(f):
            g = decorator(f)
            g.decorator = decorator
            return g
        return wrapper

    @dataclass
    class func_t:
        '''
        For hashing c-function pointer
        '''
        c_function = None
        def __init__(self, c_function): self.c_function = c_function
        def __hash__(self):
            pfn_c_function = ctypes.cast(ctypes.byref(self.c_function),  ctypes.POINTER(ctypes.c_void_p))
            return hash(pfn_c_function.contents.value)

    class rdr_t:
        '''
        For redirection instructions
        '''
        inst: bytes = bytes([])
        addr: bytes = bytes([])
        size: int   = 0
        func: None

        def __init__(self, fr: int = 0, to: int = 0):
            _, temp   = arch_template
            self.vafr = fr
            self.vato = to
            self.size = temp[0]
            self.inst = temp[1]
            self.func = temp[2]
        def __len__(self) -> int:
            return self.size
        def __bytes__(self) -> bytes:
            func = self.func if self.func else default_generate_opcodes
            return func(self.inst, self.vafr, self.vato)

    __instance = None
    __hooked_functions = {}

    def __new__(cls):
        if cls.__instance is None: cls.__instance = super().__new__(cls)
        return cls.__instance

    def __calculate_actual_instruction_sizes(self, bytes, needed_size, arch, mode) -> int:
        '''
        Calculate the actual size based on disassembled instructions
        '''
        from capstone import Cs
        result = 0
        cs = Cs(arch, mode)
        for i in cs.disasm(bytes, 0):
            result += i.size
            if result >= needed_size: break
        return result

    def hook(self, c_function, py_function):
        '''
        Hook a function
        '''
        pfn_c_function  = ctypes.cast(ctypes.byref(c_function),  ctypes.POINTER(ctypes.c_void_p)) # hold the actual address of `c_function`  in memory
        pfn_py_function = ctypes.cast(ctypes.byref(py_function), ctypes.POINTER(ctypes.c_void_p)) # hold the actual address of `py_function` in memory
        # print_hexlify(pfn_c_function.contents.value)
        # print_hexlify(pfn_py_function.contents.value)

        FREE_SIZE = 0x100  # reserve for backup instructions
        MAX_INST_SIZE = 0xF # we assume this is the instruction size of the longest instruction of all archs and all modes

        rdr_size = len(self.rdr_t())

        # allocate memory for trampoline
        trampoline = mem_allocate(rdr_size + FREE_SIZE)
        mem_protect(trampoline.addr.contents, len(trampoline), PAGE_EXECUTE_READWRITE)

        # create trampoline from the beginning of the function
        arch, _ = arch_template
        temp  = mem_read(pfn_c_function.contents, rdr_size + MAX_INST_SIZE)
        size  = self.__calculate_actual_instruction_sizes(temp, rdr_size, arch[0], arch[1]) # total size of backup instructions
        temp  = temp[0:size]
        temp += bytes(self.rdr_t(trampoline.addr.contents.value + len(temp), pfn_c_function.contents.value + len(temp)))
        mem_write(trampoline.addr.contents, temp)
        # print_hexlify(temp)

        # write redirection instruction to the beginning of the function
        temp = bytes(self.rdr_t(pfn_c_function.contents.value, pfn_py_function.contents.value))
        mem_write(pfn_c_function.contents, temp)
        # print_hexlify(temp)

        # store the hooked function to the list
        self.__hooked_functions[self.func_t(c_function)] = {
            "prototype": py_function.decorator,
            "trampoline" : trampoline,
        }

    def unhook(self, c_function):
        '''
        Unhook a hooked function
        '''
        e = self.__hooked_functions.get(self.func_t(c_function))
        assert e != None, "cannot unhook - the function was not hooked"

        rdr_size = len(self.rdr_t())

        # restore instructions in the beginning of the function
        pfn_c_function = ctypes.cast(ctypes.byref(c_function),  ctypes.POINTER(ctypes.c_void_p))
        temp = bytes(e["trampoline"])[0:rdr_size]
        mem_write(pfn_c_function.contents, temp)
        # print_hexlify(temp)

        # remove the hooked function to the list
        self.__hooked_functions.pop(self.func_t(c_function))

    def invoke(self, c_function, *args):
        '''
        Invoke the original function
        '''
        e = self.__hooked_functions.get(self.func_t(c_function))
        assert e != None, "cannot invoke - the function was not hooked"
        fn = e["prototype"](e["trampoline"].addr.contents.value)
        ret = fn(*args)
        if not ret is None: return ret
