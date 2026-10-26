"""Capture exact floor1 products from all previous real packet-front-end rows.

The independent packet model, closed-form floor1 curves and Python integers
predict every product limb. No transform, floor0 gain, PCM or target executes.
"""
import argparse
import ast
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ('native_vorbis_numeric', 'native_vorbis_setup_owner',
              'native_vorbis_packet_frame', 'native_vorbis_floor1_product')
AFFINE = ('minimum_bits', 'delta_bits', 'minimum_multiplier', 'delta_multiplier')
PRODUCT_LAYOUT = ('bins', 'limbs', 'magnitude_bits', 'exponent', 'limb_count')


def need(ok, message):
    if not ok:
        raise ValueError(message)


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


def table_factors(body):
    text = body.decode('ascii')
    match = re.search(r'static const float FLOOR1_fromdB_LOOKUP\[256\]=\{(.*?)\};', text, re.S)
    need(match is not None, 'original Xiph inverse-dB table')
    values = [Fraction(token.strip().removesuffix('F')) for token in match.group(1).split(',') if token.strip()]
    need(len(values) == 256 and values[-1] == 1, 'all original table entries')
    result = []
    for value in values:
        # Round the literal rational directly, avoiding binary64 double rounding.
        numerator, denominator = value.numerator, value.denominator
        power = numerator.bit_length() - denominator.bit_length()
        exact_power = Fraction(1 << power) if power >= 0 else Fraction(1, 1 << -power)
        if value < exact_power:
            power -= 1
        shift = 23 - power
        top = numerator << shift if shift >= 0 else numerator
        bottom = denominator if shift >= 0 else denominator << -shift
        rounded, remainder = divmod(top, bottom)
        if 2 * remainder > bottom or (2 * remainder == bottom and rounded & 1):
            rounded += 1
        if rounded == 1 << 24:
            rounded >>= 1
            power += 1
        need(-126 <= power <= 127 and 1 << 23 <= rounded < 1 << 24, 'normal rounded literal')
        bits = ((power + 127) << 23) | (rounded - (1 << 23))
        need(0 < bits <= 0x3f800000 and bits >> 23, 'positive normal binary32 factor')
        mantissa, exponent = (bits & 0x7fffff) | 0x800000, ((bits >> 23) & 255) - 150
        while not mantissa & 1:
            mantissa >>= 1
            exponent += 1
        result.append((mantissa, exponent))
    need(min(e for _, e in result) == -47 and result[-1] == (1, 0), 'table exponent anchors')
    return result


