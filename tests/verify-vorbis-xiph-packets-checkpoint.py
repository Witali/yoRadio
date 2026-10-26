"""Verify saved packet-allocation evidence without executing archived code.

Reads the complete ZIP in place. Replays exact source transformations, owned
host receipts and every original PCM comparison. Does not extract files, start
processes, invoke an SDK/decoder, or qualify the separately deferred DSP gate.
"""
import argparse
import ast
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path, PurePosixPath

BASE = '897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
PORT = '908348db2d68684ddb21211b7f255e54a6fa95302567aa27bbc160cca8072894'
EARLIER_PORT = 'b0e77efb3a7a2783168ca33cbfe1898a0646345263a7e2bc7c8b7ece0a2299d5'
GENERATOR = '873472c0a30c955fa5d81528195ef71e4f476915b1ac8b64dd1d04dbae7f0251'
RUNNER = 'c74c7c485258f9e246f4bba202e07ad1d92a77ab5233978ffd35af4f69433ea0'
FIXTURE = '1f0d8a34f1afac3d75ecf71f0e4d21fe5c018a1ec587d9da6a1b3eae6d1247fb'
EARLIER_FIXTURE = 'a173dc5f245570d33aee331af01e89164bf919375ec073516e97ec5dde1cf4d5'
FIRST_FIXTURE = 'e88e96747b2aff5fed74a41845d12e0b19bd5f0dd0a955097673831aa07280b8'
CALLER = '229d009f45e8e7cb2dc6dc0aa68c2cc583c881d99eaeca58a4a467baf8444f3d'
SUPERVISOR = '70e2341aa100beb40b1a99399342422a8edd8bae85e7897b5a31d2a39f6ad05f'
MODEL = 'a12fcb6fea905027f9af4b1d1e5b5b561fa447f457d236cd5d004fd948b07883'
CASES_HEADER = '9e3baa93c34094ba50f2e837d23c7e600f7b81fe8e0894e979d3fe9b352c1a23'
CLANG = 'f7da288749fc81d990a8fbd9ee2a81927f98cc98148cbf853055b445cb045364'
CLANG_CONFIG = '27b1de038a07a9476ab195865192e9eebc8b58d036b0f359a6689caf2b7aed64'
PRIVATE_HEADERS = tuple('native_vorbis_xiph_' + name + '_error.h'
                        for name in ('header', 'dsp', 'comment', 'packet'))
PORTED_UNITS = {'upstream/libvorbis/lib/' + name + '.c' for name in
                ('block', 'sharedbook', 'codebook', 'floor0', 'floor1',
                 'res0', 'mapping0', 'info', 'mdct', 'synthesis')}
PORTED_UNITS.add('upstream/libogg/src/bitwise.c')
STEMS = ('alloc', 'packets', 'packets_host')
ENVIRONMENT = ['env',
               'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
               'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1']


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(path):
    value = path.replace('\\', '/')
    if re.match(r'^[A-Za-z]:/', value):
        value = '/mnt/' + value[0].lower() + value[2:]
    return value


def contained(name):
    path = PurePosixPath(name)
    return (name == path.as_posix() and path.parts and not path.is_absolute()
            and '..' not in path.parts and ':' not in name and '\\' not in name)


def owned_command(read, prefix, command, argv, status=0):
    name = command['name']
    raw = read(prefix + name + '.request.json')
    request = json.loads(raw)
    observed = command['supervisor']
    need(command['transport_exit'] == 0 and not command.get('forced_stop')
         and not command.get('forced_transport_stop'), 'normal transport ' + prefix + name)
    need(observed == json.loads(read(prefix + name + '.receipt.json'))
         and observed['state'] == 'terminal' and observed['child_returncode'] == status
         and all(observed[key] is True for key in
                 ('child_reaped', 'group_gone', 'new_session', 'final')),
         'actual owned terminal ' + prefix + name)
    need(type(observed['child_pid']) is int and observed['child_pid'] > 0
         and observed['child_pid'] == observed['owned_pgid'], 'owned process-group leader')
    need(sha(raw) == observed['request_sha256'] == command['request_sha256']
         and observed['nonce'] == command['nonce'] == request['nonce']
         and request['argv'] == argv and request['timeout'] == 60,
         'nonce-bound request ' + prefix + name)
    for stream in ('stdout', 'stderr'):
        need(sha(read(prefix + name + '.' + stream + '.log'))
             == command[stream + '_sha256'], 'actual command stream ' + prefix + name)


