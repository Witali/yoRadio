"""Pure captured PCM/reference comparison; no decoder, SDK or process launch."""

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

from policy8 import CASE_IDS, TRIPLES, DIFFERENT_PAIRS, relations, bounded_policy

sys.dont_write_bytecode = True

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

METRICS = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
RUNNER = 'ce603506b72b30807123eed3efd5cf383c9ec563733a9d3beaf7a6333e38a28c'
PROTOCOL = '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'
CALLER = '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065'
CONTRACT_FILE = '65003d33a6c13634bea414ceaff487a2858e78eae93afc5458edd6da3fecac0c'
DATA = '93e0e734b0374f42b06bfd9095a4bc4270813266ee1f080b2932313e0a3e98e6'
BINDING = '4f72f66b0db4315b018517ca3ee17ea346fdcadb0ca2ae234b3630b1671086aa'
SETUP = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
COMMANDS = ('sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')


def capture(inputs, role, root, expected_report, terminal_path):
    raw_report = inputs.read(role + '/report', root / 'report.json', expected_report)
    report = json.loads(raw_report)
    need(report.get('result') == 'CHECKED_CORPUS_PCM_CAPTURED' and report.get('completed') is True and
         report.get('target_capture_completed') is True and report.get('checked_decode_completed') is True and
         all(report.get(name) is False for name in ('passed', 'vendor_comparison_available', 'vendor_checked_pcm_equal',
             'independent_reference_compared', 'numeric_reference_qualified', 'format_corpus_qualified', 'full_G6_qualified',
             'physical_device', 'production_radio_integration')), 'Complete actual checked-only capture required before PCM access')
    terminal = json.loads(inputs.read(role + '/terminal', terminal_path))
    need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and type(terminal.get('exit_code')) is int and
         terminal['exit_code'] == 0 and terminal['report_sha256'] == sha(raw_report) and
         type(terminal['session_id']) is int and terminal['session_id'] > 0 and terminal['terminal_chunk_id'], 'Actual direct-tool terminal0/report binding required')
    need(tuple(row['name'] for row in report['commands']) == COMMANDS, 'All nine actual target commands required')
    for command in report['commands']:
        need(command['state'] == 'complete' and type(command['exit_status']) is int and command['exit_status'] == 0 and
             command['timed_out'] is False and command['interrupted'] is False and type(command['pid']) is int and
             command['pid'] > 0 and command['argv'] and command['cwd'], 'Complete actual owned process facts required')
        for stream in ('stdout', 'stderr'):
            inputs.read(role + '/log/' + command['name'] + '/' + stream, root / (command['name'] + '.' + stream + '.log'), command[stream + '_sha256'])
    controller = inputs.read(role + '/controller', root / 'sources/helpers/run.py', RUNNER)
    need(sha(controller) == terminal['entrypoint_sha256'], 'Actual controller identity differs')
    protocol_path = root / 'sources/helpers/protocol.py'
    inputs.read(role + '/protocol', protocol_path, PROTOCOL)
    inputs.read(role + '/caller', root / 'sources/project/main/main.c', CALLER)
    inputs.read(role + '/setup', root / 'variant/vorbis_repair/setup.c', SETUP)
    inputs.read(role + '/candidate-setup', root / 'sources/candidate/vorbis_repair/setup.c', SETUP)
    need({relative(name): digest for name, digest in report['variant_sources'].items()}.get('variant/vorbis_repair/setup.c') == SETUP,
         'Actual variant/source setup identity differs')
    for origin, row in report['inputs'].items():
        inputs.read(role + '/input/' + relative(row['snapshot']), root / relative(row['snapshot']), row['sha256'], row.get('bytes'))
    contract_data = inputs.read(role + '/contract', root / 'sources/corpus/contract.json', CONTRACT_FILE)
    saved = json.loads(contract_data)
    inputs.read(role + '/data', root / 'sources/project/main/data.h', DATA)
    inputs.read(role + '/binding', root / 'sources/reference/reference-binding8.json', BINDING)
    relocated = []
    for item in saved['manifest_inputs']:
        row = report['inputs'][str(Path(item['path']).resolve())]
        need(row['sha256'] == item['sha256'], 'Actual frozen matrix binding differs')
        relocated.append(dict(path=str((root / relative(row['snapshot'])).resolve()), sha256=item['sha256']))
    spec = importlib.util.spec_from_file_location('pinned_singletons_numeric_protocol_' + role, protocol_path)
    protocol = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(protocol)
    contract = protocol.load_contract(relocated)
    model = contract['model']
    count = len(model['cases'])
    need(report['corpus']['contract_file_sha256'] == sha(contract_data) and
         report['corpus']['contract_sha256'] == saved['contract_sha256'] and
         (report['corpus']['cases'], report['corpus']['packets'], report['corpus']['expected_pcm']) ==
         (count, model['total_packets'], model['total_pcm']), 'Actual report/contract full accounting differs')
    need(contract['contract_sha256'] == saved['contract_sha256'] and model == saved['model'] and
         count == 8 and model['total_packets'] == count * 14 and
         model['total_pcm'] == sum(c['total_pcm'] for c in model['cases']) and model['case_mask'] == (1 << count) - 1, 'Complete exact target contract shape required')
    need(tuple(c['id'] for c in model['cases']) == CASE_IDS and (model['total_packets'], model['total_pcm'], model['case_mask']) ==
         (112, 225280, 255), 'Exact full8 reviewed order/counts required')
    for item in contract['source_facts']:
        inputs.read(role + '/relocated/' + item['path'], item['path'], item['sha256'], item['bytes'])
    qemu = report['commands'][6]
    log = (inputs.read(role + '/qemu-stdout', root / 'qemu.stdout.log', qemu['stdout_sha256']).decode(errors='replace') + '\n' +
           inputs.read(role + '/qemu-stderr', root / 'qemu.stderr.log', qemu['stderr_sha256']).decode(errors='replace'))
    observed = protocol.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
        interrupted=qemu['interrupted'], manifest_hashes=model['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == report['observed'] and observed['protocol_lines'] == 3 + count * 31 and len(captured) == len(report['observed_pcm']) == count,
         'Full actual protocol/captured case inventory required')
    paths = set()
    for index, (case, row, pcm) in enumerate(zip(model['cases'], report['observed_pcm'], captured)):
        name = relative(row['path'])
        need(name == f"observed-pcm/{index:02d}-{case['id']}.s16le" and row['case'] == pcm['case'] == index and
             row['id'] == pcm['id'] == case['id'] and row['sha256'] == pcm['sha256'] and
             row['packet_offsets'] == pcm['packet_offsets'], 'Named persisted PCM metadata differs')
        value = inputs.read(role + '/pcm/' + name, root / name, row['sha256'], row['bytes'])
        need(value == pcm['pcm'] and len(value) == case['total_pcm'], 'Persisted PCM differs from actual full PCM_HEX')
        paths.add(root / name)
    need(set((root / 'observed-pcm').iterdir()) == paths, 'Exact persisted PCM file set required')
    return report, contract, captured


