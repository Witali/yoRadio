#include <inttypes.h>
#include <stdio.h>
#include <stdatomic.h>
#include <string.h>

#include "audio_service.h"
#include "esp_heap_caps.h"
#include "esp_http_client.h"
#include "freertos/task.h"
#include "mbedtls/platform.h"

enum { PRESSURE_BLOCK_BYTES = 1024, PRESSURE_MAX_BLOCKS = 96, TLS_REQUEST_BYTES = 1536 };

static atomic_bool s_playing;

void cyd_openeth_note_playback(void) {
    atomic_store(&s_playing, true);
}

static void probe_input_reclaim(void) {
    static bool attempted;
    if (attempted) return;
    native_input_health_t before = audio_service_input_health();
    if (before.resident <= before.minimum ||
        before.ready + before.reading + before.writing >= before.resident) {
        return;
    }
    attempted = true;

    // Use the internal 8-bit heap that backs this SDK Mbed TLS profile.
    // Keep pressure local to one bounded allocation attempt and its retry.
    const uint32_t caps = MALLOC_CAP_8BIT | MALLOC_CAP_INTERNAL;
    void *blocks[PRESSURE_MAX_BLOCKS];
    unsigned held = 0;
    size_t largest = heap_caps_get_largest_free_block(caps);
    while (held < PRESSURE_MAX_BLOCKS && largest >= TLS_REQUEST_BYTES) {
        void *block = heap_caps_malloc(PRESSURE_BLOCK_BYTES, caps);
        if (!block) break;
        blocks[held++] = block;
        largest = heap_caps_get_largest_free_block(caps);
    }

    before = audio_service_input_health();
    void *recovered = largest < TLS_REQUEST_BYTES ? mbedtls_calloc(1, TLS_REQUEST_BYTES) : NULL;
    native_input_health_t after = audio_service_input_health();
    bool success = recovered != NULL;
    mbedtls_free(recovered);
    while (held) heap_caps_free(blocks[--held]);

    printf("CYD_OPENETH_RECLAIM request=%u largest=%zu recovered=%u "
           "resident_before=%" PRIu32 " resident_after=%" PRIu32
           " minimum=%" PRIu32 " budget=%" PRIu32 " released_before=%" PRIu32
           " released_after=%" PRIu32 " caps=%" PRIu32 "\n",
           (unsigned)TLS_REQUEST_BYTES, largest, (unsigned)success, before.resident, after.resident,
           before.minimum, before.target - before.minimum, before.released, after.released, caps);
}

int __real_esp_http_client_read(esp_http_client_handle_t, char *, int);
int __wrap_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int bytes) {
    // The stream task is the sole input producer. It cannot consume the idle
    // slot between the measurement and the allocation while in this hook.
    if (atomic_load(&s_playing) && !strcmp(pcTaskGetName(NULL), "radio_stream"))
        probe_input_reclaim();
    return __real_esp_http_client_read(client, buffer, bytes);
}
