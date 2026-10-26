"""Exact setup-owner lifetime and allocation failure qualification.

Reuse the independent complete-setup oracle and original31 header pairs.
No Xiph DSP, audio decoder, transform or deferred fixture runs.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
NUMERIC = ROOT / 'idf/components/native_vorbis_numeric'
OWNER = ROOT / 'idf/components/native_vorbis_setup_owner'
ORIGINAL = ROOT / '.build/vorbis-xiph-prep-20261025-01/cases.json'
ORIGINAL_SHA = '32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def linux(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def flatten(exact, subject):
    values = []
    def word(value):
        need(type(value) is int and 0 <= value <= 0xffffffff, 'exact uint32 oracle word')
        values.append(value)
    def wide(value):
        need(type(value) is int and 0 <= value <= 0xffffffffffffffff, 'exact uint64 oracle field')
        word(value & 0xffffffff)
        word(value >> 32)
    layout = exact['layout']
    for key in subject.IDFIELDS:
        word(layout['identification'][key])
    for key in ('end_bit', 'codeword_count', 'multiplicand_count'):
        wide(layout[key])
    for key in subject.LFIELDS:
        word(layout[key])
    for book in exact['books']:
        info = book['layout']
        quant = info['quantization']
        wide(info['start_bit'])
        word(info['used_entries'])
        word(info['maximum_length'])
        for key in subject.QFIELDS[:7]:
            word(quant[key])
        for key in subject.QFIELDS[7:]:
            wide(quant[key])
        word(len(book['words']))
        for entry in book['words']:
            for key in ('code', 'entry', 'length'):
                word(entry[key])
        word(len(book['multiplicands']))
        for value in book['multiplicands']:
            word(value)
    word(len(exact['configuration']))
    for value in exact['configuration']:
        word(value)
    word(len(exact['getter_values']))
    for value in exact['getter_values']:
        word(value)
    return values


def cases(subject, public_fixture, original):
    need(sha(original) == ORIGINAL_SHA, 'unchanged original31 packet model')
    model, _ = subject.cases(public_fixture=public_fixture)
    rows = [dict(row) for row in model['cases']]
    originals = json.loads(original)
    need(len(originals['cases']) == 31, 'all original31 header pairs')
    for row in originals['cases']:
        rows.append(dict(id='original31-' + row['id'], identification_hex=row['identification_hex'],
                         identification_bits=4 * len(row['identification_hex']), setup_hex=row['setup_hex'],
                         setup_bits=4 * len(row['setup_hex']), original31=True))
    # Legal empty decode tables still carry a complete setup graph.
    for empty_words, empty_quant in ((False, True), (True, False), (True, True)):
        spec = subject.baseline()
        if empty_quant:
            spec['books'] = [dict(dimensions=1, lengths=[0 if empty_words else 1], lookup=0)]
            spec['floors'] = [spec['floors'][1]]
            spec['residues'][0].update(cascades=[0], books=[])
        elif empty_words:
            for book in spec['books']:
                book['lengths'] = [0]
        rows.append(subject.make_case(f'owner-empty-pools-{int(empty_words)}-{int(empty_quant)}', spec)[0])
    spec = subject.baseline()
    spec['books'][0]['lengths'] = [2, 0, 1, 0, 0, 3, 0, 3]
    spec['books'][1]['lengths'] = [2, 0, 1, 0, 0, 3, 0, 3]
    rows.append(subject.make_case('owner-original-sparse-indexes', spec)[0])
    output = []
    names = set()
    for row in rows:
        need(row['id'] not in names and re.fullmatch('[A-Za-z0-9_-]{1,80}', row['id']), 'unique case identity')
        names.add(row['id'])
        status, exact = 0, None
        try:
            identification = subject.identification(bytes.fromhex(row['identification_hex']), row['identification_bits'])
            exact = subject.parse_setup(bytes.fromhex(row['setup_hex']), row['setup_bits'], identification)
        except subject.Truncated:
            status = -3
        except subject.Invalid:
            status = -1
        if row.get('original31'):
            need(status == 0, 'owned parser must accept original31: ' + row['id'])
        output.append(dict(id=row['id'], identification_hex=row['identification_hex'],
                           identification_bits=row['identification_bits'], setup_hex=row['setup_hex'],
                           setup_bits=row['setup_bits'], status=status,
                           setup_end_bit=exact['layout']['end_bit'] if exact else 0,
                           expected=flatten(exact, subject) if exact else [],
                           original31=row.get('original31', False)))
    need(output[0]['status'] == 0 and len(names) == len(output), 'live baseline first')
    return dict(schema='vorbis-setup-owner-cases-v1', cases=output)


def target_header(model):
    lines = ['#pragma once', '#include <stddef.h>', '#include <stdint.h>',
             '#define OWNER_CASE_COUNT ' + str(len(model['cases'])),
             'typedef struct { uint64_t identification_bits, setup_bits, setup_end_bit; const char *id;',
             ' const uint8_t *identification; size_t identification_bytes; const uint8_t *setup; size_t setup_bytes; int status;',
             ' const uint32_t *expected; size_t expected_count; } owner_case_t;']
    for index, row in enumerate(model['cases']):
        for stem in ('identification', 'setup'):
            body = bytes.fromhex(row[stem + '_hex'])
            need(body, 'nonempty literal headers')
            lines.append('static const uint8_t owner_' + stem + '_' + str(index) + '[] = {' +
                         ','.join('UINT8_C(0x' + f'{value:02x}' + ')' for value in body) + '};')
        if row['expected']:
            lines.append('static const uint32_t owner_expected_' + str(index) + '[] = {' +
                         ','.join('UINT32_C(' + str(value) + ')' for value in row['expected']) + '};')
    lines.append('static const owner_case_t owner_cases[OWNER_CASE_COUNT] = {')
    for index, row in enumerate(model['cases']):
        fields = ['.id="' + row['id'] + '"']
        for stem in ('identification', 'setup'):
            fields += ['.' + stem + '=owner_' + stem + '_' + str(index),
                       '.' + stem + '_bytes=' + str(len(row[stem + '_hex']) // 2),
                       '.' + stem + '_bits=UINT64_C(' + str(row[stem + '_bits']) + ')']
        fields += ['.status=' + str(row['status']), '.setup_end_bit=UINT64_C(' + str(row['setup_end_bit']) + ')',
                   '.expected=' + ('owner_expected_' + str(index) if row['expected'] else 'NULL'),
                   '.expected_count=' + str(len(row['expected']))]
        lines.append(' {' + ','.join(fields) + '},')
    lines += ['};', '']
    return '\n'.join(lines).encode('ascii')


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
                  native_target_executed=False, Xiph_executed=False, DSP_executed=False,
                  audio_decoder_executed=False, deferred_scopes_resumed=False, production_radio_integration=False)
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
        for folder, label in ((NUMERIC, 'native_vorbis_numeric'), (OWNER, 'native_vorbis_setup_owner')):
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    freeze(path, 'components/' + label + '/' + path.relative_to(folder).as_posix())
        for name in ('vorbis_setup_owner_test.c', 'vorbis_setup_owner_test.h', 'vorbis_setup_owner_host.c'):
            freeze(ROOT / 'tests/native' / name, 'native/' + name)
        model_source = freeze(ROOT / 'tests/test-vorbis-setup.py', 'setup-oracle.py')
        subject = load(out / 'sources/setup-oracle.py', 'independent_setup_owner_oracle')
        public = freeze(ROOT / 'tests/target/cyd_vorbis_format_qemu/main/fixture.h', 'public-fixture.h')
        original = freeze(ORIGINAL, 'original31.json')
        model = cases(subject, public, original)
        (out / 'cases.json').write_text(json.dumps(model, separators=(',', ':')) + '\n', encoding='utf-8', newline='\n')
        (out / 'owner_cases.h').write_bytes(target_header(model))
        report.update(prepared=True, cases=len(model['cases']), valid_cases=sum(row['status'] == 0 for row in model['cases']),
                      oracle_sha256=sha(model_source), model_sha256=sha((out / 'cases.json').read_bytes()),
                      generated_header_sha256=sha((out / 'owner_cases.h').read_bytes()), original31_cases=31,
                      host_all_prefixes=True)
        save()
        if args.prepare_only:
            print(json.dumps({key: report[key] for key in ('prepared', 'cases', 'valid_cases', 'original31_cases', 'model_sha256')}))
            return 0
        origin = freeze(ROOT / 'tests/test-vorbis-floor1-render.py', 'supervisor-origin.py')
        supervisors = [ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == 'SUPERVISOR' for target in node.targets)]
        need(len(supervisors) == 1, 'one nonce-bound process supervisor')
        (out / 'supervisor.py').write_text(supervisors[0], encoding='utf-8', newline='\n')
        report['supervisor_sha256'] = sha((out / 'supervisor.py').read_bytes())
        report['compiler_version'] = run('compiler-version', ['gcc', '--version'])
        report['compiler_machine'] = run('compiler-machine', ['gcc', '-dumpmachine'])
        numeric = out / 'sources/components/native_vorbis_numeric'
        owner = out / 'sources/components/native_vorbis_setup_owner'
        native = out / 'sources/native'
        common = ['gcc', '-std=c11', '-O1', '-g', '-UNDEBUG', '-D_GNU_SOURCE=1', '-fno-fast-math', '-ffp-contract=off',
                  '-fno-pie', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer',
                  '-ffunction-sections', '-fdata-sections', '-MMD', '-Wall', '-Wextra', '-Werror',
                  *['-I' + linux(path) for path in (numeric / 'include', owner / 'include', native, out)]]
        units = [numeric / (name + '.c') for name in ('quant', 'codebook', 'setup')]
        units += [owner / 'setup_owner.c', native / 'vorbis_setup_owner_test.c', native / 'vorbis_setup_owner_host.c']
        objects = []
        for index, source in enumerate(units):
            obj = out / 'objects' / f'{index:02d}.o'
            objects.append(obj)
            run(f'compile-{index:02d}', [*common, '-c', linux(source), '-o', linux(obj)])
        binary = out / 'setup-owner'
        run('link', ['gcc', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-no-pie', '-Wl,--gc-sections',
                     *[linux(path) for path in objects], '-lm', '-o', linux(binary)])
        text = run('execute', ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
                              'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', linux(binary)])
        counts = re.fullmatch(r'OWNER_PASS cases=(\d+) checks=(\d+) successes=(\d+) parse_failures=(\d+) allocation_refusals=(\d+) live=0 bytes=0\s*', text)
        need(counts is not None and not (out / 'execute.stderr.log').read_bytes(), 'complete lifetime/failure result without sanitizer diagnostics')
        values = dict(zip(('cases', 'checks', 'successes', 'parse_failures', 'allocation_refusals'), map(int, counts.groups())))
        need(values['cases'] == report['cases'] and values['checks'] > 0 and values['allocation_refusals'] > 0, 'complete actual corpus and refusal controls')
        need(all(sha(Path(path).read_bytes()) == pin['sha256'] == sha((out / pin['snapshot']).read_bytes())
                 for path, pin in inputs.items()), 'all original and frozen inputs unchanged')
        need(sha((out / 'cases.json').read_bytes()) == report['model_sha256'] and
             sha((out / 'owner_cases.h').read_bytes()) == report['generated_header_sha256'], 'predeclared model/header unchanged')
        report.update(completed=True, passed=True, totals=values, binary_sha256=sha(binary.read_bytes()), units=len(units))
        save()
        print(json.dumps({key: report[key] for key in ('completed', 'passed', 'cases', 'valid_cases', 'original31_cases', 'totals')}))
        return 0
    except BaseException as error:
        report.update(error=repr(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
