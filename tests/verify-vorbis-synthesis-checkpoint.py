"""Replay actual host/native synthesis evidence without archived execution."""
import argparse
import ast
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'tests/results/vorbis-synthesis-20261028'
ARCHIVE_SHA = '1b9937ee9009e5b1a48cd2435651f8cd26af0b3e565b2f3c0e2c1fb3c5b45877'
MANIFEST_SHA = '9601d8ba02962e89a7916c6d30ffa43195c1c7023efcf1f9c25d542a4414545b'
PHYSICAL_MEMBERS, PHYSICAL_BYTES = 424, 193778896
LOGICAL_MEMBERS, LOGICAL_BYTES = 1487, 209071195
GROUPS = {'host01', 'host02', 'host03', 'profiles01', 'fixture-lint01', 'esp32-01', 'esp32-02', 'esp32-03',
    'c3-01', 'c3-02', 'protocol01', 'protocol02', 'protocol03', 'protocol-c3-01', 'tools', 'receipts'}
FINAL_HOST = 'host03'
HOST_STATES = {'host01': dict(completed=False, passed=False, commands=1),
    'host02': dict(completed=True, passed=True, commands=3),
    'host03': dict(completed=True, passed=True, commands=4)}
NATIVE_GOOD = {'esp32-03': 'esp32', 'c3-02': 'esp32c3'}
NATIVE_FAILED = {'esp32-01': 'esp32', 'esp32-02': 'esp32', 'c3-01': 'esp32c3'}
PROTOCOL_GROUPS = {
    'protocol01': dict(target='esp32', completed=False, malformed=None),
    'protocol02': dict(target='esp32', completed=True, malformed=9),
    'protocol03': dict(target='esp32', completed=True, malformed=11),
    'protocol-c3-01': dict(target='esp32c3', completed=True, malformed=9),
}
OMITTED = {'host02/synthesis', 'host03/synthesis'}
OMITTED_COUNT, OMITTED_BYTES = 3604, 316099377
HOST_CONTROLS = dict(packets=434, pcm_bytes=738560, failed=0, checks=399271)
OWNER_CONTROLS = dict(pushes=20447, values=17828274, refusals=50, checks=46359453)
HOST_SEAL = 'receipts/vorbis-synthesis-final-seal-20261028-01.json'
PINS = {
    'vorbis_synthesis_checkpoint.py': 'dfff6c46c56bf0cbf95a2385ca3584314b720088bd11124247e20605d8712ed5',
    'verify-vorbis-pcm-exact-checkpoint.py': '22a8fbc03d658d569ca95c6d18636f18e3e79cca1e812138659993c14d5f81aa',
    'test-vorbis-synthesis.py': 'f42ab5b669b5a39e0619449a798c00f682bf2f1468664d5376eb63bdda429765',
    'test-vorbis-synthesis-qemu.py': 'ce4859daf4f9a0bd59a1c023b3b01b3e015d7a76a14acca98c8f6e27ce91222b',
    'test-vorbis-timing.py': 'f990067645a196972767639c100506be757b9adb8a2d0f8bbd8fe3857f0be33a',
    'test-vorbis-window-exact.py': '06268abe3c9fe4836bf17ca91b1fcb73ce82137ea872282e21bad61fa4494e41',
    'test-vorbis-pcm-exact.py': 'ca145e73850ac1af5e16ebef5c1287f5a4c74d131752f6a71bee63ef5190cf01',
    'test-vorbis-floor1-render.py': 'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2',
}
SOURCE_PINS = {'idf/components/native_vorbis_synthesis/synthesis.c':
    '8b7bd71d6b97671303c606740213d0d709edacc0c314e203e2954a4f3a74a50f',
    'tests/native/vorbis_synthesis_pipeline.c': '23810410ba5ce310fc90f19b73c0960271a98608388008dfb73fb9537966a0a1',
    'tests/native/vorbis_synthesis_pipeline.h': 'b27634e303e85351a2cc6376c4b737445097d59d321513eba2454d4c31aff88b',
    'tests/native/vorbis_synthesis_host.c': 'dd537bdfba5066b8bd0e53d571099d3218c5c77c9beb705f59a8be48f5244aae'}
ORIGINAL_SHA = '32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
PCM_SHA = 'b9df479b6cb6ac07b2aff2049f05bb8ba98ef9ce4fdc72acf40a333f47e01d75'
LINKED = ('vorbis_synthesis_pipeline_run', 'native_vorbis_setup_owner_replace', 'native_vorbis_frame_decode',
    'native_vorbis_frame_floor0_prepare', 'native_vorbis_imdct_transform_binary64',
    'native_vorbis_synthesis_push', 'native_vorbis_pcm_s16_product_pair')


