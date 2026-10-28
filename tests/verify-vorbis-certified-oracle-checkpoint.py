#!/usr/bin/env python3
"""Pure saved-evidence replay: no archived code, extraction, compiler or math child."""
from __future__ import annotations

import argparse
import ast
import collections
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/vorbis-certified-oracle-20261028'
ARCHIVE_SHA = 'f0040b4512daeea2f4e690e6d8f3f6378e645ef616065622de39b80f683264db'
MANIFEST_SHA = '910574cdb63aca2cac52db07952df810ae7e6feda6477643c90a17fea0cd5c1d'
RUNNER_SHA = 'f34cf3eacdaf02d0e1fcd5a8a08063e69aa302ad1f8b3f4f8704b40bed20fdbb'
ORACLE_SHA = 'a5b20411d709d8b255f23909d6f618ec56cd85219aa7b7e08b69dd0e4fa56408'
SOURCE_MANIFEST_SHA = 'fa4c8c72d83a456b3c109d32e51f06a778e82c1d40473bc78561f09b6b8837e6'
DEPENDENCY_SHA = '07c0abf3c48e4d97022bfaa3db3306c19e40a1d76032765066635d4367184d04'
MPFR_HEADER_SHA = '588c2bd606cba060afb49cd024f9119e996089a341a99d1dc7e0367622335a13'
MPFR_LIBRARY_SHA = '7357c29f8de910cb83deaf3c62f845f4862695361a798555bc8d6994911f2eca'
SUPERVISOR_ORIGIN_SHA = 'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2'
FRONT_ARCHIVE_SHA = 'c45e814f94f3462be4d4e5d054253d8d5fdbbec24e15d29b605da8eb4c2d9fb0'
OLD = 'vorbis-floor0-certified-oracle-20261028-01'
GOOD = 'vorbis-floor0-certified-oracle-20261028-02'
EXECUTED_BUILD = '/mnt/c/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/'
READERS = {
    'test-vorbis-setup.py': 'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff',
    'test-vorbis-floor-packet.py': '8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7',
    'test-vorbis-residue.py': '1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d',
    'vorbis_packet_frame_model.py': '5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9',
    'test-vorbis-packet-frame.py': '7c449b4b190500b0ab5931205f06e51e9f691112ebea80ac1affb7b200cb22d0',
}
LIVE = {
    'tests/test-vorbis-floor0-certified-oracle.py': RUNNER_SHA,
    'tools/codec_benchmark/vorbis_floor0_mpfr_oracle.c': ORACLE_SHA,
    'tools/codec_benchmark/vorbis_floor0_mpfr_oracle.sources.json': SOURCE_MANIFEST_SHA,
    'tests/test-vorbis-floor1-render.py': SUPERVISOR_ORIGIN_SHA,
    'idf/components/native_vorbis_numeric/include/native_vorbis_floor0.h': '122ee70ab248c5aa3a46354288be3d78418e6d5e67f15c4d44d43f5ff704c63b',
    'idf/components/native_vorbis_numeric/floor0.c': '297e055a68ff2ee4ea71e0879aef12456139945015d346b2a12a18db7b0a4335',
    'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/lsp.c': 'cf618a3be06feb94e39eb7a06ad0db4fd8462f8edac93faf4765b28516a9f5ef',
    **{'tests/' + name: pin for name, pin in READERS.items()},
}
OMITTED = {
    OLD + '/sources/libmpfr.a': (10247406, MPFR_LIBRARY_SHA),
    GOOD + '/sources/libmpfr.a': (10247406, MPFR_LIBRARY_SHA),
    GOOD + '/oracle': (1612440, 'd38700410cf9e5dd6393f82ce9a9cfc62a7d276d7fcb6a53129bf05e6b057f82'),
}
LICENSES = {
    'COPYING': (35149, '3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986'),
    'COPYING.LESSER': (7652, 'e3a994d82e644b03a792a930f574002658412f62407f5fee083f2555c5f23118'),
}
FIELDS = {'schema', 'ordinal', 'status', 'reason', 'precision', 'denominator',
          'log2_gain', 'floor_lo', 'floor_hi', 'floor_equal'}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def canonical(name):
    return isinstance(name, str) and bool(name) and name.isascii() and not any(
        ord(c) < 32 or ord(c) == 127 for c in name) and ':' not in name and '\\' not in name and \
        not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and \
        PurePosixPath(name).as_posix() == name


