"""Exact generic floor1 product qualification with streamed integer witnesses.

The oracle parses the pinned upstream decimals as rational numbers and rounds
them directly to binary32, ties-to-even. No production table/parser/arithmetic
is used to construct expected products. All magnitude widths1..1087 and all256
factors meet both signed endpoints; separate rows cover constant curves,
small/zero/random/carry values, selected-channel isolation and refusals.
"""
import argparse, ast, hashlib, json, os, re, struct, subprocess, sys, time, uuid
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def linux(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def table_from_upstream(body):
    match = re.search(rb'static const float FLOOR1_fromdB_LOOKUP\[256\]=\{(.*?)\n\};', body, re.S)
    need(match is not None, 'one pinned upstream floor1 table')
    literals = [part.strip().decode('ascii').removesuffix('F') for part in match[1].split(b',') if part.strip()]
    need(len(literals) == 256, 'complete upstream table')
    result = []
    for literal in literals:
        value = Fraction(Decimal(literal))
        need(0 < value <= 1, 'finite positive table value')
        exponent = value.numerator.bit_length() - value.denominator.bit_length()
        power = Fraction(2) ** exponent
        if value < power:
            exponent -= 1
        scaled = value / (Fraction(2) ** (exponent - 23))
        mantissa, remainder = divmod(scaled.numerator, scaled.denominator)
        twice = 2 * remainder
        if twice > scaled.denominator or (twice == scaled.denominator and mantissa & 1):
            mantissa += 1
        if mantissa == 1 << 24:
            mantissa >>= 1
            exponent += 1
        bits = ((exponent + 127) << 23) | (mantissa - (1 << 23))
        exponent -= 23
        while not mantissa & 1:
            mantissa >>= 1
            exponent += 1
        result.append(dict(bits=bits, mantissa=mantissa, exponent=exponent))
    need(min(row['exponent'] for row in result) == -47 and result[-1] == dict(bits=0x3f800000, mantissa=1, exponent=0),
         'exact observed coefficient range and unity')
    return result


def cases():
    rows = []
    for width in range(1, 1088):
        channels = 3 if width % 97 == 0 else 1
        rows.append(dict(id=f'width-{width:04d}', width=width, indices=[i for i in range(256) for _ in range(2)],
                         channels=channels, channel=width % channels,
                         exponent=(-788, -64, 0, 235)[width % 4], pattern='endpoints',
                         controls=width in {1, 31, 32, 33, 63, 64, 65, 1079, 1087} or channels == 3))
    for limbs in range(1, 35):
        rows.append(dict(id=f'limb-patterns-{limbs:02d}', width=limbs * 32 - 1,
                         indices=[i for i in range(256) for _ in range(7)], channels=1, channel=0,
                         exponent=-788, pattern='patterns', controls=limbs in (1, 34)))
    for index in range(256):
        rows.append(dict(id=f'constant-{index:03d}', width=1087, indices=[index] * 7, channels=1,
                         channel=0, exponent=-788, pattern='patterns', controls=index in (0, 1, 255)))
        rows.append(dict(id=f'unit-{index:03d}', width=1, indices=[index], channels=1,
                         channel=0, exponent=0, pattern='one', controls=False))
    for name, exponent, indices in (
        ('underflow', -(1 << 31), [1, 0, 128, 255]),
        ('underflow-one', -(1 << 31) + 46, [1, 0, 128, 255]),
        ('minimum', -(1 << 31) + 47, [1, 0, 128, 255]),
        ('maximum', (1 << 31) - 1, [1, 0, 128, 255]),
        ('unity-minimum', -(1 << 31), [255] * 4),
        ('unity-maximum', (1 << 31) - 1, [255] * 4),
        ('quiet-underflow', -(1 << 31) + 45, [0] * 4),
        ('quiet-minimum', -(1 << 31) + 46, [0] * 4)):
        rows.append(dict(id='exponent-' + name, width=64, indices=indices, channels=1, channel=0,
                         exponent=exponent, pattern='patterns', controls=False))
    for width in (1, 31, 32, 33, 63, 64, 65, 1055, 1056, 1087):
        for sign in (-1, 1):
            rows.append(dict(id=f'invalid-domain-{width}-{sign}', width=width, indices=[1, 255, 0, 128, 64, 200, 5],
                             channels=1, channel=0, exponent=0, pattern='invalid', invalid_sign=sign, controls=False))
    for bins, channels in ((1, 1), (4096, 255)):
        rows.append(dict(id=f'zero-{bins}-{channels}', width=0, indices=[0] * bins, channels=channels,
                         channel=channels - 1, exponent=0, pattern='zero', controls=True))
    return rows


def shape(row):
    width, bins = row['width'], len(row['indices'])
    limbs = (width + 32) // 32 if width else 0
    return bins, row['channels'], row['channel'], limbs, width, row['exponent']


def sample(row, bin_index, channel):
    width = row['width']
    if not width:
        return 0
    maximum = (1 << width) - 1
    if channel != row['channel']:
        return -1 if channel & 1 else 1
    pattern = row['pattern']
    if pattern == 'one':
        return 1
    if pattern == 'endpoints':
        return maximum if bin_index % 2 == 0 else -maximum
    if pattern == 'invalid' and bin_index == len(row['indices']) - 1:
        return row['invalid_sign'] * (1 << width)
    values = (0, 1, -1, maximum, -maximum, (1 << (width - 1)) - 1,
              -(((bin_index + 1) * 0x9e3779b97f4a7c15 * (1 << max(0, width - 64)) + 0x123456789abcdef) & maximum))
    return values[bin_index % 7]


def expected_layout(row, table):
    bins, _, _, _, width, exponent = shape(row)
    if not width:
        return 0, dict(bins=bins, limbs=0, magnitude_bits=0, exponent=0, limb_count=0)
    low = min(table[index]['exponent'] for index in row['indices'])
    high = max(table[index]['exponent'] + (table[index]['mantissa'] - 1).bit_length() for index in row['indices'])
    output_exponent = exponent + low
    if not -(1 << 31) <= output_exponent < 1 << 31:
        return -2, None
    bits = width + high - low
    limbs = (bits + 32) // 32
    return 0, dict(bins=bins, limbs=limbs, magnitude_bits=bits, exponent=output_exponent, limb_count=bins * limbs)


def write_input(path, rows):
    with path.open('xb') as stream:
        stream.write(b'F1PROD01' + struct.pack('<I', len(rows)))
        for row in rows:
            bins, channels, channel, limbs, width, exponent = shape(row)
            stream.write(struct.pack('<IIIIIiI', bins, channels, channel, limbs, width, exponent, int(row['controls'])))
            stream.write(bytes(row['indices']))
            if not limbs:
                continue
            mask = (1 << (32 * limbs)) - 1
            for current_channel in range(channels):
                for bin_index in range(bins):
                    value = sample(row, bin_index, current_channel)
                    stream.write((value & mask).to_bytes(4 * limbs, 'little'))


def compare_capture(path, rows, table):
    metrics = dict(cases=len(rows), exact_samples=0, exact_limb_words=0, refused_rows=0,
                   magnitude_widths=1087, coefficient_count=256, maximum_limbs=0,
                   all_factor_width_signed_endpoint_pairs=1087 * 256 * 2)
    digest = hashlib.sha256()
    def take(stream, fmt):
        count = struct.calcsize('<' + fmt)
        body = stream.read(count)
        need(len(body) == count, 'complete capture fields')
        value = struct.unpack('<' + fmt, body)
        return value[0] if len(value) == 1 else value
    def layout(stream):
        return dict(zip(('bins', 'limbs', 'magnitude_bits', 'exponent', 'limb_count'), take(stream, 'IIIiQ')))
    with path.open('rb') as stream:
        need(take(stream, '8s') == b'F1OUT001' and take(stream, 'I') == len(rows), 'whole ordered capture')
        for index, row in enumerate(rows):
            status, wanted = expected_layout(row, table)
            need(take(stream, 'I') == index and take(stream, 'i') == status, 'measurement status: ' + row['id'])
            if status == 0:
                need(layout(stream) == wanted, 'measured exact layout: ' + row['id'])
            scale_status = -1 if row['pattern'] == 'invalid' else status
            need(take(stream, 'i') == scale_status, 'product status: ' + row['id'])
            if scale_status:
                metrics['refused_rows'] += 1
                continue
            need(layout(stream) == wanted, 'published exact layout: ' + row['id'])
            metrics['maximum_limbs'] = max(metrics['maximum_limbs'], wanted['limbs'])
            if not wanted['limbs']:
                continue
            nbytes = wanted['limbs'] * 4
            mask = (1 << (nbytes * 8)) - 1
            for bin_index, table_index in enumerate(row['indices']):
                coefficient = table[table_index]
                shift = row['exponent'] + coefficient['exponent'] - wanted['exponent']
                value = sample(row, bin_index, row['channel']) * coefficient['mantissa'] << shift
                body = stream.read(nbytes)
                need(body == (value & mask).to_bytes(nbytes, 'little'), 'exact product limbs: ' + row['id'])
                digest.update(body)
                metrics['exact_samples'] += 1
                metrics['exact_limb_words'] += wanted['limbs']
        metrics['refusal_controls'], metrics['runtime_assertions'] = take(stream, 'QQ')
        need(not stream.read(1), 'no trailing capture bytes')
    metrics['exact_limb_sha256'] = digest.hexdigest()
    metrics['passed'] = True
    return metrics


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
    report = dict(completed=False, passed=False, inputs=inputs, commands=[],
                  scope='Generic exact floor1 coefficient multiplication only.', sanitizers=['address', 'undefined'],
                  frame_integration=False, target_executed=False, production_radio_integration=False,
                  deferred_scopes_resumed=False, transform_executed=False, PCM_executed=False)
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
        for name in ('native_vorbis_numeric', 'native_vorbis_packet_frame', 'native_vorbis_floor1_product'):
            folder = ROOT / 'idf/components' / name
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    freeze(path, 'components/' + name + '/' + path.relative_to(folder).as_posix())
        freeze(ROOT / 'tests/native/vorbis_floor1_product_host.c', 'native/vorbis_floor1_product_host.c')
        upstream = freeze(ROOT / 'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/floor1.c', 'upstream-floor1.c')
        table = table_from_upstream(upstream)
        rows = cases()
        (out / 'cases.json').write_text(json.dumps(rows, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        (out / 'factors.json').write_text(json.dumps(table, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        write_input(out / 'input.bin', rows)
        report.update(prepared=True, cases=len(rows), model_sha256=sha((out / 'cases.json').read_bytes()),
                      input_sha256=sha((out / 'input.bin').read_bytes()), factors_sha256=sha((out / 'factors.json').read_bytes()))
        save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True, cases=len(rows))))
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
        names = ('native_vorbis_numeric', 'native_vorbis_packet_frame', 'native_vorbis_floor1_product')
        common = ['gcc', '-std=c11', '-O1', '-g', '-UNDEBUG', '-D_GNU_SOURCE=1', '-fno-fast-math', '-ffp-contract=off',
                  '-fno-pie', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer',
                  '-ffunction-sections', '-fdata-sections', '-MMD', '-Wall', '-Wextra', '-Werror',
                  *['-I' + linux(components / name / 'include') for name in names]]
        units = [components / names[-1] / 'floor1_product.c', out / 'sources/native/vorbis_floor1_product_host.c']
        objects = []
        for index, source in enumerate(units):
            obj = out / 'objects' / f'{index:02d}.o'
            objects.append(obj)
            run(f'compile-{index:02d}', [*common, '-c', linux(source), '-o', linux(obj)])
        binary = out / 'floor1-product'
        run('link', ['gcc', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-no-pie', '-Wl,--gc-sections',
                     *[linux(path) for path in objects], '-o', linux(binary)])
        text = run('execute', ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
                              'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', linux(binary), linux(out / 'input.bin'), linux(out / 'capture.bin')])
        match = re.fullmatch(r'FLOOR1_PRODUCT_CAPTURE cases=(\d+) refusals=(\d+) checks=(\d+)\s*', text)
        need(match is not None and not (out / 'execute.stderr.log').read_bytes(), 'complete guarded capture without sanitizer diagnostics')
        metrics = compare_capture(out / 'capture.bin', rows, table)
        need(tuple(map(int, match.groups())) == (len(rows), metrics['refusal_controls'], metrics['runtime_assertions']), 'actual capture/control counts')
        (out / 'measurement.json').write_text(json.dumps(metrics, indent=2) + '\n', encoding='utf-8', newline='\n')
        need(all(sha(Path(path).read_bytes()) == pin['sha256'] == sha((out / pin['snapshot']).read_bytes())
                 for path, pin in inputs.items()), 'all frozen inputs unchanged')
        need(report['model_sha256'] == sha((out / 'cases.json').read_bytes()) and
             report['input_sha256'] == sha((out / 'input.bin').read_bytes()) and
             report['factors_sha256'] == sha((out / 'factors.json').read_bytes()), 'predeclared witnesses unchanged')
        report.update(completed=True, passed=True, capture_sha256=sha((out / 'capture.bin').read_bytes()),
                      measurement_sha256=sha((out / 'measurement.json').read_bytes()),
                      binary_sha256=sha(binary.read_bytes()), units=len(units), measurements=metrics)
        save()
        print(json.dumps(dict(completed=True, passed=True, measurements=metrics)))
        return 0
    except BaseException as error:
        report.update(error=repr(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