def materialization(read, names, prefix, report, port_sha):
    base = prefix + 'sources/components/native_vorbis_xiph/'
    port = prefix + 'sources/components/native_vorbis_xiph_port/'
    need(sha(read(base + 'component-manifest.json')) == BASE
         and sha(read(port + 'port-manifest.json')) == port_sha
         and sha(read(port + 'prepare.py')) == GENERATOR, 'pinned source identities ' + prefix)
    for folder, manifest_name, count in ((base, 'component-manifest.json', 116),
                                          (port, 'port-manifest.json', 76)):
        manifest = json.loads(read(folder + manifest_name))
        expected = set(manifest['files']) | {manifest_name}
        need(len(expected) == count and {name[len(folder):] for name in names
             if name.startswith(folder)} == expected, 'complete source inventory ' + folder)
        for name, digest in manifest['files'].items():
            need(contained(name) and sha(read(folder + name)) == digest,
                 'source manifest member ' + folder + name)
    original = json.loads(read(base + 'component-manifest.json'))
    adaptation = json.loads(read(port + 'port-manifest.json'))
    need(original['schema'] == 'native-vorbis-xiph-source-v1'
         and adaptation['schema'] == 'native-vorbis-xiph-resource-port-v1'
         and adaptation['base_manifest_sha256'] == BASE, 'release/port manifest schemas')
    expected = {'base/' + name: read(base + name)
                for name in (*original['files'], 'component-manifest.json')}
    changes = json.loads(read(port + 'edits.json'))
    need(changes['schema'] == 'native-vorbis-xiph-exact-edits-v1'
         and len(changes['edits']) == 33, 'all33 exact edits ' + prefix)
    modified, applied = {}, []
    for change in changes['edits']:
        source, before_name, after_name = (change[key] for key in ('source', 'before', 'after'))
        need(all(contained(name) for name in (source, before_name, after_name))
             and source in original['compile_sources'], 'compiled source deviation only')
        before, after = read(port + before_name), read(port + after_name)
        body = modified.get(source, read(base + source))
        need(before and after and before != after and body.count(before) == 1,
             'unique exact fragment ' + before_name)
        modified[source] = body.replace(before, after, 1)
        applied.append(dict(source=source, before=before_name, after=after_name,
                            before_sha256=sha(before), after_sha256=sha(after)))
    need(set(modified) == PORTED_UNITS, 'eleven modified C units only')
    expected.update({'ported/' + PurePosixPath(name).name: body
                     for name, body in modified.items()})
    for name in PRIVATE_HEADERS:
        expected['ported/' + name] = read(port + 'include/' + name)
    units = [dict(original=name, compiled='ported/' + PurePosixPath(name).name
                  if name in modified else 'base/' + name) for name in original['compile_sources']]
    record = dict(schema='native-vorbis-xiph-generated-port-v1', base_manifest_sha256=BASE,
                  port_manifest_sha256=port_sha, edits=applied, compiled_units=units,
                  files={name: sha(body) for name, body in sorted(expected.items())})
    need(len(expected) == 131 and len(units) == 22 and report['porting'] == record,
         'all132 generated files and22 compiled library units ' + prefix)
    expected['PORTING.json'] = (json.dumps(record, indent=2, sort_keys=True) + '\n').encode()
    generated = prefix + 'generated/'
    need({name[len(generated):] for name in names if name.startswith(generated)} == set(expected),
         'exact generated inventory ' + prefix)
    for name, body in expected.items():
        need(read(generated + name) == body, 'exact generated member ' + prefix + name)
    cmake = read(port + 'CMakeLists.txt').decode()
    match = re.search(r'set\(xiph_ported_units\s+([^)]*)\)', cmake)
    need(match is not None and set(match[1].split()) ==
         {PurePosixPath(name).stem for name in PORTED_UNITS if '/libvorbis/' in name},
         'CMake selects every ported Vorbis unit including synthesis')
    return record, modified


