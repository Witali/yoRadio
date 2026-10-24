"""Offline floor1 checkpoint: verify saved bytes and finite PCM; launch no tools."""
from pathlib import Path, PurePosixPath
import ast
import gzip
import hashlib
import io
import json
import re
import struct
import wave

ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT / 'manifest.json').read_text())
assert M['schema'] == 'floor1-render-evidence-v1'
assert M['complete'] and M['collection_sources_unchanged'] and M['predeclared_max_abs_error'] == 2
assert not any(M[x] for x in ('full_G6_qualified', 'production_radio_integration', 'physical_device'))
FILES, GROUPS = M['files'], M['groups']
CACHE, IDENTITY_ONLY = {}, set()


def norm(name):
    return str(name).replace('\\', '/').rstrip('/')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(name):
    value, checkout = norm(name), norm(M['checkout_root'])
    if value.casefold().startswith(checkout.casefold() + '/'):
        return value[len(checkout) + 1:]
    return value


for alias, row in FILES.items():
    assert norm(alias) == alias and not PurePosixPath(alias).is_absolute()
    assert '..' not in PurePosixPath(alias).parts
    assert re.fullmatch('[0-9a-f]{64}', row['sha256'])
    assert row['object'] == 'objects/' + row['sha256'] + '.gz'
    if row['object'] not in CACHE:
        CACHE[row['object']] = gzip.decompress((ROOT / row['object']).read_bytes())
    data = CACHE[row['object']]
    assert len(data) == row['bytes'] and sha(data) == row['sha256'], alias
assert {p.relative_to(ROOT).as_posix() for p in (ROOT / 'objects').rglob('*') if p.is_file()} == set(CACHE)
assert M['logical_files'] == len(FILES) and M['unique_objects'] == len(CACHE)
assert M['selected_uncompressed_bytes'] == sum(row['bytes'] for row in FILES.values())
for name in ('verifier.py', 'README.md', '.gitattributes'):
    assert (ROOT / name).read_bytes() == CACHE[FILES[name]['object']], name