def transition_counts(pcm, case, offsets):
    result = {name: [0, 0] for name in ('SS', 'SL', 'LS', 'LL')}
    for packet in range(1, 14):
        name = 'SL'[case['modes'][packet-1]] + 'SL'[case['modes'][packet]]
        first, stop = offsets[packet:packet+2]
        for channel in (0, 1):
            result[name][channel] += sum(pcm[i:i+2] != b'\0\0' for i in range(first + 2*channel, stop, 4))
    return result


def run(args, result, save):
    inputs = Inputs()
    result['inputs'] = inputs.rows
    here = Path(__file__).resolve().parent
    inputs.read('adapter/script', Path(__file__))
    inputs.read('adapter/metrics', here / 'pcm_metrics.py', METRICS)
    pins = json.loads(inputs.read('adapter/pins', here / 'pins.json'))
    inputs.read('adapter/policy', here / 'policy8.py', pins['policy_sha256'])
    readiness = json.loads(inputs.read('adapter/readiness', here / 'readiness.json', args.readiness_sha256))
    need(readiness['schema'] == 'more-singletons8-numeric-source-only-readiness-v1' and readiness['runtime_executed'] is False, 'Reviewed source-only readiness required')
    need({p.relative_to(here).as_posix() for p in here.rglob('*') if p.is_file()} == set(readiness['files']) | {'readiness.json'}, 'Exact adapter source file set')
    for name, row in readiness['files'].items():
        inputs.read('adapter/frozen/' + relative(name), here / relative(name), row['sha256'], row['bytes'])
    target, contract, captured = capture(inputs, 'target', args.target.resolve(), args.target_report_sha256, args.target_terminal)
    root = args.repository.resolve()
    refs = pins['reference']
    q = json.loads(inputs.read('reference/qualification', root / refs['qualification']['path'], refs['qualification']['sha256']))
    host = json.loads(inputs.read('reference/host', root / refs['host']['path'], refs['host']['sha256']))
    outer = json.loads(inputs.read('reference/outer', root / refs['outer']['path'], refs['outer']['sha256']))
    qterminal = json.loads(inputs.read('reference/qualification-terminal', root / refs['qualification_terminal']['path'], refs['qualification_terminal']['sha256']))
    matrix = json.loads(inputs.read('reference/matrix', root / refs['matrix']['path'], refs['matrix']['sha256']))
    need(q['completed'] is True and q['profile'] == 'singletons8' and q['result'] == 'XIPH_QUALIFIED_DUAL_NONPASS' and
         q['reference_corpus_qualified'] is True and q['xiph_reference_qualified'] is True and
         q['original_dual_reference_passed'] is False and q['dual_reference_qualified'] is False and
         q['original_report_sha256'] == refs['host']['sha256'] and q['original_outer_receipt_sha256'] == refs['outer']['sha256'] and
         (q['xiph_cases'], q['native_compared'], q['native_lookup2_refusals'], q['native_packet_decode_failures'], q['paired_raw_packets'], q['expected_pcm_bytes']) ==
         (8, 0, 4, 4, 112, 225280) and q['native_cause_diagnosed'] is False and outer['status'] == qterminal['status'] == 'TERMINAL' and
         outer['returncode'] == 1 and qterminal['returncode'] == 0, 'Preserve actual original dual NONPASS and full8 qualified Xiph scope')
    for name, row in q['validated_inputs'].items():
        inputs.read('reference/qualified-input/' + name, row['path'], row['sha256'], row['bytes'])
    for name, receipt in (('host', outer), ('qualifier', qterminal)):
        for path, row in receipt['logs'].items():
            inputs.read('reference/outer-log/' + name + '/' + path, path, row['sha256'], row['bytes'])
    need(host['completed'] is True and host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False and
         len(host['cases']) == len(host['failures']) == len(q['cases']) == 8 and len(host['commands']) == 16 and
         tuple(row['id'] for row in matrix['cases']) == CASE_IDS and
         matrix['expected_same_decoder_pcm_equal_groups'] == TRIPLES and matrix['expected_same_decoder_pcm_different_pairs'] == DIFFERENT_PAIRS and
         q['xiph_metamorphic_checks'] == [dict(decoder='libvorbis', kind=kind, cases=group, passed=True)
            for kind, groups in (('equal', TRIPLES), ('different', DIFFERENT_PAIRS)) for group in groups], 'Exact8 actual reference inventory/equal and different groups')
    need(q['original_failures'] == host['failures'], 'Preserve all eight original distinct native failures')
    commands = {row['name']: row for row in host['commands']}
    host_root = (root / refs['host']['path']).parent
    xiph, actual, rows = {}, {}, []
    for index, (case, pcm, original, accepted) in enumerate(zip(contract['model']['cases'], captured, host['cases'], q['cases'])):
        source = matrix['cases'][index]
        rid = '0-' + case['id']
        need(original['id'] == accepted['id'] == rid and original['input'] == source and
             original['source_matrix_sha256'] == refs['matrix']['sha256'] and accepted['xiph_qualified'] is True and
             accepted['native_compared'] is False and accepted['native_lookup2_refusal'] is (index < 4) and
             accepted['native_packet_decode_failure'] is (index >= 4) and accepted['native_cause_diagnosed'] is False and
             accepted['native_failure_kind'] == ('lookup2_setup_refusal' if index < 4 else 'packet_decode_failure_no_PCM') and
             accepted['native_actual_returncode'] == (3199971767 if index < 4 else 4294967295) and accepted['frames'] == case['frames'][1:] and
             accepted['pcm_bytes'] == case['total_pcm'], 'Exact ordered target/reference case binding')
        for kind in ('identification', 'setup', 'audio'):
            need(case['raw_sha256'][kind] == source['raw_sha256'][kind], 'Full target raw payload differs from qualified input')
        folder = host_root / 'cases' / rid
        for decoder, code in (('libvorbis', 0), ('vorbis', 3199971767 if index < 4 else 4294967295)):
            command = commands['cases/' + rid + '/decode-' + decoder]
            receipt = json.loads(inputs.read('reference/child/' + rid + '/' + decoder, host_root / relative(command['receipt']), command['sha256']))
            need(receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int and receipt['returncode'] == code and
                 type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0 and receipt.get('timed_out', False) is False and
                 receipt.get('interrupted', False) is False and not receipt.get('error_type'), 'Actual recorded child terminal differs')
        info = original['decoded']['libvorbis']
        wav = inputs.read('reference/wav/' + rid, folder / 'libvorbis.wav', info['wav_sha256'])
        reference = wav_pcm(wav, case['rate'], sum(case['frames']))
        need(sha(reference) == accepted['pcm_sha256'] == info['pcm_sha256'], 'Actual qualified Xiph PCM differs')
        frame_checksums(inputs.read('reference/framemd5/' + rid, folder / 'decode-libvorbis.stdout.log'), reference, case['rate'], case['frames'])
        value = pcm['pcm']
        row = dict(case=index, id=case['id'], lookup_type=source['vector_book']['lookup_type'],
            dimensions=source['vector_book']['dimensions'], sequence_p=source['vector_book']['sequence_p'],
            original_native_failure_kind=accepted['native_failure_kind'], original_native_returncode=accepted['native_actual_returncode'],
            rate=case['rate'], channels=2, bits=16, reference_id=rid, packet_offsets=pcm['packet_offsets'],
            comparison=compare(reference, value, case['pcm']), alignment=alignment(reference, value, 8),
            reference_transition_nonzero=transition_counts(reference, case, pcm['packet_offsets']),
            target_transition_nonzero=transition_counts(value, case, pcm['packet_offsets']))
        rows.append(row)
        xiph[case['id']], actual[case['id']] = reference, value
        result['cases'] = rows
        save()
    metamorphic = dict(xiph_triples=relations(xiph, TRIPLES), target_triples=relations(actual, TRIPLES),
        xiph_different_pairs=relations(xiph, DIFFERENT_PAIRS, kind='different'), target_different_pairs=relations(actual, DIFFERENT_PAIRS, kind='different'))
    need(all(row['expected_relation_observed'] for name, group in metamorphic.items() if name.startswith('xiph') for row in group), 'Qualified independent Xiph relations changed')
    policy, bounded = bounded_policy(rows, metamorphic, args.max_abs_error)
    inputs.current()
    result.update(measurement_completed=True, actual_reference_compared=True, cases=rows, metamorphic_relations=metamorphic,
        policy=policy, bounded_corpus_pcm_qualified=bounded, original_dual_reference_passed=False,
        original_reference_failures=host['failures'], original_reference_report_sha256=refs['host']['sha256'],
        original_native_lookup2_refusals=4, original_native_packet_decode_failures=4, original_native_cause_diagnosed=False,
        prior25_floor0_wide_regressions_record_only=True, prior_capture_requalified=False,
        result='BOUNDED_CORPUS_PCM_QUALIFIED' if bounded else 'BOUNDED_CORPUS_PCM_REJECTED')
    save()
    return 0 if bounded else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'target', 'target-terminal', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--target-report-sha256', required=True)
    parser.add_argument('--readiness-sha256', required=True)
    parser.add_argument('--max-abs-error', type=int, choices=(2,), default=2)
    args = parser.parse_args()
    need(re.fullmatch('[0-9a-f]{64}', args.target_report_sha256), 'Explicit reviewed actual target report SHA256 required')
    need(re.fullmatch('[0-9a-f]{64}', args.readiness_sha256), 'Explicit reviewed source readiness SHA256 required')
    output, repo = args.output.resolve(), args.repository.resolve()
    here = Path(__file__).resolve().parent
    need(output.parent == repo / '.build' and not output.exists() and not args.target.resolve().is_relative_to(output)
         and not here.is_relative_to(output), 'Fresh independent direct .build output required')
    output.mkdir()
    result = dict(result='INCOMPLETE', measurement_completed=False, actual_reference_compared=False,
        bounded_corpus_pcm_qualified=False, passed=False, numeric_reference_qualified=False, format_corpus_qualified=False,
        format_conformance_qualified=False, checked_only=True, vendor_comparison_available=False,
        full_G6_qualified=False, physical_device=False, production_radio_integration=False,
        fixed_project_bound_LSB=2, prior_capture_requalified=False, cases=[])
    def save():
        temp = output / 'report.json.tmp'
        temp.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
        temp.replace(output / 'report.json')
    save()
    try:
        code = run(args, result, save)
    except BaseException as error:
        result.update(result='INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'INPUT_OR_MEASUREMENT_REJECTED',
            measurement_completed=False, actual_reference_compared=False, bounded_corpus_pcm_qualified=False,
            error_type=type(error).__name__, error=str(error))
        save()
        return 130 if isinstance(error, KeyboardInterrupt) else 1
    print(json.dumps({name: result[name] for name in ('result', 'measurement_completed', 'bounded_corpus_pcm_qualified')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
