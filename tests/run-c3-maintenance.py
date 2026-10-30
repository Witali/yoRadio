"""Concurrent actual C3 stream/decode/output owners and FIFO/reader/helpers.

Pthread RTOS, HTTP, codec create/process/destroy, arena allocator statistics and
output boundary are resource-tracking seams; maintenance acknowledgements are
production code. No codec PCM, allocator correctness, DMA or hardware claim.
Actual staged/direct output implementation is qualified separately.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def execute(args,timeout=30):
    result=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+args,
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    return result.returncode,result.stdout
def stripped(path,keep=()):
    return re.sub(r'^#include[^\n]*\n',lambda m:m.group(0) if any('"'+n+'"' in m.group(0) for n in keep) else '',path.read_text(),flags=re.M)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--case',action='append')
    parser.add_argument('--variant',action='append',choices=['native-staged','native-direct','custom-staged','custom-direct'])
    parser.add_argument('--tsan',action='store_true')
    parser.add_argument('--skip-mutants',action='store_true')
    parser.add_argument('--network-power',action='store_true',help='Link the actual shared policy and assert accepted/maintenance intent')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32c3-oled-native/main';shared=ROOT/'idf/components/native_stream'
    files=[Path(__file__),*[ROOT/'tests/native'/n for n in ('c3_maintenance_platform.h','c3_maintenance_seams.h','c3_maintenance_test.c','audio_power_seam.h')],
           *[main/n for n in ('audio_service.c','native_state.c','stream_http_reader.c','deep_sleep_clock.c')],*main.glob('*.h'),
           shared/'adaptive_input.c',shared/'icy_title.c',*sorted((shared/'include').glob('*.h')),
           ROOT/'idf/components/custom_flac/custom_flac_adapter.h',
           ROOT/'idf/components/custom_legacy_codecs/custom_legacy_adapter.h']
    power=ROOT/'idf/components/native_network_power'
    if args.network_power:files += [power/'native_network_power.c',power/'include/native_network_power.h']
    hashes={}
    for file in files:
        data=file.read_bytes();hashes[file.relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest()
        dest=out/'sources'/file.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    frozen=out/'sources';main=frozen/'idf/esp32c3-oled-native/main';shared=frozen/'idf/components/native_stream';test=frozen/'tests/native'
    (out/'freertos').mkdir()
    for name in ['FreeRTOS.h','semphr.h','task.h','ringbuf.h']:
        (out/'freertos'/name).write_text('#include "'+host(test/'c3_maintenance_platform.h')+'"\n')
    for name in ['esp_err.h','sdkconfig.h','esp_audio_simple_dec.h','esp_http_client.h']:(out/name).write_text('#pragma once\n')
    source=stripped(main/'audio_service.c',('stream_encoded_router.h','stream_start.h'))
    clock=(main/'deep_sleep_clock.c').read_text()
    start=clock.index('static bool idle_clock(');end=clock.index('\nstatic bool controls_released(',start)
    (out/'idle.inc').write_text(clock[start:end])
    for name,path in [('audio.inc',main/'audio_service.c'),('adaptive.inc',shared/'adaptive_input.c'),
                      ('state.inc',main/'native_state.c'),('reader.inc',main/'stream_http_reader.c')]:
        (out/name).write_text(source if name=='audio.inc' else stripped(path))
    defines=['-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1','-DCONFIG_YORADIO_FRAME_ROUTER=1',
             '-DCONFIG_YORADIO_STREAM_CONFIRM=1','-DCONFIG_YORADIO_INPUT_TAIL_COALESCE=1',
             '-DCONFIG_YORADIO_SHARED_DECODER_ARENA=1','-DCONFIG_YORADIO_INPUT_MIN_BLOCKS=5','-DCONFIG_YORADIO_OUTPUT_TASK_FIRST=1',
             '-DCONFIG_YORADIO_STREAM_READ_TIMEOUT_MS=100','-DCONFIG_YORADIO_STREAM_READ_BYTES=2048',
             '-DCONFIG_YORADIO_INPUT_PREFILL_MS=0','-DCONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=0',
             '-DCONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS=0']
    cases=args.case or ['idle','resume','stop_cancels','end_no_resume','end_busy','state_lock','control_lock',
           'queue_failure','wide_epoch','timeout_read','timeout_open','timeout_headers','timeout_close','timeout_cleanup',
           'late_encoded','late_pcm','output_write','output_disable','control_reading','staging',
           'back_to_back','pause_failure','delete_failure','resume_queue_failure','empty_receive_epoch','stopped_no_resume','pending_resume',
           'native_aac','legacy_arena','retry_cleanup','terminal_cleanup','retry_watchdog_off','retry_backoff','shared_arena_tail','legacy_discard_fail','stream_alloc_failure','vendor_pending']
    variants=args.variant or ['native-staged','native-direct','custom-staged','custom-direct']
    report=dict(passed=False,scope=__doc__,variants={},negative_controls={},commands=[],
                complete_matrix=not args.case and not args.variant,mutants_enabled=not args.skip_mutants,
                source_sha256=hashes)
    code,compiler=execute(['gcc','--version']);assert code==0
    (out/'compiler.log').write_bytes(compiler);report['compiler']=compiler.decode().splitlines()[0]
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def build(variant,sanitizer,binary):
        opts=['-DCONFIG_YORADIO_MP3_DECODER_HELIX=1','-DCONFIG_YORADIO_AAC_DECODER_ESPRESSIF=1']
        if variant.startswith('custom'):opts+=['-DCONFIG_YORADIO_FLAC_DECODER_CUSTOM=1']
        if variant.endswith('direct'):opts+=['-DCONFIG_YORADIO_DIRECT_DMA_PCM=1']
        command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable','-Wno-unused-function','-Wno-unused-parameter','-Wno-error=format-truncation',
                 '-pthread','-fno-omit-frame-pointer','-fno-pie','-no-pie','-fsanitize='+sanitizer,*defines,*opts,
                 '-I'+host(out),'-I'+host(test),'-I'+host(shared/'include'),'-I'+host(main),
                 '-I'+host(frozen/'idf/components/custom_flac'),
                 '-I'+host(frozen/'idf/components/custom_legacy_codecs'),
                 host(test/'c3_maintenance_test.c'),host(shared/'icy_title.c'),'-o',host(binary)]
        if sanitizer=='thread':command.insert(1,'-DTEST_TSAN=1')
        if args.network_power:command[1:1]=['-DAUDIO_POWER_INTEGRATION=1','-I'+host(frozen/'idf/components/native_network_power/include'),'-I'+host(frozen/'idf/components/native_network_power')]
        report['commands'].append(command);code,log=execute(command,90);(out/(binary.name+'-build.log')).write_bytes(log)
        if code:save();raise RuntimeError('build '+binary.name+': '+log.decode(errors='replace'))
    for variant in variants:
        binary=out/variant;build(variant,'address,undefined',binary);results={}
        variant_cases=cases+(['retained_dma','retained_pause_failure'] if variant.endswith('direct') and not args.case else [])
        for case in variant_cases:
            command=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case]
            code,log=execute(command);(out/(binary.name+'-'+case+'.log')).write_bytes(log)
            results[case]=dict(status=code,output=log.decode(errors='replace').strip())
            report['variants'][variant]=results;save()
            if code:raise RuntimeError('test '+variant+'/'+case+': '+log.decode(errors='replace'))
        print(variant+': '+str(len(results))+' PASS',flush=True)
    if not args.skip_mutants:
        mutations={
            'decoder_early_ack':('maintenance_active() && maintenance_acked(MAINTENANCE_STREAM)','maintenance_active()','late_encoded','!maintenance_acked(MAINTENANCE_DECODER)'),
            'decoder_stale_epoch':('generation == atomic_load(&s_generation)) {\n                // AUTO forces','true) {\n                // AUTO forces','empty_receive_epoch','!begin_done'),
            'output_early_ack':('if (maintenance_acked(MAINTENANCE_DECODER) &&','if (true &&','late_pcm','!maintenance_acked(MAINTENANCE_OUTPUT)'),
            'ignored_pause':('esp_err_t result = native_audio_output_pause();','esp_err_t result = ESP_OK;','output_write','!http_clients&&!decoder_handles&&!driver.allocated'),
            'lost_resume':('maintenance_finish_locked(phase != MAINTENANCE_END_STOP)','maintenance_finish_locked(false)','resume','esp_timer_get_time()<end'),
            'stale_park':('maintenance_active() && atomic_load(&s_generation) == generation','((void)generation, maintenance_active())','back_to_back','begin_result==expected'),
            'pending_generation':('s_state->audio_generation = command.generation;','/* missing pending generation */','pending_resume','esp_timer_get_time()<end'),
            'stale_metadata':('native_state_begin_stream_locked(s_state, generation);','(void)generation;','output_write','!snapshot->title[0]'),
            'arena_tail_ack':('released = released && !arena.live && !arena.blocks;','(void)arena;','shared_arena_tail','begin_result==expected'),
            'legacy_discard_ack':('released = released && !legacy_decoder && custom_legacy_decoder_discard_arena();','released = released && !legacy_decoder;','legacy_discard_fail','begin_result==expected'),
            'pause_before_phase':('atomic_store(&s_maintenance_phase, MAINTENANCE_REQUESTED);','native_audio_output_request_pause(true); atomic_store(&s_maintenance_phase, MAINTENANCE_REQUESTED);','idle','maintenance_active()'),
            'retry_intent':('connection_remaining_ms(retry.deadline_us))\n                atomic_store(&s_stream_retry_pending, true);','connection_remaining_ms(retry.deadline_us))\n                atomic_store(&s_stream_retry_pending, false);','retry_cleanup','atomic_load(&s_stream_retry_pending)==retry'),
            'pcm_workspace_leak':('if (target_codec == NATIVE_CODEC_AUTO ||\n                codec_uses_custom_legacy(target_codec)) {\n                free(output);','if (target_codec == NATIVE_CODEC_AUTO ||\n                codec_uses_custom_legacy(target_codec)) {\n                /* missing free */','native_aac','!owner_allocations(ROLE_DECODER)')}
        for name,(old,new,case,assertion) in mutations.items():
            assert source.count(old)==1,(name,source.count(old))
            (out/'audio.inc').write_text(source.replace(old,new));binary=out/('negative-'+name)
            build('custom-direct','address,undefined',binary)
            code,log=execute(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case],10)
            (out/(binary.name+'.log')).write_bytes(log)
            if not code or b'Assertion `' not in log or assertion.encode() not in log or b'ERROR: AddressSanitizer' in log or b'runtime error:' in log:
                save();raise AssertionError('unexpected mutant result '+name+': '+log.decode(errors='replace'))
            report['negative_controls'][name]=dict(rejected=True,status=code,case=case,expected_assertion=assertion)
            save()
        (out/'audio.inc').write_text(source)
    if args.tsan:
        binary=out/'tsan';build('custom-direct','thread',binary);logs={};unavailable=None
        for case in cases:
            code,log=execute(['env','TSAN_OPTIONS=halt_on_error=1',host(binary),case])
            (out/('tsan-'+case+'.log')).write_bytes(log)
            if code:
                if b'unexpected memory mapping' in log or b'ThreadSanitizer: unsupported' in log:
                    unavailable=log.decode(errors='replace').strip();break
                if code in (-11,139) and b'HOST_MAIN_ENTERED' not in log:
                    unavailable='TSAN crashed before main; not qualified';break
                save();raise RuntimeError('TSAN '+case+': '+log.decode(errors='replace'))
            logs[case]=log.decode().strip()
        report['tsan']=dict(passed=unavailable is None,unavailable=unavailable,cases=logs)
    report['positive_cases']=sum(len(v) for v in report['variants'].values())
    first=next(iter(next(iter(report['variants'].values())).values()))['output']
    sizes=re.search(r'command=(\d+) token=(\d+) maintenance_fields=(\d+) token_lock=(\d+)',first)
    report['host_layout_bytes']=dict(zip(['command','token','maintenance_scalar_fields','pthread_token_lock'],map(int,sizes.groups())))
    report['host_layout_scope']='No target stack, ABI or linked RAM claim; reuse existing s_last_url/codec, no duplicate 512-byte URL.'
    report['source_files_still_match_snapshot']=all(hashlib.sha256(f.read_bytes()).hexdigest()==hashes[f.relative_to(ROOT).as_posix()] for f in files)
    report['passed']=True;save()

if __name__=='__main__':main()
