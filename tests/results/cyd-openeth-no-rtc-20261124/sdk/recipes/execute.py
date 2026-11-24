"""Future guarded execution. Authorized RTC-off build; fixed source and preserved-input guards apply.
Root authorized compilation after bounded preflight; retain the 2 GiB space guard.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from common import SOURCE, guard

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
DEP=Path('C:/Work/yoRadio/.idf')

def load(p): return json.loads(Path(p).read_bytes())
def pin(p):
    body=Path(p).read_bytes(); return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
def write(p,value):
    temporary=Path(str(p)+'.tmp'); temporary.write_text(json.dumps(value,indent=2)+'\n')
    os.replace(temporary,p)
def git(*args): return subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=ROOT)
def same(item):
    assert pin(ROOT/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256']),'Preserved input changed: '+item['path']

def main():
    backend=sys.argv[1]; assert backend in ('pdm','continuous','legacy')
    shell=sys.argv[2]
    preflight=load(BASE/'preflight.json')
    directory=BASE/backend; row=load(directory/'baseline.json')
    status=directory/'execution-status.json'; assert not status.exists()
    report=dict(state='RUNNING',backend=backend,children=[],project_reference='b65437a1bc59c9d269ce7bece597efddc70cea58',source_commit=SOURCE)
    env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',IDF_COMPONENT_MANAGER='0',
        SOURCE_DATE_EPOCH=str(row['source_date_epoch']),GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.longpaths',GIT_CONFIG_VALUE_0='true')
    sdk_python=DEP/'tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
    def call(name,args):
        report['phase']=name
        with (directory/(name+'.stdout.log')).open('xb') as out,(directory/(name+'.stderr.log')).open('xb') as err:
            child=subprocess.Popen(list(map(str,args)),cwd=ROOT,env=env,stdout=out,stderr=err)
            item=dict(phase=name,pid=child.pid,state='RUNNING'); report['children'].append(item); write(status,report)
            code=child.wait(); item.update(state='TERMINAL',exit_status=code); write(status,report)
        assert code==0,name+' failed; original logs retained'
    def invocation(name,build,config,compiler,operation):
        target=ROOT/'tests/target/cyd_full_app_openeth_qemu'
        defaults='sdkconfig.defaults'+{'pdm':'','continuous':';sdkconfig.dac.defaults','legacy':';sdkconfig.legacy-dac.defaults'}[backend]
        parameters=dict(DependencyRoot=str(DEP),AudioBackend=backend,BuildDirectory=str(build),Sdkconfig=str(config),
            IdfArguments=['-D','IDF_TOOLCHAIN='+compiler,'-D','PROJECT_VER='+row['project_version'],
                '-D','SDKCONFIG_DEFAULTS='+defaults,
                '-D','CMAKE_PROJECT_yoradio_cyd2usb_native_INCLUDE='+str(target/'attach.cmake'),
                '-D','CYD_OPENETH_PCM_PROBE=ON','-D','CYD_OPENETH_PCM_SHA256=ON','-D','CYD_OPENETH_RX_BACKOFF=ON',
                '-D','CYD_OPENETH_ALLOCATION_PROBE=ON','-D','CYD_OPENETH_RTC_ACCESS_PROBE=ON',
                '-D','CMAKE_JOB_POOLS=compile=2;link=1','-D','CMAKE_JOB_POOL_COMPILE=compile','-D','CMAKE_JOB_POOL_LINK=link',operation])
        config_file=directory/(name+'-invocation.json')
        config_file.write_text(json.dumps(dict(schema='cyd-final-production-invocation-v1',
            script=str(ROOT/'idf/esp32-cyd2usb-native/build.ps1'),parameters=parameters),indent=2)+'\n')
        call(name,[shell,'-NoLogo','-NoProfile','-File',ROOT/'.build/cyd-final-campaign-20261111-01/invoke-build.ps1','-Invocation',config_file])
    write(status,report)
    try:
        guard(preflight,row)
        assert shutil.disk_usage(ROOT).free>2*1024**3
        cache=(ROOT/row['cache']).resolve(); assert cache.is_relative_to(ROOT/'.build') and not cache.is_relative_to(ROOT/'.build/cws24r')
        assert load(cache/'config/sdkconfig.json')==load(ROOT/row['rtc_on']/'compiled/config/sdkconfig.json')
        for item in row['objects']:
            assert pin(ROOT/item['path'])==item['identity']
        report['rtc_access_probe_enabled']=True; write(status,report)
        invocation('gcc-reconfigure',cache,directory/'sdkconfig','gcc','reconfigure')
        generated=cache/'openeth-rx-overlay/esp_eth_mac_openeth.c'
        assert pin(generated)['sha256']==preflight['generated_sha256']
        invocation('gcc-build',cache,directory/'sdkconfig','gcc','build')
        guard(preflight,row)
        call('stage-fixture',[sdk_python,'-B',ROOT/'tests/target/cyd_full_app_openeth_qemu/prepare.py',
            '--build',cache,'--spiffsgen',DEP/'v6.0.2/components/spiffs/spiffsgen.py','--output',directory/'fixture'])
        compiled=directory/'compiled'; compiled.mkdir()
        for name in ('yoradio_cyd2usb_native.elf','yoradio_cyd2usb_native.map','yoradio_cyd2usb_native.bin',
            'project_description.json','compile_commands.json','config/sdkconfig.json','config/sdkconfig.h'):
            output=compiled/name; output.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(cache/name,output)
        clang=BASE/'clang-shared'; clang.mkdir(exist_ok=True); shutil.copyfile(directory/'sdkconfig',clang/'sdkconfig')
        invocation('clang-reconfigure',clang,clang/'sdkconfig','clang','reconfigure')
        assert pin(clang/'openeth-rx-overlay/esp_eth_mac_openeth.c')['sha256']==preflight['generated_sha256']
        for name in ('sdkconfig','config/sdkconfig.json','config/sdkconfig.h','compile_commands.json'):
            output=compiled/'clang'/name; output.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(clang/name,output)
        call('qualify',[sdk_python,'-B',BASE/'qualify.py',backend])
        guard(preflight,row)
        report.update(state='TERMINAL_PASS',phase='complete',physical_tested=False)
    except Exception as error:
        report.update(state='TERMINAL_NONPASS',failure=str(error)); raise
    finally:
        write(status,report)

if __name__=='__main__': main()
