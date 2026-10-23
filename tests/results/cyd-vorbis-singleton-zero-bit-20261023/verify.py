"""Read-only offline singleton zero-bit8 evidence verifier; never run a codec, process or SDK."""
import argparse
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
MATERIALIZE_HELPERS = '62f7be16aee4a60c216e887330ab801d898b7114fc1d0c16ac761e255897406e'
REFERENCE_HELPERS = 'a8509c9ebc5dd351ddab9ed4aa8e9a41bfbc742d06cce6a77a34072ffca6d8eb'
ARCHIVE_PROTOCOL = 'b7dfc6c922d63b82834c6306d6bc25c870ac6e104e32397151a9cb0d11813bc1'
NUMERIC_ROOT = '.build/cyd-vorbis-singleton-zero-bit-numeric-prep-02/'
RAW_HELPERS = '9af2a14101e5f699959603024925e0cc7e27dd2c1a27cb67fd8e6c3c050363e3'
ZERO_HELPERS = '0dd2751666a52cb5b8b2430051d2cb6f34a1b90083768f97b40ce1a201ed7a50'
REFERENCE_GATE = 'e15b4ea2aab489c203d6bc925c60f1e344a14872fd7cc7be249ae539ad22eb60'
POLICY = '3721e54061f1082c7c68eb678fb93a93170d8eaa37610bdfb4e1492d83cdb6eb'
POLICY_PROTOCOL = 'a3dd2afc97e42b8b98f9dc8eb2b66480555e94d0191743d74750ccd090f2d735'
NUMERIC_HELPERS = '98b99f683cd9f579cc0eaf4849e0dec9dd0ff34b66cf2aec38f87e11adb5ecb5'


