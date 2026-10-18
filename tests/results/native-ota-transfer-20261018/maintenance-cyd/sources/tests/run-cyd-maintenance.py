"""Run concurrent production CYD audio owners under ASan/UBSan and optionally TSAN.

Actual adaptive_input, stream framing/staging, state and all output backends;
pthread RTOS, codec/HTTP and asynchronous driver barriers are host seams.
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


def execute(args, timeout=20):
    cmd=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+args
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    return result.returncode,result.stdout


def stripped(path,keep=()):
    return re.sub(r'^#include[^\n]*\n',lambda m:m.group(0) if any('"'+n+'"' in m.group(0) for n in keep) else '',path.read_text(),flags=re.M)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--tsan',action='store_true')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32-cyd2usb-native/main';shared=ROOT/'idf/components/native_stream'
    harness=ROOT/'tests/native/cyd_maintenance_test.c'
    files=[Path(__file__).resolve(),harness,ROOT/'tests/native/cyd_maintenance_platform.h',ROOT/'tests/native/cyd_output_pause_test.c',
           *[main/n for n in ('audio_service.c','audio_service.h','native_audio_output.c','native_audio_output.h','native_state.c','native_state.h','native_health.h','input_prefill.h')],
           shared/'adaptive_input.c',shared/'icy_title.c',*sorted((shared/'include').glob('*.h'))]
    for f in files:
        target=out/'sources'/f.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
    (out/'freertos').mkdir()
    for name in ('FreeRTOS.h','semphr.h','task.h'):
        (out/'freertos'/name).write_text('#include "'+host(ROOT/'tests/native/cyd_maintenance_platform.h')+'"\n')
    (out/'esp_err.h').write_text('#pragma once\n')
    source=stripped(main/'audio_service.c',('stream_encoded_router.h','stream_start.h','input_prefill.h'))
    (out/'audio.inc').write_text(source)
    (out/'production.inc').write_text(stripped(main/'native_audio_output.c'))
    (out/'adaptive.inc').write_text(stripped(shared/'adaptive_input.c'))
    (out/'state.inc').write_text(stripped(main/'native_state.c'))
    defines=['-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1','-DCONFIG_YORADIO_FRAME_ROUTER=1',
             '-DCONFIG_YORADIO_STREAM_CONFIRM=1','-DCONFIG_YORADIO_INPUT_TAIL_COALESCE=1','-DCONFIG_YORADIO_INPUT_PREFILL_MS=250']
    cases=['idle','resume','stop_cancels','end_no_resume','end_busy','state_lock','control_lock',
           'queue_failure','wide_epoch','timeout_read','timeout_open','timeout_headers','timeout_close','timeout_cleanup',
           'late_encoded','late_pcm','output_write','output_disable','control_reading','staging',
           'back_to_back','pause_failure','resume_queue_failure','empty_receive_epoch','stopped_no_resume','pending_resume']
    report=dict(passed=False,scope=__doc__,physical_hardware=False,variants={},negative_controls={},
                source_sha256={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
    def build(backend,sanitizer,binary):
        command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable','-Wno-unused-function',
                 '-pthread','-fno-omit-frame-pointer','-fno-pie','-no-pie','-fsanitize='+sanitizer,
                 '-DCONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_'+backend+'=1',*defines,
                 '-I'+host(out),'-I'+host(ROOT/'tests/native'),'-I'+host(main),'-I'+host(shared/'include'),
                 host(harness),host(shared/'icy_title.c'),'-o',host(binary)]
        if sanitizer=='thread':command.insert(1,'-DTEST_TSAN=1')
        code,log=execute(command,60);(out/(binary.name+'-build.log')).write_bytes(log)
        if code:print(log.decode(errors='replace'),file=sys.stderr);raise RuntimeError('build failed '+binary.name)
    for backend in ('PDM','DAC','LEGACY_DAC'):
        binary=out/backend.lower();build(backend,'address,undefined',binary);results={}
        for case in cases+(['delete_failure'] if backend!='LEGACY_DAC' else []):
            code,log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case])
            (out/(binary.name+'-'+case+'.log')).write_bytes(log)
            if code:print(log.decode(errors='replace'),file=sys.stderr);raise RuntimeError('test failed '+binary.name+'/'+case)
            results[case]=log.decode().strip()
        report['variants'][backend]=results;print(backend+': '+str(len(results))+' PASS',flush=True)
    mutations={
        'decoder_early_ack':('maintenance_active() && maintenance_acked(MAINTENANCE_STREAM)','maintenance_active()','late_encoded','!maintenance_acked(MAINTENANCE_DECODER)'),
        'decoder_stale_epoch':('generation == atomic_load(&s_generation)) {\n                maintenance_ack(MAINTENANCE_DECODER);','true) {\n                maintenance_ack(MAINTENANCE_DECODER);','empty_receive_epoch','!begin_done && !maintenance_acked(MAINTENANCE_DECODER)'),
        'output_early_ack':('if (maintenance_acked(MAINTENANCE_DECODER) &&','if (true &&','late_pcm','!maintenance_acked(MAINTENANCE_OUTPUT)'),
        'ignored_dma_pause':('esp_err_t result = native_audio_output_pause();','esp_err_t result = ESP_OK;','output_write','!http_clients&&!decoder_handles&&!driver.allocated'),
        'lost_resume':('maintenance_finish_locked(phase != MAINTENANCE_END_STOP)','maintenance_finish_locked(false)','resume','esp_timer_get_time()<end'),
        'stale_park':('maintenance_active() && atomic_load(&s_generation) == generation','((void)generation, maintenance_active())','back_to_back','begin_result==expected'),
        'lost_pending_generation':('s_state->audio_generation = command.generation;','/* negative: stale pending state generation */','pending_resume','esp_timer_get_time()<end'),
        'stale_metadata':('native_state_begin_audio_locked(s_state, generation, NULL, status);','s_state->audio_generation=generation; s_state->audio_running=false; strlcpy(s_state->stream_format,status,sizeof(s_state->stream_format));','output_write','!snapshot->title[0]'),
    }
    for name,(old,new,case,assertion) in mutations.items():
        assert source.count(old)==1,name
        (out/'audio.inc').write_text(source.replace(old,new));binary=out/('negative-'+name);build('DAC','address,undefined',binary)
        code,log=execute(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case],8)
        (out/(binary.name+'.log')).write_bytes(log)
        if not code:raise AssertionError('negative control survived '+name)
        if b'Assertion `' not in log or assertion.encode() not in log or b'ERROR: AddressSanitizer' in log or b'runtime error:' in log:
            raise AssertionError('unexpected negative failure '+name+': '+log.decode(errors='replace'))
        report['negative_controls'][name]={'rejected':True,'status':code,'case':case,'expected_assertion':assertion,'kind':'semantic assertion'}
    (out/'audio.inc').write_text(source)
    if a.tsan:
        binary=out/'tsan';build('DAC','thread',binary);logs={};unavailable=None
        for case in cases:
            code,log=execute(['env','TSAN_OPTIONS=halt_on_error=1',host(binary),case])
            (out/('tsan-'+case+'.log')).write_bytes(log)
            if code:
                if b'unexpected memory mapping' in log or b'ThreadSanitizer: unsupported' in log:
                    unavailable=log.decode(errors='replace').strip();break
                if code in (-11,139) and b'HOST_MAIN_ENTERED' not in log:
                    unavailable='TSAN process crashed before main (status '+str(code)+'); no TSAN qualification';break
                print(log.decode(errors='replace'),file=sys.stderr);raise RuntimeError('TSAN failed '+case)
            logs[case]=log.decode().strip()
        report['tsan']={'passed':unavailable is None,'unavailable':unavailable,'cases':logs}
    report['compiler']=run(['gcc','--version']).decode().splitlines()[0]
    report['passed']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
