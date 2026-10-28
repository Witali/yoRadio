#!/usr/bin/env python3
"""Pure native-source-profile replay; no extraction, archived code or child process."""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/vorbis-bigfloat-20261028'
ARCHIVE_SHA = '56132fd8ec76e76fc2b6d519dc9f5cc2ceba8f92b8558c99ef3e230f8bf318cf'
MANIFEST_SHA = '1efdf113950cfb6d13cb694b92490a6bd55ebae78becc48bd64461ae8d4cb27b'
CONTROLLER_SHA = 'a6d2ca98e4493c13c50f870fe34d15574460eb6898a2b997d799508f2ce86b12'
CONTROLLERS = ['4ab1240aaf4214a69649c3805b24fae0b940571a8ac40851dbf84e543f595c3d',
               '4ab1240aaf4214a69649c3805b24fae0b940571a8ac40851dbf84e543f595c3d',
               '4dde1c65d1f2bc4780dfe8698e639177c57c17e7b681063312bfaffb5e712f06', CONTROLLER_SHA]
REPORTS = ['54c8fb5b8c7f305267256c0c3e8e2f34f7f41d2d889c62c684d6f8b7aabc1790',
           '74a59c1b19c609750132575b1ef3ac99eb7a8d55fc9310b66d1d103d4984a009',
           '88ba2075cffb8110c115933cc7872096c21d508bb92082e6a0585078d30b9efd',
           'fe56791c7a310c1039fca41f724b889231aeef3e4cc92bedbeef829190702090']
GROUPS = ['vorbis-bigfloat-profiles-20261028-%02d' % n for n in range(1, 5)]
GROUP_COUNTS = [(18, 341749), (58, 530100), (63, 1403188), (63, 1407465)]
COMPONENT = 'idf/components/native_vorbis_bigfloat/'
SOURCE = 'sources/native_vorbis_bigfloat/'
BUILD = 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/'
LX6 = 'C:/Work/yoRadio/.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf'
RV32 = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf'
CLANG = 'C:/Work/yoRadio/.idf/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang'
FLAGS = ['-O2', '-fno-inline', '-fno-fast-math', '-ffp-contract=off', '-fstack-usage',
         '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra']
TOOLS = [
    (LX6 + '/bin/xtensa-esp32-elf-gcc.exe', 906240, '20e70278d1fa041c1305e0e70e6f35dde01b7eb21f2c7bbc0013456493a011a5'),
    (LX6 + '/bin/xtensa-esp32-elf-g++.exe', 906240, '20e70278d1fa041c1305e0e70e6f35dde01b7eb21f2c7bbc0013456493a011a5'),
    (RV32 + '/bin/riscv32-esp-elf-gcc.exe', 2644480, '9a96e8e77c263d4f7f16c084e8a2dfe89dfa8598c31fd3f9b152db35ccbb2a74'),
    (RV32 + '/bin/riscv32-esp-elf-g++.exe', 2648576, '420df714d316aa3c4c7f002a3332b0a3b9c47a6b6833388ed1589a5ce75b52ee'),
    (CLANG + '/bin/clang-tidy.exe', 67037184, 'f7da288749fc81d990a8fbd9ee2a81927f98cc98148cbf853055b445cb045364')]
PATCHES = [
    ('picolibc-int32-result-local', b'    return bf_get_int32(pres, a, flags);',
     b'    int value;\n    int status = bf_get_int32(&value, a, flags);\n    *pres = value;\n    return status;'),
    ('zero-length-copy-nonnull', b'    memcpy(r->tab, a->tab, a->len * sizeof(limb_t));',
     b'    if (a->len != 0)\n        memcpy(r->tab, a->tab, a->len * sizeof(limb_t));')]
