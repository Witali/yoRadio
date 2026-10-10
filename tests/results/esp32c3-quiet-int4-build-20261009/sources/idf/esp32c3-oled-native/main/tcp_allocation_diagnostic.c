#include <inttypes.h>
#include "esp_log.h"
#include "lwip/memp.h"
#include "lwip/tcp.h"

void *__real_memp_malloc(memp_t type);
void __real_memp_free(memp_t type, void *p);
void *__wrap_memp_malloc(memp_t type) {
    void *p = __real_memp_malloc(type);
    if (type == MEMP_TCP_PCB)
        ESP_LOGI("tcp_layout", "PERF TCP_ALLOC: address=0x%08" PRIxPTR " bytes=%u",
                 (uintptr_t)p, (unsigned)sizeof(struct tcp_pcb));
    return p;
}
void __wrap_memp_free(memp_t type, void *p) {
    if (type == MEMP_TCP_PCB && p)
        ESP_LOGI("tcp_layout", "PERF TCP_FREE: address=0x%08" PRIxPTR " state=%u",
                 (uintptr_t)p, (unsigned)((struct tcp_pcb *)p)->state);
    __real_memp_free(type, p);
}
