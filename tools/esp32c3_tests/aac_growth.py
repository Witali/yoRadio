"""Compare original and delayed-growth AAC files on a quiet C3 image over HTTP.

Requires independently decoded PCM-equivalent fixture pairs. Does not flash;
the caller owns installation/restoration. No HTTPS or DMA continuity claim.
"""
import argparse
import json
from pathlib import Path
import statistics
import time
from urllib.parse import urlsplit

from common import Report, check_recovery_heap, fixtures, require, sha
from ota import image_info, snapshot, verify_snapshot
from production_health import HealthBoard, check_health
from public_file_acceptance import check_finite_playback
from run import Capture, Suite
from trace_transport import TransportTrace
from audio_test_server.generate_aac_growth import adts_frames, generate
from audio_test_server.server import Server


def load_pairs(folder):
    manifest = json.loads((folder / 'manifest.json').read_text())
    references = json.loads((folder / 'references.json').read_text())
    originals = fixtures()
    pairs = {}
    for name, info in manifest.items():
        require(name in originals and originals[name]['codec'] == 'aac', 'Unknown source AAC fixture')
        source = Path(__file__).resolve().parents[2] / 'tests/fixtures/aac_stream_format' / (name + '.aac')
        data = source.read_bytes()
        require(sha(data) == info['source_sha256'], 'Source fixture changed')
        baseline, growth, generated = generate(data)
        require(all(info[key] == value for key, value in generated.items()), 'Growth generation differs')
        reference = references[name]
        require(reference['baseline'] == reference['growth'], 'Independent PCM/format reference differs')
        decoded = reference['growth']
        faad = decoded['faad']
        require(faad['frames'] == info['frames'] and faad['samples'] > 0, 'Missing complete FAAD decode')
        if originals[name]['profile'].startswith('HE-'):
            require(faad['sbr_frames'] == info['frames'], 'Missing SBR processing')
        if originals[name]['profile'] == 'HE-AACv2':
            require(faad['ps_frames'] > 0, 'Missing PS processing')
        stream = decoded['ffprobe']['streams']
        require(len(stream) == 1 and stream[0]['codec_name'] == 'aac' and
                int(stream[0]['sample_rate']) == originals[name]['rate'] and
                int(stream[0]['channels']) == originals[name]['channels'], 'Reference format differs')
        samples_per_frame = 1024 * originals[name]['rate'] // info['core_rate'] * originals[name]['channels']
        require(decoded['ffmpeg_pcm_bytes'] == info['frames'] * samples_per_frame * 2 and
                faad['samples'] == (info['frames'] - 1) * samples_per_frame,
                'Reference PCM length differs (FAAD suppresses its first priming frame)')
        for label, payload in (('baseline', baseline), ('growth', growth)):
            require((folder / name / (label + '.aac')).read_bytes() == payload and
                    info['files'][label] == dict(bytes=len(payload), sha256=sha(payload)), 'Fixture bytes differ')
            frames, _, _ = adts_frames(payload)
            boundary = sum(map(len, frames[:info['first_growth_frame']]))
            spec = dict(originals[name], data=payload, seconds=info['seconds'],
                        sha256=sha(payload), container_label='AAC')
            # Pace before/after growth separately; a larger late frame must not
            # accelerate delivery of the earlier small-frame warmup.
            spec['segments'] = [dict(data=payload[:boundary], seconds=info['growth_seconds']),
                dict(data=payload[boundary:], seconds=info['seconds'] - info['growth_seconds'])]
            pairs[name + '-' + label] = spec
    require(pairs, 'No fixture pairs')
    return pairs, manifest, references


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', type=int, default=8772)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Preserve previous evidence')
    specs, manifest, references = load_pairs(args.fixtures)
    image = image_info(args.firmware.read_bytes())
    config = args.firmware.with_name('sdkconfig').read_text()
    for key in ('CONFIG_ESP_CONSOLE_NONE=y', 'CONFIG_LOG_MAXIMUM_LEVEL=0', 'CONFIG_ESP_TASK_WDT_EN=y'):
        require(key in config, 'Expected quiet health configuration')
    board = HealthBoard(args.board)
    identity = board.info()
    require(identity['app_elf_sha256'] == image['app_elf_sha256'], 'Wrong installed image')
    settings = snapshot(board)
    report = Report(args.output / 'report.json', identity)
    report.data.update(image=image, fixtures=manifest, references=references, idle={},
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        scope='Local HTTP: format/duration/EOF, sampled memory and lifetime faults; not HTTPS or DMA/PCM continuity')
    suite = Suite(board, 'http://' + args.host + ':' + str(args.port), specs, Capture(None), args.output)

    def case(name, action):
        try:
            report.case(name, action)
        finally:
            (args.output / 'health.json').write_text(json.dumps(board.health_samples, indent=2) + '\n')
            report.save()

    def idle(name):
        board.stop()
        suite.observe(12, 'idle:' + name, interval=1)
        report.data['idle'][name] = board.health_samples[-3:]
        return dict(samples=board.health_samples[-3:])

    def play(name):
        board.stop(); time.sleep(.8)
        try:
            suite.start(name, hint='aac')
            states = suite.observe(specs[name]['seconds'] + 10, name)
            playback = check_finite_playback(states, specs[name])
            start = suite.observations[-1]['started_at']
            steady = [h for h in board.health_samples if
                start + playback['first_playback_seconds'] + 3 <= h['at'] <=
                start + playback['first_stopped_seconds'] - 1]
            require(len(steady) >= 10, 'Missing steady health')
            require(min(s['heap'] for s in steady) >= 16384 and min(s['largest'] for s in steady) >= 8192,
                    'In-playback memory below existing budget')
            # Compare stable windows around growth; allow the expected retained
            # frame buffer, but retain observed loss for review rather than hide it.
            windows = {}
            for label, lo, hi in (('before_growth', 8, 13), ('after_growth', 23, 30)):
                rows = [h for h in steady if lo <= h['at'] - start <= hi]
                require(len(rows) >= 5, 'Missing growth memory window')
                windows[label] = {k: statistics.median(r[k] for r in rows) for k in ('heap', 'largest', 'tasks')}
            return dict(playback=playback, health=check_health(steady), windows=windows)
        finally:
            board.stop()

    with (args.output / 'request-phases.jsonl').open('x', encoding='utf-8') as log:
        with TransportTrace(urlsplit(args.board).hostname, log, capture_socket_ports=True):
            with Server('0.0.0.0', args.port, specs, pacing_ratio=1.0, delivery_stats=True) as server:
                try:
                    case('initial-idle', lambda: idle('initial'))
                    for source in manifest:
                        for label in ('baseline', 'growth'):
                            name = source + '-' + label
                            case(name, lambda n=name: play(n))
                        case('idle:' + source, lambda n=source: idle(n))
                        case('recovery:' + source, lambda n=source:
                            check_recovery_heap(report.data['idle']['initial'], report.data['idle'][n]))
                finally:
                    report.data['server_events'] = server.events
                    case('stop-and-settings', lambda: (board.stop(), verify_snapshot(board, settings))[1])
                    case('lifetime-health', lambda: check_health(board.health_samples))
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