assert (ROOT / '.gitattributes').read_bytes() == b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n'
assert {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(CACHE) | {
    'manifest.json', 'verifier.py', 'README.md', '.gitattributes'}
for row in M['omissions']:
    assert row['reason'] and type(row['bytes']) is int and row['bytes'] >= 0
    assert re.fullmatch('[0-9a-f]{64}', row['sha256'])
assert len({row['path'] for row in M['omissions']}) == len(M['omissions'])


def raw(alias):
    return CACHE[FILES[alias]['object']]


def obj(alias):
    return json.loads(raw(alias))


def archived(original):
    rel = relative(original)
    candidates = ['canonical/' + rel]
    for group, origin in GROUPS.items():
        origin = norm(origin)
        if rel == origin or rel.startswith(origin + '/'):
            candidates.append(group + rel[len(origin):])
    found = [name for name in candidates if name in FILES]
    assert found, ('missing archived input', original)
    assert len({sha(raw(name)) for name in found}) == 1
    return found[0]


def bound(group, path, digest, size=None):
    alias = group + '/' + norm(path)
    assert '..' not in PurePosixPath(alias).parts
    if alias in FILES:
        data = raw(alias)
        assert sha(data) == digest and (size is None or len(data) == size), alias
        return data
    original = norm(GROUPS[group]) + '/' + norm(path)
    matches = [x for x in M['omissions'] if norm(x['path']) == original]
    assert len(matches) == 1 and matches[0]['sha256'] == digest, ('unbound omission', alias)
    assert size is None or matches[0]['bytes'] == size
    IDENTITY_ONLY.add(original)
    return None


def closure(group):
    report = obj(group + '/report.json')
    for row in report.get('inputs', {}).values():
        bound(group, row['snapshot'], row['sha256'], row.get('bytes'))
    for key in ('build_outputs', 'variant_sources', 'project_sources', 'generated_inputs_before_cmake'):
        for name, digest in report.get(key, {}).items():
            bound(group, name, digest)
    for cmd in report.get('commands', []):
        if 'sha256' in cmd:
            bound(group, cmd['name'] + '.log', cmd['sha256'])
        for stream in ('stdout', 'stderr'):
            digest = cmd.get(stream + '_sha256')
            if digest is not None:
                bound(group, cmd.get(stream, cmd['name'] + '.' + stream + '.log'), digest)
    return report


REQUIRED = {'positions-corpus', 'slopes-corpus', 'cyd-positions', 'c3-positions',
            'cyd-slopes', 'c3-slopes', 'cyd-old-tail', 'host02', 'historical-host01',
            'references-original-nonpass', 'baseline-cyd', 'baseline-c3',
            'positions-check', 'slopes-check', 'historical-positions-check01',
            'historical-slopes-check01', 'commands', 'raw', 'raw-control', 'config'}
assert REQUIRED <= set(GROUPS)
REPORTS = {group: closure(group) for group in REQUIRED - {'positions-corpus', 'slopes-corpus', 'commands'}}
for group, digest in (
        ('references-original-nonpass', '183f3b8cfabe81021e0309a02de5674cfd264800a64d01ba2e75f0c7f0c26204'),
        ('baseline-cyd', '753c53375b29c4135f9c37844996c979c8d0f5bea8b509ec0d3a2d96840f764b'),
        ('baseline-c3', '304e2b136ea69fa627b1eeab6792877cc3bd8a05e901a8e57d5a370c4182979f'),
        ('host02', '1c28c191d293fd4685147fb8a0468b31f3ab3099c1ef1ad0f9e91aa7d67b9f8c'),
        ('historical-host01', '766f8f714c7c0906ce73371f954917f95ff357750dafa97eee96a77d6496a693')):
    assert sha(raw(group + '/report.json')) == digest


def corpus(group):
    manifest, matrix = obj(group + '/manifest.json'), obj(group + '/matrix.json')
    assert [x['expected_valid'] for x in matrix['cases']] == [True] * 8 + [False] * 6
    assert matrix['valid_raw_packet_count'] == 112 and matrix['expected_valid_pcm_bytes'] == 225280
    for row in manifest['files']:
        assert len(raw(group + '/' + row['path'])) == row['bytes']
        assert sha(raw(group + '/' + row['path'])) == row['sha256']
    assert {x.removeprefix(group + '/') for x in FILES if x.startswith(group + '/')} == {
        row['path'] for row in manifest['files']} | {'manifest.json'}
    return matrix


MATRICES = {kind: corpus(kind + '-corpus') for kind in ('positions', 'slopes')}
for kind, generator_sha in (('positions', '0248784f9baeb0c959bd1c63f56b958600d06c16f896c2c920b2cc88c442ca21'),
                            ('slopes', '835158eac4bb5a6eebaa43a2ec45b331b93943f045d82e41abe31bf389dab37b')):
    manifest = obj(kind + '-corpus/manifest.json')
    assert manifest['generator_sha256'] == generator_sha == sha(raw('canonical/tests/vorbis_format_corpus/generate_floor1_' + kind + '.py'))
    assert manifest['helper']['sha256'] == sha(raw('canonical/tests/vorbis_block_matrix/generate_minimal.py')) == '8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1'
HEADER_SHA = '3b24c3980895de79c2b3cd6460e31182d7fbc5192d474bc7e88be1fe9f917b4b'
for platform in ('esp32-cyd2usb', 'esp32c3-oled'):
    assert sha(raw('canonical/idf/' + platform + '-native/main/vorbis_repair/floor1_render.h')) == HEADER_SHA
for name, digest in (('floor1.c', '5dc87534496c039df8683b9d6149fc0c1ac6938c87a7e1b303d3a53b642330e4'),
                     ('misc.h', 'f15d78fc4c49a95df854701aea3fd527ed35597767075d4eba48b80cab70ec66'),
                     ('floor_lookup.c', 'dfc670f7648f94ae7beb25ca542380f42eba3dbf8e180e479648f20fb07bbaba')):
    assert sha(raw('public-tremor/' + name)) == digest
PCM = {}
for group in ('cyd-positions', 'c3-positions', 'cyd-slopes', 'c3-slopes',
              'cyd-old-tail', 'baseline-cyd', 'baseline-c3'):
    r = REPORTS[group]
    baseline = group.startswith('baseline-')
    kind = 'slopes' if group.endswith('slopes') else 'positions'
    cases = MATRICES[kind]['cases']
    core = 0 if group.startswith('c3-') or group == 'baseline-c3' else 1
    assert r['completed'] and r['elf_machine'] == (243 if core == 0 else 94)
    assert r['target'] == ('esp32c3' if core == 0 else 'esp32')
    assert not any(r[x] for x in ('full_G6_qualified', 'production_radio_integration', 'physical_device'))
    assert r['passed'] is baseline
    if not baseline:
        assert r['renderer'] == 'on' and r['target_capture_completed']
        assert not r['numerical_reference_qualified'] and r['result'] == 'RENDER_CAPTURED'
        assert sha(raw(group + '/sources/main/vorbis_repair/floor1_render.h')) == HEADER_SHA
        for name in r['variant_sources']:
            part = norm(name).removeprefix('variant/')
            before, after = raw(group + '/sources/main/' + part), raw(group + '/' + norm(name))
            if group == 'cyd-old-tail' and part == 'vorbis_repair/floor1_render.h':
                anchor = b'out[j] = repair_floor1_multiply(out[j], repair_floor1_from_db[ly]);'
                assert before.count(anchor) == 1
                assert after == before.replace(anchor, b'out[j] = repair_floor1_multiply(out[j], ly * 32768);', 1)
            else:
                assert before == after
    assert r['control'] == ('old-tail' if group == 'cyd-old-tail' else None)
    assert all(c['state'] == 'complete' and c['exit_status'] == 0 and type(c['pid']) is int and c['pid'] > 0 for c in r['commands'])
    assert {'build', 'symbols', 'merge', 'qemu', 'sdk-head', 'sdk-clean', 'sdk-head-after', 'sdk-clean-after'} <= {c['name'] for c in r['commands']}
    log = raw(group + '/qemu.stdout.log').decode(errors='replace').replace('\r\n', '\n')
    stderr = raw(group + '/qemu.stderr.log').decode(errors='replace')
    assert not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|FLOOR1_FAILURE', log + stderr)
    assert log.count('FLOOR1_CONTROLLED_STOP') == 1
    assert re.findall(r'^FLOOR1_START coordinator=0 decoder=(\d+)$', log, re.M) == [str(core)]
    summary = ('8', '6', '112', '225280', str(core))
    assert re.findall(r'^FLOOR1_COMPLETE accepted=(\d+) rejected=(\d+) packets=(\d+) pcm=(\d+) core=(\d+)$', log, re.M) == [summary]
    assert r['observed']['summary'] == list(summary)
    marker = 'original_exact=1' if baseline else 'renderer_repair=1'
    accepted = re.findall(r'^FLOOR1_ACCEPT case=(\d+) name=(\S+) packets=14 pcm=28160 ' + marker + r' core=(\d+)$', log, re.M)
    rejected = re.findall(r'^FLOOR1_REJECT case=(\d+) name=(\S+) result=-1 handle=0 core=(\d+)$', log, re.M)
    opens = re.findall(r'^FLOOR1_OPEN case=(\d+) result=(-?\d+) handle=([01])$', log, re.M)
    assert accepted == [(str(i), cases[i]['id'], str(core)) for i in range(8)]
    assert rejected == [(str(i), cases[i]['id'], str(core)) for i in range(8, 14)]
    assert opens == [(str(i), '0', '1') if i < 8 else (str(i), '-1', '0') for i in range(14)]
    assert [list(x) for x in accepted] == r['observed']['accepted']
    assert [list(x) for x in rejected] == r['observed']['rejected']
    assert [list(x) for x in opens] == r['observed']['opens']
    rows = re.findall(r'^FLOOR1_PCM case=(\d+) packet=(\d+) consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)$', log, re.M)
    assert [(int(c), int(p)) for c, p, *_ in rows] == [(c, p) for c in range(8) for p in range(14)]
    pins = {norm(k): v for k, v in r['observed']['pcm'].items()}
    assert set(pins) == {f'pcm/{c}.s16le' for c in range(8)}
    PCM[group] = {}
    for c in range(8):
        parts = []
        for _, p, consumed, count, hexdump in rows[c * 14:(c + 1) * 14]:
            p = int(p); data = bytes.fromhex(hexdump)
            assert len(data) == int(count) == cases[c]['expected_packet_bytes'][p]
            assert int(consumed) == cases[c]['offsets'][p + 1] - cases[c]['offsets'][p]
            parts.append(data)
        data = b''.join(parts)
        assert data == raw(group + f'/pcm/{c}.s16le') and len(data) == 28160 and any(data)
        assert sha(data) == pins[f'pcm/{c}.s16le']
        PCM[group][c] = data


def metrics(a, b):
    assert len(a) == len(b) and len(a) % 2 == 0
    errors = [abs(x[0] - y[0]) for x, y in zip(struct.iter_unpack('<h', a), struct.iter_unpack('<h', b))]
    return dict(samples=len(errors), max_abs_error=max(errors, default=0), over_bound=sum(e > 2 for e in errors), allowed=2)


for kind in ('positions', 'slopes'):
    r = REPORTS[kind + '-check']
    assert r['completed'] and r['passed'] and r['finite_renderer_qualified'] and r['both_architectures_qualified']
    assert r['predeclared_max_abs_error'] == 2 and not r['failures']
    assert r['corpus_kind'] == kind and r['corpus_manifest_sha256'] == sha(raw(kind + '-corpus/manifest.json'))
    assert not any(r[x] for x in ('full_G6_qualified', 'production_radio_integration', 'physical_device', 'sdk_or_target_executed'))
    assert len(r['targets']) == 2 and {x['target'] for x in r['targets']} == {'esp32', 'esp32c3'}
    reference = r['references'][0]
    assert reference['kind'] == ('retained_positions' if kind == 'positions' else 'fresh_libvorbis')
    assert len(reference['cases']) == 14
    reference_group = 'references-original-nonpass' if kind == 'positions' else kind + '-check'
    reference_report = REPORTS[reference_group]
    reference_commands = {c['name']: c for c in reference_report['commands']}
    if kind == 'slopes':
        assert len(reference_commands) == 14
    refs = {}
    for i, fact in enumerate(reference['cases']):
        assert fact['index'] == i and fact['id'] == MATRICES[kind]['cases'][i]['id']
        command = reference_commands[f'case-{i:02d}-libvorbis']
        assert command['state'] == 'terminal' and command['reaped'] and not command.get('forced_stop')
        assert command['returncode'] == fact['returncode']
        argv = command['argv']
        tools = [value for path, value in reference_report['tools'].items() if norm(path).casefold() == norm(argv[0]).casefold()]
        assert len(tools) == 1
        assert (tools[0]['sha256'] if isinstance(tools[0], dict) else tools[0]) == '09948d4cdd0650da6ff5a87577469f2a218dc2615ae379f8f734d24c49de0f73'
        assert argv.count('-c:a') == 2 and argv[argv.index('-c:a') + 1] == 'libvorbis'
        assert argv[argv.index('-c:a', argv.index('-c:a') + 1) + 1] == 'pcm_s16le'
        assert '-ar' not in argv and '-ac' not in argv and '-ss' not in argv and '-t' not in argv
        assert raw(archived(argv[argv.index('-i') + 1])) == raw(kind + '-corpus/' + MATRICES[kind]['cases'][i]['ogg'])
        if i < 8:
            assert command['returncode'] == 0
            data = raw(archived(fact['pcm_path']))
            assert sha(data) == fact['pcm_sha256'] and len(data) == fact['pcm_bytes'] == 28160 and any(data)
            wav = raw(archived(fact['wav_path']))
            assert sha(wav) == fact['wav_sha256']
            with wave.open(io.BytesIO(wav), 'rb') as stream:
                assert (stream.getnchannels(), stream.getframerate(), stream.getsampwidth(), stream.getnframes(), stream.getcomptype()) == (2, 48000, 2, 7040, 'NONE')
                assert stream.readframes(7040) == data and not stream.readframes(1)
            refs[i] = data
        else:
            assert fact['codec_rejection'] and fact['returncode'] in (1, -1094995529, 3199971767) and fact['pcm_bytes'] == 0
            stderr = raw(reference_group + '/' + command.get('stderr', command['name'] + '.stderr.log')).decode(errors='replace')
            codec = re.search(r'\[libvorbis @ [^]]+\].*(?:header.*(?:damaged|corrupt|invalid)|floor.*(?:invalid|error))|'
                              r'\[dec:libvorbis @ [^]]+\] Error while opening decoder: Invalid data found', stderr, re.I)
            assert codec and not re.search(r'Unknown decoder|Decoder .*not found|Unrecognized option|Option .*not found|'
                                           r'No such file or directory|Permission denied|Error writing|Unable to find.*output format', stderr, re.I)
            output = [line for line in stderr.splitlines() if line.startswith('Error opening output')]
            assert not output or output == ['Error opening output file ' + argv[-1] + '.',
                                            'Error opening output files: Invalid data found when processing input']
            assert not output or stderr.find(output[0]) > codec.end()
            for suffix in ('.wav', '.s16le'):
                alias = reference_group + '/' + command['name'] + suffix
                if alias in FILES:
                    assert not raw(alias), 'invalid carrier emitted reference output'
    for target in r['targets']:
        group = ('cyd-' if target['target'] == 'esp32' else 'c3-') + kind
        assert target['report_sha256'] == sha(raw(group + '/report.json')) and target['numerically_qualified']
        assert len(target['cases']) == 8
        for i, fact in enumerate(target['cases']):
            data = PCM[group][i]; actual = metrics(data, refs[i])
            assert fact['index'] == i and fact['raw_sha256'] == sha(data)
            assert all(fact[k] == v for k, v in actual.items()) and actual['over_bound'] == 0
            assert len(fact['packets']) == 14
            at = 0
            for p, size in enumerate(MATRICES[kind]['cases'][i]['expected_packet_bytes']):
                expected = metrics(data[at:at + size], refs[i][at:at + size]); at += size
                assert fact['packets'][p] == dict(packet=p, **expected)
        if kind == 'positions':
            baseline = 'baseline-cyd' if target['target'] == 'esp32' else 'baseline-c3'
            assert target['ordinary_baseline_byte_exact'] and all(PCM[group][i] == PCM[baseline][i] for i in range(3, 8))
    if kind == 'positions':
        assert len(r['controls']) == 1
        control = r['controls'][0]
        assert control['specific_old_tail_control_effective'] and control['all_eight_frozen_baseline_byte_exact']
        assert control['report_sha256'] == sha(raw('cyd-old-tail/report.json'))
        assert all(PCM['cyd-old-tail'][i] == PCM['baseline-cyd'][i] for i in range(8))
        for i, fact in enumerate(control['cases']):
            expected = metrics(PCM['cyd-old-tail'][i], refs[i])
            assert fact == dict(index=i, **expected)
            assert expected['max_abs_error'] == (65535 if i < 3 else 1)
            assert (expected['over_bound'] > 0) is (i < 3)


original = REPORTS['references-original-nonpass']
assert original['result'] == 'NONPASS' and not original['passed'] and len(original['commands']) == 28
for cmd in original['commands']:
    assert cmd['state'] == 'terminal' and cmd['reaped'] and not cmd.get('forced_stop')
for case in original['cases']:
    for fact in case['decoded'].values():
        if fact.get('wav_sha256') is not None:
            wav = raw('references-original-nonpass/' + fact['command'] + '.wav')
            assert sha(wav) == fact['wav_sha256']
            if wav:
                with wave.open(io.BytesIO(wav), 'rb') as stream:
                    data = stream.readframes(stream.getnframes())
                    assert len(data) == fact['pcm_bytes'] and sha(data) == fact['pcm_sha256']
                if fact.get('pcm_path'):
                    assert raw('references-original-nonpass/' + norm(fact['pcm_path'])) == data
for group in ('historical-positions-check01', 'historical-slopes-check01'):
    assert not REPORTS[group]['passed'] and not REPORTS[group]['finite_renderer_qualified']

# Host arithmetic remains retained execution evidence; bind its sources and
# cleanup receipts here without rerunning or claiming offline curve recomputation.
for group in ('host02', 'historical-host01'):
    r = REPORTS[group]
    assert r['completed'] and r['passed'] and (r['cases'], r['curve_bins'], r['wide_products']) == (1472, 1501440, 2349)
    assert r['old_tail_control']['semantic_mismatches'] == 30 and not r['old_tail_control']['sanitizer_failure']
    for original_name, digest in r['sources'].items():
        assert sha(raw(group + '/sources/' + norm(original_name).split('/')[-1])) == digest
    assert sha(raw(group + '/driver.c')) == r['driver_sha256']
    tree = ast.parse(raw(group + '/sources/test-vorbis-floor1-render.py'))
    literals = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
                if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ('C_DRIVER', 'SUPERVISOR')}
    assert literals['C_DRIVER'].encode() == raw(group + '/driver.c')
    if group == 'host02':
        assert sha(raw(group + '/supervisor.py')) == r['supervisor_sha256']
        assert literals['SUPERVISOR'].encode() == raw(group + '/supervisor.py')
        assert len(r['commands']) == 8
    for cmd in r['commands']:
        if group != 'host02':
            assert cmd['state'] == 'terminal' and cmd['returncode'] == 0
            continue
        name = cmd['name']; request_bytes = raw(group + '/' + name + '.request.json')
        request, receipt = json.loads(request_bytes), obj(group + '/' + name + '.receipt.json')
        assert sha(request_bytes) == cmd['request_sha256'] == receipt['request_sha256']
        assert request['nonce'] == cmd['nonce'] == receipt['nonce']
        assert request['argv'] == cmd['child_argv'] and receipt == cmd['supervisor']
        assert receipt['final'] and receipt['new_session'] and receipt['child_reaped'] and receipt['group_gone']
        assert receipt['owned_pgid'] == receipt['child_pid'] > 0
        assert cmd['linux_cleanup_confirmed'] and cmd['transport_reaped'] and cmd['supervisor_exit'] == 0
        assert not cmd.get('local_transport_forced_stop') and 'parent_cleanup_error' not in cmd and 'cleanup_error' not in receipt
        if name in ('timeout-control', 'interruption-control'):
            ready = obj(group + '/' + name + '.ready.json')
            assert ready == cmd['descendant_ready'] and ready['nonce'] == cmd['nonce']
            assert ready['child_pid'] == ready['child_pgid'] == ready['grandchild_pgid'] == receipt['owned_pgid']
            assert type(ready['grandchild_pid']) is int and ready['grandchild_pid'] > 0 and ready['grandchild_pid'] != ready['child_pid']
            assert cmd['state'] == ('timeout' if name == 'timeout-control' else 'stop_requested')
            assert cmd['returncode'] < 0 and receipt['group_sigkill_sent']
        else:
            assert cmd['state'] == 'terminal' and cmd['returncode'] == 0