PORTABLE = {3: ('598d82bf113286953a72b2c1f8824d1411745bcc4e4928bab5c8ccf8989c9bbe',
                 '7e8152163187eabe18f14eb46f158d7a911e123f3a1e25c54f8141f7f6403c76'),
            4: ('158da48780e54571ae2ce56ef7049f9829f62817c005009c9018bdf74d92a378',
                 'cd15a88f0718bb2f18e2b8b269a57983315ef28617b2e836b3bba07391389a42')}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def norm(value):
    return value.replace('\\', '/')


def canonical(name):
    return isinstance(name, str) and bool(name) and name.isascii() and ':' not in name and '\\' not in name and \
        not any(ord(c) < 32 or ord(c) == 127 for c in name) and not PurePosixPath(name).is_absolute() and \
        '..' not in PurePosixPath(name).parts and PurePosixPath(name).as_posix() == name


def inventory():
    archive_body = (FOLDER / 'source-profiles.zip').read_bytes()
    manifest_body = (FOLDER / 'source-profiles-manifest.json').read_bytes()
    need(len(archive_body) == 891356 and sha(archive_body) == ARCHIVE_SHA and
         sha(manifest_body) == MANIFEST_SHA, 'sealed source-only archive/manifest identity')
    manifest = json.loads(manifest_body)
    need(manifest['schema'] == 'vorbis-bigfloat-source-profiles-evidence-v1' and not manifest['omitted'] and
         manifest['total_members'] == 202 and manifest['total_decoded_bytes'] == 3682502,
         'complete source-profile inventory without omissions')
    rows = manifest['members']
    need(len(rows) == len({row['path'] for row in rows}) == 202 and all(
         set(row) == {'path', 'bytes', 'sha256'} and canonical(row['path']) and type(row['bytes']) is int and
         row['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', row['sha256']) for row in rows),
         'canonical unique manifest names')
    pins = {row['path']: row for row in rows}; members = {}
    with zipfile.ZipFile(io.BytesIO(archive_body)) as archive:
        info = archive.infolist()
        need(len(info) == len({row.filename for row in info}) == 202 and
             {row.filename for row in info} == set(pins) and sum(row.file_size for row in info) == 3682502,
             'exact ZIP member set and decoded bytes')
        for row in info:
            need(canonical(row.filename) and not row.is_dir() and not row.flag_bits & 1 and
                 stat.S_IFMT(row.external_attr >> 16) in (0, stat.S_IFREG) and
                 row.file_size == pins[row.filename]['bytes'], 'regular safe ZIP member')
            body = archive.read(row)
            need(sha(body) == pins[row.filename]['sha256'], 'every preserved source/log/object/stack byte')
            members[row.filename] = body
    need([row['path'] for row in manifest['groups']] == GROUPS and
         {name.split('/')[0] for name in members} == set(GROUPS), 'all four attempt groups')
    for i, row in enumerate(manifest['groups']):
        files = [body for name, body in members.items() if name.startswith(GROUPS[i] + '/')]
        need((len(files), sum(map(len, files))) == GROUP_COUNTS[i] == (row['files'], row['bytes']) and
             row['report_sha256'] == REPORTS[i] == sha(members[GROUPS[i] + '/report.json']) and
             row['passed'] == (i >= 2) and row['completed'] == (i >= 1) and row['source_only'] and
             not row['native_executed'], 'exact group inventory and attempt outcome')
    return members


