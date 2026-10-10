"""Sanitize actual quiet counter and HTTP handler C with SDK call doubles."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
folder=ROOT/'.build/production-health-native';folder.mkdir(parents=True,exist_ok=True)
main=ROOT/'idf/esp32c3-oled-native/main'
profiler=main/'cpu_profiler.c';web=main/'web_service.c'
harness=ROOT/'tests/native/production_health_test.c'
code=re.sub(r'^#include[^\n]*\n','',profiler.read_text(),flags=re.M)
handler=web.read_text().split('static esp_err_t health_handler(',1)[1].split('static esp_err_t reconnect_handler(',1)[0]
source=harness.read_text().replace('/* PROFILER_SOURCE */',code).replace('/* HEALTH_HANDLER */','static esp_err_t health_handler('+handler)
variants={}
for enabled in (0,1):
    unit=folder/f'health-{enabled}.c';unit.write_text(source)
    binary=folder/f'health-{enabled}'
    (folder/f'build-{enabled}.log').write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-fsanitize=address,undefined','-fno-pie','-no-pie',f'-DCONFIG_ESP_TASK_WDT_EN={enabled}',host(unit),'-o',host(binary)]))
    output=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    (folder/f'run-{enabled}.log').write_bytes(output)
    value=json.loads(output.splitlines()[0]);assert value['allocation_failures']==2**32-1
    assert value['task_watchdog_events']==(2**32-1 if enabled else 0)
    assert value['uptime_ms']==(2**63-1)//1000 and value['boot_id']=='ffffffffffffffff'
    assert value['heap']==value['largest']==value['minimum_heap']==2**32-1
    assert b'PASS:' in output
    variants[str(enabled)]={'passed':True,'json':value}
sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (profiler,web,harness,Path(__file__))}
(folder/'report.json').write_text(json.dumps(dict(variants=variants,sources=sources,scope='Actual C with SDK doubles; no hardware timing claim'),indent=2)+'\n')
print('PASS: quiet C counters and bounded JSON, watchdog enabled and disabled; ASan/UBSan')
