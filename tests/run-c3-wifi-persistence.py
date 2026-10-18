"""Exercise actual C3 credential APIs, including two historical regressions."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
SHARED=ROOT/'idf/components/native_storage'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
spec=importlib.util.spec_from_file_location('c3_wifi_helpers',ROOT/'tests/run-web-warning-regressions.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline',default='56af3052e8aeaa2416b0bd2836f4ae30971be9bc')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),ROOT/'tests/native/c3_wifi_persistence_test.c',ROOT/'tests/run-web-warning-regressions.py',
        MAIN/'network_service.c',MAIN/'network_service.h',MAIN/'web_upload.c',MAIN/'web_upload.h',
        SHARED/'file_transaction.c',SHARED/'include/file_transaction.h',SHARED/'include/credential_line.h']
    hashes={}
    for file in files:
        data=file.read_bytes();relative=file.relative_to(ROOT);hashes[relative.as_posix()]=hashlib.sha256(data).hexdigest()
        destination=out/'sources'/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    frozen=out/'sources';main=frozen/MAIN.relative_to(ROOT);shared=frozen/SHARED.relative_to(ROOT)
    current=(main/'network_service.c').read_text();storage=(main/'web_upload.c').read_text()
    baseline=subprocess.check_output(['git','rev-parse',args.baseline],cwd=ROOT,text=True).strip()
    old=subprocess.check_output(['git','show',baseline+':idf/esp32c3-oled-native/main/network_service.c'],cwd=ROOT).decode()
    (out/'baseline-network_service.c').write_text(old)
    storage_names=['web_upload_storage_init','backup_name','web_upload_open_file','web_upload_publish_file']
    (out/'c3-storage-production.inc').write_text('static SemaphoreHandle_t s_storage_lock;\n'+''.join(helpers.function(storage,name) for name in storage_names))
    network_names=['prepare_station_config','next_credential_row','read_credentials',
        'network_service_validate_credentials_file','load_validated_credentials',
        'network_service_save_credentials_file','network_service_save_credentials']
    results={}
    for name,source,negative in [('negative-interior-cr',old,'cr'),('negative-postcommit-reload',old,'reload'),('current',current,None)]:
        (out/'c3-wifi-production.inc').write_text(''.join(helpers.function(source,function) for function in network_names if function+'(' in source))
        binary=out/name
        command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
            '-fno-omit-frame-pointer','-fno-pie','-no-pie','-pthread','-I'+host(out),'-I'+host(shared),
            '-I'+host(shared/'include'),host(frozen/'tests/native/c3_wifi_persistence_test.c'),'-o',host(binary)]
        try:log=run(command)
        except subprocess.CalledProcessError as error:
            (out/(name+'-build.log')).write_bytes(error.output);print(error.output.decode(errors='replace'),file=sys.stderr);raise
        (out/(name+'-build.log')).write_bytes(log)
        fs=out/(name+'-fs');fs.mkdir()
        try:
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',
                'timeout','30',host(binary),host(fs),*([negative] if negative else [])]);passed=True
        except subprocess.CalledProcessError as error:log=error.output;passed=False
        (out/(name+'.log')).write_bytes(log)
        if negative:assert not passed,'Historical source did not reproduce '+name;results[name]='DETECTED'
        else:assert passed,log.decode(errors='replace');print(log.decode(),end='');results[name]={'passed':True,'scenarios':int(re.search(rb': (\d+) scenarios',log)[1])}
    (out/'report.json').write_text(json.dumps({'passed':True,'baseline_commit':baseline,'sanitizers':['ASan','UBSan'],
        'source_sha256':hashes,'results':results,'physical_hardware':False,
        'scope':'Actual C3 five-profile validator/save/boot-reader and actual storage/transaction functions over mapped stdio with SPIFFS no-overwrite rename, injected precommit IO/rollback and postcommit fopen OOM/read error. Historical actual source detects interior-CR acceptance and destructive postcommit reload. No network/event concurrency or physical flash durability claim.'},indent=2)+'\n')


if __name__=='__main__':main()
