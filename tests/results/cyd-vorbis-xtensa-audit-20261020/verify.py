#!/usr/bin/env python3
"""Offline integrity/entry checks only. No SDK, decoder execution or build."""
import hashlib
import json
import pathlib
import re
import sys

RAW_REPORT_SHA256 = 'debd417874bc176f011603ee09875dfcf2c5cade27aee526bcca997ccf82083e'


class VerificationError(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(detail)


def require(condition, code, detail):
    if not condition:
        raise VerificationError(code, detail)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(root):
    root = root.resolve()

    def inside(relative):
        require(isinstance(relative, str) and '\\' not in relative,
                'unsafe_archive_path', str(relative))
        pure = pathlib.PurePosixPath(relative)
        require(relative and not pure.is_absolute() and ':' not in relative and
                all(part not in ('.', '..') for part in pure.parts),
                'unsafe_archive_path', relative)
        path = (root / pure).resolve()
        require(path.is_relative_to(root), 'unsafe_archive_path', relative)
        return path

    def raw_json(relative):
        return json.loads(inside(relative).read_text(encoding='utf-8'))

    manifest = raw_json('manifest.json')
    require(manifest.get('schema') == 'cyd-vorbis-xtensa-audit-archive-v1',
            'manifest_schema', 'Unknown archive schema')
    table = manifest['files']
    actual = {path.relative_to(root).as_posix() for path in root.rglob('*') if path.is_file()}
    require(actual == set(table) | {'manifest.json'}, 'manifest_file_set',
            'Missing or additional archive files')
    for name, info in table.items():
        data = inside(name).read_bytes()
        require(len(data) == info['bytes'] and digest(data) == info['sha256'],
                'manifest_bytes_or_sha', name)
    require(inside('.gitattributes').read_text(encoding='utf-8') == '* -text\n',
            'text_attributes', 'Every archive payload must remain byte exact')
    require(digest(inside('raw/report.json').read_bytes()) == RAW_REPORT_SHA256,
            'raw_report_identity', 'Accepted raw report changed')
    report = raw_json('raw/report.json')
    capture = raw_json('raw/capture.json')
    supplement = raw_json('raw/supplement.json')
    mapping = raw_json('path-map.json')
    omitted = raw_json('omitted-binaries.json')['artifacts']
    payloads = mapping['payloads']
    normalized_payloads = {name.replace('\\', '/'): record for name, record in payloads.items()}
    require(len(normalized_payloads) == len(payloads), 'payload_path_alias', 'Ambiguous separator aliases')

    def payload(name):
        return normalized_payloads[name.replace('\\', '/')]

    def mapped(record, expected_sha=None):
        require(record['sha256'] == (expected_sha or record['sha256']),
                'mapping_sha', str(record))
        if record['disposition'] == 'preserved_byte_exact':
            path = inside(record['archive_path'])
            data = path.read_bytes()
            require(digest(data) == record['sha256'] and len(data) == record['bytes'],
                    'mapped_payload_identity', record['archive_path'])
            return path
        require(record['disposition'] == 'omitted_binary', 'mapping_disposition', str(record))
        item = omitted[record['omitted_artifact']]
        require(item['sha256'] == record['sha256'] and item['bytes'] == record['bytes'],
                'omitted_mapping_identity', record['omitted_artifact'])
        return None

    require(set(payloads) == set(report['evidence']['payloads_sha256']) | {'report.json'},
            'raw_payload_set', 'Not every original audit payload is mapped')
    for original, expected in report['evidence']['payloads_sha256'].items():
        mapped(payloads[original], expected)
    mapped(payloads['report.json'], RAW_REPORT_SHA256)
    inputs = report['evidence']['all_input_sha256']
    require(len(inputs) == 61 and set(mapping['inputs']) == set(inputs),
            'input_mapping_set', 'Expected all61 historical inputs')
    for original, expected in inputs.items():
        mapped(mapping['inputs'][original], expected)
    for original, snapshot in (capture['snapshot_map'] | supplement['snapshot_map']).items():
        require(payload(snapshot)['sha256'] == inputs[original],
                'snapshot_identity', original)
    for name, info in table.items():
        if name.startswith('raw/snapshots/'):
            require(pathlib.PurePosixPath(name).name == info['sha256'],
                    'snapshot_filename', name)
        head = inside(name).read_bytes()[:8]
        require(not (head.startswith(b'!<arch>\n') or head.startswith(b'\x7fELF') or head.startswith(b'MZ')),
                'unexpected_binary_payload', name)

    archives = report['installed_identity']['archives']
    require(len(archives) == 4, 'archive_count', 'Expected four architecture-specific archives')
    kinds = {kind: [item for item in omitted.values() if item['kind'] == kind]
             for kind in ('vendor_archive', 'extracted_elf_member', 'tool_executable')}
    require([len(kinds[kind]) for kind in kinds] == [4, 38, 4] and len(omitted) == 46,
            'omitted_binary_counts', 'Expected4archives/38members/4tools')
    for name, info in archives.items():
        match = [item for item in kinds['vendor_archive'] if item['original_path'] == info['path']]
        require(len(match) == 1 and match[0]['sha256'] == info['sha256'] and match[0]['bytes'] == info['bytes'],
                'archive_identity', name)
    require(len(capture['members']) == 38 and not any(m['dwarf_present'] for m in capture['members'].values()),
            'selected_member_scope', 'No selected DWARF/full-layout proof exists')
    for name, member in capture['members'].items():
        record = payload(member['payload'])
        require(record['disposition'] == 'omitted_binary', 'member_bytes_present', name)
        item = omitted[record['omitted_artifact']]
        board = 'esp32c3' if name.startswith('esp32c3-') else 'esp32'
        require(item['sha256'] == member['sha256'] and item['bytes'] == member['bytes'] and
                item['archive_index'] == member['archive_index'] and item['member'] == member['member'] and
                item['elf_machine'] == member['elf_machine'] == (243 if board == 'esp32c3' else 94) and
                item['archive_sha256'] == archives[board + '/' + member['archive']]['sha256'],
                'member_identity', name)
    require({i['original_path']: i['sha256'] for i in kinds['tool_executable']} == capture['tool_hash_only'],
            'tool_identity', 'All four original native tools must be hash-only')

    require(len(capture['commands']) == 80, 'command_count', 'Expected80capturednativecommands')
    for command in capture['commands']:
        require(command['exit_status'] == 0, 'command_exit', command['label'])
        require(command['argv'][0] in capture['tool_hash_only'], 'command_tool', command['label'])
        path = mapped(payload(command['payload']), command['sha256'])
        require(path is not None, 'command_payload_omitted', command['label'])
    excerpts = raw_json('raw/excerpt-map.json')
    require(len(excerpts) == 72, 'excerpt_count', 'Expected72boundfunctions')
    for name, entry in excerpts.items():
        original = mapped(payload(entry['original'])).read_text(encoding='utf-8').splitlines()
        excerpt = mapped(payload(entry['payload']), entry['sha256']).read_text(encoding='utf-8')
        expected = '\n'.join([entry['original'] + ':' + str(entry['first_line']),
                              *original[entry['first_line'] - 1:entry['last_line']]]) + '\n'
        require(excerpt == expected, 'excerpt_line_binding', name)

    findings = report['confirmed_binary_flow_findings']
    expected = {
        'V1': ('confirmed_binary_control_flow_defect', {'0xf7', '0xff', '0x109', '0x10c', '0x12f'}),
        'V2': ('confirmed_binary_control_flow_defect', {'0xd', '0x17', '0x36', '0x52'}),
        'V3': ('confirmed_binary_control_flow_defect', {'0x38', '0x3d', '0x42', '0x47'}),
        'V4': ('confirmed_binary_call_order_with_runtime_effect_to_qualify', {'0xab', '0xd9', '0xdd', '0xdf', '0xe9'}),
        'V5': ('confirmed_binary_control_flow_defect', {'0xc0', '0xd9', '0xde', '0x100', '0x102', '0x104', '0x21c', '0x226'}),
        'V6': ('confirmed_binary_error_propagation_defect', {'0x21', '0x8a', '0x8f', '0xba', '0xbf'}),
    }
    require(len(findings) == 6 and {finding['id'] for finding in findings} == set(expected),
            'finding_set', 'Expected six bounded binary findings')
    instruction_count = 0
    for finding in findings:
        classification, selected_offsets = expected[finding['id']]
        require(finding['classification'] == classification, 'finding_classification', finding['id'])
        require({i['section_offset'] for i in finding['evidence'][0]['instructions']} == selected_offsets,
                'selected_offsets', finding['id'])
        for evidence in finding['evidence']:
            path = mapped(mapping['absolute_files'][evidence['disassembly']], evidence['disassembly_sha256'])
            lines = path.read_text(encoding='utf-8').splitlines()
            require(evidence['elf_machine'] == 94 and evidence['architecture'] == 'Xtensa ESP32',
                    'finding_target_machine', finding['id'])
            member = [m for label, m in capture['members'].items() if label.startswith('esp32-') and m['member'] == evidence['member']]
            require(len(member) == 1 and member[0]['sha256'] == evidence['member_sha256'] and
                    archives['esp32/' + member[0]['archive']]['sha256'] == evidence['archive_sha256'],
                    'finding_binary_binding', finding['id'])
            for instruction in evidence['instructions']:
                line = instruction['line']
                require(0 < line <= len(lines) and lines[line - 1].strip() == instruction['instruction'],
                        'finding_instruction_line', finding['id'])
                require(re.match(r'^' + instruction['section_offset'][2:] + r':\s', instruction['instruction']),
                        'finding_instruction_offset', finding['id'])
                section = [l for l in lines[:line] if l.startswith('Disassembly of section ')][-1]
                require(section == 'Disassembly of section .text.' + evidence['symbol_or_section'] + ':',
                        'finding_instruction_section', finding['id'])
                instruction_count += 1
    # Resolve every original absolute Markdown link without rewriting the raw report.
    raw_links = re.findall(r'\[[^\]]+\]\(([^\n)]+)\)', inside('raw/report.json').read_text(encoding='utf-8'))
    # JSON serializes ordinary forward-slash Markdown links without additional escaping.
    local_links = {link for link in raw_links if re.match(r'^[A-Za-z]:/', link)}
    require(local_links == set(mapping['markdown_line_links']), 'markdown_link_set', 'Every absolute link must map')
    for original, entry in mapping['markdown_line_links'].items():
        path = mapped(entry)
        require(path is not None and 0 < entry['line'] <= len(path.read_text(encoding='utf-8').splitlines()),
                'markdown_line_binding', original)
    status = report['private_layout_observations_not_full_abi_proof']['status']
    require('Partial positive corroboration' in status and 'not' in status,
            'partial_abi_status', 'Audit must not claim full private ABI qualification')
    gates = report['required_gates_all_unrun_here']
    require(len(gates) == 8 and [gate['gate'].split()[0] for gate in gates] == ['G' + str(i) for i in range(1, 9)],
            'unrun_gates', 'Preserve G1-G8 target qualification gates')
    require(report['status'] == 'read_only_source_and_binary_audit_complete_implementation_and_target_qualification_not_run' and
            report['stage'] == 14 and 'AAC private owner-view is wholly excluded' in report['scope']['excluded'],
            'audit_scope_status', 'Implementation/target qualification pending and AAC excluded')
    require(manifest['qualification_status'] == 'audit_complete_implementation_abi_target_golden_oom_conformance_pending' and
            manifest['no_speed_or_ram_claims'] is True, 'archive_scope_status', 'Archive must preserve pending status')
    return {'passed': True, 'files_verified': len(table), 'historical_inputs': len(inputs),
            'omitted_binary_artifacts': len(omitted), 'captured_commands': len(capture['commands']),
            'bound_excerpts': len(excerpts), 'findings': len(findings), 'selected_instructions': instruction_count,
            'mapped_line_links': len(local_links), 'raw_report_sha256': RAW_REPORT_SHA256,
            'manifest_sha256': digest(inside('manifest.json').read_bytes()),
            'qualification': manifest['qualification_status'], 'builds_or_decoder_runs': 0}


if __name__ == '__main__':
    try:
        require(len(sys.argv) <= 2, 'arguments', 'Usage: verify.py [archive-directory]')
        archive = pathlib.Path(sys.argv[1]) if len(sys.argv) == 2 else pathlib.Path(__file__).resolve().parent
        result = verify(archive)
    except VerificationError as error:
        print(json.dumps({'passed': False, 'error': error.code, 'detail': error.detail}, indent=2))
        sys.exit(1)
    except Exception as error:
        print(json.dumps({'passed': False, 'error': 'invalid_archive', 'detail': str(error)}, indent=2))
        sys.exit(1)
    print(json.dumps(result, indent=2))
