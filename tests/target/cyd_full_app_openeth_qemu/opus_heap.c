#include <stdio.h>

#include "esp_heap_caps.h"
#include "esp_opus_dec.h"

esp_audio_err_t __real_esp_opus_dec_open(void *cfg, uint32_t cfg_size, void **handle);

esp_audio_err_t __wrap_esp_opus_dec_open(void *cfg, uint32_t cfg_size, void **handle)
{
    const uint32_t caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_DEFAULT;
    multi_heap_info_t before;
    multi_heap_info_t after;
    heap_caps_get_info(&before, caps);
    esp_audio_err_t result = __real_esp_opus_dec_open(cfg, cfg_size, handle);
    heap_caps_get_info(&after, caps);
    unsigned channels = cfg && cfg_size >= sizeof(esp_opus_dec_cfg_t)
        ? ((const esp_opus_dec_cfg_t *)cfg)->channel : 0;
    printf("CYD_OPENETH_OPUS_OPEN channels=%u result=%d free=%zu largest=%zu "
           "remaining=%zu remaining_largest=%zu\n",
           channels, (int)result, before.total_free_bytes, before.largest_free_block,
           after.total_free_bytes, after.largest_free_block);
    return result;
}
