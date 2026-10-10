"""Qualify finite public HTTPS FLAC/Vorbis/Opus files on a quiet C3 image.

Use independently decoded, hash-pinned references from the accompanying probe
manifest. Neither this runner nor status duration proves PCM/analog continuity.
The caller owns installation and restoration; this program never flashes.
"""
import argparse
import json
import math
from pathlib import Path
import statistics
import time
from urllib.parse import urlsplit

from common import Report, check_recovery_heap, matches, require, sha
from ota import image_info, snapshot, verify_snapshot
from production_health import HealthBoard, check_health
from public_streams import public_url
from run import Capture, Suite
from trace_transport import TransportTrace


def check_finite_playback(samples, spec):
    """Reject false format, early/absent EOF and resumed/stale playback."""
    duration = spec['seconds']
    require(type(duration) in (int, float) and math.isfinite(duration) and
            10 <= duration <= 570, 'Use a finite 10..570 second reference')
    require(len(samples) >= 10, 'Insufficient file observations')
    times = [s['seconds'] for s in samples]
    require(all(math.isfinite(t) and t >= 0 for t in times) and
            all(b > a for a, b in zip(times, times[1:])), 'Invalid observation times')
    require(all(type(s.get('audio')) is bool for s in samples), 'Missing playback state')
    require(all(type(s.get('request_ms')) in (int, float) and
                math.isfinite(s['request_ms']) and s['request_ms'] >= 0 for s in samples),
            'Invalid request timing')
    active = [i for i, s in enumerate(samples) if s['audio']]
    require(len(active) >= 10, 'No sustained file playback')
    first = active[0]
    require(times[first] <= 15, 'No playback within 15 seconds')
    require(all(matches(samples[i], spec) for i in active), 'Wrong decoded file format')
    require(active == list(range(first, active[-1] + 1)), 'Playback stopped and resumed')
    ended = active[-1] + 1
    require(ended < len(samples), 'Finite file never reached EOF')
    require(len(samples) - ended >= 3 and times[-1] - times[ended] >= 2,
            'Insufficient stopped observations after EOF')
    elapsed = times[ended] - times[first]
    require(duration - 2 <= elapsed <= duration + 5,
            'Playback duration differs from independently decoded file')
    require(max(s['request_ms'] for s in samples) < 2000, 'WebUI response exceeded 2 seconds')
    return dict(first_playback_seconds=times[first], first_stopped_seconds=times[ended],
                observed_playback_seconds=elapsed, reference_seconds=duration,
                format_samples=len(active), maximum_status_and_health_ms=max(s['request_ms'] for s in samples))


