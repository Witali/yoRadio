"""Compile actual CYD/C3 reboot code with pthread races and ASan/UBSan."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    cyd=ROOT/'idf/esp32-cyd2usb-native/main';c3=ROOT/'idf/esp32c3-oled-native/main'
    files=[Path(__file__),ROOT/'tests/native/reboot_lease_test.c',cyd/'web_reboot.c',cyd/'web_reboot.h',c3/'websocket_service.c',c3/'websocket_service.h',ROOT/'tools/codec_benchmark/run_output_dma_host.py']
    hashes={}
    for path in files:
        key=path.relative_to(ROOT);raw=path.read_bytes();dest=out/'sources'/key;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        hashes[key.as_posix()]=hashlib.sha256(raw).hexdigest()
    (out/'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_ERR_NO_MEM 0x101\n#define ESP_ERR_INVALID_ARG 0x102\n#define ESP_ERR_INVALID_STATE 0x103\n')
    (out/'esp_http_server.h').write_text('#pragma once\ntypedef void *httpd_handle_t;\n')
    (out/'native_state.h').write_text('#pragma once\ntypedef struct {int unused;} native_state_t;\n')
    for name in ['esp_system.h','freertos/FreeRTOS.h','freertos/task.h']:
        path=out/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n')
    report={'source_sha256':hashes,'variants':{},'sanitizers':['ASan','UBSan'],'negative_controls':{}}
    compiler=run(['gcc','--version']);(out/'compiler.log').write_bytes(compiler)
    report['compiler']=compiler.decode().splitlines()[0]
    original_cyd=(out/'sources'/cyd.relative_to(ROOT)/'web_reboot.c').read_bytes()

    def build(directory,frozen,text,c3_variant=False):
        directory.mkdir(exist_ok=True)
        (directory/'reboot-production.inc').write_bytes(text if isinstance(text,bytes) else text.encode())
        binary=directory/'test'
        command=['gcc','-std=c11','-D_XOPEN_SOURCE=700',*(['-DTARGET_C3=1'] if c3_variant else []),'-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-pthread','-I'+host(out),'-I'+host(frozen),'-I'+host(directory),host(out/'sources/tests/native/reboot_lease_test.c'),'-o',host(binary)]
        (directory/'command.json').write_text(json.dumps(command,indent=2)+'\n')
        try:log=run(command)
        except subprocess.CalledProcessError as error:
            (directory/'build.log').write_bytes(error.output);raise
        (directory/'build.log').write_bytes(log)
        return binary

    def execute(binary,arguments=()):
        command=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary),*arguments]
        try:return 0,run(command)
        except subprocess.CalledProcessError as error:return error.returncode,error.output

    for name,mainpath in [('cyd',cyd),('c3',c3)]:
        directory=out/name;frozen=out/'sources'/mainpath.relative_to(ROOT)
        text=(frozen/('websocket_service.c' if name=='c3' else 'web_reboot.c')).read_text()
        if name=='c3':text=text[text.index('// The status task exists'):text.index('static void log_setting_error')]
        else:text=original_cyd
        binary=build(directory,frozen,text,name=='c3')
        status,log=execute(binary)
        (directory/'test.log').write_bytes(log);print(name+': '+log.decode().strip(),flush=True)
        assert status==0 and b'PASS reboot leases:' in log,(name,status,log)
        assert b'AddressSanitizer' not in log and b'runtime error:' not in log,log
        report['variants'][name]={'passed':True,'result':log.decode().strip()}
        if name=='cyd':
            assert b'PASS reserved-immediate: 208 scenarios;' in log,log
            report['variants'][name]['complete_tu_matches_frozen_bytes']=(directory/'reboot-production.inc').read_bytes()==original_cyd
            assert report['variants'][name]['complete_tu_matches_frozen_bytes']
    source=original_cyd.decode().replace('\r\n','\n')
    immediate=source[source.index('esp_err_t web_reboot_restart_reserved_now'):source.index('esp_err_t web_reboot_abort')]
    mutations=[
        ('release-before-sdk','    portEXIT_CRITICAL(&s_deadline_lock);\n    esp_restart();',
         '    s_reserved_epoch = lease->epoch = 0;\n    portEXIT_CRITICAL(&s_deadline_lock);\n    esp_restart();',
         'reservation_retained_during_restart'),
        ('restart-under-portmux','    portEXIT_CRITICAL(&s_deadline_lock);\n    esp_restart();',
         '    esp_restart();\n    portEXIT_CRITICAL(&s_deadline_lock);',
         'restart_outside_critical'),
        ('ignore-service-lifetime','!atomic_load(&s_ready) || !lease->epoch || lease->epoch != s_reserved_epoch',
         '!lease->epoch || lease->epoch != s_reserved_epoch','unavailable_service_rejects_immediate'),
        ('ignore-exact-token','!atomic_load(&s_ready) || !lease->epoch || lease->epoch != s_reserved_epoch',
         '!atomic_load(&s_ready) || !lease->epoch','stale_copy_cannot_restart_or_consume_new_lease')]
    for name,old,new,marker in mutations:
        assert immediate.count(old)==1,(name,old)
        mutant=source.replace(immediate,immediate.replace(old,new))
        directory=out/name;binary=build(directory,out/'sources'/cyd.relative_to(ROOT),mutant)
        status,log=execute(binary,['interleaving' if name=='release-before-sdk' else 'immediate'])
        (directory/'test.log').write_bytes(log)
        assert status==80 and ('SEMANTIC_FAILURE:'+marker+':').encode() in log,(name,status,log)
        assert b'AddressSanitizer' not in log and b'runtime error:' not in log,log
        report['negative_controls'][name]={'detected':True,'exit_status':status,'expected_marker':marker}
        print('CONTROL '+name+': '+marker,flush=True)
    report['passed']=True;report['scope']='Complete unchanged CYD reboot translation unit and unchanged C3 reboot/lease source slice; real pthread admission/request and AP/OTA reservation races, SDK-entry barriers, mutex critical sections. Deterministic RTOS notification/clock/restart seams. No hardware scheduler, RF eligibility, target ABI or reboot durability claim.'
    report['generated_sha256']={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name not in ['test','report.json'] and 'sources' not in p.relative_to(out).parts}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