def inventory():
    body, manifest_body = (FOLDER / 'captures.zip').read_bytes(), (FOLDER / 'manifest.json').read_bytes()
    need(len(body) == 3817347 and sha(body) == ARCHIVE_SHA, 'exact sealed archive')
    need(sha(manifest_body) == MANIFEST_SHA, 'exact sealed manifest')
    manifest = json.loads(manifest_body)
    need(manifest['schema'] == 'certified-floor0-oracle-evidence-v1', 'manifest schema')
    rows = manifest['members']
    need(len(rows) == 97 and len({row['path'] for row in rows}) == 97 and
         all(set(row) == {'path', 'bytes', 'sha256'} and canonical(row['path']) and
             type(row['bytes']) is int and row['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', row['sha256'])
             for row in rows), 'complete canonical manifest inventory')
    pins = {row['path']: row for row in rows}
    members = {}
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        info = archive.infolist()
        need(len(info) == len({row.filename for row in info}) == 97 and
             {row.filename for row in info} == set(pins), 'exact ZIP member set, no duplicates')
        need(sum(row.file_size for row in info) == 30794467, 'exact decoded ZIP size')
        for row in info:
            need(canonical(row.filename) and not row.is_dir() and not row.flag_bits & 1 and
                 stat.S_IFMT(row.external_attr >> 16) in (0, stat.S_IFREG) and
                 row.file_size == pins[row.filename]['bytes'], 'regular canonical ZIP member')
            content = archive.read(row)
            need(sha(content) == pins[row.filename]['sha256'], 'every decoded archive byte: ' + row.filename)
            members[row.filename] = content
    omitted = manifest['omitted']
    need(len(omitted) == 3 and len({row['path'] for row in omitted}) == 3 and
         {row['path']: (row['bytes'], row['sha256']) for row in omitted} == OMITTED and
         all(canonical(row['path']) and row['path'] not in members and
             row['reason'] == 'rebuildable host executable/static dependency' for row in omitted),
         'all three exact derived omissions remain explicit')
    need({name.split('/')[0] for name in members} == {'dependency', OLD, GOOD}, 'all attempt groups retained')
    return members


def trusted_runner():
    # No import of a local helper, runner or archived program precedes these pins.
    for name, pin in LIVE.items():
        need(sha((ROOT / name).read_bytes()) == pin, 'trusted live source before import: ' + name)
    need(sha((ROOT / 'tests/results/vorbis-floor0-spectrum-20261028/captures.zip').read_bytes()) == FRONT_ARCHIVE_SHA,
         'complete retained front-end source archive before import')
    spec = importlib.util.spec_from_file_location('certified_oracle_checkpoint_live_runner',
        ROOT / 'tests/test-vorbis-floor0-certified-oracle.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    need(runner.PINS == READERS and runner.ARCHIVE_SHA == FRONT_ARCHIVE_SHA and
         runner.SUPERVISOR_ORIGIN_SHA == SUPERVISOR_ORIGIN_SHA, 'live pure reader dependency closure')
    return runner