for group in ('raw', 'raw-control'):
    r = REPORTS[group]
    assert r['passed'] and not r['physical_device'] and not r['production_radio_integration']
    assert r['pcm_comparison_scope'] == 'same-loader handle parity with shared floor1 renderer'
    assert r['unchanged_vendor_pcm_oracle'] is False and r['independent_reference_compared'] is False
    assert r['all_sources_current']
    description = obj(group + '/build/project_description.json')
    bound(group, 'build/' + description['app_elf'], r['elf_sha256'])
    bound(group, 'build/' + description['app_bin'], r['app_sha256'])
    bound(group, 'sdkconfig', r['sdkconfig_sha256'])
    bound(group, 'qemu-flash.bin', r['execution_bundle']['flash_sha256'])
    assert all(c['exit_status'] == 0 for c in r['commands'])
    symbols = raw(group + '/symbols.log').decode(errors='replace').replace('\r\n', '\n')
    assert re.search(r'\b__wrap_floor1_inverse2$', symbols, re.M)
    log = raw(group + '/qemu.log').decode(errors='replace').replace('\r\n', '\n')
    assert not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP', log)
    failures = re.findall(r'^CYD_VORBIS_FAILURE (.+)$', log, re.M)
    complete = re.findall(r'^CYD_VORBIS_RAW_COMPLETE packets=(\d+) rejected=(\d+) pcm=(\d+) original_exact=1 core=1$', log, re.M)
    assert log.count('CYD_VORBIS_CONTROLLED_STOP') == (1 if group == 'raw-control' else 0)
    if group == 'raw-control':
        assert r['control'] == 'skip-preflight' and not complete and failures == ['rejected_dsp_unchanged']
        assert r['exact_failure'] == failures[0] and r['actual_result'] is None
    else:
        assert r['control'] is None and not failures and len(complete) == 1
        assert complete == [('535', '1602', '2112000')]
        assert r['actual_result'] == list(complete[0])