def load_references(path):
    manifest = json.loads(path.read_text())
    require(type(manifest.get('sources')) is dict and manifest['sources'], 'Missing reference files')
    for name, reference in manifest['sources'].items():
        spec = reference['spec']
        require(name == spec['codec'] and name in ('flac', 'vorbis', 'opus'), 'Unsupported public-file case')
        url = public_url(reference['url'])
        require(public_url(reference['resolved_url']) == url and reference['tls_verify'] is True,
                'Reference must retain verified HTTPS origin')
        media = path.parent / 'media' / (name + Path(urlsplit(url).path).suffix)
        blob = media.read_bytes()
        require(len(blob) == reference['bytes'] and sha(blob) == reference['sha256'], 'Reference bytes changed')
        require(spec['rate'] in (8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000) and
                spec['channels'] in (1, 2) and spec['bits'] == 16, 'Unsupported reference format')
        require(spec['label'] == ('FLAC' if name == 'flac' else 'OGG'), 'Wrong reference label')
        require(math.isfinite(spec['seconds']) and 10 <= spec['seconds'] <= 570 and
                abs(reference['decoded_frames'] / spec['rate'] - spec['seconds']) < 1e-6,
                'Invalid independently decoded duration')
        stream = reference['ffprobe']['streams']
        require(len(stream) == 1 and stream[0]['codec_name'] == spec['codec'] and
                int(stream[0]['sample_rate']) == spec['rate'] and int(stream[0]['channels']) == spec['channels'],
                'Reference format and probe disagree')
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--references', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'Preserve previous evidence')
    references = load_references(a.references)
    config = a.firmware.with_name('sdkconfig').read_text()
    for key in ('CONFIG_ESP_CONSOLE_NONE=y', 'CONFIG_LOG_MAXIMUM_LEVEL=0', 'CONFIG_ESP_TASK_WDT_EN=y'):
        require(key in config, 'Required quiet/watchdog configuration missing')
    for key in ('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y', 'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y'):
        require(key not in config, 'Unexpected sleep or laboratory trust')
    board = HealthBoard(a.board)
    identity = board.info()
    expected = image_info(a.firmware.read_bytes())
    require(identity['app_elf_sha256'] == expected['app_elf_sha256'], 'Wrong installed image')
    before = snapshot(board)
    report = Report(a.output / 'report.json', identity)
    report.data.update(image=expected, references=references,
        reference_manifest_sha256=sha(a.references.read_bytes()),
        sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
        scope='Finite format/duration/EOF, heap/recovery and lifetime health; no PCM or acoustic claim',
        health_http_requests_per_status=1, idle={}, actions=[])
    suite = Suite(board, 'https://unused.invalid', {}, Capture(None), a.output)

    def case(name, fn):
        started = time.perf_counter()
        try:
            report.case(name, fn)
        finally:
            report.data['actions'].append(dict(name=name, started_at=started, ended_at=time.perf_counter()))
            (a.output / 'health.json').write_text(json.dumps(board.health_samples, indent=2)+'\n')
            report.save()

    def idle(name):
        board.stop()
        suite.observe(12, 'idle:' + name, interval=1)
        rows = board.health_samples[-3:]
        report.data['idle'][name] = rows
        return dict(samples=rows)

    def play(name, hint):
        reference = references['sources'][name]
        spec = reference['spec']
        board.stop()
        time.sleep(.8)
        try:
            board.play(reference['url'], hint)
            # Reserve startup and EOF confirmation time without exceeding ten minutes.
            states = suite.observe(spec['seconds'] + 22, 'https:' + name + ':' + hint)
            played = check_finite_playback(states, spec)
            start = suite.observations[-1]['started_at']
            steady = [r for r in board.health_samples
                      if start + played['first_playback_seconds'] + 3 <= r['at'] <=
                      start + played['first_stopped_seconds'] - 1]
            require(len(steady) >= 10, 'Missing in-playback health evidence')
            require(min(r['heap'] for r in steady) >= 16384 and min(r['largest'] for r in steady) >= 8192,
                    'In-playback memory below existing budget')
            for key, tolerance in (('heap', 2048), ('largest', 4096)):
                require(statistics.median(r[key] for r in steady[:3]) -
                        statistics.median(r[key] for r in steady[-3:]) <= tolerance,
                        'Progressive ' + key + ' loss during file playback')
            return dict(playback=played, health=check_health(steady))
        finally:
            board.stop()

    with (a.output / 'request-phases.jsonl').open('x', encoding='utf-8') as log:
        with TransportTrace(urlsplit(a.board).hostname, log, capture_socket_ports=True):
            try:
                case('initial-idle', lambda: idle('initial'))
                for name in references['sources']:
                    for hint in ('auto', name):
                        case('https:' + name + ':' + hint, lambda n=name, h=hint: play(n, h))
                    case('idle:' + name, lambda n=name: idle(n))
                    case('recovery:' + name, lambda n=name:
                         check_recovery_heap(report.data['idle']['initial'], report.data['idle'][n]))
            finally:
                case('stop-and-settings', lambda: (board.stop(), verify_snapshot(board, before))[1])
                case('lifetime-health', lambda: check_health(board.health_samples))
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
