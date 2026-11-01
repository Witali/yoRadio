"""Verify a completed local creator corpus as data; never execute saved code."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('current_packet_modes_rfc_data', Path(__file__).with_name('generate.py'))
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(folder, require_current=False):
    report = json.loads((folder / 'report.json').read_bytes())
    g.need(report['passed'] and report['completed'] and report['all_source_bindings_current'] and
           not report['native_vendor_executed'] and not report['private_abi_used'] and
           not report['numerical_conformance_claim'], 'terminal creator-only scope')
    for source in report['sources']:
        frozen = folder / source['snapshot']
        g.need(frozen.stat().st_size == source['bytes'] and sha(frozen) == source['sha256'], 'original source snapshot')
        if require_current:
            g.need(sha(ROOT / source['path']) == source['sha256'], 'current original source bytes')
    for command in report['commands']:
        g.need(command['state'] == 'complete' and command['exit_status'] == 0 and command['pid'] > 0 and
               not command.get('timed_out'), 'actual command terminal zero')
        for stream in ('stdout', 'stderr'):
            row = command[stream]; path = folder / row['path']
            g.need(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'exact original process log')
    g.need(len(report['cases']) == 49, 'all bounded cases')
    raw_frames = logical_frames = missing_frames = 0
    for index, (name, record) in enumerate(report['cases'].items()):
        case, account, encoded, decoded = record['case'], record['accounting'], record['creator_encoding'], record['creator_decoding']
        g.need(case['name'] == name and encoded['input_silent_frames'] >= case['samples'] * case['count'], 'real encoded silent quarter')
        for row in record['artifacts'].values():
            path = folder / row['path']
            g.need(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'all intact encoded and decoded artifact bytes')
        original = (folder / record['artifacts']['original.packets']['path']).read_bytes()
        framed = (folder / record['artifacts']['framed.packets']['path']).read_bytes()
        rebuilt, observed = g.reframe(original, case)
        g.need(rebuilt == framed and observed == account, 'exact complete coded frames and declared repetition/missing maps')
        ogg = (folder / record['artifacts']['complete.ogg']['path']).read_bytes()
        g.need(g.make_ogg(framed, 0x504d0000 + index) == ogg, 'entire original complete CRC/granule stream')
        info, packets = g.parse_transport(framed)
        metadata = [json.loads(line) for line in (folder / record['artifacts']['decoded.jsonl']['path']).read_text().splitlines()]
        g.need(len(packets) == len(metadata) == 4, 'four whole independently decoded packets')
        for packet, creator in zip(packets, metadata):
            row = g.parse_packet(packet)
            g.need(row['code'] == creator['code'] == case['code'] and row['sizes'] == creator['sizes'] and
                   row['samples'] == creator['samples'] and row['sizes'].count(0) == creator['zero_frames'] and
                   creator['repacketize_pad_unpad_frames_exact'] and creator['decoded_pcm_exact'],
                   'independent public creator framing and synthesis observations')
        g.need(decoded['three_full_decodes_exact'] and decoded['raw_frames'] == sum(g.parse_packet(p)['samples'] for p in packets) and
               decoded['logical_frames'] == info['logical_frames'] and decoded['raw_bytes'] == decoded['raw_frames'] * info['channels'] * 2 and
               decoded['trim_bytes'] == info['logical_frames'] * info['channels'] * 2, 'entire raw/playback accounting')
        raw = (folder / record['artifacts']['raw.pcm']['path']).read_bytes()
        trim = (folder / record['artifacts']['playback.pcm']['path']).read_bytes()
        start = info['pre_skip'] * info['channels'] * 2
        g.need(trim == raw[start:start + decoded['trim_bytes']], 'exact independent creator playback window')
        g.need(len(record['container_checks']) == 3 and all(r['pages'] == 6 and r['audio_packets'] == 4 and r['exact_complete_packets'] and
               r['eos'] and r['sync_errors'] == r['packet_holes'] == 0 for r in record['container_checks']), 'creator libogg complete streams at three split sizes')
        raw_frames += decoded['raw_frames']; logical_frames += decoded['logical_frames']; missing_frames += decoded['zero_length_coded_frames']
    return dict(passed=True, complete_streams=49, raw_frames=raw_frames, logical_frames=logical_frames,
                zero_length_coded_frames=missing_frames, native_vendor_executed=False, require_current=require_current)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--require-current', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(args.capture.resolve(), args.require_current), indent=2))
