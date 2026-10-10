"""Verify integrated fractional-clock firmware, then restore the listened quiet image."""
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
from flash_mode import validate as validate_flash
from serial_lines import serial_lines
import serial

ROOT = Path('.build/c3-frac4-20261010')
OUT = ROOT/'physical'
QUIET = Path('firmware/development/esp32c3-idf61-listen-48k/app.bin')
TRUST = Path('.build/c3-switch-owner-20261009/trust')
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
                        self.rows.append(dict(at=time.perf_counter(), line=line))
                    elif 'serial capture interrupted' in line:
                        self.transport.append(dict(at=time.perf_counter(), event='intentional-OTA USB interruption'))
            except (OSError, serial.SerialException):
                self.transport.append(dict(at=time.perf_counter(), event='USB reopen pending'))
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
        started = time.perf_counter()
        code, body = upload(BOARD.origin, multipart(image))
        require(code == 200 and body == b'OK', 'App OTA did not return 200 OK')
        identity = wait_image(BOARD, expected['app_elf_sha256'], target, timeout=60)
        if capture:
            deadline = time.perf_counter()+10
            while time.perf_counter() < deadline and not any('PERF PDM_CLOCK' in r['line'] for r in capture.rows):
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
        if capture:
            save(label+'-flash.json',validate_flash('\n'.join(r['line'] for r in capture.rows),image,'qio'))
        return identity
    finally:
        if capture and capture.thread.is_alive(): capture.close()


from public_streams import no_runtime_faults

require(not OUT.exists(), 'Preserve physical evidence')
OUT.mkdir()
CANDIDATE = Path('firmware/development/esp32c3-idf-6.1-r9a97-frac4/app.bin')
candidate, quiet = (image_info(p.read_bytes()) for p in (CANDIDATE,QUIET))
audit = json.loads((ROOT/'frac4/build-audit.json').read_text())
require(audit['result']=='PASS' and audit['image']==candidate, 'Candidate audit mismatch')
require(quiet['sha256']=='798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde','Restore changed')
manifest=json.loads(CANDIDATE.with_name('manifest.json').read_text())
require(manifest['clock_mode']=='fractional' and not manifest['integer_rate_compensation'] and not manifest['fir'],'Wrong clock controls')
require(manifest['extra_trust_ca_sha256']==sha((TRUST/'ca.pem').read_bytes()),'Wrong trust')
cert=ssl._ssl._test_decode_cert(str(TRUST/'server.pem'))
require(ssl.cert_time_to_seconds(cert['notBefore'])<time.time() and ssl.cert_time_to_seconds(cert['notAfter'])>time.time()+3600,'Expired test trust')
identity, initial=BOARD.info(),BOARD.status()
require(identity['app_elf_sha256']==quiet['app_elf_sha256'],'Unexpected initial image')
before=snapshot(BOARD)
sources={p.as_posix():sha(p.read_bytes()) for folder in ('tools/esp32c3_tests','tools/audio_test_server') for p in sorted(Path(folder).glob('*.py'))}
require(sources==json.loads((ROOT/'test-sources.json').read_text()),'Test sources changed')
script_sha=sha(Path(__file__).read_bytes());trial_sha=sha((ROOT/'trial.py').read_bytes())
save('initial.json',dict(identity=identity,status=initial,candidate=candidate,quiet=quiet,
    source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    controller_sha256=script_sha,trial_sha256=trial_sha,test_sources_sha256=sources,
    host_clock=dict(api='time.perf_counter',**vars(time.get_clock_info('perf_counter')))))
shared=['--board',BOARD.origin,'--host',HOST,'--serial-port',PORT]
phases=[]


def run_phase(label,kind):
    require(sha(Path(__file__).read_bytes())==script_sha and sha((ROOT/'trial.py').read_bytes())==trial_sha,'Controller changed')
    for name,digest in sources.items():require(sha(Path(name).read_bytes())==digest,'Test source changed')
    require(BOARD.info()['app_elf_sha256']==candidate['app_elf_sha256'],'Wrong image before phase')
    cmd=[sys.executable,'-X','utf8']
    if kind=='flac':
        cmd += [str(ROOT/'trial.py'),*shared,'--firmware',str(CANDIDATE),'--ca',str(TRUST/'ca.pem'),
                '--cert',str(TRUST/'server.pem'),'--key',str(TRUST/'server.key'),'--seconds','600']
        timeout=750
    else:
        cmd += ['tools/esp32c3_tests/trace_transport.py','--runner','tls_records','--',*shared,
                '--firmware',str(CANDIDATE),'--ca',str(TRUST/'ca.pem'),'--cert',str(TRUST/'server.pem'),
                '--key',str(TRUST/'server.key'),'--mode','grow','--seconds','600','--pacing-ratio','1.0']
        timeout=750
    cmd += ['--output',str(OUT/label)]
    started=time.perf_counter();print('START',label,flush=True)
    with (OUT/(label+'.log')).open('xb') as log:
        process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
        save('running.json',dict(phase=label,pid=process.pid,started_at=started))
        try:code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill();process.wait();code=124
    phases.append(dict(name=label,code=code,seconds=time.perf_counter()-started,image=candidate))
    save('phases.json',phases);print('END',label,code,flush=True)
    require(code!=124,'Phase timed out')
    require(BOARD.info()['app_elf_sha256']==candidate['app_elf_sha256'],'Wrong image after phase')
    rows=json.loads((OUT/label/'performance.json').read_text())
    try:
        require(bool(rows),'Empty runtime capture');no_runtime_faults(rows);result=dict(result='PASS')
    except (AssertionError,ValueError) as error:result=dict(result='FAIL',reason=str(error))
    save(label+'-runtime.json',result)
    require(result['result']=='PASS','Runtime fault requires review before another test')


attempted=False
try:
    attempted=True
    print('INSTALL integrated fractional candidate',flush=True)
    save('installed.json',dict(identity=install(CANDIDATE,'fractional','frac4'),persistence=verify_snapshot(BOARD,before)))
    BOARD.stop()
    run_phase('hev2-tls-grow','tls')
    run_phase('flac-https','flac')
    save('settings-after-tests.json',verify_snapshot(BOARD,before))
except Exception as error:
    save('controller-failure.json',dict(exception_chain=exception_details(error)));raise
finally:
    if attempted:
        print('RESTORE quiet fractional listening image',flush=True)
        try:
            restored=install(QUIET)
            if not initial['audio']:BOARD.stop()
            states=[]
            for _ in range(3):time.sleep(5);states.append(BOARD.status())
            save('restoration.json',dict(identity=restored,persistence=verify_snapshot(BOARD,before),states=states))
            require(all(s['audio']==initial['audio'] for s in states),'Playback state not restored')
            print('RESTORED fractional listening image and settings',flush=True)
        except Exception as error:
            save('restoration-failure.json',dict(exception_chain=exception_details(error)));raise

