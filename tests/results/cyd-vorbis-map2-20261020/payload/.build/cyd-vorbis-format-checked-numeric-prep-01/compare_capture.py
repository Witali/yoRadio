"""Measure complete checked-only17 PCM against Xiph; no codec/process execution."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys
import wave
from pcm_metrics import alignment, bounded_policy, compare, need, relations

sys.dont_write_bytecode = True
HOST = 'eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29'
QUALIFIED = 'd269d71ab02568fcb549c5abf39e4daf8ffcd082b1ede3c259351615768e02b0'
HOST_TERMINAL = '799bb892e5b12e0ccc13fc02607aefe49527f51568d0aecfe8a98ac88c492773'
RUNNER = '3aa167fe4b231d2c15b91b1b5c78b24da3410d18eaacc0709d6afe0c33ea902d'
PROTOCOL = '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'
CONTRACT = '847022a7835de03c0f820b3f8e418e7e8b89b6125d2dba8bdf09712d33d3a65a'
CONTRACT_FILE = '6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391'
DATA_HEADER = 'b4db391fda10e7361f57fe4242574593902042f0e0ef9a48fe24aac144bb153d'
CALLER = '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065'
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
         'Only complete checked-only17 capture is supported; NONPASS/partial captures are unusable')
    need(all(report.get(key) is False for key in ('passed', 'independent_reference_compared',
         'numeric_reference_qualified', 'format_corpus_qualified', 'full_G6_qualified',
         'physical_device', 'production_radio_integration')), 'Capture scope/classification differs')
    need(tuple(row['name'] for row in report.get('commands', [])) == COMMANDS, 'All nine actual terminal commands required')
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
         '#codec_id 0: pcm_s16le' in text and '#channel_layout_name 0: 2 channels' in text,
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
    host_root, target_root = args.host.resolve(), args.target.resolve()
    host_bytes = inputs.read('host/report', host_root / 'report.json', HOST)
    host = json.loads(host_bytes)
    qualified = json.loads(inputs.read('host/qualification', args.qualification, QUALIFIED))
    outer = json.loads(inputs.read('host/outer-terminal', args.host_terminal, HOST_TERMINAL))
    need(host['completed'] is True and host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False and
         qualified['completed'] is True and qualified['reference_corpus_qualified'] is True and
         qualified['original_dual_reference_passed'] is False and qualified['original_report_sha256'] == HOST and
         qualified['original_outer_receipt_sha256'] == HOST_TERMINAL and outer['status'] == 'TERMINAL' and
         type(outer['returncode']) is int and outer['returncode'] == 1, 'Preserve original dual-reference NONPASS')
    need((qualified['xiph_cases'], qualified['native_compared'], qualified['native_lookup2_refusals'],
          qualified['paired_raw_packets'], qualified['expected_pcm_bytes']) == (17, 7, 10, 238, 398080) and
         len(host['cases']) == len(qualified['cases']) == 17 and len(host['failures']) == 10, 'Exact host corpus accounting')
    for origin, row in outer['logs'].items():
        inputs.read('host/outer/' + PureWindowsPath(origin).name,
                    args.host_terminal.resolve().parent / PureWindowsPath(origin).name, row['sha256'], row['bytes'])
    for original, row in host['inputs'].items():
        inputs.read('host/input/' + relative(row['snapshot']), host_root / relative(row['snapshot']), row['sha256'], row.get('bytes'))
    # Reject a NONPASS capture BEFORE any attempt to read or salvage its PCM.
    target_bytes = inputs.read('target/report', target_root / 'report.json', args.target_report_sha256)
    target = json.loads(target_bytes)
    complete_capture(target)
    terminal = json.loads(inputs.read('target/outer-terminal', args.target_terminal))
    need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and
         type(terminal.get('exit_code')) is int and terminal['exit_code'] == 0 and
         type(terminal.get('session_id')) is int and terminal['session_id'] > 0 and
         isinstance(terminal.get('terminal_chunk_id'), str) and terminal['terminal_chunk_id'] and
         terminal['report_sha256'] == sha(target_bytes) and terminal['entrypoint_sha256'] == RUNNER,
         'Actual reviewed target direct-tool terminal required; no invented outer argv/cwd/status')
    for row in target['commands']:
        for stream in ('stdout', 'stderr'):
            key = row['name'] + '.' + stream + '.log'
            inputs.read('target/log/' + key, target_root / key, row[stream + '_sha256'])
    for original, row in target['inputs'].items():
        inputs.read('target/input/' + relative(row['snapshot']), target_root / relative(row['snapshot']), row['sha256'], row.get('bytes'))
    inputs.read('target/controller', target_root / 'sources/helpers/run.py', RUNNER)
    protocol_path = target_root / 'sources/helpers/protocol.py'
    inputs.read('target/protocol', protocol_path, PROTOCOL)
    need(target['corpus']['contract_file_sha256'] == CONTRACT_FILE and
         target['corpus']['data_header_sha256'] == DATA_HEADER and target['corpus']['cases'] == 17 and
         target['corpus']['packets'] == 238 and target['corpus']['expected_pcm'] == 398080, 'Exact reviewed17 corpus/header facts required')
    inputs.read('target/caller', target_root / 'sources/project/main/main.c', CALLER)
    inputs.read('target/data-header', target_root / 'sources/project/main/data.h', DATA_HEADER)
    contract_bytes = inputs.read('target/contract', target_root / 'sources/corpus/contract.json', CONTRACT_FILE)
    original_contract = json.loads(contract_bytes)
    need(original_contract['contract_sha256'] == target['corpus']['contract_sha256'] == CONTRACT, 'Reviewed contract identity')
    spec = importlib.util.spec_from_file_location('pinned_numeric_capture_protocol', protocol_path)
    protocol = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(protocol)
    relocated = []
    for item in original_contract['manifest_inputs']:
        row = target['inputs'][item['path']]
        need(row['sha256'] == item['sha256'], 'Frozen matrix input binding')
        relocated.append(dict(path=str((target_root / relative(row['snapshot'])).resolve()), sha256=item['sha256']))
    contract = protocol.load_contract(relocated)
    need(contract['contract_sha256'] == CONTRACT and contract['model'] == original_contract['model'] and
         len(contract['model']['cases']) == 17 and contract['model']['total_packets'] == 238 and
         contract['model']['total_pcm'] == 398080 and contract['model']['case_mask'] == 131071,
         'Relocation is path-only; exactly17 cases required, never a partial or25case extension')
    qemu = target['commands'][6]
    log = (inputs.read('target/log/qemu.stdout.log', target_root / 'qemu.stdout.log', qemu['stdout_sha256']).decode(errors='replace') + '\n' +
           inputs.read('target/log/qemu.stderr.log', target_root / 'qemu.stderr.log', qemu['stderr_sha256']).decode(errors='replace'))
    observed = protocol.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
                                    interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == target['observed'] and observed['cases'] == 17 and observed['decoded_packets'] == 238 and observed['pcm'] == 398080 and
         observed['protocol_lines'] == 530 and observed['checked_decode_completed'] is True and
         observed['vendor_checked_pcm_equal'] is False and observed['vendor_comparison_available'] is False,
         'Complete strict target protocol differs from stored report')
    need(len(captured) == len(target['observed_pcm']) == 17, 'All seventeen complete PCM captures required')
    commands = {row['name']: row for row in host['commands']}
    need(len(commands) == 34, 'All reference command records required')
    xiph_books, target_books, case_results, native = {}, {}, [], []
    persisted_paths = set()
    for index, (case, raw, proof, pcm_row, recovered) in enumerate(zip(contract['model']['cases'], host['cases'], qualified['cases'], target['observed_pcm'], captured)):
        reference_id = str(case['source_index']) + '-' + case['id']
        need(raw['id'] == proof['id'] == reference_id and proof['xiph_qualified'] is True and
             raw['source_matrix_sha256'] == contract['model']['manifest_sha256'][case['source_index']] and
             proof['frames'] == case['frames'][1:] and proof['pcm_bytes'] == case['total_pcm'], 'Reference/capture named case binding')
        offsets = [0]
        for count in case['pcm']:
            offsets.append(offsets[-1] + count)
        path = relative(pcm_row['path'])
        need(path == f"observed-pcm/{index:02d}-{case['id']}.s16le" and pcm_row['case'] == index and
             pcm_row['id'] == case['id'] and pcm_row['source_index'] == case['source_index'] and
             pcm_row['reference_id'] == reference_id and pcm_row['packet_offsets'] == offsets and
             pcm_row['bytes'] == case['total_pcm'], 'Exact target PCM identity/order/boundaries')
        pcm = inputs.read('target/pcm/' + path, target_root / path, pcm_row['sha256'], pcm_row['bytes'])
        persisted_paths.add((target_root / path).resolve())
        need(recovered['case'] == index and recovered['id'] == case['id'] and recovered['pcm'] == pcm and
             recovered['sha256'] == sha(pcm) and recovered['packet_offsets'] == offsets, 'Stored target PCM differs from actual strict protocol bytes')
        xiph_pcm = None
        reference_pcm = {}
        case_dir = host_root / 'cases' / reference_id
        inputs.read('host/carrier/' + reference_id, case_dir / 'input.ogg', raw['ogg_sha256'])
        for decoder in ('libvorbis', 'vorbis'):
            command = commands['cases/' + reference_id + '/decode-' + decoder]
            receipt = json.loads(inputs.read('host/receipt/' + reference_id + '/' + decoder,
                host_root / relative(command['receipt']), command['sha256']))
            need(receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int and
                 type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0 and
                 receipt['runner_sha256'] == host['capture_sha256'] and receipt['executable_sha256'] == host['tools'][receipt['argv'][0]],
                 'Actual reference command terminal/tool binding')
            for origin, row in receipt['logs'].items():
                inputs.read('host/log/' + reference_id + '/' + PureWindowsPath(origin).name,
                    case_dir / PureWindowsPath(origin).name, row['sha256'], row['bytes'])
            if decoder not in raw['decoded']:
                need(decoder == 'vorbis' and receipt['returncode'] != 0 and proof['native_lookup2_refusal'] is True,
                     'Only the preserved native lookup2 refusals may lack PCM')
                continue
            need(receipt['returncode'] == 0, 'Reference PCM must come from successful actual command')
            info = raw['decoded'][decoder]
            wav = inputs.read('host/wav/' + reference_id + '/' + decoder, case_dir / (decoder + '.wav'), info['wav_sha256'])
            decoded = wav_pcm(wav, case['rate'], sum(case['frames']))
            need(sha(decoded) == info['pcm_sha256'] and len(decoded) == info['pcm_bytes'] == case['total_pcm'] and
                 (info['rate'], info['channels'], info['bits']) == (case['rate'], 2, 16) and info['frames'] == case['frames'][1:], 'Actual WAV PCM/metadata binding')
            frame_checksums(inputs.read('host/log/' + reference_id + '/decode-' + decoder + '.stdout.log',
                case_dir / ('decode-' + decoder + '.stdout.log')), decoded, case['rate'], case['frames'])
            reference_pcm[decoder] = decoded
        xiph_pcm = reference_pcm['libvorbis']
        need(sha(xiph_pcm) == proof['pcm_sha256'], 'Qualified Xiph bytes changed')
        measured = compare(xiph_pcm, pcm, case['pcm'])
        transition_nonzero = {name: [0, 0] for name in ('SS', 'SL', 'LS', 'LL')}
        for packet in range(1, 14):
            name = 'SL'[case['modes'][packet - 1]] + 'SL'[case['modes'][packet]]
            a, b = offsets[packet], offsets[packet + 1]
            for channel in (0, 1):
                transition_nonzero[name][channel] += sum(pcm[i:i + 2] != b'\x00\x00' for i in range(a + channel * 2, b, 4))
        need(all(all(values) for values in transition_nonzero.values()), 'Target nonzero evidence required for each channel/present transition')
        row = dict(case=index, id=case['id'], reference_id=reference_id, rate=case['rate'], channels=2, bits=16,
            packet_offsets=offsets, comparison=measured, alignment=alignment(xiph_pcm, pcm, args.alignment_max_lag),
            target_transition_channel_nonzero=transition_nonzero)
        case_results.append(row)
        result['cases'] = case_results
        if case['source_index'] == 0:
            xiph_books[case['id']], target_books[case['id']] = xiph_pcm, pcm
        if 'vorbis' in reference_pcm:
            cross = compare(xiph_pcm, reference_pcm['vorbis'], case['pcm'])
            need(proof['native_compared'] is True and proof['native_lookup2_refusal'] is False and
                 cross['zero_lag_direct_LR']['max_abs_error'] == raw['cross_reference_max_abs_error'], 'Preserved native crosscheck mismatch')
            native.append(dict(reference_id=reference_id, comparison=cross))
        save()
    need(set((target_root / 'observed-pcm').iterdir()) == persisted_paths and len(native) == 7, 'Exact target/native PCM file accounting')
    declared = []
    for mi, item in enumerate(relocated):
        matrix = json.loads(inputs.read('target/matrix/' + str(mi), item['path'], item['sha256']))
        for kind, field in (('equal', 'expected_same_decoder_pcm_equal_groups'), ('different', 'expected_same_decoder_pcm_different_pairs')):
            for group in matrix.get(field, []):
                declared.append(dict(decoder='libvorbis', kind=kind, cases=group, passed=True))
    need(len(declared) == 4 and declared == qualified['xiph_metamorphic_checks'],
         'All actual source-declared17 books relations must match the independent qualification')
    metamorphic = dict(xiph=relations(xiph_books, declared), target=relations(target_books, declared))
    need(all(row['expected_relation_observed'] for row in metamorphic['xiph']), 'Previously qualified Xiph relations changed')
    policy, qualified_pcm = bounded_policy(case_results, metamorphic, args.max_abs_error)
    inputs.current()
    result.update(measurement_completed=True, actual_reference_compared=True,
        bounded_corpus_pcm_qualified=qualified_pcm, policy=policy, cases=case_results, metamorphic_relations=metamorphic,
        original_dual_reference_passed=False, preserved_native_crosschecks=native,
        preserved_native_lookup2_refusals=host['failures'], historical_host_cross_reference_bound=host['cross_reference_pcm16_max_error_allowed'],
        result='MEASURED_POLICY_UNSET' if policy is None else 'BOUNDED_CORPUS_PCM_QUALIFIED' if qualified_pcm else 'BOUNDED_CORPUS_PCM_REJECTED')
    save()
    return 0 if policy is None or qualified_pcm else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'host', 'qualification', 'host-terminal', 'target', 'target-terminal', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--target-report-sha256', required=True)
    parser.add_argument('--max-abs-error', type=int, choices=(2,), default=None)
    parser.add_argument('--alignment-max-lag', type=int, choices=range(65), default=8)
    args = parser.parse_args()
    need(re.fullmatch('[0-9a-f]{64}', args.target_report_sha256), 'Explicit reviewed target report SHA256 required')
    repo, out = args.repository.resolve(), args.output.resolve()
    protected = (args.host.resolve(), args.target.resolve(), Path(__file__).resolve().parent)
    need(out.is_relative_to(repo / '.build') and out != repo / '.build' and not out.exists() and
         all(not out.is_relative_to(p) and not p.is_relative_to(out) for p in protected), 'Fresh independent .build output required')
    out.mkdir(parents=True, exist_ok=False)
    result = dict(result='INCOMPLETE', checked_only=True, vendor_comparison_available=False, vendor_checked_pcm_equal=False,
        measurement_completed=False, actual_reference_compared=False,
        bounded_corpus_pcm_qualified=False, policy=None, passed=False, numeric_reference_qualified=False,
        format_conformance_qualified=False, format_corpus_qualified=False, full_G6_qualified=False,
        physical_device=False, production_radio_integration=False, cases=[])
    def save():
        temp = out / 'report.json.tmp'
        temp.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
        temp.replace(out / 'report.json')
    save()
    try:
        code = run(args, result, save)
    except BaseException as error:
        result.update(result='INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'INPUT_OR_MEASUREMENT_REJECTED',
            measurement_completed=False, actual_reference_compared=False, bounded_corpus_pcm_qualified=False,
            error_type=type(error).__name__, error=str(error))
        save()  # Preserve primary partial evidence before returning failure.
        return 130 if isinstance(error, KeyboardInterrupt) else 1
    print(json.dumps({k: result[k] for k in ('result', 'measurement_completed', 'bounded_corpus_pcm_qualified', 'policy')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
