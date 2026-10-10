"""Install the requested production application; retain settings and verify boot/playback."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, check_playback, fixtures, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import HealthBoard, check_health
from sustained_output import sustained_window, check_output, check_memory
from audio_test_server.server import Server
from run import Capture, Suite

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'deployment'
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000')
previous = Path('.build/c3-mp3-transport-controls-20261010/physical-v2/restoration.json')
restored = json.loads(previous.read_text())
require(all(restored['persistence'].values()) and len(restored['states']) == 3,
        'Previous controller has not verified restoration')
require(not OUT.exists(), 'Preserve deployment evidence')
board = Board('http://192.168.100.4')
initial = board.info()
require(initial['app_elf_sha256'] == restored['identity']['app_elf_sha256'], 'Unexpected current image')
require(not board.status()['audio'], 'Expected idle board after completed controller')
image = (ART/'app.bin').read_bytes()
expected = image_info(image)
require(len(image) <= initial['max_size'], 'OTA slot too small')
require(json.loads((ROOT/'production-prefill1000/build-audit.json').read_text())['result'] == 'PASS', 'Missing build audit')
require(json.loads((ROOT/'application-comparison.json').read_text())['result'] == 'PASS', 'Missing object comparison')
specs = fixtures()
before = snapshot(board)
OUT.mkdir()
def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n')
save('initial.json', dict(identity=initial, candidate=expected, controller_sha256=sha(Path(__file__).read_bytes())))
target = 'app1' if initial['partition'] == 'app0' else 'app0'
print('Uploading production application through WebUI OTA', flush=True)
code, body = upload(board.origin, multipart(image))
require(code == 200 and body == b'OK', 'OTA failed')
boot = wait_image(board, expected['app_elf_sha256'], target, timeout=60)
save('installed.json', dict(identity=boot, persistence=verify_snapshot(board, before)))
print('Production image identity and settings verified', flush=True)
b = HealthBoard(board.origin)
suite = Suite(b, 'http://192.168.100.253:8772', {}, Capture(None), OUT)
try:
    b.stop()
    suite.observe(10, 'idle:installed', interval=2)
    with Server('192.168.100.253', 8772, specs, delivery_stats=True, pacing_ratio=1.0) as server:
        name = 'hev2-44100-stereo'
        b.play('http://192.168.100.253:8772/stream/'+name)
        start = len(b.health_samples)
        print('Checking HE-AACv2 at native 44.1 kHz for 60 seconds', flush=True)
        states = suite.observe(60, name)
        rows = b.health_samples[start:]
        steady, measured = sustained_window(states, rows, 60)
        save('health.json', b.health_samples)
        save('server-events.json', server.events)
        result = dict(format=check_playback(states, specs[name], minimum=30, warmup=15),
                      output=check_output(measured), memory=check_memory(measured), health=check_health(rows))
        save('playback.json', dict(result='PASS', evidence=result))
        print('HE-AACv2 playback, output and memory: PASS', flush=True)
finally:
    b.stop()
    states = []
    for _ in range(3):
        time.sleep(3)
        states.append(b.status())
    save('health.json', b.health_samples)
    final = dict(identity=b.info(), persistence=verify_snapshot(board, before), states=states,
                 health=check_health(b.health_samples))
    save('final.json', final)
    require(final['identity']['app_elf_sha256'] == expected['app_elf_sha256'] and all(not s['audio'] for s in states), 'Final state differs')
    print('Production firmware remains installed; settings and idle state preserved', flush=True)