def sources(members):
    expected = {'runner.py': RUNNER_SHA, 'oracle.c': ORACLE_SHA, 'mpfr.h': MPFR_HEADER_SHA,
                'libmpfr.a': MPFR_LIBRARY_SHA, 'oracle.sources.json': SOURCE_MANIFEST_SHA,
                'dependency-build-report.json': DEPENDENCY_SHA,
                'supervisor-origin.py': SUPERVISOR_ORIGIN_SHA,
                **{'readers/' + name: pin for name, pin in READERS.items()}}
    origin = (ROOT / 'tests/test-vorbis-floor1-render.py').read_bytes()
    templates = [ast.literal_eval(node.value) for node in ast.parse(origin).body
                 if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and
                 target.id == 'SUPERVISOR' for target in node.targets)]
    need(len(templates) == 1 and templates[0].count('assert 0<timeout<=60') == 1,
         'one literal supervisor origin, no archived execution')
    supervisor = templates[0].replace('assert 0<timeout<=60', 'assert 0<timeout<=180').encode()
    reports = {}
    for group in (OLD, GOOD):
        report = json.loads(members[group + '/report.json'])
        reports[group] = report
        need(report['sources'] == expected and report['supervisor_sha256'] == sha(supervisor) and
             members[group + '/supervisor.py'] == supervisor, 'all executed source/supervisor pins: ' + group)
        for name, pin in expected.items():
            if name != 'libmpfr.a':
                need(sha(members[group + '/sources/' + name]) == pin, 'retained source binding: ' + name)
        need(report['oracle_only'] and not report['production_selected'] and
             not report['new_PCM_executed'] and not report['native_executed'] and
             report['original_frame_cases'] == 447 and report['unique_requests'] == 8202 and
             report['source_archive_sha256'] == FRONT_ARCHIVE_SHA, 'honest saved host-only scope')
    need(sha(members['dependency/build-report.json']) == DEPENDENCY_SHA, 'dependency receipt pin')
    dependency = json.loads(members['dependency/build-report.json'])
    need(dependency['status'] == 'PASS' and len(dependency['commands']) == 5 and
         [row['name'] for row in dependency['commands']] == ['compiler-version', 'installed-gmp', 'configure', 'make', 'install'] and
         all(row['exit_code'] == 0 for row in dependency['commands']), 'all actual dependency build exits')
    need(all('-fsanitize' not in arg for row in dependency['commands'] for arg in row['argv']),
         'dependency build is not mislabelled sanitizer-instrumented')
    installed = {row['path']: row for row in dependency['installed_files']}
    need(installed['install/include/mpfr.h']['sha256'] == MPFR_HEADER_SHA and
         installed['install/lib/libmpfr.a']['sha256'] == MPFR_LIBRARY_SHA, 'real header/library dependency identity')
    source_manifest = json.loads(members[GOOD + '/sources/oracle.sources.json'])
    need(source_manifest['dependency_build']['sha256'] == DEPENDENCY_SHA and
         source_manifest['mpfr'] == dict(version='4.2.2', url='https://www.mpfr.org/mpfr-4.2.2/mpfr-4.2.2.tar.xz',
             sha256='b67ba0383ef7e8a8563734e2e889ef5ec3c3b898a01d00fa0a6869ad81c6ce01', bytes=1505596),
         'official MPFR source archive and actual build lineage')
    for row in source_manifest['sources']:
        if not row['path'].endswith('.md'):
            need(LIVE.get(row['path']) == row['sha256'] and
                 len((ROOT / row['path']).read_bytes()) == row['bytes'], 'non-documentary design/source pin')
    for name, wanted in LICENSES.items():
        content = (FOLDER / name).read_bytes()
        record = installed['install/share/doc/mpfr/' + name]
        need((len(content), sha(content)) == wanted == (record['bytes'], record['sha256']),
             'unchanged MPFR license sidecar: ' + name)
    return reports


