from __future__ import annotations
import ctypes, ctypes.util
from dataclasses import dataclass

from .os_spec import *

LIBC = "c" if is_posix() else "msvcrt"

if is_posix(): # posix memory protection
    PROT_NONE  = 0
    PROT_READ  = 1
    PROT_WRITE = 2
    PROT_EXEC  = 4
    # wrapper for posix
    PAGE_NOACCESS           = PROT_NONE
    PAGE_READONLY           = PROT_READ
    PAGE_READWRITE          = PROT_READ | PROT_WRITE
    PAGE_EXECUTE_READ       = PROT_EXEC | PROT_READ
    PAGE_EXECUTE_READWRITE  = PAGE_EXECUTE_READ | PROT_WRITE
else: # windows memory protection
    PAGE_NOACCESS           = 0x01
    PAGE_READONLY           = 0x02
    PAGE_READWRITE          = 0x04
    PAGE_EXECUTE            = 0x10
    PAGE_EXECUTE_READ       = 0x20
    PAGE_EXECUTE_READWRITE  = 0x40

@winnt
def mem_protect(ptr: ctypes.c_void_p, size: int, protection: int) -> int | None:
    '''
    Set memory protection of a region of memory
    '''
    kernel32 = ctypes.CDLL(ctypes.util.find_library("kernel32"))
    previous_protection = ctypes.c_long(0)
    ret = kernel32.VirtualProtect(ptr, size, protection, ctypes.byref(previous_protection))
    assert ret != 0, "set memory protection failed"
    return previous_protection.value

@posix
def mem_protect(ptr: ctypes.c_void_p, size: int, protection: int) -> int | None:
    '''
    Set memory protection of a region of memory
    '''
    PAGE_SIZE = 0x1000 # default page size
    try:
        from os import sysconf
        PAGE_SIZE = sysconf("SC_PAGE_SIZE")
    except: pass
    # align on a page boundary (in posix, we have to set whole page)
    addr = ptr.value
    mem_addr = addr & ~(PAGE_SIZE - 1)
    mem_end  = (addr + size) & ~(PAGE_SIZE - 1)
    if (addr + size) > mem_end: mem_end += PAGE_SIZE
    mem_len = mem_end - mem_addr
    ptr  = ctypes.c_void_p(mem_addr)
    size = mem_len
    # set protection to aligned page boundary
    libc = ctypes.CDLL(ctypes.util.find_library("c"))
    ret = libc.mprotect(ptr, size, protection)
    assert ret == 0, "set memory protection failed"
    return protection # TODO: return previous memory protection

@dataclass
class mem_t:
    addr: None
    size: None
    data: None
    def __bytes__(self) -> bytes: return bytes(self.data)
    def __len__(self) -> int: return self.size

def mem_allocate(size: int) -> mem_t:
    '''
    Allocate a data block
    '''
    c_mem_allocator = ctypes.c_uint8 * size
    mem = c_mem_allocator()
    ptr = ctypes.pointer(ctypes.c_void_p(ctypes.addressof(mem)))
    return mem_t(ptr, size, mem)

def mem_write(ptr: ctypes.c_void_p, data: str | bytes):
    '''
    Write a data block to a region of memory
    '''
    size = len(data)
    # change memory protection to writable
    previous_protection = mem_protect(ptr, size, PAGE_EXECUTE_READWRITE)
    # write data block
    libc = ctypes.CDLL(ctypes.util.find_library(LIBC))
    libc.memcpy(ptr, ctypes.create_string_buffer(data), size)
    # restore the previous memory protection
    mem_protect(ptr, size, previous_protection)

def mem_read(ptr: ctypes.c_void_p, size: int) -> bytes:
    '''
    Read a data block from a region of memory
    '''
    mem = mem_allocate(size)
    # change memory protection to readable
    previous_protection = mem_protect(ptr, size, PAGE_EXECUTE_READ)
    # read data block
    libc = ctypes.CDLL(ctypes.util.find_library(LIBC))
    libc.memcpy(mem.data, ptr, size)
    # restore the previous memory protection
    mem_protect(ptr, size, previous_protection)
    # return read data
    return bytes(mem)