def literal_assignment(body, name):
    values = [ast.literal_eval(node.value) for node in ast.parse(body).body if isinstance(node, ast.Assign) and
              any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    need(len(values) == 1, 'one literal controller constant: ' + name)
    return values[0]


def diagnostics(body):
    found = re.findall(r'^.*?:\d+:(?:\d+:)?\s+(warning|(?:fatal )?error):', body.replace('\r\n', '\n'), re.M)
    return dict(warnings=found.count('warning'), errors=sum(value.endswith('error') for value in found))


def elf(body, machine):
    need(len(body) >= 52 and body[:9] == b'\x7fELF\x01\x01\x01\0\0', 'ELF32 little-endian v1 System-V ABI')
    kind, actual, version = struct.unpack_from('<HHI', body, 16)
    flags = struct.unpack_from('<I', body, 36)[0]
    header, phsize, phcount, shsize, shcount, shstrings = struct.unpack_from('<HHHHHH', body, 40)
    shoffset = struct.unpack_from('<I', body, 32)[0]
    need(kind == 1 and actual == machine and version == 1 and header == 52 and phcount == phsize == 0 and
         shsize == 40 and shcount > 0 and shstrings < shcount and shoffset + shcount * shsize <= len(body),
         'actual relocatable machine/header/section geometry')
    need(flags == (0x300 if machine == 94 else 1), 'Xtensa ABI flags or RV32 RVC/soft-float ABI')
    return dict(machine=machine, elf_class=32, flags=flags, sections=shcount)


def check_patch(members, group, report, number, upstream):
    prefix = group + '/' + SOURCE
    manifest = json.loads(members[prefix + 'upstream-manifest.json'])
    need(manifest['archive_sha256'] == '4b23394d67a4a3c3266a38b66831094523fffb5d01974a5c05a0327b36b0a340' and
         manifest['archive_bytes'] == 150365 and manifest['version'] == '2025-06-03' and
         manifest['source'] == 'https://bellard.org/libbf/libbf-2025-06-03.tar.gz' and
         {row['path'] for row in manifest['files']} == set(upstream), 'official original creator lineage')
    for row in manifest['files']:
        body = members[prefix + row['path']]
        need((len(body), sha(body)) == tuple(upstream[row['path']]) == (row['bytes'], row['sha256']),
             'unchanged original creator bytes')
    if number < 3:
        need(not manifest['modifications'], 'stock-source attempts have no hidden patch')
        return
    portable_pin, patch_pin = PORTABLE[number]
    original = members[prefix + 'upstream/libbf.c']; reconstructed = original
    changes = manifest['modifications']
    need(len(changes) == number - 2, 'exact historical/current patch count')
    for actual, (identifier, old, new) in zip(changes, PATCHES):
        need(actual['id'] == identifier and actual['old'] == old.decode() and actual['new'] == new.decode() and
             actual['occurrences'] == 1 and actual['original'] == 'upstream/libbf.c' and
             actual['original_sha256'] == sha(original) and actual['modified'] == 'portable/libbf.c' and
             actual['modified_sha256'] == portable_pin and actual['patch'] == 'portability.patch' and
             actual['patch_sha256'] == patch_pin and reconstructed.count(old) == 1, 'exact documented replacement')
        reconstructed = reconstructed.replace(old, new, 1)
    portable = members[prefix + 'portable/libbf.c']; patch = members[prefix + 'portability.patch']
    need(portable == reconstructed and sha(portable) == portable_pin and sha(patch) == patch_pin,
         'mechanically reconstruct both copied source and exact patch identity')
    proof = report['portability']
    need(proof['reconstruction_verified'] and proof['unchanged_original_preserved'] and
         proof['modified_sha256'] == portable_pin and proof['patch_sha256'] == patch_pin and
         proof['portable_bytes'] == len(portable) and proof['patch_bytes'] == len(patch), 'executed reconstruction receipt')


def expected_commands(group, number):
    base = BUILD + group; src = base + '/sources/native_vorbis_bigfloat'
    include = ['-I' + src + '/include', '-I' + src + '/upstream']
    result = []
    for label, prefix, arch in [('lx6', LX6 + '/bin/xtensa-esp32-elf-', []),
                                ('rv32', RV32 + '/bin/riscv32-esp-elf-', ['-march=rv32imc', '-mabi=ilp32'])]:
        cc, cxx = prefix + 'gcc.exe', prefix + 'g++.exe'
        result += [(label + '-gcc-version', [cc, '--version']), (label + '-g++-version', [cxx, '--version'])]
        for unit, path, compiler, standard, strict in [
            ('bigfloat', src + '/bigfloat.c', cc, 'gnu17', True),
            ('libbf', src + ('/portable/libbf.c' if number >= 3 else '/upstream/libbf.c'), cc, 'gnu17', False),
            ('cutils', src + '/upstream/cutils.c', cc, 'gnu17', False),
            ('header', base + '/sources/header.cpp', cxx, 'c++17', True)]:
            result.append((label + '-' + unit, [compiler, *arch, *FLAGS, '-std=' + standard,
                *(['-Werror'] if strict else []), *include, '-c', path, '-o', base + '/' + label + '-' + unit + '.o']))
    result.append(('clang-tidy-version', [CLANG + '/bin/clang-tidy.exe', '--version']))
    result.append(('lint-adapter', [CLANG + '/bin/clang-tidy.exe', src + '/bigfloat.c',
        '--config-file=' + base + '/sources/clang-tidy.yaml', '--header-filter=.*',
        '--export-fixes=' + base + '/adapter-fixes.yaml', '--', '--target=xtensa-esp-elf', '-mcpu=esp32',
        '-std=gnu17', '-O2', '-fno-fast-math', '-ffp-contract=off', '-nostdinc',
        '-isystem', CLANG + '/lib/clang/20/include', '-isystem', LX6 + '/picolibc/include', *include]))
    return result[:1] if number == 1 else result


def check_group(members, group, number, upstream, smoke):
    report = json.loads(members[group + '/report.json'])
    need(report['schema'] == 'vorbis-bigfloat-profiles-v1' and report['source_only'] and all(
         report[key] is False for key in ('native_executed', 'linked', 'sdk_executed', 'qemu_executed')),
         'source-only scope is explicit in every attempt')
    need(report['passed'] == (number >= 3) and report['completed'] == (number >= 2), 'actual attempt outcome')
    need(report['controller']['sha256'] == CONTROLLERS[number - 1] == sha(members[group + '/sources/controller.py']) and
         report['controller']['bytes'] == len(members[group + '/sources/controller.py']), 'exact executed controller')
    need(members[group + '/sources/header.cpp'] == smoke.encode() and
         sha(smoke.encode()) == report['generated_header']['sha256'], 'compiled C++32-bit pointer/limb assertions')
    need(members[group + '/sources/clang-tidy.yaml'] == (ROOT / '.clang-tidy').read_bytes() and
         sha(members[group + '/sources/clang-tidy.yaml']) == report['lint_configuration']['sha256'],
         'unchanged baseline lint configuration')
    source_names = {name[len(group + '/' + SOURCE):] for name in members if name.startswith(group + '/' + SOURCE)}
    expected_sources = set(upstream) | {'bigfloat.c', 'include/native_vorbis_bigfloat.h', 'CMakeLists.txt',
                                       'README.md', 'upstream-manifest.json'}
    if number >= 3:
        expected_sources |= {'portable/libbf.c', 'portability.patch'}
    need(source_names == expected_sources and len(report['sources']) == len(expected_sources), 'whole component file set')
    for row in report['sources']:
        relative = row['repository_path']
        need(canonical(relative) and relative.startswith(COMPONENT) and
             row['snapshot'] == SOURCE + relative[len(COMPONENT):], 'exact source snapshot mapping')
        body = members[group + '/' + row['snapshot']]
        need((len(body), sha(body)) == (row['bytes'], row['sha256']), 'every frozen component byte')
        if number == 4 and not relative.endswith('.md'):
            need((ROOT / relative).read_bytes() == body, 'final actual live source/header/CMake/patch: ' + relative)
    check_patch(members, group, report, number, upstream)
    expected_tools = TOOLS[:1] if number == 1 else TOOLS
    need([(norm(row['path']), row['bytes'], row['sha256']) for row in report['tools']] == expected_tools,
         'recorded actual native toolchain identities')
    expected = expected_commands(group, number)
    need([row['name'] for row in report['commands']] == [name for name, _ in expected], 'all actual compiler/lint commands')
    for row, (name, argv) in zip(report['commands'], expected):
        need([norm(arg) for arg in row['argv']] == argv and norm(row['cwd']) == BUILD + group and
             row['terminal'] is True and math.isfinite(row['elapsed_seconds']) and row['elapsed_seconds'] >= 0,
             'exact argv/flags and terminal process receipt')
        text = ''
        for stream in ('stdout', 'stderr'):
            pin = row[stream]; body = members[group + '/' + name + '.' + stream + '.log']
            need(pin['path'] == name + '.' + stream + '.log' and (len(body), sha(body)) == (pin['bytes'], pin['sha256']),
                 'exact process log identity')
            text += body.decode(errors='replace')
        need(diagnostics(text) == row['diagnostics'], 'recount every visible diagnostic')
        if number == 1:
            need(row['child_started'] is False and row['pid'] is None and row['returncode'] is None and
                 row['pre_child_error']['winerror'] == 623 and not report['objects'] and not report['stack_usage'] and
                 not row['stdout']['bytes'] and not row['stderr']['bytes'] and report['error']['type'] == 'RuntimeError',
                 'preserved WinError623 before compiler child, no native run invented')
            continue
        expected_exit = 1 if number == 2 and name in ('lx6-libbf', 'rv32-libbf') else 0
        need(row['child_started'] is True and type(row['pid']) is int and row['pid'] > 0 and
             row['returncode'] == expected_exit and not row.get('timed_out') and not row.get('pre_child_error'),
             'actual child PID and terminal exit')
        warning = 40 if name.endswith('-libbf') else 2 if name.endswith('-cutils') else 1 if name == 'lint-adapter' else 0
        need(row['diagnostics'] == dict(warnings=warning, errors=int(expected_exit == 1)), 'retained warning/error baseline')
        if expected_exit:
            need("passing argument 1 of 'bf_get_int32' from incompatible pointer type" in text and
                 '[-Wincompatible-pointer-types]' in text, 'stock source failed the real int32_t/int pointer ABI check')
        elif name.endswith('-version'):
            need(('20.1.1' if name == 'clang-tidy-version' else '15.2.0') in text, 'actual installed compiler version output')
    if number == 1:
        return dict(attempt=number, result='pre-child WinError623', objects=0, commands=1)
    need(report['immutable_sources'] is True, 'source set unchanged during actual profile')
    expected_objects = {(target, unit) for target in ('lx6', 'rv32') for unit in ('bigfloat', 'libbf', 'cutils', 'header')
                        if number != 2 or unit != 'libbf'}
    need({(row['target'], row['unit']) for row in report['objects']} == expected_objects and
         len(report['objects']) == len(expected_objects), 'complete successful object inventory')
    for row in report['objects']:
        need(row['path'] == row['target'] + '-' + row['unit'] + '.o', 'canonical target object path')
        body = members[group + '/' + row['path']]
        need((len(body), sha(body)) == (row['bytes'], row['sha256']) and row['elf_type'] == 1 and row['elf_class'] == 32,
             'retained actual ELF object identity')
        actual = elf(body, 94 if row['target'] == 'lx6' else 243)
        need(actual['machine'] == row['machine'], 'reported object machine agrees with bytes')
    need({(row['target'], row['unit']) for row in report['stack_usage']} == expected_objects, 'all successful .su records')
    for row in report['stack_usage']:
        body = members[group + '/' + row['path']]
        need((len(body), sha(body)) == (row['bytes'], row['sha256']), 'stack report identity')
        parsed = []
        for line in body.decode().splitlines():
            fields = line.split('\t'); need(len(fields) == 3 and fields[1].isdigit(), 'literal compiler .su row')
            parsed.append(dict(function=fields[0], bytes=int(fields[1]), kind=fields[2]))
        need(parsed == row['functions'] and max((x['bytes'] for x in parsed), default=0) == row['maximum_reported_bytes'],
             'all actual per-function stack figures, not whole-chain maxima')
    lint = report['lint']
    need(lint['warnings'] == 1 and lint['errors'] == lint['returncode'] == 0 and
         lint['translation_unit'] == 'bigfloat.c' and lint['upstream_translation_units_analyzed'] is False and
         lint['custom_suppressions_added'] is False, 'honest adapter-only lint scope')
    fixes = members[group + '/adapter-fixes.yaml']
    need(sha(fixes) == lint['exported_fixes']['sha256'] and len(fixes) == lint['exported_fixes']['bytes'] and
         b'bugprone-narrowing-conversions' in fixes and b'upstream/libbf.h' in fixes.replace(b'\\', b'/'),
         'one retained unchanged-header masked-flags diagnostic')
    return dict(attempt=number, result='stock compile errors' if number == 2 else 'PASS',
        commands=14, objects=len(expected_objects), adapter_header_warnings=0,
        creator_warnings_per_target=42, tidy_warnings=1, tidy_errors=0)


def verify():
    members = inventory()
    controller = (ROOT / 'tests/test-vorbis-bigfloat-profiles.py').read_bytes()
    need(sha(controller) == CONTROLLER_SHA, 'final trusted live controller remains unchanged')
    upstream, smoke = literal_assignment(controller, 'UPSTREAM'), literal_assignment(controller, 'SMOKE')
    need(literal_assignment(controller, 'FLAGS') == FLAGS and
         literal_assignment(controller, 'UNITS') == ('bigfloat.c', 'portable/libbf.c', 'upstream/cutils.c') and
         'static_assert(LIMB_BITS == 32' in smoke and 'static_assert(sizeof(void *) == 4' in smoke,
         'frozen profile semantics and compile-time ABI guard')
    groups = [check_group(members, group, number, upstream, smoke) for number, group in enumerate(GROUPS, 1)]
    controls = []
    sample = members[GROUPS[-1] + '/rv32-bigfloat.o']
    for name, offset, value in [('wrong_machine', 18, 94), ('float_abi', 36, 3)]:
        changed = bytearray(sample)
        struct.pack_into('<H' if offset == 18 else '<I', changed, offset, value)
        try:
            elf(changed, 243)
        except ValueError:
            controls.append(dict(name=name, rejected=True))
        else:
            raise ValueError('corrupted ELF control accepted')
    return dict(schema='vorbis-bigfloat-source-profiles-replay-v1', passed=True,
        archive_sha256=ARCHIVE_SHA, archive_bytes=891356, manifest_sha256=MANIFEST_SHA,
        members=202, decoded_bytes=3682502, omissions=0, groups=groups,
        final_controller_sha256=CONTROLLER_SHA, final_portable_sha256=PORTABLE[4][0],
        final_patch_sha256=PORTABLE[4][1], final_ELF32_objects=8, final_stack_reports=8,
        both_literal_replacements_verified=True, final_live_sources_verified=True,
        corruption_controls=controls, verifier_sha256=sha(Path(__file__).read_bytes()),
        archived_code_executed=False, archives_extracted=False, commands_reexecuted=0,
        source_only=True, linked=False, SDK_executed=False, QEMU_executed=False,
        MCU_arithmetic_executed=False, gain_qualified=False, production_selected=False,
        stack_scope='per-function compiler figures; no whole-chain peak or MCU-fit claim')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=FOLDER / 'source-profiles-replay.json')
    args = parser.parse_args(); output = args.output.resolve()
    need(output.is_relative_to(ROOT) and not output.exists(), 'fresh worktree replay output')
    try:
        result = verify()
    except BaseException as error:
        result = dict(passed=False, error_type=type(error).__name__, error=str(error),
                      verifier_sha256=sha(Path(__file__).read_bytes()), commands_reexecuted=0,
                      archived_code_executed=False, archives_extracted=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result), flush=True)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