def extra_cases(subject, setup, floor, residue):
    rows = []
    for name, flags in [('quiet-with-absent-coupled-channel', [1, 0]),
                        ('quiet-with-unity-channel', [1, 1])]:
        spec = residue.base_spec(1, channels=2, bins=6)
        spec['books'][1].update(lengths=[2, 1, 2], lookup=2,
                                minimum_bits=residue.ONE, delta_bits=residue.ONE, value_bits=4)
        spec['mappings'][0]['pairs'] = [(0, 1)]
        row = subject._packet(name, spec, setup, floor, residue, flags)
        data = bytearray.fromhex(row['packet_hex'])
        # One short-mode audio bit, then flag1 and two full unsigned8 Y fields.
        for bit in range(2, 18):
            data[bit // 8] &= ~(1 << (bit % 8))
        if flags[1]:
            for bit in range(19, 35):
                data[bit // 8] |= 1 << (bit % 8)
        row['packet_hex'] = data.hex()
        rows.append(row)
    return rows


def expected_product(frame, channel, context, floor, factors):
    record = frame['floors'][channel]
    result = dict(measure_status=-1, product_status=-1, layout=None, curve=[], samples=[])
    if record['type'] == 0:
        return result
    source = frame['spectrum_layout']
    bins = source['bins']
    result.update(measure_status=0, product_status=0)
    if not record['present'] or not source['limbs']:
        result['layout'] = dict(zip(PRODUCT_LAYOUT, (bins, 0, 0, 0, 0)))
        return result
    info = floor.floor_info(context, record['floor_index'])
    start = record['value_offset']
    raw = frame['floor1'][start:start + record['value_count']]
    final, active = floor.reconstruct(info, raw)
    curve = floor.curve(info, final, active, bins)
    low = min(factors[index][1] for index in curve)
    high = max(exponent + (mantissa - 1).bit_length()
               for mantissa, exponent in (factors[index] for index in curve))
    magnitude = source['magnitude_bits'] + high - low
    limbs = (magnitude + 32) // 32
    result['layout'] = dict(zip(PRODUCT_LAYOUT,
        (bins, limbs, magnitude, source['exponent'] + low, bins * limbs)))
    result['curve'] = curve
    for bin_index, index in enumerate(curve):
        offset = (channel * bins + bin_index) * source['limbs']
        words = frame['spectrum'][offset:offset + source['limbs']]
        scalar = sum(word << (32 * i) for i, word in enumerate(words))
        if words[-1] & 0x80000000:
            scalar -= 1 << (32 * source['limbs'])
        mantissa, exponent = factors[index]
        product = scalar * mantissa * (1 << (exponent - low))
        need(abs(product) < 1 << magnitude, 'exact product bound')
        encoded = product % (1 << (limbs * 32))
        result['samples'].extend((encoded >> (32 * i)) & 0xffffffff for i in range(limbs))
    return result


def build_expected(model, subject, setup, floor, residue, factors):
    rows = []
    for case in model['cases']:
        before = subject.expected_case(case, setup, floor, residue)
        row = {key: before[key] for key in
               ('measure_status', 'decode_status', 'frame', 'position', 'end_of_packet')}
        row['products'] = []
        if row['frame']:
            context = subject._context(case, setup)
            row['products'] = [expected_product(row['frame'], channel, context, floor, factors)
                               for channel in range(row['frame']['floor_count'])]
        rows.append(row)
    return rows


def read_frame(reader):
    prefix = reader.prefix()
    count, count0, count1 = reader.take('IQQ')
    need(1 <= count <= 255 and count0 <= 255 * 255 and count1 <= 255 * 65, 'bounded full floor extents')
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
    return dict(prefix=prefix, floor_count=count, floor0_count=count0, floor1_count=count1,
                implicit_zero=implicit, floor_eop=floor_eop, spectrum_layout=layout,
                residue=residue, floors=floors, floor0=values0, floor1=values1, spectrum=spectrum)


def decode_output(body, model, capture):
    reader = capture.Reader(body)
    need(reader.take('8s') == b'VF1FRAME' and reader.take('I') == len(model['cases']), 'whole ordered product capture')
    rows, checks, refusals = [], 0, 0
    for index, _ in enumerate(model['cases']):
        need(reader.take('I') == index, 'all ordered case identities')
        measured, status = reader.take('ii')
        frame, products = None, []
        if status == 0:
            frame = read_frame(reader)
            for _ in range(frame['floor_count']):
                ms, ps = reader.take('ii')
                row = dict(measure_status=ms, product_status=ps, layout=None, curve=[], samples=[])
                if ps == 0:
                    layout = dict(zip(PRODUCT_LAYOUT, reader.take('IIIiQ')))
                    need(layout['bins'] == frame['spectrum_layout']['bins'] and layout['limbs'] <= 36 and
                         layout['limb_count'] == layout['bins'] * layout['limbs'], 'bounded product extent')
                    count = reader.take('I')
                    need(count == (layout['bins'] if layout['limbs'] else 0), 'complete curve extent')
                    row.update(layout=layout, curve=[reader.take('B') for _ in range(count)],
                               samples=reader.array(layout['limb_count']))
                products.append(row)
        position, eop, refused, assertions = reader.take('QIIQ')
        need(eop in (0, 1) and assertions > 0, 'actual immutable-buffer/lifetime assertions')
        rows.append(dict(measure_status=measured, decode_status=status, frame=frame,
                         position=position, end_of_packet=bool(eop), products=products))
        refusals += refused
        checks += assertions
    need(reader.at == len(body), 'no missing/extra capture fields')
    return rows, dict(cases=len(rows), refusals=refusals, checks=checks)


def compare(model, actual, expected):
    need(len(model['cases']) == len(actual) == len(expected), 'all declared product cases')
    metrics = []
    absent_coupled = present_zero = quiet_nonzero = floor0 = product_channels = curve_bins = words = 0
    for case, got, wanted in zip(model['cases'], actual, expected):
        differences = [key for key in wanted if got.get(key) != wanted[key]]
        metrics.append(dict(id=case['id'], passed=not differences, differences=differences,
                            expected_sha256=sha(json.dumps(wanted, sort_keys=True).encode()),
                            actual_sha256=sha(json.dumps(got, sort_keys=True).encode())))
        if not wanted['frame']:
            continue
        frame = wanted['frame']
        source = frame['spectrum_layout']
        for channel, (record, product) in enumerate(zip(frame['floors'], wanted['products'])):
            if record['type'] == 0:
                floor0 += 1
                continue
            product_channels += 1
            curve_bins += len(product['curve'])
            words += len(product['samples'])
            begin = channel * source['bins'] * source['limbs']
            raw = frame['spectrum'][begin:begin + source['bins'] * source['limbs']]
            absent_coupled += int(not record['present'] and any(raw))
            present_zero += int(record['present'] and not source['limbs'])
            quiet_nonzero += int(bool(product['curve']) and 0 in product['curve'] and any(product['samples']))
    return dict(passed=all(row['passed'] for row in metrics), cases=len(metrics),
                original_packets=sum(row['id'].startswith('original31-') for row in model['cases']),
                floor1_channels=product_channels, floor0_API_refusals=floor0,
                absent_with_nonzero_residue=absent_coupled, present_zero_grid=present_zero,
                quiet_nonzero_channels=quiet_nonzero, curve_bins=curve_bins, product_words=words,
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
                  scope='Exact floor1 curve/product over actual packet frames.', transform_executed=False,
                  floor0_gain_executed=False, PCM_executed=False, target_executed=False,
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
        for name in COMPONENTS:
            folder = ROOT / 'idf/components' / name
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    freeze(path, 'components/' + name + '/' + path.relative_to(folder).as_posix())
        for name in ('vorbis_packet_frame_host.c', 'vorbis_floor1_frame_host.c'):
            freeze(ROOT / 'tests/native' / name, 'native/' + name)
        for name in ('test-vorbis-setup.py', 'test-vorbis-floor-packet.py', 'test-vorbis-residue.py',
                     'vorbis_packet_frame_model.py', 'test-vorbis-packet-frame.py'):
            freeze(ROOT / 'tests' / name, name)
        setup = load(out / 'sources/test-vorbis-setup.py', 'frozen_product_frame_setup')
        floor = load(out / 'sources/test-vorbis-floor-packet.py', 'frozen_product_frame_floor')
        residue = load(out / 'sources/test-vorbis-residue.py', 'frozen_product_frame_residue')
        subject = load(out / 'sources/vorbis_packet_frame_model.py', 'frozen_product_frame_model')
        capture = load(out / 'sources/test-vorbis-packet-frame.py', 'frozen_product_frame_capture')
        original = freeze(ROOT / '.build/vorbis-xiph-prep-20261025-01/cases.json', 'original31.json')
        table = freeze(ROOT / 'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/floor1.c', 'xiph-floor1.c')
        factors = table_factors(table)
        model = subject.cases(setup, floor, residue, original)
        need(len(model['cases']) == 1311, 'all previous1311 packet rows')
        model['cases'].extend(extra_cases(subject, setup, floor, residue))
        expected = build_expected(model, subject, setup, floor, residue, factors)
        (out / 'cases.json').write_text(json.dumps(model, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        (out / 'expected.json').write_text(json.dumps(expected, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        (out / 'input.bin').write_bytes(capture.encode_input(model))
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
        includes = [components / name / 'include' for name in COMPONENTS]
        common = ['gcc', '-std=c11', '-O1', '-g', '-UNDEBUG', '-D_GNU_SOURCE=1', '-fno-fast-math', '-ffp-contract=off',
                  '-fno-pie', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer',
                  '-ffunction-sections', '-fdata-sections', '-MMD', '-Wall', '-Wextra', '-Werror',
                  *['-I' + linux(path) for path in includes]]
        units = [components / COMPONENTS[0] / (name + '.c') for name in ('floor0', 'quant', 'codebook', 'setup', 'floor_packet', 'residue')]
        units += [components / COMPONENTS[1] / 'setup_owner.c', components / COMPONENTS[2] / 'packet_frame.c',
                  components / COMPONENTS[3] / 'floor1_product.c', out / 'sources/native/vorbis_floor1_frame_host.c']
        objects = []
        for index, source in enumerate(units):
            obj = out / 'objects' / f'{index:02d}.o'
            objects.append(obj)
            run(f'compile-{index:02d}', [*common, '-c', linux(source), '-o', linux(obj)])
        binary = out / 'floor1-frame'
        run('link', ['gcc', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-no-pie', '-Wl,--gc-sections',
                     *[linux(path) for path in objects], '-lm', '-o', linux(binary)])
        text = run('execute', ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
                              'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', linux(binary), linux(out / 'input.bin'), linux(out / 'capture.bin')])
        match = re.fullmatch(r'FLOOR1_FRAME_CAPTURE cases=(\d+) refusals=(\d+) checks=(\d+) live=0 bytes=0\s*', text)
        need(match is not None and not (out / 'execute.stderr.log').read_bytes(), 'complete guarded capture without sanitizer diagnostics')
        body = (out / 'capture.bin').read_bytes()
        observed, counts = decode_output(body, model, capture)
        need(tuple(map(int, match.groups())) == tuple(counts[key] for key in ('cases', 'refusals', 'checks')), 'actual assertion/refusal counts')
        measured = compare(model, observed, expected)
        (out / 'measurement.json').write_text(json.dumps(measured, indent=2) + '\n', encoding='utf-8', newline='\n')
        report.update(measurement_completed=True, measurement_sha256=sha((out / 'measurement.json').read_bytes()),
                      capture_sha256=sha(body), controls=counts)
        save()
        need(measured['passed'] and measured['original_packets'] == 434, 'all exact frame fields, curves and product limbs')
        need(measured['absent_with_nonzero_residue'] > 0 and measured['present_zero_grid'] > 0 and
             measured['quiet_nonzero_channels'] > 0 and measured['floor0_API_refusals'] > 0,
             'silence/quiet/zero-grid/mixed-floor semantic controls exercised')
        need(all(sha(Path(path).read_bytes()) == pin['sha256'] == sha((out / pin['snapshot']).read_bytes())
                 for path, pin in inputs.items()), 'all frozen/original inputs unchanged')
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
