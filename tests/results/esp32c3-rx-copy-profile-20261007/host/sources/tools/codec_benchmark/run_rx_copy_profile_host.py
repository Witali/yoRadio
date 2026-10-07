"""Test RX accounting with the pinned real lwIP pbuf/mem implementation."""
import argparse
import hashlib
import json
from pathlib import Path

from run_output_dma_host import host, run

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT/'idf/esp32c3-oled-native/main'
TEST = ROOT/'tests/native/rx_copy_profile'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--idf',type=Path,required=True)
    args=p.parse_args(); args.output.mkdir(parents=True,exist_ok=False)
    sdk=args.idf/'components/lwip/lwip/src'
    files=[MAIN/'rx_copy_profile.c',MAIN/'rx_copy_profile.h',Path(__file__),
           *sorted(p for p in TEST.rglob('*') if p.is_file())]
    report=dict(sources={},sdk_sources={},scope='Real SDK pbuf/mem paths with host platform stubs; not physical timing')
    for path in files:
        name=path.relative_to(ROOT); data=path.read_bytes()
        dest=args.output/'sources'/name; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data)
        report['sources'][name.as_posix()]=hashlib.sha256(data).hexdigest()
    for name in ('pbuf.c','mem.c'):
        data=(sdk/'core'/name).read_bytes()
        (args.output/name).write_bytes(data)
        report['sdk_sources'][name]=hashlib.sha256(data).hexdigest()
    stubs=args.output/'stubs'; (stubs/'freertos').mkdir(parents=True)
    definitions={
        'sdkconfig.h':'#define CONFIG_YORADIO_RX_COPY_PROFILE 1\n#define CONFIG_LWIP_L2_TO_L3_COPY 1\n',
        'esp_heap_caps.h':'#include <stddef.h>\nsize_t heap_caps_get_allocated_size(void *);\n',
        'esp_log.h':'#define ESP_LOGI test_log\n',
        'esp_netif.h':'#pragma once\ntypedef int esp_err_t; typedef struct { int unused; } esp_netif_t;\n#define ESP_OK 0\n#define ESP_FAIL -1\n#define ESP_ERR_NO_MEM -2\n',
        'esp_netif_net_stack.h':'void esp_netif_free_rx_buffer(void *, void *);\n',
        'esp_rom_crc.h':'',
        'esp_timer.h':'#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
        'freertos/FreeRTOS.h':'#include <pthread.h>\n#include <assert.h>\ntypedef pthread_mutex_t portMUX_TYPE;\n#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER\n#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))\n#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))\n',
    }
    for name,data in definitions.items(): (stubs/name).write_text(data)
    binary=args.output/'test'
    command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-fsanitize=address,undefined',
             '-fno-pie','-no-pie','-pthread','-Dmem_clib_malloc=test_malloc',
             '-include',host(TEST/'test_support.h'),'-I'+host(stubs),'-I'+host(TEST),
             '-I'+host(MAIN),'-I'+host(sdk/'include'),host(TEST/'test.c'),
             host(args.output/'pbuf.c'),host(args.output/'mem.c'),'-Wl,--wrap=mem_free','-o',host(binary)]
    (args.output/'build.log').write_bytes(run(command))
    log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    (args.output/'run.log').write_bytes(log)
    report['passed']=True
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(log.decode())


if __name__=='__main__': main()
