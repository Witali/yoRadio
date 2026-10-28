"""Replay sealed exact PCM captures locally; execute no archived code or child."""
import argparse
import ast
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'tests/results/vorbis-pcm-exact-20261028'
ARCHIVE_SHA = 'e47fe7e135c1c78af04250b0cc92d78b3619aecf530cced6801af9723d1f2b97'
MANIFEST_SHA = '8719e3aaed4851420a941331ac6b2032d8e345cfa85654d7dd9feffc4c29ba16'
MEMBERS = 431
DECODED_BYTES = 611118904
PHYSICAL_MEMBERS = 124
PHYSICAL_BYTES = 302750255
FINAL_HOST = 'host05'
HOST_STATES = {
    'host01': dict(completed=False, passed=False, commands=0),
    'host02': dict(completed=False, passed=False, commands=1),
    'host03': dict(completed=False, passed=False, commands=3),
    'host04': dict(completed=True, passed=True, commands=3),
    'host05': dict(completed=True, passed=True, commands=3),
}
HISTORICAL_ERRORS = {'host01': 'FileNotFoundError', 'host02': 'owned transport terminal: compiler-version',
    'host03': 'corrupted exact PCM capture accepted: adapter-PCM'}
HISTORICAL_CONTROLS = {'host04': dict(scalars=207979, refusals=2882, checks=62348012),
    'host05': dict(scalars=208411, refusals=4178, checks=62379152)}
PARITY_GROUPS = ('host03', 'host04')
FIXTURE_LINT = {
    'fixture-lint01': dict(completed=True, returncode=0, warnings=28, errors=0, source_group='host04'),
    'fixture-lint02': dict(completed=True, returncode=0, warnings=27, errors=0, source_group='host05'),
}
OMITTED = {'host03/pcm-exact', 'host04/pcm-exact', 'host05/pcm-exact'}
EXPECTED_CONTROLS = dict(scalars=208411, refusals=4178, checks=62379152)
EXPECTED_CORRUPTIONS = ['magic', 'legacy-source', 'legacy-PCM', 'scalar-index', 'scalar-product',
    'scalar-base', 'genuine-tail-PCM', 'coefficient', 'signed-origin', 'unwindowed-source',
    'window-product', 'adapter-PCM', 'truncated', 'trailing']
EXPECTED_SCALARS = 208411
FIXTURE_SHA = 'd092cb41e160e8a9c427309da8f7d45b4130a0bb456219d0398c758705a24244'
SEAL = 'receipts/vorbis-pcm-exact-final-seal-20261028-01.json'
PINS = {
    'vorbis_synthesis_checkpoint.py': 'dfff6c46c56bf0cbf95a2385ca3584314b720088bd11124247e20605d8712ed5',
    'test-vorbis-pcm-exact.py': 'ca145e73850ac1af5e16ebef5c1287f5a4c74d131752f6a71bee63ef5190cf01',
    'test-vorbis-pcm-pair.py': 'f53ec0429b06abf2576e5c052df4ea95fc60dae59f63f42687a25e6ba7e60aa9',
    'test-vorbis-window-exact.py': '06268abe3c9fe4836bf17ca91b1fcb73ce82137ea872282e21bad61fa4494e41',
    'test-vorbis-window.py': 'c2fbcc21f1236b2c4b95d7e4f77a5498d4eb427fb2ec5ec5777c0447b0ed69d9',
    'test-vorbis-floor1-render.py': 'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2',
}
PCM_ARCHIVE = 'd96b5cbe53cee88ca78d5f4fb4e43dd72b5fc8676f64b55d92c2d575d413e648'
PCM_MANIFEST = '1cab066613634e0cd0240389c45c783c536df6e620e86d6cc4da83f4a6bbedd0'
OVERLAP_ARCHIVE = '685778be3a8650fd9e1740e2e99b1540b1f2cde7ec33046f96d3e3bde6fd2d23'
OVERLAP_MANIFEST = 'cba1bd703fb6467828b56db3becd796eaf270f4ecdebf78025f5d3b577c54700'
EXPECTED_WITNESSES = dict(records=864, terms=1197984, witnesses=17962,
    exponents_at_least1074=13767,
    identity_sha256='844e6d38700b6e8c6d8683d7afcc49d7a46289a1a4d1735d3cc1a554826af472')


