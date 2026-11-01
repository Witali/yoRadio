"""Authenticate frozen Opus observations as data, without executing saved code."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import zipfile

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def parse_packet(body):
    need(body, 'nonempty Opus packet, distinct from a missing coded frame')
    toc = body[0]; code = toc & 3; config = toc >> 3
    duration = (480, 960, 1920, 2880)[config % 4] if config < 12 else 480 << (config % 2) if config < 16 else 120 << (config % 4)
    at, end, padding = 1, len(body), 0
    def length():
        nonlocal at
        need(at < end, 'complete frame length')
        value = body[at]; at += 1
        if value >= 252:
            need(at < end, 'complete two-byte frame length')
            value += 4 * body[at]; at += 1
        return value
    if code == 0:
        sizes = [end - at]
    elif code == 1:
        need((end - at) % 2 == 0, 'equal code1 sizes')
        sizes = [(end - at) // 2] * 2
    elif code == 2:
        size = length(); sizes = [size, end - at - size]
    else:
        need(at < end, 'complete frame-count byte')
        control = body[at]; at += 1; count = control & 63
        need(1 <= count <= 48, 'bounded count')
        if control & 64:
            while True:
                need(at < end, 'complete padding length')
                value = body[at]; at += 1; padding += 254 if value == 255 else value
                if value != 255:
                    break
        end -= padding; need(at <= end, 'bounded complete padding')
        if control & 128:
            sizes = [length() for _ in range(count - 1)]
            sizes.append(end - at - sum(sizes))
        else:
            need((end - at) % count == 0, 'complete equal CBR frames')
            sizes = [(end - at) // count] * count
    need(1 <= len(sizes) <= 48 and duration * len(sizes) <= 5760 and
         all(0 <= size <= 1275 for size in sizes), 'legal complete duration and frame extents')
    frames = []
    for size in sizes:
        need(at + size <= end, 'complete coded payload')
        frames.append(body[at:at + size]); at += size
    need(at == end, 'exact encoded body extent')
    return dict(toc=toc, config=config, code=code, sizes=sizes, frames=frames, duration=duration,
                samples=duration * len(frames), padding=padding)


def transport(body):
    need(len(body) >= 28 and body[:8] == b'OPMODE1\0', 'whole creator packet transport')
    channels, skip, logical, count, samples = struct.unpack_from('<5I', body, 8)
    need(channels in (1, 2) and logical > 0 and 1 <= count <= 192, 'bounded complete stream geometry')
    at, packets = 28, []
    for _ in range(count):
        need(at + 4 <= len(body), 'whole packet-length record')
        size = struct.unpack_from('<I', body, at)[0]; at += 4
        need(0 < size <= 61440 and at + size <= len(body), 'whole original encoded packet')
        packets.append(body[at:at + size]); at += size
    need(at == len(body), 'exact packet transport EOF')
    return dict(channels=channels, skip=skip, logical=logical, count=count, samples=samples), packets


def crc(body):
    value = 0
    for byte in body:
        value ^= byte << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value


def check_ogg(body, info, expected, index):
    at, sequence, packets, granules = 0, 0, [], []
    while at < len(body):
        need(at + 27 <= len(body) and body[at:at + 5] == b'OggS\0', 'whole Ogg v0 page')
        count = body[at + 26]; payload = at + 27 + count
        need(payload <= len(body) and count, 'whole nonnil lacing')
        lace = body[at + 27:payload]; end = payload + sum(lace)
        need(end <= len(body) and lace[-1] < 255 and all(n == 255 for n in lace[:-1]), 'one whole original packet per page')
        page = bytearray(body[at:end]); stored = struct.unpack_from('<I', page, 22)[0]; page[22:26] = bytes(4)
        need(crc(page) == stored and struct.unpack_from('<II', page, 14) == (0x504d0000 + index, sequence) and
             page[5] == (2 if sequence == 0 else 4 if end == len(body) else 0), 'actual CRC, serial, sequence and BOS/EOS')
        packets.append(body[payload:end]); granules.append(struct.unpack_from('<Q', page, 6)[0])
        at = end; sequence += 1
    need(sequence == 6 and packets[0] == struct.pack('<8sBBHIhB', b'OpusHead', 1, info['channels'], info['skip'], 48000, 0, 0) and
         packets[1].startswith(b'OpusTags') and packets[2:] == expected and granules[:2] == [0, 0] and
         granules[2:-1] == [info['samples'] * n for n in (1, 2, 3)] and
         granules[-1] == info['skip'] + info['logical'] == info['samples'] * 4 - 13, 'complete headers, unchanged encoded packets and exact playback granules')


def scope(manifest):
    need(manifest['diagnostic_completed'] and not manifest['production_sources_changed'] and not manifest['private_codec_abi'] and
         not manifest['physical_hardware'] and not manifest['production_pipeline_acceptance'] and
         not manifest['full_standard_numeric_qualification'] and not manifest['numeric_tolerance_applied'] and
         not manifest['creator_clipped_integer_cadence_equivalence'], 'precise diagnostic and numeric qualification boundary')


def verify(require_current=False):
    manifest = json.loads((FOLDER / 'manifest.json').read_bytes()); scope(manifest)
    pin = manifest['archive']; path = FOLDER / pin['path']
    need(path.parent == FOLDER and path.name == 'captures.zip' and path.stat().st_size == pin['bytes'] and sha(path.read_bytes()) == pin['sha256'], 'exact complete archive')
    with zipfile.ZipFile(path) as z:
        names = z.namelist(); need(len(names) == len(set(names)) == manifest['physical_blobs'], 'unique full physical census')
        blobs = {name: z.read(name) for name in names}
    for name, body in blobs.items():
        need(name == 'blobs/' + sha(body) and not body.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')), 'exact nonexecutable published blobs')
    files, identities = {}, {}
    for row in manifest['files']:
        name = row['path']; p = PurePosixPath(name); body = blobs[row['blob']]
        need(not p.is_absolute() and '..' not in p.parts and name not in identities and
             len(body) == row['bytes'] and sha(body) == row['sha256'] and p.suffix not in ('.pcm', '.f32', '.bin', '.elf', '.obj', '.a', '.exe'), 'exact unique safe logical bytes')
        files[name] = body; identities[name] = row
    need(len(files) == manifest['logical_files'] and set(blobs) == {row['blob'] for row in manifest['files']}, 'complete logical and physical inventory')
    for row in manifest['omitted_payloads']:
        name = row['path']
        need(name not in identities and row['original_retained_locally'] and row['byte_payload_published'] is False, 'whole retained omissions')
        if row['categories']:
            need('blobs/' + row['sha256'] not in blobs, 'no alternate publication of flagged whole bytes')
        identities[name] = row
    def identity(name, digest, size=None):
        need(name in identities and identities[name]['sha256'] == digest and
             (size is None or identities[name]['bytes'] == size), 'original exact binding: ' + name)
    reports = {}
    for label, campaign in manifest['campaigns'].items():
        body = files[label + '/report.json']; need(sha(body) == campaign['original_report_sha256'], 'original report identity')
        report = json.loads(body); reports[label] = report
        expected = label != 'native01'
        need(campaign['expected_pass'] == expected and report['passed'] == expected and report['completed'] == expected, 'authentic original terminal outcome')
        for command in report['commands']:
            terminal = command['state'] == 'complete' and command['exit_status'] == 0
            need(command['pid'] > 0 and (terminal or label == 'native01' and command['name'] == 'build' and command['exit_status'] == 1), 'actual child terminal status')
            for stream in ('stdout', 'stderr'):
                if isinstance(command.get(stream), dict):
                    row = command[stream]; identity(label + '/' + row['path'], row['sha256'], row['bytes'])
                else:
                    identity(label + '/' + command['name'] + '.' + stream + '.log', command[stream + '_sha256'])
        if campaign['kind'] == 'creator':
            for row in report['sources']:
                identity(label + '/' + row['snapshot'], row['sha256'], row['bytes'])
            if label.startswith('reference'):
                for record in report['cases'].values():
                    for row in record['artifacts'].values():
                        identity(label + '/' + row['path'], row['sha256'], row['bytes'])
            else:
                for record in report['cases'].values():
                    for row in record['files'].values():
                        identity(label + '/' + row['path'], row['sha256'], row['bytes'])
        else:
            sources = json.loads(files[label + '/source-manifest.json'])
            for row in sources.values():
                identity(label + '/' + row['snapshot'], row['sha256'], row['bytes'])
            if label == 'native01':
                need(not report['target_executed'] and label + '/sdk-child.json' not in identities and
                     label + '/execution-bundle.json' not in identities and b'623' in files[label + '/build.stderr.log'], 'preserved activation-only failure before SDK child/codec execution')
            else:
                need(report['target_executed'] and report['all_bound_inputs_current'] and report['actual_translation_units'] == 5, 'actual target and source bindings')
                child = json.loads(files[label + '/sdk-child.json'].decode('utf-8-sig'))
                need(child['pid'] > 0 and child['exit_status'] == 0, 'real SDK child terminal zero')
                bundle = json.loads(files[label + '/execution-bundle.json'])
                need(bundle['sources'] == sources, 'exact compiled source manifest')
                for name, digest in bundle['artifacts'].items():
                    identity(label + '/' + name, digest)
                closure = json.loads(files[label + '/actual-compiler-closure.json'])
                need(len(closure['translation_units']) == 5 and len(closure['dependencies']) == report['actual_compiler_dependencies'], 'complete actual compiler dependency census')
                for row in closure['dependencies'].values():
                    need(sources[row['manifest_original']]['sha256'] == row['sha256'], 'every consumed compiler dependency source binding')
                need(report['actual_compiler_dependencies'] >= 206, 'recorded full selected dependency closure')
    need(set(reports) == {'reference01', 'reference02', 'reference03', 'native01', 'native02', 'frame-reference01', 'raw-native01'}, 'all seven unchanged campaigns')
    creator = reports['reference03']; need(len(creator['cases']) == 49, 'complete final creator corpus')
    classes = Counter(); raw_total = logical_total = missing_total = 0
    table, bodies, offset = [], [], 1584
    for index, (name, fixture) in enumerate(creator['cases'].items()):
        artifacts = fixture['artifacts']; original = files['reference03/' + artifacts['original.packets']['path']]
        framed = files['reference03/' + artifacts['framed.packets']['path']]
        original_info, original_packets = transport(original); info, packets = transport(framed)
        source_frames = [parse_packet(packet)['frames'][0] for packet in original_packets]
        need(all(len(parse_packet(packet)['frames']) == 1 for packet in original_packets), 'whole original single-frame creator packets')
        maps = fixture['accounting']['source_frame_map']; flattened = [source for packet in maps for source in packet]
        category = 'missing_coded_frames' if None in flattened else 'unaltered_consecutive_fully_coded' if flattened == list(range(len(flattened))) else 'nonconsecutive_or_repeated_fully_coded'
        classes[category] += 1
        need(len(packets) == len(maps) == 4 and fixture['creator_encoding']['input_silent_frames'] >= fixture['case']['samples'] * fixture['case']['count'], 'whole final stream and genuinely encoded silent quarter')
        metadata = [json.loads(line) for line in files['reference03/' + artifacts['decoded.jsonl']['path']].decode().splitlines()]
        for packet, source_map, public in zip(packets, maps, metadata):
            parsed = parse_packet(packet)
            need(parsed['frames'] == [b'' if source is None else source_frames[source] for source in source_map] and
                 parsed['sizes'] == public['sizes'] and parsed['code'] == public['code'] == fixture['case']['code'] and
                 parsed['samples'] == public['samples'] and parsed['sizes'].count(0) == public['zero_frames'] and
                 public['repacketize_pad_unpad_frames_exact'] and public['decoded_pcm_exact'], 'whole exact coded-frame provenance and independent public synthesis')
        ogg = files['reference03/' + artifacts['complete.ogg']['path']]; check_ogg(ogg, info, packets, index)
        decoded = fixture['creator_decoding']
        need(decoded['three_full_decodes_exact'] and decoded['raw_frames'] == info['samples'] * 4 == info['skip'] + info['logical'] + 13 and
             decoded['raw_bytes'] == decoded['raw_frames'] * info['channels'] * 2 and decoded['trim_bytes'] == info['logical'] * info['channels'] * 2, 'full creator raw/playback geometry')
        raw_total += decoded['raw_frames']; logical_total += info['logical']; missing_total += decoded['zero_length_coded_frames']
        table.append(struct.pack('<8I', info['channels'], offset, len(ogg), decoded['raw_frames'], info['logical'], info['skip'], fixture['case']['mode'], index))
        bodies.append(ogg); offset += len(ogg)
    need(dict(classes) == {'unaltered_consecutive_fully_coded': 18, 'nonconsecutive_or_repeated_fully_coded': 10, 'missing_coded_frames': 21} and
         (raw_total, logical_total, missing_total) == (514080, 501419, 84), 'explicit bounded source classes and absent-frame counts')
    blob = struct.pack('<4I', 0x504d4f47, 1, 49, 32) + b''.join(table) + b''.join(bodies)
    for label in ('native01', 'native02'):
        identity(label + '/project/main/modes.bin', sha(blob), len(blob))
    native = reports['native02']; observed = native['measurements']; cases = observed['cases']
    need(len(cases) == 196 and observed['reported_refusals'] == observed['geometry_gaps'] == 0 and observed['exact_vendor_windows'] == 98 and
         observed['all_complete_playback_geometry'] and not observed['numeric_conformance_claim'] and observed['no_numeric_tolerance_applied'], 'all complete actual mode cases without numeric overclaim')
    for index, record in enumerate(cases):
        row = record['measurements']; fixture = list(creator['cases'].values())[index // 4]
        need(row['id'] == index and row['fixture'] == index // 4 and row['mode'] == index % 4 // 2 and row['chunk'] == (257 if index % 2 else 0) and
             row['status'] == row['cause'] == 0 and row['drained'] == 1 and row['opens'] == row['closes'] == 1 and
             row['offered'] == row['consumed'] == row['fixture_bytes'] and row['data_eos'] > 0 and row['empty_eos'] > 0 and
             record['raw_matches_stock_whole'] and row['raw_bytes'] == fixture['creator_decoding']['raw_bytes'] and
             (not row['mode'] or record['exact_vendor_window'] and row['output_bytes'] == fixture['creator_decoding']['trim_bytes']), 'actual full input/EOS/PCM window contract')
        calls = record['public_calls']
        need(len(calls) == row['calls'] and sum(call['consumed'] for call in calls) == row['consumed'] and
             sum(call['decoded'] for call in calls) == row['raw_bytes'] and all(call['consumed'] <= call['len'] and call['decoded'] <= call['capacity'] for call in calls), 'every genuine public call and decoded byte accounted')
        for pin in record['complete_pcm'].values():
            identity('native02/' + pin['path'], pin['sha256'], pin['bytes'])
    need(sum(row['measurements']['resizes'] for row in cases) == 20, 'twenty real mode-buffer retries')
    control = reports['frame-reference01']; need(len(control['cases']) == 4, 'all creator cadence controls')
    for name, record in control['cases'].items():
        summary = record['observations'][-1]
        need(summary['float_unequal_samples'] == summary['float_max_error'] == 0 and not summary['numeric_tolerance_applied'], 'exact creator float cadence, no tolerance')
        if 'cbr' in name:
            need(summary['integer_unequal_samples'] == 63 and summary['integer_max_error'] == 6820 and summary['float_peak'] == 1105064.25,
                 'clipped creator integer cadence is not declared equivalent')
    raw = reports['raw-native01']; raw_cases = raw['measurements']['cases']
    need(len(raw_cases) == 24 and raw['measurements']['reported_refusals'] == raw['measurements']['geometry_gaps'] == 0 and
         not raw['measurements']['creator_clipped_integer_cadence_equivalence'] and not raw['measurements']['numeric_conformance_claim'], 'authentic public raw controls and limited oracle')
    for index, record in enumerate(raw_cases):
        row = record['measurements']
        need(row['id'] == index and row['fixture'] == index // 6 and row['mode'] == index % 6 and row['status'] == 0 and
             row['opens'] == row['closes'] == 1 and record['complete_expected_geometry'] and
             record['matches_current_stock_ogg'] and record['matches_raw_aggregate_presized'], 'all raw/cadence/capacity/configuration paths equal stock Ogg')
        identity('raw-native01/' + record['pcm']['path'], record['pcm']['sha256'], record['pcm']['bytes'])
    need(sum(record['measurements']['resizes'] for record in raw_cases) == 3, 'three actual raw-buffer retries')
    analysis = json.loads(files['numeric-localization02.json'])
    need(analysis['classification_is_observation_not_conformance'] and not analysis['new_tolerance_applied'] and
         analysis['input_native_report']['sha256'] == manifest['campaigns']['native02']['original_report_sha256'] and
         analysis['input_creator_report']['sha256'] == manifest['campaigns']['reference03']['original_report_sha256'], 'full numeric observation has exact original inputs')
    need(analysis['summary']['unaltered_consecutive_fully_coded']['clipped_native'] == analysis['summary']['unaltered_consecutive_fully_coded']['clipped_creator'] == 0 and
         all(row['alignment']['best']['lag_frames'] == 0 and not row['alignment']['best']['swapped_channels'] for row in analysis['cases'].values()), 'ordinary unclipped class and bounded alignment observation')
    meta = json.loads(files['raw-control-metadata-check01.json'])
    canonical = 'tests/run-cyd-opus-frame-control-qemu.py'
    need(meta['passed'] and meta['metadata_only'] and not meta['native_newly_executed'] and
         meta['fixtures'] == list(control['cases']) and meta['source_sha256'] == manifest['canonical_source_sha256'][canonical], 'post-capture metadata-only constructor correction')
    need(set(raw['fixtures']) == {'fixture20.ogg', 'fixture120.ogg', 'fixturevorbis.ogg'} and
         {record['name'] for record in raw_cases} == set(control['cases']), 'historical unused catalog is preserved, actual four controls remain explicit')
    for name, digest in manifest['canonical_source_sha256'].items():
        need(sha(files['canonical/' + name]) == digest, 'every current canonical source snapshot')
        if require_current:
            need(sha((ROOT / name).read_bytes()) == digest, 'current canonical source: ' + name)
    contradictions = 0
    for flag in ('full_standard_numeric_qualification', 'numeric_tolerance_applied', 'creator_clipped_integer_cadence_equivalence', 'production_pipeline_acceptance'):
        changed = dict(manifest); changed[flag] = True
        try:
            scope(changed)
        except ValueError:
            contradictions += 1
    need(contradictions == 4, 'all unsupported acceptance claims are rejected')
    return dict(passed=True, campaigns=7, logical_files=len(files), physical_blobs=len(blobs), omitted_payloads=len(manifest['omitted_payloads']),
                creator_streams=49, native_mode_cases=196, native_raw_cases=24, rejected_scope_contradictions=contradictions,
                full_standard_numeric_qualification=False, require_current=require_current)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(args.require_current), indent=2))
