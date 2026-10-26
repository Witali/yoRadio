"""Replay the saved independent channel-scratch evidence without tool execution.

The archive is read in place, never extracted or executed. The reviewed local
packet verifier supplies pure source/host/PCM validation. Four source-only
Xtensa objects establish own-function compiler frames, not a task stack bound,
an SDK application build, native playback, or deferred amplitude/DSP coverage.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
import zipfile
from pathlib import Path, PurePosixPath

PACKET_VERIFIER = 'bf9dd0f148d29523520fbc733bda457b8727b365d0c48e09742cc53bc0b8d744'
PORT = '400e4c3f3b01fec11d7d051d3a0cef62cc7e0528eb71962bd6e015ab8bf95355'
FIXTURE = '1f0d8a34f1afac3d75ecf71f0e4d21fe5c018a1ec587d9da6a1b3eae6d1247fb'
FLOOR0 = '8f8e76aadf16e65eb4a6d243406a8f0bfc61796064f27202a8fd87ea92b8c23d'
GCC = '20e70278d1fa041c1305e0e70e6f35dde01b7eb21f2c7bbc0013456493a011a5'
PRECEDING = {
    'mapping-inverse.after.c': 'b1573988e9aae941e12a14cec001f067931172c599446f160a568deaac89c0fc',
    'residue01-inverse.after.c': '2aac1c489afae692777fa6643fc01ecbf9ad84cdddf09468b25a3719ab9efb8d',
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def trusted_packet_verifier(read):
    path = Path(__file__).resolve().with_name('verify-vorbis-xiph-packets-checkpoint.py')
    body = path.read_bytes()
    need(sha(body) == PACKET_VERIFIER and body == read('sources/tests/' + path.name),
         'reviewed local packet verifier and archived dependency have identical pinned bytes')
    spec = importlib.util.spec_from_file_location('trusted_local_packet_checkpoint', path)
    module = importlib.util.module_from_spec(spec)
    # Normal import of the trusted local dependency; never import archive data.
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def streams(read, prefix, command):
    parts = []
    need(command['returncode'] == 0 and not command.get('forced_stop')
         and type(command['pid']) is int and command['pid'] > 0,
         'normal source-only compiler/analysis terminal')
    for stream in ('stdout', 'stderr'):
        body = read(prefix + '.' + stream + '.log')
        need(sha(body) == command[stream + '_sha256'], 'actual retained compiler stream')
        parts.append(body.decode('utf-8', errors='replace'))
    return '\n'.join(parts)


def stack_result(read, helper, modified, host_directory):
    report = json.loads(read('stack/report.json'))
    need(report['completed'] is True and report['tool_sha256'] == GCC,
         'complete source-only Xtensa compiler observation')
    for key in ('target_runtime', 'SDK_build', 'production_build', 'physical_device'):
        need(report[key] is False, 'source-only stack scope ' + key)
    need('own-function stack frames' in report['scope']
         and 'No SDK app, link, emulator, target execution, whole-call-chain stack bound'
         in report['scope'], 'own compiler frames cannot qualify a call chain or production task')
    names = ['compiler-version', 'compiler-machine', 'compiler-macros',
             'compile-before-mapping0', 'compile-after-mapping0',
             'compile-before-res0', 'compile-after-res0']
    commands = report['commands']
    need([row['name'] for row in commands] == names, 'all seven actual source-only GCC commands')
    tool = commands[0]['argv'][0]
    need(commands[0]['argv'] == [tool, '--version']
         and commands[1]['argv'] == [tool, '-dumpmachine']
         and commands[2]['argv'] == [tool, '-dM', '-E', '-x', 'c', '-'],
         'actual compiler identity and architecture queries')
    for command in commands:
        streams(read, 'stack/' + command['name'], command)
    need(read('stack/compiler-machine.stdout.log').decode().strip() == 'xtensa-esp-elf',
         'observed Xtensa compiler triple')
    macros = read('stack/compiler-macros.stdout.log').decode()
    need(all(line in macros.splitlines() for line in
             ('#define __SIZEOF_POINTER__ 4', '#define __SIZEOF_LONG__ 4', '#define __XTENSA__ 1')),
         'observed32-bit Xtensa pointer/long ABI')
    includes = [host_directory + '/generated/' + suffix for suffix in
                ('base/upstream/libvorbis/include', 'base/upstream/libogg/include',
                 'base/platform', 'base/upstream/libvorbis/lib', 'ported')]
    common = [helper.normalized(tool), '-std=gnu17', '-O2', '-fno-inline',
              '-DHAVE_ALLOCA_H=1', '-D_GNU_SOURCE=1', '-fno-fast-math',
              '-ffp-contract=off', '-fstack-usage', *['-I' + name for name in includes]]
    sources = {}
    frames = {}
    input_pins = {helper.normalized(path): digest for path, digest in report['inputs'].items()}
    for unit, edit, function, before_bytes, after_bytes in (
            ('mapping0', 'mapping-inverse', 'mapping0_inverse', 96, 128),
            ('res0', 'residue01-inverse', '_01inverse', 112, 112)):
        current = modified['upstream/libvorbis/lib/' + unit + '.c']
        fragment_name = edit + '.after.c'
        after = read('host/sources/components/native_vorbis_xiph_port/edits/' + fragment_name)
        before = read('preceding/' + fragment_name)
        need(sha(before) == PRECEDING[fragment_name] and before != after
             and current.count(after) == 1, 'one reviewed channel-scratch fragment reversal')
        for version, body, size, kind in (
                ('before', current.replace(after, before, 1), before_bytes, 'dynamic'),
                ('after', current, after_bytes, 'static')):
            key = version + '-' + unit
            raw = read('stack/' + key + '.c')
            need(raw == body, 'whole source differs only by the corresponding scratch change')
            command = commands[names.index('compile-' + key)]
            argv = command['argv']
            normalized = []
            for value in argv:
                normalized.append('-I' + helper.normalized(value[2:])
                                  if value.startswith('-I') else helper.normalized(value))
            directory = helper.normalized(argv[argv.index('-c') + 1]).rsplit('/', 1)[0]
            source = directory + '/' + key + '.c'
            expected = [*common, '-c', source, '-o', directory + '/objects/' + key + '.o']
            need(normalized == expected and '-include' not in argv,
                 'identical source-only -O2/no-inline/stack-usage recipes')
            need(input_pins[source] == sha(raw), 'actual frozen source-only compile input')
            sources[source] = sha(raw)
            obj = read('stack/objects/' + key + '.o')
            need(len(obj) >= 52 and obj[:7] == b'\x7fELF\x01\x01\x01'
                 and struct.unpack_from('<H', obj, 16)[0] == 1
                 and struct.unpack_from('<H', obj, 18)[0] == 94,
                 'retained ELF32 little-endian Xtensa relocatable object')
            usage = read('stack/objects/' + key + '.su')
            matches = []
            for line in usage.decode().splitlines():
                fields = line.rsplit('\t', 2)
                need(len(fields) == 3 and fields[1].isdigit(), 'whole compiler stack-usage record')
                if fields[0].rsplit(':', 1)[-1] == function:
                    matches.append(dict(function=function, own_frame_bytes=int(fields[1]), kind=fields[2]))
            need(matches == [dict(function=function, own_frame_bytes=size, kind=kind)],
                 'actual own-function frame ' + key)
            observed = dict(**matches[0], source_sha256=sha(raw), object_sha256=sha(obj), usage_sha256=sha(usage))
            need(report['functions'][key] == observed, 'saved own-frame report matches raw source/object/.su')
            frames[key] = dict(function=function, own_frame_bytes=size, kind=kind)
    need(input_pins == sources and set(report['functions']) == set(frames),
         'exactly four source-only compiler inputs and function observations')
    return frames


def lint_result(read, helper, commands, directory):
    report = json.loads(read('lint/report.json'))
    need(report['completed'] is True and report['errors'] == 0
         and len(report['commands']) == 25
         and report['host_report_sha256'] == sha(read('host/report.json')),
         'complete25-unit Clang result bound to frozen host source')
    need('not an SDK GCC build, target execution or whole-radio lint' in report['scope']
         and len(report['tools']) == 1 and set(report['tools'].values()) == {helper.CLANG}
         and sha(read('lint/clang-tidy.yaml')) == helper.CLANG_CONFIG,
         'explicit Clang-only scope, tool and unchanged configuration')
    source_paths = [commands['compile-library-' + str(i).zfill(2)][
                    commands['compile-library-' + str(i).zfill(2)].index('-c') + 1] for i in range(22)]
    source_paths += [directory + '/sources/native/vorbis_xiph_' + stem + '.c' for stem in helper.STEMS]
    inputs = {helper.normalized(path): digest for path, digest in report['inputs'].items()}
    need(set(inputs) == set(source_paths), 'every actual Clang source input')
    warnings = errors = 0
    for index, (command, source) in enumerate(zip(report['commands'], source_paths)):
        argv = command['argv']
        need(helper.normalized(argv[1]) == source and command['name'] == PurePosixPath(source).name,
             'actual Clang unit in original compile order')
        need(all(flag in argv for flag in ('--target=xtensa-esp-elf', '-mcpu=esp32',
             '-UNDEBUG', '-fno-fast-math', '-ffp-contract=off', '-nostdinc'))
             and not any(flag.startswith('-DNDEBUG') for flag in argv),
             'actual Xtensa arithmetic and assertion flags')
        need(('-include' in argv and helper.normalized(argv[argv.index('-include') + 1])
             == directory + '/sources/native/vorbis_xiph_alloc_inject.h')
             if index < 22 else '-include' not in argv,
             'Clang allocator injection confined to22 library units')
        need(source.startswith(directory + '/') and sha(read('host/' + source[len(directory) + 1:]))
             == inputs[source], 'Clang analyzes the identical qualified frozen source')
        stem = str(index).zfill(2) + '-' + PurePosixPath(source).stem
        text = streams(read, 'lint/' + stem, command)
        wc = len(re.findall(r': warning:', text))
        ec = len(re.findall(r': (?:error|fatal error):', text))
        need(wc == command['warnings'] and ec == command['errors'], 'raw Clang diagnostic counts')
        warnings += wc
        errors += ec
    need(warnings == report['warnings'] == 316 and errors == report['errors'] == 0,
         'all316 warnings retained with zero Clang errors')
    return warnings


def outer_receipts(read, helper):
    for name in ('host', 'generation', 'stack', 'lint'):
        receipt = json.loads(read('receipts/' + name + '.json'))
        need(receipt['status'] == 'TERMINAL' and receipt['returncode'] == 0
             and type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0,
             'retained actual outer terminal ' + name)
        for path, pin in receipt['logs'].items():
            body = read('receipts/' + helper.normalized(path).rsplit('/', 1)[-1])
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'outer raw stream ' + name)
    need(b'Ran 16 tests' in read('receipts/generation.stderr.log')
         and b'OK' in read('receipts/generation.stderr.log'), 'pure source-generation regression result')


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) and all(
             name == PurePosixPath(name).as_posix() and PurePosixPath(name).parts
             and not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
             and ':' not in name and '\\' not in name for name in names), 'unique contained archive members')
        cache = {}

        def read(name):
            if name not in cache:
                cache[name] = archive.read(name)
            return cache[name]

        manifest = json.loads(read('manifest.json'))
        need(manifest['schema'] == 'vorbis-xiph-channels-checkpoint-v1'
             and set(names) == set(manifest['files']) | {'manifest.json'}, 'complete archive inventory')
        for name, pin in manifest['files'].items():
            body = read(name)
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'archive member ' + name)
        helper = trusted_packet_verifier(read)
        host, modified, commands, directory = helper.host_result(
            read, names, 'host/', FIXTURE, PORT, (19268, 9232, 72))
        need(read('sources/tests/test-vorbis-xiph-packets.py') == read('host/sources/runner.py'),
             'unchanged owned packet runner matches executed snapshot')
        need(sha(read('host/sources/components/native_vorbis_xiph_port/edits/floor0-inverse1.after.c')) == FLOOR0,
             'the separately deferred amplitude source is unchanged')
        frames = stack_result(read, helper, modified, directory)
        warnings = lint_result(read, helper, commands, directory)
        outer_receipts(read, helper)
        stop = json.loads(read('audit/amplitude-stop.json'))
        need(stop['status'] == 'deferred' and stop['cybersecurity_review_stopped'] is True
             and stop['files_created'] is False and stop['wide_amplitude_qualified'] is False,
             'separate amplitude review stop remains deferred and unqualified')
        need(not any(name.startswith('native/') for name in names), 'no invented native runtime evidence')
        return dict(verified_evidence=True, host_qualified=True, native_qualified=False,
                    deferred_DSP_gate_qualified=False, wide_amplitude_qualified=False,
                    max255_runtime_qualified=False, generated_files=132, host_commands=62,
                    arena_scenarios=23, packet_scenarios=27875, fatal_packet_refusals=12930,
                    optional_refusals=124, synthetic_scenarios=19268,
                    synthetic_fatal_refusals=9232, synthetic_optional_refusals=72,
                    total_scenarios=47166, cases=31, packets=434, pcm_bytes=738560,
                    max_abs_error=0, relations=14, clang_units=25,
                    clang_warnings=warnings, clang_errors=0,
                    source_only_xtensa_commands=7, source_only_xtensa_objects=4,
                    own_function_frames=frames, general_task_stack_bound=False,
                    SDK_application_build=False, native_runtime_executed=False,
                    production_radio_integration=False, physical_device=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive)))


if __name__ == '__main__':
    main()
