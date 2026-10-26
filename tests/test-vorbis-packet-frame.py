"""Guarded exact packet-front-end capture and independent floor/residue oracle.

All original434 packets remain unmodified. No gain, transform, PCM, SDK or
deferred fixture executes; this qualifies the new composition boundary.
"""
import argparse, ast, hashlib, importlib.util, json, os, re, struct, subprocess, sys, time, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ('mode', 'blockflag', 'previous_window', 'next_window', 'mapping', 'blocksize')
LAYOUT = ('mapping', 'bins', 'channels', 'limbs', 'magnitude_bits', 'exponent', 'sample_count', 'limb_count', 'classification_count')
AFFINE = ('minimum_bits', 'delta_bits', 'minimum_multiplier', 'delta_multiplier')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def linux(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def encode_input(model):
    result = bytearray(b'VFRAME01')
    def put(fmt, *values):
        result.extend(struct.pack('<' + fmt, *values))
    put('I', len(model['cases']))
    for row in model['cases']:
        name = row['id'].encode('ascii')
        need(re.fullmatch(rb'[A-Za-z0-9_-]{1,128}', name), 'literal case name')
        put('I', len(name))
        result.extend(name)
        for stem in ('identification', 'setup', 'packet'):
            body = bytes.fromhex(row[stem + '_hex'])
            put('I', len(body))
            result.extend(body)
            put('Q', row[stem + '_bits'])
        put('QI', row['start_bit'], int(row['initial_eop']))
    return bytes(result)


class Reader:
    def __init__(self, body):
        self.body, self.at = body, 0

    def take(self, fmt):
        width = struct.calcsize('<' + fmt)
        need(width <= len(self.body) - self.at, 'complete capture field')
        values = struct.unpack_from('<' + fmt, self.body, self.at)
        self.at += width
        return values[0] if len(values) == 1 else values

    def array(self, count):
        need(0 <= count <= (len(self.body) - self.at) // 4, 'complete bounded array extent')
        if not count:
            return []
        values = list(struct.unpack_from('<' + 'I' * count, self.body, self.at))
        self.at += 4 * count
        return values

    def boolean(self):
        value = self.take('I')
        need(value in (0, 1), 'boolean capture field')
        return bool(value)

    def prefix(self):
        return dict(zip(PREFIX, self.take('IIIIII')))

    def layout(self):
        return dict(zip(LAYOUT, self.take('IIIIIiQQQ')))


def decode_output(body, model):
    reader = Reader(body)
    need(reader.take('8s') == b'VFOUT001' and reader.take('I') == len(model['cases']), 'whole ordered capture')
    rows, checks, refusals = [], 0, 0
    for index, case in enumerate(model['cases']):
        need(reader.take('I') == index, 'case identity/order')
        measured = reader.take('i')
        requirements = None
        if measured == 0:
            requirements = dict(prefix=reader.prefix(), floor_count=reader.take('I'),
                                floor0_values=reader.take('Q'), floor1_values=reader.take('Q'),
                                residue_bound=reader.layout())
        status = reader.take('i')
        frame = None
        if status == 0:
            prefix = reader.prefix()
            count, count0, count1 = reader.take('IQQ')
            need(1 <= count <= 255 and count0 <= 255 * 255 and count1 <= 255 * 65, 'full-format floor extents')
            implicit, floor_eop = reader.boolean(), reader.boolean()
            layout = reader.layout()
            residue = dict(zip(('classwords', 'vectors', 'values', 'stopped_on_eop'), reader.take('QQQI')))
            floors = []
            for _ in range(count):
                floor = dict(zip(('floor_index', 'type', 'present', 'value_count', 'selected_book'), reader.take('IIIII')))
                floor['amplitude'] = dict(raw_amplitude=reader.take('Q'), amplitude_bits=reader.take('I'), amplitude_offset=reader.take('I'))
                floor['value_offset'] = reader.take('Q')
                floors.append(floor)
            values0 = [dict(zip(AFFINE, reader.take('IIII'))) for _ in range(count0)]
            values1 = reader.array(count1)
            spectrum = reader.array(layout['limb_count'])
            frame = dict(prefix=prefix, floor_count=count, floor0_count=count0, floor1_count=count1,
                         implicit_zero=implicit, floor_eop=floor_eop, spectrum_layout=layout,
                         residue=residue, floors=floors, floor0=values0, floor1=values1, spectrum=spectrum)
        position, eop, guards, refused, assertions = reader.take('QIIIQ')
        need(eop in (0, 1) and guards == 7 and assertions > 0, 'actual immutable-buffer/lifetime guards')
        rows.append(dict(id=case['id'], measure_status=measured, requirements=requirements,
                         decode_status=status, frame=frame, position=position, end_of_packet=bool(eop)))
        refusals += refused
        checks += assertions
    need(reader.at == len(body), 'no extra/missing capture bytes')
    return rows, dict(cases=len(rows), pool_refusals=refusals, checks=checks)


def compare(model, observed, expected):
    need(len(model['cases']) == len(observed) == len(expected), 'all declared exact rows')
    metrics = []
    for case, actual, wanted in zip(model['cases'], observed, expected):
        need(actual['id'] == case['id'], 'retained case identity')
        fields = {key: value for key, value in actual.items() if key != 'id'}
        reasons = [key for key in wanted if fields.get(key) != wanted[key]]
        metrics.append(dict(id=case['id'], passed=not reasons, differences=reasons,
                            expected_sha256=sha(json.dumps(wanted, sort_keys=True).encode()),
                            actual_sha256=sha(json.dumps(fields, sort_keys=True).encode())))
    return dict(passed=all(row['passed'] for row in metrics), cases=len(metrics),
                original_packets=sum(row['id'].startswith('original31-') for row in model['cases']),
                floor_eop=sum(bool(row['frame'] and row['frame']['floor_eop']) for row in observed),
                residue_eop=sum(bool(row['frame'] and row['frame']['residue']['stopped_on_eop']) for row in observed),
                coupled_limb_words=sum(len(row['frame']['spectrum']) for row in observed if row['frame']),
                affine_values=sum(len(row['frame']['floor0']) for row in observed if row['frame']),
                raw_Y_values=sum(len(row['frame']['floor1']) for row in observed if row['frame']),
                measurements=metrics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and out != ROOT / '.build' and not out.exists(), 'fresh task-local output')
    out.mkdir(parents=True)
    (out / 'objects').mkdir()
    inputs = {}
    report = dict(completed=False, passed=False, inputs=inputs, commands=[], sanitizers=['address', 'undefined'],
                  scope='Exact front end through inverse coupling only.', gain_executed=False,
                  transform_executed=False, PCM_executed=False, target_executed=False,
                  deferred_scopes_resumed=False, production_radio_integration=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    def freeze(path, name):
        body = path.read_bytes()
        target = out / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        inputs[str(path.resolve())] = dict(sha256=sha(body), snapshot=target.relative_to(out).as_posix())
        return body
    def run(name, argv):
        nonce = uuid.uuid4().hex
        request, receipt, stop = (out / (name + suffix) for suffix in ('.request.json', '.receipt.json', '.stop'))
        request.write_text(json.dumps(dict(nonce=nonce, argv=list(map(str, argv)), timeout=60,
                                          receipt=linux(receipt), stop=linux(stop))), encoding='utf-8')
        command = (['wsl.exe', '--exec', 'python3'] if sys.platform == 'win32' else [sys.executable]) + [linux(out / 'supervisor.py'), linux(request)]
        row = dict(name=name, argv=command, child_argv=list(map(str, argv)), nonce=nonce, request_sha256=sha(request.read_bytes()))
        report['commands'].append(row)
        save()
        child, error, started = None, None, time.monotonic()
        try:
            with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
                child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                row['transport_pid'] = child.pid
                child.wait(timeout=80)
        except BaseException as caught:
            error = caught
            row['parent_error'] = repr(caught)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce, encoding='ascii')
                try:
                    child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
                    row['forced_transport_stop'] = True
            observed = json.loads(receipt.read_text()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic() - started, supervisor=observed,
                       transport_exit=None if child is None else child.poll())
            for stream in ('stdout', 'stderr'):
                path = out / (name + '.' + stream + '.log')
                row[stream + '_sha256'] = sha(path.read_bytes()) if path.exists() else None
            save()
        need(error is None and row['transport_exit'] == 0 and not row.get('forced_transport_stop'), 'owned transport terminal: ' + name)
        need(observed.get('nonce') == nonce and observed.get('request_sha256') == row['request_sha256'] and
             observed.get('state') == 'terminal' and observed.get('final') is True and
             observed.get('child_reaped') is True and observed.get('group_gone') is True and
             observed.get('new_session') is True and observed.get('child_pid') == observed.get('owned_pgid') and
             observed.get('child_returncode') == 0, 'owned command terminal: ' + name)
        return (out / (name + '.stdout.log')).read_text('utf-8', errors='replace')
    save()
    try:
        freeze(Path(__file__), 'runner.py')
        for name in ('native_vorbis_numeric', 'native_vorbis_setup_owner', 'native_vorbis_packet_frame'):
            folder = ROOT / 'idf/components' / name
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    freeze(path, 'components/' + name + '/' + path.relative_to(folder).as_posix())
        freeze(ROOT / 'tests/native/vorbis_packet_frame_host.c', 'native/vorbis_packet_frame_host.c')
        for name in ('test-vorbis-setup.py', 'test-vorbis-floor-packet.py', 'test-vorbis-residue.py', 'vorbis_packet_frame_model.py'):
            freeze(ROOT / 'tests' / name, name)
        setup = load(out / 'sources/test-vorbis-setup.py', 'frozen_frame_setup')
        floor = load(out / 'sources/test-vorbis-floor-packet.py', 'frozen_frame_floor')
        residue = load(out / 'sources/test-vorbis-residue.py', 'frozen_frame_residue')
        subject = load(out / 'sources/vorbis_packet_frame_model.py', 'frozen_frame_model')
        original = freeze(ROOT / '.build/vorbis-xiph-prep-20261025-01/cases.json', 'original31.json')
        model = subject.cases(setup, floor, residue, original)
        expected = [subject.expected_case(row, setup, floor, residue) for row in model['cases']]
        (out / 'cases.json').write_text(json.dumps(model, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        (out / 'expected.json').write_text(json.dumps(expected, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        (out / 'input.bin').write_bytes(encode_input(model))
        report.update(prepared=True, cases=len(model['cases']), original_packets=434,
            model_sha256=sha((out / 'cases.json').read_bytes()), expected_sha256=sha((out / 'expected.json').read_bytes()),
            input_sha256=sha((out / 'input.bin').read_bytes()))
        save()
        if args.prepare_only:
            print(json.dumps({key: report[key] for key in ('prepared', 'cases', 'original_packets')}))
            return 0
        origin = freeze(ROOT / 'tests/test-vorbis-floor1-render.py', 'supervisor-origin.py')
        supervisors = [ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == 'SUPERVISOR' for target in node.targets)]
        need(len(supervisors) == 1, 'one owned process supervisor')
        (out / 'supervisor.py').write_text(supervisors[0], encoding='utf-8', newline='\n')
        report['supervisor_sha256'] = sha((out / 'supervisor.py').read_bytes())
        report['compiler_version'] = run('compiler-version', ['gcc', '--version'])
        report['compiler_machine'] = run('compiler-machine', ['gcc', '-dumpmachine'])
        components = out / 'sources/components'
        names = ('native_vorbis_numeric', 'native_vorbis_setup_owner', 'native_vorbis_packet_frame')
        includes = [components / name / 'include' for name in names]
        common = ['gcc', '-std=c11', '-O1', '-g', '-UNDEBUG', '-D_GNU_SOURCE=1', '-fno-fast-math', '-ffp-contract=off',
                  '-fno-pie', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer',
                  '-ffunction-sections', '-fdata-sections', '-MMD', '-Wall', '-Wextra', '-Werror',
                  *['-I' + linux(path) for path in includes]]
        units = [components / names[0] / (name + '.c') for name in ('floor0', 'quant', 'codebook', 'setup', 'floor_packet', 'residue')]
        units += [components / names[1] / 'setup_owner.c', components / names[2] / 'packet_frame.c', out / 'sources/native/vorbis_packet_frame_host.c']
        objects = []
        for index, source in enumerate(units):
            obj = out / 'objects' / f'{index:02d}.o'
            objects.append(obj)
            run(f'compile-{index:02d}', [*common, '-c', linux(source), '-o', linux(obj)])
        binary = out / 'packet-frame'
        run('link', ['gcc', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-no-pie', '-Wl,--gc-sections',
                     *[linux(path) for path in objects], '-lm', '-o', linux(binary)])
        text = run('execute', ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
                              'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', linux(binary), linux(out / 'input.bin'), linux(out / 'capture.bin')])
        match = re.fullmatch(r'FRAME_CAPTURE cases=(\d+) pool_refusals=(\d+) checks=(\d+) live=0 bytes=0\s*', text)
        need(match is not None and not (out / 'execute.stderr.log').read_bytes(), 'complete guarded capture without sanitizer diagnostics')
        capture = (out / 'capture.bin').read_bytes()
        observed, counts = decode_output(capture, model)
        need(tuple(map(int, match.groups())) == tuple(counts[key] for key in ('cases', 'pool_refusals', 'checks')), 'capture/control counts match actual output')
        measured = compare(model, observed, expected)
        (out / 'measurement.json').write_text(json.dumps(measured, indent=2) + '\n', encoding='utf-8', newline='\n')
        report.update(measurement_completed=True, measurement_sha256=sha((out / 'measurement.json').read_bytes()),
                      capture_sha256=sha(capture), controls=counts)
        save()
        need(measured['passed'] and measured['original_packets'] == 434, 'all unshifted exact front-end fields/limbs')
        need(all(sha(Path(path).read_bytes()) == pin['sha256'] == sha((out / pin['snapshot']).read_bytes())
                 for path, pin in inputs.items()), 'all frozen and original inputs unchanged')
        need(sha((out / 'cases.json').read_bytes()) == report['model_sha256'] and
             sha((out / 'expected.json').read_bytes()) == report['expected_sha256'] and
             sha((out / 'input.bin').read_bytes()) == report['input_sha256'], 'predeclared data unchanged')
        report.update(completed=True, passed=True, binary_sha256=sha(binary.read_bytes()), units=len(units),
            measurements={key: value for key, value in measured.items() if key != 'measurements'})
        save()
        print(json.dumps({key: report[key] for key in ('completed', 'passed', 'cases', 'original_packets', 'controls', 'measurements')}))
        return 0
    except BaseException as error:
        report.update(error=repr(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
