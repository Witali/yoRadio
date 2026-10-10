"""Observe five public HTTPS variants on the exact candidate, then restore."""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, exception_details, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'physical'
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000')
RESTORE = Path('firmware/development/esp32c3-idf61-listen-48k/app.bin')
BOARD = Board('http://192.168.100.4')
require(not OUT.exists(), 'Preserve previous evidence')
candidate, quiet = image_info((ART / 'app.bin').read_bytes()), image_info(RESTORE.read_bytes())
audit = json.loads((ROOT / 'prior-build/quiet-prefill1000/build-audit.json').read_text())
manifest = json.loads((ART / 'manifest.json').read_text())
require(audit['result'] == 'PASS' and candidate == audit['image'] == manifest['image'], 'Build identity differs')
require(manifest['production_profile'] and not manifest['lab_ca'], 'Use normal public trust')
require(quiet['sha256'] == '798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde', 'Restore image changed')
initial, state = BOARD.info(), BOARD.status()
require(initial['app_elf_sha256'] == quiet['app_elf_sha256'] and not state['audio'], 'Unexpected initial state')
before = snapshot(BOARD)
OUT.mkdir()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

sources = {}
for folder in ('tools/esp32c3_tests', 'tools/audio_test_server'):
    for file in sorted(Path(folder).glob('*.py')):
        sources[file.as_posix()] = sha(file.read_bytes())
        dest = ROOT / 'test-sources' / file
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(file.read_bytes())
save('initial.json', dict(identity=initial, status=state, candidate=candidate, quiet=quiet,
    controller_sha256=sha(Path(__file__).read_bytes()), test_sources_sha256=sources,
    reference_command_sha256=sha((ROOT / 'faad-reference-command.json').read_bytes()),
    source_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()))

def install(path):
    image = path.read_bytes()
    expected, active = image_info(image), BOARD.info()
    require(len(image) <= active['max_size'], 'Image exceeds OTA slot')
    target = 'app1' if active['partition'] == 'app0' else 'app0'
    BOARD.stop()
    code, body = upload(BOARD.origin, multipart(image))
    require(code == 200 and body == b'OK', 'OTA did not return 200 OK')
    return wait_image(BOARD, expected['app_elf_sha256'], target, timeout=60)

try:
    print('INSTALL normal-trust candidate', flush=True)
    save('installed.json', dict(identity=install(ART / 'app.bin'), persistence=verify_snapshot(BOARD, before)))
    for name, digest in sources.items():
        require(sha(Path(name).read_bytes()) == digest, 'Test source changed')
    require(Path('tools/esp32c3_tests/public_streams.json').read_bytes() == (ROOT / 'public_streams.json').read_bytes(), 'Public source manifest changed')
    command = [sys.executable, '-B', '-X', 'utf8', 'tools/esp32c3_tests/quiet_acceptance.py',
        '--board', BOARD.origin, '--host', '192.168.100.253', '--firmware', str(ART / 'app.bin'),
        '--suite', 'public', '--seconds', '60', '--aac-reference-command',
        str(ROOT / 'faad-reference-command.json'), '--output', str(OUT / 'public')]
    started = time.perf_counter()
    with (OUT / 'public.log').open('xb') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        save('running.json', dict(pid=child.pid, command=command, started_at=started))
        print('START five public HTTPS variants', flush=True)
        try:
            code = child.wait(timeout=900)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
            code = 124
    save('phase.json', dict(code=code, seconds=time.perf_counter() - started))
    print('END public HTTPS', code, flush=True)
    require(code == 0, 'Public acceptance failed; preserve failures and restore')
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
        require(all(not s['audio'] for s in states), 'Playback state not restored')
        print('RESTORED image and settings', flush=True)
    except Exception as error:
        save('restoration-failure.json', dict(exception_chain=exception_details(error)))
        raise
