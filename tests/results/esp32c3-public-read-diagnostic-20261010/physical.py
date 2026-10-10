"""Two MP3 attempts and one HE-AAC observation with independent host decoding."""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, Failure, check_playback, check_recovery_heap, exception_details, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import HealthBoard, check_health
from sustained_output import sustained_window, check_output, check_memory
from pipeline_probe import analyze_pipeline
from public_streams import probe
from run import Capture, Suite

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'physical'
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-read-diag')
RESTORE = Path('firmware/development/esp32c3-idf61-listen-48k/app.bin')
board = Board('http://192.168.100.4')
candidate, quiet = image_info((ART / 'app.bin').read_bytes()), image_info(RESTORE.read_bytes())
manifest = json.loads((ART / 'manifest.json').read_text())
require(manifest['pipeline_diagnostic'] and not manifest['lab_ca'], 'Expected public-trust diagnostics')
require(candidate == manifest['image'], 'Image identity changed')
require(quiet['sha256'] == '798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde', 'Restore image changed')
initial = board.info()
require(initial['app_elf_sha256'] == quiet['app_elf_sha256'] and not board.status()['audio'], 'Unexpected starting firmware/playback')
before = snapshot(board)
require(not OUT.exists(), 'Preserve earlier evidence')
OUT.mkdir()
sources = {}
for folder in ('tools/esp32c3_tests', 'tools/audio_test_server'):
    for file in sorted(Path(folder).glob('*.py')):
        sources[file.as_posix()] = sha(file.read_bytes())
        dest = ROOT / 'test-sources' / file
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(file.read_bytes())
reference_command = Path('.build/c3-prefill1000-public-20261010/faad-reference-command.json')
shutil.copyfile(reference_command, ROOT / reference_command.name)
command = json.loads(reference_command.read_text())
ffmpeg = shutil.which('ffmpeg')
require(ffmpeg is not None, 'Independent decoder missing')

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

save('initial.json', dict(identity=initial, candidate=candidate, quiet=quiet,
    test_sources_sha256=sources, controller_sha256=sha(Path(__file__).read_bytes()),
    ffmpeg=dict(path=ffmpeg, sha256=sha(Path(ffmpeg).read_bytes()))))

def install(path):
    image = path.read_bytes(); expected = image_info(image); current = board.info()
    require(len(image) <= current['max_size'], 'OTA slot too small')
    target = 'app1' if current['partition'] == 'app0' else 'app0'
    board.stop()
    code, body = upload(board.origin, multipart(image))
    require(code == 200 and body == b'OK', 'OTA did not return 200 OK')
    return wait_image(board, expected['app_elf_sha256'], target, timeout=60)

def evaluate(fn):
    try: return dict(result='PASS', evidence=fn())
    except Failure as error: return dict(result='FAIL', reason=str(error))

last_progress = 0
def checkpoint(completed, batch):
    global last_progress
    now = time.perf_counter()
    if now - last_progress >= 25:
        last_progress = now
        save('progress.json', dict(case=batch['case'], status=batch['samples'][-1], health=b.health_samples[-1]))
        print('OBSERVE', batch['case'], round(batch['samples'][-1]['seconds']), flush=True)

try:
    print('INSTALL diagnostics', flush=True)
    save('installed.json', dict(identity=install(ART / 'app.bin'), persistence=verify_snapshot(board, before)))
    b = HealthBoard(board.origin)
    suite = Suite(b, 'http://unused.invalid', {}, Capture(None), OUT, checkpoint=checkpoint)
    b.stop(); suite.observe(12, 'idle:initial', interval=1)
    idle = b.health_samples[-3:]
    require('stream_failure' in idle[-1]['pipeline'], 'Missing read-failure diagnostics')
    results = {}
    for name, suffix in (('mp3-first', '256-mp3'), ('he64', '64-aac'), ('mp3-repeat', '256-mp3')):
        b.stop()
        url = 'https://ice5.somafm.com/groovesalad-' + suffix
        reference = probe(url, 'ffprobe', command)
        seconds = 120
        ffcommand = [ffmpeg, '-hide_banner', '-nostats', '-loglevel', 'error', '-rw_timeout', '12000000',
                     '-tls_verify', '1', '-i', url, '-t', str(seconds+5), '-progress', 'pipe:1', '-f', 'null', '-']
        with (OUT / (name + '-host-progress.log')).open('xb') as progress, (OUT / (name + '-host-errors.log')).open('xb') as errors:
            host = subprocess.Popen(ffcommand, stdout=progress, stderr=errors)
            start = time.perf_counter()
            host_result = dict(command=ffcommand, pid=host.pid, started_at=start)
            save(name + '-host.json', host_result)
            try:
                b.play(url)
                begin = len(b.health_samples)
                states = suite.observe(seconds, name)
                rows = b.health_samples[begin:]
                steady, measured = sustained_window(states, rows, seconds)
                results[name] = dict(url=url, reference=reference,
                    checks=dict(format=evaluate(lambda: check_playback(states, reference['spec'], minimum=int((seconds-15)*.6), warmup=15)),
                                output=evaluate(lambda: check_output(measured)), memory=evaluate(lambda: check_memory(measured))),
                    pipeline=analyze_pipeline(measured), health=check_health(measured),
                    last_failure=rows[-1]['pipeline']['stream_failure'],
                    first_stopped=next((s for s in steady if not s['audio']), None))
                print('RESULT', name, json.dumps(results[name]['checks']), 'FAILURE', json.dumps(results[name]['last_failure']), flush=True)
                b.stop()
            finally:
                try: host_result['exit_code'] = host.wait(timeout=35)
                except subprocess.TimeoutExpired:
                    host.kill(); host_result['exit_code'] = host.wait(); host_result['timed_out'] = True
                host_result['ended_at'] = time.perf_counter()
                save(name + '-host.json', host_result)
                save('health.json', b.health_samples)
                save('results.json', results)
        suite.observe(12, 'idle:' + name, interval=1)
    save('summary.json', dict(health=check_health(b.health_samples),
        recovery=evaluate(lambda: check_recovery_heap(idle, b.health_samples[-3:])),
        persistence=verify_snapshot(b, before), idle=dict(initial=idle, final=b.health_samples[-3:])))
    save('health.json', b.health_samples)
except Exception as error:
    save('controller-failure.json', dict(exception_chain=exception_details(error)))
    raise
finally:
    print('RESTORE listened image', flush=True)
    try:
        restored = install(RESTORE); board.stop(); states = []
        for _ in range(3):
            time.sleep(5); states.append(board.status())
        save('restoration.json', dict(identity=restored, persistence=verify_snapshot(board, before), states=states))
        require(all(not s['audio'] for s in states), 'Playback state differs')
        print('RESTORED image and settings', flush=True)
    except Exception as error:
        save('restoration-failure.json', dict(exception_chain=exception_details(error)))
        raise
