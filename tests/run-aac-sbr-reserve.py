"""Exercise the production reservation/ownership hooks with allocation faults."""
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
with tempfile.TemporaryDirectory(prefix='aac-reserve-') as directory:
    tmp=Path(directory);(tmp/'freertos').mkdir()
    (tmp/'sdkconfig.h').write_text('#define CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE 1\n#define CONFIG_FREERTOS_THREAD_LOCAL_STORAGE_POINTERS 2\n')
    (tmp/'freertos/FreeRTOS.h').write_text('#include <stddef.h>\n')
    (tmp/'freertos/task.h').write_text('void *pvTaskGetThreadLocalStoragePointer(void *,int);\nvoid vTaskSetThreadLocalStoragePointer(void *,int,void *);\n')
    (tmp/'test.c').write_text(r'''
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include "aac_sbr_reserve.h"
static unsigned task,failed,calls,live;
static void *tls[2];
void *pvTaskGetThreadLocalStoragePointer(void *t,int slot){(void)t;assert(slot==1);return tls[task];}
void vTaskSetThreadLocalStoragePointer(void *t,int slot,void *p){(void)t;assert(slot==1);tls[task]=p;}
static void *test_calloc(size_t n,size_t size){++calls;if(failed){--failed;return NULL;}void *p=calloc(n,size);if(p)++live;return p;}
static void test_free(void *p){if(p)--live;free(p);}
void *__real_media_lib_module_calloc(const char *m,size_t n,size_t size){(void)m;return test_calloc(n,size);}
#define calloc test_calloc
#define free test_free
#include "aac_sbr_reserve.c"
#undef calloc
#undef free
int main(void){
    aac_sbr_reserve_t a={0},b={0};
    aac_sbr_reserve_prepare(&a);aac_sbr_reserve_prepare(&b);assert(live==2);
    for(size_t i=0;i<55128;++i)assert(!((uint8_t*)a.pending)[i]);
    void *original=a.pending;unsigned before=calls;
    aac_sbr_reserve_enter(&a);
    // Another task's codec cannot consume this task's reserved memory.
    task=1;void *ordinary=__wrap_media_lib_module_calloc("test",1,55128);assert(ordinary!=original);test_free(ordinary);
    aac_sbr_reserve_enter(&b);void *p=__wrap_media_lib_module_calloc("test",1,55128);assert(p && !b.pending);aac_sbr_reserve_leave();test_free(p);
    task=0;p=__wrap_media_lib_module_calloc("test",1,55128);assert(p==original && !a.pending && calls==before+1);aac_sbr_reserve_leave();
    aac_sbr_reserve_discard(&a);aac_sbr_reserve_discard(&b);assert(live==1);test_free(p);assert(!live);
    // LC/early close releases an unclaimed owner. Repeated discard is safe.
    aac_sbr_reserve_prepare(&a);aac_sbr_reserve_discard(&a);aac_sbr_reserve_discard(&a);assert(!live);
    // Early OOM can recover when the real SBR request retries.
    failed=1;aac_sbr_reserve_prepare(&a);assert(!a.pending && !a.allocation_failed);
    aac_sbr_reserve_enter(&a);p=__wrap_media_lib_module_calloc("test",1,55128);assert(p && !a.allocation_failed);aac_sbr_reserve_leave();test_free(p);
    // Actual SBR/control failures are remembered for the adapter to reject PCM.
    for(unsigned i=0;i<2;++i){aac_sbr_reserve_enter(&a);failed=1;p=__wrap_media_lib_module_calloc("test",1,i?1180:55128);assert(!p && a.allocation_failed);aac_sbr_reserve_leave();}
    // An unrelated request is forwarded and cannot take the reserve.
    aac_sbr_reserve_prepare(&a);original=a.pending;aac_sbr_reserve_enter(&a);
    p=__wrap_media_lib_module_calloc("test",2,27564);assert(p && a.pending==original && !a.allocation_failed);
    aac_sbr_reserve_leave();test_free(p);aac_sbr_reserve_discard(&a);assert(!live);
    puts("AAC_SBR_RESERVE_PASS ownership, task isolation, zeroing, retry, failure and cleanup");
}
''')
    exe=tmp/'reserve-test'
    subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
                    '-fno-omit-frame-pointer','-I'+str(tmp),'-I'+str(MAIN),str(tmp/'test.c'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