def resolve_logical_members(physical, manifest):
    """Validate the deduplicated layout and return immutable byte aliases only."""
    if manifest.get('storage') != 'sha256-member-aliases-v1':
        raise ValueError('documented SHA256 alias storage schema')
    result, referenced = {}, set()
    for row in manifest['logical_files']:
        name, blob, digest, count = row['path'], row['blob'], row['sha256'], row['bytes']
        if not all(isinstance(value, str) for value in (name, blob, digest)):
            raise ValueError('logical path and digest strings')
        path = PurePosixPath(name)
        if not (path.parts and not path.is_absolute() and '..' not in path.parts and
            path.as_posix() == name and ':' not in name and '\\' not in name and name not in result and
            re.fullmatch('[0-9a-f]{64}', digest) and blob == 'blobs/'+digest and
            isinstance(count, int) and not isinstance(count, bool) and count >= 0 and blob in physical):
            raise ValueError('contained unique logical path and content-addressed blob')
        body = physical[blob]
        if not isinstance(body, bytes) or len(body) != count or (
            blob not in referenced and hashlib.sha256(body).hexdigest() != digest):
            raise ValueError('every logical size and digest matches its physical bytes')
        referenced.add(blob)
        result[name] = body
    if set(physical) != referenced:
        raise ValueError('exact referenced physical blob inventory')
    return result


