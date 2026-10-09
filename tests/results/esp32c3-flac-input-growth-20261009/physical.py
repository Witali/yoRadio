"""Matched FLAC queue growth A/B/A, switching and AAC TLS recovery."""
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

ROOT = Path('.build/c3-flac-input-growth-20261009')
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


require(not OUT.exists(),'Preserve physical evidence')
OUT.mkdir()
paths={name:Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-input'+name+'/app.bin')
       for name in ('0','4')}
images={name:image_info(path.read_bytes()) for name,path in paths.items()}
manifests={name:json.loads(path.with_name('manifest.json').read_text()) for name,path in paths.items()}
for name in paths:
    require(images[name]==manifests[name]['image'],'Image differs from manifest')
    for field in ('audio_service.c','native_audio_output.c','native_audio_output.h','pipeline_profile.h','pipeline_wait.h','CMakeLists.txt'):
        key='idf/esp32c3-oled-native/main/'+field
        require(manifests[name]['source_overlay_sha256'][key]==manifests['4']['source_overlay_sha256'][key],
                'Controls must have identical firmware implementation')
require(all(v['result']=='PASS' for v in json.loads((ROOT/'build-audit.json').read_text()).values()),'Builds unaudited')
quiet=image_info(QUIET.read_bytes())
require(quiet['sha256']=='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a','Restore changed')
cert=ssl._ssl._test_decode_cert(str(TRUST/'server.pem'))
require(ssl.cert_time_to_seconds(cert['notBefore'])<time.time() and
        ssl.cert_time_to_seconds(cert['notAfter'])>time.time()+2400,'Certificate must cover comparison')
identity,initial=BOARD.info(),BOARD.status()
require(identity['app_elf_sha256']==quiet['app_elf_sha256'],'Unexpected initial image')
before=snapshot(BOARD)
sources={p.as_posix():sha(p.read_bytes()) for folder in
         ('tools/esp32c3_tests','tools/audio_test_server') for p in sorted(Path(folder).glob('*.py'))}
save('initial.json',dict(identity=identity,status=initial,images=images,quiet=quiet,
    source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    test_sources_sha256=sources,ca_sha256=sha((TRUST/'ca.pem').read_bytes()),
    leaf_sha256=sha((TRUST/'server.pem').read_bytes())))
phases=[]
shared=['--board',BOARD.origin,'--host',HOST,'--serial-port',PORT]
tls=['--https-origin','https://'+HOST+':8771','--tls-cert',str(TRUST/'server.pem'),'--tls-key',str(TRUST/'server.key')]


def run_phase(label,variant,suite,extra,timeout,records=False):
    for relative,digest in sources.items():require(sha(Path(relative).read_bytes())==digest,'Runner source changed during comparison')
    require(BOARD.info()['app_elf_sha256']==images[variant]['app_elf_sha256'],'Wrong image before phase')
    command=[sys.executable,'-X','utf8','tools/esp32c3_tests/trace_transport.py',
        '--runner','diagnostic','--','run',*shared,'--suite',suite,
        '--sdkconfig',str(paths[variant].with_name('sdkconfig')),'--leave-stopped',
        '--unpaced-files','--delivery-stats','--pacing-ratio','1.0',
        '--output',str(OUT/label),*map(str,extra)]
    if records:
        command=[sys.executable,'-X','utf8','tools/esp32c3_tests/trace_transport.py',
            '--runner','tls_records','--',*shared,'--firmware',str(paths[variant]),
            '--ca',str(TRUST/'ca.pem'),'--cert',str(TRUST/'server.pem'),
            '--key',str(TRUST/'server.key'),'--seconds','75','--mode','grow',
            '--pacing-ratio','1.0','--output',str(OUT/label)]
    started=time.monotonic();print('START',label,flush=True)
    with (OUT/(label+'.log')).open('xb') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        save('running.json',dict(phase=label,pid=process.pid,started_at=started))
        try:code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:process.kill();process.wait();code=124
    phases.append(dict(name=label,variant=variant,code=code,seconds=time.monotonic()-started))
    save('phases.json',phases);print('END',label,code,flush=True)
    require(code!=124,'Phase timed out')
    require(BOARD.info()['app_elf_sha256']==images[variant]['app_elf_sha256'],'Wrong image after phase')


def activate(variant,label):
    print('INSTALL',label,flush=True)
    save('installed-'+label+'.json',dict(identity=install(paths[variant],'fractional',label),
        persistence=verify_snapshot(BOARD,before),variant=variant))
    BOARD.stop()


attempted=False
try:
    attempted=True
    for label,variant in (('flac-control-before','0'),('flac-candidate','4'),('flac-control-after','0')):
        activate(variant,label)
        run_phase(label,variant,'load',['--case','stress-flac-48000-2ch-16bit-610s',
            '--fixture-manifest','.build/c3-reserve-soak-20261008/fixtures/manifest.json',
            '--load-seconds','180','--load-idle-recovery','--sustained-protocol','https',*tls],timeout=330)
    activate('4','switch-candidate')
    run_phase('switch','4','switch',['--case','flac-level8','--case','he-48000-stereo',
        '--case','hev2-44100-stereo','--cycles','3'],timeout=210)
    run_phase('eof-https','4','eof',['--case','flac-level8','--case','hev2-44100-stereo',
        '--eof-protocol','https',*tls],timeout=240)
    run_phase('records-after-switch','4',None,[],timeout=165,records=True)
    save('settings-after-tests.json',verify_snapshot(BOARD,before))
except Exception as error:
    save('controller-failure.json',dict(exception_chain=exception_details(error)))
    raise
finally:
    if attempted:
        print('RESTORE production application',flush=True)
        try:
            restored=install(QUIET)
            if not initial['audio']:BOARD.stop()
            states=[]
            for _ in range(3):time.sleep(5);states.append(BOARD.status())
            save('restoration.json',dict(identity=restored,persistence=verify_snapshot(BOARD,before),states=states))
            require(all(s['audio']==initial['audio'] for s in states),'Initial playback not restored')
            print('RESTORED production and settings',flush=True)
        except Exception as error:
            save('restoration-failure.json',dict(exception_chain=exception_details(error)))
            raise