def load_module(name, path, expected):
    need(sha(path.read_bytes()) == expected, 'Unreviewed archived module')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(bundle, repository):
    bundle, repository = bundle.resolve(), repository.resolve()
    manifest = obj((bundle / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'cyd-singleton-zero-bit-checkpoint-v1' and
         manifest['plan']['schema'] == 'cyd-singleton-zero-bit-selection-v1' and
         set(manifest['plan']['roles']) == {'capture8', 'numeric8', 'numeric-input-failure01', 'host-zero8'}, 'Focused singleton zero-bit archive schema/roles')
    need(manifest['dependency_archive'] == dict(path='tests/results/cyd-vorbis-map2-20261020',
        manifest_sha256=MANIFEST_SHA, required=True, standalone=False, scope='exact-shared-entries-only-no-prior-campaign-replay'), 'Explicit unchanged CYD dependency required')
    need(manifest['intended_destination'] == 'tests/results/cyd-vorbis-singleton-zero-bit-20261023' and
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
    for role in ('capture8', 'numeric8', 'numeric-input-failure01', 'host-zero8'):
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
                need(role.startswith('numeric') and omitted.get('external_numeric_input') is True and
                     omitted['raw_sha256'] == row['sha256'] and omitted['raw_bytes'] == row['bytes'] and
                     PureWindowsPath(external).name in {'ffmpeg.exe', 'python.exe'}, 'Explicit hash-only external numeric tool metadata')
                continue
            frozen(role, path, row['sha256'], row.get('bytes'))
        for path, digest in report.get('tools', {}).items():
            need(manifest['external_omitted'][norm(path)]['raw_sha256'] == digest, 'Tool/archive hash omission metadata')
    def source_module(name, key, expected=None):
        need(key in raw and files[key].get('encoding') == 'raw', 'Retained plain module source required')
        return load_module(name, bundle / files[key]['stored'], expected or sha(raw[key]))
    failed_numeric = reports['numeric-input-failure01']
    need(sha(data('numeric-input-failure01')) == '1bb67ee06ccb018ae99dc86798b3a0f22936ae97095611e8df5570f914efc5fc' and
         failed_numeric['result'] == 'INPUT_OR_MEASUREMENT_REJECTED' and failed_numeric['cases'] == [] and
         failed_numeric['measurement_completed'] is failed_numeric['actual_reference_compared'] is failed_numeric['bounded_corpus_pcm_qualified'] is False and
         all(failed_numeric[k] is False for k in ('passed', 'numeric_reference_qualified', 'format_corpus_qualified', 'format_conformance_qualified',
             'full_G6_qualified', 'physical_device', 'production_radio_integration', 'vendor_comparison_available', 'original_dual_reference_passed', 'native_cause_diagnosed')) and
         failed_numeric['error_type'] == 'KeyError' and failed_numeric['error'] == "'ogg_sha256'" and
         manifest['roles']['numeric-input-failure01']['expected_outer_exit'] == 1,
         'Actual first schema input rejection before first target-reference metrics; no numerical NONPASS inference')
    target = reports['capture8']
    need(target['result'] == 'CHECKED_CORPUS_PCM_CAPTURED' and target['completed'] is True and
         target['target_capture_completed'] is True and target['checked_decode_completed'] is True and
         all(target.get(name) is False for name in ('passed', 'vendor_comparison_available', 'vendor_checked_pcm_equal',
             'independent_reference_compared', 'numeric_reference_qualified', 'format_corpus_qualified', 'full_G6_qualified',
             'physical_device', 'production_radio_integration')), 'Actual full8 capture scope')
    terminal = obj(raw[manifest['roles']['capture8']['terminal']])
    need(terminal['report_sha256'] == sha(data('capture8')) and terminal['entrypoint_sha256'] ==
         'e873f0e66ca99b8d81a2e06f74a7577c2274d3426c5b3e77f5897ecaaf8d9169' and
         (terminal['session_id'], terminal['terminal_chunk_id'], terminal['exit_code']) == (30900, 'e74ce4', 0), 'Actual direct-tool target terminal')
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
    need(sha(data('capture8', 'sources/corpus/contract.json')) == '1aba63ac2aab7255c012d65276fa98e438876784d0b3cdb3f70ed4429676078c' and
         sha(data('capture8', 'sources/project/main/data.h')) == '55c60cc4bcaa280a138251683c7c30ddbf44aaa810f82c193aa5d0967dc262c6', 'Exact full8 contract/header')
    need(sha(data('capture8', 'sources/helpers/protocol.py')) == 'a3dd2afc97e42b8b98f9dc8eb2b66480555e94d0191743d74750ccd090f2d735', 'Exact original runtime protocol source')
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

    runtime_root = '.build/cyd-vorbis-singleton-zero-bit-runtime-01/'
    materializer = load_module('offline_zero8_restricted_C_reader', bundle / 'materialize_helpers.py', MATERIALIZE_HELPERS)
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

    zero_root = '.build/cyd-vorbis-singleton-zero-bit-generated-01/'
    original_root = '.build/cyd-vorbis-more-singletons-generated-01/'
    index = obj(raw[zero_root + 'manifest.json'])
    need(index['schema'] == 'singleton-zero-bit-generated-manifest-v1' and len(index['files']) == 43 and
         sha(raw[zero_root + 'manifest.json']) == 'c300a312f36abff95e9219479c7d0edd59b47ce09cf6a6dcd6af25f304e45858' and
         {key[len(zero_root):] for key in raw if key.startswith(zero_root)} == {row['path'] for row in index['files']} | {'manifest.json'},
         'Exact complete44-file additive zero corpus')
    for row in index['files']:
        need(len(raw[zero_root + row['path']]) == row['bytes'] and sha(raw[zero_root + row['path']]) == row['sha256'], 'Every generated zero raw/metadata/carrier file')
    old_index = obj(raw[original_root + 'manifest.json'])
    need(sha(raw[original_root + 'manifest.json']) == '3ad3a1f9b466d92b2c701c787bdec42ed708cfa9146a3804dcf3d5cc766aeadf',
         'Original source-generation manifest identity remains recorded')
    for name in ('matrix.json', 'bitfields.json'):
        row = next(row for row in old_index['files'] if row['path'] == name)
        need(len(raw[original_root + name]) == row['bytes'] and sha(raw[original_root + name]) == row['sha256'], 'Finite original source metadata exact')
    matrix, bitfields = obj(raw[original_root + 'matrix.json']), obj(raw[original_root + 'bitfields.json'])
    zero_matrix, zero_fields = obj(raw[zero_root + 'matrix.json']), obj(raw[zero_root + 'bitfields.json'])
    zero_witness = obj(raw['.build/cyd-vorbis-singleton-zero-bit-witness-01.json'])
    need(zero_witness['result'] == 'FINITE_ZERO_BIT_COMPARISON_WITNESSED' and
         (zero_witness['cases'], zero_witness['audio_packets'], zero_witness['zero_tokens'], zero_witness['comparison_tokens'], zero_witness['cleared_original_one_bits']) ==
         (8, 112, 112, 224, 56), 'Actual full additive zero witness counts')
    helper = load_module('raw_helpers', bundle / 'raw_helpers.py', RAW_HELPERS)
    saved_raw_helper = sys.modules.get('raw_helpers')
    sys.modules['raw_helpers'] = helper
    try:
        zero_helper = load_module('zero_helpers', bundle / 'zero_helpers.py', ZERO_HELPERS)
        def parts(root, case):
            return {kind: frozen('capture8', base + '/' + root + rel(case[kind]), case['files'][kind]['sha256'], case['files'][kind]['bytes'])
                    for kind in ('identification', 'comment', 'setup', 'audio', 'ogg')}
        def packets(case, content):
            offsets = case['offsets']
            need(len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(content['audio']) and
                 all(type(a) is int and a < b for a, b in zip(offsets, offsets[1:])), 'Full actual packet offsets')
            return [content['audio'][a:b] for a, b in zip(offsets, offsets[1:])]
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
            book, book_proof, setup_fields = helper.parse_setup(old_parts['setup'], old['id'])
            helper.compare_field_report(setup_fields, zero_fields[old['id']]['setup'])
            helper.compare_field_report(helper.parse_identification(old_parts['identification']), zero_fields[old['id']]['identification'])
            helper.compare_field_report(helper.parse_comment(old_parts['comment']), zero_fields[old['id']]['comment'])
            old_audio, new_audio = packets(old, old_parts), packets(new, new_parts)
            need(old['offsets'] == new['offsets'], 'Additive full packet offsets unchanged')
            proofs, original_proofs, edits = [], [], []
            for packet, (a, b) in enumerate(zip(old_audio, new_audio)):
                original_proof, original_fields = helper.parse_audio(a, book, packet)
                helper.compare_field_report(original_fields, zero_fields[old['id']]['audio'][packet])
                original_proofs.append(original_proof)
                proof, fields, positions = zero_helper.parse_zero_audio(b, book, packet)
                helper.compare_field_report(fields, zero_fields[new['id']]['audio'][packet])
                need(zero_fields[new['id']]['audio'][packet] == zero_helper.zero_field_report(zero_fields[old['id']]['audio'][packet], positions),
                     'Every non-token field metadata unchanged')
                expected = copy.deepcopy(original_proof); expected['single_entry_wire_bits'] = [[0], [0]]
                need(proof == expected, 'Full actual vectors/indices/classwords/consumption unchanged')
                edits.append(dict(packet=packet, original_id=old['id'], changed_bit_offsets=zero_helper.unchanged_except_tokens(a, b, positions), consumed_zero_tokens=2))
                proofs.append(proof)
            need(original_proofs == old['packet_syntax'], 'All original singleton fields/vectors exactly witnessed')
            helper.compare_audit(book, old['vector_book'], original_proofs)
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

    finally:
        if saved_raw_helper is None:
            sys.modules.pop('raw_helpers', None)
        else:
            sys.modules['raw_helpers'] = saved_raw_helper

    runtime_readiness = obj(raw['.build/cyd-vorbis-singleton-zero-bit-runtime-prep-01/readiness.json'])
    need(sha(raw['.build/cyd-vorbis-singleton-zero-bit-runtime-prep-01/readiness.json']) ==
         'eee7166bc9ed73edf08f5181864a2d01635ecc53c397035058bdad890b69e9bb' and
         runtime_readiness['schema'] == 'singleton-zero8-runtime-source-readiness-v1' and
         {key[len('.build/cyd-vorbis-singleton-zero-bit-runtime-prep-01/'):] for key in raw if key.startswith('.build/cyd-vorbis-singleton-zero-bit-runtime-prep-01/')} ==
         set(runtime_readiness['expected_self_files']), 'Complete28-file reviewed runtime preparation')
    for row in runtime_readiness['files']:
        value = raw['.build/cyd-vorbis-singleton-zero-bit-runtime-prep-01/' + row['path']]
        need(len(value) == row['bytes'] and sha(value) == row['sha256'], 'Each exact runtime preparation source')
    preparation = obj(raw[runtime_root + 'preparation.json'])
    need(sha(raw[runtime_root + 'preparation.json']) == '2730c7db7c6843f2ef3d2e2ce6d395e11a6fcef58e38e1dd84eeb880cb7f38e4' and
         preparation['schema'] == 'singleton-zero8-root-materialization-v1' and preparation['completed'] is
         preparation['all_eight_original_bytes_unchanged'] is preparation['actual_qualification_terminal0_verified'] is True and
         preparation['counts'] == dict(cases=8, packets=112, expected_pcm_bytes=225280, protocol_events=251, case_mask=255, arrays=40, full_raw_arrays=24) and
         all(preparation[k] is False for k in ('target_executed', 'numeric_qualified', 'full_G6_qualified')), 'Actual source materialization only')
    qkey = '.build/cyd-vorbis-singleton-zero-bit-qualified-01/qualification.json'
    qualified = obj(raw[qkey]); host = reports['host-zero8']
    gate = load_module('offline_zero8_mixed_reference_gate', bundle / 'reference_gate.py', REFERENCE_GATE)
    gate.qualification_gate(qualified)
    need(sha(raw[qkey]) == '86b8a8e94c0d84eccc788bb38912a62b6bc6b52cf9ff4e11a333b7b79e3f9d47' and
         host['completed'] is host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False and
         host['target_executed'] is host['production_changed'] is False and len(host['commands']) == 16 and len(host['cases']) == 8 and
         len(host['failures']) == 4 and qualified['original_failures'] == host['failures'] and
         qualified['original_report_sha256'] == sha(data('host-zero8')) and
         qualified['original_outer_receipt_sha256'] == sha(raw[manifest['roles']['host-zero8']['terminal']]) and
         qualified['policy'] == dict(max_abs_error=2, predeclared=True, purpose='bounded-reference-crosscheck-not-standard-conformance'),
         'One actual mixed reference campaign; full8 dual NONPASS remains')
    for row in qualified['validated_inputs'].values():
        path = norm(row['path'])
        if path in manifest['external_omitted']:
            need(manifest['external_omitted'][path]['raw_sha256'] == row['sha256'] and manifest['external_omitted'][path]['raw_bytes'] == row['bytes'],
                 'Actual qualified external tool identity omitted exactly')
        else:
            frozen('capture8', row['path'], row['sha256'], row['bytes'])
    binding = obj(raw[runtime_root + 'reference-binding8.json'])
    need(binding['schema'] == 'singleton-zero8-recorded-reference-binding-v1' and binding['completed'] is True and
         binding['contract_sha256'] == contract['contract_sha256'] and len(binding['cases']) == len(mapping['cases']) == 8 and
         binding['actual_single_scope_reference_campaign_exists'] is binding['prior_original_singletons_numeric_record_only'] is True and
         binding['expected_equal_groups'] == pairs and binding['expected_different_pairs'] == [] and
         (binding['native_compared'], binding['native_packet_decode_failures'], binding['native_lookup2_refusals'],
          binding['successful_current_WAV_streams_replayed'], binding['actual_child_receipts_checked']) == (4, 4, 0, 12, 16) and
         all(binding[k] is False for k in ('dual_reference_passed', 'native_cause_diagnosed', 'new_reference_commands_executed',
             'aggregate_reference_campaign_exists', 'prior_numeric_NONPASS_requalified', 'target_executed', 'target_numeric_comparison_performed', 'full_G6_qualified')),
         'Full8 mixed source/reference binding with separate original4 refusal and new4 acceptance')
    need(binding['source_scopes'] == [dict(name='actual_zero8', qualification_path=qkey, qualification_sha256=sha(raw[qkey]),
        host_path=manifest['roles']['host-zero8']['root'] + '/report.json', host_sha256=sha(data('host-zero8')),
        receipt_path=manifest['roles']['host-zero8']['terminal'], receipt_sha256=sha(raw[manifest['roles']['host-zero8']['terminal']]),
        original_returncode=1, totals=[8, 4, 0, 4, 112, 225280])], 'Exact one mixed-reference source scope')
    for row in binding['proof_facts']:
        frozen('capture8', row['path'], row['sha256'], row['bytes'])
    for row in binding['external_reference_tool_identities']:
        need(manifest['external_omitted'][norm(row['path'])]['raw_sha256'] == row['sha256'] and
             manifest['external_omitted'][norm(row['path'])]['raw_bytes'] == row['bytes'], 'Exact mixed reference tool omissions')
    reference = load_module('offline_zero8_reference_reader', bundle / 'reference_helpers.py', REFERENCE_HELPERS)
    commands = {row['name']: row for row in host['commands']}
    need(len(commands) == 16 and len(zero_matrix['cases']) == len(contract['model']['cases']) == 8 and
         [c['id'] for c in zero_matrix['cases']] == list(gate.CASE_IDS), 'Exactly16 distinct children and exact8 original/zero order')
    current_pcm = {'vorbis': {}, 'libvorbis': {}}; current_info = {}; binding_rows = []
    for index, (case, origin, source, original, accepted) in enumerate(zip(contract['model']['cases'], mapping['cases'], zero_matrix['cases'], host['cases'], qualified['cases'])):
        rid, native = '0-' + case['id'], index >= 4; folder = 'cases/' + rid + '/'
        need(original['id'] == accepted['id'] == rid and original['input'] == source and original['source_matrix_sha256'] == sha(raw[zero_root + 'matrix.json']) and
             norm(ntpath.normpath(original['source_matrix'])) == base + '/' + zero_root + 'matrix.json' and
             frozen('host-zero8', original['source_matrix'], sha(raw[zero_root + 'matrix.json'])) == raw[zero_root + 'matrix.json'] and
             origin['case'] == index and origin['id'] == case['id'] == source['id'] and
             origin['original_case_fields'] == origin['selected_case_fields'] == source and origin['fields_changed'] == [] and
             case['raw_sha256'] == {kind: source['raw_sha256'][kind] for kind in ('identification', 'setup', 'audio')} and
             (accepted['rate'], accepted['channels'], accepted['bits']) == (case['rate'], 2, 16) and
             accepted['frames'] == case['frames'][1:] and accepted['pcm_bytes'] == case['total_pcm'], 'Every original path, snapshot, header, frame and classification binding')
        for kind in ('identification', 'comment', 'setup', 'audio', 'ogg'):
            expected = raw[zero_root + rel(source[kind])]
            need(sha(expected) == source['files'][kind]['sha256'] and len(expected) == source['files'][kind]['bytes'], 'Every source member hash/size')
            for which in ('original', 'selected'):
                fact = origin['files'][kind][which]
                need(frozen('capture8', fact['path'], fact['sha256'], fact['bytes']) == expected, 'All original/selected bytes unchanged')
        need(data('host-zero8', folder + 'input.ogg') == raw[zero_root + source['ogg']], 'Every actual current reference input carrier exact')
        details = {}
        for decoder in ('vorbis', 'libvorbis'):
            code = 4294967295 if decoder == 'vorbis' and not native else 0
            name = folder + 'decode-' + decoder; command = commands[name]
            child_raw = data('host-zero8', command['receipt']); need(sha(child_raw) == command['sha256'], 'Actual child receipt identity')
            child = obj(child_raw); receipt(child, code, 'host-zero8'); argv = child['argv']
            need(child['runner_sha256'] == '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e' and
                 child['executable_sha256'] == host['tools'][argv[0]] and argv[argv.index('-c:a') + 1] == decoder and
                 '-ar' not in argv and '-ac' not in argv and '-xerror' in argv and argv[argv.index('-err_detect') + 1] == 'explode' and
                 address(argv[argv.index('-i') + 1], 'host-zero8') == manifest['roles']['host-zero8']['root'] + '/' + folder + 'input.ogg',
                 'Every actual strict decoder command/tool/current input')
            stdout, stderr = data('host-zero8', name + '.stdout.log'), data('host-zero8', name + '.stderr.log')
            if code:
                need(not stdout and data('host-zero8', folder + 'vorbis.wav') == b'' and decoder not in original['decoded'] and
                     len(original['failures']) == 1 and original['failures'][0]['stage'] == 'vorbis' and
                     b'Error submitting packet to decoder: Operation not permitted' in stderr and
                     b'Error processing packet in decoder: Operation not permitted' in stderr and b'Codebook lookup type not supported.' not in stderr,
                     'All4 original native packet refusals and empty output; no lookup/OS/cause inference')
                continue
            need(not stderr, 'Strict successful reference decoder stderr')
            pcm, evidence = reference.decoded_pcm(data('host-zero8', folder + decoder + '.wav'), stdout, case['rate'], 2, case['frames'], case['modes'])
            need(evidence == original['decoded'][decoder] and len(pcm) == case['total_pcm'], 'Every12 current complete WAV/framemd5 streams and real-channel transitions')
            if decoder == 'libvorbis':
                need({k: v for k, v in accepted.items() if k not in ('id', 'xiph_qualified', 'native_compared', 'native_lookup2_refusal',
                    'native_packet_decode_failure', 'native_outcome_kind', 'native_actual_returncode', 'native_cause_diagnosed', 'cross_reference_max_abs_error')} == evidence,
                    'Every qualified Xiph field exactly replayed')
            current_pcm[decoder][case['id']], details[decoder] = pcm, evidence
        current_info[case['id']] = details
        binding_rows.append(dict(case=index, id=case['id'], original_group='zero4' if native else 'original4', original_reference_id=rid,
            qualification_sha256=sha(raw[qkey]), original_host_report_sha256=sha(data('host-zero8')),
            original_host_receipt_sha256=sha(raw[manifest['roles']['host-zero8']['terminal']]), original_host_returncode=1,
            raw_sha256=case['raw_sha256'], frames=case['frames'], pcm_bytes=case['total_pcm'], rate=case['rate'], channels=2,
            reference_pcm_sha256=accepted['pcm_sha256'], reference_wav_sha256=accepted['wav_sha256'], native_compared=native,
            native_lookup2_refusal=False, native_packet_decode_failure=not native, native_outcome_kind=accepted['native_outcome_kind'],
            native_actual_returncode=accepted['native_actual_returncode'], cross_reference_max_abs_error=accepted['cross_reference_max_abs_error'],
            native_cause_diagnosed=False, xiph_qualified_existing=True))
    need(binding_rows == binding['cases'] and len(current_pcm['libvorbis']) == 8 and len(current_pcm['vorbis']) == 4,
         'Complete mixed12 current outputs and all8 exact binding rows')
    expected_meta = [dict(decoder=decoder, kind='equal', cases=group, passed=decoder == 'libvorbis')
                     for decoder in ('vorbis', 'libvorbis') for group in pairs]
    need(host['metamorphic_checks'] == qualified['original_metamorphic_checks'] == expected_meta and
         qualified['xiph_metamorphic_checks'] == [row for row in expected_meta if row['decoder'] == 'libvorbis'] and
         all(current_pcm['libvorbis'][old] == current_pcm['libvorbis'][new] for old, new in pairs), 'All4 actual current Xiph equality pairs, native pairs remain unavailable')
    facts = qualified['validated_inputs']
    prior_q = obj(frozen('capture8', facts['predecessor/qualification']['path'], facts['predecessor/qualification']['sha256']))
    prior_host = obj(frozen('capture8', facts['predecessor/host']['path'], facts['predecessor/host']['sha256']))
    need(facts['predecessor/qualification']['sha256'] == 'a5b5d47dca0d0826cdcff1dac010c78a836fdd44c053f93cf2818fb1877559bc' and
         qualified['predecessor_qualification_sha256'] == facts['predecessor/qualification']['sha256'] and
         prior_q['result'] == 'XIPH_QUALIFIED_DUAL_NONPASS' and prior_q['xiph_cases'] == 8 and prior_q['dual_reference_qualified'] is False,
         'Prior qualification record only; unchanged original refusal scope')
    preserved = []
    for name, new in pairs:
        case = next(c for c in contract['model']['cases'] if c['id'] == name); rid = '0-' + name
        wav, md5 = facts['predecessor-Xiph-WAV/' + rid], facts['predecessor-Xiph-framemd5/' + rid]
        pcm, evidence = reference.decoded_pcm(frozen('capture8', wav['path'], wav['sha256'], wav['bytes']),
            frozen('capture8', md5['path'], md5['sha256'], md5['bytes']), case['rate'], 2, case['frames'], case['modes'])
        old = next(c for c in prior_host['cases'] if c['id'] == rid)
        need(evidence == old['decoded']['libvorbis'] and pcm == current_pcm['libvorbis'][name] == current_pcm['libvorbis'][new],
             'Every prior original4 raw/full-Xiph preservation; no old target PCM replay')
        preserved.append(dict(id=rid, all_raw_bytes_equal=True, full_Xiph_PCM_bytes_equal=True, pcm_bytes=len(pcm), pcm_sha256=sha(pcm),
            predecessor_qualification_sha256=facts['predecessor/qualification']['sha256']))
    need(preserved == qualified['original_map1_preservation'] == binding['original_map1_preservation'], 'All4 actual predecessor-preservation records exact')
    prior_numeric = obj(raw[address(base + '/.build/cyd-vorbis-more-singletons-numeric-measurement-01/report.json', 'capture8')])
    need(prior_numeric['measurement_completed'] is True and prior_numeric['bounded_corpus_pcm_qualified'] is False and
         prior_numeric['result'] == 'BOUNDED_CORPUS_PCM_REJECTED', 'Prior numeric NONPASS record-only; no target requalification')

    for root, digest, schema in (('.build/cyd-vorbis-singleton-zero-bit-numeric-prep-01/', '8642af1eb5e03b8b0c2435fb3e31176765b594838e1fcb19c1942548d79622d6', 'singleton-zero8-numeric-source-readiness-v1'),
                                 (NUMERIC_ROOT, '1af060f66ebf9ccce67e6c76eee948103566ffbf778d02559aa6706709c9efa2', 'singleton-zero8-numeric02-source-readiness-v1')):
        need(sha(raw[root + 'readiness.json']) == digest, 'Both reviewed immutable numerical source preparations')
        numeric_readiness = obj(raw[root + 'readiness.json'])
        need(numeric_readiness['schema'] == schema and
             {key[len(root):] for key in raw if key.startswith(root)} == set(numeric_readiness['expected_self_files']),
             'Both complete numerical source inventories')
        for row in numeric_readiness['files']:
            value = raw[root + row['path']]
            need(len(value) == row['bytes'] and sha(value) == row['sha256'], 'Every original/corrected numerical source/metric/policy pin')
    saved_modules = {name: sys.modules.get(name) for name in ('pcm_metrics', 'protocol', 'policy8')}
    try:
        metrics = source_module('pcm_metrics', NUMERIC_ROOT + 'pcm_metrics.py', METRICS)
        sys.modules['pcm_metrics'] = metrics
        policy_protocol = source_module('protocol', NUMERIC_ROOT + 'protocol.py', POLICY_PROTOCOL)
        sys.modules['protocol'] = policy_protocol
        policy = source_module('policy8', NUMERIC_ROOT + 'policy8.py', POLICY)
        sys.modules['policy8'] = policy
        numeric_helper = load_module('offline_zero8_numeric_helper', bundle / 'numeric_helpers.py', NUMERIC_HELPERS)
        need(tuple(case['id'] for case in zero_matrix['cases']) == policy.CASE_IDS == gate.CASE_IDS and
             [list(pair) for pair in policy.GROUPS] == pairs, 'Exact predeclared original4/zero4 numerical order and equal pairs')
        measured_rows = []; target_pcm = {}; numeric = reports['numeric8']
        for index, (case, item, accepted, original, bound) in enumerate(zip(contract['model']['cases'], captured, qualified['cases'], host['cases'], binding['cases'])):
            native = index >= 4; name = case['id']; decoders = ('libvorbis', 'vorbis') if native else ('libvorbis',)
            references = {}
            for decoder in decoders:
                pcm = current_pcm[decoder][name]
                references[decoder] = dict(comparison=metrics.compare(pcm, item['pcm'], case['pcm']),
                    alignment_diagnostic=metrics.alignment(pcm, item['pcm'], 8),
                    reference_transition_nonzero=numeric_helper.transition_counts(pcm, case, item['packet_offsets']),
                    target_transition_nonzero=numeric_helper.transition_counts(item['pcm'], case, item['packet_offsets']))
            cross = None
            if native:
                cross = metrics.compare(current_pcm['vorbis'][name], current_pcm['libvorbis'][name], case['pcm'])
                need(cross['zero_lag_direct_LR']['max_abs_error'] == accepted['cross_reference_max_abs_error'] ==
                     original['cross_reference_max_abs_error'] == bound['cross_reference_max_abs_error'] and
                     cross['zero_lag_direct_LR']['max_abs_error'] <= 2, 'Four available native/Xiph complete reference crosschecks unchanged')
            else:
                need(accepted['cross_reference_max_abs_error'] is bound['cross_reference_max_abs_error'] is None,
                     'No native original4 PCM/cross comparison fabricated')
            target_pcm[name] = item['pcm']
            measured_rows.append(dict(case=index, id=name, rate=case['rate'], channels=2, bits=16,
                frames=case['frames'], packet_bytes=case['pcm'], pcm_bytes=len(item['pcm']), packet_offsets=item['packet_offsets'], reference_id='0-' + name,
                references=references, native_compared=native, native_packet_decode_failure=not native, native_lookup2_refusal=False,
                native_actual_returncode=accepted['native_actual_returncode'], native_cause_diagnosed=False,
                original_reference_cross_comparison=cross, original_reference_metadata=current_info[name]))
        need(measured_rows == numeric['cases'], 'All8 complete case rows and all12 untrimmed sample/channel/packet metrics/alignment exactly replayed')
        metamorphic = dict(xiph=policy.relations(current_pcm['libvorbis']), target=policy.relations(target_pcm))
        chosen, bounded = policy.bounded_policy(measured_rows, metamorphic, 2)
        need(numeric['measurement_completed'] is numeric['actual_reference_compared'] is numeric['target_platform_verified'] is True and
             (numeric['complete_target_cases'], numeric['complete_target_packets'], numeric['complete_target_PCM_bytes'], numeric['complete_reference_streams_verified'],
              numeric['complete_target_reference_comparisons'], numeric['actual_reference_child_receipts_checked']) == (8, 112, 225280, 12, 12, 16) and
             numeric['metamorphic'] == metamorphic and numeric['policy'] == chosen and
             numeric['bounded_by_reference'] == chosen['bounded_by_reference'] and
             numeric['bounded_original4_Xiph'] is chosen['bounded_original4_Xiph'] and
             numeric['bounded_new_zero4_both_references'] is chosen['bounded_new_zero4_both_references'] and
             numeric['bounded_corpus_pcm_qualified'] is bounded and
             numeric['result'] == ('BOUNDED_CORPUS_PCM_QUALIFIED' if bounded else 'BOUNDED_CORPUS_PCM_REJECTED') and
             manifest['roles']['numeric8']['expected_outer_exit'] == (0 if bounded else 1), 'Complete fixed2 mixed12 result; actual NONPASS never promoted')
        need(numeric['native_original4_packet_refusals_retained'] == numeric['native_compared_new_zero4'] == 4 and
             numeric['prior_other_numeric_NONPASS_record_only'] is True and numeric['original_reference_failures'] == host['failures'] and
             numeric['original_reference_report_sha256'] == sha(data('host-zero8')) and
             numeric['target_report_sha256'] == sha(data('capture8')) and numeric['target_terminal_sha256'] == sha(raw[manifest['roles']['capture8']['terminal']]) and
             numeric['actual_runtime_preparation_sha256'] == sha(raw[runtime_root + 'preparation.json']) and
             numeric['policy_predeclared_max_abs_error'] == 2 and numeric['policy_requires_all12_available_references'] is True and
             all(numeric[k] is False for k in ('passed', 'numeric_reference_qualified', 'format_corpus_qualified', 'format_conformance_qualified',
                 'full_G6_qualified', 'physical_device', 'production_radio_integration', 'vendor_comparison_available',
                 'original_dual_reference_passed', 'native_cause_diagnosed', 'prior_numeric_NONPASS_requalified', 'new_reference_commands_executed')),
             'Mixed numerical scope/actual pins/no full8 dual pass and unrelated prior NONPASS unchanged')
    finally:
        for name, previous in saved_modules.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous
    for receipt_key in manifest['plan']['extra_receipts']:
        need(sha(raw[receipt_key]) == manifest['plan']['extra_receipt_pins'][receipt_key], 'Every actual extra receipt identity')
        receipt(obj(raw[receipt_key]), 0)
    for name, count in (('cyd-vorbis-singleton-zero-bit-controls-01-command.json', 28),
                        ('cyd-vorbis-singleton-zero-bit-runtime-controls-01-command.json', 30),
                        ('cyd-vorbis-singleton-zero-bit-numeric-controls-01-command.json', 44),
                        ('cyd-vorbis-singleton-zero-bit-numeric-controls-02-command.json', 54)):
        actual = obj(raw['.build/' + name]); stderr = next(path for path in actual['logs'] if path.endswith('stderr.log'))
        need(re.search(rb'Ran ' + str(count).encode() + rb' tests\b.*\bOK\b', frozen(None, stderr, actual['logs'][stderr]['sha256']), re.S),
             'Recorded full control-count/OK actual terminal0; controls are not rerun')
    checkpoint = manifest['plan']['checkpoint']
    need(files[checkpoint['path']]['stored'] == 'CHECKPOINT.md' and sha(raw[checkpoint['path']]) == checkpoint['sha256'], 'Exact root factual checkpoint')
    need(manifest['plan']['prior_other_numeric_NONPASS_record_only_not_replayed'] is manifest['plan']['no_full8_dual_reference_pass'] is True,
         'Only current full8/mixed12 comparison; unrelated numerical NONPASS remain record-only')
    dep.current()
    return dict(verified=True, cases=8, packets=112, PCM_bytes=225280, protocol_events=251, case_mask=255,
        source_controls_recorded=28, runtime_controls_recorded=30, original_numeric_controls_recorded=44, successor_numeric_controls_recorded=54, actual_reference_children=16, current_reference_PCM_streams=12,
        predecessor_Xiph_preservation_streams=4, original_native_packet_refusals=4, native_new_zero_accepted=4,
        full8_dual_reference_passed=False, native_cause_diagnosed=False, fixed_max_abs_error=2,
        bounded_by_reference=chosen['bounded_by_reference'], bounded_original4_Xiph=chosen['bounded_original4_Xiph'],
        bounded_new_zero4_both_references=chosen['bounded_new_zero4_both_references'], bounded_corpus_pcm_qualified=bounded,
        actual_numeric_NONPASS_preserved=not bounded, prior_other_numeric_NONPASS_replayed=False,
        max_abs_errors_by_reference={decoder: [row['references'][decoder]['comparison']['zero_lag_direct_LR']['max_abs_error']
            for row in measured_rows if decoder in row['references']] for decoder in ('libvorbis', 'vorbis')},
        full_G6_qualified=False, physical_device=False, production_firmware=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--repository', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle, args.repository)))
