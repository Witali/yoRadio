"""Check public HTTPS radio streams with full PCM, CPU/RAM and WebUI load.

Only public, credential-free URLs belong in the manifest. No broadcast audio,
station metadata, Wi-Fi credentials or private settings are retained. FFprobe
checks the live source immediately before playback; this is not a frozen-fixture
PCM equivalence test. Requires an awake profiling image and passive serial capture.
"""
import argparse
import json
from pathlib import Path
import re
import statistics
import subprocess
import time
from urllib.parse import urlsplit

from common import (Board, Report, check_cpu, check_playback, check_recovery_heap,
                    require, sha)
from diagnostic import DiagnosticCapture
from ota import image_info, snapshot, verify_snapshot, wait_image
from ota_diagnostic import serial_health
from run import Suite


DEFAULT_MANIFEST = Path(__file__).with_name('public_streams.json')


def public_url(url):
    parsed = urlsplit(url)
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username
            and not parsed.password and not parsed.query and not parsed.fragment,
            'Use a public HTTPS URL without credentials, query or fragment')
    return url


def playback_url(url, transport):
    # An explicit cleartext comparison uses the same public origin/path. Source
    # probing and the default board playback retain certificate verification.
    require(transport in ('https', 'http'), 'Unsupported comparison transport')
    parsed = urlsplit(public_url(url))
    return parsed._replace(scheme=transport).geturl()


def probe_spec(value):
    streams = value.get('streams', [])
    require(len(streams) == 1, 'Expected exactly one probed audio stream')
    stream = streams[0]
    codec, profile = stream.get('codec_name'), stream.get('profile')
    labels = {'LC': 'AAC PCM', 'HE-AAC': 'HE-AAC ', 'HE-AACv2': 'HE-AACv2 '}
    require(codec == 'mp3' or codec == 'aac' and profile in labels,
            'Public-stream runner currently accepts MP3 and LC/HE/HEv2 AAC')
    return dict(codec=codec, profile=profile, rate=int(stream['sample_rate']),
                channels=int(stream['channels']), bits=16,
                label='MP3' if codec == 'mp3' else labels[profile])


def probe(url, ffprobe, aac_reference_command=None):
    command = [ffprobe, '-v', 'error', '-rw_timeout', '15000000',
               '-analyzeduration', '3000000', '-probesize', '131072',
               '-tls_verify', '1', '-select_streams', 'a', '-show_entries',
               'stream=codec_name,profile,sample_rate,channels,channel_layout',
               '-of', 'json', public_url(url)]
    result = subprocess.run(command, capture_output=True, timeout=30, check=False)
    # Do not retain arbitrary server metadata or ffprobe error text.
    require(result.returncode == 0, 'FFprobe could not verify/decode the HTTPS source')
    spec = probe_spec(json.loads(result.stdout))
    if spec['codec'] == 'aac' and aac_reference_command is not None:
        from aac_reference import probe_aac
        reference = probe_aac(public_url(url), spec, aac_reference_command)
        return dict(reference, tls_verify=True)
    return dict(spec=spec, tls_verify=True)


def no_runtime_faults(rows):
    require(serial_health(rows)['result'] == 'PASS', 'Serial panic or capture failure')
    require(not any(re.search(r'^(ESP-ROM:|rst:|waiting for download)', r['line'])
                    for r in rows), 'Unexpected reboot during playback')
    require(not any(re.search(r'allocation failed|decode (?:error|failed)|TLS failure:', r['line'])
                    for r in rows), 'Runtime allocation/decoder/TLS failure')


