"""Qualify minimum-prefill TLS, EOF and OTA, then restore saved production."""
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

ROOT = Path('.build/c3-min250-tls-ota-20261009')
OUT = ROOT/'continuation'
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
IMAGE=Path('firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/app.bin')
UNTRUSTED=Path('.build/c3-tls-final-gates-20261009/untrusted')
expected=image_info(IMAGE.read_bytes())
require(expected['sha256']=='89d320f663bda6439456c95b6f47d09cd5cac2d434ff9fe85df568fa07fbae9c','Candidate changed')
quiet=image_info(QUIET.read_bytes())
require(quiet['sha256']=='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a','Restore image changed')
cert=ssl._ssl._test_decode_cert(str(TRUST/'server.pem'))
require(ssl.cert_time_to_seconds(cert['notBefore']) < time.time() and
        ssl.cert_time_to_seconds(cert['notAfter']) > time.time()+3600,'Certificate must cover experiment')
identity,initial=BOARD.info(),BOARD.status()
require(identity['app_elf_sha256']==quiet['app_elf_sha256'],'Unexpected initial firmware')
before=snapshot(BOARD)  # Private settings exist only in memory.
sources={p.as_posix():sha(p.read_bytes())
         for folder in ('tools/esp32c3_tests','tools/audio_test_server')
         for p in sorted(Path(folder).glob('*.py'))}
save('initial.json',dict(identity=identity,status=initial,candidate=expected,quiet=quiet,
    source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    test_sources_sha256=sources,ca_sha256=sha((TRUST/'ca.pem').read_bytes()),
    leaf_sha256=sha((TRUST/'server.pem').read_bytes()),untrusted_cert_sha256=sha((UNTRUSTED/'cert.pem').read_bytes())))
phases=[]


def run_phase(label,script,arguments,timeout):
    for relative,digest in sources.items():
        require(sha(Path(relative).read_bytes())==digest,'Test source changed during qualification')
    command=[sys.executable,'-X','utf8',script,*map(str,arguments)]
    started=time.monotonic()
    print('START',label,flush=True)
    with (OUT/(label+'.log')).open('xb') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        save('running.json',dict(phase=label,pid=process.pid,started_at=started))
        try: code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill();process.wait();code=124
    phases.append(dict(name=label,code=code,seconds=time.monotonic()-started))
    save('phases.json',phases)
    print('END',label,code,flush=True)
    require(code!=124,'Physical phase timed out')
    require(BOARD.info()['app_elf_sha256']==expected['app_elf_sha256'],'Unexpected firmware after phase')


shared=['--board',BOARD.origin,'--host',HOST,'--serial-port',PORT]
tls=['--firmware',IMAGE,'--ca',TRUST/'ca.pem','--cert',TRUST/'server.pem','--key',TRUST/'server.key']
from failure_monitor import FailureMonitor
monitor=FailureMonitor(OUT)
try:
    attempted=False
    try:
        attempted=True
        print('INSTALL minimum-prefill candidate',flush=True)
        save('installed.json',dict(identity=install(IMAGE,'fractional'),persistence=verify_snapshot(BOARD,before)))
        BOARD.stop()
        run_phase('eof-https-all','tools/esp32c3_tests/trace_transport.py',[
            '--runner','diagnostic','--','run',*shared,'--suite','eof','--eof-protocol','https',
            '--https-origin','https://'+HOST+':8771','--tls-cert',TRUST/'server.pem',
            '--tls-key',TRUST/'server.key','--unpaced-files','--delivery-stats','--pacing-ratio','1.0',
            '--sdkconfig',IMAGE.with_name('sdkconfig'),'--leave-stopped','--output',OUT/'eof-https-all'],720)
        run_phase('ota','tools/esp32c3_tests/ota_diagnostic.py',[
            *shared,'--firmware',IMAGE,'--case','hev2-44100-stereo',
            '--https-origin','https://'+HOST+':8771','--tls-cert',TRUST/'server.pem',
            '--tls-key',TRUST/'server.key','--output',OUT/'ota'],480)
        BOARD.stop()
        run_phase('records-after-ota','tools/esp32c3_tests/trace_transport.py',[
            '--runner','tls_records','--',*shared,*tls,'--seconds','75','--mode','grow',
            '--pacing-ratio','1.0','--output',OUT/'records-after-ota'],160)
        save('settings-after-tests.json',verify_snapshot(BOARD,before))
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
                require(all(s['audio']==initial['audio'] for s in states),'Initial playback not restored')
                print('RESTORED production and settings',flush=True)
            except Exception as error:
                save('restoration-failure.json',dict(exception_chain=exception_details(error)))
                raise
finally:
    monitor.close()
