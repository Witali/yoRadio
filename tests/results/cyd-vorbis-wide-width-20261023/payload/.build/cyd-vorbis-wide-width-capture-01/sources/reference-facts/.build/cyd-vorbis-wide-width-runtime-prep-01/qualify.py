"""Pure recorded-reference qualification; never launches a decoder or process."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import struct
import wave
from carrier import packets


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    path = PurePosixPath(str(value).replace('\\', '/'))
    need(str(value) and not path.is_absolute() and '..' not in path.parts and ':' not in str(path), 'Unsafe relative path')
    return path.as_posix()


class Inputs:
    def __init__(self):
        self.rows = {}

    def read(self, role, path, expected=None, size=None):
        path = Path(path).resolve()
        data = path.read_bytes()
        row = dict(path=str(path), bytes=len(data), sha256=sha(data))
        need(expected is None or row['sha256'] == expected, 'Input SHA mismatch: ' + role)
        need(size is None or row['bytes'] == size, 'Input size mismatch: ' + role)
        need(role not in self.rows or self.rows[role] == row, 'Input role changed: ' + role)
        self.rows[role] = row
        return data

    def current(self):
        for role, row in self.rows.items():
            data = Path(row['path']).read_bytes()
            need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Input changed during qualification: ' + role)


def terminal(receipt, code):
    need(receipt.get('status') == 'TERMINAL' and type(receipt.get('returncode')) is int and
         receipt['returncode'] == code and type(receipt.get('owned_pid')) is int and receipt['owned_pid'] > 0 and
         receipt.get('timed_out', False) is False and receipt.get('interrupted', False) is False and
         not receipt.get('error_type') and 'returncode_after_stop' not in receipt,
         'Actual terminal/non-timeout/non-interrupted process facts required')


def decoded_pcm(wav, md5_text, rate, channels, frames, modes):
    with wave.open(io.BytesIO(wav), 'rb') as stream:
        need(stream.getcomptype() == 'NONE' and stream.getframerate() == rate and stream.getnchannels() == channels and
             stream.getsampwidth() == 2 and stream.getnframes() == sum(frames), 'Actual WAV metadata/frame count')
        pcm = stream.readframes(sum(frames) + 1)
    need(len(pcm) == sum(frames) * channels * 2, 'Complete WAV PCM required')
    text = md5_text.decode().replace('\r\n', '\n')
    need(re.search(r'^#tb 0: 1/' + str(rate) + '$', text, re.M) and
         re.search(r'^#sample_rate 0: ' + str(rate) + '$', text, re.M) and '#codec_id 0: pcm_s16le' in text,
         'Actual framemd5 metadata')
    need(re.search(r'^#channel_layout_name 0: (?:2 channels|stereo)$', text, re.M), 'Actual stereo framemd5 layout')
    rows = [line for line in text.splitlines() if line.strip() and not line.startswith('#')]
    need(len(rows) == len(frames) - 1 and frames[0] == 0, 'Exact nonprimer packet count')
    cursor = timestamp = 0
    transition_bytes, transition_channels = {}, {}
    for index, (line, count) in enumerate(zip(rows, frames[1:]), 1):
        fields = [item.strip() for item in line.split(',')]
        size = count * channels * 2
        need(len(fields) == 6 and [int(x) for x in fields[:5]] == [0, timestamp, timestamp, count, size],
             'Actual packet PTS/duration/PCM size')
        chunk = pcm[cursor:cursor + size]
        need(hashlib.md5(chunk).hexdigest() == fields[5], 'Actual packet MD5 differs from WAV PCM')
        kind = 'SL'[modes[index - 1]] + 'SL'[modes[index]]
        transition_bytes[kind] = transition_bytes.get(kind, 0) + sum(value != 0 for value in chunk)
        counts = transition_channels.setdefault(kind, [0] * channels)
        for channel in range(channels):
            counts[channel] += sum(chunk[pos:pos + 2] != b'\0\0' for pos in range(channel * 2, len(chunk), channels * 2))
        cursor += size
        timestamp += count
    need(cursor == len(pcm) and set(transition_bytes) == {'SS', 'SL', 'LS', 'LL'} and
         all(transition_bytes.values()) and all(all(values) for values in transition_channels.values()),
         'Every channel must be nonzero in every present transition')
    return pcm, dict(rate=rate, channels=channels, bits=16, frames=frames[1:], pcm_bytes=len(pcm),
        nonzero_bytes=sum(value != 0 for value in pcm), transition_nonzero_bytes=transition_bytes,
        transition_nonzero_frames_per_channel=transition_channels, wav_sha256=sha(wav), pcm_sha256=sha(pcm))


def qualify(args, result, save):
    pins = json.loads(Path(__file__).with_name('pins.json').read_bytes())
    profile = pins['profiles'][args.profile]
    inputs = Inputs()
    result['validated_inputs'] = inputs.rows
    repo, root = args.repository.resolve(), args.campaign.resolve()
    inputs.read('qualifier/pins', Path(__file__).with_name('pins.json'))
    inputs.read('qualifier/script', __file__)
    inputs.read('qualifier/carrier', Path(__file__).with_name('carrier.py'), pins['carrier_source']['proposed_helper_sha256'])
    raw_report = inputs.read('report', root / 'report.json', profile['report_sha256'])
    report = json.loads(raw_report)
    outer = json.loads(inputs.read('outer-receipt', args.outer, profile['outer_sha256']))
    terminal(outer, profile['outer_returncode'])
    need(report['schema'] == 'public-vorbis-format-corpus-host-v1' and report['completed'] is True and
         report['target_executed'] is False and report['production_changed'] is False and
         report['driver_sha256'] == pins['driver_sha256'] and report['parser_source_sha256'] == pins['parser_sha256'] and
         report['capture_sha256'] == pins['capture_sha256'] == outer['runner_sha256'] and
         report['cross_reference_pcm16_max_error_allowed'] == 2, 'Pinned driver/scope/policy differs')
    for row in pins['supporting_source_inputs']:
        inputs.read('supporting/' + row['path'], repo / relative(row['path']), row['sha256'], row['bytes'])
    for origin, row in outer['logs'].items():
        inputs.read('outer-log/' + PureWindowsPath(origin).name, args.outer.resolve().parent / PureWindowsPath(origin).name,
                    row['sha256'], row['bytes'])
    need(len(report['tools']) == len(pins['tools']) == 2, 'Exactly the two actual reference tools required')
    for origin, digest in report['tools'].items():
        need(pins['tools'][PureWindowsPath(origin).name] == digest, 'Actual reference tool pin')
        inputs.read('tool/' + origin, Path(origin), digest)
    need(any(PureWindowsPath(path) == PureWindowsPath(outer['argv'][0]) and
             sha_value == outer['executable_sha256'] and PureWindowsPath(path).name == 'python.exe'
             for path, sha_value in report['tools'].items()), 'Actual outer Python identity')
    frozen = {}
    for origin, row in report['inputs'].items():
        rel = PureWindowsPath(origin).relative_to(PureWindowsPath(outer['cwd'])).as_posix()
        need('..' not in PurePosixPath(rel).parts, 'Original source escapes repository')
        actual = inputs.read('original/' + origin, repo / rel, row['sha256'], row['bytes'])
        snapshot = inputs.read('snapshot/' + origin, root / relative(row['snapshot']), row['sha256'], row['bytes'])
        need(actual == snapshot, 'Original/frozen bytes differ')
        frozen[origin] = snapshot
    def source(origin):
        matches = [value for path, value in frozen.items() if PureWindowsPath(path) == PureWindowsPath(origin)]
        need(len(matches) == 1, 'Unbound/ambiguous source input')
        return matches[0]
    matrices = []
    for origin, digest in profile['source_matrices'].items():
        raw = source(origin)
        need(sha(raw) == digest, 'Source matrix pin')
        matrices.append((origin, json.loads(raw)))
    expected = [(index, origin, case) for index, (origin, matrix) in enumerate(matrices) for case in matrix['cases']]
    need(len(expected) == len(report['cases']) == profile['case_count'] and
         [row['id'] for row in report['cases']] == profile['case_ids'], 'Exact case set/order')
    commands = {row['name']: row for row in report['commands']}
    need(len(commands) == len(report['commands']) == profile['case_count'] * 2, 'All actual owned reference receipts required')
    pcm_by_case, rows_out, native_compared, refused = {}, [], 0, 0
    for (mi, origin, case), recorded in zip(expected, report['cases']):
        case_id = str(mi) + '-' + case['id']
        need(recorded['id'] == case_id and recorded['input'] == case and recorded['source_matrix'] == origin and
             recorded['source_matrix_sha256'] == profile['source_matrices'][origin], 'Named case/source identity')
        parts = {kind: source(str(PureWindowsPath(origin).parent / case[kind]))
                 for kind in ('identification', 'comment', 'setup', 'audio', 'ogg')}
        info = parts['identification']
        need(len(info) == 30 and info[:7] == b'\x01vorbis' and info[7:11] == bytes(4) and info[29] & 1 and
             parts['setup'][:7] == b'\x05vorbis' and parts['comment'][:7] == b'\x03vorbis', 'Full public headers')
        rate, channels, short, long = int.from_bytes(info[12:16], 'little'), info[11], 1 << (info[28] & 15), 1 << (info[28] >> 4)
        need((rate, channels, short, long) == tuple(case[key] for key in ('rate', 'channels', 'short', 'long')) and
             channels in (1, 2) and rate > 0 and 64 <= short <= long <= 8192, 'Actual identification metadata')
        modes, offsets = case['mode_flags'], case['offsets']
        need(case['packet_count'] == len(modes) == 14 and len(offsets) == 15 and offsets[0] == 0 and
             offsets[-1] == len(parts['audio']) and all(type(x) is int and x in (0, 1) for x in modes) and
             all(type(x) is int for x in offsets) and all(a < b for a, b in zip(offsets, offsets[1:])), 'Complete raw packet/mode offsets')
        frames = [0] + [((long if a else short) + (long if b else short)) // 4 for a, b in zip(modes, modes[1:])]
        need(frames == case.get('expected_packet_samples', case.get('expected_packet_frames')) and
             sum(frames) == case['expected_raw_samples'] and sum(frames) * channels * 2 == case['expected_s16le_bytes'], 'Independent overlap accounting')
        carrier = packets(parts['ogg'])
        need(len(carrier) == 17 and [row['data'] for row in carrier[:3]] == [parts['identification'], parts['comment'], parts['setup']] and
             [row['data'] for row in carrier[3:]] == [parts['audio'][a:b] for a, b in zip(offsets, offsets[1:])], 'CRC carrier/raw packet equivalence')
        cumulative = 0
        for i, row in enumerate(carrier[3:]):
            cumulative += frames[i]
            first = row['data'][0]
            need(row['granule'] == cumulative and row['eos'] == (i == 13) and first & 3 == modes[i] << 1, 'Carrier mode/granule/EOS')
            if modes[i]:
                need(0 < i < 13 and (first >> 2) & 1 == modes[i - 1] and (first >> 3) & 1 == modes[i + 1], 'Long neighbor flags')
        folder = root / 'cases' / case_id
        need(inputs.read('carrier/' + case_id, folder / 'input.ogg', recorded['ogg_sha256']) == parts['ogg'], 'Actually decoded carrier differs')
        actual_info = {}
        for decoder in ('vorbis', 'libvorbis'):
            name = 'cases/' + case_id + '/decode-' + decoder
            command = commands[name]
            need(command['receipt'] == name + '.json', 'Owned command role/path')
            receipt = json.loads(inputs.read('receipt/' + name, root / relative(command['receipt']), command['sha256']))
            refused_case = decoder == 'vorbis' and profile['native_lookup2_refusals'] > 0
            terminal(receipt, 3199971767 if refused_case else 0)
            need(receipt['runner_sha256'] == pins['capture_sha256'] and
                 receipt['executable_sha256'] == report['tools'][receipt['argv'][0]], 'Actual owned reference tool/capture identity')
            argv = receipt['argv']
            need(argv[argv.index('-c:a') + 1] == decoder and '-ar' not in argv and '-ac' not in argv and
                 '-xerror' in argv and '-err_detect' in argv and argv[argv.index('-err_detect') + 1] == 'explode', 'Actual decoder/unforced metadata options')
            need(PureWindowsPath(argv[argv.index('-i') + 1]) == PureWindowsPath(outer['cwd']) / '.build' / profile['campaign'] / 'cases' / case_id / 'input.ogg', 'Actual input command path')
            wav_options = [i for i, value in enumerate(argv[:-2]) if value == '-f' and argv[i + 1] == 'wav']
            md5_options = [i for i, value in enumerate(argv[:-2]) if value == '-f' and argv[i + 1] == 'framemd5']
            expected_wav = PureWindowsPath(outer['cwd']) / '.build' / profile['campaign'] / 'cases' / case_id / (decoder + '.wav')
            need(len(wav_options) == len(md5_options) == 1 and
                 PureWindowsPath(argv[wav_options[0] + 2]) == expected_wav and argv[md5_options[0] + 2] == '-',
                 'Actual WAV/framemd5 dual output operands')
            need(len(receipt['logs']) == 2, 'Both actual owned streams required')
            for log, row in receipt['logs'].items():
                inputs.read('log/' + name + '/' + PureWindowsPath(log).name, folder / PureWindowsPath(log).name,
                            row['sha256'], row['bytes'])
            stderr = inputs.read('log/' + name + '/decode-' + decoder + '.stderr.log', folder / ('decode-' + decoder + '.stderr.log'))
            if refused_case:
                stdout = inputs.read('log/' + name + '/decode-' + decoder + '.stdout.log', folder / ('decode-' + decoder + '.stdout.log'))
                need(not stdout and b'Codebook lookup type not supported.' in stderr and b'Setup header corrupt.' in stderr and decoder not in recorded['decoded'] and
                     len(recorded['failures']) == 1 and recorded['failures'][0]['stage'] == 'vorbis', 'Only exact documented native lookup2 refusals allowed')
                refused += 1
                continue
            need(not stderr, 'Successful strict reference emitted error diagnostics')
            wav = inputs.read('wav/' + case_id + '/' + decoder, folder / (decoder + '.wav'), recorded['decoded'][decoder]['wav_sha256'])
            md5 = inputs.read('log/' + name + '/decode-' + decoder + '.stdout.log', folder / ('decode-' + decoder + '.stdout.log'))
            pcm, observed = decoded_pcm(wav, md5, rate, channels, frames, modes)
            need(observed == recorded['decoded'][decoder], 'Recomputed PCM evidence differs from report')
            actual_info[decoder] = observed
            pcm_by_case[(mi, case['id'], decoder)] = pcm
        cross_error = None
        if 'vorbis' in actual_info:
            aa, bb = (pcm_by_case[(mi, case['id'], decoder)] for decoder in ('vorbis', 'libvorbis'))
            need(len(aa) == len(bb), 'Crossreference cannot truncate samples')
            av, bv = struct.unpack('<' + 'h' * (len(aa) // 2), aa), struct.unpack('<' + 'h' * (len(bb) // 2), bb)
            cross_error = max(abs(a - b) for a, b in zip(av, bv))
            need(cross_error <= 2 and cross_error == recorded['cross_reference_max_abs_error'] and not recorded['failures'], 'Predeclared bounded crossreference policy failed')
            native_compared += 1
        xiph = actual_info['libvorbis']
        rows_out.append(dict(id=case_id, xiph_qualified=True, native_compared='vorbis' in actual_info,
            native_lookup2_refusal='vorbis' not in actual_info, cross_reference_max_abs_error=cross_error, **xiph))
        result['cases'] = rows_out
        save()
    metamorphic = []
    for mi, (_, matrix) in enumerate(matrices):
        for decoder in ('vorbis', 'libvorbis'):
            for kind, field in (('equal', 'expected_same_decoder_pcm_equal_groups'), ('different', 'expected_same_decoder_pcm_different_pairs')):
                for group in matrix.get(field, []):
                    keys = [(mi, name, decoder) for name in group]
                    available = all(key in pcm_by_case for key in keys)
                    equal = available and all(pcm_by_case[key] == pcm_by_case[keys[0]] for key in keys[1:])
                    observed = available and (equal if kind == 'equal' else not equal)
                    metamorphic.append(dict(decoder=decoder, kind=kind, cases=group, passed=observed))
    need(metamorphic == report['metamorphic_checks'], 'Actual metamorphic PCM relations differ from original report')
    xiph_relations = [row for row in metamorphic if row['decoder'] == 'libvorbis']
    need(len(xiph_relations) == profile['xiph_relations'] and all(row['passed'] for row in xiph_relations) and
         (native_compared, refused) == (profile['native_compared'], profile['native_lookup2_refusals']) and
         len(report['failures']) == refused, 'Complete Xiph/support accounting')
    dual = refused == 0 and all(row['passed'] for row in metamorphic)
    need(report['xiph_reference_qualified'] is True and report['dual_reference_qualified'] is dual and
         dual == (profile['outer_returncode'] == 0), 'Derived classification differs; never rewrite original NONPASS')
    inputs.current()
    result.update(completed=True, reference_corpus_qualified=True, xiph_reference_qualified=True,
        dual_reference_qualified=dual, original_dual_reference_passed=dual,
        original_report_sha256=sha(raw_report), original_outer_receipt_sha256=profile['outer_sha256'],
        xiph_cases=len(rows_out), native_compared=native_compared, native_lookup2_refusals=refused,
        paired_raw_packets=sum(case['input']['packet_count'] for case in report['cases']),
        expected_pcm_bytes=sum(row['pcm_bytes'] for row in rows_out), xiph_metamorphic_checks=xiph_relations,
        original_metamorphic_checks=metamorphic, original_failures=report['failures'],
        policy=pins['cross_reference_policy'], result='DUAL_REFERENCE_QUALIFIED' if dual else 'XIPH_QUALIFIED_DUAL_NONPASS')
    save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('wide12',), required=True)
    for name in ('repository', 'campaign', 'outer', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    repo, output = args.repository.resolve(), args.output.resolve()
    protected = (args.campaign.resolve(), Path(__file__).resolve().parent)
    need(output.is_relative_to(repo / '.build') and output != repo / '.build' and not output.exists() and
         all(not output.is_relative_to(path) and not path.is_relative_to(output) for path in protected), 'Fresh independent .build output required')
    output.mkdir(parents=True, exist_ok=False)
    result = dict(schema='public-vorbis-new-format-reference-qualification-v1', profile=args.profile,
        result='INCOMPLETE', completed=False, reference_corpus_qualified=False, xiph_reference_qualified=False,
        dual_reference_qualified=False, target_executed=False, production_changed=False,
        standard_conformance_qualified=False, full_G6_qualified=False, physical_device=False, cases=[])
    def save():
        temp = output / 'qualification.json.tmp'
        temp.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
        temp.replace(output / 'qualification.json')
    save()
    try:
        qualify(args, result, save)
    except BaseException as error:
        result.update(result='INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'REJECTED', completed=False,
            reference_corpus_qualified=False, xiph_reference_qualified=False, dual_reference_qualified=False,
            error_type=type(error).__name__, error=str(error))
        save()
        return 130 if isinstance(error, KeyboardInterrupt) else 1
    print(json.dumps({key: result[key] for key in ('result', 'reference_corpus_qualified', 'dual_reference_qualified',
                     'xiph_cases', 'native_compared', 'native_lookup2_refusals', 'paired_raw_packets', 'expected_pcm_bytes')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
