"""Offline stored-byte/reference/matrix verification, using only Python stdlib.

Does not replay archived SDK/tests/qualifiers, read SDK/tool bytes, reconstruct
omitted binaries, or turn report integrity into physical/runtime conformance.
Optional --repository checks only explicitly linked repository evidence/files.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.dont_write_bytecode = True
import evidence_rules as rules


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe(root, relative):
    require(isinstance(relative, str) and '\\' not in relative and ':' not in relative
            and not PurePosixPath(relative).is_absolute()
            and all(part not in ('', '.', '..') for part in relative.split('/')),
            'Unsafe archive/repository member path')
    path = (Path(root) / relative).resolve()
    require(path.is_relative_to(Path(root).resolve()), 'Archive/repository path escape')
    return path


def manifest_files(root, expected_sha):
    raw = (root / 'manifest.json').read_bytes()
    require(re.fullmatch('[0-9a-f]{64}', expected_sha) and sha(raw) == expected_sha,
            'Externally supplied archive manifest SHA mismatch')
    manifest = json.loads(raw)
    require(manifest['schema'] == 'cyd-static-rx-sdk-archive-manifest-v1', 'Known archive manifest schema')
    names = []
    for row in manifest['files']:
        path = safe(root, row['path'])
        data = path.read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Stored archive file hash mismatch')
        names.append(row['path'])
    require(len(names) == len(set(names)), 'Duplicate manifest member')
    actual = {path.relative_to(root).as_posix() for path in root.rglob('*') if path.is_file()}
    require(actual == set(names) | {'manifest.json'}, 'Missing or unmanifested archive file')


def payloads(root, entries):
    decoded = {}
    require([row['id'] for row in entries] == list(range(len(entries))), 'Contiguous unique evidence IDs required')
    require(len(entries) <= 20000, 'Bounded entry count')
    for row in entries:
        require(type(row['bytes']) is int and row['bytes'] >= 0
                and re.fullmatch('[0-9a-f]{64}', row['sha256']) and row['observed_bytes'] is True,
                'Observed size/SHA required for every selected input')
        if row['disposition'] == 'stored':
            require(row['bytes'] <= 64 * 1024 * 1024 and row['encoding'] in ('raw', 'gzip'), 'Bounded known text encoding')
            stored = safe(root, row['stored_path']).read_bytes()
            require(len(stored) == row['stored_bytes'] and sha(stored) == row['stored_sha256'], 'Encoded payload hash mismatch')
            if row['encoding'] == 'gzip':
                with gzip.GzipFile(fileobj=io.BytesIO(stored)) as stream:
                    raw = stream.read(row['bytes'] + 1)
            else:
                raw = stored
            require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Decoded payload hash mismatch')
            raw.decode('utf-8')
            require(b'\0' not in raw and not raw.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')),
                    'Binary bytes cannot be retained as text')
            require(Path(row['original_path']).suffix.lower() not in
                    ('.a', '.bin', '.dll', '.elf', '.exe', '.o', '.obj', '.pyc', '.so', '.zip'),
                    'Binary extension must be omission/reference')
            decoded[row['id']] = raw
        elif row['disposition'] == 'omitted':
            require(row['reason'] and isinstance(row['prefix_hex'], str), 'Explicit binary omission reason/observation')
            require(not any(role in row['roles'] for role in ['full-project lint TU source',
                        'actual marker-guarded SDK supporting source']), 'Required source cannot be omitted')
            prefix = bytes.fromhex(row['prefix_hex'])
            require(Path(row['original_path']).suffix.lower() in
                    ('.a', '.bin', '.dll', '.elf', '.exe', '.o', '.obj', '.pyc', '.so', '.zip')
                    or prefix.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')), 'Unknown omission classification')
        elif row['disposition'] == 'external':
            relative = row['repository_reference']
            require(relative.startswith('tests/results/') and len(PurePosixPath(relative).parts) >= 4,
                    'External payload must be an explicitly linked previous evidence bundle')
            safe(root, relative)  # Validate syntax only; not an archive-local payload.
            require(type(row['linked_manifest_id']) is int, 'Linked bundle manifest identity required')
        else:
            raise ValueError('Unknown evidence disposition')
    return decoded


def bindings_check(entries, decoded, bindings):
    def document(number):
        require(number in decoded, 'Bound evidence JSON must be stored')
        return json.loads(decoded[number])
    for binding in bindings:
        value = document(binding['container_id'])
        for token in binding['tokens']:
            value = value[token]
        target = entries[binding['target_id']]
        if binding['kind'] == 'identity':
            require(value['bytes'] == target['bytes'] and value['sha256'] == target['sha256']
                    and rules.normalize(value['path']) == rules.normalize(target['original_path']),
                    'Original JSON path/size/SHA reference mismatch')
        elif binding['kind'] == 'historical_seed':
            require(value['bytes'] == target['bytes'] and value['sha256'] == target['sha256']
                    and 'immutable original full sdkconfig seed' in target['roles'],
                    'Original pre-normalization seed byte relationship mismatch')
        else:
            require(binding['kind'] == 'sha256' and value == target['sha256'], 'Original scalar SHA reference mismatch')


def nm_symbols(raw):
    result = {}
    for line in raw.decode().splitlines():
        fields = line.split()
        if len(fields) == 4 and re.fullmatch('[0-9a-f]+', fields[0]):
            result[fields[3]] = {'address': int(fields[0], 16), 'bytes': int(fields[1], 16), 'type': fields[2]}
    return result


def verify(root, manifest_sha, repository=None):
    root = Path(root).resolve()
    manifest_files(root, manifest_sha)
    entries = json.loads((root / 'path-map.json').read_bytes())['entries']
    decoded = payloads(root, entries)
    bindings_check(entries, decoded, json.loads((root / 'bindings.json').read_bytes())['bindings'])
    index = json.loads((root / 'index.json').read_bytes())
    require(index['schema'] == 'cyd-static-rx-sdk-archive-index-v1', 'Known archive index')
    document = lambda number: json.loads(decoded[number])
    summary = document(index['summary_id'])
    receipt = document(index['root_terminal_id'])
    old, repair = document(index['original_marker_id']), document(index['repair_marker_id'])
    require(entries[index['original_marker_id']]['sha256'] == rules.ORIGINAL_MARKER
            and entries[index['repair_marker_id']]['sha256'] == rules.REPAIR_MARKER, 'Exact immutable marker identities')
    repair_sources = [item for item in repair['scripts'] if rules.normalize(item['path']).endswith('/repair.py')]
    require(len(repair_sources) == 1, 'Exact frozen successor script path')
    rules.terminal(summary, receipt, entries[index['summary_id']]['sha256'],
                   entries[index['summary_id']]['original_path'], repair_sources[0]['path'])
    rules.source_snapshot(index['source_snapshot'])
    require(index['source_snapshot'] == old['source_snapshot'] == repair['source_snapshot'] == summary['source_snapshot'],
            'All frozen source identities must agree')
    require(repair['original_campaign']['sha256'] == rules.ORIGINAL_SCRIPT
            and repair['exact_typed_clang_delta'] == rules.expected_clang_delta(), 'Exact original helper and strict repair policy')
    failed = document(index['original_failed_pdm_id'])
    rules.historical_failure(failed, entries[index['original_failed_pdm_id']]['sha256'])
    rules.control_report(document(index['pure_policy_controls_id']))
    prep = document(index['pure_archive_preparation_id'])
    require(prep['passed'] is True and prep['sources_unchanged'] is True
            and prep['actual_plan_collect_write_sdk_compiler_git_device_invocations'] == 0
            and prep['scope'].startswith('Pure synthetic schema/storage/config guards only'),
            'Honest source-only archive-tool preparation controls')
    warning_review = index['warning_review_ids']
    require(set(warning_review) == {'comparison.json', 'REVIEW.md', 'pending-history.json', 'review.ps1'}
            and all(number in decoded for number in warning_review.values()), 'Separate complete warning review retention')
    require(entries[warning_review['comparison.json']]['sha256'] ==
            '92d5b58198522f537055b0925d6e701b0d4207ad33fd536c4f85830ec0b4a2e1'
            and entries[warning_review['REVIEW.md']]['sha256'] ==
            '38cda2056bb4fb5112301c7a8a78e89c221fc903298f19d6e96e0d8db06cb2af',
            'Exact root-accepted warning review identities')
    require(index['limits'] == {'physical_qualified': False, 'heap_saving_claimed': False,
            'clang_is_experimental_frontend_profile': True, 'production_compiler_is_gcc': True,
            'omitted_binaries_reconstructed': False, 'original_failed_qualifier_remains_nonpass': True},
            'Exact archive qualification limits required')
    profiles = index['profiles']
    frozen_plan = document(index['original_plan_id'])
    require(len(profiles) == 7 and {row['name'] for row in profiles} == set(rules.SPECS), 'Seven unique profile records')
    selected_reports = []
    full_lint_units, full_lint_warnings = {}, {}
    for profile in profiles:
        name = profile['name']
        frozen_rows = [item for item in frozen_plan['rows'] if item['name'] == name]
        require(len(frozen_rows) == 1, 'One original frozen plan row per profile')
        frozen_row = frozen_rows[0]
        require((profile['backend'], profile['custom_flac'], profile['enabled']) == rules.SPECS[name],
                'Saved backend/custom/reserve profile mismatch')
        before = document(profile['baseline_config_id'])
        baseline = frozen_plan['baselines'][frozen_row['baseline']]
        text_path = baseline['files']['sdkconfig']['snapshot']
        text_rows = [item for item in entries if rules.normalize(item['original_path']) == rules.normalize(text_path)]
        require(len(text_rows) == 1 and text_rows[0]['id'] in decoded, 'Exact frozen baseline raw config text')
        initial = decoded[text_rows[0]['id']]
        newline = b'\r\n' if b'\r\n' in initial else b'\n'
        setting = (('CONFIG_' + rules.RESERVE + '=y') if profile['enabled'] else
                   ('# CONFIG_' + rules.RESERVE + ' is not set')).encode() + newline
        require(b'CONFIG_' + rules.RESERVE.encode() not in initial, 'Baseline must predate reserve setting')
        position = initial.find(b'# Deprecated options for backward compatibility')
        expected_seed = initial[:position] + setting + initial[position:] if position >= 0 else initial + setting
        require(decoded[profile['seed_id']] == expected_seed
                and entries[profile['seed_id']]['sha256'] == frozen_row['seed']['sha256'],
                'Exact original full-config seed relationship')
        for kind in ['export'] + (['clang'] if profile['enabled'] else []):
            metadata = profile[kind]
            report = document(metadata['qualification_id'])
            after = document(metadata['config_id'])
            changes = rules.config_scope(before, after, name, kind)
            require(report['passed'] is True and report['kind'] == kind and report['row'] == name
                    and report['source_snapshot'] == index['source_snapshot']
                    and report['physical_tested'] is False and report['heap_saving_claimed'] is False,
                    'Qualified report exact status/source/scope')
            if kind == 'clang':
                require(report['schema'] == 'cyd-static-rx-clang-qualification-repair-v1'
                        and report['config_delta'] == changes and report['repair_marker']['sha256'] == rules.REPAIR_MARKER,
                        'Successor Clang qualification/policy required')
            else:
                require(report['schema'] == 'cyd-static-rx-production-v2'
                        and report['config_delta'] == {rules.RESERVE: {'before': None, 'after': profile['enabled']}},
                        'Original reserve-only GCC qualification required')
            selected_reports.append(entries[metadata['qualification_id']]['sha256'])
            execution = document(metadata['execution_id'])
            require(execution['status'] == 'TERMINAL_SUCCESS' and execution['kind'] == kind
                    and execution['row'] == name and execution['marker_sha256'] == rules.ORIGINAL_MARKER
                    and execution['source_snapshot_before'] == execution['source_snapshot_after'] == index['source_snapshot'],
                    'Original execution terminal/source identity required')
            require(execution['commands'] and all(command['status'] == 'TERMINAL'
                    and type(command['returncode']) is int and command['returncode'] == 0
                    and len(command['logs']) == 2 for command in execution['commands']),
                    'Every actual executed command has terminal0 and both retained logs')
            require(execution['seed_before_build']['bytes'] == entries[profile['seed_id']]['bytes']
                    and execution['seed_before_build']['sha256'] == entries[profile['seed_id']]['sha256'],
                    'Initial working config bytes recovered through immutable seed')
            require(all(number in decoded for number in metadata['selected_text'].values()),
                    'Selected qualifier text must be stored')
            require(metadata['compile_database_id'] in decoded
                    and all(number in decoded for number in metadata['compiler_description_ids']),
                    'Actual compiler/config description text retained')
            if kind == 'export':
                exported = document(metadata['receipt_id'])
                require(exported['build_check'] == 'PASS' and exported['source_commit'] == rules.HEAD
                        and exported['backend'] == profile['backend'] and exported['target'] == 'esp32'
                        and exported['source_content_sha256'] == index['source_snapshot']['content_sha256'],
                        'Production GCC image receipt identity')
                require(metadata['firmware_link'].startswith('firmware/development/'), 'Saved development firmware link')
                binary_rows = [row for row in entries if row.get('repository_reference') == metadata['firmware_link']]
                require(len(binary_rows) == 1 and binary_rows[0]['disposition'] == 'omitted'
                        and binary_rows[0]['sha256'] == exported['app_sha256']
                        and binary_rows[0]['bytes'] == exported['app_bytes'], 'Firmware app is linked with exact omitted bytes/SHA')
                syms = nm_symbols(decoded[metadata['selected_text']['nm.log']])
                require(('s_rx' in syms) is profile['enabled'] and '__wrap_esp_mbedtls_mem_free' not in syms,
                        'Recorded actual on/off symbol scope and ordinary global free')
                if profile['enabled']:
                    reserve = report['static_rx']
                    probe = reserve['actual_macro_probe']
                    probe_symbols = nm_symbols(decoded[metadata['selected_text']['sdk-rx-size-probe-nm.log']])
                    require(syms['s_rx'] == reserve['symbol'] and syms['s_rx']['bytes'] == probe['actual_macro_bytes']
                            == probe_symbols['yoradio_sdk_rx_size_probe']['bytes']
                            and reserve['record_content'] == after['MBEDTLS_SSL_IN_CONTENT_LEN'],
                            'Actual qualified RX symbol/probe/config sizes agree, without guessed overhead')
            else:
                lint = document(metadata['lint_report_id'])
                results = lint['results']
                require(lint['complete'] is True and lint['errors'] == 0 and lint['source_commit'] == rules.HEAD
                        and lint['units'] == len(results) and len({item['file'] for item in results}) == len(results)
                        and set(metadata['tu_source_ids']) == {item['file'] for item in results},
                        'Complete exact full-project lint results/TU source set')
                for item in results:
                    number = metadata['tu_source_ids'][item['file']]
                    require(number in decoded and entries[number]['sha256'] == item['source_sha256']
                            and item['complete'] is True and item['returncode'] == 0,
                            'Every actual full-project lint TU source/result retained')
                require({entries[number]['sha256'] for number in metadata['lint_artifact_ids']}
                        == {item['sha256'] for item in report['lint_artifacts']}
                        and all(number in decoded for number in metadata['lint_artifact_ids']),
                        'All qualified original lint log/YAML/report artifacts retained')
                require(report['sdk_frontend']['returncode'] == 0
                        and report['sdk_frontend']['scope'].startswith('separate actual SDK overlay frontend'),
                        'Separate actual SDK frontend qualification retained')
                full_lint_units[name], full_lint_warnings[name] = lint['units'], lint['warnings']
    require(len(selected_reports) == 13 and set(selected_reports) == {item['report']['sha256'] for item in summary['reports']},
            'Archive matrix is the exact authoritative successor closure matrix')
    required_links = ('cyd-tls-static-rx-host-20261020', 'cyd-tls-static-rx-qemu-20261020')
    require(all(any(rules.normalize(path).endswith('/' + name) for path in index['linked_manifests'])
                for name in required_links), 'Existing canonical host/QEMU manifest links required')
    for row in entries:
        if row['disposition'] == 'external':
            linked = entries[row['linked_manifest_id']]
            require(linked['id'] in decoded and Path(linked['original_path']).name == 'manifest.json',
                    'Stored previous-bundle manifest for every external reference')
        if repository is not None and 'repository_reference' in row:
            data = safe(Path(repository), row['repository_reference']).read_bytes()
            require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Linked repository payload hash mismatch')
    return {'verified': True, 'source_commit': rules.HEAD, 'gcc_exports': 7, 'successor_clang_qualifications': 6,
            'sdk_revisions_from_original_marker': old['sdk_state'],
            'full_lint_units_from_actual_reports': full_lint_units,
            'full_lint_warnings_from_actual_reports': full_lint_warnings,
            'stored_payloads': len(decoded), 'binary_omissions': sum(row['disposition'] == 'omitted' for row in entries),
            'external_links': sum(row['disposition'] == 'external' for row in entries),
            'linked_repository_payloads_checked': repository is not None,
            'omitted_binaries_reconstructed': False, 'sdk_tests_or_qualifiers_replayed': False,
            'physical_qualified': False, 'heap_saving_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--repository', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, args.manifest_sha256, args.repository), sort_keys=True))


if __name__ == '__main__':
    main()
