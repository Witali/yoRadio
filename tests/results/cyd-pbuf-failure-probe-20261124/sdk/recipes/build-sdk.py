import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]; DEP=Path('C:/Work/yoRadio/.idf')
def load(p): return json.loads(Path(p).read_bytes())
def pin(p):
 b=Path(p).read_bytes(); return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
backend,shell=sys.argv[1:3]; assert backend in ('legacy','pdm','continuous')
d=BASE/'sdk'/backend; old=BASE/'sdk-baseline'/backend; row=load(old/'snapshot.json'); p=load(BASE/'candidate-inputs.json')
status=d/'build-status.json'; assert not status.exists()
r=dict(state='RUNNING',backend=backend,source_commit=p['source_commit'],children=[])
def save():
 tmp=status.with_suffix('.tmp'); tmp.write_text(json.dumps(r,indent=2)+'\n'); os.replace(tmp,status)
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',IDF_COMPONENT_MANAGER='0',SOURCE_DATE_EPOCH=str(row['source_date_epoch']))
def guard():
 git=lambda *a:subprocess.check_output(['git','-c','core.longpaths=true',*a],cwd=ROOT)
 assert git('rev-parse','HEAD').decode().strip()==p['source_commit'] and not git('diff','--name-only','HEAD') and not git('diff','--cached','--name-only')
 for name,value in p['sources'].items(): assert pin(ROOT/name)==value
 for item in p['protected']: assert pin(ROOT/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256'])
 assert pin(BASE/'sdk-baseline/baseline-index.json')==p['baseline_index']
def call(name,args):
 r['phase']=name
 with (d/(name+'.stdout.log')).open('xb') as out,(d/(name+'.stderr.log')).open('xb') as err:
  child=subprocess.Popen(list(map(str,args)),cwd=ROOT,env=env,stdout=out,stderr=err)
  item=dict(phase=name,pid=child.pid,state='RUNNING'); r['children'].append(item); save(); code=child.wait()
 item.update(state='TERMINAL',exit_status=code); save(); assert code==0,name+' failed; original logs retained'
def invoke(operation):
 target=ROOT/'tests/target/cyd_full_app_openeth_qemu'; defaults='sdkconfig.defaults'+{'pdm':'','continuous':';sdkconfig.dac.defaults','legacy':';sdkconfig.legacy-dac.defaults'}[backend]
 flags=['-D','IDF_TOOLCHAIN=gcc','-D','PROJECT_VER='+row['project_version'],'-D','SDKCONFIG_DEFAULTS='+defaults,
 '-D','CMAKE_PROJECT_yoradio_cyd2usb_native_INCLUDE='+str(target/'attach.cmake')]
 for flag in ('PCM_PROBE','PCM_SHA256','RX_BACKOFF','ALLOCATION_PROBE','RTC_ACCESS_PROBE','PBUF_FAILURE_PROBE'): flags+=['-D','CYD_OPENETH_'+flag+'=ON']
 flags+=['-D','CMAKE_JOB_POOLS=compile=2;link=1','-D','CMAKE_JOB_POOL_COMPILE=compile','-D','CMAKE_JOB_POOL_LINK=link',operation]
 invocation=dict(schema='cyd-final-production-invocation-v1',script=str(ROOT/'idf/esp32-cyd2usb-native/build.ps1'),parameters=dict(DependencyRoot=str(DEP),AudioBackend=backend,BuildDirectory=str(ROOT/row['cache']),Sdkconfig=str(d/'sdkconfig'),IdfArguments=flags))
 f=d/(operation+'-invocation.json'); f.write_text(json.dumps(invocation,indent=2)+'\n')
 call('gcc-'+operation,[shell,'-NoLogo','-NoProfile','-File',ROOT/'.build/cyd-final-campaign-20261111-01/invoke-build.ps1','-Invocation',f])
save()
try:
 guard(); assert shutil.disk_usage(ROOT).free>2*1024**3
 cache=ROOT/row['cache']; assert load(cache/'config/sdkconfig.json')==load(old/'sdkconfig.json')
 for item in load(old/'objects.json'): assert pin(ROOT/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256'])
 assert pin(cache/'esp-idf/main/libmain.a')==row['main_archive']
 invoke('reconfigure'); assert load(cache/'config/sdkconfig.json')==load(old/'sdkconfig.json') and (cache/'config/sdkconfig.h').read_bytes()==(old/'sdkconfig.h').read_bytes()
 invoke('build'); guard()
 python=DEP/'tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
 call('stage-fixture',[python,'-B',ROOT/'tests/target/cyd_full_app_openeth_qemu/prepare.py','--build',cache,'--spiffsgen',DEP/'v6.0.2/components/spiffs/spiffsgen.py','--output',d/'fixture'])
 compiled=d/'compiled'; compiled.mkdir()
 for name in ('yoradio_cyd2usb_native.elf','yoradio_cyd2usb_native.map','yoradio_cyd2usb_native.bin','project_description.json','compile_commands.json','config/sdkconfig.json','config/sdkconfig.h'):
  destination=compiled/name; destination.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(cache/name,destination)
 guard(); r.update(state='BUILD_PASS_QUALIFICATION_PENDING',phase='compiled-and-frozen')
except Exception as error:
 r.update(state='TERMINAL_NONPASS',failure=str(error)); raise
finally: save()