def owned_commands(members, report):
    base = EXECUTED_BUILD + GOOD
    executable = ['env', 'ASAN_OPTIONS=detect_leaks=1:abort_on_error=1',
                  'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', base + '/oracle']
    budgeted = executable + ['--max-precision', '8192']
    expected = {
        'compiler-version': ['gcc', '--version'],
        'compile': ['gcc', '-std=c11', '-O1', '-g', '-UNDEBUG', '-Wall', '-Wextra', '-Werror',
                    '-fno-fast-math', '-ffp-contract=off', '-fno-pie', '-no-pie', '-fsanitize=address,undefined',
                    '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-I' + base + '/sources',
                    base + '/sources/oracle.c', base + '/sources/libmpfr.a', '-lgmp', '-lm', '-o', base + '/oracle'],
        'oracle-version': executable + ['--version'],
        'budget-control': budgeted + [base + '/budget-control.txt'],
        'protocol-controls': budgeted + [base + '/protocol-controls.txt'],
        **{'execute-' + str(p): budgeted + [base + '/input-' + str(p) + '.txt'] for p in (256, 512)},
        **{f'refine-{i}-{p}': budgeted + [base + f'/refine-{i}-{p}.txt']
           for i in (8000, 8198) for p in (1024, 2048, 4096)},
    }
    need([row['name'] for row in report['commands']] == list(expected), 'all thirteen actual commands in order')
    nonces = set()
    for row in report['commands']:
        name = row['name']; stem = GOOD + '/' + name
        request_body = members[stem + '.request.json']; request = json.loads(request_body)
        receipt = json.loads(members[stem + '.receipt.json'])
        nonce = row['nonce']
        need(re.fullmatch('[0-9a-f]{32}', nonce) and nonce not in nonces, 'unique command nonce')
        nonces.add(nonce)
        expected_exit = 2 if name == 'protocol-controls' else 0
        need(request == dict(nonce=nonce, argv=expected[name], timeout=180,
             receipt=base + '/' + name + '.receipt.json', stop=base + '/' + name + '.stop') and
             row['child_argv'] == expected[name] and row['request_sha256'] == sha(request_body) and
             row['argv'] == ['wsl.exe', '--exec', 'python3', base + '/supervisor.py', base + '/' + name + '.request.json'] and
             row['expected_exit'] == expected_exit and row['transport_exit'] == 0 and
             type(row['transport_pid']) is int and row['transport_pid'] > 0 and
             not row.get('forced_transport_stop'), 'exact owned argv/request/transport: ' + name)
        need(receipt == row['supervisor'] and receipt['nonce'] == nonce and
             receipt['request_sha256'] == sha(request_body) and receipt['state'] == 'terminal' and
             receipt['final'] is True and receipt['new_session'] is True and
             receipt['child_reaped'] is True and receipt['group_gone'] is True and
             receipt['child_pid'] == receipt['owned_pgid'] > 0 and receipt['supervisor_pid'] > 0 and
             receipt['child_returncode'] == expected_exit, 'actual child terminal/reap/group ownership: ' + name)
        need(not members[stem + '.stderr.log'], 'no oracle sanitizer/compiler stderr: ' + name)
    need(members[GOOD + '/compiler-version.stdout.log'].decode() == report['compiler_version'] and
         members[GOOD + '/oracle-version.stdout.log'].decode() == report['oracle_version'] + '\n' and
         report['oracle_version'] == 'F0MPFR1 MPFR=4.2.2 GMP=6.3.0', 'actual compiler and linked runtime versions')
    return len(expected)


def response(runner, row, ordinal, precision, exceptional=False):
    need(set(row) == FIELDS and type(row['ordinal']) is int and row['ordinal'] == ordinal and
         type(row['precision']) is int and row['precision'] == precision, 'strict response shape/ordinal/precision')
    if exceptional:
        need(row['schema'] == 'F0MPFR1' and row['status'] == 'resource' and
             row['reason'] == 'caller_precision_budget' and all(row[key] is None for key in
             ('denominator', 'log2_gain', 'floor_lo', 'floor_hi', 'floor_equal')), 'explicit caller-budget refusal')
        return None
    bounds = runner.enclosure(row)
    status, reason = row['status'], row['reason']
    reasons = {'absent': {'raw_zero'}, 'pole': {'exact_zero_denominator'},
               'indeterminate': {'exact_zero_denominator'}, 'unity': {'exact_identity'},
               'certified': {'floor_agrees'}, 'unresolved': {'denominator_lower_zero', 'integer_boundary'}}
    need(reason in reasons[status], 'strict mathematical status/reason')
    if bounds is None:
        need(all(row[key] is None for key in ('floor_lo', 'floor_hi', 'floor_equal')), 'unavailable floors are explicit null')
    else:
        need(type(row['floor_equal']) is bool and all(isinstance(row[key], str) and
             re.fullmatch(r'-?(?:0|[1-9a-f][0-9a-f]*)', row[key]) and row[key] != '-0'
             for key in ('floor_lo', 'floor_hi')), 'literal unbounded canonical integer floors')
    if status == 'absent':
        need(row['denominator'] is None and bounds is None, 'absent floor bypasses denominator')
    elif status in ('pole', 'indeterminate'):
        need(bounds is None and row['denominator'] is not None and all(
             runner.dyadic(row['denominator'][key]) == 0 for key in ('lo', 'hi')), 'exact zero denominator route')
    elif status == 'unity':
        need(bounds == (0, 0) and row['floor_lo'] == row['floor_hi'] == '0' and row['floor_equal'], 'exact unity export')
    elif status == 'certified':
        need(bounds is not None and row['floor_equal'], 'certified endpoint floors agree')
    elif reason == 'denominator_lower_zero':
        need(bounds is None and row['denominator'] is not None and
             runner.dyadic(row['denominator']['lo']) == 0, 'rounded cancellation stays unresolved')
    else:
        need(bounds is not None and not row['floor_equal'], 'unresolved integer-boundary export')
    return bounds


