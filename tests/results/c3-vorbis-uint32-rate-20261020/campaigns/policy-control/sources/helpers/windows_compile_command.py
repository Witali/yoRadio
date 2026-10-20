"""Prepare a GCC macro dump from a real C3 Windows compilation-database row."""
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


def generated_cflags_inputs(argv, cwd):
    """Validate the one observed generated cflags file without expanding it."""
    response = [arg for arg in argv if arg.startswith('@')]
    if not response: raise ValueError('Expected the pinned C3 build/toolchain/cflags response')
    cflags, specs = (cwd/'toolchain/cflags').resolve(), (cwd/'specs/picolibc.specs').resolve()
    if (len(response) != 1 or (cwd/response[0][1:]).resolve() != cflags or
        not cflags.is_relative_to(cwd) or not specs.is_relative_to(cwd)):
        raise ValueError('Only this build/toolchain/cflags response is supported')
    data = cflags.read_bytes()
    expected = ['-march=rv32imc_zicsr_zifencei', '-mtune=esp-base',
                '"-specs='+specs.as_posix()+'"', '-D__PICOLIBC_ERRNO_FUNCTION=__errno']
    if data.decode('utf-8').splitlines() != expected:
        raise ValueError('Generated cflags content differs from the four reviewed RV32 lines')
    specs_data = specs.read_bytes()
    if not specs_data: raise ValueError('Generated picolibc.specs is empty')
    return {cflags:data, specs:specs_data}


def check_macro_inputs(inputs):
    """Require both captured generated inputs to remain byte-identical."""
    for path,data in inputs.items():
        if path.read_bytes() != data:
            raise ValueError('Generated macro input changed: '+str(path))


def macro_command(row, compiler, source):
    """Return argv,cwd,original-argv,generated-input-bytes; never execute/write.

    Preserve the original @cflags argument for GCC. Only its reviewed generated
    path/four-line RV32 content is supported; arbitrary/nested responses are rejected.
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
    generated = generated_cflags_inputs(raw,cwd)
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
    if sum(locate(arg) == Path(source).resolve() for arg in output[1:] if not arg.startswith(('-', '@'))) != 1:
        raise ValueError('Expected exactly one unchanged source operand')
    return output + ['-E', '-dM'], cwd, list(raw), generated
