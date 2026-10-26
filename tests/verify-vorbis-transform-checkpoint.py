"""Replay frozen transform evidence with pinned local pure readers only."""
import argparse, copy, hashlib, importlib.util, json, re, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/vorbis-transform-20261026'
ARCHIVE_SHA = '0e3682f21e327d13308e2c771ae6cb286c224d49ed779ce93ef2a55622d4ea87'
MANIFEST_SHA = '29368cf8266fb0d4468022118b3a750bb343fc569f88960bd6d67ff0fcab5475'
PINS = {
    'tests/test-vorbis-transform.py':'443000f55dc389a3a53a84af4a8bb118ada5367e4a3ccbf8525a9ceb630cf59c',
    'tests/test-vorbis-setup.py':'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff',
    'tests/test-vorbis-floor-packet.py':'8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7',
    'tests/test-vorbis-residue.py':'1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d',
    'tests/vorbis_packet_frame_model.py':'5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9',
    'tests/test-vorbis-floor1-frame.py':'570f1cc80a4eea6611bb2ef8a051ce11d1a9e60d6aff96afbc764f247ffccdad',
    'tools/generate-vorbis-imdct64.py':'631b32cd4db11f2eb1cc5ee2cf394bc91678951cf722d582622a2563cc253509'}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def verify():
    need(sha((FOLDER / 'captures.zip').read_bytes()) == ARCHIVE_SHA, 'pinned archive')
    manifest_body = (FOLDER / 'manifest.json').read_bytes()
    need(sha(manifest_body) == MANIFEST_SHA, 'pinned manifest')
    manifest = json.loads(manifest_body)
    need(manifest['schema'] == 'vorbis-transform-evidence-v1' and manifest['archive_sha256'] == ARCHIVE_SHA, 'matching manifest')
    with zipfile.ZipFile(FOLDER / 'captures.zip') as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 438 and set(names) == set(manifest['files']), 'exact unique inventory')
        for name in names:
            path = PurePosixPath(name)
            need(name == path.as_posix() and not path.is_absolute() and '..' not in path.parts and
                 ':' not in name and '\\' not in name, 'canonical member name')
        bodies = {name:archive.read(name) for name in names}
    for name, body in bodies.items():
        need(manifest['files'][name] == dict(bytes=len(body),sha256=sha(body)), 'member hash and extent')
    read = lambda name: json.loads(bodies[name])
    modules = []
    for relative, pin in PINS.items():
        path = ROOT / relative
        need(sha(path.read_bytes()) == pin, 'trusted local reader identity: ' + relative)
        spec = importlib.util.spec_from_file_location('trusted_transform_' + str(len(modules)), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    subject, setup, floor, residue, model_reader, frame, generator = modules
    need(subject.NORM_BOUND == 5e-12 and subject.ANCHOR_BOUND == 5e-13, 'unchanged declared numerical bounds')
    need(generator.generated_body(bodies['host03/sources/upstream/mdct.c']) ==
         bodies['host03/sources/components/native_vorbis_transform/xiph_backward.inc'], 'unchanged Xiph bodies')
    need((ROOT / 'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/mdct.c').read_bytes() ==
         bodies['host03/sources/upstream/mdct.c'], 'pinned baseline unchanged')
    model = model_reader.cases(setup,floor,residue,bodies['host03/sources/original31.json'])
    need(len(model['cases']) == 1311, 'all previous packet rows')
    model['cases'].extend(frame.extra_cases(model_reader,setup,floor,residue))
    packets = frame.build_expected(model,model_reader,setup,floor,residue,
        frame.table_factors(bodies['host03/sources/xiph-floor1.c']))
    rows = subject.synthetic_cases() + subject.packet_cases(model,packets)
    expected = subject.build_expected(rows)
    anchors = subject.oracle_anchors()
    need(len(rows) == 3084 and read('host03/cases.json') == rows and
         read('host03/expected.json') == expected and read('host03/oracle-anchors.json') == anchors and
         bodies['host03/input.bin'] == subject.encode_input(rows), 'independent models/inputs/anchors')
    report = read('host03/report.json')
    need(report['completed'] and report['passed'] and report['measurement_completed'] and report['units'] == 3 and
         report['sanitizers'] == ['address','undefined'], 'complete three-unit sanitized host gate')
    for key in ('target_executed','production_radio_integration','deferred_scopes_resumed','floor0_gain_executed','PCM_executed'):
        need(report[key] is False, 'finite qualification boundary')
    for filename, key in (('cases.json','model_sha256'),('expected.json','expected_sha256'),('input.bin','input_sha256'),
                          ('oracle-anchors.json','oracle_anchors_sha256'),('capture.bin','capture_sha256'),('measurement.json','measurement_sha256')):
        need(sha(bodies['host03/' + filename]) == report[key], 'declared evidence identity')
    for label, pin in report['inputs'].items():
        body = bodies['host03/' + pin['snapshot']]
        need(sha(body) == pin['sha256'], 'executed frozen input')
        portable = label.replace('\\','/')
        if not label.startswith('archive:'):
            for marker in ('/idf/components/','/tests/','/tools/'):
                if marker in portable:
                    local = ROOT / (marker.strip('/') + '/' + portable.split(marker,1)[1])
                    need(local.read_bytes() == body, 'current input equals executed bytes')
    need(sha(bodies['host03/sources/native/vorbis_transform_host.c']) ==
         'd821d607689267b4e1ab642ea49430cd6052a22e20d9b33fc3a2fff94130432e', 'guarded fixture identity')
    commands = report['commands']
    need([row['name'] for row in commands] == ['compiler-version','compiler-machine','compile-00','compile-01','compile-02','link','execute'], 'seven actual commands')
    for row in commands:
        stem = 'host03/' + row['name']
        request, receipt = read(stem + '.request.json'), read(stem + '.receipt.json')
        need(receipt == row['supervisor'] and request['argv'] == row['child_argv'] and
             request['nonce'] == row['nonce'] == receipt['nonce'] and sha(bodies[stem + '.request.json']) ==
             row['request_sha256'] == receipt['request_sha256'], 'owned request/receipt binding')
        need(row['transport_exit'] == 0 and not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and
             receipt['final'] and receipt['child_returncode'] == 0 and receipt['child_reaped'] and receipt['group_gone'] and
             receipt['new_session'] and receipt['child_pid'] == receipt['owned_pgid'], 'terminal/reaped real command')
        for stream in ('stdout','stderr'):
            need(sha(bodies[stem + '.' + stream + '.log']) == row[stream + '_sha256'], 'raw diagnostic hash')
        if row['name'].startswith('compile-'):
            need(all(flag in row['child_argv'] for flag in ('-UNDEBUG','-Wall','-Wextra','-Werror',
                '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-fast-math','-ffp-contract=off')), 'active assertions/sanitizers')
    need(not bodies['host03/execute.stderr.log'], 'empty sanitizer stderr')
    observed, plans, controls = subject.decode_output(bodies['host03/capture.bin'],rows)
    measured = subject.compare(rows,expected,observed,plans)
    need(measured == read('host03/measurement.json') == report['measurements'] and measured['passed'] and
         controls == report['controls'] == dict(refusals=943,checks=10981418), 'every actual value and guard')
    need({key:measured[key] for key in ('cases','conversion_values','transformed_values','invalid_rows','magnitude_widths',
         'block_sizes','lookup_values','packet_channels','original_packet_channels','original_packets_represented')} ==
         dict(cases=3084,conversion_values=465958,transformed_values=881216,invalid_rows=44,magnitude_widths=1151,
              block_sizes=8,lookup_values=24480,packet_channels=1750,original_packet_channels=532,original_packets_represented=266), 'measured scope')
    need(not read('host01/report.json')['passed'] and not read('host02/report.json')['passed'] and
         'canonical positive zero block' in read('host02/report.json')['error'], 'preserved failed attempts')
    for name in ('cases.json','expected.json','input.bin','capture.bin','oracle-anchors.json'):
        need(bodies['host02/' + name] == bodies['host03/' + name], 'unchanged data after comparator-only correction')
    lint = read('lint03/report.json')
    need(lint['completed'] and lint['warnings'] == 5 and lint['errors'] == 0 and len(lint['commands']) == 3, 'final complete lint')
    for index, row in enumerate(lint['commands']):
        stem = f'lint03/{index:02}-' + Path(row['source']).stem
        diagnostics = b'\n'.join(bodies[stem + '.' + stream + '.log'] for stream in ('stdout','stderr'))
        need(row['returncode'] == 0 and not row.get('forced_stop') and row['errors'] == 0 and
             len(re.findall(rb': warning:',diagnostics)) == row['warnings'] == (0,0,5)[index], 'unfiltered lint counts')
        for stream in ('stdout','stderr'):
            need(sha(bodies[stem + '.' + stream + '.log']) == row[stream + '_sha256'], 'lint diagnostic identity')
    need(read('lint01/report.json')['warnings'] == 1 and read('lint02/report.json')['warnings'] == 0, 'retained constructor warning/fix')
    gcc = read('gcc02/report.json')
    need(gcc['completed'] and gcc['source_only'] and not gcc['SDK_build'] and not gcc['target_executed'] and
         not gcc['production_build'] and not gcc['whole_call_chain_stack_qualified'] and len(gcc['commands']) == 12, 'source-only compiler scope')
    for row in gcc['commands']:
        need(row['returncode'] == 0 and not row.get('forced_stop'), 'compiler command terminal')
        for stream in ('stdout','stderr'):
            need(sha(bodies['gcc02/' + row['name'] + '.' + stream + '.log']) == row[stream + '_sha256'], 'compiler raw diagnostics')
    for profile, machine in (('esp32-lx6',94),('esp32-c3',243)):
        for stem, record in gcc['profiles'][profile]['objects'].items():
            obj = bodies['gcc02/' + profile + '/' + stem + '.o']
            stack = bodies['gcc02/' + profile + '/' + stem + '.su']
            need(obj[:6] == b'\x7fELF\x01\x01' and int.from_bytes(obj[16:18],'little') == 1 and
                 int.from_bytes(obj[18:20],'little') == machine and sha(obj) == record['sha256'] and sha(stack) == record['stack_sha256'], 'actual ELF32 and stack records')
            parsed = []
            for line in stack.decode().splitlines():
                site, count, kind = line.split('\t')
                parsed.append(dict(function=site.rsplit(':',1)[-1],own_frame_bytes=int(count),kind=kind))
            need(parsed == record['own_function_frames'] and all(row['kind'] == 'static' for row in parsed), 'own static function frames')
    rejected = 0
    for body in (b'',bodies['host03/capture.bin'][:100],bodies['host03/capture.bin'] + b'\0'):
        try:
            subject.decode_output(body,rows)
        except ValueError:
            rejected += 1
    corrupted = bytearray(bodies['host03/capture.bin']);corrupted[54] ^= 0x10
    try:
        actual, lookups, _ = subject.decode_output(bytes(corrupted),rows)
        subject.compare(rows,expected,actual,lookups)
    except ValueError:
        rejected += 1
    wrong = copy.deepcopy(expected)
    next(row for row in wrong if row['status'] == 0)['converted_bits'][0] ^= 1
    try:
        subject.compare(rows,wrong,observed,plans)
    except ValueError:
        rejected += 1
    need(rejected == 5, 'all damaged/partial/semantic controls rejected')
    return dict(passed=True,members=len(bodies),measurements=measured,controls=controls,
                rejected_controls=rejected,target_executed=False,production_radio_integration=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = verify()
    if args.output:
        need(not args.output.exists(),'fresh output receipt')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