def replay(members, runner, report):
    requests, identities, retained = runner.exact_inputs()
    requests += runner.special_inputs()
    need(len(requests) == 8202 and len(identities) == 447 and
         json.loads(members[GOOD + '/requests.json']) == requests and
         json.loads(members[GOOD + '/identities.json']) == identities and report['retained_source'] == retained,
         'complete independently rebuilt 447-frame/8202-request lineage')
    for group in (OLD, GOOD):
        old = json.loads(members[group + '/report.json'])
        need(members[group + '/requests.json'] == members[GOOD + '/requests.json'] and
             members[group + '/identities.json'] == members[GOOD + '/identities.json'] and
             old['request_sha256'] == sha(members[group + '/requests.json']) and
             old['identities_sha256'] == sha(members[group + '/identities.json']), 'all attempt input bytes identical')
    captures = {}
    for precision in (256, 512):
        need(members[GOOD + '/input-' + str(precision) + '.txt'] ==
             ''.join(runner.protocol(row, precision) for row in requests).encode(), 'every exact numerical input line')
        rows = [json.loads(line) for line in members[GOOD + '/execute-' + str(precision) + '.stdout.log'].splitlines()]
        need(len(rows) == 8202, 'all exact output rows, no truncation')
        for ordinal, row in enumerate(rows, 1):
            response(runner, row, ordinal, precision)
        captures[precision] = rows
    nested = unresolved = denominator_nested = 0
    for index, source in enumerate(requests):
        low, high = captures[256][index], captures[512][index]
        a, b = runner.enclosure(low), runner.enclosure(high)
        if a is not None and b is not None:
            need(a[0] <= b[0] <= b[1] <= a[1], 'every 256/512 logarithm interval nests')
            nested += 1
        elif b is None:
            unresolved += int(high['status'] == 'unresolved')
        if low['denominator'] is not None and high['denominator'] is not None:
            l = [runner.dyadic(low['denominator'][k]) for k in ('lo', 'hi')]
            h = [runner.dyadic(high['denominator'][k]) for k in ('lo', 'hi')]
            need(l[0] <= h[0] <= h[1] <= l[1], 'every available denominator interval nests')
            denominator_nested += 1
        if source.get('id') != 'tiny-finite-1572bit-exponent':
            runner.analytical(source, high)
    need((nested, unresolved) == (8194, 2) and report['nested_enclosures'] == nested and
         report['initial_unresolved'] == unresolved, 'exact full nesting/unresolved inventory')
    refinements = []
    final = {}
    for index in (8000, 8198):
        previous = runner.enclosure(captures[512][index])
        for precision in (1024, 2048, 4096):
            stem = f'refine-{index}-{precision}'
            need(members[GOOD + '/' + stem + '.txt'] == runner.protocol(requests[index], precision).encode(),
                 'adaptive request retains original exact provenance')
            lines = members[GOOD + '/' + stem + '.stdout.log'].splitlines()
            need(len(lines) == 1, 'one complete adaptive result')
            row = json.loads(lines[0]); current = response(runner, row, 1, precision)
            if previous is not None and current is not None:
                need(previous[0] <= current[0] <= current[1] <= previous[1], 'all adaptive log bounds nest')
            previous = current
            refinements.append(dict(request=index, precision=precision, status=row['status'], floor_equal=row['floor_equal']))
        need(row['status'] == 'certified' and row['floor_equal'], 'both finite exceptional requests resolve at4096')
        runner.analytical(requests[index], row)
        final[index] = row
    need(refinements == report['refinements'], 'all six actual precision refinements')
    return requests, identities, captures, dict(nested_enclosures=nested, initial_unresolved=unresolved,
        denominator_enclosures_nested=denominator_nested, refinements=refinements,
        finite_witness_floor_bits=int(final[8198]['floor_lo'], 16).bit_length(),
        status_counts_512=dict(collections.Counter(row['status'] for row in captures[512])))


