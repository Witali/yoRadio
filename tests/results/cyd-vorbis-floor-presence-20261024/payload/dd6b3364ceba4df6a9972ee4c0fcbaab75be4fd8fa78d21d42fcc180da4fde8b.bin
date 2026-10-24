"""Portable recorded-evidence replay only; no decoder, process, SDK or device."""
import argparse
import gzip
import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys
import tempfile


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()


def safe(value):
    path = PurePosixPath(str(value).replace('\\', '/'))
    need(str(value) and not path.is_absolute() and '..' not in path.parts and ':' not in str(path), 'safe archive-relative path')
    return path.as_posix()


def run(args):
    root = args.root.resolve()
    manifest_raw = (root / 'manifest.json').read_bytes()
    need(sha(manifest_raw) == args.manifest_sha256, 'independently pinned manifest SHA')
    manifest = json.loads(manifest_raw)
    expected_files = {'manifest.json'}
    for row in manifest['files']:
        name = safe(row['path']); need(name not in expected_files, 'distinct physical manifest members')
        expected_files.add(name); path = root / name
        need(path.resolve().is_relative_to(root) and not path.is_symlink(), 'physical archive boundary')
        data = path.read_bytes()
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'physical archive SHA closure:' + name)
    need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == expected_files,
         'exact physical archive member set')
    inventory = json.loads((root / 'inventory.json').read_bytes()); entries = inventory['files']
    original = PureWindowsPath(inventory['original_worktree'])
    cache = {}

    def get(name):
        name = safe(name); need(name in entries, 'selected logical member:' + name)
        row = entries[name]; storage = safe(row['stored'])
        need(storage in expected_files and storage.startswith('payload/'), 'manifested payload storage')
        if storage not in cache:
            raw = (root / storage).read_bytes()
            need(row['encoding'] in ('gzip', 'raw'), 'known storage encoding')
            cache[storage] = gzip.decompress(raw) if row['encoding'] == 'gzip' else raw
        data = cache[storage]
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'logical source SHA:' + name)
        return data

    def doc(name): return json.loads(get(name))

    for name in entries: get(name)
    need(len(entries) == inventory['logical_files'] and
         sum(row['bytes'] for row in entries.values()) == inventory['decoded_logical_bytes'], 'logical inventory totals')
    need({row['stored'] for row in entries.values()} == {p for p in expected_files if p.startswith('payload/')},
         'no unreferenced or missing payloads')
    host_name = '.build/cyd-vorbis-floor-presence-host-01'
    target_name = '.build/cyd-vorbis-floor-presence-target-01'
    runtime_name = '.build/cyd-vorbis-floor-presence-runtime-01'
    root_name = '.build/cyd-vorbis-floor-presence-root-01'
    numeric_name = '.build/cyd-vorbis-floor-presence-numeric-01'
    corpus_name = '.build/cyd-vorbis-floor-presence-corpus-01'
    source_name = '.build/cyd-vorbis-floor-presence-runtime-prep-01'
    for directory in ('.build/cyd-vorbis-floor-presence-prep-01', '.build/cyd-vorbis-floor-presence-prep-02',
                      source_name, '.build/cyd-vorbis-floor-presence-source-clarification-01'):
        readiness = doc(directory + '/readiness.json')
        for row in readiness['files']:
            raw = get(directory + '/' + safe(row['path']))
            need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'immutable preparation/readiness closure')
    host, target = doc(host_name + '/report.json'), doc(target_name + '/report.json')
    numeric, saved = doc(numeric_name + '/report.json'), doc(runtime_name + '/contract.json')
    aliases = {}
    for directory, report in ((host_name, host), (target_name, target)):
        for source, row in report['inputs'].items():
            name = directory + '/' + safe(row['snapshot']); raw = get(name)
            need(sha(raw) == row['sha256'] and ('bytes' not in row or len(raw) == row['bytes']), 'frozen original/source alias')
            key = str(PureWindowsPath(source)).casefold()
            need(key not in aliases or get(aliases[key]) == raw, 'consistent declared source aliases')
            aliases[key] = name
    omissions = json.loads((root / 'omissions.json').read_bytes())
    omitted = {str(PureWindowsPath(row['path'])).casefold(): row for row in omissions['items']}

    def source(path, expected=None, size=None, allow_recorded_omission=False):
        windows = PureWindowsPath(path); key = str(windows).casefold()
        try: direct = windows.relative_to(original).as_posix()
        except ValueError: direct = None
        name = direct if direct in entries else aliases.get(key)
        if name is None:
            need(allow_recorded_omission and key in omitted and expected == omitted[key]['sha256'],
                 'no current-file fallback; explicit recorded omission:' + str(path))
            return None
        raw = get(name)
        need(expected is None or sha(raw) == expected, 'absolute source SHA binding')
        need(size is None or len(raw) == size, 'absolute source size binding')
        return raw

    # Ordinary imports use the exact archived module bytes. No function/global
    # replacement and no import of the archived driver/controller entrypoints.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root / 'helpers'))
    helper_names = ('protocol', 'pcm_witness', 'recorded_qualification', 'carrier', 'mono_metrics', 'pcm_metrics', 'policy39')
    for name in helper_names:
        need((root / 'helpers' / (name + '.py')).read_bytes() == get(source_name + '/' + name + '.py'), 'exact frozen ordinary helper:' + name)
        need(name not in sys.modules, 'fresh ordinary helper namespace:' + name)
    protocol = importlib.import_module('protocol')
    recorded = importlib.import_module('recorded_qualification')
    mono_metrics = importlib.import_module('mono_metrics'); pcm_metrics = importlib.import_module('pcm_metrics')
    policy = importlib.import_module('policy39')
    carrier = sys.modules['carrier']
    for name in helper_names:
        need(Path(sys.modules[name].__file__).resolve() == root / 'helpers' / (name + '.py'), 'archive-only helper import')

    wrapper_sha = sha(get('.build/cyd-vorbis-format-command-01.py'))
    outer_names = ('generate', 'test_controls', 'test_reference_numeric', 'canonical-generate', 'canonical-controls',
                   'host', 'seal-reference', 'qualification', 'runtime-preparation', 'seal-numeric', 'numeric')
    for name in outer_names:
        receipt = doc(root_name + '/' + name + '-command.json'); recorded.terminal(receipt, 0)
        need(receipt['runner_sha256'] == wrapper_sha, 'actual root wrapper identity')
        for path, row in receipt['logs'].items(): source(path, row['sha256'], row['bytes'])
    for name, count in (('test_controls', 17), ('test_reference_numeric', 13), ('canonical-controls', 17)):
        text = get(root_name + '/' + name + '-command.stderr.log').decode().replace('\r\n', '\n')
        need(re.search(r'Ran ' + str(count) + r' tests? in ', text) and re.search(r'^OK$', text, re.M), 'actual archived control count and OK')

    matrix_raw = get(corpus_name + '/matrix.json'); matrix = json.loads(matrix_raw)
    corpus_manifest = doc(corpus_name + '/manifest.json')
    need(len(corpus_manifest['files']) + 1 == 198 and len(matrix['cases']) == 39 and matrix['total_packets'] == 546 and
         matrix['expected_total_s16le_bytes'] == 971520 and matrix['case_mask'] == 549755813887,
         'full original198 / matrix39/546/971520')
    for row in corpus_manifest['files']:
        raw = get(corpus_name + '/' + safe(row['path']))
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'original corpus manifest identity')
    need(get(runtime_name + '/inputs/all39/matrix.json') == matrix_raw, 'sealed original matrix bytes')
    need(sha(get('tests/vorbis_format_corpus/generate_floor_presence.py')) == '6191cc695995fda18f04bf2c95faecc40b3f0fdcc15df487cf44aa702a6204e0' and
         get('tests/vorbis_floor_presence/test_controls.py') == get(source_name + '/test_controls.py'), 'canonical exact source promotion')
    canonical_name = '.build/cyd-vorbis-floor-presence-canonical-01'
    canonical_manifest = doc(canonical_name + '/manifest.json')
    for row in canonical_manifest['files']:
        raw = get(canonical_name + '/' + safe(row['path']))
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'canonical corpus full manifest')
    for row in corpus_manifest['files']:
        need(get(corpus_name + '/' + row['path']) == get(canonical_name + '/' + row['path']), 'all197 nonmanifest original/canonical files identical')

    terminal = doc(root_name + '/target-terminal.json')
    need(terminal['schema'] == 'direct-exec-tool-terminal-v1' and terminal['exit_code'] == 0 and
         terminal['report_sha256'] == sha(get(target_name + '/report.json')) and
         terminal['entrypoint_sha256'] == sha(get(runtime_name + '/run-cyd-vorbis-floorpresence39-qemu.py')),
         'actual archived target direct-tool terminal0/report/controller')
    need(target['result'] == 'CHECKED_CORPUS_PCM_CAPTURED' and target['completed'] is target['target_capture_completed'] is True and
         target['checked_decode_completed'] is True and target['full_G6_qualified'] is False, 'actual finite target capture classification')
    commands = ('sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')
    need(tuple(row['name'] for row in target['commands']) == commands, 'exact inherited nine-command target workflow')
    for row in target['commands']:
        need(row['state'] == 'complete' and type(row['exit_status']) is int and row['exit_status'] == 0 and
             row['timed_out'] is row['interrupted'] is False and type(row['pid']) is int and row['pid'] > 0, 'actual target child terminal0')
        for stream in ('stdout', 'stderr'):
            need(sha(get(target_name + '/' + row['name'] + '.' + stream + '.log')) == row[stream + '_sha256'], 'target child stream identity')
    for path, row in target['sdk_build_logs'].items():
        data = get(target_name + '/' + path); need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'actual SDK build log')
    for scope, report in (('host', host), ('target', target)):
        for path, digest in report['tools'].items():
            key = str(PureWindowsPath(path)).casefold()
            need(key in omitted and omitted[key]['sha256'] == digest and omitted[key]['body_retained'] is False,
                 'recorded-only external tool/archive identity')
    for path, digest in target['build_outputs'].items():
        logical = target_name + '/' + safe(path)
        if logical in entries: need(sha(get(logical)) == digest, 'retained text build-context identity')
        else:
            key = str(PureWindowsPath(str(original) + '/' + logical)).casefold()
            need(key in omitted and omitted[key]['sha256'] == digest and omitted[key]['body_retained'] is False, 'explicit omitted build binary')

    need(host['completed'] is host['xiph_reference_qualified'] is host['dual_reference_qualified'] is True and
         host['failures'] == [] and len(host['cases']) == 39 and len(host['commands']) == 78 and
         host['cross_reference_pcm16_max_error_allowed'] == 2, 'complete actual dual reference39/78 PASS')
    qualification = doc('.build/cyd-vorbis-floor-presence-qualification-01/qualification.json')
    need(qualification['result'] == 'DUAL_REFERENCE_QUALIFIED' and qualification['profile'] == 'floorpresence39' and
         (qualification['xiph_cases'], qualification['native_compared'], qualification['native_lookup2_refusals'],
          qualification['paired_raw_packets'], qualification['expected_pcm_bytes']) == (39, 39, 0, 546, 971520) and
         qualification['original_report_sha256'] == sha(get(host_name + '/report.json')), 'separate actual recorded-reference qualification')
    for row in qualification['validated_inputs'].values(): source(row['path'], row['sha256'], row['bytes'], True)
    for row in numeric['inputs'].values(): source(row['path'], row['sha256'], row['bytes'], True)
    children = {row['name']: row for row in host['commands']}; need(len(children) == 78, 'unique78 child commands')
    measured = []
    with tempfile.TemporaryDirectory(prefix='floor-presence39-archive-') as temporary:
        folder = Path(temporary)
        # Only archived original data is hydrated. Original absolute paths are
        # evidence labels, never live filesystem read targets.
        for row in corpus_manifest['files']:
            relative = safe(row['path']); destination = folder / relative
            destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(get(corpus_name + '/' + relative))
        contract = protocol.load_contract([dict(path=str(folder / 'matrix.json'), sha256=sha(matrix_raw))])
        need(contract['model'] == saved['model'] and contract['contract_sha256'] == saved['contract_sha256'], 'portable relocation keeps full contract model and ID')
        log = get(target_name + '/qemu.stdout.log').decode(errors='replace') + '\n' + get(target_name + '/qemu.stderr.log').decode(errors='replace')
        qemu = target['commands'][6]
        observed = protocol.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
            interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
        captured = observed.pop('case_pcm')
        need(observed == target['observed'] and observed['protocol_lines'] == 1212 and len(captured) == len(target['observed_pcm']) == 39,
             'exact full1212 protocol replay and39 complete streams')

        def transitions(pcm, case, offsets):
            counts = {name: [0] * case['channels'] for name in ('SS', 'SL', 'LS', 'LL')}
            for packet in range(1, 14):
                label = 'SL'[case['modes'][packet - 1]] + 'SL'[case['modes'][packet]]
                first, stop = offsets[packet:packet + 2]
                for channel in range(case['channels']):
                    counts[label][channel] += sum(pcm[p:p + 2] != b'\0\0' for p in range(first + 2 * channel, stop, 2 * case['channels']))
            return counts

        for index, (case, raw_case, item, stored, host_case, qcase, recorded_row) in enumerate(zip(
                contract['model']['cases'], matrix['cases'], captured, target['observed_pcm'], host['cases'], qualification['cases'], numeric['cases'])):
            need(case['id'] == raw_case['id'] == item['id'] == stored['id'] == recorded_row['id'] and
                 host_case['id'] == qcase['id'] == '0-' + case['id'] and host_case['input'] == raw_case and
                 host_case['source_matrix_sha256'] == sha(matrix_raw), 'all39 case/source/recorded order binding')
            parts = {kind: get(corpus_name + '/' + raw_case[kind]) for kind in ('identification', 'comment', 'setup', 'audio', 'ogg')}
            pages = carrier.packets(parts['ogg'])
            need(len(pages) == 17 and [row['data'] for row in pages[:3]] == [parts[k] for k in ('identification', 'comment', 'setup')] and
                 [row['data'] for row in pages[3:]] == [parts['audio'][a:b] for a, b in zip(case['offsets'], case['offsets'][1:])],
                 'original full CRC carrier/raw packet equivalence')
            granule = 0
            for packet, page in enumerate(pages[3:]):
                granule += case['frames'][packet]
                need(page['granule'] == granule and page['eos'] == (packet == 13), 'natural packet granules and EOS')
            pcm = get(target_name + '/' + safe(stored['path']))
            need(pcm == item['pcm'] and sha(pcm) == stored['sha256'] == item['sha256'] and
                 stored['bytes'] == len(pcm) == case['total_pcm'] and stored['packet_offsets'] == item['packet_offsets'], 'every persisted target PCM byte')
            metric = mono_metrics if case['channels'] == 1 else pcm_metrics
            refs, streams, details = {}, {}, {}
            for decoder in ('vorbis', 'libvorbis'):
                role = 'cases/0-' + case['id'] + '/decode-' + decoder
                command = children[role]; receipt = doc(host_name + '/' + safe(command['receipt']))
                need(sha(get(host_name + '/' + command['receipt'])) == command['sha256'], 'actual host child receipt identity')
                recorded.terminal(receipt, 0); argv = receipt['argv']
                need(receipt['runner_sha256'] == wrapper_sha and receipt['executable_sha256'] == host['tools'][argv[0]] and
                     argv[argv.index('-c:a') + 1] == decoder and '-ar' not in argv and '-ac' not in argv and
                     '-xerror' in argv and argv[argv.index('-err_detect') + 1] == 'explode', 'actual strict explicit decoder identity/options')
                for path, row in receipt['logs'].items(): source(path, row['sha256'], row['bytes'])
                need(source(argv[argv.index('-i') + 1]) == get(corpus_name + '/' + raw_case['ogg']), 'actual host carrier input binding')
                base = host_name + '/cases/0-' + case['id'] + '/'
                need(get(base + 'decode-' + decoder + '.stderr.log') == b'', 'strict reference has no diagnostics')
                wav, md5 = get(base + decoder + '.wav'), get(base + 'decode-' + decoder + '.stdout.log')
                reference, info = recorded.decoded_pcm(wav, md5, case['rate'], case['channels'], case['frames'], case['modes'], raw_case)
                need(info == host_case['decoded'][decoder] and len(reference) == len(pcm), 'full78 WAV/MD5/PTS/frame/silence replay')
                comparison = metric.compare(reference, pcm, case['pcm'])
                refs[decoder] = dict(comparison=comparison, alignment_diagnostic=metric.alignment(reference, pcm, 8),
                    reference_transition_nonzero=transitions(reference, case, item['packet_offsets']),
                    target_transition_nonzero=transitions(pcm, case, item['packet_offsets']))
                need(refs[decoder] == recorded_row['references'][decoder] and policy.whole(comparison, case['channels'])['max_abs_error'] <= 2,
                     'complete raw78 comparison replay under unchanged2LSB bound')
                streams[decoder], details[decoder] = reference, info
            cross = metric.compare(streams['vorbis'], streams['libvorbis'], case['pcm'])
            need(cross == recorded_row['original_reference_cross_comparison'] and details == recorded_row['original_reference_metadata'] and
                 policy.whole(cross, case['channels'])['max_abs_error'] == host_case['cross_reference_max_abs_error'] == qcase['cross_reference_max_abs_error'] and
                 policy.whole(cross, case['channels'])['max_abs_error'] <= 2, 'full original cross-reference comparison replay')
            measured.append(dict(case=index, id=case['id'], rate=case['rate'], channels=case['channels'], bits=16,
                frames=case['frames'], packet_bytes=case['pcm'], pcm_bytes=len(pcm), floor_masks=case['floor_masks'],
                packet_offsets=item['packet_offsets'], reference_id='0-' + case['id'], references=refs,
                original_reference_cross_comparison=cross, original_reference_metadata=details))
    actual_policy, accepted = policy.bounded_policy(measured, 2)
    need(measured == numeric['cases'] and actual_policy == numeric['policy'] and accepted and
         numeric['result'] == 'BOUNDED_CORPUS_PCM_QUALIFIED' and numeric['measurement_completed'] is True and
         numeric['bounded_corpus_pcm_qualified'] is True and numeric['full_G6_qualified'] is False and
         numeric['target_report_sha256'] == terminal['report_sha256'] and
         numeric['target_terminal_sha256'] == sha(get(root_name + '/target-terminal.json')), 'exact recorded full numerical qualification')
    need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == expected_files, 'verification added no archive files')
    print(json.dumps(dict(archive_consistent=True, recorded_cases=39, recorded_packets=546,
        recorded_PCM_bytes=971520, replayed_reference_streams=78, replayed_target_reference_comparisons=78,
        max_abs_error_bound=2, recorded_bounded_result_reproduced=True, new_target_execution=False,
        current_external_tools_rehashed=False, full_dependency_walk_verified=False, full_G6_qualified=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True); parser.add_argument('--manifest-sha256', required=True)
    run(parser.parse_args())
