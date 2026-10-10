"""Qualify quiet normal-trust prefill across codecs and OTA, then restore exactly."""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, exception_details, fixtures, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from audio_test_server.server import Server

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'physical'
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000')
RESTORE = Path('firmware/development/esp32c3-idf61-listen-48k/app.bin')
BOARD = Board('http://192.168.100.4')
HOST = '192.168.100.253'
require(not OUT.exists(), 'Preserve previous physical evidence')
candidate = image_info((ART / 'app.bin').read_bytes())
quiet = image_info(RESTORE.read_bytes())
manifest = json.loads((ART / 'manifest.json').read_text())
audit = json.loads((ROOT / 'quiet-prefill1000/build-audit.json').read_text())
comparison = json.loads((ROOT / 'laboratory-comparison.json').read_text())
require(audit['result'] == comparison['result'] == 'PASS', 'Missing build audits')
require(candidate == audit['image'] == manifest['image'] and
        manifest['production_profile'] and not manifest['lab_ca'], 'Wrong candidate')
require(quiet['sha256'] == '798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde', 'Restore image changed')
initial, status = BOARD.info(), BOARD.status()
require(initial['app_elf_sha256'] == quiet['app_elf_sha256'] and not status['audio'], 'Unexpected initial board state')
before = snapshot(BOARD)
specs = fixtures()
OUT.mkdir()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

sources = {p.as_posix(): sha(p.read_bytes())
           for folder in ('tools/esp32c3_tests', 'tools/audio_test_server')
           for p in sorted(Path(folder).glob('*.py'))}
for name in sources:
    dest = ROOT / 'test-sources' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(Path(name).read_bytes())
save('initial.json', dict(identity=initial, status=status, candidate=candidate, quiet=quiet,
                         controller_sha256=sha(Path(__file__).read_bytes()), test_sources_sha256=sources,
                         source_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                         host_clock=dict(api='time.perf_counter', **vars(time.get_clock_info('perf_counter')))))

def install(path):
    image = path.read_bytes()
    expected, active = image_info(image), BOARD.info()
    target = 'app1' if active['partition'] == 'app0' else 'app0'
    require(len(image) <= active['max_size'], 'Application exceeds OTA slot')
    BOARD.stop()
    code, body = upload(BOARD.origin, multipart(image))
    require(code == 200 and body == b'OK', 'App-only OTA did not return 200 OK')
    return wait_image(BOARD, expected['app_elf_sha256'], target, timeout=60)

phases = []
def run_phase(label, args, limit):
    for name, digest in sources.items():
        require(sha(Path(name).read_bytes()) == digest, 'Test source changed')
    require(BOARD.info()['app_elf_sha256'] == candidate['app_elf_sha256'], 'Wrong app before phase')
    print('START', label, flush=True)
    start = time.perf_counter()
    with (OUT / (label + '.log')).open('xb') as log:
        child = subprocess.Popen([sys.executable, '-B', '-X', 'utf8', *map(str, args)], stdout=log, stderr=subprocess.STDOUT)
        save('running.json', dict(phase=label, pid=child.pid, started_at=start))
        try:
            code = child.wait(timeout=limit)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
            code = 124
    phases.append(dict(name=label, code=code, seconds=time.perf_counter() - start))
    save('phases.json', phases)
    print('END', label, code, flush=True)
    require(code == 0, 'Acceptance phase failed; retain evidence and restore')
    require(BOARD.info()['app_elf_sha256'] == candidate['app_elf_sha256'], 'Wrong app after phase')

try:
    print('INSTALL normal-trust candidate', flush=True)
    save('installed.json', dict(identity=install(ART / 'app.bin'), persistence=verify_snapshot(BOARD, before)))
    run_phase('local', ['tools/esp32c3_tests/quiet_acceptance.py', '--board', BOARD.origin,
              '--host', HOST, '--firmware', ART / 'app.bin', '--suite', 'http',
              '--suite', 'transitions', '--suite', 'network', '--suite', 'websocket',
              '--output', OUT / 'local'], 1200)
    server = Server(HOST, 8772, specs, delivery_stats=True, pacing_ratio=1.0)
    try:
        with server:
            try:
                run_phase('ota', ['tools/esp32c3_tests/ota.py', '--board', BOARD.origin,
                          '--firmware', ART / 'app.bin', '--suite', 'negative', '--suite', 'roundtrip',
                          '--suite', 'while-playing', '--suite', 'slow',
                          '--play-url', f'http://{HOST}:8772/stream/he-44100-stereo',
                          '--play-fixture', 'he-44100-stereo', '--output', OUT / 'ota.json'], 600)
            finally:
                BOARD.stop()
    finally:
        save('ota-server-events.json', server.events)
    save('settings-after-tests.json', verify_snapshot(BOARD, before))
except Exception as error:
    save('controller-failure.json', dict(exception_chain=exception_details(error)))
    raise
finally:
    print('RESTORE listened image', flush=True)
    try:
        restored = install(RESTORE)
        BOARD.stop()
        states = []
        for _ in range(3):
            time.sleep(5)
            states.append(BOARD.status())
        save('restoration.json', dict(identity=restored, persistence=verify_snapshot(BOARD, before), states=states))
        require(all(not state['audio'] for state in states), 'Playback state not restored')
        print('RESTORED image and settings', flush=True)
    except Exception as error:
        save('restoration-failure.json', dict(exception_chain=exception_details(error)))
        raise