def protocol_controls(members, runner):
    special = runner.special_inputs()
    # This one executed control used Windows write_text's default CRLF. The
    # corpus/refinement files explicitly requested LF and are checked as such.
    need(members[GOOD + '/budget-control.txt'] == runner.protocol(special[1], 8193).replace('\n', '\r\n').encode(),
         'exact above-budget control, including its executed CRLF encoding')
    budget = members[GOOD + '/budget-control.stdout.log'].splitlines()
    need(len(budget) == 1, 'one complete budget refusal')
    response(runner, json.loads(budget[0]), 1, 8193, exceptional=True)
    valid = runner.protocol(special[1], 256).encode()
    invalid = [b'\n', b'F0MPFR2 256 0 0 1 8 1 60\n', b'F0MPFR1 0 0 0 1 8 1 60\n',
               b'F0MPFR1 0256 0 0 1 8 1 60\n', b'F0MPFR1 256 256 0 1 8 1 60\n',
               b'F0MPFR1 256 0 1 1 8 1 60\n', b'F0MPFR1 256 0 0 0 8 1 60\n',
               b'F0MPFR1 256 0 0 1 64 1 60\n', b'F0MPFR1 256 0 0 1 8 256 60\n',
               b'F0MPFR1 256 0 0 1 8 1 256\n', b'F0MPFR1 256 1 0 1 8 1 60\n',
               b'F0MPFR1 256 0 0 1 8 1 60 extra\n', valid[:-1] + b'\0\n',
               valid[:-1] + b'\xff\n', b'x' * 32768 + b'\n']
    need(members[GOOD + '/protocol-controls.txt'] == b''.join(invalid) + valid + valid[:-1],
         'all malformed complete records, valid middle and final partial input retained')
    rows = [json.loads(line) for line in members[GOOD + '/protocol-controls.stdout.log'].splitlines()]
    need(len(rows) == 17, 'all protocol-control output records')
    for ordinal, row in enumerate(rows, 1):
        if ordinal == 16:
            response(runner, row, ordinal, 256)
            need(row['status'] == 'unity', 'valid middle protocol record survives')
        else:
            need(set(row) == FIELDS and row['schema'] == 'F0MPFR1' and row['ordinal'] == ordinal and
                 row['status'] == 'invalid' and row['reason'] == 'protocol' and all(row[key] is None for key in
                 ('precision', 'denominator', 'log2_gain', 'floor_lo', 'floor_hi', 'floor_equal')),
                 'all sixteen malformed refusals and null outputs')
    return dict(malformed_refused=16, valid_middle_retained=True, caller_budget_refused=True)


