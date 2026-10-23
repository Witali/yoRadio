"""Execute unchanged C3 WS status loop, key/JSON capture and broadcast ownership.

Actual status_task/profile/capture/format/JSON and broadcast admission/dispatch
run together. Deterministic RTOS delay and HTTPD work dispatch, provider snapshots,
clock, session storage and frame-send/shutdown are explicit host seams. No actual
socket/TLS timing or physical stack/RAM claim; those protocol paths have separate
TCP/TLS suites. No production code is rewritten for the positive executable.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host

KEY_FIELDS=('audio_running','volume','balance','bitrate_kbps','sample_rate_hz',
            'channels','bits_per_sample','pcm_sample_rate_hz','pcm_channels',
            'current_item','station_uppercase','station','title','codec','stream_format')
CASES=['initial','unchanged','heartbeat','tick_wrap','changes','reject_status','reject_current','reject_both','held_status','held_current','playlist','list_failure','send_failure','replaced_session','heartbeat_fields','stopped_buffer','profile','json_escape','no_clients','deadline_backpressure','deadline_retry','metadata_bounds',
       'key_padding']+['key_'+field for field in KEY_FIELDS]+['key_tail_'+field for field in KEY_FIELDS[-4:]]

def execute(command,timeout=30):
    r=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout);return r.returncode,r.stdout
def stripped(path):return re.sub(r'^#include[^\n]*\n','',path.read_text(),flags=re.M)
def span(source,start,end):
    first=source.index(start);return source[first:source.index(end,first)]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--case',action='append',choices=CASES,help='Run selected positive cases only; default runs all cases and seven semantic controls')
    a=p.parse_args()
    if a.case and len(a.case)!=len(set(a.case)):p.error('Each --case must be distinct')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32c3-oled-native/main';shared=ROOT/'idf/components/native_stream/include';harness=ROOT/'tests/native/c3_websocket_status_test.c'
    files=[Path(__file__).resolve(),harness,ROOT/'tests/native/c3_ws_status/platform.h',main/'websocket_service.c',main/'websocket_service.h',main/'native_state.h',main/'websocket_message.h',main/'json_buffer.h',shared/'websocket_message.h',shared/'json_buffer.h']
    report={'passed':False,'scope':__doc__,'physical_hardware':False,'full_suite':not a.case,'case_filter':a.case,'cases':{},'negative_controls':{},'source_sha256':{}}
    def save_report():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    for f in files:
        name=f.relative_to(ROOT).as_posix();saved=out/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(f.read_bytes());report['source_sha256'][name]=hashlib.sha256(f.read_bytes()).hexdigest()
    source=(out/'sources'/main.relative_to(ROOT)/'websocket_service.c').read_text()
    production=(span(source,'#define WS_STATUS_POLL_MS','static int ws_wait(')+
      span(source,'static void ws_finish_client(','static esp_err_t websocket_pre_handshake(')+
      span(source,'static esp_err_t ws_send_control(','static void json_escape(')+
      span(source,'static void json_escape(','static esp_err_t ws_send_request(')+
      span(source,'typedef struct {\n    atomic_bool busy;','static void format_status(')+
      span(source,'static void format_status(','static esp_err_t send_initial_state(')+
      span(source,'typedef struct {\n    int64_t started_us;','esp_err_t websocket_service_register('))
    (out/'production.inc').write_text(production);(out/'state-header.inc').write_text(stripped(out/'sources'/main.relative_to(ROOT)/'native_state.h'))
    frozen=out/'sources';command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(out),'-I'+host(frozen/'tests/native'),'-I'+host(frozen/shared.relative_to(ROOT)),host(frozen/harness.relative_to(ROOT)),'-o',host(out/'status')]
    def build(suffix=''):
        cmd=command.copy();cmd[-1]+=suffix;code,log=execute(cmd,60);(out/('build'+suffix+'.log')).write_bytes(log)
        if code:raise RuntimeError(log.decode(errors='replace'))
        return Path(str(out/'status')+suffix)
    binary=build();report['command']=command
    cases=a.case or CASES
    save_report()
    for case in cases:
        code,log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case]);(out/(case+'.log')).write_bytes(log)
        if code:
            report['cases'][case]={'passed':False,'status':code};save_report()
            raise RuntimeError(case+': '+log.decode(errors='replace'))
        messages=[json.loads(line[5:]) for line in log.decode().splitlines() if line.startswith('JSON ')]
        assert all(isinstance(message,dict) for message in messages)
        report['cases'][case]={'passed':True,'json_frames':len(messages),'result':log.decode().splitlines()[-1]}
        save_report()
    mutations={
      'advance_after_one_admission':('if (status_queued && current_queued) {','if (status_queued || current_queued) {','reject_current','previous key advances only after both admissions'),
      'false_current_success':('bool current_queued = !station_changed;','bool current_queued = true;','held_current','previous key advances only after both admissions'),
      'rewrite_pending_status':('atomic_load(&s_status_send_pending) == 0U) {','true) {','held_status','queued payload immutable until HTTPD dispatch'),
      'rewrite_pending_current':('atomic_load(&s_current_send_pending) == 0U;','true;','held_current','queued payload immutable until HTTPD dispatch'),
      'lost_admission_unwind':('atomic_fetch_sub(pending, 1U);','/* negative: pending count leaks on rejected work */','reject_status','previous key advances only after both admissions'),
      'lost_playlist_retry':('atomic_store(&s_playlist_changed_pending, true);','/* negative: drop playlist retry */','playlist','atomic_load(&s_playlist_changed_pending)'),
      'lost_deadline_poll':('        poll_message_deadlines();','        /* negative: no fragmented message deadlines */','deadline_backpressure','accepted[DEADLINE]==1'),
    }
    if a.case:mutations={}
    for name,(old,new,case,assertion) in mutations.items():
        # The playlist flag setter also contains the same line; mutate only the
        # retry branch, before the public notification function.
        at=production.index(old);mutated=production[:at]+production[at:].replace(old,new,1);(out/'production.inc').write_text(mutated);negative=build('-negative-'+name)
        code,log=execute(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(negative),case]);(out/('negative-'+name+'.log')).write_bytes(log)
        assert code and b'Assertion' in log and assertion.encode() in log,(name,log)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log
        report['negative_controls'][name]={'case':case,'status':code,'expected_assertion':assertion,'rejected':True}
    (out/'production.inc').write_text(production);report['passed']=True;save_report();print('PASS',len(cases),'actual loop cases +',len(mutations),'semantic mutants','(filtered)' if a.case else '(full suite)')
if __name__=='__main__':main()
