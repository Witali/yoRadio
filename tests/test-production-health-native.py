"""Sanitize actual quiet counter and HTTP handler C with SDK call doubles."""
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'.build/production-health-native')
folder=parser.parse_args().output;folder.mkdir(parents=True,exist_ok=True)
main=ROOT/'idf/esp32c3-oled-native/main'
profiler=main/'cpu_profiler.c';web=main/'web_service.c'
profiler_header=main/'cpu_profiler.h'
header=main/'native_audio_output.h'
probe_header=main/'audio_pipeline_probe.h'
harness=ROOT/'tests/native/production_health_test.c'
code=re.sub(r'^#include[^\n]*\n','',profiler.read_text(),flags=re.M)
handler=web.read_text().split('static esp_err_t health_handler(',1)[1].split('static esp_err_t web_memory_handler(',1)[0]
source=harness.read_text().replace('/* PROFILER_SOURCE */',code).replace('/* HEALTH_HANDLER */','static esp_err_t health_handler('+handler)
source=source.replace('/* PROFILER_TYPES */',re.sub(r'^#(?:include|pragma)[^\n]*\n','',profiler_header.read_text(),flags=re.M))
output_type=header.read_text().split('typedef struct {',1)[1].split('} native_audio_output_health_t;',1)[0]
source=source.replace('/* OUTPUT_HEALTH_TYPE */','typedef struct {'+output_type+'} native_audio_output_health_t;')
variants={}
for enabled,probe,arena in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(1,1,1),(1,0,1)):
    name=f'{enabled}-probe{probe}-arena{arena}'
    diagnostic=''
    if probe:
        diagnostic='#define CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC 1\n#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 160\n'
        diagnostic+=re.sub(r'^#(?:include|pragma)[^\n]*\n','',probe_header.read_text(),flags=re.M)
        diagnostic+='\nvolatile audio_pipeline_probe_t s_audio_pipeline_probe;\n'
        diagnostic+='#define CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER 1\n'
    if arena:
        diagnostic+='#define CONFIG_YORADIO_SHARED_DECODER_ARENA 1\n'
    unit=folder/f'health-{name}.c';unit.write_text(source.replace('/* PIPELINE_PROBE_SOURCE */',diagnostic))
    binary=folder/f'health-{name}'
    (folder/f'build-{name}.log').write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-fsanitize=address,undefined','-fno-pie','-no-pie',f'-DCONFIG_ESP_TASK_WDT_EN={enabled}',host(unit),'-o',host(binary)]))
    output=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    (folder/f'run-{name}.log').write_bytes(output)
    value=json.loads(output.splitlines()[0]);assert value['allocation_failures']==2**32-1
    assert value['task_watchdog_events']==(2**32-1 if enabled else 0)
    assert value['last_allocation_failure']==dict(size=2**32-1,caps=2**32-1)
    assert value['decoder_failure']==dict(sequence=2**32-1,codec=2**32-1,stage=2**32-1,
        result=-(2**31),completion=2**32-1,input_bytes=2**32-1,allocation_sequence=2**32-1)
    assert value['uptime_ms']==(2**63-1)//1000 and value['boot_id']=='ffffffffffffffff'
    assert value['heap']==value['largest']==value['minimum_heap']==2**32-1
    assert value['output']==dict(available=True,completion_queue_drops=8 if probe else 2**32-1,write_errors=2**32-1)
    if probe:
        sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
        from production_health import validate_pipeline
        validate_pipeline(value['pipeline'],value['output'])
        assert len(value['pipeline']['events'])==16
        assert value['pipeline']['event_version']==2
        assert value['pipeline']['process_max_us']==2**32-1
        assert value['input_queue']['ready_bytes']==2**32-1
    if arena:
        assert value['decoder_arena']['capacity']==2**32-1
    if arena and probe:
        assert value['arena_timing']['malloc']==[2**32-1]*2
    unavailable=json.loads(output.splitlines()[1])
    assert unavailable['output']==dict(value['output'],available=bool(probe))
    assert b'PASS:' in output
    variants[name]={'passed':True,'json_bytes':len(output.splitlines()[0]),'json':value}
sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (profiler,profiler_header,web,header,probe_header,harness,Path(__file__))}
(folder/'report.json').write_text(json.dumps(dict(variants=variants,sources=sources,scope='Actual C with SDK doubles; no hardware timing claim'),indent=2)+'\n')
print('PASS: quiet C counters and bounded JSON, watchdog and pipeline probe enabled/disabled; ASan/UBSan')