def history(members, old):
    need(not old['completed'] and not old['passed'] and len(old['commands']) == 1 and
         old['error'] == 'owned oracle transport terminal: compiler-version', 'failed first campaign retained')
    row = old['commands'][0]; stem = OLD + '/compiler-version'
    request = json.loads(members[stem + '.request.json'])
    need(row['name'] == 'compiler-version' and row['child_argv'] == ['gcc', '--version'] and
         row['request_sha256'] == sha(members[stem + '.request.json']) and request['nonce'] == row['nonce'] and
         request['argv'] == row['child_argv'] and row['transport_exit'] == 4294967295 and not row['supervisor'] and
         stem + '.receipt.json' not in members and 'Wsl/E_ACCESSDENIED' in
         members[stem + '.stdout.log'].decode('utf-16-le') and not members[stem + '.stderr.log'],
         'actual pre-Linux-child WSL access refusal, no missing success receipt invented')
    preparation = json.loads(members['dependency/source-preparation-01.failure.json'])
    need(preparation['status'] == 'FAIL' and preparation['exit_code'] == 1 and
         preparation['stage'] == 'before extraction or build' and
         preparation['source_sha256'] == 'b67ba0383ef7e8a8563734e2e889ef5ec3c3b898a01d00fa0a6869ad81c6ce01',
         'dependency source-preparation failure remains explicit')
    return dict(first_campaign='WSL access refused before Linux child', source_preparation_failure_retained=True)


def negative_controls(runner, captures):
    base = next(row for row in captures[256] if row['log2_gain'] is not None and row['status'] == 'certified')
    tests = []
    def refused(name, changed):
        try:
            response(runner, changed, base['ordinal'], 256)
        except (ValueError, TypeError, KeyError):
            tests.append(dict(name=name, rejected=True)); return
        raise ValueError('corrupted saved response accepted: ' + name)
    row = copy.deepcopy(base); row['floor_lo'] = format(int(row['floor_lo'], 16) + 1, 'x'); refused('integer_floor', row)
    row = copy.deepcopy(base); row['ordinal'] += 1; refused('duplicate_or_reordered_ordinal', row)
    row = copy.deepcopy(base); row['precision'] = 512; refused('wrong_precision', row)
    row = copy.deepcopy(base); row['extra'] = 1; refused('extra_field', row)
    for name in ('../x', '/x', 'a\\b', 'a//b', 'a/./b', 'C:x'):
        need(not canonical(name), 'malformed archive name control')
        tests.append(dict(name='archive_name:' + name, rejected=True))
    return tests


def verify():
    members = inventory()
    runner = trusted_runner()
    reports = sources(members)
    good = reports[GOOD]
    need(good['completed'] and good['passed'] and good['protocol_refusals'] == 16, 'qualified actual campaign')
    commands = owned_commands(members, good)
    requests, identities, captures, numerical = replay(members, runner, good)
    controls = protocol_controls(members, runner)
    attempts = history(members, reports[OLD])
    corruptions = negative_controls(runner, captures)
    return dict(schema='certified-floor0-oracle-checkpoint-replay-v1', passed=True,
        archive_sha256=ARCHIVE_SHA, archive_bytes=3817347, manifest_sha256=MANIFEST_SHA,
        archive_members=97, decoded_bytes=30794467, explicit_derived_omissions=3,
        live_runner_sha256=RUNNER_SHA, live_oracle_sha256=ORACLE_SHA,
        verifier_sha256=sha(Path(__file__).read_bytes()), identities=len(identities), unique_requests=len(requests),
        owned_commands=commands, all_actual_commands_terminal_reaped=True, protocol_expected_exit=2,
        numerical=numerical, controls=controls, histories=attempts, corruption_controls=corruptions,
        archived_code_executed=False, archives_extracted=False, commands_reexecuted=0,
        oracle_sanitizers=['address', 'undefined'], dependency_sanitizers_instrumented=False,
        new_PCM_executed=False, MCU_gain_qualified=False, Bark_index_qualified=False,
        native_executed=False, production_selected=False, MPFR_license_sidecars_verified=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=FOLDER / 'replay.json')
    args = parser.parse_args()
    output = args.output.resolve()
    need(output.is_relative_to(ROOT) and not output.exists(), 'fresh replay output within the worktree')
    try:
        result = verify()
    except BaseException as error:
        result = dict(passed=False, error_type=type(error).__name__, error=str(error),
                      verifier_sha256=sha(Path(__file__).read_bytes()), commands_reexecuted=0,
                      archived_code_executed=False, archives_extracted=False)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps(result), flush=True)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
