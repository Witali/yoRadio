"""Verify exact floor1 captures with pinned local pure readers; no children."""
import argparse, copy, hashlib, importlib.util, io, json, re, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/vorbis-floor1-product-20261026'
ARCHIVE_SHA = '3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea'
MANIFEST_SHA = '2542e701020ade4ae7b3c005f807e8f1ca712da9b67a90d9c313afd0f23c111e'
PINS = {
    'test-vorbis-floor1-product.py':'d03e736c2e66504c5d2d22e9ae1b4af23ee8871d89c5fdb610caa9a3c118c9ff',
    'test-vorbis-floor1-frame.py':'570f1cc80a4eea6611bb2ef8a051ce11d1a9e60d6aff96afbc764f247ffccdad',
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


class Blob:
    def __init__(self, body):
        self.body = body

    def open(self, mode):
        need(mode == 'rb', 'read-only capture')
        return io.BytesIO(self.body)


class DigestSink:
    def __init__(self):
        self.digest, self.count = hashlib.sha256(), 0

    def open(self, mode):
        need(mode == 'xb', 'new virtual input stream')
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def write(self, body):
        self.digest.update(body)
        self.count += len(body)
        return len(body)


def verify():
    need(sha((FOLDER / 'captures.zip').read_bytes()) == ARCHIVE_SHA, 'pinned archive')
    manifest_body = (FOLDER / 'manifest.json').read_bytes()
    need(sha(manifest_body) == MANIFEST_SHA, 'pinned manifest')
    manifest = json.loads(manifest_body)
    need(manifest['schema'] == 'vorbis-floor1-product-evidence-v1' and
         manifest['archive_sha256'] == ARCHIVE_SHA, 'manifest identity')
    with zipfile.ZipFile(FOLDER / 'captures.zip') as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) == 583 and set(names) == set(manifest['files']), 'exact inventory')
        for name in names:
            path = PurePosixPath(name)
            need(path.as_posix() == name and not path.is_absolute() and '..' not in path.parts and
                 ':' not in name and '\\' not in name, 'canonical member name')
        bodies = {name:archive.read(name) for name in names}
    for name, body in bodies.items():
        need(manifest['files'][name] == dict(bytes=len(body), sha256=sha(body)), 'member identity')
    read = lambda name: json.loads(bodies[name])
    modules = {}
    for name, pin in PINS.items():
        path = ROOT / 'tests' / name
        need(sha(path.read_bytes()) == pin, 'trusted local pure reader: ' + name)
        spec = importlib.util.spec_from_file_location('trusted_floor1_' + str(len(modules)), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    math, frame, capture, model_reader, setup, floor, residue = (modules[name] for name in PINS)

    def host(prefix, units):
        report = read(prefix + '/report.json')
        need(report['completed'] and report['passed'] and report['units'] == units and
             report['sanitizers'] == ['address', 'undefined'], 'complete host gate')
        for key in ('target_executed','production_radio_integration','deferred_scopes_resumed','transform_executed','PCM_executed'):
            need(report[key] is False, 'qualification boundary')
        for name, pin in report['inputs'].items():
            body = bodies[prefix + '/' + pin['snapshot']]
            need(sha(body) == pin['sha256'], 'frozen input')
            if prefix.endswith('03'):
                portable = name.replace('\\', '/')
                for marker in ('/idf/components/', '/tests/'):
                    if marker in portable:
                        local = ROOT / (marker.strip('/') + '/' + portable.split(marker, 1)[1])
                        need(local.read_bytes() == body, 'current files equal final executed files')
        commands = report['commands']
        need([row['name'] for row in commands] == ['compiler-version','compiler-machine'] +
             [f'compile-{i:02}' for i in range(units)] + ['link','execute'], 'actual command inventory')
        for row in commands:
            stem = prefix + '/' + row['name']
            request, receipt = read(stem + '.request.json'), read(stem + '.receipt.json')
            need(receipt == row['supervisor'] and request['argv'] == row['child_argv'] and
                 request['nonce'] == row['nonce'] == receipt['nonce'] and
                 sha(bodies[stem + '.request.json']) == row['request_sha256'] == receipt['request_sha256'], 'owned command binding')
            need(row['transport_exit'] == 0 and not row.get('forced_transport_stop') and receipt['final'] and
                 receipt['state'] == 'terminal' and receipt['child_returncode'] == 0 and
                 receipt['child_reaped'] and receipt['group_gone'] and receipt['new_session'] and
                 receipt['child_pid'] == receipt['owned_pgid'], 'terminal/reaped command')
            for stream in ('stdout','stderr'):
                need(sha(bodies[stem + '.' + stream + '.log']) == row[stream + '_sha256'], 'raw diagnostics')
            if row['name'].startswith('compile-'):
                need(all(flag in row['child_argv'] for flag in ('-UNDEBUG','-Wall','-Wextra','-Werror',
                    '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-fast-math','-ffp-contract=off')), 'compiler checks enabled')
        need(not bodies[prefix + '/execute.stderr.log'], 'empty sanitizer stderr')
        for filename, key in (('cases.json','model_sha256'),('input.bin','input_sha256'),
                              ('capture.bin','capture_sha256'),('measurement.json','measurement_sha256')):
            need(sha(bodies[prefix + '/' + filename]) == report[key], 'reported evidence hash')
        return report

    rows = math.cases()
    table = math.table_from_upstream(bodies['math03/sources/upstream-floor1.c'])
    need(len(rows) == 1663 and table == read('math03/factors.json'), 'independent coefficient table')
    sink = DigestSink()
    math.write_input(sink, rows)
    need(sink.count == len(bodies['math03/input.bin']) and sink.digest.hexdigest() == sha(bodies['math03/input.bin']), 'all generic input bytes')
    math_metrics = []
    for prefix, assertions in (('math02',22968025),('math03',33603855)):
        report = host(prefix, 2)
        need(read(prefix + '/cases.json') == rows and read(prefix + '/factors.json') == table, 'full generic model')
        measured = math.compare_capture(Blob(bodies[prefix + '/capture.bin']), rows, table)
        need(measured == read(prefix + '/measurement.json') == report['measurements'] and
             measured['runtime_assertions'] == assertions and measured['exact_samples'] == 619540 and
             measured['exact_limb_words'] == 11816765 and measured['refusal_controls'] == 663 and
             measured['refused_rows'] == 23 and measured['maximum_limbs'] == 36, 'all generic products and controls')
        math_metrics.append(measured)
    need(bodies['math02/capture.bin'][:-8] == bodies['math03/capture.bin'][:-8], 'same arithmetic after stronger guards')

    model = model_reader.cases(setup, floor, residue, bodies['frame03/sources/original31.json'])
    need(len(model['cases']) == 1311, 'retain all prior packet cases')
    model['cases'].extend(frame.extra_cases(model_reader, setup, floor, residue))
    factors = frame.table_factors(bodies['frame03/sources/xiph-floor1.c'])
    need(factors == [(row['mantissa'],row['exponent']) for row in table], 'independent exact table oracles agree')
    expected = frame.build_expected(model, model_reader, setup, floor, residue, factors)
    frame_metrics = None
    for prefix in ('frame02','frame03'):
        report = host(prefix, 10)
        need(read(prefix + '/cases.json') == model and read(prefix + '/expected.json') == expected and
             bodies[prefix + '/input.bin'] == capture.encode_input(model), 'all original packet inputs/references')
        actual, controls = frame.decode_output(bodies[prefix + '/capture.bin'], model, capture)
        measured = frame.compare(model, actual, expected)
        need(measured == read(prefix + '/measurement.json') and measured['passed'] and controls == report['controls'] ==
             dict(cases=1313,refusals=11237,checks=862469), 'all packet products and guards')
        need({key:measured[key] for key in ('original_packets','floor1_channels','floor0_API_refusals',
             'absent_with_nonzero_residue','present_zero_grid','quiet_nonzero_channels','curve_bins','product_words')} ==
             dict(original_packets=434,floor1_channels=1750,floor0_API_refusals=972,absent_with_nonzero_residue=75,
                  present_zero_grid=78,quiet_nonzero_channels=2,curve_bins=275808,product_words=297056), 'integration scope')
        frame_metrics = measured
    for name in ('cases.json','expected.json','input.bin','capture.bin','measurement.json'):
        need(bodies['frame02/' + name] == bodies['frame03/' + name], 'unchanged result after exact table oracle')

    lint = read('lint03/report.json')
    need(lint['completed'] and lint['warnings'] == 10 and lint['errors'] == 0 and len(lint['commands']) == 3, 'full final lint')
    for index, row in enumerate(lint['commands']):
        stem = f'lint03/{index:02}-' + Path(row['source']).stem
        diagnostics = b'\n'.join(bodies[stem + '.' + stream + '.log'] for stream in ('stdout','stderr'))
        need(row['returncode'] == 0 and not row.get('forced_stop') and row['errors'] == 0 and
             len(re.findall(rb': warning:', diagnostics)) == row['warnings'] == (0,2,8)[index], 'unfiltered lint diagnostics')
        for stream in ('stdout','stderr'):
            need(sha(bodies[stem + '.' + stream + '.log']) == row[stream + '_sha256'], 'lint log binding')
    gcc = read('gcc02/report.json')
    need(gcc['completed'] and gcc['source_only'] and not gcc['SDK_build'] and not gcc['target_executed'] and
         not gcc['production_build'] and not gcc['whole_call_chain_stack_qualified'] and len(gcc['commands']) == 10, 'source-only profiles')
    for row in gcc['commands']:
        need(row['returncode'] == 0 and not row.get('forced_stop'), 'compiler command terminal')
        for stream in ('stdout','stderr'):
            need(sha(bodies['gcc02/' + row['name'] + '.' + stream + '.log']) == row[stream + '_sha256'], 'compiler raw logs')
    for profile, machine in (('esp32-lx6',94),('esp32-c3',243)):
        for stem, record in gcc['profiles'][profile]['objects'].items():
            obj = bodies['gcc02/' + profile + '/' + stem + '.o']
            stack = bodies['gcc02/' + profile + '/' + stem + '.su']
            need(sha(obj) == record['sha256'] and obj[:6] == b'\x7fELF\x01\x01' and
                 int.from_bytes(obj[16:18],'little') == 1 and int.from_bytes(obj[18:20],'little') == machine and
                 sha(stack) == record['stack_sha256'], 'actual ELF32 objects and stack records')
            parsed = []
            for line in stack.decode().splitlines():
                site, count, kind = line.split('\t')
                parsed.append(dict(function=site.rsplit(':',1)[-1], own_frame_bytes=int(count), kind=kind))
            need(parsed == record['own_function_frames'] and all(row['kind'] == 'static' for row in parsed), 'static own-function frames')
    for prefix in ('math01','frame01'):
        report = read(prefix + '/report.json')
        need(not report['completed'] and not report['passed'] and len(report['commands']) == 1 and
             not report['commands'][0]['supervisor'], 'retained pre-compiler WSL refusal')
    need(not read('gcc01/report.json')['completed'], 'retained initial compiler launch failure')

    rejected = 0
    for body in (b'', bodies['math03/capture.bin'][:100],
                 bodies['math03/capture.bin'][:72] + bytes([bodies['math03/capture.bin'][72] ^ 1]) + bodies['math03/capture.bin'][73:]):
        try:
            math.compare_capture(Blob(body), rows, table)
        except ValueError:
            rejected += 1
    try:
        frame.decode_output(bodies['frame03/capture.bin'][:100], model, capture)
    except ValueError:
        rejected += 1
    wrong = copy.deepcopy(expected)
    changed = False
    for row in wrong:
        for product in row['products']:
            if product['samples']:
                product['samples'][0] ^= 1
                changed = True
                break
        if changed:
            break
    actual, _ = frame.decode_output(bodies['frame03/capture.bin'], model, capture)
    need(changed and not frame.compare(model, actual, wrong)['passed'], 'detect semantic reference mismatch')
    rejected += 1
    need(rejected == 5, 'all partial/corrupted/semantic controls rejected')
    return dict(passed=True,members=len(bodies),math=math_metrics[-1],
                frame={key:value for key,value in frame_metrics.items() if key != 'measurements'},
                rejected_controls=rejected,target_executed=False,production_radio_integration=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify()
    if args.output:
        need(not args.output.exists(), 'fresh receipt')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
