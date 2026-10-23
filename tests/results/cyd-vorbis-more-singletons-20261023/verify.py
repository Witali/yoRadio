"""Read-only offline singleton8 plus preferred-zero evidence verifier; never run a codec, process or SDK."""
import argparse
from collections import Counter
import copy
import gzip
import importlib.util
import json
import ntpath
from pathlib import Path, PureWindowsPath
import re
import struct
import sys
from dependency import Dependency, MANIFEST_SHA, need, norm, obj, rel, sha

sys.dont_write_bytecode = True
PREFIX = 'CYD_VORBIS_CHECKED_CORPUS_'
COMMANDS = ['sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after']
METRICS = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
MATERIALIZE_HELPERS = 'c2f96df5d68ed5bbacb9e14edb34442c46f062a01ae2d93de3e331f67b4ff58f'
RAW_HELPERS = '9af2a14101e5f699959603024925e0cc7e27dd2c1a27cb67fd8e6c3c050363e3'
ZERO_HELPERS = '0dd2751666a52cb5b8b2430051d2cb6f34a1b90083768f97b40ce1a201ed7a50'
REFERENCE_HELPERS = '53b15ce726c9ebe95610bd61b2649713dba0c862e721e406913f045eb78a4b0c'
ARCHIVE_PROTOCOL = 'bbea6f80706495630a31fd7b9393bbfe2567ddfda05a1a19e632d1194fea068a'


