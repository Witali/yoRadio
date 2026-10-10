"""Compare integer/fractional PDM at 1.00x; always restore the saved production app."""
import json
from pathlib import Path
import ssl
import subprocess
import sys
import threading
import time

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require, sha, exception_details
from ota import snapshot, verify_snapshot, image_info, upload, multipart, wait_image
from pdm_clock import parse as parse_clock
from serial_lines import serial_lines
import serial

ROOT = Path('.build/c3-pdm-clock-20261009')
OUT = ROOT/'physical'
QUIET = Path('firmware/development/esp32c3-idf-6.1-r9a97-production-qio80/app.bin')
TRUST = Path('.build/c3-tls-records-20261007/trust')
BOARD = Board('http://192.168.100.4')
HOST = '192.168.100.253'
PORT = 'COM9'


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


class ClockCapture:
    """Passive native USB capture; reconnect only across the intentional OTA reboot."""
    def __init__(self):
        self.rows, self.transport = [], []
        self.closed, self.ready = threading.Event(), threading.Event()
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()
        if not self.ready.wait(5):
            self.close()
            require(False, 'USB unavailable for clock capture')

    def read(self):
        first = True
        while not self.closed.is_set():
            port = serial.Serial(port=None, baudrate=115200, timeout=.2)
            port.dtr = port.rts = False
            port.port = PORT
            try:
                port.open()
                if first:
                    port.reset_input_buffer()
                    first = False
                self.ready.set()
                for line in serial_lines(port, self.closed):
                    if 'PERF PDM_CLOCK' in line or line.startswith('FLASH_PROBE_'):
                        self.rows.append(dict(at=time.monotonic(), line=line))
                    elif 'serial capture interrupted' in line:
                        self.transport.append(dict(at=time.monotonic(), event='intentional-OTA USB interruption'))
            except (OSError, serial.SerialException):
                self.transport.append(dict(at=time.monotonic(), event='USB reopen pending'))
            finally:
                port.close()
            self.closed.wait(.2)

    def close(self):
        self.closed.set()
        self.thread.join(3)
        require(not self.thread.is_alive(), 'USB clock capture did not stop')


def install(path, clock_mode=None):
    image = path.read_bytes()
    expected = image_info(image)
    active = BOARD.info()
    target = 'app1' if active['partition'] == 'app0' else 'app0'
    require(len(image) <= active['max_size'], 'Application exceeds OTA slot')
    capture = ClockCapture() if clock_mode else None
    try:
        BOARD.stop()
        started = time.monotonic()
        code, body = upload(BOARD.origin, multipart(image))
        require(code == 200 and body == b'OK', 'App OTA did not return 200 OK')
        identity = wait_image(BOARD, expected['app_elf_sha256'], target, timeout=60)
        if capture:
            deadline = time.monotonic()+10
            while time.monotonic() < deadline and not any('PERF PDM_CLOCK' in r['line'] for r in capture.rows):
                time.sleep(.1)
            capture.close()
            save(clock_mode+'-clock.json',dict(identity=identity,rows=capture.rows,
                transport=capture.transport,clocks=[],parsed=False))
            observed = [dict(at=r['at'], **value) for r in capture.rows
                        if r['at'] >= started and (value := parse_clock(r['line'])) is not None]
            save(clock_mode+'-clock.json',dict(identity=identity, rows=capture.rows,
                transport=capture.transport, clocks=observed,parsed=True))
            require(len(observed) == 1, 'Expected one fresh PDM initialization readback')
            require(observed[0]['exact_nominal_48khz'] == (clock_mode == 'fractional'),
                    'Actual clock registers do not match requested experiment')
        return identity
    finally:
        if capture and capture.thread.is_alive(): capture.close()


require(not OUT.exists(), 'Preserve earlier physical evidence')
OUT.mkdir()
quiet = image_info(QUIET.read_bytes())
require(quiet['sha256'] == '21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a', 'Restore image changed')
images = {mode:Path(f'firmware/development/esp32c3-idf-6.1-r9a97-pdm-{mode}/app.bin')
          for mode in ('integer','fractional')}
audit = json.loads((ROOT/'build-audit.json').read_text())
require(audit['result'] == 'PASS', 'Build comparison not audited')
for mode,path in images.items():
    require(sha(path.read_bytes()) == audit['images'][mode]['image']['sha256'], 'Audited application changed')
cert = ssl._ssl._test_decode_cert(str(TRUST/'server.pem'))
require(ssl.cert_time_to_seconds(cert['notBefore']) < time.time() and
        ssl.cert_time_to_seconds(cert['notAfter']) > time.time()+2700, 'Certificate must cover both runs')
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(TRUST/'server.pem', TRUST/'server.key')
identity, initial = BOARD.info(), BOARD.status()
require(identity['app_elf_sha256'] == quiet['app_elf_sha256'], 'Unexpected production image')
before = snapshot(BOARD)  # Credentials remain in memory only.
save('initial.json', dict(identity=identity, status=initial, quiet=quiet,
    images={m:image_info(p.read_bytes()) for m,p in images.items()},
    cert_sha256=sha((TRUST/'server.pem').read_bytes())))
phases = []
attempted = False
try:
    for mode,path in images.items():
        attempted = True
        print('INSTALL',mode,'by app-only OTA',flush=True)
        save(mode+'-installed.json',dict(identity=install(path, mode),persistence=verify_snapshot(BOARD,before)))
        BOARD.stop()
        command = [sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/diagnostic.py', 'run',
            '--board', BOARD.origin, '--host', HOST, '--serial-port', PORT,
            '--output', str(OUT/mode), '--sdkconfig', str(path.with_name('sdkconfig')),
            '--leave-stopped', '--unpaced-files', '--delivery-stats', '--suite', 'load',
            '--case', 'hev2-44100-stereo', '--load-seconds', '600', '--load-idle-recovery',
            '--sustained-protocol', 'https', '--https-origin', 'https://'+HOST+':8771',
            '--tls-cert', str(TRUST/'server.pem'), '--tls-key', str(TRUST/'server.key'),
            '--pacing-ratio', '1.0']
        print('START',mode,'600s HTTPS HEv2 at 1.00x',flush=True)
        started = time.monotonic()
        with (OUT/(mode+'.log')).open('xb') as log:
            process = subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            save('running.json',dict(phase=mode,pid=process.pid,started_at=started))
            try: code=process.wait(timeout=750)
            except subprocess.TimeoutExpired:
                process.kill();process.wait();code=124
        phases.append(dict(name=mode,code=code,seconds=time.monotonic()-started))
        save('phases.json',phases)
        print('END',mode,code,flush=True)
        require(code != 124,'Physical test timed out')
        require(BOARD.info()['app_elf_sha256'] == image_info(path.read_bytes())['app_elf_sha256'], 'Unexpected image after load')
except Exception as error:
    save('controller-failure.json',dict(exception_chain=exception_details(error)))
    raise
finally:
    if attempted:
        print('RESTORE production application',flush=True)
        try:
            restored=install(QUIET)
            if not initial['audio']: BOARD.stop()
            states=[]
            for _ in range(3):
                time.sleep(5);states.append(BOARD.status())
            save('restoration.json',dict(identity=restored,persistence=verify_snapshot(BOARD,before),states=states))
            require(all(s['audio']==initial['audio'] for s in states),'Initial playback state not restored')
            print('RESTORED production and settings',flush=True)
        except Exception as error:
            save('restoration-failure.json',dict(exception_chain=exception_details(error)))
            raise
