"""Compile actual CYD/C3 reboot code with pthread races and ASan/UBSan."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    cyd=ROOT/'idf/esp32-cyd2usb-native/main';c3=ROOT/'idf/esp32c3-oled-native/main'
    files=[Path(__file__),ROOT/'tests/native/reboot_lease_test.c',cyd/'web_reboot.c',cyd/'web_reboot.h',c3/'websocket_service.c',c3/'websocket_service.h']
    hashes={}
    for path in files:
        key=path.relative_to(ROOT);raw=path.read_bytes();dest=out/'sources'/key;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        hashes[key.as_posix()]=hashlib.sha256(raw).hexdigest()
    (out/'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_ERR_NO_MEM 0x101\n#define ESP_ERR_INVALID_ARG 0x102\n#define ESP_ERR_INVALID_STATE 0x103\n')
    (out/'esp_http_server.h').write_text('#pragma once\ntypedef void *httpd_handle_t;\n')
    (out/'native_state.h').write_text('#pragma once\ntypedef struct {int unused;} native_state_t;\n')
    report={'source_sha256':hashes,'variants':{},'sanitizers':['ASan','UBSan']}
    for name,mainpath in [('cyd',cyd),('c3',c3)]:
        directory=out/name;directory.mkdir();frozen=out/'sources'/mainpath.relative_to(ROOT)
        text=(frozen/('websocket_service.c' if name=='c3' else 'web_reboot.c')).read_text()
        if name=='c3':text=text[text.index('// The status task exists'):text.index('static void log_setting_error')]
        else:text=re.sub(r'^#include[^\n]*\n','',text,flags=re.M)
        (directory/'reboot-production.inc').write_text(text)
        binary=directory/'test'
        try:
            log=run(['gcc','-std=c11','-D_XOPEN_SOURCE=700',*(['-DTARGET_C3=1'] if name=='c3' else []),'-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-pthread','-I'+host(out),'-I'+host(frozen),'-I'+host(directory),host(out/'sources/tests/native/reboot_lease_test.c'),'-o',host(binary)])
            (directory/'build.log').write_bytes(log)
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
            (directory/'test.log').write_bytes(log);print(name+': '+log.decode().strip())
        except subprocess.CalledProcessError as error:
            (directory/'failure.log').write_bytes(error.output);print(error.output.decode(errors='replace'));raise
        report['variants'][name]={'passed':True,'result':log.decode().strip()}
    report['passed']=True;report['scope']='Actual target reboot/lease functions, real pthread admission/request races and mutex critical sections; deterministic RTOS notification/clock/restart seams. No hardware scheduler or reboot durability claim.'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
