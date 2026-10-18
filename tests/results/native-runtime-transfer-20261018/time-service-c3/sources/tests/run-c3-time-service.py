"""Exercise actual C3 time adapter worker/controller and timezone WS serializer.

RTOS tasks are real pthread owners; settings and shared SNTP APIs are explicit
boundaries. Actual pinned SNTP/DNS lifetime is qualified by a separate runner.
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
from run_output_dma_host import host,run

def function(text,name):
    m=re.search(r'^static [^\n]*\b'+name+r'\(',text,re.M);assert m,name
    start=text.index('{',m.start());end=start+1;level=1
    while level:level+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[m.start():end]+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32c3-oled-native/main';test=ROOT/'tests/native';backend=ROOT/'idf/components/native_time/include'
    files=[Path(__file__).resolve(),*[main/n for n in ('time_service.c','time_service.h','runtime_settings.h','websocket_service.c','json_buffer.h')],
           *[test/n for n in ('c3_time_service_platform.h','c3_time_service_test.c','c3_time_ws_snapshot_test.c')],backend/'native_time_sntp.h',ROOT/'idf/components/native_stream/include/json_buffer.h']
    hashes={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    for f in files:
        dest=out/'sources'/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes())
    (out/'freertos').mkdir()
    for h in ('esp_err.h','board_config.h','esp_log.h','freertos/FreeRTOS.h','freertos/task.h','freertos/semphr.h'):(out/h).write_text('#pragma once\n')
    source=re.sub(r'^#include[^\n]*\n','',(main/'time_service.c').read_text(),flags=re.M)
    (out/'service.inc').write_text(source)
    ws=(main/'websocket_service.c').read_text()
    (out/'timezone.inc').write_text(function(ws,'json_escape')+function(ws,'send_timezone_settings'))
    common=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable','-Wno-unused-function',
            '-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(out),'-I'+host(main),'-I'+host(test),'-I'+host(backend)]
    env=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1']
    report=dict(passed=False,scope=__doc__,source_sha256=hashes,cases={},negative_controls={})
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def build(fixture,tag):
        binary=out/tag
        try:log=run(common+[host(test/fixture),'-o',host(binary)])
        except subprocess.CalledProcessError as e:(out/(tag+'-build.log')).write_bytes(e.output);print(e.output.decode(errors='replace'));raise
        (out/(tag+'-build.log')).write_bytes(log);return binary
    binary=build('c3_time_service_test.c','adapter')
    for case in ('offline','early_ip','snapshot_failure','init_failure','setenv_failure','apply_failure','restart_failure','task_failure','mutex_oom','concurrent_start','serialized_order','reconnect_serialized','timezone'):
        try:log=run(env+[host(binary),case])
        except subprocess.CalledProcessError as e:(out/(case+'-failure.log')).write_bytes(e.output);save();print(e.output.decode(errors='replace'));raise
        (out/(case+'.log')).write_bytes(log);report['cases'][case]=log.decode().strip();save()
    ui=build('c3_time_ws_snapshot_test.c','timezone-ws')
    try:log=run(env+[host(ui)])
    except subprocess.CalledProcessError as e:(out/'timezone-ws-failure.log').write_bytes(e.output);print(e.output.decode(errors='replace'));raise
    (out/'timezone-ws.log').write_bytes(log);report['cases']['timezone-ws']=log.decode().strip()
    apply_begin=source.index('esp_err_t time_service_apply(void) {')
    apply_end=source.index('\nvoid time_service_notify_network_ready(',apply_begin)
    public_apply=source[apply_begin:apply_end]
    unlocked_apply=public_apply.replace('    xSemaphoreTake(lock, portMAX_DELAY);\n','').replace('    xSemaphoreGive(lock);\n','')
    worker_begin=source.index('static void time_sync_task(')
    worker_end=source.index('\nstatic esp_err_t ensure_time_sync_task(',worker_begin)
    worker=source[worker_begin:worker_end]
    unlocked_worker=worker.replace('            xSemaphoreTake(lock, portMAX_DELAY);\n','').replace('            xSemaphoreGive(lock);\n','')
    mutations={
        'lost_first_ip':('atomic_store(&s_network_ready_seen, true);','/* lost initial readiness */','early_ip','applies==1&&!s_apply_pending'),
        'ignored_snapshot_failure':('if (result != ESP_OK) return result;','if (result != ESP_OK) return ESP_OK;','snapshot_failure','time_service_apply()==ESP_ERR_TIMEOUT'),
        'timezone_sign':('int posix_minutes = -offset_minutes;','int posix_minutes = offset_minutes;','timezone','!strcmp(getenv("TZ"),expected)'),
        'offline_ipc':('if (!atomic_load(&s_network_ready_seen)) {','if (false) {','offline','atomic_load(&backend_ready)'),
        'unlocked_apply':(public_apply,unlocked_apply,'serialized_order','active==1'),
        'unlocked_reconnect':(worker,unlocked_worker,'reconnect_serialized','active==1')}
    for name,(old,new,case,assertion) in mutations.items():
        # The first check propagates snapshot failure before init/TZ/backend.
        assert old in source,name
        (out/'service.inc').write_text(source.replace(old,new,1));bad=build('c3_time_service_test.c',name)
        try:run(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(bad),case])
        except subprocess.CalledProcessError as e:
            (out/(name+'.log')).write_bytes(e.output)
            if b'Assertion `' not in e.output or assertion.encode() not in e.output or b'ERROR: AddressSanitizer' in e.output or b'runtime error:' in e.output:save();raise AssertionError('unexpected mutant failure '+name) from e
            report['negative_controls'][name]=dict(rejected=True,case=case,expected_assertion=assertion)
        else:save();raise AssertionError('mutant survived '+name)
    (out/'service.inc').write_text(source)
    report['source_files_still_match_snapshot']=all(hashlib.sha256(f.read_bytes()).hexdigest()==hashes[f.relative_to(ROOT).as_posix()] for f in files)
    assert report['source_files_still_match_snapshot'];report['passed']=True;save()
    print('PASS C3 time adapter: '+str(len(report['cases']))+' groups; '+str(len(report['negative_controls']))+' exact semantic mutants')

if __name__=='__main__':main()
