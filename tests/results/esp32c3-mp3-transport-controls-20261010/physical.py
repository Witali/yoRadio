"""Compare paced local 44.1/48 kHz MP3 and public HTTP/HTTPS on the same image."""
import http.client
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, Failure, check_playback, check_recovery_heap, exception_details, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import HealthBoard, check_health
from sustained_output import sustained_window, check_output, check_memory
from pipeline_probe import analyze_pipeline
from public_streams import probe
from run import Capture, Suite
from audio_test_server.fixtures import load_fixtures
from audio_test_server.server import Server

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'physical'
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-read-diag')
RESTORE = Path('firmware/development/esp32c3-idf61-listen-48k/app.bin')
board = Board('http://192.168.100.4')
candidate, quiet = image_info((ART / 'app.bin').read_bytes()), image_info(RESTORE.read_bytes())
require(candidate['sha256'] == '174d78968f7e02b37fc05d0d9ae00ad9d342b4bb4b615ce831e771fa6b15947d', 'Diagnostic image changed')
require(quiet['sha256'] == '798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde', 'Restore image changed')
require(board.info()['app_elf_sha256'] == quiet['app_elf_sha256'] and not board.status()['audio'], 'Unexpected initial state')
before = snapshot(board)
require(not OUT.exists(), 'Preserve evidence')
OUT.mkdir()
sources = {}
for folder in ('tools/esp32c3_tests', 'tools/audio_test_server'):
    for file in sorted(Path(folder).glob('*.py')):
        sources[file.as_posix()] = sha(file.read_bytes())
        dest = ROOT / 'test-sources' / file
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(file.read_bytes())

def save(name, value): (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

ffmpeg = shutil.which('ffmpeg')
require(ffmpeg is not None, 'FFmpeg missing')
save('initial.json', dict(candidate=candidate, quiet=quiet, test_sources_sha256=sources,
    controller_sha256=sha(Path(__file__).read_bytes()), ffmpeg_sha256=sha(Path(ffmpeg).read_bytes())))

def install(path):
    image=path.read_bytes(); expected=image_info(image); current=board.info()
    require(len(image)<=current['max_size'], 'OTA slot too small')
    target='app1' if current['partition']=='app0' else 'app0'
    board.stop();code,body=upload(board.origin,multipart(image))
    require(code==200 and body==b'OK','OTA failed')
    return wait_image(board,expected['app_elf_sha256'],target,timeout=60)

def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))

last_progress=0
def checkpoint(completed,batch):
    global last_progress
    if time.perf_counter()-last_progress>=25:
        last_progress=time.perf_counter()
        save('progress.json',dict(case=batch['case'],status=batch['samples'][-1],health=b.health_samples[-1]))
        print('OBSERVE',batch['case'],round(batch['samples'][-1]['seconds']),flush=True)

