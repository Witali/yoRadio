"""Verify immutable frame captures using pinned local pure readers only."""
import argparse, hashlib, importlib.util, json, re, zipfile
from pathlib import Path, PurePosixPath
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/vorbis-packet-frame-20261026'
ARCHIVE_SHA = 'e23c996d8fdd4b37e34090875d5430ced460247507ff393edd725a253ae159b9'
PINS = {
    'test-vorbis-packet-frame.py':'7c449b4b190500b0ab5931205f06e51e9f691112ebea80ac1affb7b200cb22d0',
    'vorbis_packet_frame_model.py':'5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9',
    'test-vorbis-setup.py':'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff',
    'test-vorbis-floor-packet.py':'8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7',
    'test-vorbis-residue.py':'1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d'}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def verify():
    need(sha((FOLDER / 'captures.zip').read_bytes()) == ARCHIVE_SHA, 'complete pinned archive')
    manifest = json.loads((FOLDER / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'vorbis-packet-frame-evidence-v1' and manifest['archive_sha256'] == ARCHIVE_SHA, 'matching evidence manifest')
    with zipfile.ZipFile(FOLDER / 'captures.zip') as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) and set(names) == set(manifest['files']), 'exact unique inventory')
        for name in names:
            path = PurePosixPath(name)
            need(name == path.as_posix() and not path.is_absolute() and '..' not in path.parts and ':' not in name and '\\' not in name,
                 'canonical relative archive member')
        bodies = {name: archive.read(name) for name in names}
    for name, body in bodies.items():
        need(manifest['files'][name] == dict(bytes=len(body), sha256=sha(body)), 'all member hashes/extents')
    read_json = lambda name: json.loads(bodies[name])
    modules = {}
    for name, pin in PINS.items():
        path = ROOT / 'tests' / name
        need(sha(path.read_bytes()) == pin, 'trusted local reader identity: ' + name)
        frozen = 'host02/sources/' + ('runner.py' if name == 'test-vorbis-packet-frame.py' else name)
        need(sha(bodies[frozen]) == pin, 'executed reader equals trusted source')
        spec = importlib.util.spec_from_file_location('trusted_frame_' + str(len(modules)), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    subject = modules['test-vorbis-packet-frame.py']
    model_reader = modules['vorbis_packet_frame_model.py']
    setup, floor, residue = (modules[name] for name in ('test-vorbis-setup.py','test-vorbis-floor-packet.py','test-vorbis-residue.py'))
    # No archived code, compiler, child process or extraction executes.
    model = model_reader.cases(setup, floor, residue, bodies['host02/sources/original31.json'])
    expected = [model_reader.expected_case(row, setup, floor, residue) for row in model['cases']]
    need(model == read_json('host02/cases.json') and expected == read_json('host02/expected.json'), 'independent full model and exact references')
    need(subject.encode_input(model) == bodies['host02/input.bin'], 'all actual input bytes')
    report = read_json('host02/report.json')
    need(report['completed'] and report['passed'] and report['measurement_completed'] and report['units'] == 9, 'complete nine-unit host gate')
    for key in ('gain_executed','transform_executed','PCM_executed','target_executed','deferred_scopes_resumed','production_radio_integration'):
        need(report[key] is False, 'finite qualification boundary: ' + key)
    for name, field in (('cases.json','model_sha256'),('expected.json','expected_sha256'),('input.bin','input_sha256'),
                        ('capture.bin','capture_sha256'),('measurement.json','measurement_sha256')):
        need(sha(bodies['host02/' + name]) == report[field], 'declared capture/reference identity')
    for pin in report['inputs'].values():
        need(sha(bodies['host02/' + pin['snapshot']]) == pin['sha256'], 'all frozen sources/inputs')
    need(sha(bodies['host02/sources/native/vorbis_packet_frame_host.c']) ==
         '4152ff07aec8ad75563200b19e1baf80eb8b9164cbc4120c48a7e9eabface880', 'final explicit snapshot invariants')
    for name, body in bodies.items():
        prefix = 'host02/sources/components/'
        if name.startswith(prefix):
            need((ROOT / 'idf/components' / name.removeprefix(prefix)).read_bytes() == body, 'current component equals executed source')
    commands = report['commands']
    need([row['name'] for row in commands] == ['compiler-version','compiler-machine'] +
         [f'compile-{index:02d}' for index in range(9)] + ['link','execute'], 'all thirteen real commands')
    for row in commands:
        prefix = 'host02/' + row['name']
        request, receipt = read_json(prefix + '.request.json'), read_json(prefix + '.receipt.json')
        need(receipt == row['supervisor'] and sha(bodies[prefix + '.request.json']) == row['request_sha256'], 'actual receipt/request binding')
        need(request['argv'] == row['child_argv'] and request['nonce'] == row['nonce'] == receipt['nonce'] and
             receipt['request_sha256'] == row['request_sha256'], 'owned process identity')
        need(row['transport_exit'] == 0 and not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and
             receipt['final'] and receipt['child_returncode'] == 0 and receipt['child_reaped'] and receipt['group_gone'] and
             receipt['new_session'] and receipt['child_pid'] == receipt['owned_pgid'], 'successful terminal/reaped command')
        for stream in ('stdout','stderr'):
            need(sha(bodies[prefix + '.' + stream + '.log']) == row[stream + '_sha256'], 'raw command diagnostics')
        if row['name'].startswith('compile-'):
            need(all(flag in row['child_argv'] for flag in ('-UNDEBUG','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                 '-fno-sanitize-recover=all','-fno-fast-math','-ffp-contract=off')), 'active assertions/sanitizers/warnings')
    need(not bodies['host02/execute.stderr.log'], 'no sanitizer diagnostics')
    observed, controls = subject.decode_output(bodies['host02/capture.bin'], model)
    measured = subject.compare(model, observed, expected)
    need(measured == read_json('host02/measurement.json') and measured['passed'], 'all exact fields and limbs')
    need(controls == report['controls'] == dict(cases=1311,pool_refusals=3332,checks=1631165), 'actual guarded/refusal/retry counts')
    need({key: measured[key] for key in ('cases','original_packets','floor_eop','residue_eop','coupled_limb_words','affine_values','raw_Y_values')} ==
         dict(cases=1311,original_packets=434,floor_eop=384,residue_eop=420,coupled_limb_words=411520,affine_values=2769,raw_Y_values=2224),
         'original corpus and full integration results')
    old_report = read_json('host01/report.json')
    old_rows, old_controls = subject.decode_output(bodies['host01/capture.bin'], model)
    need(old_report['passed'] and old_rows == observed and old_controls['pool_refusals'] == 3332 and
         old_controls['checks'] == 1210741 and bodies['host01/cases.json'] == bodies['host02/cases.json'] and
         bodies['host01/expected.json'] == bodies['host02/expected.json'], 'earlier full pass and stronger final harness retained')
    for prefix, warnings in (('lint01',8),('lint02',7)):
        lint = read_json(prefix + '/report.json')
        need(lint['completed'] and lint['warnings'] == warnings and lint['errors'] == 0 and len(lint['commands']) == 9, 'unfiltered nine-unit lint outcome')
        for index, row in enumerate(lint['commands']):
            stem = prefix + '/' + f'{index:02d}-' + Path(row['source']).stem
            text = '\n'.join(bodies[stem+'.'+stream+'.log'].decode('utf-8',errors='replace') for stream in ('stdout','stderr'))
            need(len(re.findall(r': warning:', text)) == row['warnings'] and
                 len(re.findall(r': (?:error|fatal error):', text)) == row['errors'] and row['returncode'] == 0,
                 'raw warning/error counts')
        need(lint['commands'][7]['warnings'] == 0, 'new coordinator has no warnings')
    profiles = read_json('profiles/report.json')
    need(profiles['completed'] and profiles['source_only'] and not profiles['SDK_build'] and not profiles['target_executed'] and
         not profiles['production_build'] and not profiles['whole_call_chain_stack_qualified'] and len(profiles['commands']) == 10,
         'source-only profile scope')
    for profile, evidence in profiles['profiles'].items():
        macros = bodies['profiles/' + profile + '-macros.stdout.log'].replace(b'\r\n',b'\n')
        need(b'#define __SIZEOF_POINTER__ 4\n' in macros and b'#define __SIZEOF_LONG__ 4\n' in macros, 'actual ILP32 compiler macros')
        for stem, obj in evidence['objects'].items():
            body = bodies['profiles/' + profile + '/' + stem + '.o']
            need(sha(body) == obj['sha256'] and body[:6] == b'\x7fELF\x01\x01' and
                 int.from_bytes(body[16:18],'little') == 1 and int.from_bytes(body[18:20],'little') == obj['machine'], 'actual relocatable ELF32 object')
            usage = bodies['profiles/' + profile + '/' + stem + '.su']
            need(sha(usage) == obj['stack_sha256'], 'actual compiler stack record')
            rows = []
            for line in usage.decode().splitlines():
                site, count, kind = line.split('\t')
                rows.append(dict(function=site.rsplit(':',1)[-1],own_frame_bytes=int(count),kind=kind))
            need(rows == obj['own_function_frames'] and all(row['kind']=='static' for row in rows), 'static own frames')
    capture = bodies['host02/capture.bin']
    rejected = 0
    for mutation in (b'', b'BADMAGIC'+capture[8:], capture[:-1], capture+b'\0'):
        try:
            subject.decode_output(mutation, model)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('partial/corrupted capture accepted')
    changed = bytearray(capture)
    changed[20] ^= 1
    changed_rows, _ = subject.decode_output(bytes(changed), model)
    need(not subject.compare(model, changed_rows, expected)['passed'], 'semantic prefix corruption rejected')
    return dict(verified=True,cases=1311,original_packets=434,exact_limb_words=411520,
        capacity_refusals=3332,floor_eop=384,residue_eop=420,reader_controls=rejected+1,
        ILP32_source_profiles=2,SDK_build=False,target_executed=False,PCM_qualified=False)


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(verify()))
