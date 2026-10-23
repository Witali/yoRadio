"""Measure complete checked-only31 PCM against Xiph; no codec/process execution."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys
import wave
from pcm_metrics import alignment, compare, need
from policy25 import relations8, bounded_policy25
from policy31 import CASE_IDS, FLOOR_PAIRS, relations14, bounded_policy31
from reference31 import command as reference_command, full_new12

sys.dont_write_bytecode = True
RUNNER = 'dc3ceac1c9beebadc0e1afd2fa320a925e7c8c2a830cd9a5a941ffd401f7de86'
PROTOCOL = '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'
CONTRACT = '419efac93fc69c65dc162f6b45017b0eb81a276f8de95d50d6f9d1bd06e5aa02'
CONTRACT_FILE = 'ef8823f169d08b98fe5586221a7ab9a64904373e3be4f212631a58d1fcdc24ff'
DATA_HEADER = '433ffdc59206485e0650c9fbbb0796bf053725c9dacf0cbdd6c3ebf826318cdf'
CALLER = '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065'
CASE_HEADER = '91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3'
SOURCE_MAP = 'f81cfc76044f7d4d1ad9949b8376945afd82815d001b9a4af1672acbb63f0c16'
BINDING = 'a13275e2663a428895b326fbfbf9d38458f23b0eeee0811406f39e6dab3874b5'
BINDING_HELPER = 'fce060219d914542c570b7777b1cfc1f77303f8b5d4d914f23fc5153d20a751f'
METRICS = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
POLICY25 = '32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6'
POLICY31 = 'da5553823f588e7a7d9adb82d53044a30c2de6eda696d9e8af1c6848a912e9c7'
REFERENCE31 = 'd136aa4d3fd0d7505195efa8de6f1fe0f6501ea4a874c6616e181311256e75d3'
TARGET_REPORT = '6f7f346df8c2185776fa8727977e363c284f8bdc459ef90c5ed28affc3b6d81d'
TARGET_TERMINAL = '0fa1dee0e6140c4d58280ec5985071a5e59a8479c897d857950ef35f4917a61c'
SCOPE_PINS = [{'qualification_path': '.build/cyd-vorbis-format-corpus-qualified-01/qualification.json', 'qualification_sha256': 'd269d71ab02568fcb549c5abf39e4daf8ffcd082b1ede3c259351615768e02b0', 'host_path': '.build/cyd-vorbis-format-corpus-host-01/report.json', 'host_sha256': 'eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29', 'receipt_path': '.build/cyd-vorbis-format-corpus-host-01-command.json', 'receipt_sha256': '799bb892e5b12e0ccc13fc02607aefe49527f51568d0aecfe8a98ac88c492773', 'original_returncode': 1, 'totals': [17, 7, 10, 238, 398080]}, {'qualification_path': '.build/cyd-vorbis-map2-regression-qualified-01/qualification.json', 'qualification_sha256': 'bb78d2478d6e2a191202098443f5d224cda37fe7c44b33052de005ce10662bc4', 'host_path': '.build/cyd-vorbis-map2-regression-host-01/report.json', 'host_sha256': '5701c50e49118123e059c2a48a152f1fdd2f9def3bffb84053759b51c9a8df88', 'receipt_path': '.build/cyd-vorbis-map2-regression-host-01-command.json', 'receipt_sha256': '829899ce49f473962c2abc838fb9a1c6a6be14cf1ec007e66c464f7cff09bc2f', 'original_returncode': 1, 'totals': [8, 0, 8, 112, 225280]}, {'name': 'new12', 'qualification_path': '.build/cyd-vorbis-floor0-equivalent-qualified-01/qualification.json', 'qualification_sha256': '29ca7992d6deed8766f61ec5fc79ac3b5108bf7ec0dd12d1732df514af65881c', 'host_path': '.build/cyd-vorbis-floor0-equivalent-host-01/report.json', 'host_sha256': '804a46f29eed98ab6e3c71a5aff79d11546d1efd87dddea8f6fad7f7cee2ce17', 'receipt_path': '.build/cyd-vorbis-floor0-equivalent-host-01-command.json', 'receipt_sha256': '3606acc8058a6147b3eedf86f61683bca1902b41fe2b1f8479281fbfa95a7e54', 'original_returncode': 1, 'full_reference_cases': 12, 'selected_cases': 6, 'actual_child_commands': 24, 'exact_equivalence_relations': [{'original_id': 'floor0-even6-r0-s64-l256', 'historical_id': '1-floor0-even6-r0-s64-l256', 'equivalent_id': 'floor0-even6-r0-minp1-s64-l256', 'historical_pcm_sha256': '08b3201644908b3cea1dd3b87379caf6da2278415f3ef2bc42de719ef2e43186', 'historical_pcm_bytes': 3968, 'exact_complete_PCM_equal': True}, {'original_id': 'floor0-even6-r0-s256-l2048', 'historical_id': '1-floor0-even6-r0-s256-l2048', 'equivalent_id': 'floor0-even6-r0-minp1-s256-l2048', 'historical_pcm_sha256': '5ce3336533c5b1f34440f24b0886205a44cb12754824d0e88972255ff4c0fce6', 'historical_pcm_bytes': 28160, 'exact_complete_PCM_equal': True}, {'original_id': 'floor0-even6-r0-s64-l2048', 'historical_id': '1-floor0-even6-r0-s64-l2048', 'equivalent_id': 'floor0-even6-r0-minp1-s64-l2048', 'historical_pcm_sha256': '789eb23176004a3ad43df44763489f2966620daaa445c0ad2da44902579c7a47', 'historical_pcm_bytes': 25472, 'exact_complete_PCM_equal': True}, {'original_id': 'floor0-odd5-r0-s64-l256', 'historical_id': '1-floor0-odd5-r0-s64-l256', 'equivalent_id': 'floor0-odd5-r0-minp1-s64-l256', 'historical_pcm_sha256': '6ad9e4122a687ffb9ec9c2beb09077178454cb54a6f5b0b7cf1be900aa2ec34d', 'historical_pcm_bytes': 3968, 'exact_complete_PCM_equal': True}, {'original_id': 'floor0-odd5-r0-s256-l2048', 'historical_id': '1-floor0-odd5-r0-s256-l2048', 'equivalent_id': 'floor0-odd5-r0-minp1-s256-l2048', 'historical_pcm_sha256': 'da30728f0e659f672e292af2a66b3941731cf8f4cbbffe36cb442119b5f56d05', 'historical_pcm_bytes': 28160, 'exact_complete_PCM_equal': True}, {'original_id': 'floor0-odd5-r0-s64-l2048', 'historical_id': '1-floor0-odd5-r0-s64-l2048', 'equivalent_id': 'floor0-odd5-r0-minp1-s64-l2048', 'historical_pcm_sha256': 'e5a2972a9736e16cdfa06a76a1ca55b4aee2d1a7be6de2eb7fbe68b500c8a2d8', 'historical_pcm_bytes': 25472, 'exact_complete_PCM_equal': True}]}]
COMMANDS = ('sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    path = PurePosixPath(str(value).replace('\\', '/'))
    need(str(value) and not path.is_absolute() and '..' not in path.parts and ':' not in str(path), 'Unsafe relative input path')
    return path.as_posix()


class Inputs:
    def __init__(self):
        self.rows = {}

    def read(self, role, path, expected=None, size=None):
        path = Path(path).resolve()
        data = path.read_bytes()
        digest = sha(data)
        need(expected is None or digest == expected, 'Input identity mismatch: ' + role)
        need(size is None or len(data) == size, 'Input size mismatch: ' + role)
        row = dict(path=str(path), bytes=len(data), sha256=digest)
        need(role not in self.rows or self.rows[role] == row, 'Role input changed: ' + role)
        self.rows[role] = row
        return data

    def current(self):
        for role, row in self.rows.items():
            data = Path(row['path']).read_bytes()
            need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Input changed during comparison: ' + role)


def complete_capture(report):
    need(report.get('result') == 'CHECKED_CORPUS_PCM_CAPTURED' and report.get('completed') is True and
         report.get('target_capture_completed') is True and report.get('checked_decode_completed') is True and
         report.get('vendor_checked_pcm_equal') is False and report.get('vendor_comparison_available') is False,
         'Only complete checked-only31 capture is supported; NONPASS/partial captures are unusable')
    need(all(report.get(key) is False for key in ('passed', 'independent_reference_compared',
         'numeric_reference_qualified', 'format_corpus_qualified', 'full_G6_qualified',
         'physical_device', 'production_radio_integration')), 'Capture scope/classification differs')
    need(tuple(row['name'] for row in report.get('commands', [])) == COMMANDS, 'All nine actual terminal commands required')
    need((report['corpus']['cases'], report['corpus']['packets'], report['corpus']['expected_pcm']) == (31, 434, 738560) and
         (report['observed']['cases'], report['observed']['decoded_packets'], report['observed']['pcm'], report['observed']['protocol_lines']) == (31, 434, 738560, 964),
         'Complete31 report facts required before any PCM')
    for row in report['commands']:
        need(row.get('state') == 'complete' and type(row.get('exit_status')) is int and row['exit_status'] == 0 and
             row.get('timed_out') is False and row.get('interrupted') is False and type(row.get('pid')) is int and
             row['pid'] > 0 and row.get('argv') and row.get('cwd'), 'Incomplete target process facts')


def wav_pcm(data, rate, frames):
    with wave.open(io.BytesIO(data), 'rb') as stream:
        need(stream.getcomptype() == 'NONE' and stream.getnchannels() == 2 and stream.getsampwidth() == 2 and
             stream.getframerate() == rate and stream.getnframes() == frames, 'Reference WAV metadata/count mismatch')
        pcm = stream.readframes(frames + 1)
    need(len(pcm) == frames * 4, 'Truncated or excess reference WAV PCM')
    return pcm


def frame_checksums(data, pcm, rate, frames):
    text = data.decode('utf-8').replace('\r\n', '\n')
    need(re.search(r'^#tb 0: 1/' + str(rate) + '$', text, re.M) and
         re.search(r'^#sample_rate 0: ' + str(rate) + '$', text, re.M) and
         '#codec_id 0: pcm_s16le' in text and re.search(r'^#channel_layout_name 0: (?:2 channels|stereo)$', text, re.M),
         'Reference framemd5 metadata mismatch')
    rows = [line for line in text.splitlines() if line and not line.startswith('#')]
    need(len(rows) == len(frames) - 1 and frames[0] == 0, 'Exact thirteen nonprimer reference frames required')
    cursor = timestamp = 0
    for line, count in zip(rows, frames[1:]):
        fields = [item.strip() for item in line.split(',')]
        need(len(fields) == 6 and [int(x) for x in fields[:5]] == [0, timestamp, timestamp, count, count * 4],
             'Reference per-packet PTS/duration/size mismatch')
        part = pcm[cursor:cursor + count * 4]
        need(hashlib.md5(part).hexdigest() == fields[5], 'Reference per-packet checksum mismatch')
        cursor += count * 4
        timestamp += count
    need(cursor == len(pcm), 'Reference packet offsets do not cover full PCM')


def run(args, result, save):
    inputs = Inputs()
    result['inputs'] = inputs.rows
    repo, target_root = args.repository.resolve(), args.target.resolve()
    inputs.read('adapter/script', Path(__file__))
    inputs.read('adapter/metrics', Path(__file__).with_name('pcm_metrics.py'), METRICS)
    inputs.read('adapter/policy25', Path(__file__).with_name('policy25.py'), POLICY25)
    inputs.read('adapter/policy31', Path(__file__).with_name('policy31.py'), POLICY31)
    inputs.read('adapter/reference31', Path(__file__).with_name('reference31.py'), REFERENCE31)
    # No reference or persisted target PCM is read before complete31 process gates.
    need(args.target_report_sha256 == TARGET_REPORT, 'Exact actual root31 report SHA required')
    target_bytes = inputs.read('target/report', target_root / 'report.json', TARGET_REPORT)
    target = json.loads(target_bytes)
    complete_capture(target)
    terminal = json.loads(inputs.read('target/outer-terminal', args.target_terminal, TARGET_TERMINAL))
    need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and
         type(terminal.get('exit_code')) is int and terminal['exit_code'] == 0 and
         type(terminal.get('session_id')) is int and terminal['session_id'] == 69878 and
         terminal.get('terminal_chunk_id') == 'd6f0b8' and
         terminal['report_sha256'] == sha(target_bytes) and terminal['entrypoint_sha256'] == RUNNER,
         'Actual reviewed31 target direct-tool terminal required; no invented argv/cwd/status')
    for row in target['commands']:
        for stream in ('stdout', 'stderr'):
            key = row['name'] + '.' + stream + '.log'
            inputs.read('target/log/' + key, target_root / key, row[stream + '_sha256'])
    for original, row in target['inputs'].items():
        inputs.read('target/input/' + relative(row['snapshot']), target_root / relative(row['snapshot']), row['sha256'], row.get('bytes'))
    def frozen(role, original, expected, size=None):
        row = target['inputs'][str(Path(original).resolve())]
        need(row['sha256'] == expected, 'Frozen original-path identity differs: ' + role)
        return inputs.read(role, target_root / relative(row['snapshot']), expected, size)
    inputs.read('target/controller', target_root / 'sources/helpers/run.py', RUNNER)
    protocol_path = target_root / 'sources/helpers/protocol.py'
    inputs.read('target/protocol', protocol_path, PROTOCOL)
    inputs.read('target/caller', target_root / 'sources/project/main/main.c', CALLER)
    inputs.read('target/descriptor-header', target_root / 'sources/project/main/corpus_case.h', CASE_HEADER)
    inputs.read('target/data-header', target_root / 'sources/project/main/data.h', DATA_HEADER)
    inputs.read('target/source-binding-helper', target_root / 'sources/helpers/reference_binding.py', BINDING_HELPER)
    mapping = json.loads(inputs.read('target/source-map', target_root / 'sources/corpus/source-map.json', SOURCE_MAP))
    binding = json.loads(inputs.read('target/source-binding', target_root / 'sources/reference/reference-binding31.json', BINDING))
    corpus = target['corpus']
    need((corpus['contract_file_sha256'], corpus['data_header_sha256'], corpus['source_map_sha256'], corpus['reference_binding_sha256']) ==
         (CONTRACT_FILE, DATA_HEADER, SOURCE_MAP, BINDING) and
         (corpus['cases'], corpus['packets'], corpus['expected_pcm']) == (31, 434, 738560), 'Exact reviewed31 corpus/header/binding facts')
    original_contract = json.loads(inputs.read('target/contract', target_root / 'sources/corpus/contract.json', CONTRACT_FILE))
    need(original_contract['contract_sha256'] == corpus['contract_sha256'] == binding['contract_sha256'] == CONTRACT, 'Reviewed31 model identity')
    need(binding['completed'] is True and binding['new_reference_commands_executed'] is False and
         binding['aggregate_reference_campaign_exists'] is False and binding['dual_reference_passed'] is False and
         len(binding['cases']) == len(mapping['cases']) == 31, 'Only coherent actual17+8+12 source binding supported')
    for item in binding['proof_facts']:
        frozen('target/proof-fact/' + item['path'], item['path'], item['sha256'], item['bytes'])
    spec = importlib.util.spec_from_file_location('pinned_expanded31_numeric_protocol', protocol_path)
    protocol = importlib.util.module_from_spec(spec); spec.loader.exec_module(protocol)
    relocated = []
    for item in original_contract['manifest_inputs']:
        row = target['inputs'][item['path']]
        need(row['sha256'] == item['sha256'], 'Frozen selected matrix binding')
        relocated.append(dict(path=str((target_root / relative(row['snapshot'])).resolve()), sha256=item['sha256']))
    contract = protocol.load_contract(relocated)
    need(contract['contract_sha256'] == CONTRACT and contract['model'] == original_contract['model'] and
         len(contract['model']['cases']) == 31 and contract['model']['total_packets'] == 434 and
         contract['model']['total_pcm'] == 738560 and contract['model']['case_mask'] == 2147483647 and
         tuple(c['id'] for c in contract['model']['cases']) == CASE_IDS, 'Exactly31 relocated cases; no partial/subset extension')
    for item in contract['source_facts']:
        inputs.read('target/relocated-source/' + item['path'], item['path'], item['sha256'], item['bytes'])
    qemu = target['commands'][6]
    log = (inputs.read('target/log/qemu.stdout.log', target_root / 'qemu.stdout.log', qemu['stdout_sha256']).decode(errors='replace') + '\n' +
           inputs.read('target/log/qemu.stderr.log', target_root / 'qemu.stderr.log', qemu['stderr_sha256']).decode(errors='replace'))
    observed = protocol.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
                                    interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == target['observed'] and (observed['cases'], observed['decoded_packets'], observed['pcm'], observed['protocol_lines']) == (31, 434, 738560, 964) and
         observed['checked_decode_completed'] is True and observed['vendor_checked_pcm_equal'] is False and
         observed['vendor_comparison_available'] is False and len(captured) == len(target['observed_pcm']) == 31,
         'Complete actual31 protocol/PCM required; partial capture cannot be salvaged')
    scopes = {}
    for scope, expected in zip(binding['source_scopes'], SCOPE_PINS):
        need(scope == expected, 'Three exact separately qualified historical scopes required')
        host_root = (repo / relative(scope['host_path'])).parent
        host = json.loads(frozen('reference/' + scope['host_path'], repo / scope['host_path'], scope['host_sha256']))
        qualified = json.loads(frozen('reference/' + scope['qualification_path'], repo / scope['qualification_path'], scope['qualification_sha256']))
        outer = json.loads(frozen('reference/' + scope['receipt_path'], repo / scope['receipt_path'], scope['receipt_sha256']))
        need(outer['status'] == 'TERMINAL' and type(outer['returncode']) is int and outer['returncode'] == 1 and
             type(outer['owned_pid']) is int and outer['owned_pid'] > 0 and host['completed'] is True and
             host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False and
             Path(outer['cwd']).resolve() == repo and outer['runner_sha256'] == host['capture_sha256'] and
             outer['executable_sha256'] == host['tools'][next(origin for origin in host['tools'] if PureWindowsPath(origin).name == 'python.exe')],
             'Preserve each actual original dual-reference NONPASS')
        if scope.get('name') == 'new12':
            need(qualified['completed'] is True and qualified['result'] == 'XIPH_EQUIVALENCE_QUALIFIED_DUAL_NONPASS' and
                 qualified['xiph_reference_qualified'] is True and qualified['dual_reference_qualified'] is False and
                 qualified['original_report_sha256'] == scope['host_sha256'] and qualified['original_outer_returncode'] == 1 and
                 (qualified['xiph_cases'], qualified['native_lookup2_refusals'], qualified['actual_child_commands_checked'], qualified['xiph_PCM_equal_pairs']) == (12,12,24,6) and
                 len(host['cases']) == len(qualified['cases']) == 12 and len(host['failures']) == 12,
                 'Exact separate full12 qualified scope; only six additions selected')
        else:
            need(qualified['completed'] is True and qualified['reference_corpus_qualified'] is True and qualified['original_dual_reference_passed'] is False and
                 qualified['original_report_sha256'] == scope['host_sha256'] and qualified['original_outer_receipt_sha256'] == scope['receipt_sha256'] and
                 [qualified[key] for key in ('xiph_cases','native_compared','native_lookup2_refusals','paired_raw_packets','expected_pcm_bytes')] == scope['totals'] and
                 len(host['cases']) == len(qualified['cases']) == scope['totals'][0] and len(host['failures']) == scope['totals'][2],
                 'Exact unchanged old17/new8 qualified scopes')
        for origin, digest in host['tools'].items():
            inputs.read('reference/tool/' + scope['host_path'] + '/' + origin, origin, digest)
        for origin, row in outer['logs'].items():
            inputs.read('reference/outer/' + scope['receipt_path'] + '/' + PureWindowsPath(origin).name,
                (repo / scope['receipt_path']).parent / PureWindowsPath(origin).name, row['sha256'], row['bytes'])
        for original, row in host['inputs'].items():
            inputs.read('reference/snapshot/' + scope['host_path'] + '/' + relative(row['snapshot']), host_root / relative(row['snapshot']), row['sha256'], row.get('bytes'))
        commands = {row['name']: row for row in host['commands']}
        need(len(commands) == len(host['commands']) == 2 * (scope['full_reference_cases'] if scope.get('name') == 'new12' else scope['totals'][0]), 'Each real host command set complete; no aggregate command invented')
        scopes[scope['qualification_sha256']] = dict(scope=scope, host_root=host_root, host=host, qualified=qualified, commands=commands)
    need(len(scopes) == len(binding['source_scopes']) == 3, 'Exact old17/new8/new12 scope count')
    full12_state = next(state for state in scopes.values() if state['scope'].get('name') == 'new12')
    full12_checked = full_new12(inputs,full12_state,frozen,wav_pcm,frame_checksums,sha)
    xiph_books, target_books, xiph_all, target_all, case_results, native, persisted_paths = {}, {}, {}, {}, [], [], set()
    for index, (case, source, origin, pcm_row, recovered) in enumerate(zip(contract['model']['cases'], binding['cases'], mapping['cases'], target['observed_pcm'], captured)):
        state = scopes[source['qualification_sha256']]
        scope, host_root, host, qualified, commands = (state[k] for k in ('scope','host_root','host','qualified','commands'))
        reference_id = source['original_reference_id']
        need(source['case'] == origin['case'] == index and source['id'] == origin['id'] == case['id'] and source['raw_sha256'] == case['raw_sha256'], 'Exact all31 selected source/order/raw identity')
        raw = [row for row in host['cases'] if row['id'] == reference_id]
        proof = [row for row in qualified['cases'] if row['id'] == reference_id]
        need(len(raw) == len(proof) == 1, 'Exactly one real source reference case')
        raw, proof = raw[0], proof[0]
        need((proof['xiph_reference_revalidated'] if scope.get('name') == 'new12' else proof['xiph_qualified']) is True and raw['input'] == origin['original_case_fields'] == origin['selected_case_fields'] and
             origin['fields_changed'] == [] and raw['source_matrix_sha256'] == source.get('reference_matrix',source['original_matrix'])['sha256'] and
             proof['frames'] == case['frames'][1:] and proof['pcm_bytes'] == source['pcm_bytes'] == case['total_pcm'] and
             proof['pcm_sha256'] == source['reference_pcm_sha256'], 'Actual per-case scoped reference/input/PCM binding')
        if scope.get('name') == 'new12':
            need(proof['native']['returncode'] == 3199971767 and proof['native']['PCM_accepted'] is False and
                 source['native_compared'] is False and source['native_lookup2_refusal'] is True, 'Exact qualified new12 native support')
        else:
            need((proof['native_compared'],proof['native_lookup2_refusal']) == (source['native_compared'],source['native_lookup2_refusal']), 'Unchanged qualified old17/new8 native support')
        for kind in ('identification','setup','audio'):
            original = origin['files'][kind]['original']
            need(host['inputs'][original['path']]['sha256'] == case['raw_sha256'][kind] == original['sha256'] == origin['files'][kind]['selected']['sha256'], 'Raw bytes differ between original/copy/model/real host')
        offsets = [0]
        for count in case['pcm']: offsets.append(offsets[-1] + count)
        path = relative(pcm_row['path'])
        need(path == f"observed-pcm/{index:02d}-{case['id']}.s16le" and pcm_row['case'] == index and
             pcm_row['id'] == case['id'] and pcm_row['source_index'] == case['source_index'] and pcm_row['reference_id'] == reference_id and
             pcm_row['reference_scope'] == source['original_group'] and pcm_row['reference_qualification_sha256'] == source['qualification_sha256'] and
             pcm_row['packet_offsets'] == offsets and pcm_row['bytes'] == case['total_pcm'], 'Exact target named PCM identity/order/boundaries')
        pcm = inputs.read('target/pcm/' + path, target_root / path, pcm_row['sha256'], pcm_row['bytes'])
        persisted_paths.add((target_root / path).resolve())
        need(recovered['case'] == index and recovered['id'] == case['id'] and recovered['pcm'] == pcm and
             recovered['sha256'] == sha(pcm) and recovered['packet_offsets'] == offsets, 'Persisted PCM differs from strict actual PCM_HEX bytes')
        case_dir = host_root / 'cases' / reference_id
        inputs.read('reference/carrier/' + scope['host_path'] + '/' + reference_id, case_dir / 'input.ogg', raw['ogg_sha256'])
        reference_pcm = {}
        for decoder in ('libvorbis','vorbis'):
            receipt, reference_streams = reference_command(inputs,state,raw,decoder)
            if decoder not in raw['decoded']:
                need(decoder == 'vorbis' and receipt['returncode'] == 3199971767 and source['native_lookup2_refusal'] is True,
                     'Only actual documented native lookup2 refusals may lack PCM')
                continue
            need(receipt['returncode'] == 0, 'Reference WAV requires actual successful command')
            info = raw['decoded'][decoder]
            wav = inputs.read('reference/wav/' + scope['host_path'] + '/' + reference_id + '/' + decoder, case_dir / (decoder + '.wav'), info['wav_sha256'])
            decoded = wav_pcm(wav, case['rate'], sum(case['frames']))
            need(sha(decoded) == info['pcm_sha256'] and len(decoded) == info['pcm_bytes'] == case['total_pcm'] and
                 (info['rate'], info['channels'], info['bits']) == (case['rate'],2,16) and info['frames'] == case['frames'][1:], 'Actual reference WAV/PCM/metadata identity')
            frame_checksums(reference_streams['stdout'], decoded, case['rate'], case['frames'])
            reference_pcm[decoder] = decoded
        xiph_pcm = reference_pcm['libvorbis']
        need(sha(xiph_pcm) == proof['pcm_sha256'] == source['reference_pcm_sha256'], 'Qualified actual Xiph PCM changed')
        measured = compare(xiph_pcm, pcm, case['pcm'])
        transition_nonzero = {name:[0,0] for name in ('SS','SL','LS','LL')}
        reference_transition_nonzero = {name:[0,0] for name in ('SS','SL','LS','LL')}
        for packet in range(1,14):
            name = 'SL'[case['modes'][packet-1]] + 'SL'[case['modes'][packet]]
            first, stop = offsets[packet], offsets[packet+1]
            for channel in (0,1):
                transition_nonzero[name][channel] += sum(pcm[i:i+2] != b'\x00\x00' for i in range(first+channel*2,stop,4))
                reference_transition_nonzero[name][channel] += sum(xiph_pcm[i:i+2] != b'\x00\x00' for i in range(first+channel*2,stop,4))
        row = dict(case=index,id=case['id'],reference_id=reference_id,source_group=source['original_group'],reference_qualification_sha256=source['qualification_sha256'],
            rate=case['rate'],channels=2,bits=16,packet_offsets=offsets,comparison=measured,
            alignment=alignment(xiph_pcm,pcm,args.alignment_max_lag),target_transition_channel_nonzero=transition_nonzero,
            reference_transition_channel_nonzero=reference_transition_nonzero)
        case_results.append(row); result['cases'] = case_results
        xiph_all[case['id']],target_all[case['id']] = xiph_pcm,pcm
        if index < 16: xiph_books[case['id']],target_books[case['id']] = xiph_pcm,pcm
        if 'vorbis' in reference_pcm:
            cross = compare(xiph_pcm,reference_pcm['vorbis'],case['pcm'])
            need(source['native_compared'] is True and source['native_lookup2_refusal'] is False and
                 cross['zero_lag_direct_LR']['max_abs_error'] == raw['cross_reference_max_abs_error'], 'Preserved native crosscheck mismatch')
            native.append(dict(reference_id=reference_id,scope=source['original_group'],comparison=cross))
        save()
    need(set((target_root/'observed-pcm').iterdir()) == persisted_paths and len(native) == 7, 'Exact all31 persisted/native file accounting')
    declared_by_scope = []
    for group, state in zip(('books8','newbooks8'),scopes.values()):
        originals = [o for o in mapping['cases'] if o['original_group'] == group]
        need(len(originals) == 8, 'Declared books subgroup size')
        matrix_fact = originals[0]['original_matrix']
        matrix = json.loads(frozen('reference/original-matrix/' + group,matrix_fact['path'],matrix_fact['sha256'],matrix_fact['bytes']))
        declared = []
        for kind, field in (('equal','expected_same_decoder_pcm_equal_groups'),('different','expected_same_decoder_pcm_different_pairs')):
            for ids in matrix.get(field,[]): declared.append(dict(decoder='libvorbis',kind=kind,cases=ids,passed=True))
        need(len(declared) == 4 and declared == state['qualified']['xiph_metamorphic_checks'], 'Four actual declared relations per original books scope')
        declared_by_scope.append(declared)
    declared = declared_by_scope[0] + declared_by_scope[1]
    books_metamorphic = dict(xiph=relations8(xiph_books,declared),target=relations8(target_books,declared))
    floors = [[row['exact_original_floor0_relation']['original_id'], row['id']] for row in binding['cases'][25:]]
    need(tuple(tuple(pair) for pair in floors) == FLOOR_PAIRS, 'Six exact old19..24/new25..30 floor relation identities')
    metamorphic = dict(xiph=relations14(xiph_all,declared,floors),target=relations14(target_all,declared,floors))
    need(all(row['expected_relation_observed'] for row in metamorphic['xiph']), 'Previously qualified Xiph14 relations changed')
    policy, qualified_pcm = bounded_policy31(case_results,metamorphic,args.max_abs_error)
    # Secondary old25 projection is evaluated only after the whole31 measurement.
    subgroup_policy, subgroup_qualified = bounded_policy25(case_results[:25],books_metamorphic,args.max_abs_error)
    inputs.current()
    result.update(measurement_completed=True,actual_reference_compared=True,bounded_corpus_pcm_qualified=qualified_pcm,
        policy=policy,cases=case_results,metamorphic_relations=metamorphic,
        metamorphic_by_source_scope={'old_books8':{k:v[:4] for k,v in metamorphic.items()},'new_books8':{k:v[4:8] for k,v in metamorphic.items()},'floor0_equivalent6':{k:v[8:] for k,v in metamorphic.items()}},
        declared_subgroup_old25=dict(scope='declared_old25_only_after_complete31_measurement',case_indices=list(range(25)),policy=subgroup_policy,
            bounded_subgroup_pcm_qualified=subgroup_qualified,does_not_override_full31=True),
        full12_reference_recheck=full12_checked,
        original_dual_reference_passed=False,preserved_native_crosschecks=native,
        preserved_native_lookup2_refusals=[dict(scope=s['scope']['qualification_sha256'],failures=s['host']['failures']) for s in scopes.values()],
        source_reference_scopes=binding['source_scopes'],new_aggregate_reference_commands_executed=False,
        result='MEASURED_POLICY_UNSET' if policy is None else 'BOUNDED_CORPUS_PCM_QUALIFIED' if qualified_pcm else 'BOUNDED_CORPUS_PCM_REJECTED')
    save()
    return 0 if policy is None or qualified_pcm else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository','target','target-terminal','output'):
        parser.add_argument('--' + name,type=Path,required=True)
    parser.add_argument('--target-report-sha256',required=True)
    parser.add_argument('--max-abs-error',type=int,choices=(2,),default=None)
    parser.add_argument('--alignment-max-lag',type=int,choices=range(65),default=8)
    args = parser.parse_args()
    need(re.fullmatch('[0-9a-f]{64}',args.target_report_sha256),'Explicit reviewed target report SHA256 required')
    repo,out = args.repository.resolve(),args.output.resolve()
    build_root = (repo/'.build').resolve()
    protected = (args.target.resolve(),Path(__file__).resolve().parent,repo/'.build/cyd-vorbis-format-expanded31-runtime-01',
        *[(repo/scope['host_path']).parent.resolve() for scope in SCOPE_PINS],
        *[(repo/scope['qualification_path']).parent.resolve() for scope in SCOPE_PINS])
    need(build_root.parent == repo and out.is_relative_to(build_root) and out != build_root and not out.exists() and
         all(not out.is_relative_to(p) and not p.is_relative_to(out) for p in protected),'Fresh independent .build output required')
    out.mkdir(parents=True,exist_ok=False)
    result = dict(result='INCOMPLETE',checked_only=True,vendor_comparison_available=False,vendor_checked_pcm_equal=False,
        measurement_completed=False,actual_reference_compared=False,bounded_corpus_pcm_qualified=False,policy=None,
        passed=False,numeric_reference_qualified=False,format_conformance_qualified=False,format_corpus_qualified=False,
        full_G6_qualified=False,physical_device=False,production_radio_integration=False,cases=[])
    def save():
        temp = out/'report.json.tmp'
        temp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        temp.replace(out/'report.json')
    save()
    try:
        code = run(args,result,save)
    except BaseException as error:
        result.update(result='INTERRUPTED' if isinstance(error,KeyboardInterrupt) else 'INPUT_OR_MEASUREMENT_REJECTED',
            measurement_completed=False,actual_reference_compared=False,bounded_corpus_pcm_qualified=False,
            error_type=type(error).__name__,error=str(error))
        save()
        return 130 if isinstance(error,KeyboardInterrupt) else 1
    print(json.dumps({k:result[k] for k in ('result','measurement_completed','bounded_corpus_pcm_qualified','policy','declared_subgroup_old25')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
