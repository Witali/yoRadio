"""Continue local and OTA tests after preserved public failures; restore the listened image."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require,exception_details,sha
from ota import image_info,snapshot,verify_snapshot,upload,multipart,wait_image
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'physical-local'
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health')
RESTORE=Path('firmware/development/esp32c3-idf61-listen-48k/app.bin')
BOARD=Board('http://192.168.100.4')
HOST='192.168.100.253'
require(not OUT.exists(),'Preserve physical evidence')
candidate=image_info((ART/'app.bin').read_bytes());quiet=image_info(RESTORE.read_bytes())
manifest=json.loads((ART/'manifest.json').read_text())
audit=json.loads((ROOT/'quiet-mpi-health/build-audit.json').read_text())
health=json.loads((ROOT/'health-audit.json').read_text())
require(audit['result']=='PASS' and health['result']=='PASS' and health['elf_sha256']==candidate['app_elf_sha256'],'Missing audits')
require(candidate==audit['image']==manifest['image'] and manifest['production_profile'] and not manifest['lab_ca'],'Wrong candidate')
require(quiet['sha256']=='798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde','Restore image changed')
initial,status=BOARD.info(),BOARD.status()
require(initial['app_elf_sha256']==quiet['app_elf_sha256'],'Unexpected initial firmware')
before=snapshot(BOARD)
reference=Path('.build/idf-upgrade/faad-reference-command.json')
command=json.loads(reference.read_text())
require(Path('C:/Work/yoRadio/.worktree/esp32c3-stream-format/.build/faad2-comparison/probe-float').is_file(),'Missing reference decoder')
OUT.mkdir()
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
sources={p.as_posix():sha(p.read_bytes()) for folder in ('tools/esp32c3_tests','tools/audio_test_server') for p in sorted(Path(folder).glob('*.py'))}
for file in sources:
    dst=ROOT/'test-sources'/file;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(Path(file).read_bytes())
(ROOT/'faad-reference-command.json').write_bytes(reference.read_bytes())
save('initial.json',dict(identity=initial,status=status,candidate=candidate,quiet=quiet,
    controller_sha256=sha(Path(__file__).read_bytes()),test_sources_sha256=sources,
    source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    host_clock=dict(api='time.perf_counter',**vars(time.get_clock_info('perf_counter')))))

def install(path):
    image=path.read_bytes();expected=image_info(image);active=BOARD.info()
    target='app1' if active['partition']=='app0' else 'app0'
    require(len(image)<=active['max_size'],'App exceeds OTA slot')
    BOARD.stop();code,body=upload(BOARD.origin,multipart(image))
    require(code==200 and body==b'OK','App-only OTA did not return 200 OK')
    return wait_image(BOARD,expected['app_elf_sha256'],target,timeout=60)

phases=[]
def run_phase(label,args,limit):
    for file,digest in sources.items():require(sha(Path(file).read_bytes())==digest,'Test source changed')
    require(BOARD.info()['app_elf_sha256']==candidate['app_elf_sha256'],'Wrong app before phase')
    print('START',label,flush=True);start=time.perf_counter()
    with (OUT/(label+'.log')).open('xb') as log:
        proc=subprocess.Popen([sys.executable,'-X','utf8',*map(str,args)],stdout=log,stderr=subprocess.STDOUT)
        save('running.json',dict(phase=label,pid=proc.pid,started_at=start))
        try:code=proc.wait(timeout=limit)
        except subprocess.TimeoutExpired:proc.kill();proc.wait();code=124
    phases.append(dict(name=label,code=code,seconds=time.perf_counter()-start));save('phases.json',phases)
    print('END',label,code,flush=True)
    require(code==0,'Phase failed; preserve original evidence and restore')
    require(BOARD.info()['app_elf_sha256']==candidate['app_elf_sha256'],'Wrong app after phase')

attempted=False
try:
    attempted=True
    print('INSTALL quiet production candidate',flush=True)
    save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(BOARD,before)))
    BOARD.stop()
    common=['tools/esp32c3_tests/quiet_acceptance.py','--board',BOARD.origin,'--host',HOST,'--firmware',ART/'app.bin']
    run_phase('local',[*common,'--suite','http','--suite','transitions','--suite','network','--suite','websocket','--output',OUT/'local'],1200)
    run_phase('ota',['tools/esp32c3_tests/ota.py','--board',BOARD.origin,'--firmware',ART/'app.bin',
        '--suite','negative','--suite','roundtrip','--output',OUT/'ota.json'],600)
    save('settings-after-tests.json',verify_snapshot(BOARD,before))
except Exception as error:
    save('controller-failure.json',dict(exception_chain=exception_details(error)));raise
finally:
    if attempted:
        print('RESTORE listened fractional-clock image',flush=True)
        try:
            restored=install(RESTORE)
            if not status['audio']:BOARD.stop()
            states=[]
            for _ in range(3):time.sleep(5);states.append(BOARD.status())
            save('restoration.json',dict(identity=restored,persistence=verify_snapshot(BOARD,before),states=states))
            require(all(s['audio']==status['audio'] for s in states),'Original playback state not restored')
            print('RESTORED listened image and settings',flush=True)
        except Exception as error:
            save('restoration-failure.json',dict(exception_chain=exception_details(error)));raise