def metrics(samples, rows, spec, seconds, start, end, max_busy=85):
    no_runtime_faults(rows)
    first = next((s['seconds'] for s in samples if s.get('audio')), None)
    require(first is not None and first <= 15, 'No PCM playback within 15 seconds')
    playback = check_playback(samples, spec, minimum=int((seconds-15)*.6), warmup=15)
    require(max(s['request_ms'] for s in samples) < 2000, 'WebUI response exceeded 2 s')
    stable = [r for r in rows if start+15 <= r['at'] <= end]
    cpu = check_cpu(stable, max_busy=max_busy, start=start+15, end=end)
    times = sorted(s['request_ms'] for s in samples)
    return dict(playback=playback, first_pcm_seconds=first,
                status_samples=len(samples), max_http_ms=max(times),
                p95_http_ms=times[int((len(times)-1)*.95)],
                median_http_ms=statistics.median(times), **cpu)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--serial-port', required=True)
    parser.add_argument('--firmware', type=Path, required=True,
                        help='Installed app.bin with adjacent exact sdkconfig; not flashed')
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--case', action='append')
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--max-cpu-busy', type=float,
                        help='Optional CPU percentage limit; default records CPU without a headroom gate')
    parser.add_argument('--interval', type=float, default=.1,
                        help='Delay between status requests; .1 is concurrent WebUI load')
    parser.add_argument('--transport', choices=('https', 'http'), default='https',
                        help='HTTP is an explicit same-origin memory/CPU comparison')
    parser.add_argument('--ffprobe', default='ffprobe')
    parser.add_argument('--aac-reference-command', type=Path,
                        help='JSON argv for unquantized FAAD history probe; use {input} or {input_wsl}')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.seconds >= 45 and .05 <= args.interval <= 1,
            'Use at least 45 seconds and a 0.05..1 second polling interval')
    config = args.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_QEMU=y' not in config and
            'CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config, 'Use an awake physical image')
    manifest = json.loads(args.manifest.read_text())
    names = args.case or list(manifest['streams'])
    require(names and all(name in manifest['streams'] for name in names), 'Unknown stream case')
    urls = {name: public_url(manifest['streams'][name]) for name in names}
    play_urls = {name: playback_url(url, args.transport) for name, url in urls.items()}
    board = Board(args.board)
    initial_playing = board.status()['audio']
    initial = board.info()
    image = image_info(args.firmware.read_bytes())
    require(initial['app_elf_sha256'] == image['app_elf_sha256'], 'Wrong installed image')
    before = snapshot(board)
    report = Report(args.output/'report.json', initial)
    report.data.update(image=image, public_urls=urls, playback_urls=play_urls,
        transport=args.transport, sources=manifest['sources'],
        seconds=args.seconds, interval=args.interval, cpu_budget_percent=args.max_cpu_busy,
        manifest_sha256=sha(args.manifest.read_bytes()),
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        ffprobe_version=subprocess.run([args.ffprobe, '-version'], capture_output=True,
                                       text=True, timeout=5, check=True).stdout.splitlines()[0])
    report.save()
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, 'https://unused.invalid', {}, capture, args.output)
    baseline = None

    def settled_baseline():
        nonlocal baseline
        baseline = suite.idle_heap()
        return dict(samples=baseline)

    def play(name):
        reference = probe(urls[name], args.ffprobe,
                          json.loads(args.aac_reference_command.read_text())
                          if args.aac_reference_command else None)
        report.data.setdefault('reference_probes', {})[name] = reference
        report.save()
        board.stop()
        time.sleep(.8)
        started = time.perf_counter()
        window = dict(start=started)
        report.data.setdefault('windows', {})[name] = window
        try:
            board.play(play_urls[name])
            samples = suite.observe(args.seconds, name, interval=args.interval)
            evidence = metrics(samples, capture.since(started), reference['spec'],
                               args.seconds, started, time.perf_counter(), max_busy=args.max_cpu_busy)
            with board.websocket() as ws:
                ws.send('getindex')
                deadline = time.perf_counter()+5
                while time.perf_counter() < deadline:
                    message = json.loads(ws.recv(timeout=5))
                    values = {p['id']: p['value'] for p in message.get('payload', [])}
                    if 'fmt' in values:
                        require(values['fmt'] == board.status()['format'] and
                                values.get('playerwrap') == 'playing', 'WebSocket format/state mismatch')
                        break
                else:
                    require(False, 'No WebSocket playback snapshot')
            return dict(reference=reference, websocket_matches_rest=True, **evidence)
        finally:
            window['end'] = time.perf_counter()
            board.stop()

    def recovery():
        final = suite.idle_heap()
        require(baseline is not None, 'Missing baseline heap')
        check_recovery_heap(baseline, final)
        require(serial_health(capture.rows)['result'] == 'PASS', 'Serial panic or capture failure')
        require(not any(re.search(r'^(ESP-ROM:|rst:|waiting for download)', r['line'])
                        for r in capture.rows), 'Unexpected reboot during test')
        return dict(samples=final, no_unexpected_resets=True)

    def restore():
        board.stop()
        board.reboot()
        time.sleep(3)
        wait_image(board, image['app_elf_sha256'], initial['partition'])
        if not initial_playing:
            board.stop()
            require(not board.status()['audio'], 'Could not restore stopped state')
            return dict(stopped_state_restored=True, **verify_snapshot(board, before))
        deadline = time.perf_counter()+30
        state = board.status()
        while not state['audio'] and time.perf_counter() < deadline:
            time.sleep(1)
            state = board.status()
        require(state['audio'], 'Saved station did not resume after reboot')
        return dict(saved_station_playing=True, **verify_snapshot(board, before))

    try:
        report.case('idle:baseline', settled_baseline)
        for name in names:
            report.case(args.transport+':'+name, lambda n=name: play(n))
        report.case('idle:recovery', recovery)
    finally:
        report.case('restore', restore)
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n', newline='\n')
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
