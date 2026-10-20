"""Offline integrity and selected-entry verification; reads only this archive.

No SDK, Git, network, firmware execution or external tool is required. Original
binary identities remain omissions; metadata does not replace physical tests.
"""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parent
HEAD = '1190aebce400375c382a5ad54211e2400f98161d'
PREFIX = 'esp32-cyd2usb-native-early-mpi-'
MPI = 'YORADIO_TLS_EARLY_MPI_LOCK'
PRIOR_MARKER = 'd0b8632d82f03fae323e0ed631700261c7d7c34488ff9bdae4d1701d5ba00ab7'
BACKEND_MARKER = '3886135a74d1ea51a34744a443288e31cda82f4bf55cdc2535de41891ff66b0b'
PRIOR_REPORT = '7c2007b1a33a3dfedde6be0ee13e09b463403d6ffdd9d6506fbe1edbbb29a1f4'
SPECS = {'pdm': ('pdm', False, True), 'disabled-pdm': ('pdm', False, False),
         'continuous': ('continuous', False, True), 'legacy': ('legacy', False, True),
         'custom-flac-pdm': ('pdm', True, True), 'custom-flac-continuous': ('continuous', True, True),
         'custom-flac-legacy': ('legacy', True, True)}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(name):
    return json.loads((ROOT / name).read_bytes())


def exact_text_relation(blob, working):
    def style(raw):
        raw.decode('utf-8')
        require(b'\0' not in raw and b'\r' not in raw.replace(b'\r\n', b''), 'Canonical text NUL/lone CR')
        if b'\r\n' in raw:
            require(raw.count(b'\n') == raw.count(b'\r\n'), 'Canonical mixed LF/CRLF')
            return 'CRLF'
        return 'LF'
    blob_style, working_style = style(blob), style(working)
    normalized = blob.replace(b'\r\n', b'\n')
    reconstructed = normalized.replace(b'\n', b'\r\n') if working_style == 'CRLF' else normalized
    require(reconstructed == working, 'Canonical change beyond uniform newline conversion')
    return {'relationship': 'byte-equal' if blob == working else blob_style + '-blob-to-' + working_style + '-working',
            'git_blob_line_endings': blob_style, 'working_line_endings': working_style}


def call_trace(text, words, syms):
    registers, calls = {}, []
    for line in text.splitlines():
        match = re.match(r'^\s*([0-9a-f]+):\s+[0-9a-f]+\s+(\S+)\s*(.*)$', line)
        if not match:
            continue
        pc, opcode, operands = match.groups()
        if opcode == 'l32r':
            operand = re.match(r'(a\d+),\s*([0-9a-f]+)', operands)
            if operand:
                register, literal = operand.groups()
                value = words[str(int(literal, 16))]
                require(struct.unpack('<I', bytes.fromhex(value['raw_hex']))[0] == value['value'], 'Actual ELF data word encoding')
                registers[register] = (value['value'], int(literal, 16))
        elif re.fullmatch(r'call(?:0|4|8|12)', opcode):
            target = int(re.match(r'([0-9a-f]+)', operands)[1], 16)
            calls.append({'pc': int(pc, 16), 'target': target, 'kind': 'direct',
                          'symbols': [name for name, value in syms.items() if value['address'] == target]})
            registers.clear()
        elif re.fullmatch(r'callx(?:0|4|8|12)', opcode):
            target, literal = registers.get(operands.split(',')[0].strip(), (None, None))
            calls.append({'pc': int(pc, 16), 'target': target, 'kind': 'indirect', 'literal': literal,
                          'symbols': [name for name, value in syms.items() if value['address'] == target]})
            registers.clear()
        else:
            registers.pop(operands.split(',')[0].strip(), None)
    return calls