try:
    print('INSTALL same diagnostic image',flush=True)
    save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
    b=HealthBoard(board.origin)
    suite=Suite(b,'http://192.168.100.253:8772',{},Capture(None),OUT,checkpoint=checkpoint)
    b.stop();suite.observe(12,'idle:initial',interval=1);idle=b.health_samples[-3:]
    specs=load_fixtures(ROOT/'fixtures/manifest.json')
    results={}
    with Server('192.168.100.253',8772,specs,delivery_stats=True,pacing_ratio=1.0) as server:
        cases=[('local44100','http://192.168.100.253:8772/file/mp3-256-44100-stereo','mp3-256-44100-stereo'),
               ('local48000','http://192.168.100.253:8772/file/mp3-256-48000-stereo','mp3-256-48000-stereo'),
               ('public-http','http://ice5.somafm.com/groovesalad-256-mp3',None),
               ('public-https','https://ice5.somafm.com/groovesalad-256-mp3',None)]
        for name,url,fixture in cases:
            b.stop();seconds=90
            if fixture:
                reference=dict(spec={k:v for k,v in specs[fixture].items() if k!='data'},source='generated MP3 verified by FFprobe and full FFmpeg decode')
            else:
                reference=probe('https://ice5.somafm.com/groovesalad-256-mp3','ffprobe')
                if name=='public-http':
                    connection=http.client.HTTPConnection('ice5.somafm.com',timeout=15)
                    connection.request('GET','/groovesalad-256-mp3',headers={'User-Agent':'yoRadio-native/1','Icy-MetaData':'1','Connection':'close'})
                    response=connection.getresponse()
                    reference['http_precheck']=dict(status=response.status,location=response.getheader('Location'),bytes=len(response.read(1024)))
                    connection.close()
                    require(reference['http_precheck']['status']==200 and not reference['http_precheck']['location'],'HTTP comparison redirects')
            host=None;handles=[];host_result=None
            if not fixture:
                ffcommand=[ffmpeg,'-hide_banner','-nostats','-loglevel','error','-rw_timeout','12000000']
                if url.startswith('https:'):ffcommand+=['-tls_verify','1']
                ffcommand+=['-user_agent','yoRadio-native/1','-headers','Connection: close\r\n','-i',url,
                            '-t',str(seconds+5),'-progress','pipe:1','-f','null','-']
                handles=[(OUT/(name+'-host-progress.log')).open('xb'),(OUT/(name+'-host-errors.log')).open('xb')]
                host=subprocess.Popen(ffcommand,stdout=handles[0],stderr=handles[1])
                host_result=dict(command=ffcommand,pid=host.pid,started_at=time.perf_counter())
                save(name+'-host.json',host_result)
            try:
                b.play(url);begin=len(b.health_samples)
                states=suite.observe(seconds,name);rows=b.health_samples[begin:]
                steady,measured=sustained_window(states,rows,seconds)
                results[name]=dict(url=url,reference=reference,seconds=seconds,
                    checks=dict(format=evaluate(lambda:check_playback(states,reference['spec'],minimum=45,warmup=15)),
                                output=evaluate(lambda:check_output(measured)),memory=evaluate(lambda:check_memory(measured))),
                    health=check_health(measured),pipeline=analyze_pipeline(measured),
                    failure_before=rows[0]['pipeline']['stream_failure'],failure_after=rows[-1]['pipeline']['stream_failure'],
                    first_stopped=next((s for s in steady if not s['audio']),None))
                print('RESULT',name,json.dumps(results[name]['checks']),flush=True)
                b.stop()
            finally:
                if host:
                    try:host_result['exit_code']=host.wait(timeout=35)
                    except subprocess.TimeoutExpired:
                        host.kill();host_result['exit_code']=host.wait();host_result['timed_out']=True
                    host_result['ended_at']=time.perf_counter()
                    for handle in handles:handle.close()
                    save(name+'-host.json',host_result)
                save('results.json',results);save('health.json',b.health_samples);save('server-events.json',server.events)
            suite.observe(12,'idle:'+name,interval=1)
        save('server-events.json',server.events)
    save('summary.json',dict(health=check_health(b.health_samples),
        recovery=evaluate(lambda:check_recovery_heap(idle,b.health_samples[-3:])),
        persistence=verify_snapshot(b,before),idle=dict(initial=idle,final=b.health_samples[-3:])))
    save('health.json',b.health_samples)
except Exception as error:
    save('controller-failure.json',dict(exception_chain=exception_details(error)));raise
finally:
    print('RESTORE listened image',flush=True)
    try:
        restored=install(RESTORE);board.stop();states=[]
        for _ in range(3):time.sleep(5);states.append(board.status())
        save('restoration.json',dict(identity=restored,persistence=verify_snapshot(board,before),states=states))
        require(all(not s['audio'] for s in states),'Playback state differs')
        print('RESTORED image and settings',flush=True)
    except Exception as error:
        save('restoration-failure.json',dict(exception_chain=exception_details(error)));raise
