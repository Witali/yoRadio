"""Prepare a GCC macro dump from a real Windows compilation-database row."""
import ctypes
from pathlib import Path


def windows_argv(command):
    """Use Windows quoting rules; shlex(posix=False) breaks joined -I\"path\"."""
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    shell.CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
    shell.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    count = ctypes.c_int()
    parsed = shell.CommandLineToArgvW(command, ctypes.byref(count))
    if not parsed:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return [parsed[i] for i in range(count.value)]
    finally:
        kernel.LocalFree(ctypes.cast(parsed, ctypes.c_void_p))


def macro_command(row, compiler, source):
    """Return argv,cwd,original-argv; never execute or write files.

    The pinned CYD compile row is direct GCC with no response files. Reject
    different contexts for explicit review instead of changing their meaning.
    """
    cwd = Path(row['directory']).resolve()
    locate = lambda value: (cwd / value).resolve()
    if locate(row['file']) != Path(source).resolve():
        raise ValueError('Wrong compilation row source')
    raw = row.get('arguments')
    if raw is None: raw = windows_argv(row['command'])
    if not raw or any(not isinstance(x, str) for x in raw):
        raise ValueError('Invalid compilation argv')
    if locate(raw[0]) != Path(compiler).resolve():
        raise ValueError('Expected the actual direct compiler, without a shell/launcher')
    if any(arg.startswith('@') for arg in raw):
        raise ValueError('Response-file compile context requires explicit review')
    if raw.count('-c') != 1 or raw.count('-o') != 1:
        raise ValueError('Expected exactly one -c and -o operand in an ordinary compile row')
    argv = list(raw)
    output, i = [argv[0]], 1
    while i < len(argv):
        arg = argv[i]
        if arg == '-c':
            i += 1
        elif arg == '-o':
            if i + 1 >= len(argv): raise ValueError('Missing output option argument')
            i += 2
        elif (arg.startswith(('-o', '--output', '-save-temps', '-MF', '-MT', '-MQ')) or
              arg in ('-E', '-S', '-M', '-MM', '-MD', '-MMD', '-MP', '-MG') or arg.startswith('-Wp,')):
            raise ValueError('Unrecognized output/preprocessor context requires explicit review')
        else:
            output.append(arg); i += 1
    if sum(locate(arg) == Path(source).resolve() for arg in output[1:] if not arg.startswith('-')) != 1:
        raise ValueError('Expected exactly one unchanged source operand')
    return output + ['-E', '-dM'], cwd, list(raw)