def load_module(name, path, expected):
    need(sha(path.read_bytes()) == expected, 'Unreviewed archived module')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(bundle, repository):
    bundle, repository = bundle.resolve(), repository.resolve()
    manifest = obj((bundle / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'cyd-more-singletons-checkpoint-v1' and
         set(manifest['plan']['roles']) == {'capture8', 'numeric8', 'host-original8', 'host-zero8'}, 'Focused singleton archive schema/roles')
    need(manifest['dependency_archive'] == dict(path='tests/results/cyd-vorbis-map2-20261020',
        manifest_sha256=MANIFEST_SHA, required=True, standalone=False, scope='exact-shared-entries-only-no-prior-campaign-replay'), 'Explicit unchanged CYD dependency required')
    need(manifest['intended_destination'] == 'tests/results/cyd-vorbis-more-singletons-20261023' and
         all(manifest[k] is False for k in ('full_G6_qualified', 'physical_device', 'production_firmware')), 'Finite unchanged archive scope')
    dep = Dependency(repository)
    # The pinned committed dependency supplies exact shared bytes only; no prior campaigns are replayed.
    files, raw, stored, physical = manifest['files'], {}, {'manifest.json'}, {}
    for key, row in files.items():
        rel(key)
        need(type(row['raw_bytes']) is int and row['raw_bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', row['raw_sha256']), 'Raw identity syntax')
        if 'dependency_key' in row:
            need(row['stored'] is None and row['dependency_key'] == key, 'Exact original-path dependency reuse only')
            data = dep.read(key)
        elif row['stored'] is None:
            need(row.get('omitted'), 'Undeclared local omission')
            if 'actual_elf_header64_hex' in row:
                header = bytes.fromhex(row['actual_elf_header64_hex'])
                need(len(header) == 64 and header[:5] == b'\x7fELF\x01' and struct.unpack_from('<H', header, 18)[0] == 94,
                     'Actual 64-byte Xtensa ELF32 header required')
            continue
        else:
            path = (bundle / rel(row['stored'])).resolve()
            need(path.is_relative_to(bundle) and row['stored'] not in stored, 'Stored path boundary/uniqueness')
            stored.add(row['stored'])
            blob = path.read_bytes()
            need(len(blob) == row['stored_bytes'] and sha(blob) == row['stored_sha256'] and row['encoding'] in ('raw', 'gzip'), 'Stored identity/encoding')
            data = gzip.decompress(blob) if row['encoding'] == 'gzip' else blob
            physical[norm(path)] = key
            if key.endswith(('.py', '.h')):
                need(row['encoding'] == 'raw', 'Sources must remain plain readable bytes')
        need(len(data) == row['raw_bytes'] and sha(data) == row['raw_sha256'], 'Raw/dependency content identity')
        raw[key] = data
    for name, row in manifest['generated'].items():
        path = (bundle / rel(name)).resolve()
        need(path.is_relative_to(bundle) and name not in stored, 'Generated path boundary/uniqueness')
        stored.add(name)
        need(len(path.read_bytes()) == row['bytes'] and sha(path.read_bytes()) == row['sha256'], 'Generated identity')
    need({path.relative_to(bundle).as_posix() for path in bundle.rglob('*') if path.is_file()} == stored, 'Exact stored inventory')
    need((bundle / '.gitattributes').read_bytes() == b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n', 'Raw Git byte policy')
    base = manifest['repository'].rstrip('/')
    def address(value, role=None):
        name = norm(ntpath.normpath(str(value)))
        if name in physical:
            return physical[name]
        if role is not None and name in manifest['aliases'].get(role, {}):
            return manifest['aliases'][role][name]
        if name.startswith(base + '/'):
            key = rel(name[len(base) + 1:])
            if key in files:
                return key
        matches = {aliases[name] for aliases in manifest['aliases'].values() if name in aliases}
        need(matches and all(key in raw for key in matches) and len({sha(raw[key]) for key in matches}) == 1,
             'No unbound, ambiguous or current-file fallback: ' + name)
        return sorted(matches)[0]
    def data(role, path='report.json'):
        return raw[manifest['roles'][role]['root'] + '/' + rel(path)]
    def record(role, path='report.json'):
        return obj(data(role, path))
    def frozen(role, path, expected, size=None):
        key = address(path, role)
        value = raw[key]
        need(sha(value) == expected and (size is None or len(value) == size), 'Archived original/snapshot binding')
        return value
    def receipt(value, code, role=None):
        actual = value.get('exit_code', value.get('returncode'))
        need(type(actual) is int and actual == code and
             (value.get('schema') == 'direct-exec-tool-terminal-v1' or value.get('status') == 'TERMINAL'), 'Actual terminal status/exit')
        if value.get('status') == 'TERMINAL':
            need(type(value.get('owned_pid')) is int and value['owned_pid'] > 0 and value.get('timed_out', False) is False and
                 value.get('interrupted', False) is False, 'Actual owned receipt without timeout/interruption')
        for path, row in value.get('logs', {}).items():
            frozen(role, path, row['sha256'], row['bytes'])
        if 'executable_sha256' in value:
            need(manifest['external_omitted'][norm(value['argv'][0])]['raw_sha256'] == value['executable_sha256'], 'Actual omitted executable binding')
    reports = {role: record(role) for role in manifest['roles']}
    for role in ('capture8', 'numeric8', 'host-original8', 'host-zero8'):
        report, selected = reports[role], manifest['plan']['roles'][role]
        need(sha(data(role)) == selected['report_sha256'], 'Root-reviewed actual report identity')
        need(sha(raw[manifest['roles'][role]['terminal']]) == selected['terminal_sha256'], 'Root-reviewed actual outer receipt identity')
        receipt(obj(raw[manifest['roles'][role]['terminal']]), selected['expected_outer_exit'], role)
        for origin, row in report.get('inputs', {}).items():
            path = origin if 'snapshot' in row else row['path']
            name = norm(path)
            external = manifest.get('external_numeric_aliases', {}).get(role, {}).get(name)
            if external is not None:
                omitted = manifest['external_omitted'][external]
                need(role == 'numeric8' and omitted.get('external_numeric_input') is True and
                     omitted['raw_sha256'] == row['sha256'] and omitted['raw_bytes'] == row['bytes'] and
                     PureWindowsPath(external).name in {'ffmpeg.exe', 'python.exe'}, 'Explicit hash-only external numeric tool metadata')
                continue
            frozen(role, path, row['sha256'], row.get('bytes'))
        for path, digest in report.get('tools', {}).items():
            need(manifest['external_omitted'][norm(path)]['raw_sha256'] == digest, 'Tool/archive hash omission metadata')
    def source_module(name, key, expected=None):
        need(key in raw and files[key].get('encoding') == 'raw', 'Retained plain module source required')
        return load_module(name, bundle / files[key]['stored'], expected or sha(raw[key]))
    target = reports['capture8']
    need(target['result'] == 'CHECKED_CORPUS_PCM_CAPTURED' and target['completed'] is True and
         target['target_capture_completed'] is True and target['checked_decode_completed'] is True and
         all(target.get(name) is False for name in ('passed', 'vendor_comparison_available', 'vendor_checked_pcm_equal',
             'independent_reference_compared', 'numeric_reference_qualified', 'format_corpus_qualified', 'full_G6_qualified',
             'physical_device', 'production_radio_integration')), 'Actual full8 capture scope')
    terminal = obj(raw[manifest['roles']['capture8']['terminal']])
    need(terminal['report_sha256'] == sha(data('capture8')) and terminal['entrypoint_sha256'] ==
         'ce603506b72b30807123eed3efd5cf383c9ec563733a9d3beaf7a6333e38a28c' and
         (terminal['session_id'], terminal['terminal_chunk_id'], terminal['exit_code']) == (26677, '5c5e61', 0), 'Actual direct-tool target terminal')
    need([row['name'] for row in target['commands']] == COMMANDS, 'All9 actual target commands')
    for command in target['commands']:
        need(command['state'] == 'complete' and type(command['exit_status']) is int and command['exit_status'] == 0 and
             command['timed_out'] is False and command['interrupted'] is False and type(command['pid']) is int and command['pid'] > 0,
             'Actual owned target command terminals')
        for stream in ('stdout', 'stderr'):
            need(sha(data('capture8', command['name'] + '.' + stream + '.log')) == command[stream + '_sha256'], 'Actual target command log')
    for field in ('build_outputs', 'variant_sources'):
        for path, digest in target.get(field, {}).items():
            need(files[manifest['roles']['capture8']['root'] + '/' + norm(path)]['raw_sha256'] == digest, 'Actual target output/variant identity')
    need(sha(data('capture8', 'sources/project/main/main.c')) == '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065' and
         sha(data('capture8', 'variant/vorbis_repair/setup.c')) == sha(data('capture8', 'sources/candidate/vorbis_repair/setup.c')) ==
         '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c', 'Exact public caller/CYD source')
    context = target['setup_macro_context']
    need(context['row'] in record('capture8', 'build/compile_commands.json'), 'Actual setup compile row')
    need(len(context['generated_inputs']) == 2, 'Actual cflags/specs macro context')
    for path, row in context['generated_inputs'].items():
        need(row['sha256_before'] == row['sha256_after'] == sha(raw[address(path, 'capture8')]), 'Stable actual macro inputs')
    macros = data('capture8', 'setup-macros.stdout.log').decode().replace('\r\n', '\n')
    need(not re.search(r'^#define (LIMIT_TO_64kHz|CONFIG_FREERTOS_UNICORE)\b', macros, re.M) and
         re.search(r'^#define CONFIG_IDF_TARGET_ESP32 1$', macros, re.M) and
         re.search(r'^#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240$', macros, re.M) and
         data('capture8', 'sdk-head.stdout.log').strip() == b'7101770dc6db2667b3c477cc31365dd1acd6db4e' and
         not data('capture8', 'sdk-clean.stdout.log').strip(), 'Actual CYD SDK/Xtensa/SMP profile')
    contract = record('capture8', 'sources/corpus/contract.json')
    need(sha(data('capture8', 'sources/corpus/contract.json')) == '65003d33a6c13634bea414ceaff487a2858e78eae93afc5458edd6da3fecac0c' and
         sha(data('capture8', 'sources/project/main/data.h')) == '93e0e734b0374f42b06bfd9095a4bc4270813266ee1f080b2932313e0a3e98e6', 'Exact full8 contract/header')
    need(sha(data('capture8', 'sources/helpers/protocol.py')) == '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e', 'Exact original runtime protocol source')
    archive_protocol = load_module('offline_explicit_archive_protocol', bundle / 'archive_protocol.py', ARCHIVE_PROTOCOL)
    protocol = archive_protocol.make_validator(lambda path: raw[address(path, 'capture8')])
    need(protocol['load_contract'](contract['manifest_inputs']) == contract, 'Every actual raw/model contract field reconstructed archive-only')
    qemu = target['commands'][6]
    log = (data('capture8', 'qemu.stdout.log') + b'\n' + data('capture8', 'qemu.stderr.log')).decode(errors='replace')
    observed = protocol['validate_log'](log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
        interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == target['observed'] and (observed['cases'], observed['decoded_packets'], observed['pcm'], observed['protocol_lines'], observed['case_mask']) ==
         (8, 112, 225280, 251, 255) and len(captured) == len(target['observed_pcm']) == 8, 'Strict full8 actual protocol')
    for item, row in zip(captured, target['observed_pcm']):
        need(item['pcm'] == data('capture8', row['path']) and item['sha256'] == row['sha256'] and
             (item['case'], item['id'], item['packet_offsets']) == (row['case'], row['id'], row['packet_offsets']), 'Every persisted actual PCM byte/boundary')
    need({manifest['roles']['capture8']['root'] + '/' + norm(row['path']) for row in target['observed_pcm']} ==
         {key for key in raw if key.startswith(manifest['roles']['capture8']['root'] + '/observed-pcm/')}, 'Exact target PCM inventory')

    runtime_root = '.build/cyd-vorbis-more-singletons-runtime-01/'
    materializer = load_module('offline_singletons8_restricted_C_reader', bundle / 'materialize_helpers.py', MATERIALIZE_HELPERS)
    mapping = record('capture8', 'sources/corpus/source-map.json')
    raw_cases = [{kind: raw[address(item['files'][kind]['selected']['path'], 'capture8')]
                  for kind in ('identification', 'setup', 'audio')} for item in mapping['cases']]
    recovered = materializer.recover(data('capture8', 'sources/project/main/data.h').decode('ascii'), contract, raw_cases,
                                    sha(data('capture8', 'sources/corpus/contract.json')))
    saved_materialization = obj(raw[runtime_root + 'materialized01/report.json'])
    need(recovered == saved_materialization['cases'] and saved_materialization['counts'] ==
         dict(cases=8, arrays=40, full_raw_payload_arrays=24, packets=112, expected_pcm_bytes=225280,
              descriptor_capacity=8, case_mask=255) and len(saved_materialization['controls']) == 5 and
         all(row['rejected'] is True for row in saved_materialization['controls']), 'Actual independent40-array/header recovery and controls')

    def generated(key, schema):
        record = obj(raw[key + 'manifest.json'])
        need(record['schema'] == schema and {name[len(key):] for name in raw if name.startswith(key)} ==
             {row['path'] for row in record['files']} | {'manifest.json'}, 'Exact complete generated corpus inventory')
        for row in record['files']:
            value = raw[key + row['path']]
            need(len(value) == row['bytes'] and sha(value) == row['sha256'], 'Generated member raw identity')
        return obj(raw[key + 'matrix.json']), obj(raw[key + 'bitfields.json'])

    original_root = '.build/cyd-vorbis-more-singletons-generated-01/'
    zero_root = '.build/cyd-vorbis-singleton-zero-bit-generated-01/'
    matrix, bitfields = generated(original_root, 'more-singletons-generated-manifest-v1')
    zero_matrix, zero_fields = generated(zero_root, 'singleton-zero-bit-generated-manifest-v1')
    need(sha(raw[original_root + 'manifest.json']) == '3ad3a1f9b466d92b2c701c787bdec42ed708cfa9146a3804dcf3d5cc766aeadf' and
         sha(raw[zero_root + 'manifest.json']) == 'c300a312f36abff95e9219479c7d0edd59b47ce09cf6a6dcd6af25f304e45858', 'Exact actual original/zero generations')
    helper = load_module('raw_helpers', bundle / 'raw_helpers.py', RAW_HELPERS)
    saved_modules = {name: sys.modules.get(name) for name in ('raw_helpers', 'pcm_metrics', 'policy8')}
    sys.modules['raw_helpers'] = helper
    try:
        zero_helper = load_module('zero_helpers', bundle / 'zero_helpers.py', ZERO_HELPERS)
        reference_helper = load_module('reference_helpers', bundle / 'reference_helpers.py', REFERENCE_HELPERS)
        metrics = source_module('pcm_metrics', '.build/cyd-vorbis-more-singletons-numeric-prep-01/pcm_metrics.py', METRICS)
        sys.modules['pcm_metrics'] = metrics
        policy = source_module('policy8', '.build/cyd-vorbis-more-singletons-numeric-prep-01/policy8.py',
            '3eb4e474a3611a69707e4c851f90d1d8ba680b5c3a401faf343d8d5af39b4865')
        sys.modules['policy8'] = policy
        adapter = source_module('offline_singletons8_numeric_helpers', '.build/cyd-vorbis-more-singletons-numeric-prep-01/compare_capture8.py',
            'b4e8ab02c07601d406c5d51ef96e7de4c613a5fb70cf7d01534e52a094f04893')
        need(tuple(c['id'] for c in matrix['cases']) == policy.CASE_IDS and len(matrix['cases']) == 8 and
             matrix['expected_same_decoder_pcm_equal_groups'] == policy.TRIPLES and
             matrix['expected_same_decoder_pcm_different_pairs'] == policy.DIFFERENT_PAIRS, 'Exact declared original8 order/relations')
        witness = obj(raw['.build/cyd-vorbis-more-singletons-witness-01.json'])
        zero_witness = obj(raw['.build/cyd-vorbis-singleton-zero-bit-witness-01.json'])
        need(witness['result'] == 'FINITE_RAW_SINGLETONS_WITNESSED' and (witness['cases'], witness['packets'], witness['Ogg_pages']) == (8, 112, 136) and
             witness['generated_manifest_sha256'] == sha(raw[original_root + 'manifest.json']), 'Actual original independent raw witness')
        need(zero_witness['result'] == 'FINITE_ZERO_BIT_COMPARISON_WITNESSED' and
             (zero_witness['cases'], zero_witness['audio_packets'], zero_witness['zero_tokens'], zero_witness['comparison_tokens'], zero_witness['cleared_original_one_bits']) ==
             (8, 112, 112, 224, 56), 'Actual additive zero raw witness counts')

        def parts(root, case):
            return {kind: raw[root + case[kind]] for kind in ('identification', 'comment', 'setup', 'audio', 'ogg')}

        def packets(case, content):
            offsets = case['offsets']
            need(len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(content['audio']) and
                 all(type(a) is int and a < b for a, b in zip(offsets, offsets[1:])), 'Full actual packet offsets')
            return [content['audio'][a:b] for a, b in zip(offsets, offsets[1:])]

        for index, case in enumerate(matrix['cases']):
            content = parts(original_root, case); audio = packets(case, content)
            for kind, value in content.items():
                need(case['files'][kind] == dict(bytes=len(value), sha256=sha(value)), 'All original raw case member metadata')
            book, book_proof, setup_fields = helper.parse_setup(content['setup'], case['id'])
            helper.compare_field_report(setup_fields, bitfields[case['id']]['setup'])
            helper.compare_field_report(helper.parse_identification(content['identification']), bitfields[case['id']]['identification'])
            helper.compare_field_report(helper.parse_comment(content['comment']), bitfields[case['id']]['comment'])
            proofs, consumption = [], []
            for packet, value in enumerate(audio):
                proof, fields = helper.parse_audio(value, book, packet)
                helper.compare_field_report(fields, bitfields[case['id']]['audio'][packet])
                proofs.append(proof); consumption.append({k: v for k, v in fields.items() if k != 'trace'})
            need(proofs == case['packet_syntax'], 'Every original audio field and exact Fraction/residue0 vector')
            helper.compare_audit(book, case['vector_book'], proofs)
            wire = Counter(bit for proof in proofs for ch in proof['single_entry_wire_bits'] for bit in ch)
            pages = helper.carrier(content['ogg'], [content[k] for k in ('identification', 'comment', 'setup')] + audio,
                [0, 0, 0] + case['packet_granules'], 0x53470001 + index)
            need(witness['reports'][index] == dict(id=case['id'], actual_book=book, original_row_proof=book_proof,
                actual_packet_count=14, actual_used_wire_bit_counts={str(k): v for k, v in sorted(wire.items())},
                packet_consumption=consumption, actual_pages=pages), 'Recomputed complete original witness row')

        zero_helper.validate_matrix_status(zero_matrix)
        expected_zero_ids = [c['id'] for c in matrix['cases'][4:]]
        pairs = [[name, name + '_wire0'] for name in expected_zero_ids]
        need([c['id'] for c in zero_matrix['cases']] == expected_zero_ids + [name + '_wire0' for name in expected_zero_ids] and
             zero_matrix['expected_Xiph_PCM_equal_pairs'] == zero_matrix['expected_same_decoder_pcm_equal_groups'] == pairs,
             'Exact unchanged original4 and additive zero4 order/relations')
        all_edits = {}
        for index, original in enumerate(matrix['cases'][4:]):
            old, new = zero_matrix['cases'][index], zero_matrix['cases'][index + 4]
            need(old == original, 'Every original4 map1 matrix field preserved')
            old_parts, new_parts = parts(zero_root, old), parts(zero_root, new)
            need(old_parts == parts(original_root, original), 'Every original4 raw byte preserved')
            need(all(old_parts[k] == new_parts[k] for k in ('identification', 'comment', 'setup')), 'All additive headers/setup byteequal')
            zero_helper.validate_field_report_keys(zero_fields[new['id']], zero_fields[old['id']])
            need(zero_fields[old['id']] == bitfields[old['id']], 'Original field metadata preserved')
            need({k: zero_fields[new['id']][k] for k in ('identification', 'comment', 'setup')} ==
                 {k: zero_fields[old['id']][k] for k in ('identification', 'comment', 'setup')}, 'Additive header metadata preserved')
            book, book_proof, _ = helper.parse_setup(old_parts['setup'], old['id'])
            old_audio, new_audio = packets(old, old_parts), packets(new, new_parts)
            need(old['offsets'] == new['offsets'], 'Additive full packet offsets unchanged')
            proofs, edits = [], []
            for packet, (a, b) in enumerate(zip(old_audio, new_audio)):
                original_proof, _ = helper.parse_audio(a, book, packet)
                proof, fields, positions = zero_helper.parse_zero_audio(b, book, packet)
                helper.compare_field_report(fields, zero_fields[new['id']]['audio'][packet])
                need(zero_fields[new['id']]['audio'][packet] == zero_helper.zero_field_report(zero_fields[old['id']]['audio'][packet], positions),
                     'Every non-token field metadata unchanged')
                expected = copy.deepcopy(original_proof); expected['single_entry_wire_bits'] = [[0], [0]]
                need(proof == expected, 'Full actual vectors/indices/classwords/consumption unchanged')
                edits.append(dict(packet=packet, original_id=old['id'], changed_bit_offsets=zero_helper.unchanged_except_tokens(a, b, positions), consumed_zero_tokens=2))
                proofs.append(proof)
            expected = copy.deepcopy(old); expected['id'] = new['id']; expected['wire_zero_control_for'] = old['id']
            expected['features'] = ['singleton_wire_bits_all_zero' if f == 'both_singleton_wire_bits' else f for f in expected['features']] + ['preferred_zero_singleton_tokens']
            expected['packet_syntax'] = proofs
            for kind in new_parts:
                expected[kind] = f"cases/{new['id']}/" + ('reference.ogg' if kind == 'ogg' else kind + '.bin')
            expected['files'] = {k: dict(bytes=len(v), sha256=sha(v)) for k, v in new_parts.items()}
            expected['raw_sha256'] = {k: sha(v) for k, v in new_parts.items() if k != 'ogg'}
            need(new == expected, 'Exact only allowed additive metadata delta')
            old_pages = helper.carrier(old_parts['ogg'], [old_parts[k] for k in ('identification', 'comment', 'setup')] + old_audio,
                [0, 0, 0] + old['packet_granules'], 0x53470005 + index)
            new_pages = helper.carrier(new_parts['ogg'], [new_parts[k] for k in ('identification', 'comment', 'setup')] + new_audio,
                [0, 0, 0] + old['packet_granules'], 0x53470005 + index)
            for a, b in zip(old_pages, new_pages):
                start = a['offset']; old_header = bytearray(old_parts['ogg'][start:start + 27 + old_parts['ogg'][start + 26]])
                start2 = b['offset']; new_header = bytearray(new_parts['ogg'][start2:start2 + 27 + new_parts['ogg'][start2 + 26]])
                old_header[22:26] = new_header[22:26] = b'\0' * 4
                need(old_header == new_header and {k: v for k, v in a.items() if k != 'checksum'} ==
                     {k: v for k, v in b.items() if k != 'checksum'}, 'All raw Ogg headers/lacing/fields except necessary CRC unchanged')
            need(zero_witness['reports'][index] == dict(original_id=old['id'], zero_id=new['id'], original_row_proof=book_proof,
                zero_tokens=28, comparison_tokens=56, cleared_one_bits=14, changes=edits, original_pages=old_pages, zero_pages=new_pages,
                actual_spectra_equal=True, actual_PCM_equality_verified=False), 'Recomputed complete zero-pair witness row')
            all_edits[new['id']] = edits
        need(obj(raw[zero_root + 'construction.json'])['changes'] == all_edits and
             zero_witness['actual_spectral_equal_pairs'] == pairs, 'All56 changed bits/224token observations exact')

        def qualified_reference(role, root, source_matrix, profile, qualification_key, expected_sha):
            host = reports[role]; qualified = obj(raw[qualification_key])
            need(sha(raw[qualification_key]) == expected_sha and qualified['profile'] == profile and
                 qualified['result'] == 'XIPH_QUALIFIED_DUAL_NONPASS' and qualified['completed'] is True and
                 qualified['xiph_reference_qualified'] is qualified['reference_corpus_qualified'] is True and
                 qualified['dual_reference_qualified'] is qualified['original_dual_reference_passed'] is False and
                 qualified['native_cause_diagnosed'] is False and qualified['target_executed'] is False and
                 qualified['original_report_sha256'] == sha(data(role)) and qualified['original_failures'] == host['failures'] and
                 (qualified['xiph_cases'], qualified['paired_raw_packets'], qualified['expected_pcm_bytes']) == (8, 112, 225280), 'Actual complete independently qualified Xiph/dual NONPASS scope')
            need(qualified['original_outer_receipt_sha256'] == sha(raw[manifest['roles'][role]['terminal']]) and
                 all(qualified[k] is False for k in ('production_changed', 'standard_conformance_qualified', 'full_G6_qualified', 'physical_device')), 'Actual outer receipt binding and unchanged qualification limits')
            expected_counts = (0, 4, 4) if profile == 'singletons8' else (4, 0, 4)
            need((qualified['native_compared'], qualified['native_lookup2_refusals'], qualified['native_packet_decode_failures']) == expected_counts and
                 host['completed'] is host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False and
                 len(host['commands']) == 16 and len(host['cases']) == len(qualified['cases']) == 8 and
                 len(host['failures']) == (8 if profile == 'singletons8' else 4), 'All16 reference children and distinct native classifications')
            for row in qualified['validated_inputs'].values():
                path = norm(row['path'])
                if path in manifest['external_omitted']:
                    need(manifest['external_omitted'][path]['raw_sha256'] == row['sha256'], 'Qualified omitted executable identity')
                else:
                    frozen(role, row['path'], row['sha256'], row['bytes'])
            commands = {row['name']: row for row in host['commands']}
            need(len(commands) == 16, 'Distinct actual decoder child commands')
            decoded = {}
            for index, (case, reported, accepted) in enumerate(zip(source_matrix['cases'], host['cases'], qualified['cases'])):
                rid = '0-' + case['id']; content = parts(root, case); folder = 'cases/' + rid + '/'
                need(reported['id'] == accepted['id'] == rid and reported['input'] == case and
                     reported['source_matrix_sha256'] == sha(raw[root + 'matrix.json']) and
                     data(role, folder + 'input.ogg') == content['ogg'], 'Actual complete decoder input and ordered metadata')
                native_code = (3199971767 if index < 4 else 4294967295) if profile == 'singletons8' else (4294967295 if index < 4 else 0)
                kind = ('lookup2_setup_refusal' if index < 4 else 'packet_decode_failure_no_PCM') if profile == 'singletons8' else ('packet_decode_failure_no_PCM' if index < 4 else 'accepted')
                outcome = accepted.get('native_failure_kind', accepted.get('native_outcome_kind'))
                need(outcome == kind and accepted['native_actual_returncode'] == native_code and accepted['native_cause_diagnosed'] is False and
                     accepted['native_compared'] is (native_code == 0) and accepted['native_lookup2_refusal'] is (kind == 'lookup2_setup_refusal') and
                     accepted['native_packet_decode_failure'] is (kind == 'packet_decode_failure_no_PCM'), 'Exact per-case native outcomes without cause inference')
                values = {}
                for decoder, code in (('vorbis', native_code), ('libvorbis', 0)):
                    name = folder + 'decode-' + decoder; command = commands[name]
                    child_raw = data(role, command['receipt']); need(sha(child_raw) == command['sha256'], 'Actual child receipt hash')
                    child = obj(child_raw); receipt(child, code, role)
                    argv = child['argv']
                    need(child['runner_sha256'] == '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e' and
                         child['executable_sha256'] == host['tools'][argv[0]] and argv[argv.index('-c:a') + 1] == decoder and
                         '-ar' not in argv and '-ac' not in argv and '-xerror' in argv and argv[argv.index('-err_detect') + 1] == 'explode' and
                         address(argv[argv.index('-i') + 1], role) == manifest['roles'][role]['root'] + '/' + folder + 'input.ogg', 'Actual strict decoder/tool/input command')
                    stdout, stderr = data(role, name + '.stdout.log'), data(role, name + '.stderr.log')
                    if code:
                        need(not stdout and decoder not in reported['decoded'] and len(reported['failures']) == 1 and reported['failures'][0]['stage'] == 'vorbis', 'Original failed native output remains unavailable')
                        if kind == 'lookup2_setup_refusal':
                            need(b'Codebook lookup type not supported.' in stderr and b'Setup header corrupt.' in stderr, 'Actual lookup2 refusal diagnostics')
                        else:
                            need(b'Error submitting packet to decoder: Operation not permitted' in stderr and
                                 b'Error processing packet in decoder: Operation not permitted' in stderr and
                                 b'Codebook lookup type not supported.' not in stderr and data(role, folder + 'vorbis.wav') == b'', 'Actual packet failure/no PCM; no OS/cause inference')
                        continue
                    need(not stderr, 'Strict successful decoder stderr')
                    wav = data(role, folder + decoder + '.wav')
                    pcm, evidence = reference_helper.decoded_pcm(wav, stdout, case['rate'], 2, case['expected_packet_samples'], case['mode_flags'])
                    need(evidence == reported['decoded'][decoder], 'Complete WAV/framemd5/sample/transition evidence')
                    if decoder == 'libvorbis':
                        need(all(accepted[k] == v for k, v in evidence.items()), 'Full independently qualified Xiph evidence')
                    values[decoder] = pcm
                if native_code == 0:
                    error = metrics.compare(values['libvorbis'], values['vorbis'], case['expected_packet_pcm_bytes'])['zero_lag_direct_LR']['max_abs_error']
                    need(error == accepted['cross_reference_max_abs_error'] == reported['cross_reference_max_abs_error'] == 1, 'All4 new-zero native complete PCM comparisons max1')
                decoded[case['id']] = values['libvorbis']
            expected_meta = [dict(decoder=decoder, kind=kind, cases=group,
                passed=(all(name in decoded for name in group) and (all(decoded[name] == decoded[group[0]] for name in group[1:]) if kind == 'equal' else not all(decoded[name] == decoded[group[0]] for name in group[1:]))) if decoder == 'libvorbis' else False)
                for decoder in ('vorbis', 'libvorbis')
                for kind, groups in (('equal', source_matrix['expected_same_decoder_pcm_equal_groups']), ('different', source_matrix.get('expected_same_decoder_pcm_different_pairs', []))) for group in groups]
            need(host['metamorphic_checks'] == expected_meta and qualified['original_metamorphic_checks'] == expected_meta and
                 qualified['xiph_metamorphic_checks'] == [row for row in expected_meta if row['decoder'] == 'libvorbis'] and
                 all(row['passed'] for row in expected_meta if row['decoder'] == 'libvorbis'), 'Every recorded Xiph relation and unavailable native pair preserved')
            return qualified, decoded

        qualified, xiph_all = qualified_reference('host-original8', original_root, matrix, 'singletons8',
            '.build/cyd-vorbis-more-singletons-qualified-01/qualification.json', 'a5b5d47dca0d0826cdcff1dac010c78a836fdd44c053f93cf2818fb1877559bc')
        zero_qualified, zero_xiph = qualified_reference('host-zero8', zero_root, zero_matrix, 'zero8',
            '.build/cyd-vorbis-singleton-zero-bit-qualified-01/qualification.json', '86b8a8e94c0d84eccc788bb38912a62b6bc6b52cf9ff4e11a333b7b79e3f9d47')
        preserved = []
        for name, new in pairs:
            need(zero_xiph[name] == xiph_all[name] == zero_xiph[new], 'Complete original/raw Xiph PCM preserved and four actual zero-pair equalities')
            preserved.append(dict(id='0-' + name, all_raw_bytes_equal=True, full_Xiph_PCM_bytes_equal=True,
                pcm_bytes=len(zero_xiph[name]), pcm_sha256=sha(zero_xiph[name]), predecessor_qualification_sha256=sha(raw['.build/cyd-vorbis-more-singletons-qualified-01/qualification.json'])))
        need(zero_qualified['original_map1_preservation'] == preserved and zero_qualified['predecessor_qualification_sha256'] ==
             sha(raw['.build/cyd-vorbis-more-singletons-qualified-01/qualification.json']), 'All four predecessor raw/full-PCM preservation records exact')

        numeric = reports['numeric8']; target_all = {}
        need(numeric['result'] == 'BOUNDED_CORPUS_PCM_REJECTED' and numeric['measurement_completed'] is numeric['actual_reference_compared'] is True and
             numeric['bounded_corpus_pcm_qualified'] is False and len(numeric['cases']) == 8 and numeric['original_dual_reference_passed'] is False and
             numeric['original_reference_failures'] == reports['host-original8']['failures'] and numeric['original_native_lookup2_refusals'] == numeric['original_native_packet_decode_failures'] == 4 and
             numeric['original_native_cause_diagnosed'] is False and numeric['prior_capture_requalified'] is False, 'Actual complete numeric NONPASS/original failures preserved')
        need(all(numeric[k] is False for k in ('passed', 'numeric_reference_qualified', 'format_corpus_qualified', 'format_conformance_qualified',
             'full_G6_qualified', 'physical_device', 'production_radio_integration')), 'Bounded numeric rejection cannot become broader qualification')
        for index, (case, item, measured) in enumerate(zip(contract['model']['cases'], captured, numeric['cases'])):
            reference = xiph_all[case['id']]
            source, accepted = matrix['cases'][index], qualified['cases'][index]
            need((measured['lookup_type'], measured['dimensions'], measured['sequence_p']) ==
                 tuple(source['vector_book'][k] for k in ('lookup_type', 'dimensions', 'sequence_p')) and
                 (measured['rate'], measured['channels'], measured['bits'], measured['reference_id']) == (case['rate'], 2, 16, '0-' + case['id']) and
                 measured['original_native_failure_kind'] == accepted['native_failure_kind'] and measured['original_native_returncode'] == accepted['native_actual_returncode'], 'All per-case numeric/source/reference classification metadata')
            need(measured['case'] == index and measured['id'] == case['id'] and measured['packet_offsets'] == item['packet_offsets'] and
                 measured['comparison'] == metrics.compare(reference, item['pcm'], case['pcm']) and
                 measured['alignment'] == metrics.alignment(reference, item['pcm'], 8) and
                 measured['reference_transition_nonzero'] == adapter.transition_counts(reference, case, item['packet_offsets']) and
                 measured['target_transition_nonzero'] == adapter.transition_counts(item['pcm'], case, item['packet_offsets']), 'All8 untrimmed sample/channel/packet metrics and diagnostic alignment')
            target_all[case['id']] = item['pcm']
        relations = dict(xiph_triples=policy.relations(xiph_all, policy.TRIPLES), target_triples=policy.relations(target_all, policy.TRIPLES),
            xiph_different_pairs=policy.relations(xiph_all, policy.DIFFERENT_PAIRS, kind='different'), target_different_pairs=policy.relations(target_all, policy.DIFFERENT_PAIRS, kind='different'))
        chosen, passed = policy.bounded_policy(numeric['cases'], relations, 2)
        need(relations == numeric['metamorphic_relations'] and all(row['expected_relation_observed'] for rows in relations.values() for row in rows) and
             chosen == numeric['policy'] and passed is False and [row['comparison']['zero_lag_direct_LR']['max_abs_error'] for row in numeric['cases']] ==
             [1, 1, 1, 65535, 1, 65535, 1, 65535], 'Fixed2-LSB complete8 NONPASS; all2 triples/4 differences on each decoder pass')
    finally:
        for name, previous in saved_modules.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous

    for receipt_key in manifest['plan']['extra_receipts']:
        need(sha(raw[receipt_key]) == manifest['plan']['extra_receipt_pins'][receipt_key], 'Exact actual extra receipt identity')
        receipt(obj(raw[receipt_key]), 0)
    for name, count in (('cyd-vorbis-more-singletons-controls-01-command.json', 31), ('cyd-vorbis-singleton-zero-bit-controls-01-command.json', 28)):
        actual = obj(raw['.build/' + name]); stderr = next(path for path in actual['logs'] if path.endswith('stderr.log'))
        need(re.search(rb'Ran ' + str(count).encode() + rb' tests\b.*\bOK\b', frozen(None, stderr, actual['logs'][stderr]['sha256']), re.S), 'Actual complete control-count/OK terminal evidence; controls are not rerun')
    checkpoint = manifest['plan']['checkpoint']
    need(files[checkpoint['path']]['stored'] == 'CHECKPOINT.md' and sha(raw[checkpoint['path']]) == checkpoint['sha256'], 'Exact root factual checkpoint')
    need(manifest['plan']['prior25_floor0_wide_record_only_not_replayed'] is True and manifest['plan']['zero_target_executed'] is False,
         'Unchanged historical record-only scope and no zero target inference')
    dep.current()
    return dict(verified=True, cases=8, packets=112, PCM_bytes=225280, protocol_events=251, case_mask=255,
        original_controls_recorded=31, zero_controls_recorded=28, reference_children=32,
        full_numeric_NONPASS_preserved=True, original_dual_NONPASS_preserved=True, zero_dual_NONPASS_preserved=True,
        max_abs_errors=[1, 1, 1, 65535, 1, 65535, 1, 65535], metric_bound=2,
        zero_control_cleared_one_bits=56, zero_tokens=112, zero_comparison_tokens=224,
        zero_native_accepted_cases=4, zero_native_max_abs_errors=[1, 1, 1, 1], zero_target_executed=False,
        prior_campaigns_replayed=False, full_G6_qualified=False, physical_device=False, production_firmware=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--repository', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle, args.repository)))

