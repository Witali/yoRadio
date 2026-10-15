"""Sanitize the actual compact pending-owner allocation and free wrappers."""
from pathlib import Path
import hashlib
import json
import sys
import re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
source=ROOT/'idf/esp32c3-oled-native/main/aac_compact_owner.c'
harness=ROOT/'tests/native/aac_compact_reserve_test.c'
text=source.read_text()
start=text.index('void *__real_media_lib_module_calloc(')
end=text.index('int __real_PVMP4AudioDecodeFrame(',start)
out=ROOT/'.build/aac-compact-reserve-host';out.mkdir(parents=True,exist_ok=True)
unit=out/'test.c';unit.write_text(harness.read_text().replace('/* PRODUCTION_RESERVE_AND_WRAPPERS */',text[start:end]))
binary=out/'test'
(out/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-pie','-no-pie',host(unit),'-o',host(binary)]))
log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
(out/'run.log').write_bytes(log)
(out/'report.json').write_text(json.dumps(dict(passed=True,scope=__doc__,sources={
    p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
    for p in (source,harness,Path(__file__))}),indent=2)+'\n')
print(log.decode(),end='')
adapter_source=source.with_name('native_aac_decoder.c')
adapter_harness=harness.with_name('aac_compact_reserve_adapter_test.c')
prefix=unit.read_text().split('int main(void)',1)[0]
adapter=re.sub(r'^#include[^\n]*\n','',adapter_source.read_text(),flags=re.M)
unit=out/'adapter.c'
unit.write_text(prefix+adapter_harness.read_text().replace('/* PRODUCTION_NATIVE_ADAPTER */',adapter))
for slots in (0,4):
    name='adapter' if not slots else 'adapter-input4'
    binary=out/name
    (out/(name+'-build.log')).write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-DCONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS='+str(slots),
        '-fsanitize=address,undefined','-fno-pie','-no-pie',host(unit),'-o',host(binary)]))
    log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    (out/(name+'-run.log')).write_bytes(log)
    print(log.decode(),end='')
report=json.loads((out/'report.json').read_text())
report['adapter_passed']=True
report['adapter_extra_slot_variants']=[0,4]
for p in (adapter_source,adapter_harness):
    report['sources'][p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(log.decode(),end='')
