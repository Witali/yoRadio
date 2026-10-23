"""Read actual recorded reference commands; never execute a reference/process."""
import json
from pathlib import Path, PureWindowsPath
from pcm_metrics import need

NATIVE_LOOKUP2_REFUSAL = 3199971767


def argv_for(ffmpeg, folder, decoder):
    return [ffmpeg, '-nostdin', '-n', '-hide_banner', '-loglevel', 'error', '-xerror', '-err_detect', 'explode',
        '-c:a', decoder, '-i', str(folder / 'input.ogg'), '-map', '0:a:0', '-map_metadata', '-1', '-fflags', '+bitexact',
        '-flags:a', '+bitexact', '-c:a', 'pcm_s16le', '-f', 'wav', str(folder / (decoder + '.wav')),
        '-map', '0:a:0', '-map_metadata', '-1', '-flags:a', '+bitexact', '-c:a', 'pcm_s16le', '-f', 'framemd5', '-']


def command(inputs, state, raw, decoder):
    scope, host_root, host, commands = (state[key] for key in ('scope', 'host_root', 'host', 'commands'))
    reference_id = raw['id']
    entry = commands['cases/' + reference_id + '/decode-' + decoder]
    path = host_root / entry['receipt']
    need(path.resolve().is_relative_to(host_root) and path.name == 'decode-' + decoder + '.json', 'Reference child receipt boundary/role')
    role = 'reference/' + scope['host_path'] + '/' + reference_id + '/' + decoder
    receipt = json.loads(inputs.read(role + '/receipt', path, entry['sha256']))
    expected_code = 0 if decoder in raw['decoded'] else NATIVE_LOOKUP2_REFUSAL
    ffmpeg = next(origin for origin in host['tools'] if PureWindowsPath(origin).name == 'ffmpeg.exe')
    need(receipt.get('status') == 'TERMINAL' and type(receipt.get('returncode')) is int and receipt['returncode'] == expected_code and
         type(receipt.get('owned_pid')) is int and receipt['owned_pid'] > 0 and receipt.get('timed_out', False) is False and
         receipt.get('interrupted', False) is False and not receipt.get('error_type') and 'returncode_after_stop' not in receipt and
         receipt['runner_sha256'] == host['capture_sha256'] and receipt['executable_sha256'] == host['tools'][ffmpeg] and
         receipt['argv'] == argv_for(ffmpeg, path.parent, decoder) and receipt['timeout_seconds'] == 30 and
         Path(receipt['cwd']).resolve() == host_root.parents[1],
         'Exact actual strict reference child terminal/tool/argv; no gain/trim/resampling')
    need(len(receipt['logs']) == 2, 'Both actual reference streams required')
    streams = {}
    for stream in ('stdout', 'stderr'):
        filename = 'decode-' + decoder + '.' + stream + '.log'
        candidates = [row for origin, row in receipt['logs'].items() if PureWindowsPath(origin).name == filename]
        need(len(candidates) == 1, 'Unique actual reference stream')
        row = candidates[0]
        streams[stream] = inputs.read(role + '/' + stream, path.parent / filename, row['sha256'], row['bytes'])
    if expected_code:
        need(decoder == 'vorbis' and not streams['stdout'] and b'Codebook lookup type not supported.' in streams['stderr'],
             'Only exact documented native lookup2 refusals may lack PCM')
    else:
        need(not streams['stderr'], 'Strict accepted reference emitted an error')
    return receipt, streams


def full_new12(inputs, state, frozen, wav_pcm, frame_checksums, sha):
    """Check all24 existing new12 receipts/WAVs, including its six old originals."""
    scope, host_root, host, qualified = (state[key] for key in ('scope', 'host_root', 'host', 'qualified'))
    need(len(host['cases']) == len(qualified['cases']) == 12 and len(state['commands']) == 24, 'Exact full new12 scope required')
    pcms = {}
    for raw, accepted in zip(host['cases'], qualified['cases']):
        case = raw['input']
        need(accepted['id'] == raw['id'] and accepted['xiph_reference_revalidated'] is True and
             accepted['native']['returncode'] == NATIVE_LOOKUP2_REFUSAL and accepted['native']['PCM_accepted'] is False and
             case['rate'] == accepted['rate'] == 48000 and case['channels'] == accepted['channels'] == 2 and accepted['bits'] == 16,
             'Actual full12 qualified reference metadata/support')
        matrix = Path(raw['source_matrix'])
        parts = {}
        for kind in ('identification', 'setup', 'audio', 'ogg'):
            source = matrix.parent / case[kind]
            identity = host['inputs'][str(source.resolve())]
            parts[kind] = frozen('reference/full12/raw/' + raw['id'] + '/' + kind, source, identity['sha256'], identity.get('bytes'))
        need(len(parts['identification']) == 30 and parts['identification'][:7] == b'\x01vorbis' and
             parts['identification'][11] == 2 and int.from_bytes(parts['identification'][12:16], 'little') == 48000 and
             parts['setup'][:7] == b'\x05vorbis', 'Full12 actual raw header identity')
        folder = host_root / 'cases' / raw['id']
        need(inputs.read('reference/full12/carrier/' + raw['id'], folder / 'input.ogg', raw['ogg_sha256']) == parts['ogg'],
             'Actually decoded full12 carrier differs from raw source')
        for decoder in ('vorbis', 'libvorbis'):
            _, streams = command(inputs, state, raw, decoder)
            if decoder == 'vorbis':
                continue
            info = raw['decoded']['libvorbis']
            data = inputs.read('reference/full12/wav/' + raw['id'], folder / 'libvorbis.wav', info['wav_sha256'])
            pcm = wav_pcm(data, 48000, sum(case['expected_packet_frames']))
            frame_checksums(streams['stdout'], pcm, 48000, case['expected_packet_frames'])
            need(sha(pcm) == accepted['pcm_sha256'] == info['pcm_sha256'] and len(pcm) == accepted['pcm_bytes'] ==
                 info['pcm_bytes'] == case['expected_s16le_bytes'], 'Complete actual full12 WAV/framemd5/qualified PCM')
            pcms[case['id']] = pcm
    relations = []
    for relation in scope['exact_equivalence_relations']:
        first, second = relation['original_id'], relation['equivalent_id']
        need(pcms[first] == pcms[second] and sha(pcms[first]) == relation['historical_pcm_sha256'],
             'Actual full12 Xiph/historical six exact relations')
        relations.append(dict(original_id=first, equivalent_id=second, byte_equal=True, pcm_sha256=sha(pcms[first])))
    need(len(relations) == 6 and len(host['metamorphic_checks']) == 12 and
         all(row['passed'] is (row['decoder'] == 'libvorbis') for row in host['metamorphic_checks']),
         'Original full12 native-unavailable/Xiph-equal relation accounting')
    return dict(scope='separate_actual_new12', actual_existing_children_checked=24,
        xiph_complete_WAVs_checked=12, native_lookup2_refusals=12, exact_PCM_relations=relations,
        original_outer_returncode=1, original_dual_reference_passed=False, new_reference_commands_executed=False)
