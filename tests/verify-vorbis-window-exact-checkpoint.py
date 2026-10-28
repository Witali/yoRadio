"""Replay sealed exact-window evidence locally; never execute archived code."""
import argparse
import ast
import hashlib
import importlib.util
import json
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'tests/results/vorbis-window-exact-20261028'
ARCHIVE_SHA = 'ba372710a086d31849ad2aab28075549480490a499855c131882c4dc0ab50989'
MANIFEST_SHA = '7610b9255c57b670922696d9625dc5b7c39754e9a2db7931bfd636620624c6b2'
MEMBERS = 394
DECODED_BYTES = 247543897
FINAL_HOST = 'host04'
HOST_STATES = {
    'host01': dict(completed=False, passed=False, commands=1),
    'host02': dict(completed=True, passed=True, commands=3),
    'host03': dict(completed=True, passed=True, commands=3),
    'host04': dict(completed=True, passed=True, commands=3),
}
FIXTURE_LINT = {
    'fixture-lint01': dict(completed=False, returncode=1, warnings=23, errors=1, source_group='host03'),
    'fixture-lint02': dict(completed=False, returncode=1, warnings=23, errors=1, source_group='host03'),
    'fixture-lint03': dict(completed=True, returncode=0, warnings=24, errors=0, source_group='host03'),
    'fixture-lint04': dict(completed=True, returncode=0, warnings=23, errors=0, source_group='host04'),
}
OMITTED = {'host02/window-exact', 'host03/window-exact', 'host04/window-exact'}
EXPECTED_CONTROLS = dict(rows=64940, refusals=10360, checks=14889244)
EXPECTED_CORRUPTIONS = ['magic', 'scalar-index', 'sample', 'factor', 'base-exponent',
    'status', 'canonical-zero', 'high-product', 'coefficient', 'geometry', 'view-product',
    'truncated', 'trailing']
EXPECTED_WITNESSES = dict(records=864, terms=1197984, witnesses=17962,
    exponents_at_least1074=13767,
    identity_sha256='844e6d38700b6e8c6d8683d7afcc49d7a46289a1a4d1735d3cc1a554826af472')
PINS = {
    'vorbis_synthesis_checkpoint.py': 'dfff6c46c56bf0cbf95a2385ca3584314b720088bd11124247e20605d8712ed5',
    'test-vorbis-window.py': 'c2fbcc21f1236b2c4b95d7e4f77a5498d4eb427fb2ec5ec5777c0447b0ed69d9',
    'test-vorbis-floor1-render.py': 'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2',
    'test-vorbis-window-exact.py': '06268abe3c9fe4836bf17ca91b1fcb73ce82137ea872282e21bad61fa4494e41',
}
FIXTURE_SHA = 'a197b9fd0873275d747bc3799d8e08cae5c2cb0f0b4bbd5c8683961581ea844b'
PRIOR_SHA = '685778be3a8650fd9e1740e2e99b1540b1f2cde7ec33046f96d3e3bde6fd2d23'
PRIOR_MANIFEST_SHA = 'cba1bd703fb6467828b56db3becd796eaf270f4ecdebf78025f5d3b577c54700'
PROFILE_TRAILER = (b'extern "C" auto window_product_probe() -> '
    b'decltype(&native_vorbis_window_multiply_exact) { '
    b'return &native_vorbis_window_multiply_exact; }\n')


