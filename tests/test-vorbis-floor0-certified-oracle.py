"""Qualify the independent MPFR floor0 oracle, without selecting it on an MCU.

All 447 retained packet identities are accounted for. Active floor0 channels
are checked at every possible supplied Bark index; Bark indexing itself and
new PCM synthesis are deliberately separate requirements.
"""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time
import uuid
import zipfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'tests/results/vorbis-floor0-spectrum-20261028/captures.zip'
ARCHIVE_SHA = 'c45e814f94f3462be4d4e5d054253d8d5fdbbec24e15d29b605da8eb4c2d9fb0'
PINS = {
    'test-vorbis-setup.py': 'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff',
    'test-vorbis-floor-packet.py': '8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7',
    'test-vorbis-residue.py': '1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d',
    'vorbis_packet_frame_model.py': '5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9',
    'test-vorbis-packet-frame.py': '7c449b4b190500b0ab5931205f06e51e9f691112ebea80ac1affb7b200cb22d0',
}
SUPERVISOR_ORIGIN_SHA = 'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2'
AFFINE = ('minimum_bits', 'delta_bits', 'minimum_multiplier', 'delta_multiplier')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def linux(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if os.name == 'nt' else value


def load_readers():
    modules = {}
    for index, (name, pin) in enumerate(PINS.items()):
        path = ROOT / 'tests' / name
        need(sha(path.read_bytes()) == pin, 'unchanged pure reader: ' + name)
        spec = importlib.util.spec_from_file_location('gain_oracle_reader_' + str(index), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


def exact_inputs():
    """Use pinned saved C output only after matching the independent bit model."""
    body = ARCHIVE.read_bytes()
    need(sha(body) == ARCHIVE_SHA, 'complete retained 447-frame source archive')
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        model_body = archive.read('frame08/model.json')
        front_body = archive.read('frame08/front.bin')
    model = json.loads(model_body)
    modules = load_readers()
    setup = modules['test-vorbis-setup.py']
    floor = modules['test-vorbis-floor-packet.py']
    residue = modules['test-vorbis-residue.py']
    subject = modules['vorbis_packet_frame_model.py']
    front = modules['test-vorbis-packet-frame.py']
    observed, _ = front.decode_output(front_body, model)
    expected = [subject.expected_case(row, setup, floor, residue) for row in model['cases']]
    need(front.compare(model, observed, expected)['passed'], 'exact packet model agrees with saved actual C frames')
    need(len(observed) == 447 and sum(row['id'].startswith('original31-') for row in observed) == 434,
         'all original 434 and supplemental 13 packet identities')
    requests, lookup, identities, contexts = [], {}, [], {}

    def request(order, bark, size, amplitude, angles):
        key = (order, bark, size, amplitude['amplitude_bits'], amplitude['raw_amplitude'],
               amplitude['amplitude_offset'], tuple(tuple(value[key] for key in AFFINE) for value in angles))
        if key not in lookup:
            lookup[key] = len(requests)
            requests.append(dict(order=order, bark=bark, size=size, amplitude=dict(amplitude),
                                 angles=[dict(value) for value in angles]))
        return lookup[key]

    for case, actual in zip(model['cases'], observed):
        frame = actual['frame']
        need(frame is not None, 'retained packet really decoded')
        if case['setup_hex'] not in contexts:
            contexts[case['setup_hex']] = subject._context(case, setup)
        context = contexts[case['setup_hex']]
        channels = []
        for channel, state in enumerate(frame['floors']):
            entry = dict(channel=channel, type=state['type'], requests=[])
            if state['type'] != 0:
                entry['reason'] = 'floor1'
            elif not state['present']:
                entry['reason'] = 'absent floor0: no encoded LSP to import'
            else:
                info = floor.floor_info(context, state['floor_index'])
                if not info['rate'] or not info['bark']:
                    entry['reason'] = 'undefined active mapping remains separate'
                else:
                    angles = frame['floor0'][state['value_offset']:state['value_offset'] + state['value_count']]
                    need(len(angles) == info['order'], 'complete encoded affine LSPs')
                    entry['requests'] = [request(info['order'], bark, info['bark'], state['amplitude'], angles)
                                         for bark in range(info['bark'])]
                    entry['reason'] = 'every possible exact supplied Bark index'
            channels.append(entry)
        identities.append(dict(id=case['id'], channels=channels))
    return requests, identities, dict(model_sha256=sha(model_body), front_sha256=sha(front_body))


def special_inputs():
    amplitude = lambda bits, raw, offset: dict(amplitude_bits=bits, raw_amplitude=raw, amplitude_offset=offset)
    row = lambda name, order, bark, size, amp, angles: dict(id=name, order=order, bark=bark, size=size,
                                                         amplitude=amp, angles=angles)
    affine = lambda minimum, delta=0, mm=1, dm=0: dict(zip(AFFINE, (minimum, delta, mm, dm)))
    return [
        row('absent-bits0', 0, 0, 1, amplitude(0, 0, 255), []),
        row('order0-unity', 0, 0, 1, amplitude(63, (1 << 63) - 1, 255), []),
        row('order0-near-unity', 0, 0, 1, amplitude(63, (1 << 63) - 2, 1), []),
        row('order0-negative', 0, 0, 1, amplitude(8, 1, 60), []),
        row('pole', 1, 0, 1, amplitude(8, 1, 60), [affine(0)]),
        row('indeterminate', 1, 0, 1, amplitude(8, 1, 0), [affine(0)]),
        row('tiny-finite-1572bit-exponent', 1, 0, 1, amplitude(8, 1, 60), [affine(1)]),
        row('cancelled-affine-pole', 1, 0, 1, amplitude(8, 1, 60), [affine(1, 0x80000001, 7, 7)]),
        row('tiny-offset0-unity', 1, 0, 1, amplitude(8, 1, 0), [affine(1)]),
        row('largest-phase', 2, 32767, 65535, amplitude(63, (1 << 63) - 2, 255),
            [affine(0x7fffffff, 1, 0xffffffff, 1), affine(0xffffffff, 1, 0xffffffff, 1)]),
    ]


def protocol(row, precision):
    amplitude = row['amplitude']
    numbers = [precision, row['order'], row['bark'], row['size'], amplitude['amplitude_bits'],
               amplitude['raw_amplitude'], amplitude['amplitude_offset']]
    numbers.extend(value[key] for value in row['angles'] for key in AFFINE)
    return 'F0MPFR1 ' + ' '.join(map(str, numbers)) + '\n'


def dyadic(value):
    need(isinstance(value, dict) and set(value) == {'hex', 'exp2'}, 'strict exact dyadic object')
    integer, exponent = value['hex'], value['exp2']
    need(isinstance(integer, str) and re.fullmatch(r'-?(?:0|[1-9a-f][0-9a-f]*)', integer),
         'canonical signed hexadecimal integer')
    need(isinstance(exponent, int) and not isinstance(exponent, bool) and abs(exponent) <= 10000000,
         'bounded exact exported exponent')
    coefficient = int(integer, 16)
    return Fraction(coefficient << exponent) if exponent >= 0 else Fraction(coefficient, 1 << -exponent)


def enclosure(response):
    """JSON fields are explicitly checked; returned values never pass through float."""
    status = response['status']
    need(response['schema'] == 'F0MPFR1' and
         status in ('certified', 'absent', 'unity', 'pole', 'indeterminate', 'unresolved'), 'known mathematical status')
    if response.get('denominator') is not None:
        lower, upper = (dyadic(response['denominator'][key]) for key in ('lo', 'hi'))
        need(0 <= lower <= upper, 'ordered nonnegative denominator enclosure')
    if response.get('log2_gain') is None:
        need(status in ('absent', 'pole', 'indeterminate', 'unresolved'), 'explicit unavailable log gain')
        return None
    lower, upper = (dyadic(response['log2_gain'][key]) for key in ('lo', 'hi'))
    need(lower <= upper and status in ('certified', 'unity', 'unresolved'), 'ordered finite logarithm enclosure')
    floors = [int(response[key], 16) for key in ('floor_lo', 'floor_hi')]
    need(floors == [lower.numerator // lower.denominator, upper.numerator // upper.denominator],
         'full arbitrary-size integer floors, including negative fractions')
    need(response['floor_equal'] == (floors[0] == floors[1]), 'literal integer-floor decision')
    return lower, upper


def ln2_rational(terms=260):
    """ln2=2*atanh(1/3); exact positive geometric majorant bounds its tail."""
    total = sum((Fraction(2, (2 * k + 1) * 3 ** (2 * k + 1)) for k in range(terms)), Fraction())
    tail = Fraction(9, 4 * (2 * terms + 1) * 3 ** (2 * terms + 1))
    return total, total + tail


def analytical(row, response):
    bounds = enclosure(response)
    name = row.get('id')
    wanted = {'absent-bits0': 'absent', 'order0-unity': 'unity', 'pole': 'pole',
              'indeterminate': 'indeterminate', 'cancelled-affine-pole': 'pole', 'tiny-offset0-unity': 'unity'}
    if name in wanted:
        need(response['status'] == wanted[name], 'exact identity classification: ' + name)
    if row['order'] == 0 and bounds:
        amplitude = row['amplitude']
        maximum = (1 << amplitude['amplitude_bits']) - 1
        n = (Fraction(amplitude['raw_amplitude'] * amplitude['amplitude_offset'], maximum) -
             amplitude['amplitude_offset']) * Fraction(11512925, 100000000)
        lo_ln, hi_ln = ln2_rational()
        lo, hi = sorted((n / lo_ln, n / hi_ln))
        need(bounds[0] <= hi and bounds[1] >= lo, 'independent exact-rational order0 enclosure overlaps')
        need(dyadic(response['denominator']['lo']) == dyadic(response['denominator']['hi']) == 1,
             'order0 denominator exact identity')
    if name == 'tiny-finite-1572bit-exponent':
        need(bounds is not None and bounds[0] > (1 << 1571), 'finite witness exceeds machine-word exponent')
        need(int(response['floor_lo'], 16).bit_length() >= 1572 and response['floor_equal'],
             'certified arbitrary-length exponent split for finite tiny LSP')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mpfr-prefix', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out, prefix = args.output.resolve(), args.mpfr_prefix.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh task-local output')
    need(prefix.is_relative_to(ROOT / '.build'), 'local pinned MPFR build, no guessed runtime ABI')
    out.mkdir(parents=True)
    report = dict(completed=False, passed=False, commands=[], sources={}, production_selected=False,
                  oracle_only=True, new_PCM_executed=False, native_executed=False, original_frame_cases=447)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')

    def freeze(path, name):
        body = Path(path).read_bytes()
        destination = out / 'sources' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)
        report['sources'][name] = sha(body)
        return destination

    def run(name, argv, expected=0, timeout=180):
        nonce = uuid.uuid4().hex
        request, receipt, stop = [out / (name + suffix) for suffix in ('.request.json', '.receipt.json', '.stop')]
        request.write_text(json.dumps(dict(nonce=nonce, argv=list(map(str, argv)), timeout=timeout,
                                          receipt=linux(receipt), stop=linux(stop))), encoding='utf-8')
        command = (['wsl.exe', '--exec', 'python3'] if os.name == 'nt' else [sys.executable]) + [
            linux(out / 'supervisor.py'), linux(request)]
        row = dict(name=name, argv=command, child_argv=list(map(str, argv)), nonce=nonce,
                   request_sha256=sha(request.read_bytes()), expected_exit=expected)
        report['commands'].append(row)
        save()
        child = None
        started = time.monotonic()
        try:
            with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
                child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                         creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                row['transport_pid'] = child.pid
                child.wait(timeout=timeout + 20)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce, encoding='ascii')
                try:
                    child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
                    row['forced_transport_stop'] = True
            result = json.loads(receipt.read_bytes()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic() - started, supervisor=result,
                       transport_exit=None if child is None else child.poll())
            save()
        need(row['transport_exit'] == 0 and not row.get('forced_transport_stop'), 'owned oracle transport terminal: ' + name)
        need(result.get('nonce') == nonce and result.get('request_sha256') == row['request_sha256'] and
             result.get('state') == 'terminal' and result.get('final') and result.get('new_session') and
             result.get('child_pid') == result.get('owned_pgid') and result.get('child_reaped') and
             result.get('group_gone') and result.get('child_returncode') == expected,
             'owned oracle child terminal: ' + name)
        return (out / (name + '.stdout.log')).read_text('utf-8')

    save()
    try:
        freeze(Path(__file__), 'runner.py')
        oracle = freeze(ROOT / 'tools/codec_benchmark/vorbis_floor0_mpfr_oracle.c', 'oracle.c')
        header = freeze(prefix / 'include/mpfr.h', 'mpfr.h')
        library = freeze(prefix / 'lib/libmpfr.a', 'libmpfr.a')
        manifest = json.loads(freeze(ROOT / 'tools/codec_benchmark/vorbis_floor0_mpfr_oracle.sources.json',
                                     'oracle.sources.json').read_bytes())
        dependency_path = ROOT / manifest['dependency_build']['path']
        dependency = freeze(dependency_path, 'dependency-build-report.json')
        need(sha(dependency.read_bytes()) == manifest['dependency_build']['sha256'], 'pinned dependency build receipt')
        dependency_report = json.loads(dependency.read_bytes())
        need(len(dependency_report['commands']) == 5 and all(row['exit_code'] == 0 for row in dependency_report['commands']),
             'all actual dependency build commands terminal0')
        installed = {row['path']: row for row in dependency_report['installed_files']}
        for path, label in ((header, 'install/include/mpfr.h'), (library, 'install/lib/libmpfr.a')):
            need(sha(path.read_bytes()) == installed[label]['sha256'] and path.stat().st_size == installed[label]['bytes'],
                 'compiled real MPFR input matches dependency build')
        for item in manifest['sources']:
            need(sha((ROOT / item['path']).read_bytes()) == item['sha256'], 'independent reference source pin: ' + item['path'])
        report['mpfr_prefix'] = str(prefix)
        for name in PINS:
            freeze(ROOT / 'tests' / name, 'readers/' + name)
        origin = freeze(ROOT / 'tests/test-vorbis-floor1-render.py', 'supervisor-origin.py').read_bytes()
        need(sha(origin) == SUPERVISOR_ORIGIN_SHA, 'owned supervisor source identity')
        templates = [ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == 'SUPERVISOR' for target in node.targets)]
        need(len(templates) == 1 and templates[0].count('assert 0<timeout<=60') == 1, 'single timeout derivation')
        (out / 'supervisor.py').write_text(templates[0].replace('assert 0<timeout<=60', 'assert 0<timeout<=180'),
                                          encoding='utf-8', newline='\n')
        report['supervisor_sha256'] = sha((out / 'supervisor.py').read_bytes())
        requests, identities, source_pins = exact_inputs()
        requests += special_inputs()
        (out / 'requests.json').write_text(json.dumps(requests, indent=2) + '\n', encoding='utf-8')
        (out / 'identities.json').write_text(json.dumps(identities, indent=2) + '\n', encoding='utf-8')
        report.update(source_archive_sha256=ARCHIVE_SHA, retained_source=source_pins,
                      unique_requests=len(requests), request_sha256=sha((out / 'requests.json').read_bytes()),
                      identities_sha256=sha((out / 'identities.json').read_bytes()))
        save()
        if args.prepare_only:
            report['prepared_only'] = True
            save()
            print(json.dumps(dict(prepared=True, requests=len(requests), packets=len(identities))))
            return 0
        report['compiler_version'] = run('compiler-version', ['gcc', '--version'])
        run('compile', ['gcc', '-std=c11', '-O1', '-g', '-UNDEBUG', '-Wall', '-Wextra', '-Werror',
                        '-fno-fast-math', '-ffp-contract=off', '-fno-pie', '-no-pie', '-fsanitize=address,undefined',
                        '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-I' + linux(header.parent),
                        linux(oracle), linux(library), '-lgmp', '-lm', '-o', linux(out / 'oracle')])
        executable = ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1',
                      'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', linux(out / 'oracle')]
        version = run('oracle-version', executable + ['--version'])
        need(re.fullmatch(r'F0MPFR1 MPFR=4\.2\.2 GMP=[0-9.]+\n', version), 'actual pinned MPFR version')
        report['oracle_version'] = version.strip()
        budgeted = executable + ['--max-precision', '8192']
        budget_path = out / 'budget-control.txt'
        budget_path.write_text(protocol(special_inputs()[1], 8193), encoding='ascii')
        budget_lines = run('budget-control', budgeted + [linux(budget_path)]).splitlines()
        need(len(budget_lines) == 1 and json.loads(budget_lines[0])['status'] == 'resource' and
             json.loads(budget_lines[0])['reason'] == 'caller_precision_budget', 'caller budget stops before MPFR allocation')
        valid = protocol(special_inputs()[1], 256).encode('ascii')
        bad_lines = [b'\n', b'F0MPFR2 256 0 0 1 8 1 60\n', b'F0MPFR1 0 0 0 1 8 1 60\n',
                     b'F0MPFR1 0256 0 0 1 8 1 60\n', b'F0MPFR1 256 256 0 1 8 1 60\n',
                     b'F0MPFR1 256 0 1 1 8 1 60\n', b'F0MPFR1 256 0 0 0 8 1 60\n',
                     b'F0MPFR1 256 0 0 1 64 1 60\n', b'F0MPFR1 256 0 0 1 8 256 60\n',
                     b'F0MPFR1 256 0 0 1 8 1 256\n', b'F0MPFR1 256 1 0 1 8 1 60\n',
                     b'F0MPFR1 256 0 0 1 8 1 60 extra\n', valid[:-1] + b'\x00\n',
                     valid[:-1] + b'\xff\n', b'x' * 32768 + b'\n']
        controls_path = out / 'protocol-controls.txt'
        controls_path.write_bytes(b''.join(bad_lines) + valid + valid[:-1])
        controls = [json.loads(line) for line in run('protocol-controls', budgeted + [linux(controls_path)], expected=2).splitlines()]
        need(len(controls) == len(bad_lines) + 2 and all(row['ordinal'] == i + 1 for i, row in enumerate(controls)),
             'invalid complete records and final partial record preserve exact protocol ordinals')
        need(all(row['status'] == 'invalid' and row['reason'] == 'protocol'
                 for row in controls[:len(bad_lines)] + controls[-1:]) and
             controls[-2]['status'] == 'unity' and not (out / 'protocol-controls.stderr.log').read_bytes(),
             'all malformed records rejected, valid middle record retained, no sanitizer diagnostics')
        report['protocol_refusals'] = len(bad_lines) + 1
        captures = {}
        for precision in (256, 512):
            input_path = out / ('input-' + str(precision) + '.txt')
            input_path.write_text(''.join(protocol(row, precision) for row in requests), encoding='ascii', newline='\n')
            text = run('execute-' + str(precision), budgeted + [linux(input_path)])
            need(not (out / ('execute-' + str(precision) + '.stderr.log')).read_bytes(), 'oracle sanitizer stderr empty')
            rows = [json.loads(line) for line in text.splitlines()]
            need(len(rows) == len(requests), 'exact complete output row count')
            for ordinal, response in enumerate(rows, 1):
                need(response['ordinal'] == ordinal and response['precision'] == precision, 'exact oracle ordinal and precision')
                enclosure(response)
            captures[precision] = rows
        nested = unresolved = 0
        for index, row in enumerate(requests):
            low, high = captures[256][index], captures[512][index]
            a, b = enclosure(low), enclosure(high)
            if a is not None and b is not None:
                need(a[0] <= b[0] <= b[1] <= a[1], 'directed precision refinement nests')
                nested += 1
            elif b is None:
                unresolved += int(high['status'] == 'unresolved')
            if row.get('id') != 'tiny-finite-1572bit-exponent':
                analytical(row, high)
        refinements = []
        for index, row in enumerate(requests):
            response = captures[512][index]
            if response['status'] != 'unresolved' and (response.get('floor_equal') or response['status'] in ('absent', 'pole', 'indeterminate')):
                continue
            previous = enclosure(response)
            for precision in (1024, 2048, 4096, 8192):
                path = out / ('refine-' + str(index) + '-' + str(precision) + '.txt')
                path.write_text(protocol(row, precision), encoding='ascii', newline='\n')
                name = path.stem
                lines = run(name, budgeted + [linux(path)]).splitlines()
                need(len(lines) == 1 and not (out / (name + '.stderr.log')).read_bytes(), 'single clean refinement response')
                response = json.loads(lines[0])
                current = enclosure(response)
                if previous is not None and current is not None:
                    need(previous[0] <= current[0] <= current[1] <= previous[1], 'adaptive bounds remain enclosed')
                previous = current
                refinements.append(dict(request=index, precision=precision, status=response['status'],
                                        floor_equal=response.get('floor_equal')))
                if current is not None and response['floor_equal']:
                    break
            need(response['status'] in ('certified', 'unity') and response['floor_equal'], 'finite test request resolves without narrowing exponent')
            analytical(row, response)
        report.update(completed=True, passed=True, nested_enclosures=nested,
                      initial_unresolved=unresolved, refinements=refinements)
        save()
        print(json.dumps({key: report[key] for key in ('passed', 'unique_requests', 'original_frame_cases',
                                                      'nested_enclosures', 'initial_unresolved', 'refinements')}))
        return 0
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