def main():
    manifest = read_json('manifest.json')
    expected = {row['path']: row for row in manifest['files']}
    actual = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob('*') if path.is_file() and path != ROOT / 'manifest.json'}
    require(len(expected) == len(manifest['files']) and set(expected) == actual, 'Complete unique manifest file set')
    for name, row in expected.items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), 'Manifest path escapes archive')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Manifest identity: ' + name)
    require((ROOT / '.gitattributes').read_bytes() == b'* -text\n** -text\n', 'Archive byte-preserving attributes')
    mapping = read_json('path-map.json')['entries']
    by_id = {row['id']: row for row in mapping}
    require(len(by_id) == len(mapping), 'Unique path mapping IDs')
    decoded = {}
    for row in mapping:
        require(re.fullmatch('[0-9a-f]{64}', row['sha256']) and type(row['bytes']) is int and row['bytes'] >= 0 and row['roles'] and row['observed_from'], 'Mapped identity/provenance')
        if row['disposition'] == 'omitted':
            require(row['reason'] and 'stored_path' not in row, 'Explicit omission')
            continue
        require(row['disposition'] == 'stored' and row['stored_path'] in expected, 'Stored payload in manifest')
        stored = (ROOT / row['stored_path']).read_bytes()
        require(len(stored) == row['stored_bytes'] and sha(stored) == row['stored_sha256'], 'Encoded identity')
        require(row['encoding'] in ('raw', 'gzip'), 'Known storage encoding')
        raw = gzip.decompress(stored) if row['encoding'] == 'gzip' else stored
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Decoded original bytes')
        require(not raw.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')), 'Executable/archive must be omitted')
        require(Path(row['original_path']).suffix.lower() not in ('.bin', '.elf', '.obj', '.o', '.a', '.exe', '.dll', '.pyc', '.zip'), 'Binary extension must be omitted')
        decoded[row['id']] = raw

    def document(number):
        require(number in decoded, 'JSON evidence was omitted')
        return json.loads(decoded[number])

    def mapped_text(path):
        normalized = path.replace('\\', '/')
        values = [row for row in mapping if row['original_path'].replace('\\', '/') == normalized]
        require(len(values) == 1 and values[0]['id'] in decoded, 'Unique mapped text input: ' + normalized)
        return decoded[values[0]['id']].decode(errors='replace')

    for binding in read_json('bindings.json')['bindings']:
        value = document(binding['container_id'])
        for token in binding['hash_tokens']:
            value = value[token]
        require(value == by_id[binding['target_id']]['sha256'], 'Original report/marker hash binding')
    index = read_json('index.json')
    failed = document(index['historical_failed_lfs_prepare_id'])
    require(failed['passed'] is False and failed['build_or_export_executed'] is False and failed['raw_stderr_file_retained'] is False and 'Raw file differs from Git HEAD:' in failed['error'], 'Honest historical LFS prepare failure/no raw stderr')
    prior = document(index['primary_report_ids']['prior'])
    backends = document(index['primary_report_ids']['backends'])
    require(by_id[index['primary_report_ids']['prior']]['sha256'] == PRIOR_REPORT, 'Exact original prior report')
    require(by_id[index['primary_report_ids']['backends']]['sha256'] == index['backend_qualification_sha256'], 'Exact root-authorized backend report')
    require(index['prior_marker_sha256'] == PRIOR_MARKER and index['backend_marker_sha256'] == BACKEND_MARKER, 'Exact immutable marker pair')
    require(index['status'] == {'seven_linked_applications_qualified': True, 'default_enabled': False, 'physical_qualified': False, 'radio_pre_app_mutex_observed': False, 'benefit_measured': False}, 'Exact qualification limits')
    snapshot = index['complete_source_snapshot']
    require(snapshot['commit'] == index['source_commit'] == HEAD and snapshot['dirty'] is False and snapshot['source_dirty'] is False and snapshot['untracked'] == [], 'Complete clean committed source snapshot')
    for name, row in index['canonical_sources'].items():
        blob, working = decoded[row['git_head_blob_id']], decoded[row['working_id']]
        relation = exact_text_relation(blob, working)
        require(all(row[key] == value for key, value in relation.items()), 'Exact canonical dual representation: ' + name)
        require(hashlib.sha1(b'blob ' + str(len(blob)).encode() + b'\0' + blob).hexdigest() == row['git_blob_oid'], 'Raw HEAD Git blob object identity')
    require(all(value['passed'] is True and value['all_bound_inputs_current'] is True and value['head_after'] == value['source_commit'] == HEAD and value['physical_qualification'] is False for value in (prior, backends)), 'Both authoritative terminal qualifications')
    require(len(prior['images']) == 2 and len(backends['images']) == 5 and len(backends['full_seven_matrix']) == 7 and backends['all_backend_qualification'] is True, 'Exact two+five full matrix')
    require(backends['previous_pdm_qualification']['qualification_sha256'] == PRIOR_REPORT, 'Full matrix binds exact prior report')
    profiles = index['profiles']
    require(len(profiles) == 7 and len({row['variant'] for row in profiles}) == 7 and {row['variant'] for row in profiles} == {PREFIX + name for name in SPECS}, 'Seven exact unique profiles')
    facts = read_json('elf-metadata.json')
    warnings = read_json('warnings.json')
    for profile in profiles:
        variant = profile['variant']
        backend, custom, enabled = SPECS[variant.removeprefix(PREFIX)]
        require((profile['backend'], profile['custom_flac'], profile['enabled']) == (backend, custom, enabled), 'Backend/custom/enabled identity')
        report = document(profile['qualification_id'])
        image = report['images'][profile['image_index']]
        require(image['variant'] == variant and image['enabled'] is enabled and image['elf_machine'] == 94, 'Linked image identity')
        marker, receipt = document(profile['marker_id']), document(profile['receipt_id'])
        require(marker['source_snapshot'] == snapshot and marker['source_commit'] == HEAD, 'Per-campaign source identity')
        marker_sha = PRIOR_MARKER if profile['qualification_id'] == index['primary_report_ids']['prior'] else BACKEND_MARKER
        require(by_id[profile['marker_id']]['sha256'] == marker_sha, 'Per-campaign marker SHA')
        baseline_maps = marker.get('baselines') or {'pdm': {'raw_sha256': marker['baseline_raw_sha256'], 'commit_bindings': marker['baseline_commit_bindings']}}
        for baseline_record in baseline_maps.values():
            for filename in ('app.bin', 'partition-table.bin'):
                binding = baseline_record['commit_bindings'][filename]
                pointer = binding['git_pointer_ascii'].encode('ascii')
                parsed = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize (0|[1-9][0-9]*)\n', pointer)
                require(parsed is not None and parsed[1].decode() == binding['oid'] == baseline_record['raw_sha256'][filename] and int(parsed[2]) == binding['bytes'], 'Exact manifest-bound LFS pointer')
                require(sha(pointer) == binding['git_pointer_sha256'] and any(raw == pointer for raw in decoded.values()), 'Raw LFS pointer retained')
                objects = [row for row in mapping if row['original_path'] == binding['local_object'] and row['sha256'] == binding['local_object_sha256']]
                require(len(objects) == 1 and objects[0]['disposition'] == 'omitted' and objects[0]['bytes'] == binding['bytes'] and binding['local_object_sha256'] == binding['oid'], 'Local LFS binary identity omitted')
        require(receipt['source_commit'] == HEAD and receipt['source_content_sha256'] == snapshot['content_sha256'] and receipt['build_check'] == 'PASS' and receipt['physical_tested'] is False, 'Production receipt status')
        require(receipt['source_dirty'] is False and receipt['source_git_dirty'] is False and receipt['source_git_dirty_after_build'] is False and not receipt['source_untracked'], 'Production receipt clean source')
        require(receipt['variant'] == variant and receipt['backend'] == backend and receipt['target'] == 'esp32', 'Production receipt profile')
        require(len(receipt['evidence']) == 4 and {row['path']: row['sha256'] for row in receipt['evidence']} == marker['evidence'], 'Four unchanged original evidence files')
        before, after = document(profile['baseline_config_id']), document(profile['config_id'])
        delta = {key: {'previous': before.get(key), 'current': after.get(key)} for key in sorted(set(before) | set(after)) if key not in before or key not in after or type(before[key]) is not type(after[key]) or before[key] != after[key]}
        require(type(after.get(MPI)) is bool and after[MPI] is enabled and delta == {MPI: {'previous': None, 'current': enabled}}, 'Exact single absent-to-bool configuration delta')
        require('YORADIO_VORBIS_REPAIR' not in after and after['YORADIO_TLS_INPUT_RECLAIM'] is True and after['YORADIO_HTTP_REQUEST_BUFFER_RELEASE'] is True and after['FREERTOS_UNICORE'] is False, 'Preserved reclaim/HTTP/dual-core/unwired bridge')
        require(after['YORADIO_FLAC_DECODER_CUSTOM'] is custom and after['YORADIO_FLAC_DECODER_ESPRESSIF'] is (not custom), 'Preserved codec selector')
        keys = {'pdm': 'YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 'continuous': 'YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 'legacy': 'YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC'}
        require(after[keys[backend]] is True and all(after[value] is False for key, value in keys.items() if key != backend), 'Preserved backend selector')
        initial = decoded[profile['baseline_text_id']]
        suffix = b'CONFIG_YORADIO_TLS_EARLY_MPI_LOCK=y\n' if enabled else b'# CONFIG_YORADIO_TLS_EARLY_MPI_LOCK is not set\n'
        seed = initial + (b'' if initial.endswith(b'\n') else b'\n') + suffix
        require(decoded[profile['initial_seed_id']] == seed and sha(seed) == receipt['sdkconfig_seed']['source_sha256'], 'Exact original immutable initial seed')
        require(min(slot['bytes'] for slot in receipt['ota_slots']) == 0x1b0000 and all(image['app_bytes'] <= slot['bytes'] for slot in receipt['ota_slots']), 'OTA slot capacity')
        require(by_id[profile['elf_id']]['disposition'] == 'omitted' and by_id[profile['elf_id']]['sha256'] == image['elf_sha256'], 'Original ELF omission identity')
        metadata = facts[variant]
        require(metadata['machine'] == 94 and metadata['elf_class'] == metadata['data_encoding'] == 1 and metadata['sha256'] == image['elf_sha256'] and metadata['bytes'] == by_id[profile['elf_id']]['bytes'], 'Derived ELF metadata identity')
        logs = {name: decoded[number].decode(errors='replace') for name, number in profile['log_ids'].items()}
        syms = {}
        for line in logs['nm.log'].splitlines():
            fields = line.split()
            if len(fields) == 4:
                syms[fields[3]] = {'address': int(fields[0], 16), 'bytes': int(fields[1], 16), 'type': fields[2]}
        require(('native_tls_early_mpi_prepare' in syms) is enabled and '__wrap_esp_mbedtls_mem_free' not in syms, 'On/off MPI and ordinary free ownership')
        require(('custom_flac_decoder_feed' in syms) is custom and ('esp_flac_dec_register' in syms) is (not custom), 'Actual linked codec identity')
        calls = call_trace(logs['app-main.log'], metadata['data_words'], syms)
        require(calls == image['actual_app_main_calls'] and calls, 'Recomputed actual app_main call trace')
        if enabled:
            require(calls[0]['target'] == syms['native_tls_early_mpi_prepare']['address'], 'MPI before first log/health/state/NVS call')
            body = call_trace(logs['mpi-body.log'], metadata['data_words'], syms)
            require([row['target'] for row in body] == [syms[name]['address'] for name in ('esp_crypto_mpi_lock_acquire', 'esp_crypto_mpi_lock_release')], 'Exactly one ordinary public acquire/release pair')
        for name, target in (('mbedtls_calloc_func', '__wrap_esp_mbedtls_mem_calloc'), ('mbedtls_free_func', 'esp_mbedtls_mem_free')):
            pointer = metadata['data_words'][str(syms[name]['address'])]
            require(syms[name]['bytes'] == 4 and pointer['value'] == syms[target]['address'] and image['sdk_allocator_pointer_routes'][name]['value'] == pointer['value'], 'Actual ordinary allocator/free function pointer pairing')
        require(len(image['mpi_compile_rows']) == int(enabled) and len(image['reclaim_compile_rows']) == 1 and 'xtensa-esp32-elf-gcc' in image['http_overlay_compile_row']['command'], 'Canonical whole module actual-target compile counts')
        ninja = mapped_text(profile['build_directory'] + '/build.ninja')
        require('--wrap=esp_mbedtls_mem_calloc' in ninja and '--undefined=__wrap_esp_mbedtls_mem_calloc' in ninja and '--wrap=esp_mbedtls_mem_free' not in ninja and '--wrap=esp_vorbis_dec_open' not in ninja, 'Actual preserved allocator ownership and unconnected Vorbis link graph')
        if backend == 'pdm':
            require(all(0x40080000 <= syms[name]['address'] < 0x400a0000 for name in ('pdm_completion_queue_drop', 'native_output_metrics_queue_drop')), 'PDM-only callback IRAM gate')
        for name, size in (('s_output_metrics', 64), ('s_output_metrics_lock', 8)):
            require(syms[name]['bytes'] == size and 0x3ff80000 <= syms[name]['address'] < 0x40000000, 'Metrics DRAM layout')
        inventory = warnings[variant]
        require(all(row['category'] in ('component-include-dependency', 'object-path-length') and row['block'].startswith('CMake Warning') for row in inventory['cmake']), 'Explicit separate known CMake warnings')
        compiler = inventory['compiler']
        names = [re.search(r"periph_rtc_apll_(freq_set|acquire|release)' is deprecated", row['message']) for row in compiler]
        require(not compiler or backend == 'legacy' and len(compiler) == 3 and all(names) and {row[1] for row in names} == {'freq_set', 'acquire', 'release'}, 'Exact known unique legacy compiler warnings')
    require(read_json('current-verification.json')['all_selected_read_inputs_unchanged_after'] is True, 'Archival stable input check')
    require(read_json('SDK.json')['all_seven'] is True and read_json('SDK.json')['physical_tested'] is False, 'SDK summary scope')
    print(json.dumps({'passed': True, 'manifest_files': len(expected), 'mapped_versions': len(mapping), 'json_hash_bindings': len(read_json('bindings.json')['bindings']), 'seven_linked_apps': 7, 'offline_only': True}, indent=2))


if __name__ == '__main__':
    main()