def verify():
    # Hash every live dependency before importing even the shared helper.
    for name, digest in PINS.items():
        if hashlib.sha256((ROOT/'tests'/name).read_bytes()).hexdigest() != digest:
            raise ValueError('pinned live reader: '+name)
    fixture = ROOT/'tests/native/vorbis_window_exact_host.c'
    if hashlib.sha256(fixture.read_bytes()).hexdigest() != FIXTURE_SHA:
        raise ValueError('pinned live exact-window fixture')
    path = ROOT/'tests/vorbis_synthesis_checkpoint.py'
    spec = importlib.util.spec_from_file_location('window_exact_checkpoint_helper', path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    need, sha = helper.need, helper.sha
    reader = helper.load_local('tests/test-vorbis-window-exact.py',
        PINS['test-vorbis-window-exact.py'], 'window_exact_checkpoint_reader')
    oracle = helper.load_local('tests/test-vorbis-window.py',
        PINS['test-vorbis-window.py'], 'window_exact_checkpoint_sine')
    members = helper.archive_members(FOLDER, ARCHIVE_SHA, MANIFEST_SHA)
    read = lambda name: json.loads(members[name])
    need(len(members) == MEMBERS and sum(map(len, members.values())) == DECODED_BYTES,
        'complete sealed archive inventory')
    for name in members:
        need(PurePosixPath(name).as_posix() == name and ':' not in name and '\\' not in name,
            'canonical data-only archive member')
    groups = {name.split('/')[0] for name in members}
    need(groups == set(HOST_STATES) | set(FIXTURE_LINT) | {'profiles01', 'profiles02', 'tools', 'receipts'},
        'exact retained attempt groups')
    manifest = json.loads((ROOT/FOLDER/'manifest.json').read_bytes())
    omitted = {row['path']: row for row in manifest['omitted']}
    need(len(omitted) == len(manifest['omitted']) and set(omitted) == OMITTED and
        all(row['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}', row['sha256']) and name not in members
            for name, row in omitted.items()), 'only declared rebuildable executables omitted')

    def sources(group, report, live=False, profile=False):
        for label, digest in report['sources'].items():
            need(PurePosixPath(label).as_posix() == label and '..' not in PurePosixPath(label).parts
                and ':' not in label and '\\' not in label, 'contained source snapshot name')
            body = members[group+'/sources/'+label]
            need(sha(body) == digest, 'every frozen source or data byte')
            if not live:
                continue
            if profile:
                relative = 'idf/components/'+label
            elif label.startswith('components/'):
                relative = 'idf/'+label
            elif label.startswith('native/'):
                relative = 'tests/'+label
            elif label == 'runner.py':
                relative = 'tests/test-vorbis-window-exact.py'
            elif label == 'window-oracle.py':
                relative = 'tests/test-vorbis-window.py'
            elif label == 'supervisor-origin.py':
                relative = 'tests/test-vorbis-floor1-render.py'
            else:
                continue
            if Path(relative).suffix in ('.c', '.h', '.inc', '.py') or Path(relative).name == 'CMakeLists.txt':
                need((ROOT/relative).read_bytes() == body, 'live code equals final executed source snapshot')

    def commands(group, report, successful):
        for row in report['commands']:
            stem = group+'/'+row['name']
            request = read(stem+'.request.json')
            need(request['argv'] == row['child_argv'] and request['nonce'] == row['nonce'] and
                sha(members[stem+'.request.json']) == row['request_sha256'], 'owned request binding')
            receipt = row.get('supervisor')
            if not receipt:
                need(not successful and stem+'.receipt.json' not in members and
                    row.get('transport_exit') != 0 and
                    (row.get('transport_exit') is not None or 'transport_pid' not in row),
                    'retained refusal before child dispatch without an unclosed transport')
                continue
            need(receipt == read(stem+'.receipt.json') and receipt['nonce'] == row['nonce'] and
                receipt['request_sha256'] == row['request_sha256'] and row['transport_exit'] == 0 and
                not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and
                receipt['final'] and receipt['new_session'] and receipt['child_pid'] == receipt['owned_pgid'] and
                receipt['child_reaped'] and receipt['group_gone'] and
                (not successful or receipt['child_returncode'] == 0), 'every dispatched child terminal and reaped')
        if 'supervisor_sha256' in report:
            need(sha(members[group+'/supervisor.py']) == report['supervisor_sha256'], 'frozen supervisor identity')
            definitions = [ast.literal_eval(node.value)
                for node in ast.parse(members[group+'/sources/supervisor-origin.py']).body
                if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and
                    target.id == 'SUPERVISOR' for target in node.targets)]
            need(len(definitions) == 1 and members[group+'/supervisor.py'] == definitions[0].encode(),
                'supervisor retained as literal data from the frozen controller')

    original, original_report = reader.original_data()
    need(reader.PRIOR_SHA == PRIOR_SHA and reader.PRIOR_MANIFEST_SHA == PRIOR_MANIFEST_SHA and
        reader.WINDOW_SHA == PINS['test-vorbis-window.py'] and reader.BOUND == oracle.BOUND == 2e-15,
        'unchanged prior DATA lineage and predeclared sine bound')
    witnesses, witness_metrics = reader.saved_witnesses(original)
    rows = reader.cases(witnesses)
    need(witness_metrics == EXPECTED_WITNESSES,
        'all original underflow identities retained without deduplication')
    report, capture = helper.clean_host(members, FINAL_HOST)
    sources(FINAL_HOST, report, live=True)
    commands(FINAL_HOST, report, successful=True)
    need(read(FINAL_HOST+'/model.json') == rows and reader.encode(rows) == members[FINAL_HOST+'/input.bin'],
        'complete independently rebuilt scalar corpus and raw input')
    need(members[FINAL_HOST+'/sources/recorded-overlap.bin'] == original and
        members[FINAL_HOST+'/sources/recorded-overlap-report.json'] == original_report and
        report['saved_DATA_archive_sha256'] == PRIOR_SHA and
        report['saved_DATA_manifest_sha256'] == PRIOR_MANIFEST_SHA and
        report['witnesses'] == witness_metrics, 'exact saved DATA and every original witness identity')
    for filename, key in (('model.json', 'model_sha256'), ('input.bin', 'input_sha256')):
        need(sha(members[FINAL_HOST+'/'+filename]) == report[key], 'final input and model identities')
    need(omitted[FINAL_HOST+'/window-exact']['sha256'] == report['binary_sha256'], 'omitted derived executable identity')
    need([row['name'] for row in report['commands']] == ['compiler-version', 'compile', 'execute'] and
        report['sanitizers'] == ['address', 'undefined'] and all(not report[key] for key in
            ('native_executed', 'production_selected', 'overlap_executed', 'PCM_executed', 'deferred_scopes_resumed')),
        'complete host-only exact-window execution scope')
    argv = report['commands'][1]['child_argv']
    need(all(flag in argv for flag in ('-UNDEBUG', '-fno-fast-math', '-ffp-contract=off', '-Wall',
        '-Wextra', '-Werror', '-fsanitize=address,undefined', '-fno-sanitize-recover=all')) and
        sum(arg.endswith('.c') for arg in argv) == 4, 'all four compilation units instrumented')
    measured = reader.compare(capture, rows, oracle)
    corruptions = reader.corruption_controls(capture, rows, oracle)
    need(measured == report['measurements'] and corruptions == report['corruption_controls'] and
        corruptions == EXPECTED_CORRUPTIONS and report['controls'] == EXPECTED_CONTROLS,
        'every exact scalar/view result, full guard totals and corruption controls')
    need(measured['scalar_rows'] == 64940 and measured['invalid_scalar_rows'] == 70 and
        measured['exact_view_values'] == 587520 and measured['shapes'] == 288 and
        measured['configurations'] == 36 and measured['coefficients'] == 8160 and
        measured['coefficient_bound'] == 2e-15 and measured['maximum_coefficient_error'] <= 2e-15 and
        measured['maximum_product_bits'] == 106 and measured['minimum_shift'] == -2148 and
        measured['maximum_shift'] == 1023 and measured['finite_sample_exponent_fields'] == 2047 and
        measured['factor_exponent_fields'] == 1024 and measured['significand_widths'] == 53 and
        measured['factor_significand_widths'] == 53 and
        measured['saved_underflow_witnesses'] == 17962 and measured['saved_witnesses_at_least1074'] == 13767 and
        not measured['full_synthesis_qualified'], 'complete declared numerical range and qualified scope')
    need(members[FINAL_HOST+'/execute.stdout.log'].decode().strip() ==
        'WINDOW_EXACT rows={rows} shapes=288 refusals={refusals} checks={checks}'.format(**EXPECTED_CONTROLS),
        'actual fixture guard totals')
    seal = read('receipts/vorbis-window-exact-final-seal-20261028-01.json')
    need(all(seal[key] for key in ('passed', 'live_code_headers_CMake_readers_identical',
        'all_handles_terminal', 'earlier_capture_input_parity')) and
        seal['runner_sha256'] == PINS['test-vorbis-window-exact.py'] and seal['fixture_sha256'] == FIXTURE_SHA and
        seal['witnesses'] == witness_metrics and seal['controls'] == EXPECTED_CONTROLS and
        seal['corruption_controls'] == EXPECTED_CORRUPTIONS and not seal['source_profiles_reexecuted'] and
        not seal['overlap_executed'] and not seal['PCM_executed'], 'sealed source, scope and corpus provenance')
    for unit in ('product', 'view'):
        need(seal[unit+'_sha256'] == sha(members[FINAL_HOST+'/sources/components/native_vorbis_window_exact/'+unit+'.c']),
            'seal binds exact production source bytes')
    for key in ('input_sha256', 'model_sha256', 'capture_sha256', 'binary_sha256'):
        need(seal[key] == report[key], 'seal binds every final evidence identity')

    def corrected_profile(group):
        raw, corrected = members[group+'/report.json'], members[group+'/report-corrected.json']
        correction = read(group+'/metadata-correction.json')
        need(correction['original_sha256'] == sha(raw) and correction['corrected_sha256'] == sha(corrected) and
            raw == corrected+PROFILE_TRAILER and correction['commands_reexecuted'] == 0 and
            correction['compiler_inputs_changed'] is False, 'exact documented metadata-only trailer removal')
        return json.loads(corrected)

    failed_profile = corrected_profile('profiles01')
    sources('profiles01', failed_profile)
    need(not failed_profile['completed'] and not failed_profile['passed'] and failed_profile['source_only'] and
        not failed_profile['native_executed'] and [row['name'] for row in failed_profile['commands']] == ['lx6-version'] and
        'pid' not in failed_profile['commands'][0] and 'returncode' not in failed_profile['commands'][0] and
        failed_profile['objects'] == [] and failed_profile['lint'] == [] and
        '623' in failed_profile['error'], 'failed Windows 623 profile attempt retained honestly')
    profiles = corrected_profile('profiles02')
    sources('profiles02', profiles, live=True, profile=True)
    names = ['lx6-version', 'lx6-product', 'lx6-view', 'lx6-header',
        'rv32-version', 'rv32-product', 'rv32-view', 'rv32-header', 'lint-product', 'lint-view']
    need(profiles['completed'] and profiles['passed'] and profiles['source_only'] and
        not profiles['native_executed'] and [row['name'] for row in profiles['commands']] == names,
        'all ten source-only profile commands')
    for row in profiles['commands']:
        need(row['returncode'] == 0 and not row.get('forced_stop'), 'source profile process terminal')
        for stream in ('stdout', 'stderr'):
            need(sha(members['profiles02/'+row['name']+'.'+stream+'.log']) == row[stream+'_sha256'],
                'unaltered source profile diagnostics')
    need(profiles['lint'] == [dict(unit='product', warnings=0, errors=0), dict(unit='view', warnings=0, errors=0)] and
        all(not members['profiles02/'+name+'.'+stream+'.log'] for name in names[-2:] for stream in ('stdout', 'stderr')),
        'both C units have zero lint diagnostics')
    need(len(profiles['objects']) == 6 and {row['name'] for row in profiles['objects']} ==
        {target+'-'+unit+'.o' for target in ('lx6', 'rv32') for unit in ('product', 'view', 'header')},
        'all six actual C and C++ source objects')
    for row in profiles['objects']:
        body = members['profiles02/'+row['name']]
        machine = 94 if row['name'].startswith('lx6-') else 243
        need(sha(body) == row['sha256'] and body[:6] == b'\x7fELF\x01\x01' and
            int.from_bytes(body[16:18], 'little') == 1 and
            int.from_bytes(body[18:20], 'little') == row['machine'] == machine,
            'hash-bound little-endian ELF32 relocatable for LX6 or RV32')
    frames = {}
    for name, text in profiles['stack_records'].items():
        need(members['profiles02/'+name].decode().replace('\r\n', '\n') == text, 'unaltered compiler stack record')
        parsed = {}
        for line in text.splitlines():
            site, count, kind = line.split('\t')
            need(kind == 'static', 'only static own-function stack records')
            parsed[site.rsplit(':', 1)[-1]] = int(count)
        frames[name] = parsed
    for target, prepare, at in (('lx6', 144, 48), ('rv32', 160, 32)):
        need(frames[target+'-product.su']['native_vorbis_window_multiply_exact'] == 112 and
            frames[target+'-view.su']['native_vorbis_window_exact_prepare'] == prepare and
            frames[target+'-view.su']['native_vorbis_window_exact_at'] == at,
            'bounded own-function frames without a whole-call-chain claim')

    lint_results = {}
    for group, expected in FIXTURE_LINT.items():
        lint = read(group+'/report.json')
        diagnostics = members[group+'/stdout.log']+members[group+'/stderr.log']
        actual = {key: lint[key] for key in ('completed', 'returncode', 'warnings', 'errors')}
        need(actual == {key: expected[key] for key in actual} and lint['source_only'] and
            not lint['native_executed'] and not lint['SDK_executed'] and
            len(re.findall(rb': warning:', diagnostics)) == expected['warnings'] and
            len(re.findall(rb': (?:fatal )?error:', diagnostics)) == expected['errors'] and
            lint['source_sha256'] == sha(members[expected['source_group']+'/sources/native/vorbis_window_exact_host.c']),
            'honest fixture lint totals and exact source binding')
        if 'generated_warnings' in lint:
            generated = re.findall(rb'^(\d+) warnings generated\.', diagnostics, re.MULTILINE)
            need(len(generated) <= 1 and lint['generated_warnings'] == (int(generated[0]) if generated else 0),
                'unaltered generated warning summary')
        need(members[group+'/clang-tidy.yaml'] == members['profiles02/clang-tidy.yaml'] ==
            (ROOT/'.clang-tidy').read_bytes(), 'unchanged lint configuration without added suppressions')
        lint_results[group] = actual
    need(seal['displayed_fixture_lint_warnings'] == 23 and seal['generated_fixture_lint_warnings'] == 44 and
        seal['default_suppressed_system_warnings'] == 5 and seal['fixture_lint_errors'] == 0 and
        b'44 warnings generated.' in members['fixture-lint04/stderr.log'] and
        b'Suppressed 5 warnings (5 in non-user code).' in members['fixture-lint04/stderr.log'],
        'honest generated, displayed and default system-header diagnostics')
    history = {}
    for group, state in HOST_STATES.items():
        old = read(group+'/report.json')
        sources(group, old)
        commands(group, old, successful=old['passed'])
        actual = dict(completed=old['completed'], passed=old['passed'], commands=len(old['commands']))
        need(actual == state, 'every historical host attempt retained honestly')
        if old.get('capture_sha256'):
            need(sha(members[group+'/capture.bin']) == old['capture_sha256'], 'historical raw capture identity')
        if old['passed']:
            helper.clean_host(members, group)
            need(omitted[group+'/window-exact']['sha256'] == old['binary_sha256'],
                'every successful omitted derived executable identity')
            expected_controls = EXPECTED_CONTROLS if group == FINAL_HOST else dict(
                rows=64940, refusals=10360, checks=14888956)
            need(old['controls'] == expected_controls and members[group+'/execute.stdout.log'].decode().strip() ==
                'WINDOW_EXACT rows={rows} shapes=288 refusals={refusals} checks={checks}'.format(**expected_controls),
                'historical fixture guard totals before the final assertion improvement')
        history[group] = actual
    need(members['host02/capture.bin'] == members['host03/capture.bin'] == capture,
        'pure reader and fixture assertion additions preserve every earlier numerical capture byte')
    return dict(passed=True, members=len(members), decoded_bytes=sum(map(len, members.values())),
        measurements=measured, witnesses=witness_metrics, controls=report['controls'],
        corruption_controls=corruptions, historical_attempts=history, profile_commands=10, ELF32_objects=6,
        production_lint_warnings=0, fixture_lint=lint_results, own_function_frames=frames,
        profile_metadata_corrections=2, archived_code_executed=False, commands_reexecuted=0,
        files_extracted=False, native_executed=False, overlap_executed=False, PCM_executed=False,
        full_synthesis_qualified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.report and (not args.report.resolve().is_relative_to(ROOT/'.build') or args.report.exists()):
        raise ValueError('fresh report within task-local .build required')
    result = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))
