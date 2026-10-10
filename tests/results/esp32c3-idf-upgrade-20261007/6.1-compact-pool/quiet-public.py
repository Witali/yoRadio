"""Status-only HTTPS checks on the exact quiet production image.

No CPU, heap, serial-panic or acoustic-continuity qualification is inferred.
Public source audio/metadata and private board settings are never retained.
"""
import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, Report, check_playback, require, sha
from ota import image_info, snapshot, verify_snapshot, wait_image
from public_streams import DEFAULT_MANIFEST, probe, public_url
from run import Capture, Suite

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--firmware', type=Path, required=True)
p.add_argument('--board', default='http://192.168.100.4')
p.add_argument('--output', type=Path, required=True)
p.add_argument('--aac-reference-command', type=Path)
a = p.parse_args()
require(not a.output.exists(), 'Use a fresh output directory')
config = a.firmware.with_name('sdkconfig').read_text()
for option in ('QEMU', 'DEEP_SLEEP_CLOCK', 'CPU_PROFILE_HTTP'):
    require(f'CONFIG_YORADIO_{option}=y' not in config, 'Use quiet awake production')
require('CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y' not in config,
        'Use production without runtime profiling')
b = Board(a.board)
initial = b.info()
image = image_info(a.firmware.read_bytes())
require(initial['app_elf_sha256'] == image['app_elf_sha256'], 'Wrong installed image')
playing = b.status()['audio']
before = snapshot(b)
report = Report(a.output/'report.json', initial)
manifest = json.loads(DEFAULT_MANIFEST.read_text())
report.data.update(image=image, manifest_sha256=sha(DEFAULT_MANIFEST.read_bytes()),
                   qualification='HTTPS format/state and WebSocket only; no CPU/heap/acoustic gate',
                   public_urls=manifest['streams'], seconds=60, interval=.4,
                   sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()))
suite = Suite(b, 'https://unused.invalid', {}, Capture(None), a.output)

def play(name, url):
    reference = probe(public_url(url), 'ffprobe',
                      json.loads(a.aac_reference_command.read_text()) if a.aac_reference_command else None)
    report.data.setdefault('reference_probes', {})[name] = reference
    report.save()
    b.stop()
    time.sleep(.8)
    try:
        b.play(url)
        samples = suite.observe(60, name)
        first = next((s['seconds'] for s in samples if s.get('audio')), None)
        require(first is not None and first <= 15, 'No PCM playback within 15 seconds')
        result = check_playback(samples, reference['spec'], minimum=27, warmup=15)
        times = sorted(s['request_ms'] for s in samples)
        require(max(times) < 2000, 'WebUI response exceeded 2 seconds')
        with b.websocket() as ws:
            ws.send('getindex')
            deadline = time.monotonic()+5
            while time.monotonic() < deadline:
                message = json.loads(ws.recv(timeout=5))
                values = {p['id']: p['value'] for p in message.get('payload', [])}
                if 'fmt' in values:
                    require(values['fmt'] == b.status()['format'] and
                            values.get('playerwrap') == 'playing', 'WebSocket format/state mismatch')
                    break
            else:
                require(False, 'No WebSocket playback snapshot')
        require(b.info()['app_elf_sha256'] == image['app_elf_sha256'], 'Installed image changed')
        return dict(reference=reference, playback=result, first_pcm_seconds=first,
                    websocket_matches_rest=True, median_http_ms=statistics.median(times),
                    max_http_ms=max(times), p95_http_ms=times[int((len(times)-1)*.95)])
    finally:
        b.stop()

def restore():
    b.stop()
    b.reboot()
    time.sleep(3)
    wait_image(b, image['app_elf_sha256'], initial['partition'])
    if not playing:
        b.stop()
        require(not b.status()['audio'], 'Stopped state was not restored')
    else:
        deadline = time.monotonic()+30
        while not b.status()['audio'] and time.monotonic() < deadline:
            time.sleep(1)
        require(b.status()['audio'], 'Saved station did not resume')
    return dict(initial_playing_state_restored=True, **verify_snapshot(b, before))

try:
    for name, url in manifest['streams'].items():
        report.case('https:'+name, lambda n=name, u=url: play(n, u))
finally:
    report.case('restore', restore)
raise SystemExit(report.exit_code())