def verify():
    # Check all live helper bytes before importing even the shared inspector.
    for name, digest in PINS.items():
        if hashlib.sha256((ROOT/'tests'/name).read_bytes()).hexdigest() != digest:
            raise ValueError('pinned live reader: '+name)
    fixture = ROOT/'tests/native/vorbis_pcm_exact_host.c'
    if hashlib.sha256(fixture.read_bytes()).hexdigest() != FIXTURE_SHA:
        raise ValueError('pinned live exact PCM fixture')
    spec = importlib.util.spec_from_file_location('pcm_exact_checkpoint_helper',
        ROOT/'tests/vorbis_synthesis_checkpoint.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    need, sha = helper.need, helper.sha
    loaded = {name: helper.load_local('tests/'+name, PINS[name], 'pcm_exact_checkpoint_'+str(index))
        for index, name in enumerate(('test-vorbis-pcm-exact.py', 'test-vorbis-pcm-pair.py',
            'test-vorbis-window-exact.py', 'test-vorbis-window.py'))}
    reader, legacy, window, sine = (loaded[name] for name in ('test-vorbis-pcm-exact.py',
        'test-vorbis-pcm-pair.py', 'test-vorbis-window-exact.py', 'test-vorbis-window.py'))
    physical = helper.archive_members(FOLDER, ARCHIVE_SHA, MANIFEST_SHA)
    manifest = json.loads((ROOT/FOLDER/'manifest.json').read_bytes())
    members = resolve_logical_members(physical, manifest)
    read = lambda name: json.loads(members[name])
    need(len(members) == MEMBERS and sum(map(len, members.values())) == DECODED_BYTES,
        'complete sealed logical archive inventory')
    need(len(physical) == PHYSICAL_MEMBERS and sum(map(len, physical.values())) == PHYSICAL_BYTES,
        'complete sealed physical blob inventory')
    for name in members:
        need(PurePosixPath(name).as_posix() == name and ':' not in name and '\\' not in name,
            'canonical data-only archive member')
    groups = {name.split('/')[0] for name in members}
    need(groups == set(HOST_STATES) | set(FIXTURE_LINT) | {'profiles01', 'tools', 'receipts'},
        'exact retained attempt groups')
    omitted = {row['path']: row for row in manifest['omitted']}
    need(len(omitted) == len(manifest['omitted']) and set(omitted) == OMITTED and
        all(row['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}', row['sha256']) and name not in members
            for name, row in omitted.items()), 'only declared rebuildable executables omitted')

    def sources(group, report, live=False, profile=False):
        for label, digest in report['sources'].items():
            need(PurePosixPath(label).as_posix() == label and '..' not in PurePosixPath(label).parts and
                ':' not in label and '\\' not in label, 'contained source snapshot name')
            body = members[group+'/sources/'+label]
            need(sha(body) == digest, 'every frozen source or DATA byte')
            if not live:
                continue
            if profile:
                relative = 'idf/components/'+label
            elif label.startswith('components/'):
                relative = 'idf/'+label
            elif label.startswith('native/'):
                relative = 'tests/'+label
            elif label == 'runner.py':
                relative = 'tests/test-vorbis-pcm-exact.py'
            elif label == 'supervisor-origin.py':
                relative = 'tests/test-vorbis-floor1-render.py'
            elif label in reader.PINS:
                relative = 'tests/'+reader.PINS[label][0]
            else:
                continue
            if Path(relative).suffix in ('.c', '.h', '.inc', '.py') or Path(relative).name == 'CMakeLists.txt':
                need((ROOT/relative).read_bytes() == body, 'live code equals final executed source snapshot')

    def commands(group, report, successful):
        for row in report['commands']:
            stem = group+'/'+row['name']
            request = read(stem+'.request.json')
            need(request['argv'] == row['child_argv'] and request['nonce'] == row['nonce'] and
                request['timeout'] == (180 if row['name'] == 'execute' else 60) and
                sha(members[stem+'.request.json']) == row['request_sha256'], 'owned request and watchdog binding')
            receipt = row.get('supervisor')
            if not receipt:
                need(not successful and stem+'.receipt.json' not in members and row.get('transport_exit') != 0 and
                    (row.get('transport_exit') is not None or 'transport_pid' not in row),
                    'retained refusal before child dispatch without an unclosed transport')
                continue
            need(receipt == read(stem+'.receipt.json') and receipt['nonce'] == row['nonce'] and
                receipt['request_sha256'] == row['request_sha256'] and row['transport_exit'] == 0 and
                not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and receipt['final'] and
                receipt['new_session'] and receipt['child_pid'] == receipt['owned_pgid'] and receipt['child_reaped'] and
                receipt['group_gone'] and (not successful or receipt['child_returncode'] == 0),
                'all dispatched children terminal and reaped')
        if 'supervisor_sha256' in report:
            supervisor = members[group+'/supervisor.py']
            need(sha(supervisor) == report['supervisor_sha256'], 'frozen supervisor identity')
            definitions = [ast.literal_eval(node.value)
                for node in ast.parse(members[group+'/sources/supervisor-origin.py']).body
                if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and
                    target.id == 'SUPERVISOR' for target in node.targets)]
            need(len(definitions) == 1 and definitions[0].count('assert 0<timeout<=60') == 1 and
                supervisor == definitions[0].replace('assert 0<timeout<=60', 'assert 0<timeout<=180').encode(),
                'exact single timeout-cap derivation preserves ownership and reaping logic')

    need(reader.PCM_ARCHIVE == PCM_ARCHIVE and reader.PCM_MANIFEST == PCM_MANIFEST and
        window.PRIOR_SHA == OVERLAP_ARCHIVE and window.PRIOR_MANIFEST_SHA == OVERLAP_MANIFEST and
        reader.PINS == {'legacy-reader.py': ('test-vorbis-pcm-pair.py', PINS['test-vorbis-pcm-pair.py']),
            'window-reader.py': ('test-vorbis-window-exact.py', PINS['test-vorbis-window-exact.py']),
            'sine-oracle.py': ('test-vorbis-window.py', PINS['test-vorbis-window.py'])},
        'unchanged independent pure readers and both prior DATA lineages')
    old_input, old_capture, old_report = reader.saved_pcm()
    overlap, overlap_report = reader.saved_overlap(window)
    model = reader.model(legacy, window, old_input, old_capture, overlap)
    original_pcm = json.loads(old_report)
    need(original_pcm['completed'] and original_pcm['passed'] and
        original_pcm['capture_sha256'] == sha(old_capture) and original_pcm['input_sha256'] == sha(old_input) and
        original_pcm['measurement'] == model['legacy_measurements'] and
        model['legacy_measurements']['rows'] == 2479 and model['legacy_measurements']['pcm_values'] == 478388 and
        model['witness_metrics'] == EXPECTED_WITNESSES, 'every original PCM batch/output and overlap witness identity')
    report, capture = helper.clean_host(members, FINAL_HOST)
    sources(FINAL_HOST, report, live=True)
    commands(FINAL_HOST, report, successful=True)
    for label, body in (('saved-pcm-input.bin', old_input), ('saved-pcm-capture.bin', old_capture),
        ('saved-pcm-report.json', old_report), ('saved-overlap-capture.bin', overlap),
        ('saved-overlap-report.json', overlap_report)):
        need(members[FINAL_HOST+'/sources/'+label] == body, 'exact original DATA bytes retained without legacy C execution')
    scalar_body = (json.dumps(model['scalars'], separators=(',', ':'))+'\n').encode()
    recipe = dict(schema='owned-exact-PCM-scalar-recipe-v1', rows=EXPECTED_SCALARS, half_boundaries=65538,
        half_perturbation_variants=3, widths=list(range(1, 107)), shifts=[-2148, 0, 1023],
        genuine_tail_rows=4, wide_merge_matrix_rows=432, wide_merge_widths=[64, 65, 105, 106],
        normalized_exponent_distances=[0, 1, 2], model_sha256=sha(scalar_body))
    need(read(FINAL_HOST+'/scalar-recipe.json') == recipe and
        members[FINAL_HOST+'/input.bin'] == reader.encode(model) and
        recipe['model_sha256'] == report['scalar_model_sha256'] and
        sha(members[FINAL_HOST+'/input.bin']) == report['input_sha256'],
        'complete regenerated scalar model and full raw-input recipe')
    need(reader.fraction_anchors() == report['fraction_anchors'] == 2033 and
        legacy.fraction_anchors() == report['legacy_fraction_anchors'] == 2033 and
        report['witnesses'] == EXPECTED_WITNESSES, 'both independent Fraction anchor sets and complete witness provenance')
    need([row['name'] for row in report['commands']] == ['compiler-version', 'compile', 'execute'] and
        report['sanitizers'] == ['address', 'undefined'] and all(not report[key] for key in
            ('native_executed', 'production_selected', 'old_overlap_API_executed', 'old_PCM_API_executed',
                'deferred_scopes_resumed')), 'complete new exact-window and exact PCM host scope')
    argv = report['commands'][1]['child_argv']
    units = [arg.replace('\\', '/') for arg in argv if arg.endswith('.c')]
    suffixes = ['components/native_vorbis_window/window.c', 'components/native_vorbis_window_exact/product.c',
        'components/native_vorbis_window_exact/view.c', 'components/native_vorbis_pcm_exact/pcm.c',
        'components/native_vorbis_pcm_exact/windows.c', 'native/vorbis_pcm_exact_host.c']
    need(all(flag in argv for flag in ('-UNDEBUG', '-fno-fast-math', '-ffp-contract=off', '-Wall', '-Wextra',
        '-Werror', '-fsanitize=address,undefined', '-fno-sanitize-recover=all')) and len(units) == len(suffixes) and
        all(unit.endswith('/sources/'+suffix) for unit, suffix in zip(units, suffixes)),
        'all six actual units instrumented without the old overlap or PCM implementation')
    measured = reader.compare(capture, model, window, sine)
    corruptions = reader.corruption_controls(capture, model, window, sine)
    need(measured == report['measurements'] and corruptions == report['corruption_controls'] == EXPECTED_CORRUPTIONS and
        report['controls'] == EXPECTED_CONTROLS and measured['scalar_rows'] == EXPECTED_SCALARS,
        'complete numerical replay, full guard totals and every corruption control')
    need(measured['legacy_batches'] == 2479 and measured['legacy_pcm_values'] == 478388 and
        measured['scalar_widths'] == 106 and measured['invalid_scalar_rows'] == 21 and
        measured['genuine106_tail_witnesses'] == 4 and measured['wide_merge_matrix_rows'] == 432 and
        measured['half_boundaries'] == 65538 and measured['half_perturbation_variants'] == 3 and
        measured['adapter_rows'] == 864 and measured['ready_rows'] == 648 and
        measured['adapter_pcm_values'] == 598992 and measured['exact_window_terms'] == 1197984 and
        measured['preserved_underflow_witnesses'] == 17962 and measured['preserved_witnesses_at_least1074'] == 13767 and
        measured['coefficients'] == 8160 and measured['coefficient_bound'] == 2e-15 and
        measured['maximum_coefficient_error'] <= 2e-15 and sine.BOUND == 2e-15 and
        not measured['old_overlap_API_executed'] and not measured['old_PCM_API_executed'] and
        not measured['deferred_scopes_resumed'] and not measured['full_decoder_qualified'],
        'all original DATA, widths, half grids, real-product tails and exact adapter outputs')
    need(members[FINAL_HOST+'/execute.stdout.log'].decode().strip() ==
        'PCM_EXACT batches=2479 scalars={scalars} adapters=864 refusals={refusals} checks={checks}'.format(**EXPECTED_CONTROLS),
        'actual fixture guard totals')
    seal = read(SEAL)
    need(all(seal[key] for key in ('passed', 'live_code_headers_CMake_readers_identical',
        'all_handles_terminal', 'host03_04_numeric_capture_identical')) and
        seal['runner_sha256'] == PINS['test-vorbis-pcm-exact.py'] and seal['fixture_sha256'] == FIXTURE_SHA and
        seal['witnesses'] == EXPECTED_WITNESSES and seal['controls'] == EXPECTED_CONTROLS and
        seal['corruption_controls'] == EXPECTED_CORRUPTIONS and
        seal['supervisor_only_change'] == 'assert 0<timeout<=60 -> assert 0<timeout<=180' and
        seal['execution_timeout_seconds'] == 180 and not seal['old_overlap_API_executed'] and
        not seal['old_PCM_API_executed'] and not seal['deferred_scopes_resumed'],
        'sealed source, watchdog, scope and complete corpus provenance')
    for name, key in (('pcm.c', 'pcm_source_sha256'), ('windows.c', 'adapter_source_sha256')):
        need(seal[key] == sha(members[FINAL_HOST+'/sources/components/native_vorbis_pcm_exact/'+name]),
            'seal binds exact production source bytes')
    for key in ('input_sha256', 'scalar_model_sha256', 'capture_sha256', 'binary_sha256'):
        need(seal[key] == report[key], 'seal binds every final numerical artifact')

    profiles = read('profiles01/report.json')
    sources('profiles01', profiles, live=True, profile=True)
    names = ['lx6-version', 'lx6-pcm', 'lx6-windows', 'lx6-header',
        'rv32-version', 'rv32-pcm', 'rv32-windows', 'rv32-header', 'lint-pcm', 'lint-windows']
    need(profiles['completed'] and profiles['passed'] and profiles['source_only'] and
        not profiles['native_executed'] and [row['name'] for row in profiles['commands']] == names,
        'all ten source-only profile commands without metadata repair')
    for row in profiles['commands']:
        need(row['returncode'] == 0 and not row.get('forced_stop'), 'source profile process terminal')
        for stream in ('stdout', 'stderr'):
            need(sha(members['profiles01/'+row['name']+'.'+stream+'.log']) == row[stream+'_sha256'],
                'unaltered source profile diagnostics')
    need(profiles['lint'] == [dict(unit='pcm', warnings=0, errors=0), dict(unit='windows', warnings=0, errors=0)] and
        all(not members['profiles01/'+name+'.'+stream+'.log'] for name in names[-2:] for stream in ('stdout', 'stderr')),
        'both production C units have zero lint diagnostics')
    need(len(profiles['objects']) == 6 and {row['name'] for row in profiles['objects']} ==
        {target+'-'+unit+'.o' for target in ('lx6', 'rv32') for unit in ('pcm', 'windows', 'header')},
        'all six actual C and C++ source objects')
    for row in profiles['objects']:
        body = members['profiles01/'+row['name']]
        machine = 94 if row['name'].startswith('lx6-') else 243
        need(sha(body) == row['sha256'] and body[:6] == b'\x7fELF\x01\x01' and
            int.from_bytes(body[16:18], 'little') == 1 and
            int.from_bytes(body[18:20], 'little') == row['machine'] == machine,
            'hash-bound little-endian ELF32 relocatable for LX6 or RV32')
    frames = {}
    for name, text in profiles['stack_records'].items():
        need(members['profiles01/'+name].decode().replace('\r\n', '\n') == text, 'unaltered compiler stack record')
        parsed = {}
        for line in text.splitlines():
            site, count, kind = line.split('\t')
            need(kind == 'static', 'only static own-function stack records')
            parsed[site.rsplit(':', 1)[-1]] = int(count)
        frames[name] = parsed
    for target, three, rounding in (('lx6', 320, 256), ('rv32', 304, 288)):
        need(frames[target+'-pcm.su']['native_vorbis_pcm_s16_product_pair'] == 192 and
            frames[target+'-pcm.su']['three_sign'] == three and
            frames[target+'-pcm.su']['rounded_sample'] == rounding and
            frames[target+'-windows.su']['native_vorbis_pcm_s16_windows'] == 112,
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
            lint['source_sha256'] == sha(members[expected['source_group']+'/sources/native/vorbis_pcm_exact_host.c']),
            'honest fixture diagnostics and exact source binding')
        if 'generated_warnings' in lint:
            generated = re.findall(rb'^(\d+) warnings generated\.', diagnostics, re.MULTILINE)
            need(len(generated) <= 1 and lint['generated_warnings'] == (int(generated[0]) if generated else 0),
                'unaltered generated warning summary')
        need(members[group+'/clang-tidy.yaml'] == members['profiles01/clang-tidy.yaml'] ==
            (ROOT/'.clang-tidy').read_bytes(), 'unchanged lint configuration without added suppressions')
        lint_results[group] = actual
    need(seal['displayed_fixture_lint_warnings'] == 27 and seal['generated_fixture_lint_warnings'] == 48 and
        seal['default_suppressed_system_warnings'] == 5 and seal['fixture_lint_errors'] == 0 and
        b'48 warnings generated.' in members['fixture-lint02/stderr.log'] and
        b'Suppressed 5 warnings (5 in non-user code).' in members['fixture-lint02/stderr.log'],
        'honest generated, displayed and default system-header diagnostics')
    history = {}
    for group, expected in HOST_STATES.items():
        old = read(group+'/report.json')
        sources(group, old)
        commands(group, old, successful=old['passed'] or group == 'host03')
        actual = dict(completed=old['completed'], passed=old['passed'], commands=len(old['commands']))
        need(actual == expected, 'every retained historical host state')
        if group in HISTORICAL_ERRORS:
            need(not old['passed'] and HISTORICAL_ERRORS[group] in old.get('error', ''),
                'documented historical preparation, dispatch or reader failure')
        if group == 'host03':
            need(not members[group+'/execute.stderr.log'] and
                members[group+'/execute.stdout.log'] == members['host04/execute.stdout.log'],
                'historical unchanged-probe failure followed successful guarded C execution')
        if old.get('capture_sha256'):
            need(sha(members[group+'/capture.bin']) == old['capture_sha256'], 'historical raw capture identity')
        if old['passed']:
            helper.clean_host(members, group)
            need(omitted[group+'/pcm-exact']['sha256'] == old['binary_sha256'] and
                old['controls'] == HISTORICAL_CONTROLS[group] and members[group+'/execute.stdout.log'].decode().strip() ==
                'PCM_EXACT batches=2479 scalars={scalars} adapters=864 refusals={refusals} checks={checks}'.format(**old['controls']),
                'every historical executable identity and actual guard total')
        history[group] = actual
    # Remove only the new matrix from the final data, renumbering scalar row
    # IDs. This proves every earlier scalar and both complete DATA sections
    # retained their input bits and numerical results across the bounded addition.
    old_model = dict(model)
    old_model['scalars'] = [row for row in model['scalars'] if not row['matrix']]
    need(len(old_model['scalars']) == 207979, 'all pre-matrix scalar rows retained')
    old_recipe_input = reader.encode(old_model)
    for group in ('host02', *PARITY_GROUPS):
        need(members[group+'/input.bin'] == old_recipe_input, 'complete pre-matrix input identity')
    count_at = len(old_capture)
    start = count_at + 4
    reduced = bytearray(capture[:count_at])+struct.pack('<I', len(old_model['scalars']))
    prior_index = 0
    for index, row in enumerate(model['scalars']):
        if row['matrix']:
            continue
        at = start+74*index
        reduced.extend(struct.pack('<I', prior_index)+capture[at+4:at+74])
        prior_index += 1
    reduced.extend(capture[start+74*len(model['scalars']):])
    for group in PARITY_GROUPS:
        need(members[group+'/capture.bin'] == reduced,
            'all pre-matrix source, scalar, lookup, adapter and PCM capture bytes retained')
    return dict(passed=True, physical_members=len(physical), physical_decoded_bytes=sum(map(len, physical.values())),
        logical_members=len(members), logical_decoded_bytes=sum(map(len, members.values())),
        measurements=measured, legacy_measurements=model['legacy_measurements'], witnesses=EXPECTED_WITNESSES,
        fraction_anchors=2033, legacy_fraction_anchors=2033, controls=report['controls'],
        corruption_controls=corruptions, historical_attempts=history, profile_commands=10, ELF32_objects=6,
        production_lint_warnings=0, fixture_lint=lint_results, own_function_frames=frames,
        archived_code_executed=False, commands_reexecuted=0, files_extracted=False, native_executed=False,
        old_overlap_API_executed=False, old_PCM_API_executed=False, deferred_scopes_resumed=False,
        full_decoder_qualified=False)


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
