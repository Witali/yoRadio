"""Build the offline, pinned JPEG dependency for the ESP32-C2 application."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile

PROJECT = Path(__file__).resolve().parents[1]
VENDOR = PROJECT / 'third_party/libjpeg-turbo'
PATCH_KEYS = ('patch', 'flash_tables_patch', 'compact_pools_patch')


def sha(path):
    """Fingerprint saved bytes, including tool binaries and generated headers."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    """Use stable UTF-8/LF metadata on Windows and Unix."""
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n',
                    encoding='utf-8', newline='\n')


def verify_bundle(vendor=VENDOR):
    """Reject corrupt archives, mismatched patches or licenses before extraction."""
    bundle = json.loads((vendor / 'BUNDLE.json').read_text(encoding='utf-8'))
    upstream = json.loads((vendor / 'UPSTREAM.json').read_text(encoding='utf-8'))
    archive = vendor / 'upstream.tar.gz'
    if sha(archive) != bundle['gzip_sha256']:
        raise ValueError('JPEG compressed source archive differs from BUNDLE.json')
    raw = gzip.decompress(archive.read_bytes())
    if (hashlib.sha256(raw).hexdigest() != upstream['source_archive_sha256'] or
            len(raw) != bundle['tar_bytes'] or upstream['commit'] != bundle['commit']):
        raise ValueError('JPEG upstream source archive or revision differs')
    for key in PATCH_KEYS:
        if sha(vendor / upstream[key]) != upstream[key + '_sha256']:
            raise ValueError('JPEG adaptation patch differs: ' + upstream[key])
    for name, digest in upstream['license_files'].items():
        if sha(vendor / name) != digest:
            raise ValueError('JPEG license differs: ' + name)
    return upstream


def apply_patch(path, source):
    """Apply only to the isolated export, never to its enclosing Git worktree."""
    environment = os.environ.copy()
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR'):
        environment.pop(name, None)
    environment['GIT_CEILING_DIRECTORIES'] = source.parent.as_posix()
    discovery = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'],
                               cwd=source, env=environment, capture_output=True)
    if discovery.returncode == 0:
        raise ValueError('JPEG export unexpectedly discovered a parent Git repository')
    for flags in (['--check'], []):
        subprocess.run(['git', 'apply', *flags, str(path)], cwd=source,
                       env=environment, check=True)


def products(directory):
    """Bind the archive and all exported/configured headers consumed by the app."""
    paths = sorted(p for p in (directory / 'source').rglob('*') if p.is_file())
    paths += sorted((directory / 'library').glob('*.h'))
    paths += [directory / 'library/libjpeg.a', directory / 'rv32-toolchain.cmake']
    return {p.relative_to(directory).as_posix(): sha(p) for p in paths}


def build(args):
    """Reuse only a completely verified build with identical inputs and tools."""
    vendor = args.vendor.resolve()
    upstream = verify_bundle(vendor)
    binaries = args.toolchain_bin.resolve()
    suffix = '.exe' if (binaries / 'riscv32-esp-elf-gcc.exe').is_file() else ''
    tools = {name: binaries / ('riscv32-esp-elf-' + name + suffix)
             for name in ('gcc', 'ar', 'ranlib')}
    specs = binaries.parent / 'riscv32-esp-elf/lib/picolibc.specs'
    cmake, ninja = args.cmake.resolve(), args.ninja.resolve()
    flags = ['-march=rv32imc_zicsr_zifencei', '-mabi=ilp32', '-mtune=esp-base',
             '-ffunction-sections', '-fdata-sections', '-fstack-usage',
             '-fno-jump-tables', '-fno-tree-switch-conversion',
             '-D__PICOLIBC_ERRNO_FUNCTION=__errno', '-specs=' + specs.as_posix()]
    inputs = {'builder': sha(Path(__file__)), 'flags': flags,
              'release_flags': '-Os -DNDEBUG',
              'vendor': {p.relative_to(vendor).as_posix(): sha(p)
                         for p in sorted(vendor.rglob('*')) if p.is_file()},
              'tools': {str(p): sha(p) for p in [*tools.values(), specs, cmake, ninja]}}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True,
                                            separators=(',', ':')).encode()).hexdigest()
    output = args.output.resolve()
    directory = output / fingerprint
    report_path = directory / 'report.json'
    if directory.exists():
        if not report_path.is_file():
            raise ValueError('Incomplete JPEG build; select a fresh output directory: ' + str(directory))
        report = json.loads(report_path.read_text(encoding='utf-8'))
        if (report['build_inputs'] != inputs or report['products_sha256'] != products(directory) or
                report['library_sha256'] != sha(directory / 'library/libjpeg.a') or
                report['upstream_commit'] != upstream['commit'] or
                any(report[key] != upstream[value] for key, value in
                    (('patch_sha256', 'patch_sha256'),
                     ('flash_patch_sha256', 'flash_tables_patch_sha256'),
                     ('pool_patch_sha256', 'compact_pools_patch_sha256')))):
            raise ValueError('Cached JPEG build changed; select a fresh output directory')
    else:
        directory.mkdir(parents=True)
        source = directory / 'source'
        source.mkdir()
        with tarfile.open(vendor / 'upstream.tar.gz', 'r:gz') as archive:
            # Python's data filter rejects traversal/escaping links in source bundles.
            archive.extractall(source, filter='data')
        for key in PATCH_KEYS:
            apply_patch(vendor / upstream[key], source)
        toolchain = directory / 'rv32-toolchain.cmake'
        toolchain.write_text('\n'.join([
            'set(CMAKE_SYSTEM_NAME Generic)', 'set(CMAKE_SYSTEM_PROCESSOR riscv32)',
            'set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)',
            *[f'set(CMAKE_{key} "{tools[name].as_posix()}")' for key, name in
              (('C_COMPILER', 'gcc'), ('AR', 'ar'), ('RANLIB', 'ranlib'))],
            f'set(CMAKE_C_FLAGS_INIT "{" ".join(flags)}")', '']),
            encoding='utf-8', newline='\n')
        library = directory / 'library'
        options = [f'-DCMAKE_TOOLCHAIN_FILE={toolchain.as_posix()}',
                   '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_C_FLAGS_RELEASE=-Os -DNDEBUG',
                   '-DENABLE_SHARED=OFF', '-DENABLE_STATIC=ON', '-DWITH_SIMD=OFF',
                   '-DWITH_TURBOJPEG=OFF', '-DWITH_TOOLS=OFF', '-DWITH_TESTS=OFF']
        subprocess.run([str(cmake), '-S', str(source), '-B', str(library), '-G', 'Ninja',
                        '-DCMAKE_MAKE_PROGRAM=' + ninja.as_posix(), *options], check=True)
        subprocess.run([str(cmake), '--build', str(library), '--target', 'jpeg-static',
                        '--parallel', '2'], check=True)
        # Set Release explicitly: a toolchain normal variable can differ from
        # the cache display. Check Ninja's actual commands as well as the cache.
        cache = (library / 'CMakeCache.txt').read_text(encoding='utf-8')
        if 'CMAKE_C_FLAGS_RELEASE:STRING=-Os -DNDEBUG\n' not in cache:
            raise ValueError('JPEG release optimization flags differ')
        compile_flags = sorted(set(re.findall(r'^  FLAGS = (.+)$',
            (library / 'build.ninja').read_text(encoding='utf-8'), re.MULTILINE)))
        if not compile_flags or any('-Os -DNDEBUG' not in value or '-O3' in value
                                    for value in compile_flags):
            raise ValueError('JPEG actual compiler flags differ')
        report = dict(schema_version=1, upstream_commit=upstream['commit'],
                      source_archive_sha256=upstream['source_archive_sha256'],
                      patch_sha256=upstream['patch_sha256'], flash_tables=True,
                      flash_patch_sha256=upstream['flash_tables_patch_sha256'],
                      compact_pools=True, pool_patch_sha256=upstream['compact_pools_patch_sha256'],
                      library_sha256=sha(library / 'libjpeg.a'), build_inputs=inputs,
                      cmake_flags=options, actual_compile_flags=compile_flags,
                      products_sha256=products(directory),
                      scope='RV32 dependency build; application runtime acceptance is separate')
        # No changing patch, source, tool or executable may silently bless a build.
        verify_bundle(vendor)
        if inputs['vendor'] != {p.relative_to(vendor).as_posix(): sha(p)
                                for p in sorted(vendor.rglob('*')) if p.is_file()}:
            raise ValueError('JPEG dependency inputs changed while compiling')
        if any(sha(Path(p)) != digest for p, digest in inputs['tools'].items()):
            raise ValueError('JPEG build tools changed while compiling')
        save_json(report_path, report)
    save_json(output / 'selection.json', dict(build_directory=directory.as_posix(),
              fingerprint=fingerprint, library_sha256=report['library_sha256']))
    print('JPEG dependency ready:', directory)


def main():
    """Build only offline saved inputs using the caller's pinned ESP-IDF tools."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor', type=Path, default=VENDOR)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--toolchain-bin', type=Path, required=True)
    parser.add_argument('--cmake', type=Path, required=True)
    parser.add_argument('--ninja', type=Path, required=True)
    build(parser.parse_args())


if __name__ == '__main__':
    main()
