"""Two paced HEv2 loads on one saved image; restore production via app-only OTA."""
import json
from pathlib import Path
import ssl
import subprocess
import sys
import time

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require, sha, exception_details
from ota import snapshot, verify_snapshot, image_info, upload, multipart, wait_image

ROOT = Path('.build/c3-heap-pacing-20261009')
OUT = ROOT/'physical'
QUIET = Path('firmware/development/esp32c3-idf-6.1-r9a97-production-qio80/app.bin')
LAB = Path('firmware/development/esp32c3-idf-6.1-r9a97-flash-qio80/app.bin')
TRUST = Path('.build/c3-tls-records-20261007/trust')
BOARD = Board('http://192.168.100.4')
HOST = '192.168.100.253'


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def install(path):
    image = path.read_bytes()
    expected = image_info(image)
    active = BOARD.info()
    target = 'app1' if active['partition'] == 'app0' else 'app0'
    require(len(image) <= active['max_size'], 'Application exceeds OTA slot')
    BOARD.stop()
    code, body = upload(BOARD.origin, multipart(image))
    require(code == 200 and body == b'OK', 'App OTA did not return 200 OK')
    return wait_image(BOARD, expected['app_elf_sha256'], target, timeout=60)


require(not OUT.exists(), 'Preserve earlier physical evidence')
OUT.mkdir()
quiet, lab = (image_info(p.read_bytes()) for p in (QUIET, LAB))
require(quiet['sha256'] == '21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a', 'Restore image changed')
require(lab['sha256'] == 'eb80d669af3122324370fc776c0a752a70cd83162a673049412890c4eb5d991c', 'Lab image changed')
cert = ssl._ssl._test_decode_cert(str(TRUST/'server.pem'))
require(ssl.cert_time_to_seconds(cert['notBefore']) < time.time() and
        ssl.cert_time_to_seconds(cert['notAfter']) > time.time()+1800, 'Certificate must cover both runs')
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(TRUST/'server.pem', TRUST/'server.key')
identity, initial = BOARD.info(), BOARD.status()
require(identity['app_elf_sha256'] == quiet['app_elf_sha256'], 'Unexpected production image')
before = snapshot(BOARD)  # Credentials stay only in memory.
save('initial.json', dict(identity=identity, status=initial, quiet=quiet, laboratory=lab,
                         cert_sha256=sha((TRUST/'server.pem').read_bytes())))
phases = []
attempted = False
try:
    attempted = True
    print('INSTALL laboratory application by OTA', flush=True)
    save('installed.json', dict(identity=install(LAB), persistence=verify_snapshot(BOARD, before)))
    for label, ratio in [('rate100', '1.0'), ('rate102', '1.02')]:
        # Start both observations from a fresh boot of exactly the same image.
        current = BOARD.info()
        BOARD.reboot()
        time.sleep(3)
        wait_image(BOARD, lab['app_elf_sha256'], current['partition'], timeout=60)
        BOARD.stop()
        command = [sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/diagnostic.py', 'run',
            '--board', BOARD.origin, '--host', HOST, '--serial-port', 'COM9',
            '--output', str(OUT/label), '--sdkconfig', str(LAB.with_name('sdkconfig')),
            '--leave-stopped', '--unpaced-files', '--delivery-stats', '--suite', 'load',
            '--case', 'hev2-44100-stereo', '--load-seconds', '600', '--load-idle-recovery',
            '--sustained-protocol', 'https', '--https-origin', 'https://'+HOST+':8771',
            '--tls-cert', str(TRUST/'server.pem'), '--tls-key', str(TRUST/'server.key'),
            '--pacing-ratio', ratio]
        print('START', label, flush=True)
        started = time.monotonic()
        with (OUT/(label+'.log')).open('xb') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            save('running.json', dict(phase=label, pid=process.pid, started_at=started))
            try:
                code = process.wait(timeout=750)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
                code = 124
        phases.append(dict(name=label, code=code, seconds=time.monotonic()-started))
        save('phases.json', phases)
        print('END', label, code, flush=True)
        require(code != 124, 'Controller time limit reached')
        require(BOARD.info()['app_elf_sha256'] == lab['app_elf_sha256'], 'Unexpected image during tests')
except Exception as error:
    save('controller-failure.json', dict(exception_chain=exception_details(error)))
    raise
finally:
    if attempted:
        print('RESTORE production application by OTA', flush=True)
        try:
            restored = install(QUIET)
            if not initial['audio']:
                BOARD.stop()
            states = []
            for _ in range(3):
                time.sleep(5)
                states.append(BOARD.status())
            result = dict(identity=restored, persistence=verify_snapshot(BOARD, before), states=states)
            save('restoration.json', result)
            require(all(s['audio'] == initial['audio'] for s in states), 'Initial playback state not restored')
            print('RESTORED production and settings', flush=True)
        except Exception as error:
            save('restoration-failure.json', dict(exception_chain=exception_details(error)))
            raise
