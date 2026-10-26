"""Verify saved unsigned-rate evidence without extracting or running its code.

Only hash-pinned trusted local modules supply pure receipt/PCM/protocol readers.
Archived generators, compilers, SDK tools and decoder programs are never run.
The native qualification is identification/comment metadata and granule_time;
it does not qualify audio packets, the old deferred gates or physical output.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import re
import struct
import sys
import zipfile
from pathlib import Path, PurePosixPath

BASE = '897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
HOST_PORT = '5eaf91336853646962c77e729d3acb95b668ea64f29bd07607fe11234c2551e5'
PORT = 'b9cc3c829a816ef8f1a283e23a5b9cc1a45214e9eee541e85560858ed70b0104'
GENERATOR = 'ab969373a3b105c44cdce1d74fdc83dae66ec0576565aee089a2f489cd3ab6b5'
FIRST_FIXTURE = '5d809a0b2704034626ed0f3561b7d231c7a01138e11e96aeaf87996856a23fb4'
FIXTURE = '3f843a6d41b0dfa717f992fe96e341e467df2eb60f8c0c8c777fc16973411276'
RATE_RUNNER = 'b72d9d14c79582a9819f9d3dc541faaafbb621b9fa6057c4edde25bed1fea433'
PACKET_RUNNER = 'd29949a368e2b891d5841a3a37f0aaa3a36285e7827404a57a83ae50d6527f36'
PACKET_FIXTURE = '1f0d8a34f1afac3d75ecf71f0e4d21fe5c018a1ec587d9da6a1b3eae6d1247fb'
PACKET_READER = 'bf9dd0f148d29523520fbc733bda457b8727b365d0c48e09742cc53bc0b8d744'
CONTROLLER = 'd212e0c2c45cbca5c9bca8363e5eadade3874d5eca9da092cfe2fa5196a7e2e0'
ABI_RUNNER = '5c0dc723d0d6e125c5fa13023bff5c32acd5942fc2654815fb241f9fb93879e4'
NATIVE_MAIN = '536856b8e7322590fcd58f00c4ed5d2eecd819691a9801e2659970a7939239d3'
NATIVE_LAYOUT = '2359ce108c4caaf715bf9f5de60adfd26a9f4a89d40decc70257a900f63311e4'
QEMU = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
SDK = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
GCC = '20e70278d1fa041c1305e0e70e6f35dde01b7eb21f2c7bbc0013456493a011a5'
SDK_PYTHON = '0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14'
POWERSHELL = '362a356ce7f0940ec74f73a8fc2c990a2cc24a38a11c90bbd8eca947110ad139'
NINJA = '68865c3276d449d746cea5065fdec2baf755d7813e161ab04205b0907b2629b8'
CLANG = 'f7da288749fc81d990a8fbd9ee2a81927f98cc98148cbf853055b445cb045364'
PUBLIC = ('codec.h', 'vorbisenc.h', 'vorbisfile.h')
PRIVATE = tuple('native_vorbis_xiph_' + name + '_error.h'
                for name in ('header', 'dsp', 'comment', 'packet'))
PUBLIC_SOURCE = 'upstream/libvorbis/include/vorbis/codec.h'
PORTED = {'upstream/libvorbis/lib/' + name + '.c' for name in
          ('block', 'sharedbook', 'codebook', 'floor0', 'floor1', 'res0',
           'mapping0', 'info', 'mdct', 'synthesis')}
PORTED.add('upstream/libogg/src/bitwise.c')
ENV = ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
       'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1']
FORBIDDEN_CALL = re.compile(rb'\b(?:vorbis_synthesis(?:_init|_blockin|_trackonly)?|'
                            rb'vorbis_dsp_clear|vorbis_block_init|xiph_dsp_tests|'
                            rb'xiph_header_tests)\s*\(')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(name):
    path = PurePosixPath(name)
    return (name == path.as_posix() and path.parts and not path.is_absolute()
            and '..' not in path.parts and ':' not in name and '\\' not in name)


def norm(value):
    return str(value).replace('\\', '/').rstrip('/')


def local_reader(read, name, digest):
    path = Path(__file__).resolve().with_name(name)
    body = path.read_bytes()
    need(sha(body) == digest and body == read('sources/tests/' + name),
         'hash-pinned trusted local reader matches its frozen copy ' + name)
    spec = importlib.util.spec_from_file_location('trusted_local_' + path.stem.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def source_inputs(read, prefix, report):
    for pin in report['inputs'].values():
        need(canonical(pin['snapshot']), 'contained frozen source path')
        body = read(prefix + pin['snapshot'])
        need(sha(body) == pin['sha256'] and ('bytes' not in pin or len(body) == pin['bytes']),
             'actual frozen source ' + prefix + pin['snapshot'])


def tree(read, names, folder, manifest_name, pin, count):
    raw = read(folder + manifest_name)
    need(sha(raw) == pin, 'pinned complete manifest ' + folder)
    manifest = json.loads(raw)
    expected = set(manifest['files']) | {manifest_name}
    need(len(expected) == count and {name[len(folder):] for name in names
         if name.startswith(folder)} == expected, 'complete source inventory ' + folder)
    bodies = {name: read(folder + name) for name in expected}
    for name, digest in manifest['files'].items():
        need(canonical(name) and sha(bodies[name]) == digest, 'source member ' + folder + name)
    return manifest, bodies


def materialization(read, names, prefix, generated, port_pin, recorded):
    base, originals = tree(read, names, prefix + 'sources/components/native_vorbis_xiph/',
                           'component-manifest.json', BASE, 116)
    port, deviations = tree(read, names, prefix + 'sources/components/native_vorbis_xiph_port/',
                            'port-manifest.json', port_pin, 80)
    need(port['base_manifest_sha256'] == BASE and sha(deviations['prepare.py']) == GENERATOR,
         'unchanged generator/base identities')
    edits = json.loads(deviations['edits.json'])
    need(edits['schema'] == 'native-vorbis-xiph-exact-edits-v1' and len(edits['edits']) == 35,
         'all35 declared exact edits')
    modified, applied = {}, []
    for edit in edits['edits']:
        source, before_name, after_name = (edit[key] for key in ('source', 'before', 'after'))
        need(source in base['compile_sources'] or source == PUBLIC_SOURCE,
             'only declared C units and the reviewed public header change')
        before, after = deviations[before_name], deviations[after_name]
        body = modified.get(source, originals[source])
        need(before and after and before != after and body.count(before) == 1,
             'unique exact source transformation ' + before_name)
        modified[source] = body.replace(before, after, 1)
        applied.append(dict(source=source, before=before_name, after=after_name,
                            before_sha256=sha(before), after_sha256=sha(after)))
    need(set(modified) == PORTED | {PUBLIC_SOURCE}, 'eleven C units and one public header')
    wanted = {'base/' + name: body for name, body in originals.items()}
    wanted.update({'ported/' + PurePosixPath(name).name: body for name, body in modified.items()
                   if name != PUBLIC_SOURCE})
    public_headers = []
    for name in PUBLIC:
        origin = 'upstream/libvorbis/include/vorbis/' + name
        destination = 'ported/include/vorbis/' + name
        wanted[destination] = modified.get(origin, originals[origin])
        public_headers.append(dict(original=origin, generated=destination, modified=origin in modified))
    for name in PRIVATE:
        wanted['ported/' + name] = deviations['include/' + name]
    units = [dict(original=name, compiled='ported/' + PurePosixPath(name).name
                  if name in modified else 'base/' + name) for name in base['compile_sources']]
    need(len(units) == 22, 'same complete22 library sources')
    record = dict(schema='native-vorbis-xiph-generated-port-v1', base_manifest_sha256=BASE,
                  port_manifest_sha256=port_pin, edits=applied, compiled_units=units,
                  public_headers=public_headers, files={name: sha(body) for name, body in sorted(wanted.items())})
    need(record == recorded and json.loads(read(generated + 'PORTING.json')) == record,
         'independently reconstructed generated record')
    wanted['PORTING.json'] = (json.dumps(record, indent=2, sort_keys=True) + '\n').encode()
    need(len(wanted) == 135 and {name[len(generated):] for name in names
         if name.startswith(generated)} == set(wanted), 'complete135 generated files')
    for name, body in wanted.items():
        need(read(generated + name) == body, 'exact generated bytes ' + generated + name)
    cmake = deviations['CMakeLists.txt']
    need(b'INCLUDE_DIRS "${xiph_generated}/ported/include"' in cmake
         and b'"${xiph_generated}/base/upstream/libvorbis/include"' not in cmake,
         'only matching owned public Vorbis headers are exported')
    need(b'#define NATIVE_VORBIS_XIPH_RATE_API 1' in modified[PUBLIC_SOURCE]
         and b'typedef unsigned long native_xiph_sample_rate_t;' in modified[PUBLIC_SOURCE]
         and b'#if ULONG_MAX == 0xffffffffUL' in modified[PUBLIC_SOURCE], 'reviewed conditional source type')
    return record, modified, deviations


def host(read, names, helper, prefix, stems, runner_pin, fixture_pin):
    report = json.loads(read(prefix + 'report.json'))
    need(report['completed'] is True and report['passed'] is True
         and report['sanitizers'] == ['address', 'undefined'], 'successful host sanitizer result ' + prefix)
    for key in ('physical_device', 'production_radio_integration', 'deferred_DSP_gate_resumed'):
        need(report[key] is False, 'host qualification scope ' + key)
    source_inputs(read, prefix, report)
    need(sha(read(prefix + 'sources/runner.py')) == runner_pin
         and sha(read(prefix + 'sources/native/vorbis_xiph_' + stems[1] + '.c')) == fixture_pin,
         'actual owned host caller identities')
    record, modified, deviations = materialization(read, names, prefix, prefix + 'generated/',
                                                   HOST_PORT, report['porting'])
    metadata = stems[1] == 'rate'
    runs = [('execute', [])] if metadata else [('execute-arena', ['--arena']), ('execute-synthetic', ['--synthetic'])]
    if not metadata:
        runs += [('execute-case-' + str(i).zfill(2), ['--case', str(i)]) for i in range(31)]
        runs += [('execute-capture', None)]
    expected = ['compiler-version', 'compiler-machine'] + ['compile-library-' + str(i).zfill(2) for i in range(22)]
    expected += ['compile-fixture-' + stem for stem in stems] + ['link'] + [name for name, _ in runs]
    need([row['name'] for row in report['commands']] == expected, 'all actual host command stages ' + prefix)
    commands = {}
    for row in report['commands']:
        helper.owned_command(read, prefix, row, row['child_argv'], 0)
        commands[row['name']] = row['child_argv']
    first = commands['compile-library-00']
    suffix = '/generated/' + record['compiled_units'][0]['compiled']
    source = first[first.index('-c') + 1]
    need(source.endswith(suffix), 'host generated compile root')
    directory = source[:-len(suffix)]
    includes = ['-I' + directory + '/' + part for part in
                ('generated/ported/include', 'generated/base/upstream/libogg/include',
                 'generated/base/platform', 'generated/base/upstream/libvorbis/lib',
                 'generated/ported', 'sources/native')]
    objects = []
    for index, unit in enumerate(record['compiled_units']):
        argv = commands['compile-library-' + str(index).zfill(2)]
        obj = directory + '/objects/library-' + str(index).zfill(2) + '.o'
        objects.append(obj)
        need(argv[argv.index('-c') + 1] == directory + '/generated/' + unit['compiled']
             and argv[argv.index('-o') + 1] == obj and argv.count('-include') == 1
             and argv[argv.index('-include') + 1] == directory + '/sources/native/vorbis_xiph_alloc_inject.h',
             'selected host library source and allocator injection')
        if metadata:
            dep = read(prefix + 'objects/library-' + str(index).zfill(2) + '.d')
            pin = report['library_dependencies'][unit['original']]
            need(sha(dep) == pin['sha256'] and '-MMD' in argv, 'actual host header dependency')
            headers = re.findall(r'\S+/vorbis/codec\.h', dep.decode())
            need(headers == pin['codec_header']
                 and all(path == directory + '/generated/ported/include/vorbis/codec.h' for path in headers)
                 and bool(headers) == ('/libvorbis/' in unit['original']), 'owned codec header on every Vorbis unit')
    for stem in stems:
        argv = commands['compile-fixture-' + stem]
        obj = directory + '/objects/fixture-' + stem + '.o'
        objects.append(obj)
        need(argv[argv.index('-c') + 1] == directory + '/sources/native/vorbis_xiph_' + stem + '.c'
             and argv[argv.index('-o') + 1] == obj and '-include' not in argv, 'non-injected host fixture')
    for name, argv in commands.items():
        if name.startswith('compile-'):
            need(argv[0] == 'gcc' and [arg for arg in argv if arg.startswith('-I')] == includes
                 and all(flag in argv for flag in ('-UNDEBUG', '-fsanitize=address,undefined',
                     '-fno-sanitize-recover=all', '-fno-fast-math', '-ffp-contract=off', '-fno-pie'))
                 and not any(arg.startswith('-DNDEBUG') for arg in argv), 'host assertions/arithmetic/header flags')
    binary = 'rate-tests' if metadata else 'packet-tests'
    need(commands['link'] == ['gcc', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
         '-no-pie', '-Wl,--gc-sections', *objects, '-lm', '-o', directory + '/' + binary], 'whole host link recipe')
    need(sha(read(prefix + binary)) == report['binary_sha256'], 'saved actual host executable')
    for name, arguments in runs:
        if arguments is None:
            arguments = ['--capture', directory + '/pcm.bin']
        need(commands[name] == [*ENV, directory + '/' + binary, *arguments]
             and not read(prefix + name + '.stderr.log'), 'actual host invocation without sanitizer diagnostics')
    if metadata:
        for key in ('raw_header_decoder_executed', 'identification_header_executed', 'comment_header_executed'):
            need(report[key] is True, 'identification/comment metadata executed')
        for key in ('setup_header_executed', 'dsp_executed', 'packet_decoder_executed', 'full_decoder_qualified'):
            need(report[key] is False, 'metadata-only host limit ' + key)
        need(report['scenarios'] == 13492 and report['library_units'] == 22 and report['fixture_units'] == 3
             and read(prefix + 'execute.stdout.log').decode().strip() == 'RATE_PASS scenarios=13492 live=0 bytes=0',
             'complete asserted metadata host result')
        fixture = read(prefix + 'sources/native/vorbis_xiph_rate.c')
        need(not FORBIDDEN_CALL.search(fixture) and b'No setup header' in fixture
             and b'info->rate > 0' in fixture and b'ORIGINAL_OFFSET(codec_setup)' in fixture,
             'reviewed metadata caller and ABI assertions')
        if fixture_pin == FIXTURE:
            need(b'vorbis_granule_time(&state, INT64_MIN)' in fixture
                 and b'vorbis_granule_time(&state, -2)' in fixture, 'final unsigned-granule regression checks')
    else:
        for key in ('target_executed', 'general_OOM_qualified', 'general_16KiB_stack_bound', 'deferred_DSP_fixture_executed'):
            need(report[key] is False, 'finite packet host scope ' + key)
        need(read(prefix + 'execute-arena.stdout.log').decode().strip() == 'PACKET_ARENA_PASS scenarios=23 live=0 bytes=0',
             'arena marker')
        need(read(prefix + 'execute-synthetic.stdout.log').decode().strip()
             == 'PACKET_SYNTHETIC_PASS scenarios=19268 fatal=9232 optional=72 live=0 bytes=0', 'synthetic marker')
        sweeps = []
        for index in range(31):
            match = re.fullmatch(r'PACKET_PASS case=(\d+) scenarios=(\d+) fatal=(\d+) optional=(\d+) live=0 bytes=0\s*',
                                 read(prefix + 'execute-case-' + str(index).zfill(2) + '.stdout.log').decode())
            need(match is not None and int(match[1]) == index, 'whole original packet sweep marker')
            sweeps.append(dict(case=index, scenarios=int(match[2]), fatal=int(match[3]), optional=int(match[4])))
        need(sweeps == report['sweeps'] and sum(row['scenarios'] for row in sweeps) == 27875
             and sum(row['fatal'] for row in sweeps) == 12930 and sum(row['optional'] for row in sweeps) == 124,
             'all original packet allocation ordinals')
        need(report['packet_scenarios'] == 27875 and report['fatal_packet_refusals'] == 12930
             and report['optional_refusals'] == 124 and read(prefix + 'execute-capture.stdout.log').decode().strip()
             == 'CAPTURE_PASS cases=31 packets=434 pcm_bytes=738560 live=0 bytes=0', 'whole original PCM capture')
        helper.pcm_result(read, prefix, report, True)
    return report, record, modified, deviations, commands, directory


def equivalence(read, names, previous):
    report = json.loads(read('equivalence/report.json'))
    raw = read('equivalence/current-port-manifest.json')
    need(report['completed'] is True and report['implementation_files_unchanged'] is True
         and report['host_port_manifest_sha256'] == HOST_PORT and sha(raw) == report['current_port_manifest_sha256'] == PORT
         and report['changed_files'] == ['README.md', 'port-manifest.json'], 'declared documentation-only reseal')
    current = dict(previous)
    current['README.md'] = read('equivalence/current-README.md')
    current['port-manifest.json'] = raw
    old = b'same base-library units, types, floating configuration'
    need(previous['README.md'].count(old) == 1 and current['README.md'] == previous['README.md'].replace(
         old, b'same base-library units, floating configuration', 1), 'only stale README type claim changes')
    need(set(report['files']) == set(current) == set(previous), 'all-file equivalence inventory')
    manifest = json.loads(raw)
    need(set(manifest['files']) == set(current) - {'port-manifest.json'}, 'complete current port inventory')
    for name, body in current.items():
        need(report['files'][name] == dict(before_sha256=sha(previous[name]), after_sha256=sha(body)),
             'independent before/after file proof ' + name)
        if name != 'port-manifest.json':
            need(manifest['files'][name] == sha(body), 'current resealed source identity ' + name)
        if name not in report['changed_files']:
            need(body == previous[name], 'every implementation/header byte is unchanged')
    return current


def abi(read, helper, host_report, directory):
    report = json.loads(read('abi/report.json'))
    need(report['completed'] is True and report['source_only'] is True and report['target_runtime'] is False
         and report['positive_probes'] == 12 and report['negative_header_selection_probes'] == 2
         and report['all_public_orders'] is True and report['host_report_sha256'] == sha(read('host/report.json'))
         and sha(read('abi/runner.py')) == ABI_RUNNER, 'complete owned C/C++ host ABI probe campaign')
    expected_names = []
    for language in ('c', 'cpp'):
        expected_names += [language + '-version', language + '-machine']
        expected_names += ['compile-' + language + '-' + str(i) for i in range(6)]
        expected_names += ['compile-' + language + '-original-first']
    need([row['name'] for row in report['commands']] == expected_names, 'all18 ABI commands')
    commands = {row['name']: row for row in report['commands']}
    for row in report['commands']:
        status = 1 if row['name'].endswith('-original-first') else 0
        need(row['expected_exit'] == status, 'explicit negative/positive compile expectation')
        helper.owned_command(read, 'abi/', row, row['argv'], status)
    orders = list(itertools.permutations(PUBLIC))
    need(len(report['probes']) == 12, 'all12 distinct successful ABI probes')
    for index, probe in enumerate(report['probes']):
        language, number = ('c' if index < 6 else 'cpp'), index % 6
        stem = language + '-' + str(number)
        extension = '.c' if language == 'c' else '.cc'
        body = read('abi/' + stem + extension)
        need(probe['name'] == stem and probe['language'] == language
             and probe['order'] == list(orders[number]) and sha(body) == probe['source_sha256']
             and re.findall(rb'#include "vorbis/([^\"]+)"', body) == [name.encode() for name in orders[number]]
             and all(('OFFSET(' + field + ')').encode() in body for field in
                 ('version', 'channels', 'rate', 'bitrate_upper', 'bitrate_nominal', 'bitrate_lower', 'bitrate_window', 'codec_setup'))
             and b'ASSERT(sizeof(vorbis_info)==sizeof(struct original_info_layout)' in body
             and b'SAME(native_xiph_sample_rate_t,unsigned long)' in body, 'reviewed ABI/type/entry-order source')
        argv = commands['compile-' + stem]['argv']
        need(argv[0] == ('gcc' if language == 'c' else 'g++')
             and all(flag in argv for flag in ('-Wall', '-Wextra', '-Werror', '-MMD'))
             and argv[argv.index('-c') + 1].endswith('/' + stem + extension)
             and [arg for arg in argv if arg.startswith('-I')] == ['-I' + directory + '/' + part for part in
                 ('generated/ported/include', 'generated/base/upstream/libogg/include', 'generated/base/platform')],
             'actual C/C++ probe compile flags and public include order')
        obj, dep = read('abi/objects/' + stem + '.o'), read('abi/objects/' + stem + '.d')
        need(sha(obj) == probe['object_sha256'] and sha(dep) == probe['dependency_sha256'], 'retained probe object/dependency')
        headers = re.findall(r'\S+/vorbis/codec\.h', dep.decode())
        need(headers == probe['codec_header'] and headers and all(path == directory +
             '/generated/ported/include/vorbis/codec.h' for path in headers), 'actual owned ABI header dependency')
    for language in ('c', 'cpp'):
        row = commands['compile-' + language + '-original-first']
        includes = [arg for arg in row['argv'] if arg.startswith('-I')]
        need(includes[:2] == ['-I' + directory + '/generated/base/upstream/libvorbis/include',
             '-I' + directory + '/generated/ported/include'], 'real original-header-first control')
        error = read('abi/compile-' + language + '-original-first.stderr.log')
        extension = '.c' if language == 'c' else '.cc'
        control = read('abi/' + language + '-original-first' + extension)
        positive = read('abi/' + language + '-0' + extension)
        suffix = b'#include <limits.h>' + positive.split(b'#include <limits.h>', 1)[1]
        need(control == b'#define OV_EXCLUDE_STATIC_CALLBACKS 1\n#include "vorbis/vorbisfile.h"\n' + suffix,
             'negative control retains the same ABI assertions and only selects the original sibling header first')
        need(b'Owned rate header not selected' in error and b'error:' in error,
             'actual negative control rejects mismatched public header')


def native(read, names, controller, modified, current):
    report = json.loads(read('native/report.json'))
    for key in ('completed', 'passed', 'metadata_qualified', 'identification_rate_qualified',
                'ILP32_runtime_qualified', 'identification_header_executed', 'comment_header_executed',
                'whole_module_compiled', 'source_inputs_unchanged', 'exact_source_port_validated'):
        need(report[key] is True, 'complete native metadata gate ' + key)
    for key in ('setup_header_executed', 'packet_decoder_executed', 'decoder_executed', 'dsp_tests_executed',
                'full_decoder_qualified', 'dsp_gate_qualified', 'packet_target_gate_qualified',
                'wide_amplitude_qualified', 'encoder_rate_qualified', 'convenience_library_qualified',
                'production_firmware', 'production_radio_integration', 'physical_device'):
        need(report[key] is False, 'native metadata-only limitation ' + key)
    need(report['target'] == 'esp32' and report['sdk_revision'] == SDK and report['expected_cases'] == 13492
         and report['source_sha256'] == {'base-manifest': BASE, 'port-manifest': PORT, 'fixture': FIXTURE, 'qemu': QEMU},
         'pinned metadata campaign identities')
    source_inputs(read, 'native/', report)
    need(read('native/sources/controller.py') == read('sources/tests/run-vorbis-xiph-rate-qemu.py'),
         'actual frozen trusted controller')
    porting_path = report['generated_porting']['path']
    need(canonical(porting_path) and porting_path.endswith('/PORTING.json') and sha(read('native/' + porting_path)) == report['generated_porting']['sha256'],
         'actual native generated record')
    generated = 'native/' + porting_path.rsplit('/', 1)[0] + '/'
    record, actual_modified, deviations = materialization(read, names, 'native/', generated, PORT,
                                                         report['generated_porting']['record'])
    need(actual_modified == modified and deviations == current, 'same implementation and matching current documentation')
    for key in ('project_sources', 'generated_sources', 'build_outputs'):
        for name, digest in report[key].items():
            need(canonical(name) and sha(read('native/' + name)) == digest, 'retained native ' + key + ' ' + name)
    required_outputs = {'build/vorbis_xiph_rate_qemu.elf', 'build/vorbis_xiph_rate_qemu.map', 'qemu-flash.bin',
        'sdkconfig', 'elf-header.bin', 'sdk-child.json', 'sdk-build.stdout.log', 'sdk-build.stderr.log',
        'build/bootloader/bootloader.bin', 'build/partition_table/partition-table.bin', 'build/vorbis_xiph_rate_qemu.bin',
        'build/compile_commands.json', 'build/project_description.json', 'build/flasher_args.json',
        'build/CMakeCache.txt', 'build/config/sdkconfig.h', 'build/build.ninja', 'build/CMakeFiles/rules.ninja'}
    need(required_outputs <= report['build_outputs'].keys()
         and set(report['generated_sources']) <= report['build_outputs'].keys()
         and set(report['stack_usage']['paths']) <= report['build_outputs'].keys(), 'complete declared native output set')
    main = read('native/project/main/main.c')
    need(sha(main) == NATIVE_MAIN and sha(read('native/project/main/layout_probe.h')) == NATIVE_LAYOUT
         and sha(read('native/project/main/vorbis_xiph_rate.c')) == FIXTURE
         and not FORBIDDEN_CALL.search(main) and not FORBIDDEN_CALL.search(read('native/project/main/vorbis_xiph_rate.c')),
         'reviewed metadata-only native caller and ABI assertions')
    command_names = ['sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after']
    need([row['name'] for row in report['commands']] == command_names, 'all nine actual native commands')
    commands = {}
    for row in report['commands']:
        need(row['state'] == 'complete' and row['exit_status'] == 0 and not row['timed_out']
             and not row['interrupted'] and type(row['pid']) is int and row['pid'] > 0
             and not any(key in row for key in ('tree_stop_returncode', 'tree_stop_error')), 'normal native command terminal')
        for stream in ('stdout', 'stderr'):
            need(sha(read('native/' + row['name'] + '.' + stream + '.log')) == row[stream + '_sha256'],
                 'actual native raw stream')
        commands[row['name']] = row['argv']
    for name in ('sdk-head', 'sdk-head-after'):
        need(read('native/' + name + '.stdout.log').decode().strip() == SDK, 'actual SDK revision')
    for name in ('sdk-clean', 'sdk-clean-after'):
        need(not read('native/' + name + '.stdout.log').strip(), 'actual clean SDK snapshot')
    child = json.loads(read('native/sdk-child.json').decode('utf-8-sig'))
    need(child == report['sdk_child'] and child['exit_status'] == 0 and type(child['pid']) is int
         and child['pid'] > 0 and child['argv'][-1] == 'build'
         and all(value in child['argv'] for value in ('IDF_TARGET=esp32', 'XIPH_BASE_MANIFEST_SHA256=' + BASE,
             'XIPH_PORT_MANIFEST_SHA256=' + PORT, 'XIPH_RATE_FIXTURE_SHA256=' + FIXTURE, 'XIPH_RATE_CASES=13492')),
         'actual SDK child and complete rate build identity')
    for path, digest in report['tools'].items():
        need(re.fullmatch('[0-9a-f]{64}', digest) is not None, 'recorded external tool hash')
    tools = {norm(path).casefold(): digest for path, digest in report['tools'].items()}
    for stage, digest in (('build', POWERSHELL), ('merge', SDK_PYTHON), ('dependencies', NINJA), ('symbols', GCC)):
        need(tools[norm(commands[stage][0]).casefold()] == digest, 'pinned actual external tool for ' + stage)
    qargv = commands['qemu']
    need(report['tools'][qargv[0]] == QEMU and qargv[1:8] == ['-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2', '-L']
         and all(flag in qargv for flag in ('-no-reboot', '-snapshot'))
         and qargv[qargv.index('-display') + 1] == 'none' and qargv[qargv.index('-monitor') + 1] == 'none'
         and qargv[qargv.index('-serial') + 1] == 'stdio' and qargv[qargv.index('-nic') + 1] == 'none'
         and norm(qargv[-1]).endswith('/qemu-flash.bin,if=mtd,format=raw'), 'actual isolated QEMU recipe')
    log = read('native/qemu.stdout.log').decode('utf-8', errors='replace').replace('\r\n', '\n')
    log += '\n' + read('native/qemu.stderr.log').decode('utf-8', errors='replace')
    observed = controller.validate_log(log, BASE, PORT, FIXTURE, 13492)
    need(observed == report['observed'], 'strict raw five-event native metadata protocol')
    config = read('native/sdkconfig').decode().replace('\r\n', '\n')
    for name in ('CONFIG_ESP_TASK_WDT_EN', 'CONFIG_ESP_TASK_WDT_INIT', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0',
                 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1', 'CONFIG_COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE'):
        need(re.search(r'^' + name + '=y$', config, re.M), 'watchdog/idle/assertions remain enabled ' + name)
    need('CONFIG_FREERTOS_UNICORE=y' not in config and 'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ=240' in config,
         'actual dual-core metadata profile')
    elf = read('native/build/vorbis_xiph_rate_qemu.elf')
    need(elf[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', elf, 18)[0] == report['elf_machine'] == 94,
         'actual ELF32 little-endian Xtensa application')
    need(read('native/elf-header.bin') == elf[:len(read('native/elf-header.bin'))], 'saved actual ELF header')
    need(len(read('native/qemu-flash.bin')) == 4 * 1024 * 1024, 'complete isolated metadata flash image')
    recipe = json.loads(read('native/build/flasher_args.json'))
    need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'DIO40 metadata profile')
    need({int(offset, 0) for offset in recipe['flash_files']} == {4096, 32768, 65536}, 'metadata boot/image offsets')
    rows = report['compile_rows']
    probes = tuple('probe_' + str(i) + '.' + ext for ext in ('c', 'cpp') for i in range(6))
    need(report['public_header_probes'] == list(probes), 'all12 native public-header probes')
    unit_names = [row['original'] for row in record['compiled_units']]
    expected_names = ['fixture', 'vorbis_xiph_alloc.c', 'vorbis_xiph_rate.c', *probes, *unit_names]
    need(list(rows) == expected_names and len(rows) == 37
         and len({norm(row['output']).casefold() for row in rows.values()}) == 37,
         'all37 distinct actual sources and objects')
    database = json.loads(read('native/build/compile_commands.json'))
    build_directory = norm(rows['fixture']['directory'])
    directory = build_directory.rsplit('/', 1)[0]
    gen_directory = directory + '/' + porting_path.rsplit('/', 1)[0]
    wanted_sources = {'fixture': directory + '/project/main/main.c'}
    wanted_sources.update({name: directory + '/project/main/' + name for name in ('vorbis_xiph_alloc.c', 'vorbis_xiph_rate.c', *probes)})
    wanted_sources.update({row['original']: gen_directory + '/' + row['compiled'] for row in record['compiled_units']})
    dependencies = {}
    current_object = None
    for line in read('native/dependencies.stdout.log').decode().splitlines():
        match = re.fullmatch(r'(.+): #deps [0-9]+,.*\(VALID\)', line)
        if match:
            current_object = norm(match[1]).casefold()
            need(current_object not in dependencies, 'one actual dependency block per object')
            dependencies[current_object] = set()
        elif line.startswith('    ') and current_object is not None:
            dependencies[current_object].add(norm(line.strip()).casefold())
    need(len(dependencies) == 37, 'all37 actual ninja dependency records')
    for name, row in rows.items():
        source = wanted_sources[name]
        need(norm(row['file']) == source and [item for item in database if norm(item['file']) == source] == [row],
             'unique actual database row ' + name)
        command = norm(row['command'])
        driver = command.split(' ', 1)[0].strip('"').casefold()
        need(tools[driver] == GCC, 'pinned actual Xtensa C/C++ compiler driver')
        need(all(flag in command for flag in ('-fno-fast-math', '-ffp-contract=off', '-fstack-usage'))
             and '-DNDEBUG' not in command, 'native arithmetic/stack/assertion flags')
        injection = directory + '/project/main/vorbis_xiph_alloc_inject.h'
        need((injection in command and '-include' in command) if name in unit_names else injection not in command,
             'native injection confined to22 library units')
        need(('g++.exe' in command) if name.endswith('.cpp') else 'gcc.exe' in command, 'actual C/C++ driver')
        deps = dependencies[norm(row['output']).casefold()]
        need(source.casefold() in deps and (gen_directory + '/base/upstream/libvorbis/include/vorbis/codec.h').casefold() not in deps,
             'actual source dependency without shadowing original public header')
        if name not in ('vorbis_xiph_alloc.c', 'upstream/libogg/src/bitwise.c', 'upstream/libogg/src/framing.c'):
            need((gen_directory + '/ported/include/vorbis/codec.h').casefold() in deps, 'actual owned codec header dependency')
        if name in probes:
            for public in PUBLIC:
                need((gen_directory + '/ported/include/vorbis/' + public).casefold() in deps, 'all public entry headers are owned')
            body = read('native/project/main/' + name)
            order = list(itertools.permutations(PUBLIC))[int(name.split('_')[1].split('.')[0])]
            need(re.findall(rb'#include "vorbis/([^\"]+)"', body) == [part.encode() for part in order]
                 and b'#include "layout_probe.h"' in body, 'native C/C++ entry-order source')
    for name in PRIVATE:
        need(any((gen_directory + '/ported/' + name).casefold() in deps for deps in dependencies.values()), 'private interface dependency')
    usage = report['stack_usage']
    need(len(usage['paths']) == 22 and 'not a full call-tree' in usage['scope'], 'compiler frame scope stays bounded')
    actual_frames = []
    for name in usage['paths']:
        for line in read('native/' + name).decode().splitlines():
            site, size, qualifier = line.rsplit('\t', 2)
            actual_frames.append(dict(function=site.rsplit(':', 1)[-1], bytes=int(size), qualifier=qualifier, path=name))
    need(actual_frames == usage['rows'], 'raw native compiler frame observations')
    warnings = [line for stream in ('stdout', 'stderr') for line in read('native/sdk-build.' + stream + '.log').decode(
        'utf-8', errors='replace').splitlines() if re.search(r'\bwarning:', line)]
    need(warnings == report['build_warning_lines'], 'all SDK build warning lines retained')
    symbols = read('native/symbols.stdout.log').decode().replace('\r\n', '\n')
    for name in controller.PUBLIC:
        need(re.search(r'\b' + name + r'$', symbols, re.M), 'linked metadata function ' + name)
    need(not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_\w+$', symbols, re.M), 'no vendor decoder symbols')
    map_bytes = read('native/build/vorbis_xiph_rate_qemu.map')
    need(b'libesp_audio_codec.a' not in map_bytes and b'libnative_vorbis_xiph.a' not in map_bytes,
         'no vendor/second baseline archive')
    return observed


def lint(read, host_directory):
    report = json.loads(read('lint/report.json'))
    need(report['completed'] is True and report['warnings'] == 306 and report['errors'] == 0
         and report['host_report_sha256'] == sha(read('host/report.json')) and len(report['commands']) == 25,
         'complete25-unit Clang campaign')
    host_report = json.loads(read('host/report.json'))
    expected_sources = ['generated/' + row['compiled'] for row in host_report['porting']['compiled_units']]
    expected_sources += ['sources/native/vorbis_xiph_' + stem + '.c' for stem in ('alloc', 'rate', 'rate_host')]
    need(len(report['inputs']) == 25, 'all25 distinct Clang source inputs')
    warnings = errors = 0
    for index, row in enumerate(report['commands']):
        argv = row['argv']
        source = norm(argv[1])
        need(report['tools'][argv[0]] == CLANG and row['returncode'] == 0 and not row.get('forced_stop')
             and all(flag in argv for flag in ('--target=xtensa-esp-elf', '-mcpu=esp32', '-nostdinc', '-UNDEBUG',
                                              '-fno-fast-math', '-ffp-contract=off')), 'actual Clang Xtensa flags and tool')
        relative = source.split('/vorbis-xiph-rate-host-20261026-02/', 1)[1]
        need(relative == expected_sources[index] and sha(read('host/' + relative)) == report['inputs'][argv[1]],
             'same complete ordered final Clang compilation units')
        need(any(norm(arg).endswith('/generated/ported/include') for arg in argv if arg.startswith('-I'))
             and not any(norm(arg).endswith('/base/upstream/libvorbis/include') for arg in argv if arg.startswith('-I')),
             'Clang uses matching owned public headers')
        stem = str(index).zfill(2) + '-' + PurePosixPath(source).stem
        parts = []
        for stream in ('stdout', 'stderr'):
            body = read('lint/' + stem + '.' + stream + '.log')
            need(sha(body) == row[stream + '_sha256'], 'actual raw Clang stream')
            parts.append(body.decode('utf-8', errors='replace'))
        text = '\n'.join(parts)
        wc, ec = len(re.findall(r': warning:', text)), len(re.findall(r': (?:error|fatal error):', text))
        need(wc == row['warnings'] and ec == row['errors'], 'actual Clang diagnostic counts')
        warnings += wc
        errors += ec
    need(warnings == 306 and errors == 0, 'all306 warnings retained with zero errors')


def receipts(read, helper):
    for name in ('host-metadata', 'host-metadata-final', 'host-packets', 'host-abi',
                 'generation', 'generation-final', 'protocol', 'lint', 'native'):
        receipt = json.loads(read('receipts/' + name + '.json'))
        need(receipt['status'] == 'TERMINAL' and receipt['returncode'] == 0
             and type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0, 'actual outer terminal ' + name)
        for path, pin in receipt['logs'].items():
            body = read('receipts/' + helper.normalized(path).rsplit('/', 1)[-1])
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'outer raw stream ' + name)
    for name, count in (('generation', 17), ('generation-final', 17), ('protocol', 7)):
        text = read('receipts/' + name + '.stderr.log')
        need(('Ran ' + str(count) + ' tests').encode() in text and b'OK' in text, 'actual pure protocol/generation result')


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) and all(canonical(name) for name in names), 'unique contained archive members')
        cache = {}

        def read(name):
            if name not in cache:
                cache[name] = archive.read(name)
            return cache[name]

        inventory = json.loads(read('manifest.json'))
        need(inventory['schema'] == 'vorbis-xiph-rate-checkpoint-v1'
             and set(names) == set(inventory['files']) | {'manifest.json'}, 'complete archive inventory')
        for name, pin in inventory['files'].items():
            body = read(name)
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'saved archive member ' + name)
        helper = local_reader(read, 'verify-vorbis-xiph-packets-checkpoint.py', PACKET_READER)
        controller = local_reader(read, 'run-vorbis-xiph-rate-qemu.py', CONTROLLER)
        first = host(read, names, helper, 'host-first/', ('alloc', 'rate', 'rate_host'), RATE_RUNNER, FIRST_FIXTURE)
        final = host(read, names, helper, 'host/', ('alloc', 'rate', 'rate_host'), RATE_RUNNER, FIXTURE)
        packets = host(read, names, helper, 'packets/', ('alloc', 'packets', 'packets_host'), PACKET_RUNNER, PACKET_FIXTURE)
        need(first[2] == final[2] == packets[2] and first[3] == final[3] == packets[3], 'same executed implementation across host campaigns')
        current = equivalence(read, names, final[3])
        abi(read, helper, final[0], final[5])
        observed = native(read, names, controller, final[2], current)
        lint(read, final[5])
        receipts(read, helper)
        need(read('sources/tests/test-vorbis-xiph-rate.py') == read('host/sources/runner.py')
             and read('sources/tests/test-vorbis-xiph-packets.py') == read('packets/sources/runner.py'),
             'current owned runners match their actually executed snapshots')
        return dict(verified_evidence=True, host_metadata_qualified=True, native_metadata_qualified=True,
                    ILP32_rate_qualified=True, metadata_scenarios=13492, packet_host_total_scenarios=47166,
                    original_packet_scenarios=27875, synthetic_scenarios=19268, arena_scenarios=23,
                    generated_files=135, exact_edits=35, changed_C_units=11, public_overlay_headers=3,
                    C_CPP_host_probes=12, expected_negative_header_probes=2, native_compile_rows=37,
                    C_CPP_native_probes=12, native_protocol_events=5, original_cases=31, original_packets=434,
                    original_pcm_bytes=738560, max_abs_error=0, original_bound=2, relations=14,
                    clang_units=25, clang_warnings=306, clang_errors=0, native_observed=observed,
                    native_audio_PCM_qualified=False, setup_runtime_qualified=False, DSP_gate_qualified=False,
                    packet_target_gate_qualified=False, wide_amplitude_qualified=False, encoder_rate_qualified=False,
                    convenience_library_qualified=False, production_radio_integration=False, physical_device=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive)))


if __name__ == '__main__':
    main()