config = REPORTS['config']
assert config['passed'] and config['configure_only'] and config['all_inputs_unchanged_after']
assert config['all_generated_inputs_unchanged_after']
assert not any(config[x] for x in ('compiler_invoked', 'sdk_export_invoked', 'runtime_invoked'))
assert len(config['cases']) == len(config['commands']) == 22
assert sum(fact['expected_rejection'] for fact in config['cases'].values()) == 19
assert 'missing-floor1_render.h' in config['cases']
assert {row['case'] for row in config['commands']} == set(config['cases'])
for command in config['commands']:
    name = command['case']; fact = config['cases'][name]
    log = raw('config/' + name + '/configure.log')
    assert fact['passed'] and sha(log) == fact['log_sha256'] == command['log_sha256']
    assert fact['exit_status'] == command['exit_status'] == int(fact['expected_rejection'])
    if fact['expected_rejection']:
        assert ('Vorbis repair ' + fact['predicate']).encode() in log
    elif name == 'enabled':
        assert [norm(x).split('/')[-1] for x in fact['actual_sources']] == ['setup.c', 'simple.c', 'output.c']
        assert fact['actual_link_options'].count('-Wl,--wrap=floor1_inverse2') == 1
    else:
        assert name in ('disabled', 'early') and not fact['actual_sources']
        assert fact['actual_link_options'] == ['-Wl,--undefined=preserve_existing']

for alias in FILES:
    if alias.startswith('commands/') and alias.endswith('.json'):
        receipt = obj(alias)
        if 'owned_pid' in receipt:
            assert receipt['status'] == 'TERMINAL' and type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0
            assert type(receipt['returncode']) is int
            for path, row in receipt['logs'].items():
                data = raw(archived(path))
                assert len(data) == row['bytes'] and sha(data) == row['sha256']

print(json.dumps(dict(archive_verified=True, aliases=len(FILES), unique_objects=len(CACHE),
    finite_signed16_bound=2, both_architectures=True, old_tail_frozen_baseline_reproduced=True,
    host02_descendant_cleanup_receipts_verified=True, native_overall_nonpass_preserved=True,
    omitted_identity_records_checked=len(IDENTITY_ONLY), omitted_binary_or_tool_semantics_verified=False,
    new_decoder_or_target_execution=False, full_G6_qualified=False, production_radio_integration=False)))
