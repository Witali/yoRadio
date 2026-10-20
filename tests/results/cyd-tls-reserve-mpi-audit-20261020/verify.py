#!/usr/bin/env python3
"""Offline archival/source-entry consistency only; no SDK or runtime work."""
import hashlib
import json
import pathlib
import re
import sys

RAW_REPORT_SHA = 'e37862e39ea2b612eae72a660bc83454f8a8fbbf658a29dc6c0de33e40423001'


class VerificationError(Exception):
    def __init__(self, code, detail):
        self.code, self.detail = code, detail
        super().__init__(detail)


def require(condition, code, detail):
    if not condition:
        raise VerificationError(code, detail)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(root):
    root = root.resolve()

    def inside(relative):
        require(isinstance(relative, str) and '\\' not in relative, 'unsafe_path', str(relative))
        pure = pathlib.PurePosixPath(relative)
        require(relative and not pure.is_absolute() and ':' not in relative and
                all(part not in ('.', '..') for part in pure.parts), 'unsafe_path', relative)
        path = (root / pure).resolve()
        require(path.is_relative_to(root), 'unsafe_path', relative)
        return path

    def read(relative):
        return json.loads(inside(relative).read_text(encoding='utf-8'))

    manifest = read('manifest.json')
    require(manifest.get('schema') == 'cyd-tls-reserve-mpi-audit-archive-v1', 'schema', 'Unknown manifest')
    files = manifest['files']
    require({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == set(files) | {'manifest.json'},
            'file_set', 'Missing or additional files')
    for name, item in files.items():
        raw = inside(name).read_bytes()
        require(len(raw) == item['bytes'] and sha(raw) == item['sha256'], 'manifest_identity', name)
        require(not raw.startswith((b'!<arch>\n', b'\x7fELF', b'MZ')), 'binary_payload', name)
    require(inside('.gitattributes').read_text(encoding='utf-8') == '* -text\n', 'text_attributes', 'Byte-exact attributes required')
    require(sha(inside('raw/report.json').read_bytes()) == RAW_REPORT_SHA, 'raw_report_identity', 'Accepted report changed')
    report = read('raw/report.json')
    mapping = read('path-map.json')
    omitted = read('omitted-binaries.json')['artifacts']
    payloads = mapping['payloads']
    inputs = report['evidence']['inputs']

    def mapped(record, expected=None, byte_count=None):
        require(record['sha256'] == (expected or record['sha256']), 'mapping_hash', str(record))
        if byte_count is not None:
            require(record['bytes'] == byte_count, 'mapping_bytes', str(record))
        if record['disposition'] == 'preserved_byte_exact':
            path = inside(record['archive_path'])
            data = path.read_bytes()
            require(sha(data) == record['sha256'] and len(data) == record['bytes'], 'mapped_identity', record['archive_path'])
            return path
        require(record['disposition'] == 'omitted_binary', 'mapping_disposition', str(record))
        item = omitted[record['omitted_artifact']]
        require(item['sha256'] == record['sha256'] and item['bytes'] == record['bytes'], 'omitted_identity', str(record))
        return None

    require(set(payloads) == set(report['evidence']['payloads']) | {'report.json'}, 'payload_set', 'Every raw payload required')
    for name, item in report['evidence']['payloads'].items():
        mapped(payloads[name], item['sha256'], item['bytes'])
    mapped(payloads['report.json'], RAW_REPORT_SHA)
    require(len(inputs) == 82 and set(mapping['inputs']) == set(inputs), 'input_set', 'All82historicalinputs required')
    for original, item in inputs.items():
        path = mapped(mapping['inputs'][original], item['sha256'], item['bytes'])
        if item.get('snapshot'):
            require(path is not None and path.name == item['sha256'], 'snapshot_binding', original)
        else:
            require(path is None, 'hash_only_input', original)
    require(len(omitted) == 10 and sum(i['kind'] == 'sdk_build_archive' for i in omitted.values()) == 6 and
            sum(i['kind'] == 'tool_executable' for i in omitted.values()) == 4,
            'omission_counts', 'Expected6existingSDKarchives/4tools; no extracted objects')
    for item in omitted.values():
        original = inputs[item['original_path']]
        require(item['sha256'] == original['sha256'] and item['bytes'] == original['bytes'] and item['role'] == original['role'],
                'omission_metadata', item['original_path'])

    entries = []

    def visit(value):
        if isinstance(value, dict):
            if {'path', 'line', 'token', 'sha256', 'snapshot', 'link'} <= set(value):
                entries.append(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(report)
    require(len(entries) >= 35, 'entry_count', 'Missing source-entry evidence')
    for entry in entries:
        record = mapping['inputs'][entry['path']]
        path = mapped(record, entry['sha256'])
        require(path is not None, 'entry_snapshot', entry['path'])
        lines = path.read_text(encoding='utf-8').splitlines()
        require(0 < entry['line'] <= len(lines) and entry['token'] in lines[entry['line'] - 1], 'entry_token_line', entry['link'])
        require(entry['snapshot'] == inputs[entry['path']]['snapshot'], 'entry_snapshot_alias', entry['link'])
    links = set(re.findall(r'\[[^\]]+\]\(([^\n)]+)\)', inside('raw/report.json').read_text(encoding='utf-8')))
    links = {link for link in links if re.match(r'^[A-Za-z]:/', link)}
    require(links == set(mapping['markdown_line_links']), 'link_set', 'Every absolute link must map')
    for original, entry in mapping['markdown_line_links'].items():
        path = mapped(entry)
        require(path is not None and 0 < entry['line'] <= len(path.read_text(encoding='utf-8').splitlines()), 'link_line', original)

    config_path = next(path for path in inputs if path.endswith('build-c3-transfer\\sdkconfig'))
    config = mapped(mapping['inputs'][config_path]).read_text(encoding='utf-8')
    values = {}
    for line in config.splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            values[key] = value
        elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
            values[line[2:-11]] = 'n'
    require(all(values.get(key, 'absent') == value for key, value in report['frozen_cyd_profile'].items()), 'profile_binding', 'Profile must match captured config')
    for key, value in {'CONFIG_MBEDTLS_DYNAMIC_BUFFER': 'n', 'CONFIG_MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH': 'n',
                       'CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN': '16384', 'CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN': '4096',
                       'CONFIG_MBEDTLS_HARDWARE_MPI': 'y', 'CONFIG_FREERTOS_UNICORE': 'n'}.items():
        require(values.get(key) == value, 'bounded_profile', key)
    rows = read('raw/selected-compile-rows.json')
    require(rows['executed'] is False and len(rows['rows']) == 7, 'compile_metadata_only', 'Seven rows are metadata, not builds')
    comparison = read('raw/sdk-dynamic-comparison.json')
    for name, record in comparison.items():
        for version, prefix in [('v6.1', 'donor'), ('v6.0.2', 'cyd')]:
            original = next(path for path in inputs if '\\' + version + '\\' in path and path.endswith('\\port\\dynamic\\' + name))
            path = mapped(mapping['inputs'][original], record[prefix + '_raw_sha256'])
            require(sha(path.read_text(encoding='utf-8').encode()) == record[prefix + '_lf_sha256'], 'dynamic_normalized_hash', original)
    guard = report['donor_dynamic_comparison']['hash_guard_observation']
    require(guard['cyd_matches_donor_patch_guard'] is False and guard['installed_donor_sdk61_matches_guard'] is False,
            'historical_guard_mismatch', 'Source compatibility observation must remain bounded')
    require([gate['id'] for gate in report['unrun_gates']] == ['R1', 'R2', 'R3', 'R4', 'M1', 'M2', 'M3', 'M4'],
            'pending_gates', 'All eight gates remain unrun')
    require(report['status'] == 'read_only_audit_complete_both_candidates_unimplemented_and_unqualified' and
            'AAC/deferred private owner-view excluded' in report['scope'] and
            manifest['qualification_status'] == 'audit_complete_both_default_off_candidates_unimplemented_target_unqualified',
            'scope_status', 'No implementation/runtime qualification or deferred work')
    require(manifest['no_runtime_mpi_or_savings_claim'] is True, 'no_runtime_claim', 'No runtime/savings evidence exists')
    return {'passed': True, 'manifest_sha256': sha(inside('manifest.json').read_bytes()),
            'raw_report_sha256': RAW_REPORT_SHA, 'files_verified': len(files), 'historical_inputs': len(inputs),
            'omitted_binary_artifacts': len(omitted), 'source_entry_checks': len(entries), 'mapped_line_links': len(links),
            'pending_gates': 8, 'builds_preprocessor_crypto_network_runs': 0}


if __name__ == '__main__':
    try:
        require(len(sys.argv) <= 2, 'arguments', 'Usage: verify.py [archive-directory]')
        root = pathlib.Path(sys.argv[1]) if len(sys.argv) == 2 else pathlib.Path(__file__).resolve().parent
        result = verify(root)
    except VerificationError as error:
        print(json.dumps({'passed': False, 'error': error.code, 'detail': error.detail}, indent=2))
        sys.exit(1)
    except Exception as error:
        print(json.dumps({'passed': False, 'error': 'invalid_archive', 'detail': str(error)}, indent=2))
        sys.exit(1)
    print(json.dumps(result, indent=2))
