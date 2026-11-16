"""""" # start delvewheel patch
def _delvewheel_patch_1_13_0():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'dolphin_memory_engine.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-dolphin_memory_engine-1.3.2.dev37')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-dolphin_memory_engine-1.3.2.dev37')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_13_0()
del _delvewheel_patch_1_13_0
# end delvewheel patch

from ._dolphin_memory_engine import (
    MemWatch,
    assert_hooked,
    follow_pointers,
    get_status,
    hook,
    is_hooked,
    read_byte,
    read_bytes,
    read_double,
    read_float,
    read_word,
    un_hook,
    write_byte,
    write_bytes,
    write_double,
    write_float,
    write_word,
)

__all__ = [
    "MemWatch",
    "assert_hooked",
    "follow_pointers",
    "hook",
    "un_hook",
    "is_hooked",
    "get_status",
    "read_byte",
    "read_bytes",
    "read_double",
    "read_float",
    "read_word",
    "write_byte",
    "write_bytes",
    "write_double",
    "write_float",
    "write_word",
]
