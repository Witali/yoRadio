"""Differential VQ range audit, with exact dyadic oracles and retained gaps.

This is a baseline measurement, not a decoder-conformance pass. It compares
the current Xiph candidate and the existing owned quantization API. It never
initializes a DSP, decodes audio, or executes a deferred fixture.
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
BASE = ROOT / 'idf/components/native_vorbis_xiph'
PORT = ROOT / 'idf/components/native_vorbis_xiph_port'
NUMERIC = ROOT / 'idf/components/native_vorbis_numeric'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def linux(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def unpack(word, clamp=False):
    mantissa = word & 0x1fffff
    if word & 0x80000000:
        mantissa = -mantissa
    exponent = ((word >> 21) & 1023) - 788
    if clamp:
        exponent = max(-63, min(63, exponent))
    return Fraction(mantissa * (1 << exponent)) if exponent >= 0 else Fraction(mantissa, 1 << -exponent)


def rounded_integer(numerator, denominator):
    integer, remainder = divmod(numerator, denominator)
    return integer + (2 * remainder > denominator or
                      (2 * remainder == denominator and integer % 2))


def binary32(value):
    """Round a rational directly to IEEE binary32, ties to even (no double rounding)."""
    sign = 0x80000000 if value < 0 else 0
    numerator, denominator = abs(value.numerator), value.denominator
    if not numerator:
        return 0
    exponent = numerator.bit_length() - denominator.bit_length()
    if (numerator < denominator << exponent if exponent >= 0
            else numerator << -exponent < denominator):
        exponent -= 1
    if exponent > 127:
        return sign | 0x7f800000
    unit = max(exponent - 23, -149)
    significand = rounded_integer(numerator, denominator << unit) if unit >= 0 else rounded_integer(numerator << -unit, denominator)
    if significand >= 1 << 24:
        significand >>= 1
        exponent += 1
    if exponent > 127:
        return sign | 0x7f800000
    if exponent < -126:
        return sign | significand
    return sign | ((exponent + 127) << 23) | (significand - (1 << 23))


def float_value(bits):
    need(bits & 0x7f800000 != 0x7f800000, 'finite captured float')
    return Fraction.from_float(struct.unpack('<f', struct.pack('<I', bits))[0])


def root(entries, dimensions):
    low, high = 1, entries
    while low < high:
        middle = (low + high + 1) // 2
        if middle ** dimensions <= entries:
            low = middle
        else:
            high = middle - 1
    return low


def packed(exponent, mantissa=1, negative=False):
    need(-788 <= exponent <= 235 and 0 <= mantissa < 1 << 21, 'packed field range')
    return (int(negative) << 31) | ((exponent + 788) << 21) | mantissa


def cases():
    words = [sign | (exponent << 21) | mantissa
             for sign in (0, 0x80000000) for exponent in range(1024)
             for mantissa in (0, 1, 2, (1 << 20) - 1, 1 << 20, (1 << 20) + 1, (1 << 21) - 1)]
    books = []

    def add(name, lookup, sequence, dim, entries, minimum, delta, quant):
        need(len(quant) == (root(entries, dim) if lookup == 1 else dim * entries), 'complete multiplicands')
        books.append(dict(id=name, maptype=lookup, sequence=sequence, dimensions=dim,
                          entries=entries, minimum=minimum, delta=delta, quant=quant))

    # Every exponent and sign reaches both actual table-generation branches.
    for lookup in (1, 2):
        for sign in (0, 0x80000000):
            for exponent in range(1024):
                word = sign | (exponent << 21) | (1, 0x100001, 0x1fffff)[exponent % 3]
                for field in ('minimum', 'delta'):
                    add(f'field-{lookup}-{sign >> 31}-{exponent}-{field}', lookup, 0, 1, 1,
                        word if field == 'minimum' else 0, word if field == 'delta' else 0, [65535])
    for lookup in (1, 2):
        for sequence in (0, 1):
            for minimum, delta, label in (
                (packed(-64), 0, 'small-exact'),
                (packed(64), 0, 'large-exact'),
                (packed(128, negative=True), packed(127), 'cross-exponent-cancel'),
                (packed(128, negative=True), packed(128), 'same-exponent-cancel'),
                (packed(-788, negative=True), packed(235, 0x1fffff), 'full-span'),
                (packed(235, 0x1fffff, True), packed(-788), 'reversed-span'),
                (packed(-1, 3, True), packed(-1), 'ordinary')):
                dim, entries = (3, 27) if lookup == 1 else (3, 3)
                count = root(entries, dim) if lookup == 1 else dim * entries
                quant = [0, 1, 2] if lookup == 1 else [0, 1, 2, 2, 4, 8, 65535, 1, 0]
                need(len(quant) == count, 'declared mixed table extent')
                add(f'{label}-{lookup}-{sequence}', lookup, sequence, dim, entries, minimum, delta, quant)
            count = 1 if lookup == 1 else 65535
            add(f'full-dimension-{lookup}-{sequence}', lookup, sequence, 65535, 1,
                packed(0, 3, True), packed(0), [65535] * count)
    add('lookup1-leftover-entry16', 1, 0, 2, 17, packed(0, 3, True), packed(0), [7, 3, 5, 1])
    return dict(schema='xiph-vq-range-input-v1', words=words, books=books)


def input_bytes(model):
    body = bytearray(b'XIPHVQ01')
    def put(*values):
        body.extend(struct.pack('<' + 'I' * len(values), *values))
    put(len(model['words']))
    put(*model['words'])
    put(len(model['books']))
    for book in model['books']:
        put(*(book[k] for k in ('maptype', 'sequence', 'dimensions', 'entries', 'minimum', 'delta')),
            len(book['quant']))
        put(*book['quant'])
    return bytes(body)


def affine_rows(book):
    dimensions = book['dimensions']
    q = root(book['entries'], dimensions) if book['maptype'] == 1 else 0
    for entry in range(book['entries']):
        minimum_multiplier = delta_multiplier = 0
        remainder = entry
        for component in range(dimensions):
            index = remainder % q if q else entry * dimensions + component
            if q:
                remainder //= q
            minimum_multiplier += 1
            delta_multiplier += book['quant'][index]
            yield (book['minimum'], book['delta'], minimum_multiplier, delta_multiplier)
            if not book['sequence']:
                minimum_multiplier = delta_multiplier = 0


def measure(model, capture):
    at = 8
    need(capture[:8] == b'XIPHVQO1', 'VQ capture magic')
    def take(count=1):
        nonlocal at
        need(at + count * 4 <= len(capture), 'complete capture field')
        values = struct.unpack_from('<' + 'I' * count, capture, at)
        at += count * 4
        return values[0] if count == 1 else values
    need(take() == len(model['words']), 'all declared scalar words')
    scalar_mismatches = representable_mismatches = zero_words = 0
    witnesses = []
    for word in model['words']:
        captured_word, actual = take(2)
        need(captured_word == word, 'scalar identity/order')
        expected_clamped = binary32(unpack(word, True))
        if not word & 0x1fffff:
            expected_clamped |= word & 0x80000000
            zero_words += 1
        need(actual == expected_clamped, 'actual inherited Xiph clamp model')
        exact = unpack(word)
        if float_value(actual) != exact:
            scalar_mismatches += 1
            rounded = binary32(exact)
            if rounded & 0x7f800000 != 0x7f800000 and float_value(rounded) == exact:
                representable_mismatches += 1
        if word in (0x5a800001, 0x6a800001, 0x00000001):
            witnesses.append(dict(word=f'{word:08x}', actual_binary32=f'{actual:08x}',
                                  exact_numerator=str(exact.numerator), exact_denominator=str(exact.denominator)))
    need(take() == len(model['books']), 'all declared VQ tables')
    values = book_mismatches = exact_components = 0
    clamp_altered_components = clamped_rounding_components = 0
    book_results = []
    for index, book in enumerate(model['books']):
        count = book['entries'] * book['dimensions']
        need(take(2) == (index, count), 'complete ordered table identity/extent')
        mismatches = representable = clamp_altered = clamped_rounding = 0
        rows = affine_rows(book)
        for expected_affine in rows:
            actual, minimum, delta, minimum_multiplier, delta_multiplier = take(5)
            need((minimum, delta, minimum_multiplier, delta_multiplier) == expected_affine,
                 'owned affine values equal the independent integer recurrence')
            exact = unpack(minimum) * minimum_multiplier + unpack(delta) * delta_multiplier
            clamped_exact = unpack(minimum, True) * minimum_multiplier + unpack(delta, True) * delta_multiplier
            exact_components += 1
            clamp_altered += exact != clamped_exact
            clamped_rounding += float_value(actual) != clamped_exact
            if float_value(actual) != exact:
                mismatches += 1
                rounded = binary32(exact)
                if rounded & 0x7f800000 != 0x7f800000 and float_value(rounded) == exact:
                    representable += 1
        values += count
        book_mismatches += mismatches
        clamp_altered_components += clamp_altered
        clamped_rounding_components += clamped_rounding
        book_results.append(dict(id=book['id'], values=count, mismatches=mismatches,
                                 exactly_binary32_representable_mismatches=representable,
                                 field_clamp_changes_exact_value=clamp_altered,
                                 current_float_differs_from_exact_clamped_recurrence=clamped_rounding))
    need(at == len(capture), 'no missing or trailing capture bytes')
    need(scalar_mismatches > 0 and representable_mismatches > 0 and book_mismatches > 0,
         'current range gaps remain visible, never relabelled conformant')
    need(zero_words == 2048 and len(witnesses) == 3, 'all signed exponent-zero fields and named witnesses')
    return dict(scalars=len(model['words']), books=len(model['books']), values=values,
                exact_affine_components=exact_components, signed_zero_words=zero_words,
                scalar_mismatches=scalar_mismatches,
                exactly_binary32_representable_scalar_mismatches=representable_mismatches,
                table_component_mismatches=book_mismatches,
                field_clamp_altered_components=clamp_altered_components,
                current_float_differs_from_exact_clamped_recurrence=clamped_rounding_components,
                witnesses=witnesses,
                tables=book_results, xiph_full_vq_range_conformant=False,
                owned_quantization_exact=True)


def self_test():
    for value, bits in ((Fraction(0), 0), (Fraction(1), 0x3f800000),
                        (Fraction(-1), 0xbf800000), (Fraction(1, 1 << 149), 1),
                        (Fraction(1, 1 << 150), 0), (Fraction(3, 1 << 150), 2),
                        (Fraction(1, 1 << 126), 0x00800000),
                        (Fraction((1 << 24) - 1) * (1 << 104), 0x7f7fffff),
                        (Fraction(1 << 128), 0x7f800000),
                        (Fraction(1) + Fraction(1, 1 << 24), 0x3f800000),
                        (Fraction(1) + Fraction(3, 1 << 24), 0x3f800002)):
        need(binary32(value) == bits, 'independent rounding boundary self-test')
    need(unpack(0x5a800001) == Fraction(1, 1 << 64) and
         unpack(0x6a800001) == 1 << 64, 'named packed witnesses')
    need(unpack(packed(128, negative=True)) + 2 * unpack(packed(127)) == 0,
         'exact cancellation before any float conversion')
    need(root(17, 2) == 4 and root(1, 65535) == 1, 'integer root boundary controls')
    print('VQ_RANGE_ORACLE_PASS controls=14')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--port-manifest-sha256')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    need(args.output is not None and args.port_manifest_sha256, 'output and reviewed port required')
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and out != ROOT / '.build' and not out.exists(), 'fresh task-local output')
    need(sha((PORT / 'port-manifest.json').read_bytes()) == args.port_manifest_sha256, 'reviewed source identity')
    out.mkdir(parents=True)
    (out / 'objects').mkdir()
    inputs = {}
    report = dict(completed=False, measurement_valid=False, inputs=inputs, commands=[],
                  sanitizers=['address', 'undefined'], physical_device=False,
                  DSP_executed=False, audio_decoder_executed=False, target_executed=False,
                  deferred_scopes_resumed=False, production_radio_integration=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    def freeze(path, name):
        body = path.read_bytes()
        destination = out / 'sources' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)
        inputs[str(path.resolve())] = dict(sha256=sha(body), snapshot=destination.relative_to(out).as_posix())
        return body
    def run(name, argv):
        nonce = uuid.uuid4().hex
        request, receipt, stop = (out / (name + suffix) for suffix in ('.request.json', '.receipt.json', '.stop'))
        request.write_text(json.dumps(dict(nonce=nonce, argv=list(map(str, argv)), timeout=60,
                                          receipt=linux(receipt), stop=linux(stop))), encoding='utf-8')
        command = (['wsl.exe', '--exec', 'python3'] if sys.platform == 'win32' else [sys.executable]) + [linux(out / 'supervisor.py'), linux(request)]
        row = dict(name=name, argv=command, child_argv=list(map(str, argv)), nonce=nonce,
                   request_sha256=sha(request.read_bytes()))
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
        for folder, label in ((BASE, 'components/native_vorbis_xiph'),
                              (PORT, 'components/native_vorbis_xiph_port'),
                              (NUMERIC, 'components/native_vorbis_numeric')):
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    freeze(path, label + '/' + path.relative_to(folder).as_posix())
        for name in ('vorbis_xiph_alloc.h', 'vorbis_xiph_alloc_inject.h', 'vorbis_xiph_alloc.c', 'vorbis_xiph_vq_range_host.c'):
            freeze(ROOT / 'tests/native' / name, 'native/' + name)
        origin = freeze(ROOT / 'tests/test-vorbis-floor1-render.py', 'supervisor-origin.py')
        supervisors = [ast.literal_eval(node.value) for node in ast.parse(origin).body
                       if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'SUPERVISOR' for target in node.targets)]
        need(len(supervisors) == 1, 'one owned nonce-bound supervisor')
        (out / 'supervisor.py').write_text(supervisors[0], encoding='utf-8', newline='\n')
        report['supervisor_sha256'] = sha((out / 'supervisor.py').read_bytes())
        model = cases()
        (out / 'cases.json').write_text(json.dumps(model, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        (out / 'input.bin').write_bytes(input_bytes(model))
        report.update(cases_sha256=sha((out / 'cases.json').read_bytes()), input_sha256=sha((out / 'input.bin').read_bytes()))
        preparer = out / 'sources/components/native_vorbis_xiph_port/prepare.py'
        spec = importlib.util.spec_from_file_location('owned_vq_range_prepare', preparer)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generated = out / 'generated'
        porting = module.materialize(out / 'sources/components/native_vorbis_xiph', out / 'sources/components/native_vorbis_xiph_port', generated)
        report['porting'] = porting
        need(porting['port_manifest_sha256'] == args.port_manifest_sha256, 'executed frozen port identity')
        report['compiler_version'] = run('compiler-version', ['gcc', '--version'])
        report['compiler_machine'] = run('compiler-machine', ['gcc', '-dumpmachine'])
        native = out / 'sources/native'
        numeric = out / 'sources/components/native_vorbis_numeric'
        includes = [generated / 'ported/include', generated / 'base/upstream/libogg/include',
                    generated / 'base/platform', generated / 'base/upstream/libvorbis/lib',
                    generated / 'ported', numeric / 'include', native]
        common = ['gcc', '-std=c11', '-O1', '-g', '-UNDEBUG', '-D_GNU_SOURCE=1', '-DHAVE_ALLOCA_H=1',
                  '-fno-fast-math', '-ffp-contract=off', '-fno-pie', '-fsanitize=address,undefined',
                  '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-ffunction-sections', '-fdata-sections', '-MMD',
                  *['-I' + linux(path) for path in includes]]
        objects = []
        # This audit needs only table expansion. No DSP/audio implementation links.
        selected = [unit for unit in porting['compiled_units'] if unit['original'].endswith('/sharedbook.c')]
        need(len(selected) == 1, 'one actual table implementation')
        for index, unit in enumerate(selected):
            obj = out / 'objects' / f'library-{index:02d}.o'
            objects.append(obj)
            run(f'compile-library-{index:02d}', [*common, '-include', linux(native / 'vorbis_xiph_alloc_inject.h'), '-c', linux(generated / unit['compiled']), '-o', linux(obj)])
        for name, source in (('alloc', native / 'vorbis_xiph_alloc.c'), ('quant', numeric / 'quant.c'),
                             ('capture', native / 'vorbis_xiph_vq_range_host.c')):
            obj = out / 'objects' / (name + '.o')
            objects.append(obj)
            run('compile-' + name, [*common, '-Wall', '-Wextra', '-Werror', '-c', linux(source), '-o', linux(obj)])
        binary = out / 'vq-range'
        run('link', ['gcc', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-no-pie',
                     '-Wl,--gc-sections', *[linux(path) for path in objects], '-lm', '-o', linux(binary)])
        capture = out / 'capture.bin'
        text = run('execute', ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
                               'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', linux(binary), linux(out / 'input.bin'), linux(capture)])
        counts = re.fullmatch(r'VQ_RANGE_CAPTURE scalars=(\d+) books=(\d+) values=(\d+) live=0 bytes=0\s*', text)
        need(counts is not None and not (out / 'execute.stderr.log').read_bytes(), 'complete sanitized capture without diagnostics')
        measured = measure(model, capture.read_bytes())
        need(tuple(map(int, counts.groups())) == tuple(measured[key] for key in ('scalars', 'books', 'values')), 'matching actual capture and oracle counts')
        (out / 'measurement.json').write_text(json.dumps(measured, indent=2) + '\n', encoding='utf-8', newline='\n')
        need(all(sha(Path(path).read_bytes()) == pin['sha256'] == sha((out / pin['snapshot']).read_bytes())
                 for path, pin in inputs.items()), 'all original and frozen sources unchanged')
        report.update(completed=True, measurement_valid=True, xiph_full_vq_range_conformant=False,
                      owned_quantization_exact=True, scalar_mismatches=measured['scalar_mismatches'],
                      exactly_binary32_representable_scalar_mismatches=measured['exactly_binary32_representable_scalar_mismatches'],
                      table_component_mismatches=measured['table_component_mismatches'],
                      field_clamp_altered_components=measured['field_clamp_altered_components'],
                      current_float_differs_from_exact_clamped_recurrence=measured['current_float_differs_from_exact_clamped_recurrence'],
                      scalars=measured['scalars'], books=measured['books'], values=measured['values'],
                      binary_sha256=sha(binary.read_bytes()), capture_sha256=sha(capture.read_bytes()),
                      measurement_sha256=sha((out / 'measurement.json').read_bytes()))
        save()
        print(json.dumps({key: report[key] for key in ('completed', 'measurement_valid', 'xiph_full_vq_range_conformant',
                                                      'owned_quantization_exact', 'scalars', 'books', 'values', 'scalar_mismatches',
                                                      'exactly_binary32_representable_scalar_mismatches', 'table_component_mismatches')}))
        return 0
    except BaseException as error:
        report.update(error=repr(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