def verify():
    # Pin every live dependency before importing even the shared byte inspector.
    for name, digest in PINS.items():
        if hashlib.sha256((ROOT/'tests'/name).read_bytes()).hexdigest() != digest:
            raise ValueError('pinned live reader: '+name)
    for name, digest in SOURCE_PINS.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise ValueError('pinned live source: '+name)
    spec = importlib.util.spec_from_file_location('synthesis_checkpoint_helper', ROOT/'tests/vorbis_synthesis_checkpoint.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    need, sha = helper.need, helper.sha
    modules = {name: helper.load_local('tests/'+name, digest, 'synthesis_checkpoint_'+str(index))
        for index, (name, digest) in enumerate(PINS.items()) if name not in
        ('vorbis_synthesis_checkpoint.py', 'test-vorbis-floor1-render.py')}
    aliases = modules['verify-vorbis-pcm-exact-checkpoint.py']
    host = modules['test-vorbis-synthesis.py']
    native = modules['test-vorbis-synthesis-qemu.py']
    timing = modules['test-vorbis-timing.py']
    window = modules['test-vorbis-window-exact.py']
    pcm = modules['test-vorbis-pcm-exact.py']
    physical = helper.archive_members(FOLDER, ARCHIVE_SHA, MANIFEST_SHA)
    manifest = json.loads((ROOT/FOLDER/'manifest.json').read_bytes())
    members = aliases.resolve_logical_members(physical, manifest)
    read = lambda name: json.loads(members[name])
    need((len(physical), sum(map(len, physical.values())), len(members), sum(map(len, members.values()))) ==
        (PHYSICAL_MEMBERS, PHYSICAL_BYTES, LOGICAL_MEMBERS, LOGICAL_BYTES), 'complete physical/logical evidence inventory')
    need({name.split('/')[0] for name in members} == GROUPS, 'exact retained campaign groups')
    omitted = {row['path']: row for row in manifest['omitted']}
    need(len(omitted) == len(manifest['omitted']) == OMITTED_COUNT and
        sum(row['bytes'] for row in omitted.values()) == OMITTED_BYTES and all(
        row['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', row['sha256']) and name not in members and
        (name in OMITTED or any(name.startswith(group+'/build/') for group in (*NATIVE_GOOD, *NATIVE_FAILED))) and
        PurePosixPath(name).as_posix() == name and not PurePosixPath(name).is_absolute() and
        '..' not in PurePosixPath(name).parts and ':' not in name and '\\' not in name
        for name, row in omitted.items()), 'only pinned rebuildable build scratch or host executables omitted')

    def artifact(group, relative, digest, required=False):
        name = group+'/'+relative
        if name in members:
            need(sha(members[name]) == digest, 'every retained executed artifact byte')
        else:
            need(not required and name in omitted and omitted[name]['sha256'] == digest,
                'explicit omitted derived artifact identity')

    def live_snapshot(relative, body):
        if Path(relative).suffix in ('.c', '.h', '.inc', '.py', '.ps1', '.defaults') or Path(relative).name == 'CMakeLists.txt':
            need((ROOT/relative).read_bytes() == body, 'live source equals executed frozen code')

    def sources(group, report, live=False, profile=False, target=False):
        if target:
            rows = [(pin['snapshot'].removeprefix('sources/'), pin['sha256']) for pin in report['inputs'].values()]
        else:
            rows = report['sources'].items()
        for name, digest in rows:
            path = PurePosixPath(name)
            need(path.parts and not path.is_absolute() and '..' not in path.parts and path.as_posix() == name and
                ':' not in name and '\\' not in name, 'contained frozen source path')
            body = members[group+'/sources/'+name]
            need(sha(body) == digest, 'every frozen source/header/packet/reference byte')
            if not live:
                continue
            if profile:
                relative = 'idf/components/'+name
            elif name.startswith('components/'):
                relative = 'idf/'+name
            elif name.startswith(('native/', 'helper/')):
                relative = 'tests/native/'+name.split('/', 1)[1]
            elif name.startswith('project/'):
                relative = 'tests/target/vorbis_synthesis_qemu/'+name.split('/', 1)[1]
            elif name == 'controller.py':
                relative = 'tests/test-vorbis-synthesis-qemu.py'
            elif name == 'runner.py':
                relative = 'tests/test-vorbis-synthesis.py'
            elif name == 'supervisor-origin.py':
                relative = 'tests/test-vorbis-floor1-render.py'
            elif name == 'timing-oracle.py':
                relative = 'tests/test-vorbis-timing.py'
            elif name == 'window-oracle.py':
                relative = 'tests/test-vorbis-window-exact.py'
            elif name == 'pcm-oracle.py':
                relative = 'tests/test-vorbis-pcm-exact.py'
            else:
                continue
            live_snapshot(relative, body)

    def host_commands(group, report, successful):
        for row in report['commands']:
            stem = group+'/'+row['name']
            request = read(stem+'.request.json')
            need(request['nonce'] == row['nonce'] and request['argv'] == row['child_argv'] and
                request['timeout'] == (180 if row['name'].startswith('execute') else 60) and
                sha(members[stem+'.request.json']) == row['request_sha256'], 'nonce and exact owned request binding')
            receipt = row.get('supervisor')
            if not receipt:
                need(not successful and stem+'.receipt.json' not in members and row.get('transport_exit') != 0 and
                    (row.get('transport_exit') is not None or 'transport_pid' not in row), 'honest pre-dispatch refusal')
                continue
            need(receipt == read(stem+'.receipt.json') and receipt['nonce'] == row['nonce'] and
                receipt['request_sha256'] == row['request_sha256'] and row['transport_exit'] == 0 and
                not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and receipt['final'] and
                receipt['new_session'] and receipt['child_pid'] == receipt['owned_pgid'] and receipt['child_reaped'] and
                receipt['group_gone'] and (not successful or receipt['child_returncode'] == 0),
                'all owned transports and children terminal and reaped')
        if 'supervisor_sha256' in report:
            text = members[group+'/supervisor.py']
            templates = [ast.literal_eval(node.value) for node in ast.parse(
                members[group+'/sources/supervisor-origin.py']).body if isinstance(node, ast.Assign) and
                any(isinstance(t, ast.Name) and t.id == 'SUPERVISOR' for t in node.targets)]
            need(sha(text) == report['supervisor_sha256'] and len(templates) == 1 and
                templates[0].count('assert 0<timeout<=60') == 1 and text == templates[0].replace(
                    'assert 0<timeout<=60', 'assert 0<timeout<=180').encode(), 'exact watchdog-only supervisor derivation')

    original, model, references, xiph, saved = host.original_data()
    need(sha(original) == ORIGINAL_SHA == native.ORIGINAL_SHA and host.BOUND == model['policy']['max_abs_error'] == 2 and
        len(model['cases']) == 31 and len(model['relations']) == 14, 'unchanged original31/bound2/all14 contract')
    need(native.ORIGINAL_ARCHIVE_SHA == host.PRIOR_SHA and native.REFERENCE_ARCHIVE_SHA == host.XIPH_SHA,
        'native and host packet/reference readers anchor the same prior DATA archives')
    report, capture = helper.clean_host(members, FINAL_HOST)
    sources(FINAL_HOST, report, live=True)
    host_commands(FINAL_HOST, report, successful=True)
    need(members[FINAL_HOST+'/sources/original31.json'] == original and
        members[FINAL_HOST+'/sources/saved-Xiph-PCM.bin'] == saved and
        members[FINAL_HOST+'/input.bin'] == host.encode(model) and
        sha(members[FINAL_HOST+'/input.bin']) == report['input_sha256'], 'complete actual raw API input recipe')
    for index, row in enumerate(model['cases']):
        need(members[FINAL_HOST+f'/sources/reference/{index:02}.s16le'] == references[row['id']], 'every original reference byte')
    need(report['original31_sha256'] == ORIGINAL_SHA and report['raw_API_input_bytes'] == 7376 and
        report['retained_comment_bytes'] == 1798, 'all 9174 original header/audio/comment bytes retained')
    measured = host.compare(capture, model, references, xiph, timing)
    need(measured == report['measurements'] and measured['passed'] and measured['streams'] == 31 and
        measured['packets'] == 434 and measured['pcm_bytes'] == 738560 and measured['floor0_channels'] == 336 and
        measured['floor1_channels'] == 532 and measured['fixed_S16_bound'] == 2 and
        measured['max_abs_error'] <= 2 and measured['max_xiph_abs_error'] <= 2 and measured['pcm_sha256'] == PCM_SHA and
        len(measured['relations']) == 14 and all(row['passed'] for row in measured['relations']) and
        measured['actual_full_pipeline_executed'] and not measured['saved_transform_or_gain_inputs_used'] and
        not measured['private_decoder_executed'] and not measured['production_selected'],
        'every actual host packet/event/PCM sample against both independent references and all relations')
    host_case_sha = {row['id']: row['sha256'] for row in measured['cases']}
    owner = host.owner_data(model, timing, window)
    need(members[FINAL_HOST+'/sources/saved-overlap-DATA.bin'] == owner['saved_capture'] and
        members[FINAL_HOST+'/owner-input.bin'] == host.encode_owner(owner, timing) and
        sha(members[FINAL_HOST+'/owner-input.bin']) == report['owner_input_sha256'],
        'complete regenerated stateful owner input and saved overlap DATA lineage')
    need(report['owner_recipe'] == dict(overlap_rows=864, timing_actions=20019, channels=list(range(1, 256)),
        waveform='owner_wave/sample(i*37+channel*17+step*11)',
        signed64_exponents='INT64_MIN/MAX selected by (channel+step)&1', witnesses=owner['witness_metrics']),
        'complete owner action/channel/waveform recipe')
    owner_capture = members[FINAL_HOST+'/owner-capture.bin']
    owner_measured = host.compare_owner(owner_capture, owner, timing, window, pcm)
    need(owner_measured == report['owner_measurements'] and owner_measured['passed'] and
        sha(owner_capture) == report['owner_capture_sha256'] and report['controls'] == HOST_CONTROLS and
        report['owner_controls'] == OWNER_CONTROLS and owner_measured['overlap_rows'] == 864 and
        owner_measured['overlap_pcm_values'] == 598992 and owner_measured['timing_actions'] == 20019 and
        owner_measured['channel_counts'] == 255 and owner_measured['channel_pushes'] == 765 and
        owner_measured['saved_underflow_witnesses'] == 17962 and owner_measured['saved_witnesses_at_least1074'] == 13767 and
        owner_measured['witness_identity_sha256'] == '844e6d38700b6e8c6d8683d7afcc49d7a46289a1a4d1735d3cc1a554826af472' and
        not owner_measured['old_overlap_API_executed'] and not owner_measured['old_PCM_API_executed'],
        'all stateful overlap/timing/channel PCM, history/tails/exponents and refusal guards')
    need([row['name'] for row in report['commands']] == ['compiler-version', 'compile', 'execute', 'execute-owner'] and
        report['sanitizers'] == ['address', 'undefined'] and not members[FINAL_HOST+'/execute-owner.stderr.log'] and
        all(not report[key] for key in ('native_executed', 'production_selected', 'private_decoder_executed',
            'saved_transform_or_gain_inputs_used')), 'complete guarded host lifecycle campaign')
    argv = report['commands'][1]['child_argv']
    need(all(flag in argv for flag in ('-UNDEBUG', '-fno-fast-math', '-ffp-contract=off', '-Wall', '-Wextra',
        '-Werror', '-fsanitize=address,undefined', '-fno-sanitize-recover=all')), 'all executed host units instrumented')
    need(members[FINAL_HOST+'/execute.stdout.log'].decode().strip() ==
        'SYNTHESIS_CAPTURE cases=31 packets={packets} pcm_bytes={pcm_bytes} failed={failed} checks={checks} live=0 bytes=0'.format(**HOST_CONTROLS) and
        members[FINAL_HOST+'/execute-owner.stdout.log'].decode().strip() ==
        'SYNTHESIS_OWNER overlap=864 timing=20019 channels=255 pushes={pushes} values={values} refusals={refusals} checks={checks}'.format(**OWNER_CONTROLS),
        'actual primary and whole-owner assertion totals')

    def controls():
        results = []
        def refuse(label, body, at, compare, trunc=False, trailing=False):
            if trunc: bad = body[:-1]
            elif trailing: bad = body+b'X'
            else:
                need(0 <= at < len(body), 'bounded corruption offset')
                bad = body[:at]+bytes([body[at]^128])+body[at+1:]
            need(bad != body, 'every malformed capture actually differs')
            try:
                observed = compare(bad)
                if observed.get('passed') is False:
                    results.append(label)
                    return
            except (ValueError, struct.error, UnicodeError):
                results.append(label)
                return
            raise ValueError('malformed synthesis capture accepted: '+label)
        full = lambda body: host.compare(body, model, references, xiph, timing)
        own = lambda body: host.compare_owner(body, owner, timing, window, pcm)
        r = host.Reader(capture);r.raw(12);r.raw(24);length=r.take('Q');record_start=r.at
        packets = host.Reader(r.raw(length));first_pcm=None
        while packets.at < len(packets.body):
            fields = packets.take('5IQI5IqQ')
            if fields[-1] and first_pcm is None: first_pcm=record_start+packets.at
            packets.raw(fields[-1]*2)
        cleanup_at = r.at+16+7*8
        for label, at in (('full-magic', 0), ('full-format', 16), ('full-timing', record_start+52),
            ('full-helper-cleanup', cleanup_at), ('full-PCM', first_pcm+1)):
            refuse(label, capture, at, full)
        refuse('full-truncated', capture, 0, full, trunc=True)
        refuse('full-trailing', capture, 0, full, trailing=True)
        r = host.Reader(owner_capture);r.raw(12)
        for n in window.SIZES:r.raw(4+4*n)
        need(r.take('I') == 864, 'owner protocol control anchor')
        row_start=r.at;source_at=history_at=exponent_at=first_pcm=None
        for index in range(864):
            identity=r.take('7Iqq');n=identity[5];l=identity[1]
            r.raw(28);channels,samples=r.take('IQ');r.raw(36)
            if not index:source_at=r.at
            r.raw(n*8)
            if not index:history_at=r.at
            r.raw((l//2+2)*8)
            if not index:exponent_at=r.at
            r.raw(24)
            if samples and first_pcm is None:first_pcm=r.at
            r.raw(samples*2)
        need(r.take('I') == 20019, 'timing action protocol control anchor')
        action_at=r.at;zero_hash=None
        for _ in range(20019):
            r.raw(4+36+20+36+28);samples,_=r.take('QQ')
            if samples and zero_hash is None:zero_hash=r.at-8
        need(r.take('I') == 255, 'channel protocol control anchor')
        channel_pcm=None
        for channels in range(1,256):
            need(r.take('I') == channels, 'channel control identity')
            for step in range(3):
                r.raw(4+28);samples=r.take('Q');r.raw((channels*64+2)*8+(channels+2)*8)
                if channels == 2 and samples and channel_pcm is None:channel_pcm=r.at
                r.raw(samples*2)
            r.raw(36)
        need(r.at == len(owner_capture), 'complete owner control offsets')
        for label, at in (('owner-magic', 0), ('owner-coefficient', 16), ('owner-row', row_start),
            ('owner-source', source_at), ('owner-history', history_at), ('owner-exponent', exponent_at),
            ('owner-PCM', first_pcm), ('owner-action', action_at+4), ('owner-zero-run', zero_hash),
            ('owner-interleave', channel_pcm)):
            refuse(label, owner_capture, at, own)
        refuse('owner-truncated', owner_capture, 0, own, trunc=True)
        refuse('owner-trailing', owner_capture, 0, own, trailing=True)
        return results
    malformed_controls = controls()
    need(len(malformed_controls) == 19, 'all full-pipeline and stateful capture corruptions refused')
    seal = read(HOST_SEAL)
    need(all(seal[key] for key in ('passed', 'live_code_headers_CMake_readers_identical', 'all_own_handles_terminal',
        'host02_03_full31_capture_identical', 'no_custom_suppressions', 'actual_full_pipeline_executed')) and
        seal['runner_sha256'] == PINS['test-vorbis-synthesis.py'] and
        seal['fixture_sha256'] == SOURCE_PINS['tests/native/vorbis_synthesis_host.c'] and
        seal['pipeline_source_sha256'] == SOURCE_PINS['tests/native/vorbis_synthesis_pipeline.c'] and
        seal['pipeline_header_sha256'] == SOURCE_PINS['tests/native/vorbis_synthesis_pipeline.h'] and
        seal['synthesis_source_sha256'] == SOURCE_PINS['idf/components/native_vorbis_synthesis/synthesis.c'] and
        seal['controls'] == HOST_CONTROLS and seal['owner_controls'] == OWNER_CONTROLS and
        seal['owner_measurements'] == owner_measured and seal['full31_pcm_sha256'] == PCM_SHA and
        seal['fixed_S16_bound'] == 2 and seal['relations'] == 14 and
        seal['supervisor_only_change'] == 'assert 0<timeout<=60 -> assert 0<timeout<=180' and
        not seal['saved_transform_or_gain_inputs_used'] and not seal['private_decoder_executed'] and
        not seal['production_selected'], 'complete sealed host corpus/source/helper/lifecycle provenance')
    for key in ('input_sha256', 'capture_sha256', 'owner_input_sha256', 'owner_capture_sha256', 'binary_sha256'):
        need(seal[key] == report[key], 'host seal binds every executed input and capture')

    def native_commands(group, record, successful):
        for row in record['commands']:
            for stream in ('stdout', 'stderr'):
                if row.get(stream+'_sha256') is not None:
                    need(sha(members[group+'/'+row['name']+'.'+stream+'.log']) == row[stream+'_sha256'],
                        'every unaltered native command stream')
            if successful:
                need(row['state'] == 'complete' and row['exit_status'] == 0 and row['pid'] > 0 and
                    'tree_stop_returncode' not in row, 'native process terminal without forced stop')
            elif 'pid' in row:
                need(row.get('exit_status') is not None and row['state'] in ('complete', 'failed') and
                    'tree_stop_returncode' not in row, 'retained native failure process terminal')
            else:
                need(row['state'] == 'failed' and not successful, 'retained native launch failure before process creation')

    native_measurements, native_pcm = {}, {}
    for group, target in NATIVE_GOOD.items():
        record = read(group+'/report.json')
        need(record['completed'] and record['passed'] and record['target'] == target and record['target_executed'] and
            record['numerical_qualified'] and not record['production_firmware'] and not record['physical_device'] and
            not record['Xiph_decoder_executed'] and not record['deferred_scopes_resumed'], 'actual native public pipeline scope')
        sources(group, record, live=True, target=True)
        native_commands(group, record, successful=True)
        need([row['name'] for row in record['commands']] == ['sdk-head', 'sdk-clean', 'build', 'symbols', 'merge', 'qemu'],
            'complete native SDK/build/link/image/runtime sequence')
        need(record['sdk_revision'] == native.SDK_HEAD[target] and
            members[group+'/sdk-head.stdout.log'].decode().strip() == native.SDK_HEAD[target] and
            not members[group+'/sdk-clean.stdout.log'].strip() and record['tools']['qemu']['sha256'] == native.QEMU_SHA[target],
            'pinned clean SDK and actual target emulator identity')
        child = json.loads(members[group+'/sdk-child.json'].decode('utf-8-sig'))
        need(child == record['sdk_child'] and child['exit_status'] == 0 and child['pid'] > 0,
            'actual native SDK child terminal receipt')
        need(members[group+'/original31.json'] == original and members[group+'/cases.h'] == native.header(model) and
            sha(members[group+'/cases.h']) == record['cases_header_sha256'], 'every compiled raw packet/header and timing anchor')
        for row in model['cases']:
            need(members[group+'/reference/'+PurePosixPath(row['reference_path']).name] == references[row['id']],
                'every preserved native original reference byte')
        need(members[group+'/project/main/cases.h'] == members[group+'/cases.h'] and all(
            members[group+'/project/main/vorbis_synthesis_pipeline.'+suffix] ==
            members[group+'/sources/helper/vorbis_synthesis_pipeline.'+suffix] for suffix in ('c', 'h')) and
            members[group+'/project/main/main.c'] == members[group+'/sources/project/main/main.c'],
            'actual compiled generated header/main/helper copies equal frozen inputs')
        for relative, digest in record['build_outputs'].items():
            artifact(group, relative, digest, required=not relative.endswith('.obj'))
        description = read(group+'/build/project_description.json')
        need(description['target'] == target, 'actual native build target')
        elf = members[group+'/build/'+description['app_elf']]
        machine = 94 if target == 'esp32' else 243
        need(elf[:6] == b'\x7fELF\x01\x01' and int.from_bytes(elf[16:18], 'little') == 2 and
            int.from_bytes(elf[18:20], 'little') == machine, 'actual native ELF32 executable ABI')
        flags = ('-fstack-usage', '-fno-fast-math', '-ffp-contract=off')
        need(len(record['compile_rows']) == 22 and all(all(flag in row['command'] for flag in flags)
            for row in record['compile_rows']), 'actual public component/helper/app compiler flags')
        database = read(group+'/build/compile_commands.json')
        need(all(row in database for row in record['compile_rows']), 'all selected native compilation records retained')
        need(sum(name.endswith('.obj') for name in record['build_outputs']) == (562 if target == 'esp32' else 595),
            'complete actual native SDK and application object hash inventory')
        for row in record['compile_rows']:
            relative = row['output'].replace('\\', '/')
            if '/build/' in relative:relative=relative.rsplit('/build/', 1)[1]
            object_body=members[group+'/build/'+relative]
            need(object_body[:6] == b'\x7fELF\x01\x01' and int.from_bytes(object_body[16:18], 'little') == 1 and
                int.from_bytes(object_body[18:20], 'little') == machine and
                sha(object_body) == record['build_outputs']['build/'+relative], 'all 22 actual owned native objects have correct ABI')
        need(len(record['stack_records']) == 22 and all(members[group+'/'+name].decode().splitlines() == lines
            for name, lines in record['stack_records'].items()), 'all actual owned native compiler stack records retained')
        symbols = members[group+'/symbols.stdout.log'].decode().replace('\r\n', '\n')
        need(all(re.search(r'\b'+symbol+r'$', symbols, re.MULTILINE) for symbol in LINKED) and
            not re.search(r'\b(?:vorbis_synthesis|esp_vorbis_dec_open)$', symbols, re.MULTILINE),
            'linked exercised public route without private codec')
        config = members[group+'/sdkconfig'].decode().replace('\r\n', '\n')
        compiled_config = members[group+'/build/config/sdkconfig.h'].decode().replace('\r\n', '\n')
        need(bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.MULTILINE)) == (target == 'esp32c3') and
            all(re.search('^'+setting+'$', config, re.MULTILINE) for setting in
                ('CONFIG_ESP_TASK_WDT_EN=y', 'CONFIG_ESP_TASK_WDT_INIT=y', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y')) and
            (target != 'esp32' or re.search(r'^CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y$', config, re.MULTILINE)),
            'actual core profile and watchdog/IDLE protections retained')
        need(all(re.search(r'^#define '+setting+r' 1$', compiled_config, re.MULTILINE) for setting in
            ('CONFIG_ESP_TASK_WDT_EN', 'CONFIG_ESP_TASK_WDT_INIT', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0')) and
            re.search(r'^#define CONFIG_IDF_TARGET_'+target.upper()+r' 1$', compiled_config, re.MULTILINE) and
            bool(re.search(r'^#define CONFIG_FREERTOS_UNICORE 1$', compiled_config, re.MULTILINE)) == (target == 'esp32c3') and
            (target != 'esp32' or re.search(r'^#define CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1 1$', compiled_config, re.MULTILINE)),
            'compiled SDK configuration preserves target/core/WDT/IDLE settings')
        recipe = read(group+'/build/flasher_args.json')
        need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'actual isolated flash configuration')
        offsets = {int(offset, 0): name for offset, name in recipe['flash_files'].items()}
        flash = members[group+'/qemu-flash.bin']
        need(len(flash) == 4*1024*1024 and set(offsets) == ({4096, 32768, 65536} if target == 'esp32' else {0, 32768, 65536}),
            'complete actual native image geometry')
        for offset, name in offsets.items():
            body = members[group+'/build/'+PurePosixPath(name.replace('\\', '/')).as_posix()]
            need(flash[offset:offset+len(body)] == body, 'merged native image contains every executed build binary')
        command = record['commands'][-1]['argv']
        need(command[command.index('-smp')+1] == ('2' if target == 'esp32' else '1') and
            command[command.index('-M')+1] == ('esp32,audiodev=quiet' if target == 'esp32' else 'esp32c3') and
            command[command.index('-display')+1] == 'none' and command[command.index('-serial')+1] == 'stdio' and
            command[command.index('-drive')+1].endswith('qemu-flash.bin,if=mtd,format=raw') and
            all(flag in command for flag in ('-snapshot', '-no-reboot')),
            'actual isolated QEMU launch profile')
        log = members[group+'/qemu.stdout.log'].decode('utf-8', errors='replace').replace('\r\n', '\n')+'\n'+members[
            group+'/qemu.stderr.log'].decode('utf-8', errors='replace')
        actual = native.validate_log(log, model, references, target)
        need(actual == read(group+'/measurement.json') and sha(members[group+'/measurement.json']) == record['measurement_sha256'] and
            {key: value for key, value in actual.items() if key != 'rows'} == record['measurements'] and
            actual['pcm_sha256'] == PCM_SHA and actual['protocol_lines'] == 3450,
            'every actual native event and lossless PCM sample replayed')
        need(native.protocol_controls(model, references, target) == record['protocol_controls'] ==
            dict(valid_full_corpus=True, malformed_refused=11), 'all eleven malformed native transcript controls')
        bodies, maximum_xiph = {}, 0
        for index, row in enumerate(model['cases']):
            body = members[group+f'/pcm/{index:02}-'+row['id']+'.s16le']
            metric = actual['rows'][index]
            need(len(body) == row['pcm_bytes'] and sha(body) == metric['pcm_sha256'] == host_case_sha[row['id']],
                'every host/native PCM byte is identical and bound to its actual transcript')
            error = max((abs(a[0]-b[0]) for a, b in zip(struct.iter_unpack('<h', body),
                struct.iter_unpack('<h', xiph[row['id']]))), default=0)
            need(error <= 2, 'every native sample satisfies unchanged saved-Xiph bound2')
            maximum_xiph = max(maximum_xiph, error)
            bodies[row['id']] = body
        need(sha(b''.join(bodies[row['id']] for row in model['cases'])) == PCM_SHA,
            'all 738560 expanded native PCM bytes retained')
        native_measurements[target] = dict(actual, maximum_xiph_absolute_error=maximum_xiph)
        native_pcm[target] = bodies
    need(native_pcm['esp32'] == native_pcm['esp32c3'], 'all expanded PCM bytes equal across both native targets')

    native_history = {}
    for group, target in NATIVE_FAILED.items():
        old = read(group+'/report.json')
        sources(group, old, target=True)
        native_commands(group, old, successful=False)
        need(not old['passed'] and not old['completed'] and old['target'] == target and
            not old['target_executed'], 'native launch/compiler failures preserved before runtime')
        if group == 'esp32-01':
            need(b'WinError 623' in members[group+'/build.stderr.log'] and
                old['commands'][-1]['name'] == 'build' and old['commands'][-1]['exit_status'] == 1,
                'retained sandbox tool-activation failure before SDK compilation')
        else:
            diagnostics = members[group+'/sdk-build.stdout.log']+members[group+'/sdk-build.stderr.log']
            need(b'type-limits' in diagnostics and b'vorbis_synthesis_pipeline' in diagnostics,
                'retained actual helper size_t compiler failure')
        native_history[group] = dict(completed=old['completed'], passed=old['passed'], commands=len(old['commands']))
    protocol_history = {}
    for group, expected in PROTOCOL_GROUPS.items():
        old = read(group+'/report.json')
        need(old['completed'] == expected['completed'] and not old['target_executed'] and not old['commands'] and
            old['target'] == expected['target'], 'retained pure protocol-only state')
        if expected['completed']:
            need(old['protocol_only'] and old['protocol_controls'] == dict(valid_full_corpus=True,
                malformed_refused=expected['malformed']), 'honest historical protocol control count')
        else:
            need('all raw identification/setup/audio bytes' in old['error'], 'historical raw-byte-accounting preflight failure')
        protocol_history[group] = expected

    profiles = read('profiles01/report.json')
    sources('profiles01', profiles, live=True, profile=True)
    names = ['lx6-version', 'lx6-synthesis', 'lx6-header', 'rv32-version', 'rv32-synthesis', 'rv32-header', 'lint-synthesis']
    need(profiles['completed'] and profiles['passed'] and profiles['source_only'] and not profiles['native_executed'] and
        [row['name'] for row in profiles['commands']] == names and
        profiles['lint'] == [dict(unit='synthesis', warnings=0, errors=0)], 'supplementary source profiles complete and lint clean')
    for row in profiles['commands']:
        need(row['returncode'] == 0 and not row.get('forced_stop'), 'source profile process terminal')
        for stream in ('stdout', 'stderr'):
            need(sha(members['profiles01/'+row['name']+'.'+stream+'.log']) == row[stream+'_sha256'], 'all source profile diagnostics retained')
    need(len(profiles['objects']) == 4 and {row['name'] for row in profiles['objects']} ==
        {target+'-'+unit+'.o' for target in ('lx6', 'rv32') for unit in ('synthesis', 'header')}, 'four actual supplementary source objects')
    for row in profiles['objects']:
        body = members['profiles01/'+row['name']]
        need(sha(body) == row['sha256'] and body[:6] == b'\x7fELF\x01\x01' and
            int.from_bytes(body[18:20], 'little') == row['machine'] == (94 if row['name'].startswith('lx6-') else 243),
            'actual supplementary ELF32 objects match architecture')
    for target in ('lx6', 'rv32'):
        name=target+'-synthesis.su';text=profiles['stack_records'][name]
        need(members['profiles01/'+name].decode().replace('\r\n', '\n') == text and
            any(line.endswith('native_vorbis_synthesis_push\t160\tstatic') for line in text.splitlines()),
            'unaltered own push frame, without a whole-stack claim')
    lint = read('fixture-lint01/report.json')
    need(lint['completed'] and lint['source_only'] and not lint['SDK_executed'] and not lint['native_executed'] and
        lint['warnings'] == 17 and lint['errors'] == 0 and [row['name'] for row in lint['commands']] == ['pipeline', 'fixture'],
        'honest supplementary fixture/helper lint scope and totals')
    for row, warnings in zip(lint['commands'], (3, 14)):
        diagnostics=members['fixture-lint01/'+row['name']+'.stdout.log']+members['fixture-lint01/'+row['name']+'.stderr.log']
        need(row['returncode'] == 0 and row['warnings'] == row['generated_warnings'] == warnings and row['errors'] == 0 and
            len(re.findall(rb': warning:', diagnostics)) == warnings and not re.search(rb': (?:fatal )?error:', diagnostics) and
            row['source_sha256'] == sha(members[FINAL_HOST+'/sources/native/'+row['source']]),
            'all displayed fixture/helper warnings retained and source-bound')
    need(members['fixture-lint01/clang-tidy.yaml'] == members['profiles01/clang-tidy.yaml'] == (ROOT/'.clang-tidy').read_bytes(),
        'unchanged lint configuration without custom suppressions')
    host_history = {}
    for group, expected in HOST_STATES.items():
        old=read(group+'/report.json');sources(group, old);host_commands(group, old, successful=old['passed'])
        actual=dict(completed=old['completed'], passed=old['passed'], commands=len(old['commands']))
        need(actual == expected, 'all host attempts retained honestly')
        if old.get('capture_sha256'):need(sha(members[group+'/capture.bin']) == old['capture_sha256'], 'historical primary capture identity')
        if old['passed']:artifact(group, 'synthesis', old['binary_sha256'])
        host_history[group]=actual
    need(members['host02/capture.bin'] == capture and members['host02/input.bin'] == members[FINAL_HOST+'/input.bin'],
        'owner-state supplements preserve every original31 primary input and capture byte')

    return dict(passed=True, physical_members=len(physical), physical_decoded_bytes=sum(map(len, physical.values())),
        logical_members=len(members), logical_decoded_bytes=sum(map(len, members.values())),
        host=measured, owner=owner_measured, malformed_capture_controls=malformed_controls,
        native=native_measurements, native_history=native_history, protocol_history=protocol_history, host_history=host_history,
        profile_commands=7, profile_ELF32_objects=4, production_lint_warnings=0,
        helper_fixture_lint_warnings=dict(pipeline=3, fixture=14),
        PCM_sha256=PCM_SHA, archived_code_executed=False, commands_reexecuted=0, SDK_reexecuted=False,
        QEMU_reexecuted=False, files_extracted=False, physical_device=False, production_selected=False,
        universal_codec_qualified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.report and (not args.report.resolve().is_relative_to(ROOT/'.build') or args.report.exists()):
        raise ValueError('fresh report within task-local .build required')
    result = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))
