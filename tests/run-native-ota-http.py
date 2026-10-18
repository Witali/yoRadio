"""Actual shared OTA form/sink/HTTP and target handlers with pinned SDK I/O.

Flash/image-verifier, network readiness and acknowledged audio are explicit
fault seams. No device is accessed. Fresh --output retains source snapshots.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/native/ota_http'
COMPONENT=ROOT/'idf/components/native_ota'
SDK_ROOT=ROOT/'.idf' if (ROOT/'.idf').is_dir() else ROOT.parents[1]/'.idf'

def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value

def strip_includes(text):return re.sub(r'^\s*#\s*include[^\n]*\n','',text,flags=re.M)

def selected(source,names):
    spans=[]
    for name in names:
        match=re.search(r'^(?:(?:static|inline|const|volatile)[ \t]+)*[A-Za-z_]\w*[ \t*]+'
                        +name+r'\([^;{}]*?\)\s*\{',source,re.M)
        assert match,name
        end=source.index('{',match.start())+1;depth=1
        while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
        spans.append((match.start(),end))
    return '\n'.join(source[a:b] for a,b in sorted(spans))+'\n'

def typedef(source,name):
    match=re.search(r'typedef\s+(?:struct|enum)\s*\{[^{}]*\}\s*'+name+r'\s*;',source,re.S)
    assert match,name
    return match[0]+'\n'

def execute(command,log,negative=False):
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    log.write_bytes(result.stdout)
    if negative:assert result.returncode and b'Assertion' in result.stdout and b'Sanitizer' not in result.stdout,result.stdout.decode(errors='replace')
    elif result.returncode:raise RuntimeError(result.stdout.decode(errors='replace'))
    return result.stdout

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--sdk-cyd',type=Path,default=SDK_ROOT/'v6.0.2')
    parser.add_argument('--sdk-c3',type=Path,default=SDK_ROOT/'v6.1-9a97f6c54ec6')
    parser.add_argument('--target',choices=['cyd','c3','both'],default='both')
    args=parser.parse_args()
    if sys.platform=='win32':
        raise SystemExit(subprocess.call(['wsl.exe','--exec','python3',host(__file__),'--output',host(args.output),'--sdk-cyd',host(args.sdk_cyd),'--sdk-c3',host(args.sdk_c3),'--target',args.target]))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    cyd=ROOT/'idf/esp32-cyd2usb-native/main';c3=ROOT/'idf/esp32c3-oled-native/main'
    files=[Path(__file__),*FIXTURE.glob('*.*'),*COMPONENT.glob('native_ota_*.c'),*COMPONENT.glob('include/*.h'),
        ROOT/'idf/components/native_storage/include/web_multipart.h',ROOT/'idf/components/native_stream/include/json_buffer.h',
        cyd/'web_ota.c',cyd/'web_ota.h',cyd/'web_reboot.c',cyd/'web_reboot.h',cyd/'audio_service.h',
        c3/'web_ota.c',c3/'web_ota.h',c3/'ota_upload.c',c3/'ota_upload.h',c3/'websocket_service.c',c3/'websocket_service.h',c3/'audio_service.h']
    hashes={}
    for file in files:
        relative=file.relative_to(ROOT);raw=file.read_bytes();destination=out/'sources'/relative
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw);hashes[relative.as_posix()]=hashlib.sha256(raw).hexdigest()
    frozen=out/'sources';report={'source_sha256':hashes,'variants':{},'sanitizers':['ASan','UBSan']}
    for target,sdk in [('cyd',args.sdk_cyd),('c3',args.sdk_c3)]:
        if args.target!='both' and args.target!=target:continue
        sdk=sdk.resolve();directory=out/target;directory.mkdir()
        sdkfiles=['components/bootloader_support/include/esp_app_format.h','components/esp_app_format/include/esp_app_desc.h',
            'components/bootloader_support/include/esp_image_format.h',
            'components/esp_http_server/src/httpd_txrx.c','components/esp_http_server/src/httpd_sess.c','components/esp_http_server/src/httpd_parse.c']
        sdkhashes={}
        for key in sdkfiles:
            raw=(sdk/key).read_bytes();destination=directory/'sdk-sources'/key;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
            sdkhashes[key]=hashlib.sha256(raw).hexdigest()
        (directory/'sdk-app-format.h').write_text(strip_includes((directory/'sdk-sources'/sdkfiles[0]).read_text()))
        (directory/'sdk-app-desc.h').write_text(strip_includes((directory/'sdk-sources'/sdkfiles[1]).read_text()))
        image_header=(directory/'sdk-sources'/sdkfiles[2]).read_text()
        (directory/'sdk-image-types.inc').write_text(typedef(image_header,'esp_image_metadata_t')+typedef(image_header,'esp_image_load_mode_t'))
        txrx=(directory/'sdk-sources'/sdkfiles[3]).read_text();sess=(directory/'sdk-sources'/sdkfiles[4]).read_text()
        names=['httpd_sess_set_send_override','httpd_sess_set_recv_override','httpd_send_all','httpd_recv_pending','httpd_recv_with_opt',
            'httpd_recv','httpd_unrecv','httpd_resp_set_hdr','httpd_resp_set_status','httpd_resp_set_type','httpd_resp_send','httpd_req_recv']
        (directory/'sdk-io.inc').write_text(selected(txrx,names))
        (directory/'sdk-context.inc').write_text(selected(sess,['httpd_sess_free_ctx','httpd_sess_get_ctx','httpd_sess_set_ctx']))
        (directory/'sdk-cleanup.inc').write_text(selected((directory/'sdk-sources'/sdkfiles[5]).read_text(),['httpd_req_cleanup']))
        for name in ['esp_err.h','esp_http_server.h','esp_ota_ops.h','esp_app_format.h','esp_app_desc.h','esp_image_format.h',
            'esp_timer.h','esp_system.h','audio_service.h','deep_sleep_clock.h','display_settings.h','native_web_transport.h',
            'freertos/FreeRTOS.h','freertos/task.h','lwip/sockets.h']:
            path=directory/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n#include "host.h"\n')
        (directory/'native_state.h').write_text('#pragma once\ntypedef struct {int unused;} native_state_t;\n')
        for path in COMPONENT.glob('include/*.h'):(directory/path.name).write_bytes((frozen/path.relative_to(ROOT)).read_bytes())
        mainpath=c3 if target=='c3' else cyd
        for name in ['web_ota.h', 'websocket_service.h' if target=='c3' else 'web_reboot.h']:
            (directory/name).write_bytes((frozen/mainpath.relative_to(ROOT)/name).read_bytes())
        if target=='c3':(directory/'ota_upload.h').write_bytes((frozen/c3.relative_to(ROOT)/'ota_upload.h').read_bytes())
        reboot=(frozen/mainpath.relative_to(ROOT)/('websocket_service.c' if target=='c3' else 'web_reboot.c')).read_text()
        if target=='c3':reboot=reboot[reboot.index('// The status task exists'):reboot.index('static void log_setting_error')]
        else:reboot=strip_includes(reboot)
        (directory/'reboot.inc').write_text(reboot)
        unit=directory/'unit.c'
        unit.write_text(('#define TARGET_C3 1\n' if target=='c3' else '')+'''#include "host.h"
#include "web_ota.h"
#include "'''+('websocket_service.h' if target=='c3' else 'web_reboot.h')+'''"
#include "reboot.inc"
#define malloc host_malloc
#include "sdk-io.inc"
#undef malloc
#include "sdk-context.inc"
#include "sdk-cleanup.inc"
#include "native_ota_sink.c"
#include "native_ota_form.c"
#define calloc host_calloc
#include "native_ota_http.c"
#undef calloc
#include "target.inc"
'''+('#include "ota_upload.c"\n' if target=='c3' else '')+'''#include "platform.c"
#include "test.c"
''')
        (directory/'target.inc').write_text(strip_includes((frozen/mainpath.relative_to(ROOT)/'web_ota.c').read_text()))
        includes=[directory,frozen/FIXTURE.relative_to(ROOT),frozen/COMPONENT.relative_to(ROOT),
            frozen/'idf/components/native_storage/include',frozen/'idf/components/native_stream/include',frozen/c3.relative_to(ROOT)]
        flags=['gcc','-std=c11','-D_GNU_SOURCE','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-parameter',
            '-Wno-format','-Wno-sign-compare','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',*['-I'+str(p) for p in includes]]
        binary=directory/'test';execute([*flags,str(unit),'-o',str(binary)],directory/'build.log')
        log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','60',str(binary)],directory/'test.log')
        print(target+': '+log.decode().strip())
        report['variants'][target]={'passed':True,'groups':int(re.search(rb'(\d+) groups',log)[1]),'result':log.decode().strip(),
            'sdk_sha256':sdkhashes,'extracted_sdk_functions':names+['httpd_sess_free_ctx','httpd_sess_get_ctx','httpd_sess_set_ctx','httpd_req_cleanup']}
        mutations={
            'target-policy':('native_ota_form.c','if (strcmp(form->target, "fw") && strcmp(form->target, "firmware"))','if (false)'),
        }
        mutations.update({
            'late-maintenance-ack':('target.inc','return result == ESP_OK && (uint64_t)esp_timer_get_time() >= context->deadline','return false'),
            'response-cancels-boot':('native_ota_http.c','config->finish(config->context, activated);','config->finish(config->context, activated && response == ESP_OK);'),
            'idle-clock-not-reset':('native_ota_http.c','io->last_data = ota_now();\n        if (io->last_data >= deadline)','/* lost controlled-processing idle reset */\n        if (ota_now() >= deadline)'),
        })
        negative={}
        for name,(filename,old,new) in mutations.items():
            source=(directory/filename if filename=='target.inc' else frozen/COMPONENT.relative_to(ROOT)/filename).read_text()
            assert source.count(old)==1,name
            mutant=directory/(name+'.inc');mutant.write_text(source.replace(old,new))
            mutant_unit=directory/(name+'.c');mutant_unit.write_text(unit.read_text().replace('#include "'+filename+'"','#include "'+mutant.name+'"'))
            mutant_binary=directory/name
            execute([*flags,str(mutant_unit),'-o',str(mutant_binary)],directory/(name+'-build.log'))
            execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','60',str(mutant_binary)],directory/(name+'.log'),negative=True)
            negative[name]='DETECTED'
        report['variants'][target]['negative_controls']=negative
    report['scope']='Actual shared form/sink/HTTP and target handler/reboot code, verbatim pinned SDK public image layouts and buffered request-receive/response-send/session-context functions. Field-model SDK structs, deterministic readiness/time/scheduler and acknowledged audio, flash and image-verifier fault seams. Audio-owner implementation is qualified separately; this fixture validates the handler ACK/lease contract. No full HTTP parser/main-loop, real TLS, physical flash or target ABI claim.'
    report['passed']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
