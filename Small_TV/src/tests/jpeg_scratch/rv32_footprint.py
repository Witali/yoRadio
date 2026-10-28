"""Measure shared-scratch RV32 code/ABI/individual frames, without claiming runtime fit."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'jpeg_library_probe'))
from rv32_footprint import elf_sections


def sha(path):
    """Pin exact source and selected compiler bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Only relocatable objects are compiled; no firmware or SDK file is changed."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolchain-bin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    binaries = args.toolchain_bin.resolve()
    suffix = '.exe' if (binaries / 'riscv32-esp-elf-gcc.exe').exists() else ''
    gcc = binaries / ('riscv32-esp-elf-gcc' + suffix)
    nm = binaries / ('riscv32-esp-elf-nm' + suffix)
    specs = binaries.parent / 'riscv32-esp-elf/lib/picolibc.specs'
    source = PROJECT / 'storage/jpeg_scratch.c'
    paths = [source, PROJECT / 'storage/jpeg_scratch.h', PROJECT / 'storage/jpeg_nor.h',
             Path(__file__), HERE.parent / 'jpeg_library_probe/rv32_footprint.py', gcc, nm, specs]
    inputs = {str(p.resolve()): sha(p) for p in paths}
    flags = ['-march=rv32imc_zicsr_zifencei', '-mabi=ilp32', '-mtune=esp-base', '-Os',
             '-std=c11', '-Wall', '-Wextra', '-Werror', '-ffunction-sections', '-fdata-sections',
             '-fstack-usage', '-fno-jump-tables', '-fno-tree-switch-conversion',
             '-D__PICOLIBC_ERRNO_FUNCTION=__errno', '-specs=' + specs.as_posix(),
             '-I' + str(PROJECT / 'storage')]
    abi = output / 'abi.c'
    abi.write_text('#include "jpeg_scratch.h"\n'
                   'const unsigned char scratch_handle_bytes[sizeof(jpeg_scratch_t)]={0};\n'
                   'const unsigned char file_token_bytes[sizeof(jpeg_scratch_file_t)]={0};\n'
                   'const unsigned char file_region_bytes[sizeof(jpeg_scratch_region_t)]={0};\n',
                   encoding='utf-8', newline='\n')
    commands = []
    for name, path in [('jpeg_scratch', source), ('abi', abi)]:
        command = [str(gcc), *flags, '-c', str(path), '-o', str(output / (name + '.o'))]
        result = subprocess.run(command, capture_output=True, timeout=60)
        (output / (name + '.log')).write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
        commands.append(command)
    result = subprocess.run([str(nm), '--defined-only', '--print-size', str(output / 'abi.o')],
                            capture_output=True, check=True, timeout=30)
    (output / 'abi-symbols.txt').write_bytes(result.stdout)
    sizes = {line.split()[-1]: int(line.split()[1], 16) for line in result.stdout.decode().splitlines()}
    assert set(sizes) == {'scratch_handle_bytes', 'file_token_bytes', 'file_region_bytes'}, sizes
    frames = {}
    for line in (output / 'jpeg_scratch.su').read_text().splitlines():
        match = re.search(r':\d+:\d+:([^:]+)\t(\d+)\t(.+)$', line)
        assert match and match[3] == 'static', line
        frames[match[1]] = int(match[2])
    assert frames
    inputs_unchanged = all(sha(Path(p)) == h for p, h in inputs.items())
    assert inputs_unchanged
    report = dict(passed=True, runtime_tested=False, inputs_unchanged=inputs_unchanged,
                  inputs_sha256=inputs, commands=commands, sizes=elf_sections(output / 'jpeg_scratch.o'),
                  abi_bytes=sizes, single_frames=frames, max_single_frame=max(frames.values()),
                  object_sha256=sha(output / 'jpeg_scratch.o'), abi_object_sha256=sha(output / 'abi.o'),
                  scope='Standalone RV32IMC/ILP32 objects; no target execution, final UI link, complete call stack or whole-app RAM acceptance.')
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('RV32 scratch:', report['sizes']['code_bytes'], 'code bytes;', sizes,
          '; maximum individual frame', report['max_single_frame'])


if __name__ == '__main__':
    main()
