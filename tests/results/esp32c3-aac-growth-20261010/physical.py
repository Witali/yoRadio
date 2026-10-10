"""One bounded quiet-image HTTP AAC-growth campaign with exact app/settings restoration."""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, exception_details, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from aac_growth import load_pairs

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'physical'
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health')
RESTORE = Path('firmware/development/esp32c3-idf61-listen-48k/app.bin')
board = Board('http://192.168.100.4')
require(not OUT.exists(), 'Preserve previous physical evidence')
reference = ROOT / 'references.json'
load_pairs(ROOT)
candidate, quiet = image_info((ART / 'app.bin').read_bytes()), image_info(RESTORE.read_bytes())
require(candidate['sha256'] == '5505393d2b7d4fcad1303b3b96d9c41709c86a84e687bcbeb059a4241d243da6', 'Candidate changed')
require(quiet['sha256'] == '798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde', 'Restore image changed')
initial, state = board.info(), board.status()
require(initial['app_elf_sha256'] == quiet['app_elf_sha256'] and not state['audio'], 'Unexpected initial board state')
settings = snapshot(board)
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
    reference_sha256=sha(reference.read_bytes()),
    source_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()))

def install(path):
    image = path.read_bytes()
    expected = image_info(image)
    active = board.info()
    require(len(image) <= active['max_size'], 'Image exceeds OTA slot')
    target = 'app1' if active['partition'] == 'app0' else 'app0'
    board.stop()
    code, body = upload(board.origin, multipart(image))
    require(code == 200 and body == b'OK', 'OTA did not return 200 OK')
    return wait_image(board, expected['app_elf_sha256'], target, timeout=60)

try:
    print('INSTALL quiet candidate', flush=True)
    save('installed.json', dict(identity=install(ART / 'app.bin'), persistence=verify_snapshot(board, settings)))
    for name, digest in sources.items():
        require(sha(Path(name).read_bytes()) == digest, 'Test source changed')
    command = [sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/aac_growth.py',
        '--board', board.origin, '--firmware', str(ART / 'app.bin'),
        '--fixtures', str(ROOT), '--host', '192.168.100.253', '--output', str(OUT / 'files')]
    start = time.perf_counter()
    with (OUT / 'files.log').open('xb') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        save('running.json', dict(pid=child.pid, command=command, started_at=start))
        print('START AAC growth files', flush=True)
        try:
            code = child.wait(timeout=900)
        except subprocess.TimeoutExpired:
            child.kill(); child.wait(); code = 124
    save('phase.json', dict(code=code, seconds=time.perf_counter()-start))
    print('END AAC growth files', code, flush=True)
    require(code == 0, 'Physical acceptance failed; preserve evidence')
except Exception as error:
    save('controller-failure.json', dict(exception_chain=exception_details(error)))
    raise
finally:
    print('RESTORE listened image', flush=True)
    try:
        restored = install(RESTORE)
        board.stop()
        states = []
        for _ in range(3):
            time.sleep(5)
            states.append(board.status())
        save('restoration.json', dict(identity=restored, persistence=verify_snapshot(board, settings), states=states))
        require(all(not s['audio'] for s in states), 'Playback state not restored')
        print('RESTORED image and settings', flush=True)
    except Exception as error:
        save('restoration-failure.json', dict(exception_chain=exception_details(error)))
        raise
