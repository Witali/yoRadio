"""Compile an unchanged SDK5.5.4 NVS object for factory analysis, separately from production."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

SDK_REVISION = '735507283d5b2f9fb363a1901172dbd9e847945d'
INCLUDES = ('nvs_flash/include', 'nvs_flash/private_include', 'esp_common/include',
            'heap/include', 'spi_flash/include', 'esp_rom/include',
            'esp_partition/include', 'newlib/platform_include')


def sha(data):
    """Pin actual dependency bytes, including the compiler and its private headers."""
    return hashlib.sha256(data).hexdigest()


def run(args, directory):
    """Use argument arrays without a shell and retain compiler diagnostics on failure."""
    result = subprocess.run([str(a) for a in args], cwd=directory, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace'))
    return result.stdout.decode(errors='replace')


def dependencies(path):
    """Read GCC Make dependencies, preserving escaped spaces and Windows drive colons."""
    text = path.read_text().replace('\\\n', ' ')
    _, separator, body = text.partition(': ')
    if not separator: raise ValueError('Missing dependency rule')
    # GCC uses forward slashes for dependency paths; only spaces/backslashes need unescaping.
    return [Path(re.sub(r'\\([ \\])', r'\1', item)).resolve()
            for item in re.findall(r'(?:\\[ \\]|[^\s])+', body)]


def build(sdk, compiler, config, output):
    """Create only analysis objects and a DWARF relocation carrier; never an ESP flash image."""
    if output.exists(): raise ValueError('Preserve existing fixture output')
    if run(['git', '-C', sdk, 'rev-parse', 'HEAD'], sdk).strip() != SDK_REVISION or \
            run(['git', '-C', sdk, 'status', '--porcelain'], sdk).strip():
        raise ValueError('Require the clean pinned SDK5.5.4 checkout')
    version = run([compiler, '--version'], sdk)
    if '14.2.0_20260121' not in version: raise ValueError('Require the qualified GCC14 toolchain')
    profile = config.read_bytes()
    if b'#define CONFIG_LIBC_NEWLIB 1' not in profile or b'#define CONFIG_LIBC_PICOLIBC 1' in profile:
        raise ValueError('Analysis fixture must consistently select Newlib')
    output.mkdir(parents=True); (output/'config').mkdir()
    (output/'config/sdkconfig.h').write_bytes(profile)
    args = [compiler, '-DESP_PLATFORM', '-DIDF_VER="v5.5.4"', '-D_GNU_SOURCE',
            '-D_GLIBCXX_USE_POSIX_SEMAPHORE', '-D_GLIBCXX_HAVE_POSIX_SEMAPHORE',
            '-D_POSIX_READER_WRITER_LOCKS', '-D__STDC_WANT_LIB_EXT1__=0',
            '-march=rv32imc_zicsr_zifencei', '-mabi=ilp32', '-fno-rtti', '-ffunction-sections',
            '-fdata-sections', '-gdwarf-4', '-ggdb', '-Og', '-fno-shrink-wrap',
            '-freorder-blocks', '-fstrict-volatile-bitfields', '-fno-jump-tables',
            '-fno-tree-switch-conversion', '-std=gnu++23', '-fno-exceptions', '-fuse-cxa-atexit',
            '-I'+str(output/'config')]
    args += ['-I'+str(sdk/'components'/name) for name in INCLUDES]
    args += ['-fdebug-prefix-map='+str(sdk)+'=/IDF', '-fdebug-prefix-map='+str(output)+'=/fixture',
             '-fdebug-prefix-map='+str(compiler.parent.parent)+'=/toolchain',
             '-fmacro-prefix-map='+str(sdk)+'=/IDF', '-MD', '-MF', 'nvs_page.d',
             '-c', sdk/'components/nvs_flash/src/nvs_page.cpp', '-o', 'nvs_page.cpp.o']
    run(args, output)
    linker = compiler.with_name('riscv32-esp-elf-ld'+compiler.suffix)
    link_args = [linker, '--unresolved-symbols=ignore-all', '-Ttext=0x42000000',
                 '-e', '_ZN3nvs4Page4loadEPNS_9PartitionEm', '-o', 'layout.elf', 'nvs_page.cpp.o']
    run(link_args, output)
    roots = {'sdk': sdk, 'toolchain': compiler.parent.parent, 'fixture': output}
    def relative(path):
        """Reject unexpected external headers rather than silently mixing SDK installations."""
        for name, parent in roots.items():
            if path.is_relative_to(parent): return name+'/'+path.relative_to(parent).as_posix()
        raise ValueError('Unqualified external dependency: '+str(path))
    paths = set(dependencies(output/'nvs_page.d')) | {compiler, linker, compiler.parent.parent/'libexec/gcc/riscv32-esp-elf/14.2.0/cc1plus.exe'}
    pins = {relative(p): sha(p.read_bytes()) for p in sorted(paths)}
    def canonical(values):
        """Remove host paths from published command provenance, retaining every option."""
        result = []
        for value in values:
            text = str(value)
            for name, parent in roots.items(): text = text.replace(str(parent), '${'+name+'}')
            result.append(text)
        return result
    report = dict(schema='factory-nvs-compile-v1', passed=True, sdk_revision=SDK_REVISION,
                  compiler_version=version.strip(), dependencies=pins, compile=canonical(args), link=canonical(link_args),
                  object_sha256=sha((output/'nvs_page.cpp.o').read_bytes()),
                  layout_elf_sha256=sha((output/'layout.elf').read_bytes()), config_sha256=sha(profile),
                  factory_compiler_version_identified=False, factory_config_identified=False,
                  production_firmware_built=False)
    (output/'provenance.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8', newline='\n')
    if run(['git', '-C', sdk, 'status', '--porcelain'], sdk).strip(): raise ValueError('SDK changed during compilation')
    return report


def main():
    """Require explicit read-only inputs and a fresh task-local output folder."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('sdk', 'compiler', 'config', 'output'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    report = build(*(getattr(args, n).resolve() for n in ('sdk', 'compiler', 'config', 'output')))
    print(json.dumps({k: report[k] for k in ('passed', 'object_sha256', 'layout_elf_sha256')}))


if __name__ == '__main__': main()
