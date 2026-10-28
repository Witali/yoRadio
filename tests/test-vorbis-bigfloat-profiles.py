#!/usr/bin/env python3
"""Compile-only LX6/RV32 profiles; never link, flash, emulate, or execute MCU code."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path('C:/Work/yoRadio')
COMPONENT = ROOT / 'idf/components/native_vorbis_bigfloat'
LX6 = REPOSITORY / '.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf'
RV32 = REPOSITORY / '.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf'
CLANG = REPOSITORY / '.idf/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang'
UNITS = ('bigfloat.c', 'portable/libbf.c', 'upstream/cutils.c')
UPSTREAM = {
    'upstream/libbf.c': (242338, '8abc36c9feaeaeb04729e3494c6b693611a518442d11c6546c86bc08b30a1228'),
    'upstream/libbf.h': (18029, '6376f2965cef49ad9e1351ff99e3dce4c6e9961d9e59e75de45aad63a1724c8a'),
    'upstream/cutils.c': (6105, 'a1ec96510f657c9f585d42083c527b25cbccd480a28d31c6fa2d25f705ccaeeb'),
    'upstream/cutils.h': (4771, '92084de8f384cdd746f9fc86d8378acd178dc726cb79fbed3dbd3c642aa475a2'),
    'upstream/list.h': (3091, '484a604d8996a9c23c23d453ec5017af05b2c74de4bb34da8abcd5f5b5880f3e'),
    'upstream/readme.txt': (7638, 'e5e5919ae21c0878c2b58508005a9c4c9acf182e00f14eadb99e55ac1d7f2019'),
}
FLAGS = ['-O2', '-fno-inline', '-fno-fast-math', '-ffp-contract=off',
         '-fstack-usage', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra']
SMOKE = '''#include "native_vorbis_bigfloat.h"
static_assert(LIMB_BITS == 32, "MCU limb width must be 32");
static_assert(sizeof(void *) == 4, "MCU pointer width must be 32");
static_assert(sizeof(limb_t) == 4, "MCU limb storage must be 32");
native_vorbis_bigfloat_status_t profile_header_smoke(
    native_vorbis_bigfloat_context_t *context, bf_t *destination) {
    return native_vorbis_bigfloat_set_u64(context, destination, 0);
}
'''


def sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def file_record(path: Path, base: Path | None = None) -> dict:
    body = path.read_bytes()
    return {'path': path.relative_to(base).as_posix() if base else str(path),
            'bytes': len(body), 'sha256': sha(body)}


def diagnostics(body: str) -> dict:
    matches = re.findall(r'^.*?:\d+:(?:\d+:)?\s+(warning|(?:fatal )?error):',
                         body.replace('\r\n', '\n'), flags=re.M)
    return {'warnings': matches.count('warning'),
            'errors': sum(value.endswith('error') for value in matches)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((ROOT / '.build').resolve()):
        parser.error('output must be a fresh directory under this worktree .build')
    out.mkdir(parents=True, exist_ok=False)
    report = {'schema': 'vorbis-bigfloat-profiles-v1', 'completed': False,
              'passed': False, 'source_only': True, 'native_executed': False,
              'linked': False, 'sdk_executed': False, 'qemu_executed': False,
              'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'controller': file_record(Path(__file__)),
              'sources': [], 'tools': [], 'commands': [], 'objects': [],
              'stack_usage': [], 'lint': {}, 'scope': {
                  'gcc': 'all three C units and C++17 public-header smoke for both ISAs',
                  'warnings': 'adapter/header -Werror; creator code warnings retained, one explicit portability copy',
                  'lint': 'adapter C translation unit only, MCU headers, unchanged repository config',
                  'limits': 'compile-only evidence; no arithmetic, allocation, timing or MCU-fit qualification'}}

    def save() -> None:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def run(name: str, argv: list[str | Path], timeout: int = 120) -> dict:
        row = {'name': name, 'argv': [str(value) for value in argv], 'cwd': str(out),
               'child_started': False, 'pid': None, 'returncode': None,
               'started_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        report['commands'].append(row)
        so, se = out / (name + '.stdout.log'), out / (name + '.stderr.log')
        start = time.monotonic()
        error = None
        with so.open('wb') as stdout, se.open('wb') as stderr:
            try:
                process = subprocess.Popen(row['argv'], cwd=out, stdout=stdout, stderr=stderr,
                                           shell=False, stdin=subprocess.DEVNULL)
                row.update(child_started=True, pid=process.pid)
                save()
                try:
                    row['returncode'] = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    row['timed_out'] = True
                    process.kill()
                    row['returncode'] = process.wait(timeout=15)
                    error = 'process timeout; child killed and reaped'
            except OSError as exc:
                error = str(exc)
                row['pre_child_error'] = {'type': type(exc).__name__, 'errno': exc.errno,
                                          'winerror': getattr(exc, 'winerror', None), 'message': str(exc)}
        row['elapsed_seconds'] = time.monotonic() - start
        row['stdout'] = file_record(so, out)
        row['stderr'] = file_record(se, out)
        row['diagnostics'] = diagnostics(so.read_text(errors='replace') + se.read_text(errors='replace'))
        if error:
            row['error'] = error
        row['terminal'] = row['returncode'] is not None or not row['child_started']
        save()
        if error:
            raise RuntimeError(f'{name}: {error}')
        return row

    try:
        source = out / 'sources/native_vorbis_bigfloat'
        names = sorted(path.relative_to(COMPONENT).as_posix() for path in COMPONENT.rglob('*') if path.is_file())
        if not all(name in names for name in (*UNITS, 'include/native_vorbis_bigfloat.h',
                                               'upstream/libbf.h', 'upstream/cutils.h',
                                               'CMakeLists.txt', 'upstream-manifest.json')):
            raise AssertionError('complete component/source contract is absent')
        for name in names:
            original = COMPONENT / name
            if original.is_symlink():
                raise AssertionError('component source symlinks are not supported')
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            body = original.read_bytes()
            target.write_bytes(body)
            report['sources'].append({'repository_path': original.relative_to(ROOT).as_posix(),
                                      'snapshot': target.relative_to(out).as_posix(),
                                      'bytes': len(body), 'sha256': sha(body)})
        shutil.copyfile(__file__, out / 'sources/controller.py')
        shutil.copyfile(ROOT / '.clang-tidy', out / 'sources/clang-tidy.yaml')
        smoke = out / 'sources/header.cpp'
        smoke.write_text(SMOKE, encoding='utf-8', newline='\n')
        report['generated_header'] = file_record(smoke, out)
        report['lint_configuration'] = file_record(out / 'sources/clang-tidy.yaml', out)
        manifest = json.loads((source / 'upstream-manifest.json').read_text())
        if manifest['archive_sha256'] != '4b23394d67a4a3c3266a38b66831094523fffb5d01974a5c05a0327b36b0a340':
            raise AssertionError('unexpected official LibBF release')
        if {entry['path'] for entry in manifest['files']} != set(UPSTREAM):
            raise AssertionError('unexpected original creator source inventory')
        for entry in manifest['files']:
            actual = file_record(source / entry['path'])
            if (entry['bytes'], entry['sha256']) != UPSTREAM[entry['path']] or any(
                    actual[key] != entry[key] for key in ('bytes', 'sha256')):
                raise AssertionError('upstream manifest byte mismatch: ' + entry['path'])
        common_patch = {
            'original': 'upstream/libbf.c',
            'original_sha256': UPSTREAM['upstream/libbf.c'][1],
            'modified': 'portable/libbf.c',
            'modified_sha256': '158da48780e54571ae2ce56ef7049f9829f62817c005009c9018bdf74d92a378',
            'patch': 'portability.patch',
            'patch_sha256': 'cd15a88f0718bb2f18e2b8b269a57983315ef28617b2e836b3bba07391389a42',
            'occurrences': 1}
        expected_patches = [
            {**common_patch, 'id': 'picolibc-int32-result-local',
             'old': '    return bf_get_int32(pres, a, flags);',
             'new': '    int value;\n    int status = bf_get_int32(&value, a, flags);\n    *pres = value;\n    return status;'},
            {**common_patch, 'id': 'zero-length-copy-nonnull',
             'old': '    memcpy(r->tab, a->tab, a->len * sizeof(limb_t));',
             'new': '    if (a->len != 0)\n        memcpy(r->tab, a->tab, a->len * sizeof(limb_t));'},
        ]
        modifications = manifest['modifications']
        if len(modifications) != 2 or any(actual.get(key) != value
                for actual, expected in zip(modifications, expected_patches) for key, value in expected.items()):
            raise AssertionError('unexpected portability modification contract')
        reconstructed = (source / common_patch['original']).read_bytes()
        portable = (source / common_patch['modified']).read_bytes()
        patch = (source / common_patch['patch']).read_bytes()
        for expected in expected_patches:
            old, new = expected['old'].encode(), expected['new'].encode()
            if reconstructed.count(old) != 1:
                raise AssertionError('portability replacement does not have exactly one occurrence')
            reconstructed = reconstructed.replace(old, new, 1)
        if reconstructed != portable or sha(portable) != common_patch['modified_sha256'] or \
                sha(patch) != common_patch['patch_sha256']:
            raise AssertionError('portable copy is not the exact audited two-site reconstruction')
        cmake = (source / 'CMakeLists.txt').read_text()
        source_clause = re.search(r'\bSRCS\s+(.*?)\s+INCLUDE_DIRS\b', cmake, re.S)
        if source_clause is None or tuple(re.findall(r'"([^"]+)"', source_clause.group(1))) != UNITS:
            raise AssertionError('CMake source closure differs from profiled units')
        report['portability'] = {**common_patch, 'modifications': expected_patches, 'reconstruction_verified': True,
                                 'unchanged_original_preserved': True,
                                 'portable_bytes': len(portable), 'patch_bytes': len(patch)}

        include = ['-I' + str(source / 'include'), '-I' + str(source / 'upstream')]
        targets = [('lx6', LX6 / 'bin/xtensa-esp32-elf-', [], 94),
                   ('rv32', RV32 / 'bin/riscv32-esp-elf-', ['-march=rv32imc', '-mabi=ilp32'], 243)]
        compile_rows = []
        for label, prefix, architecture, machine in targets:
            cc, cxx = Path(str(prefix) + 'gcc.exe'), Path(str(prefix) + 'g++.exe')
            for kind, compiler in [('gcc', cc), ('g++', cxx)]:
                report['tools'].append(file_record(compiler))
                if run(label + '-' + kind + '-version', [compiler, '--version'])['returncode']:
                    raise RuntimeError(label + ' compiler version failed')
            selected = [(Path(name).stem, source / name, cc, 'gnu17', name == 'bigfloat.c') for name in UNITS]
            selected.append(('header', smoke, cxx, 'c++17', True))
            for unit, path, compiler, standard, strict in selected:
                output = out / (label + '-' + unit + '.o')
                command = [compiler, *architecture, *FLAGS, '-std=' + standard,
                           *(['-Werror'] if strict else []), *include, '-c', path, '-o', output]
                row = run(label + '-' + unit, command)
                row.update(target=label, unit=unit, warnings_as_errors=strict)
                compile_rows.append(row)
                if row['returncode']:
                    continue
                body = output.read_bytes()
                if len(body) < 52 or body[:6] != b'\x7fELF\x01\x01':
                    raise AssertionError('not a little-endian ELF32 object: ' + output.name)
                elf_type, actual_machine = struct.unpack_from('<HH', body, 16)
                if elf_type != 1 or actual_machine != machine:
                    raise AssertionError('object ISA/type mismatch: ' + output.name)
                report['objects'].append({**file_record(output, out), 'target': label,
                                          'unit': unit, 'elf_class': 32, 'elf_type': elf_type,
                                          'machine': actual_machine})
                usage = output.with_suffix('.su')
                lines = usage.read_text(encoding='utf-8', errors='strict').splitlines()
                parsed = []
                for line in lines:
                    fields = line.split('\t')
                    if len(fields) != 3 or not fields[1].isdigit():
                        raise AssertionError('unexpected stack-usage row')
                    parsed.append({'function': fields[0], 'bytes': int(fields[1]), 'kind': fields[2]})
                report['stack_usage'].append({**file_record(usage, out), 'target': label,
                                             'unit': unit, 'functions': parsed,
                                             'maximum_reported_bytes': max((x['bytes'] for x in parsed), default=0)})
                save()

        tidy = CLANG / 'bin/clang-tidy.exe'
        report['tools'].append(file_record(tidy))
        if run('clang-tidy-version', [tidy, '--version'])['returncode']:
            raise RuntimeError('clang-tidy version failed')
        lint = run('lint-adapter', [tidy, source / 'bigfloat.c',
            '--config-file=' + str(out / 'sources/clang-tidy.yaml'), '--header-filter=.*',
            '--export-fixes=' + str(out / 'adapter-fixes.yaml'), '--',
            '--target=xtensa-esp-elf', '-mcpu=esp32', '-std=gnu17', '-O2',
            '-fno-fast-math', '-ffp-contract=off', '-nostdinc',
            '-isystem', CLANG / 'lib/clang/20/include',
            '-isystem', LX6 / 'picolibc/include', *include])
        report['lint'] = {'translation_unit': 'bigfloat.c', **lint['diagnostics'],
                          'returncode': lint['returncode'], 'upstream_translation_units_analyzed': False,
                          'custom_suppressions_added': False}
        if (out / 'adapter-fixes.yaml').exists():
            report['lint']['exported_fixes'] = file_record(out / 'adapter-fixes.yaml', out)
        current_names = sorted(path.relative_to(COMPONENT).as_posix() for path in COMPONENT.rglob('*') if path.is_file())
        if current_names != names:
            raise AssertionError('component file set changed during profile')
        for row in report['sources']:
            live = ROOT / row['repository_path']
            actual = file_record(live)
            if any(actual[key] != row[key] for key in ('bytes', 'sha256')):
                raise AssertionError('live source changed during profile: ' + row['repository_path'])
        if file_record(Path(__file__))['sha256'] != report['controller']['sha256']:
            raise AssertionError('controller changed during profile')
        report['immutable_sources'] = True
        report['completed'] = True
        report['passed'] = len(report['objects']) == 8 and len(report['stack_usage']) == 8 and all(
            row['returncode'] == 0 for row in compile_rows) and lint['returncode'] == 0 and not lint['diagnostics']['errors']
    except BaseException as exc:
        report['error'] = {'type': type(exc).__name__, 'message': str(exc)}
        (out / 'controller-error.log').write_text(traceback.format_exc(), encoding='utf-8')
    finally:
        report['ended_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        save()
    print(json.dumps({'passed': report['passed'], 'completed': report['completed'],
                      'source_only': True, 'native_executed': False,
                      'commands': len(report['commands']), 'objects': len(report['objects']),
                      'lint': report['lint'], 'report': str(out / 'report.json')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
