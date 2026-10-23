"""Measure complete checked-only25 PCM against Xiph; no codec/process execution."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import struct
import sys
import wave
from pcm_metrics import alignment, compare, need
from policy25 import CASE_IDS, relations8, bounded_policy25, bounded_policy_books16

sys.dont_write_bytecode = True
SDK_REVISION = '9a97f6c54ec638111ce55cd36581b3c192f15207'
RUNNER = 'e00a30172c3b4291f080b2eee937214108adda7b6a03178e2f9833cb44d92034'
PROTOCOL = '961b0050f5881e5000116cbf7a598a122407420b0a52da0805d060c7b7e3f7ba'
CONTRACT = '660ac01523d3336ccb103f1443e51b870edf1a3d3f50321c5666969b1da634cc'
CONTRACT_FILE = '717ec7f703295f9851fd9241877cf249ff6f203c436786300a36247f2805218d'
DATA_HEADER = '97b1a62287dc048603eaaed239cf294a19a4c887ecc97d2fe2d887e7d8b8b6dc'
CALLER = '8c6aff4bb6d43c6b034db799477653e89fff4c9e65ac0b805d99f257672e9f03'
CASE_HEADER = '91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3'
SOURCE_MAP = '63f0eccf40044fabcc8d2b31c0a2094859258856e4948fe53a57cf8a9358301a'
BINDING = '802d0fe193991cfc40d388ad27594d8d0b632112f223cb6dee68226c07585f2c'
BINDING_HELPER = '3961e32fc5abb5a883260b2932a570908367c46ad2058a210a123336db7638ce'
METRICS = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
POLICY25 = '32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6'
SCOPE_PINS = [{'qualification_path': '.build/cyd-vorbis-format-corpus-qualified-01/qualification.json', 'qualification_sha256': 'd269d71ab02568fcb549c5abf39e4daf8ffcd082b1ede3c259351615768e02b0', 'host_path': '.build/cyd-vorbis-format-corpus-host-01/report.json', 'host_sha256': 'eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29', 'receipt_path': '.build/cyd-vorbis-format-corpus-host-01-command.json', 'receipt_sha256': '799bb892e5b12e0ccc13fc02607aefe49527f51568d0aecfe8a98ac88c492773', 'original_returncode': 1, 'totals': [17, 7, 10, 238, 398080]}, {'qualification_path': '.build/cyd-vorbis-map2-regression-qualified-01/qualification.json', 'qualification_sha256': 'bb78d2478d6e2a191202098443f5d224cda37fe7c44b33052de005ce10662bc4', 'host_path': '.build/cyd-vorbis-map2-regression-host-01/report.json', 'host_sha256': '5701c50e49118123e059c2a48a152f1fdd2f9def3bffb84053759b51c9a8df88', 'receipt_path': '.build/cyd-vorbis-map2-regression-host-01-command.json', 'receipt_sha256': '829899ce49f473962c2abc838fb9a1c6a6be14cf1ec007e66c464f7cff09bc2f', 'original_returncode': 1, 'totals': [8, 0, 8, 112, 225280]}]
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
         'Only complete checked-only25 capture is supported; NONPASS/partial captures are unusable')
    need(all(report.get(key) is False for key in ('passed', 'independent_reference_compared',
         'numeric_reference_qualified', 'format_corpus_qualified', 'full_G6_qualified',
         'physical_device', 'production_radio_integration')), 'Capture scope/classification differs')
    need(tuple(row['name'] for row in report.get('commands', [])) == COMMANDS, 'All nine actual terminal commands required')
    for row in report['commands']:
        need(row.get('state') == 'complete' and type(row.get('exit_status')) is int and row['exit_status'] == 0 and
             row.get('timed_out') is False and row.get('interrupted') is False and type(row.get('pid')) is int and
             row['pid'] > 0 and row.get('argv') and row.get('cwd'), 'Incomplete target process facts')


def c3_platform(inputs, target_root, target):
    need(target.get('platform') == 'esp32c3' and target.get('sdk_revision') == SDK_REVISION and
         type(target.get('elf_machine')) is int and target['elf_machine'] == 243 and
         type(target.get('coordinator_core')) is int and target['coordinator_core'] == 0 and
         type(target.get('worker_core')) is int and target['worker_core'] == 0,
         'Exact C3 SDK/RV32/unicore report facts required')
    for name in ('sdk-head', 'sdk-head-after'):
        row = next(row for row in target['commands'] if row['name'] == name)
        need(inputs.read('target/platform/' + name, target_root / (name + '.stdout.log'),
             row['stdout_sha256']).decode().strip() == SDK_REVISION, 'Actual C3 SDK terminal revision differs')
    setup_sha = target.get('selected_setup_sha256')
    need(isinstance(setup_sha, str) and re.fullmatch('[0-9a-f]{64}', setup_sha),
         'Actual C3 selected setup SHA256 required')
    source_name = 'sources/candidate/vorbis_repair/setup.c'
    source_rows = [row for row in target['inputs'].values() if relative(row['snapshot']) == source_name]
    need(len(source_rows) == 1 and source_rows[0]['sha256'] == setup_sha,
         'Selected C3 setup must bind exactly one frozen candidate source')
    inputs.read('target/platform/candidate-setup', target_root / source_name, setup_sha)
    variant_name = 'variant/vorbis_repair/setup.c'
    variants = {relative(name): value for name, value in target.get('variant_sources', {}).items()}
    need(len(variants) == len(target.get('variant_sources', {})) and variants.get(variant_name) == setup_sha,
         'Actual compiled C3 variant setup differs from selected snapshot')
    inputs.read('target/platform/variant-setup', target_root / variant_name, setup_sha)
    outputs = {relative(name): value for name, value in target.get('build_outputs', {}).items()}
    need(len(outputs) == len(target.get('build_outputs', {})), 'Duplicate normalized C3 build output paths')
    compile_name = 'build/compile_commands.json'
    need(compile_name in outputs, 'Actual C3 compile rows required')
    rows = json.loads(inputs.read('target/platform/compile-commands', target_root / compile_name,
                                 outputs[compile_name]))
    row_source = lambda row: (Path(row['directory']) / row['file']).resolve()
    setup_rows = [row for row in rows if row_source(row) == target_root / variant_name]
    need(len(setup_rows) == 1 and setup_rows[0] == target['setup_macro_context']['row'],
         'Macro proof must describe the actual selected C3 setup compile row')
    command = next(row for row in target['commands'] if row['name'] == 'setup-macros')
    macros = inputs.read('target/platform/setup-macros', target_root / 'setup-macros.stdout.log',
                         command['stdout_sha256']).decode()
    for name, value in (('CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ', 160), ('CONFIG_FREERTOS_UNICORE', 1),
                        ('__riscv_xlen', 32), ('__SIZEOF_LONG__', 4), ('__SIZEOF_POINTER__', 4),
                        ('CONFIG_IDF_TARGET_ESP32C3', 1), ('ESP_PLATFORM', 1)):
        need(re.search(r'^#define ' + name + ' ' + str(value) + '$', macros, re.M),
             'Actual C3 compile macro differs: ' + name)
    need(not re.search(r'^#define LIMIT_TO_64kHz\b', macros, re.M),
         'Actual C3 setup must retain unrestricted reviewed rate context')
    elf_names = [relative(name) for name in outputs if name.endswith('.elf')]
    need(len(elf_names) == 1 and elf_names[0].startswith('build/'), 'One actual C3 build ELF required')
    elf = inputs.read('target/platform/elf', target_root / elf_names[0], outputs[elf_names[0]])
    need(len(elf) >= 20 and elf[:6] == b'\x7fELF\x01\x01' and
         struct.unpack_from('<H', elf, 18)[0] == 243, 'Actual build must be little-endian ELF32/RISC-V')
    return dict(platform='esp32c3', sdk_revision=SDK_REVISION, elf_machine=243, riscv_bits=32,
                coordinator_core=0, worker_core=0, cpu_mhz=160, unicore=True,
                selected_setup_sha256=setup_sha, setup_snapshot=source_name, compiled_setup=variant_name,
                actual_build_elf=elf_names[0], actual_build_elf_sha256=sha(elf),
                setup_identity_from_actual_report=True, assumed_CYD_binary_equivalence=False)


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
    # No reference or persisted target PCM is read before complete25 process gates.
    target_bytes = inputs.read('target/report', target_root / 'report.json', args.target_report_sha256)
    target = json.loads(target_bytes)
    complete_capture(target)
    need((target.get('platform'), target.get('sdk_revision'), target.get('elf_machine'),
          target.get('coordinator_core'), target.get('worker_core')) ==
         ('esp32c3', SDK_REVISION, 243, 0, 0), 'Only reviewed C3 capture platform supported')
    terminal = json.loads(inputs.read('target/outer-terminal', args.target_terminal))
    need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and
         type(terminal.get('exit_code')) is int and terminal['exit_code'] == 0 and
         type(terminal.get('session_id')) is int and terminal['session_id'] > 0 and
         isinstance(terminal.get('terminal_chunk_id'), str) and terminal['terminal_chunk_id'] and
         terminal['report_sha256'] == sha(target_bytes) and terminal['entrypoint_sha256'] == RUNNER,
         'Actual reviewed25 target direct-tool terminal required; no invented argv/cwd/status')
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
    result['target_platform'] = c3_platform(inputs, target_root, target)
    result['target_platform_verified'] = True
    inputs.read('target/controller', target_root / 'sources/helpers/run.py', RUNNER)
    protocol_path = target_root / 'sources/helpers/protocol.py'
    inputs.read('target/protocol', protocol_path, PROTOCOL)
    inputs.read('target/caller', target_root / 'sources/project/main/main.c', CALLER)
    inputs.read('target/descriptor-header', target_root / 'sources/project/main/corpus_case.h', CASE_HEADER)
    inputs.read('target/data-header', target_root / 'sources/project/main/data.h', DATA_HEADER)
    inputs.read('target/source-binding-helper', target_root / 'sources/helpers/reference_binding02.py', BINDING_HELPER)
    mapping = json.loads(inputs.read('target/source-map', target_root / 'sources/corpus/source-map.json', SOURCE_MAP))
    binding = json.loads(inputs.read('target/source-binding', target_root / 'sources/reference/reference-binding02.json', BINDING))
    corpus = target['corpus']
    need((corpus['contract_file_sha256'], corpus['data_header_sha256'], corpus['source_map_sha256'], corpus['reference_binding_sha256']) ==
         (CONTRACT_FILE, DATA_HEADER, SOURCE_MAP, BINDING) and
         (corpus['cases'], corpus['packets'], corpus['expected_pcm']) == (25, 350, 623360), 'Exact reviewed25 corpus/header/binding facts')
    original_contract = json.loads(inputs.read('target/contract', target_root / 'sources/corpus/contract.json', CONTRACT_FILE))
    need(original_contract['contract_sha256'] == corpus['contract_sha256'] == binding['contract_sha256'] == CONTRACT, 'Reviewed25 model identity')
    need(binding['completed'] is True and binding['new_reference_commands_executed'] is False and
         binding['aggregate_reference_campaign_exists'] is False and binding['dual_reference_passed'] is False and
         len(binding['cases']) == len(mapping['cases']) == 25, 'Only coherent actual17+8 source binding supported')
    for item in binding['proof_facts']:
        frozen('target/proof-fact/' + item['path'], item['path'], item['sha256'], item['bytes'])
    spec = importlib.util.spec_from_file_location('pinned_expanded25_numeric_protocol', protocol_path)
    protocol = importlib.util.module_from_spec(spec); spec.loader.exec_module(protocol)
    relocated = []
    for item in original_contract['manifest_inputs']:
        row = target['inputs'][item['path']]
        need(row['sha256'] == item['sha256'], 'Frozen selected matrix binding')
        relocated.append(dict(path=str((target_root / relative(row['snapshot'])).resolve()), sha256=item['sha256']))
    contract = protocol.load_contract(relocated)
    need(contract['contract_sha256'] == CONTRACT and contract['model'] == original_contract['model'] and
         len(contract['model']['cases']) == 25 and contract['model']['total_packets'] == 350 and
         contract['model']['total_pcm'] == 623360 and contract['model']['case_mask'] == 33554431 and
         tuple(c['id'] for c in contract['model']['cases']) == CASE_IDS, 'Exactly25 relocated cases; no partial/subset extension')
    for item in contract['source_facts']:
        inputs.read('target/relocated-source/' + item['path'], item['path'], item['sha256'], item['bytes'])
    qemu = target['commands'][6]
    log = (inputs.read('target/log/qemu.stdout.log', target_root / 'qemu.stdout.log', qemu['stdout_sha256']).decode(errors='replace') + '\n' +
           inputs.read('target/log/qemu.stderr.log', target_root / 'qemu.stderr.log', qemu['stderr_sha256']).decode(errors='replace'))
    observed = protocol.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
                                    interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == target['observed'] and (observed['cases'], observed['decoded_packets'], observed['pcm'], observed['protocol_lines']) == (25, 350, 623360, 778) and
         observed['checked_decode_completed'] is True and observed['vendor_checked_pcm_equal'] is False and
         observed['vendor_comparison_available'] is False and len(captured) == len(target['observed_pcm']) == 25,
         'Complete actual25 protocol/PCM required; partial capture cannot be salvaged')
    scopes = {}
    for scope, expected in zip(binding['source_scopes'], SCOPE_PINS):
        need(scope == expected, 'Two exact separately qualified historical scopes required')
        host_root = (repo / relative(scope['host_path'])).parent
        host = json.loads(frozen('reference/' + scope['host_path'], repo / scope['host_path'], scope['host_sha256']))
        qualified = json.loads(frozen('reference/' + scope['qualification_path'], repo / scope['qualification_path'], scope['qualification_sha256']))
        outer = json.loads(frozen('reference/' + scope['receipt_path'], repo / scope['receipt_path'], scope['receipt_sha256']))
        need(qualified['completed'] is True and qualified['reference_corpus_qualified'] is True and qualified['original_dual_reference_passed'] is False and
             qualified['original_report_sha256'] == scope['host_sha256'] and qualified['original_outer_receipt_sha256'] == scope['receipt_sha256'] and
             outer['status'] == 'TERMINAL' and type(outer['returncode']) is int and outer['returncode'] == 1,
             'Preserve each actual historical dual-reference NONPASS')
        need(host['completed'] is True and host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False and
             [qualified[k] for k in ('xiph_cases','native_compared','native_lookup2_refusals','paired_raw_packets','expected_pcm_bytes')] == scope['totals'] and
             len(host['cases']) == len(qualified['cases']) == scope['totals'][0] and len(host['failures']) == scope['totals'][2], 'Exact per-host accounting')
        for origin, row in outer['logs'].items():
            inputs.read('reference/outer/' + scope['receipt_path'] + '/' + PureWindowsPath(origin).name,
                (repo / scope['receipt_path']).parent / PureWindowsPath(origin).name, row['sha256'], row['bytes'])
        for original, row in host['inputs'].items():
            inputs.read('reference/snapshot/' + scope['host_path'] + '/' + relative(row['snapshot']), host_root / relative(row['snapshot']), row['sha256'], row.get('bytes'))
        commands = {row['name']: row for row in host['commands']}
        need(len(commands) == len(host['commands']) == 2 * scope['totals'][0], 'Each real host command set complete; no aggregate command invented')
        scopes[scope['qualification_sha256']] = dict(scope=scope, host_root=host_root, host=host, qualified=qualified, commands=commands)
    need(len(scopes) == len(binding['source_scopes']) == 2, 'Exact old17/new8 scope count')
    xiph_books, target_books, case_results, native, persisted_paths = {}, {}, [], [], set()
    for index, (case, source, origin, pcm_row, recovered) in enumerate(zip(contract['model']['cases'], binding['cases'], mapping['cases'], target['observed_pcm'], captured)):
        state = scopes[source['qualification_sha256']]
        scope, host_root, host, qualified, commands = (state[k] for k in ('scope','host_root','host','qualified','commands'))
        reference_id = source['original_reference_id']
        need(source['case'] == origin['case'] == index and source['id'] == origin['id'] == case['id'] and source['raw_sha256'] == case['raw_sha256'], 'Exact all25 selected source/order/raw identity')
        raw = [row for row in host['cases'] if row['id'] == reference_id]
        proof = [row for row in qualified['cases'] if row['id'] == reference_id]
        need(len(raw) == len(proof) == 1, 'Exactly one real source reference case')
        raw, proof = raw[0], proof[0]
        need(proof['xiph_qualified'] is True and raw['input'] == origin['original_case_fields'] == origin['selected_case_fields'] and
             origin['fields_changed'] == [] and raw['source_matrix_sha256'] == source['original_matrix']['sha256'] and
             proof['frames'] == case['frames'][1:] and proof['pcm_bytes'] == source['pcm_bytes'] == case['total_pcm'] and
             proof['pcm_sha256'] == source['reference_pcm_sha256'], 'Actual per-case scoped reference/input/PCM binding')
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
            command = commands['cases/' + reference_id + '/decode-' + decoder]
            receipt = json.loads(inputs.read('reference/receipt/' + scope['host_path'] + '/' + reference_id + '/' + decoder,
                host_root / relative(command['receipt']), command['sha256']))
            need(receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int and type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0 and
                 receipt['runner_sha256'] == host['capture_sha256'] and receipt['executable_sha256'] == host['tools'][receipt['argv'][0]], 'Actual reference command/tool terminal identity')
            for log_origin, row in receipt['logs'].items():
                inputs.read('reference/log/' + scope['host_path'] + '/' + reference_id + '/' + PureWindowsPath(log_origin).name,
                    case_dir / PureWindowsPath(log_origin).name, row['sha256'], row['bytes'])
            if decoder not in raw['decoded']:
                need(decoder == 'vorbis' and receipt['returncode'] != 0 and proof['native_lookup2_refusal'] is True, 'Only actual qualified native lookup2 refusals may lack PCM')
                continue
            need(receipt['returncode'] == 0, 'Reference WAV requires actual successful command')
            info = raw['decoded'][decoder]
            wav = inputs.read('reference/wav/' + scope['host_path'] + '/' + reference_id + '/' + decoder, case_dir / (decoder + '.wav'), info['wav_sha256'])
            decoded = wav_pcm(wav, case['rate'], sum(case['frames']))
            need(sha(decoded) == info['pcm_sha256'] and len(decoded) == info['pcm_bytes'] == case['total_pcm'] and
                 (info['rate'], info['channels'], info['bits']) == (case['rate'],2,16) and info['frames'] == case['frames'][1:], 'Actual reference WAV/PCM/metadata identity')
            frame_checksums(inputs.read('reference/log/' + scope['host_path'] + '/' + reference_id + '/decode-' + decoder + '.stdout.log',
                case_dir / ('decode-' + decoder + '.stdout.log')), decoded, case['rate'], case['frames'])
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
        if index < 16: xiph_books[case['id']],target_books[case['id']] = xiph_pcm,pcm
        if 'vorbis' in reference_pcm:
            cross = compare(xiph_pcm,reference_pcm['vorbis'],case['pcm'])
            need(proof['native_compared'] is True and proof['native_lookup2_refusal'] is False and
                 cross['zero_lag_direct_LR']['max_abs_error'] == raw['cross_reference_max_abs_error'], 'Preserved native crosscheck mismatch')
            native.append(dict(reference_id=reference_id,scope=source['original_group'],comparison=cross))
        save()
    need(set((target_root/'observed-pcm').iterdir()) == persisted_paths and len(native) == 7, 'Exact all25 persisted/native file accounting')
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
    metamorphic = dict(xiph=relations8(xiph_books,declared),target=relations8(target_books,declared))
    need(all(row['expected_relation_observed'] for row in metamorphic['xiph']), 'Previously qualified Xiph relations changed')
    policy, qualified_pcm = bounded_policy25(case_results,metamorphic,args.max_abs_error)
    subgroup_policy, subgroup_qualified = bounded_policy_books16(case_results[:16],metamorphic,args.max_abs_error)
    inputs.current()
    result.update(measurement_completed=True,actual_reference_compared=True,bounded_corpus_pcm_qualified=qualified_pcm,
        policy=policy,cases=case_results,metamorphic_relations=metamorphic,
        metamorphic_by_source_scope={'old_books8':{k:v[:4] for k,v in metamorphic.items()},'new_books8':{k:v[4:] for k,v in metamorphic.items()}},
        declared_subgroup_books16=dict(scope='declared_books16_only_after_complete25_capture',case_indices=list(range(16)),policy=subgroup_policy,
            bounded_subgroup_pcm_qualified=subgroup_qualified,does_not_override_full25=True),
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
    protected = (args.target.resolve(),Path(__file__).resolve().parent,
        *[(repo/scope['host_path']).parent.resolve() for scope in SCOPE_PINS],
        *[(repo/scope['qualification_path']).parent.resolve() for scope in SCOPE_PINS])
    need(build_root.parent == repo and out.is_relative_to(build_root) and out != build_root and not out.exists() and
         all(not out.is_relative_to(p) and not p.is_relative_to(out) for p in protected),'Fresh independent .build output required')
    out.mkdir(parents=True,exist_ok=False)
    result = dict(result='INCOMPLETE',target_platform_verified=False,checked_only=True,vendor_comparison_available=False,vendor_checked_pcm_equal=False,
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
    print(json.dumps({k:result[k] for k in ('result','measurement_completed','bounded_corpus_pcm_qualified','policy','declared_subgroup_books16')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
