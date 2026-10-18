"""Qualify confirmed C3 Web/network bounds and file-loss fixes.

Compiles actual production functions against host IO/SDK seams. Historical
negative controls use the pre-change Git source, never alternate pseudocode.
No credentials are printed and no board, SDK build, or network is accessed.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
STORAGE=ROOT/'idf/components/native_storage'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def function(source,name):
    match=re.search(r'^(?:static[ \t]+)?[A-Za-z_]\w*[ \t*]+'+re.escape(name)+r'\s*\(',source,re.M)
    assert match,name
    start=match.start()
    opening=source.index('{',start)
    count=1;position=opening+1
    while count:
        count+=(source[position]=='{')-(source[position]=='}')
        position+=1
    return source[start:position]+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline',default='533ce63328fc06d1a91c0369679cc9a559ba891d')
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    baseline=subprocess.check_output(['git','rev-parse',args.baseline],cwd=ROOT,text=True).strip()
    current={name:(MAIN/name).read_text() for name in ['network_service.c','web_upload.c','web_service.c','web_file_form.h']}
    old={name:subprocess.check_output(['git','show',f'{baseline}:{(MAIN/name).relative_to(ROOT).as_posix()}'],cwd=ROOT).decode()
         for name in current}
    report={'baseline_commit':baseline,'negative_controls':{},'current':{},'physical_flash_tested':False}
    for name,text in old.items():(out/('baseline-'+name)).write_text(text)
    common=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function',
            '-Wno-unused-variable','-Wno-misleading-indentation','-pthread',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']

    def execute(name,test,flags=(),arguments=(),negative=False):
        binary=out/name
        command=common+(['-Wno-error'] if negative else [])+list(flags)+[
            '-I'+host(out),'-I'+host(MAIN),'-I'+host(STORAGE),'-I'+host(STORAGE/'include'),host(test),'-o',host(binary)]
        (out/(name+'-build.log')).write_bytes(run(command))
        try:
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                     'UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary),*arguments])
            success=True
        except subprocess.CalledProcessError as error:
            log=error.output;success=False
        (out/(name+'.log')).write_bytes(log)
        if negative:
            assert not success,name+' failed to detect historical regression'
            report['negative_controls'][name]='DETECTED'
        else:
            assert success,log.decode(errors='replace')
            print(log.decode(),end='');report['current'][name]='PASS'

    storage_source=current['web_upload.c']
    helpers=storage_source[storage_source.index('static SemaphoreHandle_t s_storage_lock;'):
                           storage_source.index('// All three routes')]
    paths=function(storage_source,'temporary_path')
    wifi_names=['prepare_station_config','next_credential_row','read_credentials',
                'network_service_validate_credentials_file','network_service_save_credentials_file']

    def storage_includes(wifi_source,publisher):
        (out/'storage-production.inc').write_text(helpers+paths+function(publisher,'publish_file'))
        (out/'wifi-production.inc').write_text(''.join(function(wifi_source,name) for name in wifi_names
                                                       if name+'(' in wifi_source))

    storage_test=ROOT/'tests/native/web_warning_storage_test.c'
    storage_includes(current['network_service.c'],storage_source)
    fs=out/'fs-current';fs.mkdir();execute('storage',storage_test,arguments=[host(fs)])
    storage_includes(old['network_service.c'],storage_source)
    fs=out/'fs-negative-wifi';fs.mkdir();execute('negative-wifi-loss',storage_test,arguments=[host(fs)],negative=True)
    fs=out/'fs-negative-row';fs.mkdir();execute('negative-wifi-row',storage_test,flags=['-DROWS_ONLY=1'],arguments=[host(fs)],negative=True)
    storage_includes(current['network_service.c'],old['web_upload.c'])
    fs=out/'fs-negative-asset';fs.mkdir();execute('negative-asset-loss',storage_test,arguments=[host(fs)],negative=True)
    storage_includes(current['network_service.c'],storage_source)

    static_test=ROOT/'tests/native/web_warning_static_test.c'
    (out/'static-production.inc').write_text(function(current['web_service.c'],'embedded_script_size')+
                                            function(current['web_service.c'],'send_static_file'))
    execute('static',static_test)
    old_static=old['web_service.c'];start=old_static.index('    char chunk[CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES];')
    end=old_static.index('\nstatic void static_worker_task',start)
    (out/'static-production.inc').write_text('static esp_err_t send_static_file(httpd_req_t *request, FILE *file) {\n'+old_static[start:end])
    execute('negative-stream-reread',static_test,flags=['-DBASELINE=1'],negative=True)
    (out/'static-production.inc').write_text(function(current['web_service.c'],'embedded_script_size')+
                                            function(current['web_service.c'],'send_static_file'))

    names_test=ROOT/'tests/native/web_warning_names_test.c'
    (out/'form-production.h').write_text(old['web_file_form.h'])
    execute('negative-small-name',names_test,flags=['-DCONFIG_SPIFFS_OBJ_NAME_LEN=8'],negative=True)
    overflow=(out/'negative-small-name.log').read_bytes()
    assert b'AddressSanitizer' in overflow or b'buffer overflow detected' in overflow
    report['negative_controls']['negative-small-name']='DETECTED '+('ASan overflow' if b'AddressSanitizer' in overflow else 'host FORTIFY overflow')
    (out/'form-production.h').write_text(current['web_file_form.h'])
    for capacity in [1,8,9,12,13,32,256]:
        execute(f'name-{capacity}',names_test,flags=[f'-DCONFIG_SPIFFS_OBJ_NAME_LEN={capacity}'])
    files=[Path(__file__),ROOT/'tests/run-esp32c3-web-memory.py',storage_test,static_test,names_test,
           *(MAIN/name for name in current),MAIN/'web_upload.h',MAIN/'web_multipart.h',
           STORAGE/'file_transaction.c',STORAGE/'include/file_transaction.h']
    report['source_sha256']={path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    for path in files:
        snapshot=out/'sources'/path.relative_to(ROOT)
        snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(path.read_bytes())
    report['passed']=True
    report['scope']='Actual production functions and actual shared file transaction; mapped host filesystem with SPIFFS no-overwrite rename/error seams, pthread serialization, stdio EOF/error seams. No claim of multi-file CSV/index atomicity or physical flash durability.'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
