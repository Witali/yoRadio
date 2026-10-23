"""Read-only offline mono/mapping21 evidence verifier; never run a codec, process or SDK."""
import argparse
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
MATERIALIZE_HELPERS = 'ac2bb1371a84dcea86176692f848b6cf91732dd27f653674f18c7e2f37c4e422'
REFERENCE_HELPERS = '049b905f19bb24d8772ef73837ae042555de3322ac2797a9a9ac58d5c593e216'
ARCHIVE_PROTOCOL = '7c51d5dad5597ea5f7cada1302e8beddb42760cb634d6340664c8bc9b4c8aec6'
NUMERIC_ROOT = '.build/cyd-vorbis-mono-mapping-numeric-prep-02/'
MONO_METRICS = '4ee2b1756a39e333bfc97d6e8149e61522cc3c06c6e3112773bb478e6d727075'
POLICY = '219ec8d967e45536cbddf926e932e8647693d3e1320a75d562a1cd913e2e9119'
NUMERIC_HELPERS = 'acc2f4dc40478c06f7bc9de419e33350d92c4132627929990f42b9ddf4e8e422'


def load_module(name, path, expected):
    need(sha(path.read_bytes()) == expected, 'Unreviewed archived module')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(bundle, repository):
    bundle, repository = bundle.resolve(), repository.resolve()
    manifest = obj((bundle / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'cyd-mono-mapping-checkpoint-v1' and
         manifest['plan']['schema'] == 'cyd-mono-mapping-selection-v1' and
         set(manifest['plan']['roles']) == {'capture21', 'numeric21', 'numeric-input-failure01', 'host21'}, 'Focused mono/mapping archive schema/roles')
    need(manifest['dependency_archive'] == dict(path='tests/results/cyd-vorbis-map2-20261020',
        manifest_sha256=MANIFEST_SHA, required=True, standalone=False, scope='exact-shared-entries-only-no-prior-campaign-replay'), 'Explicit unchanged CYD dependency required')
    need(manifest['intended_destination'] == 'tests/results/cyd-vorbis-mono-mapping-20261023' and
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
    for role in ('capture21', 'numeric21', 'numeric-input-failure01', 'host21'):
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
    need(sha(data('numeric-input-failure01')) == 'b87fd1d02fdf2fd532dd5edce71d3bc311cfe57fc4849a8937e3d690a1daad18' and
         failed_numeric['result'] == 'INPUT_OR_MEASUREMENT_REJECTED' and
         failed_numeric['measurement_completed'] is failed_numeric['actual_reference_compared'] is
         failed_numeric['bounded_corpus_pcm_qualified'] is False and failed_numeric['cases'] == [] and
         all(failed_numeric[k] is False for k in ('passed', 'numeric_reference_qualified', 'format_corpus_qualified',
             'format_conformance_qualified', 'full_G6_qualified', 'physical_device', 'production_radio_integration', 'vendor_comparison_available')) and
         failed_numeric['error_type'] == 'KeyError' and failed_numeric['error'] == "'variant/vorbis_repair/setup.c'" and
         manifest['roles']['numeric-input-failure01']['expected_outer_exit'] == 1,
         'Actual first input rejection preserved; no numeric measurement/NONPASS inference')
    target = reports['capture21']
    need(target['result'] == 'CHECKED_CORPUS_PCM_CAPTURED' and target['completed'] is True and
         target['target_capture_completed'] is True and target['checked_decode_completed'] is True and
         all(target.get(name) is False for name in ('passed', 'vendor_comparison_available', 'vendor_checked_pcm_equal',
             'independent_reference_compared', 'numeric_reference_qualified', 'format_corpus_qualified', 'full_G6_qualified',
             'physical_device', 'production_radio_integration')), 'Actual full21 capture scope')
    terminal = obj(raw[manifest['roles']['capture21']['terminal']])
    need(terminal['report_sha256'] == sha(data('capture21')) and terminal['entrypoint_sha256'] ==
         '77ceba3cc8ced16159e90316158480f778c74b5d1f7898c17f222180ee692574' and
         (terminal['session_id'], terminal['terminal_chunk_id'], terminal['exit_code']) == (46039, 'bfffd4', 0), 'Actual direct-tool target terminal')
    need([row['name'] for row in target['commands']] == COMMANDS, 'All9 actual target commands')
    for command in target['commands']:
        need(command['state'] == 'complete' and type(command['exit_status']) is int and command['exit_status'] == 0 and
             command['timed_out'] is False and command['interrupted'] is False and type(command['pid']) is int and command['pid'] > 0,
             'Actual owned target command terminals')
        for stream in ('stdout', 'stderr'):
            need(sha(data('capture21', command['name'] + '.' + stream + '.log')) == command[stream + '_sha256'], 'Actual target command log')
    for field in ('build_outputs', 'variant_sources'):
        for path, digest in target.get(field, {}).items():
            need(files[manifest['roles']['capture21']['root'] + '/' + norm(path)]['raw_sha256'] == digest, 'Actual target output/variant identity')
    need(sha(data('capture21', 'sources/project/main/main.c')) == 'e13299fb92b2635a0a8d4a664e0962118d5dfe6973c170f370a39469100ad6ab' and
         sha(data('capture21', 'variant/vorbis_repair/setup.c')) == sha(data('capture21', 'sources/candidate/vorbis_repair/setup.c')) ==
         '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c', 'Exact public caller/CYD source')
    context = target['setup_macro_context']
    need(context['row'] in record('capture21', 'build/compile_commands.json'), 'Actual setup compile row')
    need(len(context['generated_inputs']) == 2, 'Actual cflags/specs macro context')
    for path, row in context['generated_inputs'].items():
        need(row['sha256_before'] == row['sha256_after'] == sha(raw[address(path, 'capture21')]), 'Stable actual macro inputs')
    macros = data('capture21', 'setup-macros.stdout.log').decode().replace('\r\n', '\n')
    need(not re.search(r'^#define (LIMIT_TO_64kHz|CONFIG_FREERTOS_UNICORE)\b', macros, re.M) and
         re.search(r'^#define CONFIG_IDF_TARGET_ESP32 1$', macros, re.M) and
         re.search(r'^#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240$', macros, re.M) and
         data('capture21', 'sdk-head.stdout.log').strip() == b'7101770dc6db2667b3c477cc31365dd1acd6db4e' and
         not data('capture21', 'sdk-clean.stdout.log').strip(), 'Actual CYD SDK/Xtensa/SMP profile')
    contract = record('capture21', 'sources/corpus/contract.json')
    need(sha(data('capture21', 'sources/corpus/contract.json')) == '8b62de9035798c6086d52259c68e26071e96e925d4ec569b4c448f96f70abe0b' and
         sha(data('capture21', 'sources/project/main/data.h')) == 'b7dfd4ed734c1861eb0a1945e8d3a18fee23a75b5a3657799a43f7cfb78ed23b', 'Exact full21 contract/header')
    need(sha(data('capture21', 'sources/helpers/protocol.py')) == '3923febd0269874103c0d4162061998518ee6361d8358be70b415fa95db2f44a', 'Exact original runtime protocol source')
    archive_protocol = load_module('offline_explicit_archive_protocol', bundle / 'archive_protocol.py', ARCHIVE_PROTOCOL)
    protocol = archive_protocol.make_validator(lambda path: raw[address(path, 'capture21')])
    need(protocol['load_contract'](contract['manifest_inputs']) == contract, 'Every actual raw/model contract field reconstructed archive-only')
    qemu = target['commands'][6]
    log = (data('capture21', 'qemu.stdout.log') + b'\n' + data('capture21', 'qemu.stderr.log')).decode(errors='replace')
    observed = protocol['validate_log'](log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
        interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == target['observed'] and (observed['cases'], observed['decoded_packets'], observed['pcm'], observed['protocol_lines'], observed['case_mask']) ==
         (21, 294, 464640, 654, 2097151) and len(captured) == len(target['observed_pcm']) == 21, 'Strict full21 actual protocol')
    for item, row in zip(captured, target['observed_pcm']):
        need(item['pcm'] == data('capture21', row['path']) and item['sha256'] == row['sha256'] and
             (item['case'], item['id'], item['packet_offsets']) == (row['case'], row['id'], row['packet_offsets']), 'Every persisted actual PCM byte/boundary')
    need({manifest['roles']['capture21']['root'] + '/' + norm(row['path']) for row in target['observed_pcm']} ==
         {key for key in raw if key.startswith(manifest['roles']['capture21']['root'] + '/observed-pcm/')}, 'Exact target PCM inventory')

    runtime_root = '.build/cyd-vorbis-mono-mapping-runtime-01/'
    materializer = load_module('offline_mono21_restricted_C_reader', bundle / 'materialize_helpers.py', MATERIALIZE_HELPERS)
    mapping = record('capture21', 'sources/corpus/source-map.json')
    raw_cases = [{kind: raw[address(item['files'][kind]['selected']['path'], 'capture21')]
                  for kind in ('identification', 'setup', 'audio')} for item in mapping['cases']]
    recovered = materializer.recover(data('capture21', 'sources/project/main/data.h').decode('ascii'), contract, raw_cases,
                                    sha(data('capture21', 'sources/corpus/contract.json')))
    saved_materialization = obj(raw[runtime_root + 'materialized01/report.json'])
    need(recovered == saved_materialization['cases'] and saved_materialization['counts'] ==
         dict(cases=21, arrays=105, full_raw_payload_arrays=63, packets=294, expected_pcm_bytes=464640,
              descriptor_capacity=21, case_mask=2097151) and len(saved_materialization['controls']) == 5 and
         all(row['rejected'] is True for row in saved_materialization['controls']), 'Actual independent105-array/header recovery and controls')

    def generated(key, expected):
        index = obj(raw[key + 'manifest.json'])
        need(sha(raw[key + 'manifest.json']) == expected and index['schema'] == 'vorbis-mono-mapping-manifest-v1' and
             len(index['files']) == 108 and {name[len(key):] for name in raw if name.startswith(key)} ==
             {row['path'] for row in index['files']} | {'manifest.json'}, 'Exact complete109-file generated mono21 inventory')
        for row in index['files']:
            content = raw[key + rel(row['path'])]
            need(len(content) == row['bytes'] and sha(content) == row['sha256'], 'Generated member exact raw identity')
        return obj(raw[key + 'matrix.json'])

    original_root = '.build/cyd-vorbis-mono-mapping-prep-01/generated01/'
    canonical_root = '.build/vorbis-mono-mapping-canonical-check-01/'
    original = generated(original_root, '415dff7e61db9940a8b4d89fc10f2cd10aa4b43dc30d0ba34a72f5f39e24acff')
    matrix = generated(canonical_root, '990d5900cfabf9a0027de900f54ad811e857c59944fae2f5f5ff2d4076594d95')
    need(raw[original_root + 'matrix.json'] == raw[canonical_root + 'matrix.json'] and original == matrix and
         raw[original_root + 'construction.json'] == raw[canonical_root + 'construction.json'] and
         sha(raw[canonical_root + 'matrix.json']) == '30fad94ec85727030a415f33c544041ed225aae97397b09584a534f7c2636d37',
         'Exact original21/canonical matrix and construction bytes preserved')
    for name in (key[len(canonical_root):] for key in raw if key.startswith(canonical_root + 'cases/')):
        need(raw[original_root + name] == raw[canonical_root + name], 'All105 original/canonical raw and Ogg files remain identical')
    reproduction_root = 'tests/results/vorbis-more-generators-20261020/'
    need(sha(raw[reproduction_root + 'manifest.json']) == 'c66cefeb56522cdb0b4b466c9823ca02c85d9c9772ed8679aa8944f611cf95ba',
         'Exact committed reproduction manifest')
    reproduction = obj(raw[reproduction_root + 'manifest.json'])
    need(reproduction['schema'] == 'vorbis-more-generators-record-v1' and len(reproduction['files']) == 24 and
         {key[len(reproduction_root):] for key in raw if key.startswith(reproduction_root)} == set(reproduction['files']) | {'manifest.json'},
         'Finite committed generator reproduction history')
    for name, row in reproduction['files'].items():
        need(len(raw[reproduction_root + rel(name)]) == row['bytes'] and sha(raw[reproduction_root + name]) == row['sha256'],
             'Every retained committed reproduction entry exact')
    need(raw[reproduction_root + 'mono/canonical/manifest.json'] == raw[canonical_root + 'manifest.json'] and
         raw[reproduction_root + 'mono/original/manifest.json'] == raw[original_root + 'manifest.json'], 'Actual original/canonical reproduction binding')
    for version in ('01', '02'):
        root = '.build/cyd-vorbis-mono-mapping-runtime-prep-' + version + '/'
        readiness = obj(raw[root + 'readiness.json'])
        need(readiness['schema'] == 'mono21-runtime-source-readiness-v1' and readiness['source_only'] is True and
             readiness['target_executed'] is readiness['numeric_qualified'] is readiness['full_G6_qualified'] is False and
             {key[len(root):] for key in raw if key.startswith(root)} == set(readiness['expected_self_files']),
             'Both immutable runtime preparation inventories/scope')
        for row in readiness['files']:
            need(len(raw[root + row['path']]) == row['bytes'] and sha(raw[root + row['path']]) == row['sha256'],
                 'Each immutable runtime preparation raw source pin')
    need(sha(raw['.build/cyd-vorbis-mono-mapping-runtime-prep-02/readiness.json']) ==
         '6be5847a47fc9c2af2046cb5a20738ee3d439805db78a48d52180c5cdf7f2c26', 'Reviewed successor runtime readiness')
    preparation = obj(raw[runtime_root + 'preparation.json'])
    need(preparation['schema'] == 'mono21-root-materialization-v1' and preparation['completed'] is True and
         preparation['actual_qualification_terminal0_verified'] is preparation['all_twenty_one_original_bytes_unchanged'] is True and
         preparation['counts'] == dict(cases=21, packets=294, expected_pcm_bytes=464640, protocol_events=654, case_mask=2097151, arrays=105, full_raw_arrays=63) and
         preparation['target_executed'] is preparation['numeric_qualified'] is preparation['full_G6_qualified'] is False,
         'Actual materialization is source preparation only')
    qkey = '.build/cyd-vorbis-mono-mapping-qualified-01/qualification.json'
    qualified = obj(raw[qkey]); host = reports['host21']
    need(sha(raw[qkey]) == 'c31a87de53327cb0e43215f92339b07fd64c48ba57dbde8778328f298b9f5684' and
         qualified['schema'] == 'public-vorbis-new-format-reference-qualification-v1' and qualified['profile'] == 'mono21' and
         qualified['result'] == 'DUAL_REFERENCE_QUALIFIED' and all(qualified[k] is True for k in
             ('completed', 'reference_corpus_qualified', 'xiph_reference_qualified', 'dual_reference_qualified', 'original_dual_reference_passed')) and
         all(qualified[k] is False for k in ('target_executed', 'production_changed', 'standard_conformance_qualified', 'full_G6_qualified', 'physical_device')) and
         (qualified['xiph_cases'], qualified['native_compared'], qualified['native_lookup2_refusals'], qualified['paired_raw_packets'], qualified['expected_pcm_bytes']) ==
         (21, 21, 0, 294, 464640), 'Actual full21 prior dual-reference qualification/scope')
    need(host['completed'] is host['xiph_reference_qualified'] is host['dual_reference_qualified'] is True and
         host['target_executed'] is host['production_changed'] is False and len(host['commands']) == 42 and len(host['cases']) == len(qualified['cases']) == 21 and
         host['failures'] == qualified['original_failures'] == [] and
         host['metamorphic_checks'] == qualified['original_metamorphic_checks'] == qualified['xiph_metamorphic_checks'] == [] and
         qualified['original_report_sha256'] == sha(data('host21')) and
         qualified['original_outer_receipt_sha256'] == sha(raw[manifest['roles']['host21']['terminal']]) and
         qualified['policy'] == dict(max_abs_error=2, predeclared=True, purpose='bounded-reference-crosscheck-not-standard-conformance'),
         'One actual42-child campaign; no invented metamorphic group or unrelated requalification')
    for row in qualified['validated_inputs'].values():
        path = norm(row['path'])
        if path in manifest['external_omitted']:
            need(manifest['external_omitted'][path]['raw_sha256'] == row['sha256'] and
                 manifest['external_omitted'][path]['raw_bytes'] == row['bytes'], 'Qualified hash-only actual tool identity')
        else:
            frozen('host21', row['path'], row['sha256'], row['bytes'])
    binding = obj(raw[runtime_root + 'reference-binding21.json'])
    need(binding['schema'] == 'mono21-recorded-dual-reference-binding-v1' and binding['completed'] is True and
         binding['contract_sha256'] == contract['contract_sha256'] and len(binding['cases']) == len(mapping['cases']) == len(matrix['cases']) == 21 and
         binding['dual_reference_passed'] is binding['actual_single_scope_reference_campaign_exists'] is True and
         binding['dual_reference_scope'] == 'only-existing-mono21-campaign' and binding['native_lookup2_refusals'] == 0 and
         all(binding[k] is False for k in ('previous_unrelated_dual_NONPASS_reinterpreted', 'target_executed',
             'target_numeric_comparison_performed', 'full_G6_qualified', 'new_reference_commands_executed', 'aggregate_reference_campaign_exists')),
         'Complete existing21 reference binding only')
    need(binding['source_scopes'] == [dict(name='actual_mono21', qualification_path=qkey, qualification_sha256=sha(raw[qkey]),
        host_path=manifest['roles']['host21']['root'] + '/report.json', host_sha256=sha(data('host21')),
        receipt_path=manifest['roles']['host21']['terminal'], receipt_sha256=sha(raw[manifest['roles']['host21']['terminal']]),
        original_returncode=0, totals=[21, 21, 0, 294, 464640])], 'Exact single recorded reference scope without aggregation')
    for row in binding['proof_facts']:
        frozen('capture21', row['path'], row['sha256'], row['bytes'])
    for row in binding['external_reference_tool_identities']:
        need(manifest['external_omitted'][norm(row['path'])]['raw_sha256'] == row['sha256'] and
             manifest['external_omitted'][norm(row['path'])]['raw_bytes'] == row['bytes'], 'Existing reference tool identities omitted exactly')
    reference_helper = load_module('offline_mono21_reference_helpers', bundle / 'reference_helpers.py', REFERENCE_HELPERS)
    carrier = source_module('offline_mono21_carrier', runtime_root + 'carrier.py', '6cf4f49de61cf94184578fe753272606b1ef8e0225b1444ede4c73d4c549712b')
    commands = {row['name']: row for row in host['commands']}
    need(len(commands) == 42 and [c['channels'] for c in matrix['cases']].count(1) == 9 and
         [c['channels'] for c in matrix['cases']].count(2) == 12, 'Exactly42 distinct commands and9mono/12stereo cases')
    for root, digest in (('.build/cyd-vorbis-mono-mapping-numeric-prep-01/', 'e5df77c9c0b73f327b693a9ad7f76054ccc55c9fc563107778ad4fb06dea2748'),
                         (NUMERIC_ROOT, '0f7ce1d76f5a3541fbe7f7e798fe1eca7b85d27f57e6f8ac44bdd74aa4ea0950')):
        need(sha(raw[root + 'readiness.json']) == digest, 'Both exact reviewed numeric source preparations')
        numeric_readiness = obj(raw[root + 'readiness.json'])
        need(numeric_readiness['schema'] == 'mono21-numeric-source-readiness-v1' and
             {key[len(root):] for key in raw if key.startswith(root)} == set(numeric_readiness['expected_self_files']),
             'Both complete immutable numeric source inventories')
        for row in numeric_readiness['files']:
            need(len(raw[root + row['path']]) == row['bytes'] and sha(raw[root + row['path']]) == row['sha256'],
                 'Every original/successor numeric metric/policy/helper source pin')
    saved_modules = {name: sys.modules.get(name) for name in ('pcm_metrics', 'mono_metrics', 'policy21')}
    try:
        stereo = source_module('pcm_metrics', NUMERIC_ROOT + 'pcm_metrics.py', METRICS)
        sys.modules['pcm_metrics'] = stereo
        mono = source_module('mono_metrics', NUMERIC_ROOT + 'mono_metrics.py', MONO_METRICS)
        sys.modules['mono_metrics'] = mono
        policy = source_module('policy21', NUMERIC_ROOT + 'policy21.py', POLICY)
        sys.modules['policy21'] = policy
        numeric_helper = load_module('offline_mono21_numeric_helpers', bundle / 'numeric_helpers.py', NUMERIC_HELPERS)
        need(tuple(c['id'] for c in matrix['cases']) == policy.CASE_IDS and
             [c['channels'] for c in matrix['cases']] == list(policy.CHANNELS), 'Complete21 frozen case order/actual channels')
        numeric = reports['numeric21']; measured_rows = []; binding_rows = []
        for index, (case, item, original_case, accepted, origin, source) in enumerate(zip(
                contract['model']['cases'], captured, host['cases'], qualified['cases'], mapping['cases'], matrix['cases'])):
            rid = '0-' + case['id']; folder = 'cases/' + rid + '/'
            need(original_case['id'] == accepted['id'] == rid and original_case['input'] == source and
                 original_case['source_matrix_sha256'] == sha(raw[original_root + 'matrix.json']) and
                 address(original_case['source_matrix'], 'host21') == original_root + 'matrix.json' and
                 origin['case'] == index and origin['id'] == case['id'] == source['id'] and
                 origin['original_case_fields'] == origin['selected_case_fields'] == source and origin['fields_changed'] == [] and
                 (accepted['rate'], accepted['channels'], accepted['bits']) == (case['rate'], case['channels'], 16) and
                 accepted['frames'] == case['frames'][1:] and accepted['pcm_bytes'] == case['total_pcm'] and
                 accepted['xiph_qualified'] is accepted['native_compared'] is True and accepted['native_lookup2_refusal'] is False and
                 original_case['failures'] == [], 'Every actual original raw/channel/frame classification')
            content = {}
            for kind in ('identification', 'comment', 'setup', 'audio', 'ogg'):
                value = raw[canonical_root + rel(source[kind])]; content[kind] = value
                need(sha(value) == (source['ogg_sha256'] if kind == 'ogg' else source['raw_sha256'][kind]), 'Complete source raw/carrier identity')
                for role in ('original', 'selected'):
                    fact = origin['files'][kind][role]
                    need(frozen('capture21', fact['path'], fact['sha256'], fact['bytes']) == value, 'Every original/selected raw payload unchanged')
            packets = carrier.packets(content['ogg']); offsets = source['offsets']
            need(len(packets) == 17 and [x['data'] for x in packets[:3]] == [content[k] for k in ('identification', 'comment', 'setup')] and
                 [x['data'] for x in packets[3:]] == [content['audio'][a:b] for a, b in zip(offsets, offsets[1:])] and
                 [x['eos'] for x in packets] == [False] * 16 + [True] and
                 packets[-1]['granule'] == sum(case['frames']) and data('host21', folder + 'input.ogg') == content['ogg'],
                 'All complete17-packet carriers/CRC/order/EOS and exact42 decoder inputs')
            metrics = mono if case['channels'] == 1 else stereo
            pcms, details, references = {}, {}, {}
            for decoder in policy.DECODERS:
                name = folder + 'decode-' + decoder; command = commands[name]
                child_raw = data('host21', command['receipt']); need(sha(child_raw) == command['sha256'], 'Actual child receipt identity')
                child = obj(child_raw); receipt(child, 0, 'host21'); argv = child['argv']
                need(child['runner_sha256'] == '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e' and
                     child['executable_sha256'] == host['tools'][argv[0]] and argv[argv.index('-c:a') + 1] == decoder and
                     '-ar' not in argv and '-ac' not in argv and '-xerror' in argv and argv[argv.index('-err_detect') + 1] == 'explode' and
                     address(argv[argv.index('-i') + 1], 'host21') == manifest['roles']['host21']['root'] + '/' + folder + 'input.ogg' and
                     not data('host21', name + '.stderr.log'), 'All42 actual strict successful decoder commands')
                pcm, evidence = reference_helper.decoded_pcm(data('host21', folder + decoder + '.wav'), data('host21', name + '.stdout.log'),
                    case['rate'], case['channels'], case['frames'], case['modes'])
                need(evidence == original_case['decoded'][decoder] and len(pcm) == len(item['pcm']) == case['total_pcm'],
                     'All42 untrimmed WAV/framemd5/actual-channel/transition evidence streams')
                pcms[decoder], details[decoder] = pcm, evidence
                references[decoder] = dict(comparison=metrics.compare(pcm, item['pcm'], case['pcm']),
                    alignment_diagnostic=metrics.alignment(pcm, item['pcm'], 8),
                    reference_transition_nonzero=numeric_helper.transition_counts(pcm, case, item['packet_offsets']),
                    target_transition_nonzero=numeric_helper.transition_counts(item['pcm'], case, item['packet_offsets']))
            cross = metrics.compare(pcms['vorbis'], pcms['libvorbis'], case['pcm'])
            maximum = policy.whole(cross, case['channels'])['max_abs_error']
            need(maximum == original_case['cross_reference_max_abs_error'] == accepted['cross_reference_max_abs_error'] and maximum <= 2 and
                 {k: v for k, v in accepted.items() if k not in ('id', 'xiph_qualified', 'native_compared', 'native_lookup2_refusal', 'cross_reference_max_abs_error')} == details['libvorbis'],
                 'Complete dual-reference crosscheck and every qualified Xiph field')
            binding_rows.append(dict(case=index, id=case['id'], original_group='mono21', original_reference_id=rid,
                qualification_sha256=sha(raw[qkey]), original_host_report_sha256=sha(data('host21')),
                original_host_receipt_sha256=sha(raw[manifest['roles']['host21']['terminal']]), original_host_returncode=0,
                raw_sha256=case['raw_sha256'], frames=case['frames'], pcm_bytes=case['total_pcm'], rate=case['rate'], channels=case['channels'],
                reference_pcm_sha256=details['libvorbis']['pcm_sha256'], reference_wav_sha256=details['libvorbis']['wav_sha256'],
                actual_reference_decoders=details, cross_reference_max_abs_error=maximum, native_compared=True, native_lookup2_refusal=False, xiph_qualified_existing=True))
            measured_rows.append(dict(case=index, id=case['id'], rate=case['rate'], channels=case['channels'], bits=16,
                frames=case['frames'], packet_bytes=case['pcm'], pcm_bytes=len(item['pcm']), packet_offsets=item['packet_offsets'], reference_id=rid,
                references=references, original_reference_cross_comparison=cross, original_reference_metadata=details))
        need(binding_rows == binding['cases'] and measured_rows == numeric['cases'], 'Every existing binding and42 complete measured target comparisons replayed exactly')
        chosen, bounded = policy.bounded_policy(measured_rows, 2)
        need(numeric['measurement_completed'] is numeric['actual_reference_compared'] is numeric['target_platform_verified'] is True and
             (numeric['complete_target_cases'], numeric['complete_target_packets'], numeric['complete_target_PCM_bytes'], numeric['complete_reference_streams_verified'], numeric['complete_target_reference_comparisons']) ==
             (21, 294, 464640, 42, 42) and numeric['policy'] == chosen and numeric['bounded_by_reference'] == chosen['bounded_by_reference'] and
             numeric['bounded_corpus_pcm_qualified'] is bounded and numeric['result'] == ('BOUNDED_CORPUS_PCM_QUALIFIED' if bounded else 'BOUNDED_CORPUS_PCM_REJECTED') and
             manifest['roles']['numeric21']['expected_outer_exit'] == (0 if bounded else 1), 'Fixed2-LSB policy measured completely; actual NONPASS preserved')
        need(numeric['original_dual_reference_passed'] is numeric['no_predeclared_metamorphic_groups'] is True and
             numeric['original_dual_reference_scope'] == 'only-existing-mono21-campaign' and numeric['original_reference_failures'] == [] and
             numeric['original_reference_report_sha256'] == sha(data('host21')) and numeric['target_report_sha256'] == sha(data('capture21')) and
             numeric['target_terminal_sha256'] == sha(raw[manifest['roles']['capture21']['terminal']]) and
             numeric['actual_runtime_preparation_sha256'] == sha(raw[runtime_root + 'preparation.json']) and
             numeric['policy_predeclared_max_abs_error'] == 2 and numeric['policy_requires_both_existing_references'] is True and
             all(numeric[k] is False for k in ('passed', 'numeric_reference_qualified', 'format_corpus_qualified', 'format_conformance_qualified',
                 'full_G6_qualified', 'physical_device', 'production_radio_integration', 'previous_unrelated_NONPASS_reinterpreted', 'vendor_comparison_available')),
             'Actual numerical scope/pins and unrelated historical NONPASS remain unchanged')
    finally:
        for name, previous in saved_modules.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous
    for receipt_key in manifest['plan']['extra_receipts']:
        need(sha(raw[receipt_key]) == manifest['plan']['extra_receipt_pins'][receipt_key], 'Exact actual extra receipt identity')
        receipt(obj(raw[receipt_key]), 0)
    for name, count in (('cyd-vorbis-mono-mapping-controls-01-command.json', 30),
                        ('cyd-vorbis-mono-mapping-numeric-controls-01-command.json', 29),
                        ('cyd-vorbis-mono-mapping-numeric-controls-02-command.json', 39)):
        actual = obj(raw['.build/' + name]); stderr = next(path for path in actual['logs'] if path.endswith('stderr.log'))
        need(re.search(rb'Ran ' + str(count).encode() + rb' tests\b.*\bOK\b', frozen(None, stderr, actual['logs'][stderr]['sha256']), re.S),
             'Exact recorded control-count/OK actual terminal0; controls are not rerun')
    for name in ('construction01', 'readback02'):
        old = obj(raw['.build/cyd-vorbis-mono-mapping-prep-01/' + name + '.command.json'])
        need(old['schema'] == 'pure-mono-mapping-command-v1' and old['returncode'] == 0 and
             old['timed_out'] is old['interrupted'] is False and old['source_before'] == old['source_after'],
             'Original finite construction/readback history remains recorded, including prior failed readback')
        for stream in ('stdout', 'stderr'):
            row = old[stream]; frozen(None, row['path'], row['sha256'], row['bytes'])
    need('.build/cyd-vorbis-mono-mapping-prep-01/readback01.failure.json' in raw,
         'Original failed construction readback retained without reclassification')
    checkpoint = manifest['plan']['checkpoint']
    need(files[checkpoint['path']]['stored'] == 'CHECKPOINT.md' and sha(raw[checkpoint['path']]) == checkpoint['sha256'], 'Exact root factual checkpoint')
    need(manifest['plan']['prior8_floor0_wide_record_only_not_replayed'] is True, 'Unchanged record-only prior campaigns')
    dep.current()
    return dict(verified=True, cases=21, mono_cases=9, stereo_cases=12, packets=294, PCM_bytes=464640,
        protocol_events=654, case_mask=2097151, protocol_controls_recorded=30, original_numeric_controls_recorded=29, successor_numeric_controls_recorded=39, reference_children=42,
        complete_target_reference_comparisons=42, metric_bound=2, bounded_by_reference=chosen['bounded_by_reference'],
        bounded_corpus_pcm_qualified=bounded, input_rejection_history_preserved=True, actual_numeric_NONPASS_preserved=not bounded,
        max_abs_errors_by_reference={decoder: [policy.whole(row['references'][decoder]['comparison'], row['channels'])['max_abs_error']
            for row in measured_rows] for decoder in ('vorbis', 'libvorbis')},
        prior_campaigns_replayed=False, full_G6_qualified=False, physical_device=False, production_firmware=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--repository', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle, args.repository)))
