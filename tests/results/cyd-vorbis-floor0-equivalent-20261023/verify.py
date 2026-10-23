"""Read-only offline31 evidence verifier; never run a codec, process or SDK."""
import argparse
import gzip
import importlib.util
import json
import ntpath
from pathlib import Path, PureWindowsPath
import re
import struct
import sys
from dependency import Dependency, MANIFEST_SHA, VERIFY_SHA, need, norm, obj, rel, sha

sys.dont_write_bytecode = True
PREFIX = 'CYD_VORBIS_CHECKED_CORPUS_'
COMMANDS = ['sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after']
METRICS = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
POLICY25 = '32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6'


def load_module(name, path, expected):
    need(sha(path.read_bytes()) == expected, 'Unreviewed archived module')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(bundle, repository):
    bundle, repository = bundle.resolve(), repository.resolve()
    manifest = obj((bundle / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'cyd-floor0-equivalent31-checkpoint-v1' and
         set(manifest['plan']['roles']) == {'capture31', 'numeric31', 'host-new12'}, 'Focused31 archive schema/roles')
    need(manifest['dependency_archive'] == dict(path='tests/results/cyd-vorbis-map2-20261020',
        manifest_sha256=MANIFEST_SHA, required=True, standalone=False), 'Explicit unchanged CYD dependency required')
    dep = Dependency(repository)
    dep_verify = load_module('floor0_pinned_committed_cyd_verifier', dep.root / 'verify.py', VERIFY_SHA)
    need(dep_verify.verify(dep.root)['verified'] is True, 'Committed dependency failed its pinned verifier')
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
                need(len(header) == 64 and header[:4] == b'\x7fELF' and struct.unpack_from('<H', header, 18)[0] == 94,
                     'Actual Xtensa ELF64 metadata required')
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
    for role in ('capture31', 'numeric31', 'host-new12'):
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
                need(role == 'numeric31' and omitted.get('external_numeric_input') is True and
                     omitted['raw_sha256'] == row['sha256'] and omitted['raw_bytes'] == row['bytes'] and
                     PureWindowsPath(external).name in {'ffmpeg.exe', 'python.exe'}, 'Explicit hash-only external numeric tool metadata')
                continue
            frozen(role, path, row['sha256'], row.get('bytes'))
        for path, digest in report.get('tools', {}).items():
            need(manifest['external_omitted'][norm(path)]['raw_sha256'] == digest, 'Tool/archive hash omission metadata')
    target = reports['capture31']
    need(target['result'] == 'CHECKED_CORPUS_PCM_CAPTURED' and target['completed'] is True and target['checked_decode_completed'] is True and
         target['target_capture_completed'] is True and target['independent_reference_compared'] is False and
         target['numeric_reference_qualified'] is False and target['full_G6_qualified'] is False, 'Capture scope remains bounded')
    terminal = obj(raw[manifest['roles']['capture31']['terminal']])
    need(terminal['report_sha256'] == sha(data('capture31')) and terminal['entrypoint_sha256'] ==
         'dc3ceac1c9beebadc0e1afd2fa320a925e7c8c2a830cd9a5a941ffd401f7de86' and
         (terminal['session_id'], terminal['terminal_chunk_id'], terminal['exit_code']) == (69878, 'd6f0b8', 0), 'Actual direct capture terminal binding')
    need([row['name'] for row in target['commands']] == COMMANDS, 'All9 actual target commands')
    for command in target['commands']:
        need(command['state'] == 'complete' and type(command['exit_status']) is int and command['exit_status'] == 0 and
             command['timed_out'] is False and command['interrupted'] is False and type(command['pid']) is int and command['pid'] > 0,
             'Actual non-interrupted/non-timeout owned command')
        for stream in ('stdout', 'stderr'):
            need(sha(data('capture31', command['name'] + '.' + stream + '.log')) == command[stream + '_sha256'], 'Actual target command stream')
    for field in ('build_outputs', 'variant_sources'):
        for path, digest in target.get(field, {}).items():
            need(files[manifest['roles']['capture31']['root'] + '/' + norm(path)]['raw_sha256'] == digest, 'Actual build/variant metadata')
    macros = data('capture31', 'setup-macros.stdout.log').decode().replace('\r\n', '\n')
    need(not re.search(r'^#define (LIMIT_TO_64kHz|CONFIG_FREERTOS_UNICORE)\b', macros, re.M) and
         re.search(r'^#define CONFIG_IDF_TARGET_ESP32 1$', macros, re.M) and
         data('capture31', 'sdk-head.stdout.log').strip() == b'7101770dc6db2667b3c477cc31365dd1acd6db4e' and
         not data('capture31', 'sdk-clean.stdout.log').strip(), 'Actual SDK/Xtensa/SMP profile')
    contract = record('capture31', 'sources/corpus/contract.json')
    need(sha(data('capture31', 'sources/corpus/contract.json')) == 'ef8823f169d08b98fe5586221a7ab9a64904373e3be4f212631a58d1fcdc24ff' and
         sha(data('capture31', 'sources/project/main/data.h')) == '433ffdc59206485e0650c9fbbb0796bf053725c9dacf0cbdd6c3ebf826318cdf', 'Exact31 contract/header')
    def source_module(name, key, expected=None):
        need(key in raw and files[key].get('encoding') == 'raw', 'Retained plain module source required')
        return load_module(name, bundle / files[key]['stored'], expected or sha(raw[key]))
    class ArchivedPath(PureWindowsPath):
        def resolve(self): return type(self)(ntpath.normpath(str(self)))
        def read_bytes(self): return raw[address(self.resolve())]
        def is_file(self):
            try: return address(self.resolve()) in raw
            except (RuntimeError, KeyError): return False
        def rglob(self, pattern):
            need(pattern == '*', 'Bounded archived inventory only')
            prefix = norm(self.resolve()).rstrip('/') + '/'
            need(prefix.startswith(base + '/'), 'Archived glob boundary')
            key_prefix = prefix[len(base) + 1:]
            return iter(type(self)(base + '/' + key) for key in sorted(raw) if key.startswith(key_prefix))
    protocol_key = manifest['roles']['capture31']['root'] + '/sources/helpers/protocol.py'
    protocol = source_module('offline_cyd_checked31_protocol', protocol_key, '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e')
    protocol.Path = ArchivedPath  # Explicit read-only original-path virtualization; no live fallback.
    log = (data('capture31', 'qemu.stdout.log') + b'\n' + data('capture31', 'qemu.stderr.log')).decode(errors='replace')
    qemu = target['commands'][6]
    observed = protocol.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
        interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == target['observed'] and (observed['cases'], observed['decoded_packets'], observed['pcm'], observed['protocol_lines'], observed['case_mask']) ==
         (31, 434, 738560, 964, 2147483647) and len(captured) == len(target['observed_pcm']) == 31, 'Strict full31 protocol')
    for item, row in zip(captured, target['observed_pcm']):
        need(item['pcm'] == data('capture31', row['path']) and item['sha256'] == row['sha256'] and
             (item['case'], item['id'], item['packet_offsets']) == (row['case'], row['id'], row['packet_offsets']), 'Every persisted PCM byte/boundary')
    old25 = reports['old25']
    need(contract['model']['cases'][:25] == record('old25', 'sources/corpus/contract.json')['model']['cases'], 'Original25 model prefix')
    for current, old in zip(captured[:25], old25['observed_pcm']):
        need(current['pcm'] == data('old25', old['path']) and current['sha256'] == old['sha256'], 'All25 original PCM bytes unchanged')
    events = [line for line in log.splitlines() if line.startswith(PREFIX)]
    old_events = [line for line in (data('old25', 'qemu.stdout.log') + b'\n' + data('old25', 'qemu.stderr.log')).decode().splitlines() if line.startswith(PREFIX)]
    need(events[2:2 + 775] == old_events[2:2 + 775], 'All775 original case events unchanged')
    witness_key = '.build/cyd-vorbis-floor0-representation-target-witness-01.json'
    root_witness = obj(raw[witness_key])
    need(root_witness['capture_report_sha256'] == sha(data('capture31')) and root_witness['old25_report_sha256'] == sha(data('old25')) and
         root_witness['all25_original_PCM_bytes_equal'] is True and root_witness['all775_original_case_events_equal'] is True and
         root_witness['all6_target_PCM_equal'] is True, 'Actual root prefix/floor witness metadata')
    for index, row in enumerate(root_witness['six_floor0_pairs']):
        first, second = captured[19 + index], captured[25 + index]
        need(first['pcm'] == second['pcm'] and row == dict(original_case=19 + index, equivalent_case=25 + index,
            actual_target_PCM_equal=True, bytes=len(first['pcm']), original_sha256=sha(first['pcm']), equivalent_sha256=sha(second['pcm'])), 'Six actual complete target floor pairs')
    numeric = reports['numeric31']
    need(numeric['result'] == 'BOUNDED_CORPUS_PCM_REJECTED' and numeric['measurement_completed'] is True and numeric['actual_reference_compared'] is True and
         numeric['bounded_corpus_pcm_qualified'] is False and len(numeric['cases']) == 31 and
         all(numeric[flag] is False for flag in ('passed', 'numeric_reference_qualified', 'format_conformance_qualified', 'format_corpus_qualified',
             'full_G6_qualified', 'physical_device', 'production_radio_integration')), 'Full31 numerical NONPASS preserved')
    numeric_root = '.build/cyd-vorbis-format-expanded31-numeric-prep-01/'
    saved = {name: sys.modules.get(name) for name in ('pcm_metrics', 'policy25', 'policy31', 'reference31')}
    try:
        metrics = source_module('pcm_metrics', numeric_root + 'pcm_metrics.py', METRICS); sys.modules['pcm_metrics'] = metrics
        policy25 = source_module('policy25', numeric_root + 'policy25.py', POLICY25); sys.modules['policy25'] = policy25
        policy31 = source_module('policy31', numeric_root + 'policy31.py', 'da5553823f588e7a7d9adb82d53044a30c2de6eda696d9e8af1c6848a912e9c7'); sys.modules['policy31'] = policy31
        reference31 = source_module('reference31', numeric_root + 'reference31.py', 'd136aa4d3fd0d7505195efa8de6f1fe0f6501ea4a874c6616e181311256e75d3'); sys.modules['reference31'] = reference31
        adapter = source_module('offline_numeric31_pure_helpers', numeric_root + 'compare_capture31.py', '495d1e3ad94f72a624b5b3985d1a694ac3297ccdea1fd138c259ff62c6195d36')
        reference31.Path = ArchivedPath
        class ArchivedInputs:
            def read(self, role, path, expected=None, size=None):
                value = raw[address(path)]
                need(expected is None or sha(value) == expected, 'Archived reference identity: ' + role)
                need(size is None or len(value) == size, 'Archived reference size: ' + role)
                return value
        binding = record('capture31', 'sources/reference/reference-binding31.json')
        need(binding['source_scopes'] == numeric['source_reference_scopes'] and len(binding['source_scopes']) == 3, 'Three distinct actual reference scopes')
        xiph_all, target_all = {}, {}
        for index, (case, item, measured, bound) in enumerate(zip(contract['model']['cases'], captured, numeric['cases'], binding['cases'])):
            host_role = 'host-new12' if index >= 25 else 'host-new8' if bound['original_group'] == 'newbooks8' else 'host-old17'
            host = reports[host_role]
            source = next(row for row in host['cases'] if row['id'] == bound['original_reference_id'])
            need(bound['id'] == case['id'] and bound['raw_sha256'] == case['raw_sha256'], 'Exact raw scoped reference model')
            for kind in ('identification', 'setup', 'audio'):
                origin = PureWindowsPath(source['source_matrix']).parent / source['input'][kind]
                need(sha(raw[address(origin, host_role)]) == case['raw_sha256'][kind], 'Actual independent raw packet source')
            folder = ArchivedPath(base + '/' + manifest['roles'][host_role]['root'])
            state = dict(scope=next(scope for scope in binding['source_scopes'] if scope['qualification_sha256'] == bound['qualification_sha256']),
                host_root=folder, host=host, commands={row['name']: row for row in host['commands']})
            _, streams = reference31.command(ArchivedInputs(), state, source, 'libvorbis')
            declared = source['decoded']['libvorbis']
            wav = data(host_role, 'cases/' + source['id'] + '/libvorbis.wav')
            need(sha(wav) == declared['wav_sha256'], 'Actual Xiph WAV identity')
            reference = adapter.wav_pcm(wav, case['rate'], sum(case['frames']))
            adapter.frame_checksums(streams['stdout'], reference, case['rate'], case['frames'])
            need(sha(reference) == declared['pcm_sha256'] == bound['reference_pcm_sha256'] and len(reference) == case['total_pcm'], 'Complete Xiph PCM binding')
            need(measured['case'] == index and measured['id'] == case['id'] and measured['packet_offsets'] == item['packet_offsets'] and
                 measured['comparison'] == metrics.compare(reference, item['pcm'], case['pcm']) and measured['alignment'] == metrics.alignment(reference, item['pcm'], 8),
                 'All31 actual per-sample/channel/packet metrics and diagnostics')
            for label, value in (('reference_transition_channel_nonzero', reference), ('target_transition_channel_nonzero', item['pcm'])):
                counts = {kind: [0, 0] for kind in ('SS', 'SL', 'LS', 'LL')}
                for packet in range(1, 14):
                    kind = 'SL'[case['modes'][packet - 1]] + 'SL'[case['modes'][packet]]
                    first, stop = item['packet_offsets'][packet:packet + 2]
                    for channel in (0, 1):
                        counts[kind][channel] += sum(value[pos:pos + 2] != b'\0\0' for pos in range(first + channel * 2, stop, 4))
                need(measured[label] == counts, 'Every transition/channel nonzero count')
            xiph_all[case['id']], target_all[case['id']] = reference, item['pcm']
        old_numeric = obj(raw[dep.manifest['roles']['numeric-expanded25']['root'] + '/report.json'])
        declarations = [dict(decoder='libvorbis', kind=row['kind'], cases=row['cases'], passed=True) for row in old_numeric['metamorphic_relations']['xiph']]
        floors = [[row['exact_original_floor0_relation']['original_id'], row['id']] for row in binding['cases'][25:]]
        relations = dict(xiph=policy31.relations14(xiph_all, declarations, floors), target=policy31.relations14(target_all, declarations, floors))
        need(relations == numeric['metamorphic_relations'] and [i for i, row in enumerate(relations['target']) if not row['expected_relation_observed']] == [4, 5], 'Exact14 relations; only wide2 fail')
        policy, passed = policy31.bounded_policy31(numeric['cases'], relations, 2)
        books = {key: value[:8] for key, value in relations.items()}
        sub_policy, sub_passed = policy25.bounded_policy25(numeric['cases'][:25], books, 2)
        subgroup = numeric['declared_subgroup_old25']
        need(policy == numeric['policy'] and passed is numeric['bounded_corpus_pcm_qualified'] is False and sub_policy == subgroup['policy'] and
             sub_passed is subgroup['bounded_subgroup_pcm_qualified'] is False and subgroup['does_not_override_full31'] is True, 'Unchanged bound2/full31/old25 policies')
        need(numeric['preserved_native_crosschecks'] == old_numeric['preserved_native_crosschecks'], 'All7 unchanged native crosschecks')
        host12_scope = binding['source_scopes'][2]
        q12 = obj(raw[address(base + '/' + host12_scope['qualification_path'])])
        state12 = dict(scope=host12_scope, host_root=ArchivedPath(base + '/' + manifest['roles']['host-new12']['root']),
            host=reports['host-new12'], qualified=q12, commands={row['name']: row for row in reports['host-new12']['commands']})
        checked12 = reference31.full_new12(ArchivedInputs(), state12, lambda role, path, digest, size=None: frozen('capture31', path, digest, size),
            adapter.wav_pcm, adapter.frame_checksums, sha)
        need(checked12 == numeric['full12_reference_recheck'] and q12['completed'] is True and q12['dual_reference_qualified'] is False and q12['xiph_cases'] == 12,
             'Actual full12 raw/qualification/24children/WAV/framemd5/six historical relations')
        qualifier = source_module('offline_full12_qualification_pure_PCM_reader', '.build/cyd-vorbis-floor0-equivalent-qualification-prep-01/qualify.py',
            '94c1f6e460a66a2f5ee013403986355c49eba60dc412555986ad275b6ff614db')
        for host_case, accepted in zip(reports['host-new12']['cases'], q12['cases']):
            _, streams = reference31.command(ArchivedInputs(), state12, host_case, 'libvorbis')
            wav = data('host-new12', 'cases/' + host_case['id'] + '/libvorbis.wav')
            _, evidence = qualifier.pcm_evidence(wav, streams['stdout'], host_case['input']['expected_packet_frames'])
            need(evidence == host_case['decoded']['libvorbis'] and all(accepted[key] == value for key, value in evidence.items()),
                 'All12 complete actual qualification PCM/hash/transition evidence')
    finally:
        for name, old in saved.items():
            if old is None: sys.modules.pop(name, None)
            else: sys.modules[name] = old
    source_root = '.build/cyd-vorbis-floor0-equivalent-prep-01/'
    witness = source_module('offline_floor0_exact_raw_Q24_witness', source_root + 'witness.py', 'c40824c5d157fbcfd0b6a6041f4ffa77553b16a5327a12e90d22d42ea2662fab')
    witness.Path = ArchivedPath
    generated = ArchivedPath(base + '/.build/cyd-vorbis-floor0-equivalent-generated-01')
    witnessed = witness.witness(ArchivedPath(base), generated)
    need(witnessed == obj(raw['.build/cyd-vorbis-floor0-equivalent-witness-01/report.json']), 'All6 original/equivalent raw/Q24/CRC controls')
    for receipt_key in manifest['plan']['extra_receipts']:
        need(sha(raw[receipt_key]) == manifest['plan']['extra_receipt_pins'][receipt_key], 'Exact actual root extra receipt bytes')
        receipt(obj(raw[receipt_key]), 0)
    checkpoint = manifest['plan']['checkpoint']
    need(files[checkpoint['path']]['stored'] == 'CHECKPOINT.md' and sha(raw[checkpoint['path']]) == checkpoint['sha256'],
         'Exact root checkpoint is frozen and covered by the generated manifest')
    generation_key = '.build/cyd-vorbis-floor0-equivalent-generation-01-command.json'
    generation = obj(raw[generation_key])
    stdout_key = next(path for path in generation['logs'] if path.endswith('.stdout.log'))
    generated_result = obj(raw[address(stdout_key)])
    generated_manifest_key = '.build/cyd-vorbis-floor0-equivalent-generated-01/manifest.json'
    need((generated_result['additions'], generated_result['comparison_cases'], generated_result['files']) == (6, 12, 78) and
         generated_result['manifest_sha256'] == sha(raw[generated_manifest_key]), 'Actual generation78 result/manifest binding')
    prep_readme = raw['.build/cyd-vorbis-format-expanded31-prep-01/README.md']
    runtime = obj(raw['.build/cyd-vorbis-format-expanded31-runtime-01/preparation.json'])
    need(b'734464' in prep_readme and runtime['counts']['expected_pcm_bytes'] == 738560 and
         runtime['original25_model_prefix_unchanged'] is True, 'Historical README typo retained; actual model738560 authoritative')
    curve_key = '.build/cyd-vorbis-floor0-curve-run-01/report.json'
    curve = obj(raw[curve_key])
    need(sha(raw[curve_key]) == '76c5c726c076b0f75464d627d850746b838c02c852cc827de23cb34bb1f77be7' and
         curve['result'] == 'OWN_PUBLIC_FLOOR0_FORMULA_DIAGNOSTIC_COMPLETED' and
         (curve['case_count'], curve['packets'], curve['channel_packets'], curve['active_bin_observations'], curve['positive_db_observations']) ==
         (6, 84, 168, 2688, 147) and curve['controls']['groups'] == 5 and curve['math_computed'] is True and
         all(curve[key] is False for key in ('actual_decoder_or_reference_executed', 'PCM_computed', 'public_Tremor_integer_path_evaluated',
             'vendor_behavior_attributed', 'overflow_inferred_from_PCM', 'numeric_qualified', 'full_G6_qualified', 'production_qualified', 'physical_qualified')),
         'Pure own-formula diagnostic retained without backend/PCM attribution')
    dep.current()
    return dict(verified=True, files=len(files), cases=31, packets=434, PCM_bytes=738560, protocol_events=964,
        target_floor0_equal_pairs=6, original25_PCM_and775_case_events_unchanged=True,
        full31_bounded_PCM_qualified=False, source_dual_reference_passed=False,
        full_G6_qualified=False, physical_device=False, production_firmware=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--repository', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle, args.repository)))