def pcm_result(read, prefix, report, successful):
    model = json.loads(read(prefix + 'sources/cases/cases.json'))
    need(sha(json.dumps(model, sort_keys=True, separators=(',', ':')).encode()) == MODEL
         and sha(read(prefix + 'sources/native/cases.h')) == CASES_HEADER,
         'unchanged complete original31 model/header ' + prefix)
    need(len(model['cases']) == 31 and len(model['relations']) == 14, 'complete numeric corpus')
    raw = read(prefix + 'pcm.bin')
    need(raw[:8] == b'XIPHRES1', 'raw capture signature ' + prefix)
    at, packets, total = 8, 0, 0

    def u32():
        nonlocal at
        need(at + 4 <= len(raw), 'whole raw capture field')
        value = struct.unpack_from('<I', raw, at)[0]
        at += 4
        return value

    need(u32() == 31, 'all original streams')
    measurements, targets = [], {}
    for index, case in enumerate(model['cases']):
        need([u32() for _ in range(4)] == [index, case['rate'], case['channels'], 14]
             and case['channels'] == 2, 'original format and all packets')
        pieces = []
        for p, frames in enumerate(case['frames']):
            count = frames * case['channels'] * 2
            need([u32() for _ in range(3)] == [p, frames, count], 'original packet length')
            body = raw[at:at + count]
            at += count
            need(len(body) == count, 'complete untrimmed packet samples')
            pieces.append(body)
            packets += 1
        actual = b''.join(pieces)
        reference = read(prefix + 'sources/cases/' + case['reference_path'])
        need(sha(reference) == case['reference_pcm_sha256']
             and len(actual) == len(reference) == case['pcm_bytes'], 'all independent PCM bytes')
        aa = struct.unpack('<' + 'h' * (len(actual) // 2), actual)
        bb = struct.unpack('<' + 'h' * (len(reference) // 2), reference)
        maximum = max((abs(a - b) for a, b in zip(aa, bb)), default=0)
        need(maximum <= 2, 'original fixed2-S16 bound without normalization')
        measurements.append(dict(id=case['id'], max_abs_error=maximum,
                                 pcm_bytes=len(actual), sha256=sha(actual)))
        targets[case['id']] = actual
        total += len(actual)
    need(at == len(raw) and packets == 434 and total == 738560,
         'complete capture, no missing/extra bytes')
    for relation in model['relations']:
        need(relation['kind'] in ('equal', 'different'), 'known original relation')
        ids = relation['cases']
        equal = all(targets[name] == targets[ids[0]] for name in ids[1:])
        need(equal == (relation['kind'] == 'equal'), 'all14 original exact relations')
    need(report['measurement_completed'] is True and report['cases'] == 31
         and report['packets'] == 434 and report['pcm_bytes'] == total
         and report['measurements'] == measurements and report['max_abs_error'] == 0
         and all(row['max_abs_error'] == 0 for row in measurements), 'saved numeric result replayed')
    if successful:
        need(report['capture_sha256'] == sha(raw) and report['relations'] == 14,
             'qualified raw capture identity')


def host_result(read, names, prefix, fixture_sha, port_sha, synthetic, successful=True):
    report = json.loads(read(prefix + 'report.json'))
    need(report['completed'] is True and report['passed'] is successful
         and report['sanitizers'] == ['address', 'undefined'], 'retained host outcome ' + prefix)
    for key in ('physical_device', 'target_executed', 'production_radio_integration',
                'general_OOM_qualified', 'general_16KiB_stack_bound',
                'deferred_DSP_fixture_executed', 'deferred_DSP_gate_resumed'):
        need(report[key] is False, 'limited independent packet scope ' + key)
    for pin in report['inputs'].values():
        need(contained(pin['snapshot']) and sha(read(prefix + pin['snapshot'])) == pin['sha256'],
             'frozen input ' + prefix + pin['snapshot'])
    need(sha(read(prefix + 'sources/runner.py')) == RUNNER
         and sha(read(prefix + 'sources/native/vorbis_xiph_packets.c')) == fixture_sha
         and sha(read(prefix + 'sources/native/vorbis_xiph_packets_host.c')) == CALLER,
         'actual independent packet callers ' + prefix)
    need(not re.search(rb'\b(?:xiph_dsp_tests|xiph_header_tests)\s*\(',
                       read(prefix + 'sources/native/vorbis_xiph_packets.c')),
         'deferred DSP fixture is not called')
    supervisor = read(prefix + 'supervisor.py')
    origin = ast.parse(read(prefix + 'sources/supervisor-origin.py'))
    assignments = [ast.literal_eval(node.value) for node in origin.body
                   if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                   and target.id == 'SUPERVISOR' for target in node.targets)]
    need(len(assignments) == 1 and supervisor.decode() == assignments[0]
         and sha(supervisor) == report['supervisor_sha256'] == SUPERVISOR,
         'frozen nonce-owned supervisor, parsed without execution')
    record, modified = materialization(read, names, prefix, report, port_sha)
    expected = (['compiler-version', 'compiler-machine']
                + ['compile-library-' + str(i).zfill(2) for i in range(22)]
                + ['compile-fixture-' + stem for stem in STEMS] + ['link', 'execute-arena', 'execute-synthetic']
                + ['execute-case-' + str(i).zfill(2) for i in range(31)] + ['execute-capture'])
    need([row['name'] for row in report['commands']] == expected and len(expected) == 62,
         'all62 actual host commands ' + prefix)
    for command in report['commands']:
        owned_command(read, prefix, command, command['child_argv'])
    commands = {row['name']: row['child_argv'] for row in report['commands']}
    first = commands['compile-library-00']
    source = first[first.index('-c') + 1]
    suffix = '/generated/' + record['compiled_units'][0]['compiled']
    need(source.endswith(suffix), 'actual generated compile directory')
    directory = source[:-len(suffix)]
    objects = []
    for index, unit in enumerate(record['compiled_units']):
        argv = commands['compile-library-' + str(index).zfill(2)]
        obj = directory + '/objects/library-' + str(index).zfill(2) + '.o'
        objects.append(obj)
        need(argv[argv.index('-c') + 1] == directory + '/generated/' + unit['compiled']
             and argv[argv.index('-o') + 1] == obj and argv.count('-include') == 1
             and argv[argv.index('-include') + 1] == directory + '/sources/native/vorbis_xiph_alloc_inject.h',
             'selected and injected library source ' + str(index))
    for stem in STEMS:
        argv = commands['compile-fixture-' + stem]
        obj = directory + '/objects/fixture-' + stem + '.o'
        objects.append(obj)
        need(argv[argv.index('-c') + 1] == directory + '/sources/native/vorbis_xiph_' + stem + '.c'
             and argv[argv.index('-o') + 1] == obj and '-include' not in argv,
             'non-injected fixture ' + stem)
    for name, argv in commands.items():
        if name.startswith('compile-'):
            need(argv[0] == 'gcc' and all(flag in argv for flag in
                 ('-UNDEBUG', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                  '-fno-fast-math', '-ffp-contract=off', '-fno-pie'))
                 and not any(flag.startswith('-DNDEBUG') for flag in argv),
                 'active assertions/sanitizers/arithmetic flags ' + name)
    need(commands['link'] == ['gcc', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
         '-no-pie', '-Wl,--gc-sections', *objects, '-lm', '-o', directory + '/packet-tests'],
         'complete host link recipe')
    invocations = [('execute-arena', ['--arena']), ('execute-synthetic', ['--synthetic'])]
    invocations += [('execute-case-' + str(i).zfill(2), ['--case', str(i)]) for i in range(31)]
    invocations += [('execute-capture', ['--capture', directory + '/pcm.bin'])]
    for name, arguments in invocations:
        need(commands[name] == [*ENVIRONMENT, directory + '/packet-tests', *arguments]
             and not read(prefix + name + '.stderr.log'), 'actual sanitizer run ' + prefix + name)
    arena = read(prefix + 'execute-arena.stdout.log').decode()
    text = read(prefix + 'execute-synthetic.stdout.log').decode()
    match = re.fullmatch(r'PACKET_SYNTHETIC_PASS scenarios=(\d+) fatal=(\d+) optional=(\d+) live=0 bytes=0\s*', text)
    need(arena.strip() == 'PACKET_ARENA_PASS scenarios=23 live=0 bytes=0'
         and match is not None and tuple(map(int, match.groups())) == synthetic,
         'all asserted focused packet markers ' + prefix)
    focused = report['focused']
    need(focused['arena'] == dict(scenarios=23, raw=arena)
         and focused['synthetic'] == dict(scenarios=synthetic[0], raw=text,
             fatal=synthetic[1], optional=synthetic[2]), 'focused report agrees with raw stream')
    sweeps = []
    for index in range(31):
        text = read(prefix + 'execute-case-' + str(index).zfill(2) + '.stdout.log').decode()
        match = re.fullmatch(r'PACKET_PASS case=(\d+) scenarios=(\d+) fatal=(\d+) optional=(\d+) live=0 bytes=0\s*', text)
        need(match is not None and int(match[1]) == index, 'whole packet sweep marker')
        sweeps.append(dict(case=index, scenarios=int(match[2]), fatal=int(match[3]), optional=int(match[4])))
    need(sweeps == report['sweeps'] and sum(row['scenarios'] for row in sweeps) == 27875
         and sum(row['fatal'] for row in sweeps) == 12930
         and sum(row['optional'] for row in sweeps) == 124, 'all original packet ordinal sweeps')
    need(read(prefix + 'execute-capture.stdout.log').decode().strip()
         == 'CAPTURE_PASS cases=31 packets=434 pcm_bytes=738560 live=0 bytes=0',
         'complete independent raw PCM capture marker')
    pcm_result(read, prefix, report, successful)
    if successful:
        need(report['packet_scenarios'] == 27875 and report['fatal_packet_refusals'] == 12930
             and report['optional_refusals'] == 124 and sha(read(prefix + 'packet-tests')) == report['binary_sha256']
             and 'error' not in report, 'qualified host counters and executable')
    else:
        need(report['error'] == "ValueError('all original/frozen inputs unchanged')",
             'first source-drift NONPASS remains a failure')
    return report, modified, commands, directory


def baseline_result(read, host, modified, commands):
    report = json.loads(read('baseline/report.json'))
    need(report['completed'] is True and report['expected_regression'] is True
         and report['deferred_DSP_fixture_executed'] is False
         and report['host_report_sha256'] == sha(read('host/report.json')),
         'baseline bound to final independent host build')
    port = 'host/sources/components/native_vorbis_xiph_port/'
    before, after = (read(port + 'edits/synthesis-pcm.' + side + '.c') for side in ('before', 'after'))
    current = modified['upstream/libvorbis/lib/synthesis.c']
    need(current.count(after) == 1, 'one packet PCM edit for regression reversal')
    preceding = current.replace(after, before, 1)
    need(preceding == read('baseline/synthesis.c')
         == read('host/sources/components/native_vorbis_xiph/upstream/libvorbis/lib/synthesis.c')
         and sha(preceding) == report['source_sha256'], 'only PCM edit reversed to official synthesis')
    rows = report['commands']
    need([row['name'] for row in rows] == ['compile-old-synthesis', 'link', 'execute'],
         'three real baseline commands')
    for index, row in enumerate(rows):
        owned_command(read, 'baseline/', row, row['argv'], 1 if index == 2 else 0)
    expected = list(commands['compile-library-08'])
    need(expected[expected.index('-c') + 1].endswith('/generated/ported/synthesis.c'),
         'actual synthesis library slot')
    source_index, object_index = expected.index('-c') + 1, expected.index('-o') + 1
    baseline_dir = rows[0]['argv'][source_index].rsplit('/', 1)[0]
    old_object = expected[object_index]
    expected[source_index], expected[object_index] = baseline_dir + '/synthesis.c', baseline_dir + '/synthesis.o'
    need(rows[0]['argv'] == expected, 'same compile recipe except synthesis source/object')
    expected = [baseline_dir + '/synthesis.o' if value == old_object else value for value in commands['link']]
    expected[expected.index('-o') + 1] = baseline_dir + '/packet-tests'
    need(rows[1]['argv'] == expected, 'all other final library and fixture objects reused')
    execute = rows[2]['argv']
    need(len(execute) == 6 and execute[:2] == ['python3', '-c']
         and execute[3:] == [baseline_dir + '/packet-tests', '--case', '0']
         and 'os.execve(sys.argv[1],sys.argv[1:]' in execute[2]
         and 'UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"' in execute[2],
         'actual expected-regression sanitizer invocation')
    error = read('baseline/execute.stderr.log').decode()
    need('/synthesis.c:82:15: runtime error: store to null pointer' in error
         and 'in vorbis_synthesis ' in error and 'in target_trial ' in error
         and not read('baseline/execute.stdout.log'), 'actual unchecked PCM NULL-store witness')
    need(sha(read('baseline/packet-tests')) == report['binary_sha256']
         and read('baseline/supervisor.py') == read('host/supervisor.py'),
         'retained baseline executable and same owned supervisor')


def lint_result(read, host, commands, directory):
    report = json.loads(read('lint/report.json'))
    need(report['completed'] is True and report['errors'] == 0
         and len(report['commands']) == 25 and report['host_report_sha256'] == sha(read('host/report.json')),
         'complete25-unit Clang analysis bound to final host sources')
    need('not an SDK GCC build, target execution or whole-radio lint' in report['scope']
         and len(report['tools']) == 1 and set(report['tools'].values()) == {CLANG}
         and sha(read('lint/clang-tidy.yaml')) == CLANG_CONFIG, 'explicit Clang-only scope/configuration')
    expected_sources = [commands['compile-library-' + str(i).zfill(2)][
                        commands['compile-library-' + str(i).zfill(2)].index('-c') + 1] for i in range(22)]
    expected_sources += [directory + '/sources/native/vorbis_xiph_' + stem + '.c' for stem in STEMS]
    warnings = errors = 0
    actual_inputs = {normalized(path): digest for path, digest in report['inputs'].items()}
    need(set(actual_inputs) == set(expected_sources), 'every actual Clang source input')
    for index, (command, source) in enumerate(zip(report['commands'], expected_sources)):
        argv = command['argv']
        need(normalized(argv[1]) == source and command['name'] == PurePosixPath(source).name
             and command['returncode'] == 0 and not command.get('forced_stop')
             and type(command['pid']) is int and command['pid'] > 0,
             'normal actual Clang invocation')
        need(all(flag in argv for flag in ('--target=xtensa-esp-elf', '-mcpu=esp32', '-UNDEBUG',
             '-fno-fast-math', '-ffp-contract=off', '-nostdinc'))
             and not any(flag.startswith('-DNDEBUG') for flag in argv), 'actual Xtensa arithmetic/assertion flags')
        need(('-include' in argv and normalized(argv[argv.index('-include') + 1])
             == directory + '/sources/native/vorbis_xiph_alloc_inject.h') if index < 22 else '-include' not in argv,
             'Clang allocator injection confined to22 library units')
        relative = source[len(directory) + 1:]
        need(source.startswith(directory + '/') and sha(read('host/' + relative)) == actual_inputs[source],
             'same frozen Clang input as qualified host source')
        stem = str(index).zfill(2) + '-' + PurePosixPath(source).stem
        streams = []
        for stream in ('stdout', 'stderr'):
            body = read('lint/' + stem + '.' + stream + '.log')
            need(sha(body) == command[stream + '_sha256'], 'all retained raw Clang streams')
            streams.append(body.decode('utf-8', errors='replace'))
        text = '\n'.join(streams)
        wc, ec = len(re.findall(r': warning:', text)), len(re.findall(r': (?:error|fatal error):', text))
        need(wc == command['warnings'] and ec == command['errors'], 'raw Clang diagnostic counts')
        warnings += wc
        errors += ec
    need(warnings == report['warnings'] == 308 and errors == report['errors'] == 0,
         'all308 warnings retained and zero Clang errors')
    return warnings


def outer_receipts(read):
    for name in ('host-initial', 'host-final', 'host-expanded', 'generation', 'baseline', 'lint'):
        receipt = json.loads(read('receipts/' + name + '.json'))
        need(receipt['status'] == 'TERMINAL' and type(receipt['owned_pid']) is int
             and receipt['owned_pid'] > 0 and receipt['returncode'] == (1 if name == 'host-initial' else 0),
             'original outer terminal including initial failure ' + name)
        for path, pin in receipt['logs'].items():
            body = read('receipts/' + normalized(path).rsplit('/', 1)[-1])
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'outer raw stream ' + name)
    need(b'all original/frozen inputs unchanged' in read('receipts/host-initial.stderr.log'),
         'initial source-identity rejection preserved')
    need(b'Ran 16 tests' in read('receipts/generation.stderr.log')
         and b'OK' in read('receipts/generation.stderr.log'), 'actual pure generation regression result')


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) and all(contained(name) for name in names),
             'unique contained archive members')
        cache = {}

        def read(name):
            if name not in cache:
                cache[name] = archive.read(name)
            return cache[name]

        inventory = json.loads(read('manifest.json'))
        need(inventory['schema'] == 'vorbis-xiph-packets-checkpoint-v1'
             and set(names) == set(inventory['files']) | {'manifest.json'}, 'complete archive inventory')
        for name, pin in inventory['files'].items():
            body = read(name)
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'archive member ' + name)
        first = host_result(read, names, 'host-first/', FIRST_FIXTURE, EARLIER_PORT,
                            (8520, 4008, 48), successful=False)
        earlier = host_result(read, names, 'host-before-controls/', EARLIER_FIXTURE, EARLIER_PORT,
                              (13140, 6192, 72))
        host, modified, commands, directory = host_result(read, names, 'host/', FIXTURE, PORT,
                                                         (13188, 6192, 72))
        for historical in (first, earlier):
            need(historical[1] == modified, 'same reviewed library changes in preceding host captures')
        baseline_result(read, host, modified, commands)
        warnings = lint_result(read, host, commands, directory)
        outer_receipts(read)
        need(read('sources/tests/test-vorbis-xiph-packets.py') == read('host/sources/runner.py'),
             'saved owned runner matches executed source')
        stop = json.loads(read('stop/target-preparation.json'))
        need(stop['status'] == 'aborted' and stop['reason_known'] is False
             and stop['native_executed'] is False and stop['cybersecurity_rejection_confirmed'] is False,
             'target-preparation abort retains unknown reason without inference')
        need(not any(name.startswith('native/') for name in names), 'no fabricated native runtime capture')
        return dict(verified_evidence=True, host_qualified=True, native_qualified=False,
                    deferred_DSP_gate_qualified=False, first_host_qualified=False,
                    initial_source_drift_preserved=True, preceding_host_qualified=True,
                    generated_files=132, host_commands=62, arena_scenarios=23,
                    packet_scenarios=27875, fatal_packet_refusals=12930, optional_refusals=124,
                    synthetic_scenarios=13188, synthetic_fatal_refusals=6192,
                    synthetic_optional_refusals=72, cases=31, packets=434,
                    pcm_bytes=738560, max_abs_error=0, relations=14,
                    baseline_NULL_store_reproduced=True, clang_units=25,
                    clang_warnings=warnings, clang_errors=0,
                    target_preparation_aborted=True, target_abort_reason_known=False,
                    production_radio_integration=False, physical_device=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive)))


if __name__ == '__main__':
    main()
