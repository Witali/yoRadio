"""Qualify PCM tail submission and playback, then restore saved production."""
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

ROOT = Path('.build/c3-staged-flow-20261009')
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


def install(path, clock_mode=None, label=None):
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
            save((label or clock_mode)+'-clock.json',dict(identity=identity,rows=capture.rows,
                transport=capture.transport,clocks=[],parsed=False))
            observed = [dict(at=r['at'], **value) for r in capture.rows
                        if r['at'] >= started and (value := parse_clock(r['line'])) is not None]
            save((label or clock_mode)+'-clock.json',dict(identity=identity, rows=capture.rows,
                transport=capture.transport, clocks=observed,parsed=True))
            require(len(observed) == 1, 'Expected one fresh PDM initialization readback')
            require(observed[0]['exact_nominal_48khz'] == (clock_mode == 'fractional'),
                    'Actual clock registers do not match requested experiment')
        return identity
    finally:
        if capture and capture.thread.is_alive(): capture.close()


require(not OUT.exists(), 'Preserve existing physical evidence')
OUT.mkdir()
CONTROL=Path('firmware/development/esp32c3-idf-6.1-r9a97-pcm-tail/app.bin')
PROFILE=Path('firmware/development/esp32c3-idf-6.1-r9a97-staged-flow/app.bin')
images={name:image_info(path.read_bytes()) for name,path in
        [('control',CONTROL),('profile',PROFILE),('quiet',QUIET)]}
require(images['control']['sha256']=='e7d19f98719bb2f8b244096dffe73f57a98794d53fcb63ad918ff3ffbf3c1853','Control changed')
require(images['profile']['sha256']=='5f01f51c323d48e3ad59f198f0bb6b5e0615baedd84ba6359ffe15acc83cbea0','Profile changed')
require(images['quiet']['sha256']=='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a','Restore image changed')
cert=ssl._ssl._test_decode_cert(str(TRUST/'server.pem'))
require(ssl.cert_time_to_seconds(cert['notBefore'])<time.time() and
        ssl.cert_time_to_seconds(cert['notAfter'])>time.time()+2400,'Certificate validity too short')
identity,initial=BOARD.info(),BOARD.status()
require(identity['app_elf_sha256']==images['quiet']['app_elf_sha256'],'Unexpected initial image')
before=snapshot(BOARD)
sources={p.as_posix():sha(p.read_bytes()) for directory in
         ('tools/esp32c3_tests','tools/audio_test_server') for p in sorted(Path(directory).glob('*.py'))}
save('initial.json',dict(identity=identity,status=initial,images=images,
    source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    test_sources_sha256=sources,ca_sha256=sha((TRUST/'ca.pem').read_bytes()),
    leaf_sha256=sha((TRUST/'server.pem').read_bytes())))
phases=[]

def run_phase(name,image,seconds,modes,timeout):
    for relative,digest in sources.items():
        require(sha(Path(relative).read_bytes())==digest,'Test source changed during run')
    command=[sys.executable,'-X','utf8','tools/esp32c3_tests/trace_transport.py',
        '--runner','tls_records','--','--board',BOARD.origin,'--host',HOST,
        '--serial-port',PORT,'--firmware',str(image),'--ca',str(TRUST/'ca.pem'),
        '--cert',str(TRUST/'server.pem'),'--key',str(TRUST/'server.key'),
        '--seconds',str(seconds),'--pacing-ratio','1.0','--output',str(OUT/name)]
    for mode in modes: command+=['--mode',mode]
    started=time.monotonic()
    print('START',name,flush=True)
    with (OUT/(name+'.log')).open('xb') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        save('running.json',dict(phase=name,pid=process.pid,started_at=started))
        try: code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill();process.wait();code=124
    phases.append(dict(name=name,code=code,seconds=time.monotonic()-started,
                       image_sha256=sha(image.read_bytes())))
    save('phases.json',phases)
    print('END',name,code,flush=True)
    require(code!=124,'Phase exceeded its deadline')
    require(BOARD.info()['app_elf_sha256']==image_info(image.read_bytes())['app_elf_sha256'],
            'Wrong image after phase')

attempted=False
try:
    attempted=True
    print('INSTALL control',flush=True)
    save('installed-control.json',dict(identity=install(CONTROL,'fractional','control'),
                                      persistence=verify_snapshot(BOARD,before)))
    BOARD.stop()
    run_phase('control-short',CONTROL,75,['small','large'],240)
    print('INSTALL profile',flush=True)
    save('installed-profile.json',dict(identity=install(PROFILE,'fractional','profile'),
                                      persistence=verify_snapshot(BOARD,before)))
    BOARD.stop()
    run_phase('profile-short',PROFILE,75,['small','large'],240)
    run_phase('profile-long',PROFILE,600,['alternate'],750)
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
