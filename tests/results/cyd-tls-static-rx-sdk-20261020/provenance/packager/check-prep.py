"""Synthetic pure prep guards only; no actual campaign plan/collect/write."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from archive_core import Collector, encode, hashfile, ident, require, sha, write_new
import evidence_rules as rules
import verify
import build_archive

HERE = Path(__file__).resolve().parent


def fake_before(name):
    backend, custom, _enabled = rules.SPECS[name]
    before = {'IDF_TARGET': 'esp32', 'IDF_TARGET_ARCH': 'xtensa', 'FREERTOS_UNICORE': False,
              'YORADIO_TLS_EARLY_MPI_LOCK': True, 'YORADIO_TLS_INPUT_RECLAIM': True,
              'MBEDTLS_SSL_IN_CONTENT_LEN': 16384, 'MBEDTLS_SSL_OUT_CONTENT_LEN': 4096,
              'YORADIO_FLAC_DECODER_CUSTOM': custom, 'YORADIO_FLAC_DECODER_ESPRESSIF': not custom,
              'YORADIO_NATIVE_AUDIO_OUTPUT_PDM': backend == 'pdm',
              'YORADIO_NATIVE_AUDIO_OUTPUT_DAC': backend == 'continuous',
              'YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC': backend == 'legacy',
              'COMPILER_RT_LIB_GCCLIB': True, 'COMPILER_RT_LIB_NAME': 'gcc', 'FREERTOS_HZ': 1000}
    for key, (value, _) in rules.TRANSITIONS.items():
        if value is not None:
            before[key] = value
    return before


def fake_after(before, name, kind):
    after = copy.deepcopy(before)
    if kind == 'export':
        after[rules.RESERVE] = rules.SPECS[name][2]
    else:
        for key, (_, value) in rules.TRANSITIONS.items():
            if value is None:
                after.pop(key, None)
            else:
                after[key] = value
    return after


def fake_summary():
    return {'schema': 'cyd-static-rx-clang-qualification-repair-v1', 'passed': True,
            'exports': 7, 'full_clang_runs': 6,
            'source_snapshot': {'commit': rules.HEAD, 'dirty': False, 'source_dirty': False,
                                'untracked': [], 'content_sha256': '1' * 64},
            'reports': [{'kind': kind, 'origin': origin,
                         'report': {'path': '/synthetic-only/' + kind + '-' + name + '/report.json',
                                    'bytes': 1, 'sha256': sha((kind + name).encode())}}
                        for name in rules.SPECS for kind, origin in
                        [('export', 'original')] + ([('clang', 'successor')] if name != 'disabled-pdm' else [])],
            'repair_marker': {'sha256': rules.REPAIR_MARKER},
            'original_qualifier_failure': {'sha256': rules.FAILED_PDM},
            'physical_qualified': False, 'heap_saving_claimed': False,
            'warning_triage_remains_explicit': True}


def main():
    output = HERE / 'prep-check03'
    require(not output.exists(), 'Never overwrite prep controls')
    output.mkdir()
    names = ['archive_core.py', 'build_archive.py', 'evidence_rules.py', 'verify.py',
             'check-prep.py', 'SPEC.md', 'README.template.md']
    inputs = [ident(HERE / name) for name in names]
    results = []
    report = {'schema': 'cyd-static-rx-sdk-archive-prep-check-v1', 'passed': False,
              'scope': 'Pure synthetic schema/storage/config guards only; no actual campaign/archive qualification',
              'inputs': inputs, 'results': results,
              'actual_plan_collect_write_sdk_compiler_git_device_invocations': 0}

    def accepted(name, action):
        action()
        results.append({'name': name, 'expected': 'accept', 'accepted': True})

    def rejected(name, fragment, action):
        try:
            action()
        except ValueError as error:
            require(fragment in str(error), 'Wrong rejection predicate: ' + name + ': ' + str(error))
            results.append({'name': name, 'expected': 'reject', 'rejected': True, 'diagnostic': str(error)})
        else:
            raise ValueError('Missing required rejection: ' + name)

    try:
        for name in rules.SPECS:
            before = fake_before(name)
            for kind in ['export'] + (['clang'] if name != 'disabled-pdm' else []):
                after = fake_after(before, name, kind)
                accepted('synthetic_complete_' + kind + '_' + name,
                         lambda b=before, a=after, n=name, k=kind: rules.config_scope(b, a, n, k))
        before = fake_before('pdm')
        after = fake_after(before, 'pdm', 'clang')
        for key in rules.TRANSITIONS:
            changed = copy.deepcopy(after)
            changed[key] = None
            rejected('clang_null_or_type:' + key, 'Complete typed configuration scope mismatch',
                     lambda a=changed: rules.config_scope(before, a, 'pdm', 'clang'))
        for key, value in [('IDF_TARGET', 'esp32c3'), ('FREERTOS_UNICORE', True),
                           ('MBEDTLS_SSL_IN_CONTENT_LEN', 4096), ('FREERTOS_HZ', 100),
                           ('YORADIO_TLS_INPUT_RECLAIM', False), ('UNEXPECTED_KEY', True)]:
            changed = copy.deepcopy(after)
            changed[key] = value
            rejected('extra_clang_delta:' + key, 'Complete typed configuration scope mismatch',
                     lambda a=changed: rules.config_scope(before, a, 'pdm', 'clang'))
        wrong = copy.deepcopy(after)
        wrong[rules.RESERVE] = 1
        rejected('reserve_integer_is_not_bool', 'Complete typed configuration scope mismatch',
                 lambda: rules.config_scope(before, wrong, 'pdm', 'clang'))
        gcc = fake_after(before, 'pdm', 'export')
        gcc['IDF_TOOLCHAIN'] = 'clang'
        rejected('gcc_cannot_accept_clang_changes', 'Complete typed configuration scope mismatch',
                 lambda: rules.config_scope(before, gcc, 'pdm', 'export'))

        closed = fake_summary()
        accepted('synthetic_seven_original_six_successor_matrix', lambda: rules.summary(closed))
        for name, mutate, fragment in [
            ('partial_matrix', lambda v: v['reports'].pop(), 'Exact distinct'),
            ('old_clang_origin', lambda v: v['reports'][1].update(origin='original'), 'Exact distinct'),
            ('duplicate_profile', lambda v: v['reports'].__setitem__(1, copy.deepcopy(v['reports'][0])), 'Exact distinct'),
            ('claimed_heap_benefit', lambda v: v.update(heap_saving_claimed=True), 'Honest closure limitations'),
            ('physical_overclaim', lambda v: v.update(physical_qualified=True), 'Honest closure limitations'),
            ('wrong_source', lambda v: v['source_snapshot'].update(commit='2' * 40), 'Exact frozen clean source'),
            ('wrong_marker', lambda v: v['repair_marker'].update(sha256='2' * 64), 'Exact repair marker'),
        ]:
            changed = copy.deepcopy(closed)
            mutate(changed)
            rejected(name, fragment, lambda v=changed: rules.summary(v))
        script_path = rules.WORKSPACE + '/.build/cyd-clang-config-repair-prep-01/repair.py'
        receipt = {'schema': 'cyd-static-rx-sdk-close-terminal-v1', 'status': 'TERMINAL', 'returncode': 0,
                   'observed_by': 'root', 'summary_path': '/synthetic/summary.json', 'summary_sha256': '3' * 64,
                   'cwd': rules.WORKSPACE,
                   'source_commit': rules.HEAD, 'repair_marker_sha256': rules.REPAIR_MARKER,
                   'original_marker_sha256': rules.ORIGINAL_MARKER,
                   'terminal_proof': {'tool_handle': 'synthetic-only', 'tool_chunk': 'synthetic-only'},
                   'argv': ['python', script_path, 'close', '--repair-marker-sha256', rules.REPAIR_MARKER]}
        check_terminal = lambda r: rules.terminal(closed, r, '3' * 64, '/synthetic/summary.json', script_path)
        accepted('synthetic_complete_terminal_schema_not_actual_proof', lambda: check_terminal(receipt))
        raw_relative = copy.deepcopy(receipt)
        raw_relative['argv'][1] = '.build/cyd-clang-config-repair-prep-01/repair.py'
        original_raw_argv = list(raw_relative['argv'])
        accepted('truthful_relative_raw_argv_and_explicit_cwd', lambda: check_terminal(raw_relative))
        require(raw_relative['argv'] == original_raw_argv, 'Raw receipt argv must remain unchanged')
        for name, mutate, fragment in [
            ('running_not_terminal', lambda v: v.update(status='RUNNING'), 'authoritative close terminal0'),
            ('terminal_one', lambda v: v.update(returncode=1), 'authoritative close terminal0'),
            ('false_is_not_exit_zero', lambda v: v.update(returncode=False), 'authoritative close terminal0'),
            ('wrong_summary_sha', lambda v: v.update(summary_sha256='4' * 64), 'exact closure pins'),
            ('missing_actual_handle', lambda v: v['terminal_proof'].update(tool_handle=''), 'Actual tool terminal'),
            ('original_close_not_successor', lambda v: v['argv'].__setitem__(1, '/synthetic/campaign.py'), 'actual successor close'),
            ('wrong_execution_cwd', lambda v: v.update(cwd='C:/Work/yoRadio'), 'pinned execution cwd'),
            ('relative_execution_cwd', lambda v: v.update(cwd='.'), 'pinned execution cwd'),
            ('wrong_relative_script', lambda v: v['argv'].__setitem__(1, '.build/unrelated/repair.py'), 'actual successor close'),
            ('wrong_absolute_script', lambda v: v['argv'].__setitem__(1, 'C:/other/repair.py'), 'actual successor close'),
            ('wrong_command_suffix', lambda v: v['argv'].append('--unexpected'), 'actual successor close'),
            ('wrong_command_phase', lambda v: v['argv'].__setitem__(2, 'qualify'), 'actual successor close'),
            ('drive_relative_script', lambda v: v['argv'].__setitem__(1, 'C:repair.py'), 'Invalid script path in raw argv'),
            ('root_relative_script', lambda v: v['argv'].__setitem__(1, '\\repair.py'), 'Invalid script path in raw argv'),
        ]:
            changed = copy.deepcopy(receipt)
            mutate(changed)
            rejected(name, fragment, lambda v=changed: check_terminal(v))
        failed = {'passed': False, 'kind': 'clang', 'row': 'pdm',
                  'error': "RuntimeError('Unexpected complete normalized config delta: synthetic-only')"}
        accepted('synthetic_historical_nonpass_preserved', lambda: rules.historical_failure(failed, rules.FAILED_PDM))
        failed['passed'] = True
        rejected('historical_failure_cannot_be_relabelled_pass', 'must remain exact nonpass',
                 lambda: rules.historical_failure(failed, rules.FAILED_PDM))

        fixture = output / 'tiny-storage-fixture'
        fixture.mkdir()
        first, second, executable = fixture / 'first.log', fixture / 'second.log', fixture / 'fake.elf'
        first.write_bytes(b'Pure synthetic repeated log.\n' * 20)
        second.write_bytes(first.read_bytes())
        executable.write_bytes(b'\x7fELFsynthetic-not-an-actual-application')
        collector = Collector(fixture)
        one = collector.add(first, 'pure synthetic text')
        two = collector.add(second, 'pure synthetic text')
        omitted = collector.add(executable, 'pure synthetic binary classifier fixture')
        accepted('text_deduplicates_by_raw_sha', lambda: require(one['stored_path'] == two['stored_path'], 'dedup'))
        accepted('binary_bytes_are_omitted', lambda: require(omitted['disposition'] == 'omitted', 'omission'))
        accepted('gzip_is_deterministic', lambda: require(collector.payload(one) == collector.payload(two), 'gzip'))
        for row in collector.entries:
            if row['disposition'] == 'stored' and not (fixture / row['stored_path']).exists():
                write_new(fixture / row['stored_path'], collector.payload(row))
        accepted('tiny_fixture_stored_payload_hashes', lambda: verify.payloads(fixture, collector.entries))
        changed = copy.deepcopy(collector.entries)
        changed[0]['stored_sha256'] = '0' * 64
        rejected('corrupt_encoded_payload_pin', 'Encoded payload hash mismatch', lambda: verify.payloads(fixture, changed))
        changed = copy.deepcopy(collector.entries)
        changed[0]['sha256'] = '0' * 64
        rejected('corrupt_decoded_payload_pin', 'Decoded payload hash mismatch', lambda: verify.payloads(fixture, changed))
        changed = copy.deepcopy(collector.entries)
        changed[0]['stored_path'] = '../outside'
        rejected('unsafe_storage_member', 'Unsafe archive/repository member', lambda: verify.payloads(fixture, changed))
        changed = copy.deepcopy(collector.entries)
        changed[2]['roles'] = ['full-project lint TU source']
        rejected('required_tu_cannot_be_omitted', 'Required source cannot be omitted', lambda: verify.payloads(fixture, changed))
        for bad in ['../escape', '/absolute', 'C:/absolute', 'a\\b', 'a/./b']:
            rejected('unsafe_path:' + bad, 'Unsafe archive/repository member', lambda p=bad: verify.safe(fixture, p))
        target = {'id': 1, 'original_path': '/synthetic/source.c', 'bytes': 4, 'sha256': '5' * 64}
        container = {'source': {'path': target['original_path'], 'bytes': 4, 'sha256': target['sha256']}}
        entries = [{'id': 0}, target]
        bound = [{'container_id': 0, 'tokens': ['source'], 'target_id': 1, 'kind': 'identity'}]
        accepted('synthetic_original_reference_binding',
                 lambda: verify.bindings_check(entries, {0: encode(container)}, bound))
        target['bytes'] = 5
        rejected('rebound_reference_size', 'Original JSON path/size/SHA reference mismatch',
                 lambda: verify.bindings_check(entries, {0: encode(container)}, bound))
        target['bytes'] = 4
        target['original_path'] = '/synthetic/immutable-seed'
        target['roles'] = ['immutable original full sdkconfig seed']
        historical = [{'container_id': 0, 'tokens': ['source'], 'target_id': 1, 'kind': 'historical_seed'}]
        accepted('historical_seed_bytes_survive_mutable_path_normalization',
                 lambda: verify.bindings_check(entries, {0: encode(container)}, historical))
        target['sha256'] = '6' * 64
        rejected('historical_seed_wrong_bytes', 'Original pre-normalization seed byte relationship mismatch',
                 lambda: verify.bindings_check(entries, {0: encode(container)}, historical))
        nul_text = fixture / 'unknown-input.txt'
        nul_text.write_bytes(b'not a permitted text\0payload')
        rejected('unknown_nul_payload_not_silently_stored', 'Unknown binary/NUL input',
                 lambda: collector.add(nul_text, 'pure unknown binary classifier control'))
        old_identity = ident(first)
        first.write_bytes(b'changed synthetic text')
        rejected('changed_selected_input', 'Selected archival input changed', collector.stable)
        rejected('wrong_original_raw_pin', 'Input identity changed',
                 lambda: Collector(fixture).add(first, 'pure mismatched original identity', old_identity))

        # Reproduce the real retention order with synthetic source/proof bytes.
        # No actual report/SDK source, archive plan or production tree is read.
        tool_fixture = output / 'synthetic-packager-sources'
        tool_fixture.mkdir()
        for name in build_archive.TOOLS:
            (tool_fixture / name).write_bytes(('Synthetic packager source: ' + name + '\n').encode())
        proof = tool_fixture / 'proof.json'
        proof.write_bytes(encode({'inputs': [ident(tool_fixture / name) for name in build_archive.TOOLS]}))
        selected = build_archive.Selection()
        selected_tools = build_archive.packager_sources(selected, tool_fixture)
        selected.document(proof, 'synthetic later proof source identities')
        selected.drain()
        accepted('canonical_packager_paths_survive_later_proof_refs',
                 lambda: build_archive.canonical_packager_paths(selected, selected_tools))
        retained = {row['stored_path']: selected.collector.payload(row)
                    for row in selected.collector.entries if row['disposition'] == 'stored'}
        accepted('standalone_reader_and_rules_bytes_at_root', lambda: require(
            retained['verify.py'] == (tool_fixture / 'verify.py').read_bytes()
            and retained['evidence_rules.py'] == (tool_fixture / 'evidence_rules.py').read_bytes(),
            'Synthetic standalone source bytes missing'))
        reordered = build_archive.Selection()
        reordered.document(proof, 'synthetic original wrong-order control')
        reordered.drain()
        late_tools = build_archive.packager_sources(reordered, tool_fixture)
        rejected('original_late_preferred_path_bug', 'Canonical standalone packager retention path missing',
                 lambda: build_archive.canonical_packager_paths(reordered, late_tools))

        trees = {name: ast.parse((HERE / name).read_bytes(), filename=name) for name in names if name.endswith('.py')}
        imports = {alias.name.split('.')[0] for tree in trees.values() for node in ast.walk(tree)
                   if isinstance(node, ast.Import) for alias in node.names}
        imports |= {node.module.split('.')[0] for tree in trees.values() for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module}
        require(not imports.intersection({'subprocess', 'ctypes', 'socket', 'requests'}), 'No external execution/network APIs')
        require(inputs == [ident(item['path']) for item in inputs], 'Prep source changed during pure checks')
        require(not build_archive.PLAN.exists() and build_archive.PLAN.name == 'plan02.json',
                'Fresh plan02 must remain absent during source preparation; historical plan01 is preserved')
        report.update(passed=True, accepted=sum(item['expected'] == 'accept' for item in results),
                      rejected=sum(item['expected'] == 'reject' for item in results),
                      sources_unchanged=True, ast_parsed=list(trees))
    except BaseException as error:
        report['error'] = repr(error)
        raise
    finally:
        write_new(output / 'report.json', encode(report))
    print(encode({'passed': True, 'accepted': report['accepted'], 'rejected': report['rejected'],
                  'report': ident(output / 'report.json')}).decode())


if __name__ == '__main__':
    main()
