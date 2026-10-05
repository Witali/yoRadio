// Test-only entry point. The linked Ogg/Vorbis decoder objects are unmodified.
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_audio_simple_dec.h"
#include "simple_dec/impl/esp_ogg_dec.h"
#include "esp_vorbis_dec.h"
#include "esp_heap_caps.h"
#include "esp_partition.h"
#include "esp_rom_sys.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "psa/crypto.h"
#ifdef CONFIG_YORADIO_VORBIS_REPAIR
#include "decoder_registration.h"
#include "decoder_resources.h"
// This isolated image never constructs an AAC handle.
void native_aac_decoder_destroy(native_aac_decoder_t *decoder) { assert(!decoder); }
#endif

enum { COMMAND_MAGIC = 0x564c4631, COMMAND_VERSION = 1,
       OWNER_SLOTS = 1024, INPUT_BYTES = 2048, PCM_BYTES = 16384,
       TEST_STACK_BYTES = 16384, MAX_DECODE_CALLS = 20000 };
enum { TEST_STREAM, TEST_HEADER, TEST_REGISTRATION, TEST_SERVICE, TEST_OUTPUT };
typedef enum { PH_REGISTER, PH_OPEN, PH_HEADERS, PH_DECODE, PH_CLOSE } phase_t;
typedef struct {
    uint32_t magic, version, direct, fail_at, cycles, ogg_bytes, info_bytes, setup_bytes;
} command_t;
_Static_assert(sizeof(command_t) == 32, "Host command format");
typedef struct {
    void *pointer;
    size_t requested, actual;
    uint32_t id, run;
} owner_t;
static owner_t owners[OWNER_SLOTS];
static unsigned run_id, attempt, next_id, failure_target, injected, bad_owners;
static size_t live_requested, live_actual, peak_requested, peak_actual;
static size_t min_free, min_largest;
static phase_t phase;
static bool trace;
static uint8_t input[INPUT_BYTES], pcm[PCM_BYTES];
static const uint8_t *fixture, *info_header, *setup_header;
static command_t command;
typedef struct {
    uint32_t initial_bytes, rejected_retries, eos_calls, resize_oom, each_packet, input_bytes;
} output_command_t;
static output_command_t output_command;
static unsigned synthesis_calls;
extern int __real_vorbis_dsp_synthesis(void *, void *, int);
int __wrap_vorbis_dsp_synthesis(void *dsp, void *packet, int decode) {
    ++synthesis_calls;
    return __real_vorbis_dsp_synthesis(dsp, packet, decode);
}

static unsigned find_owner(const void *p) {
    for (unsigned i = 0; i < OWNER_SLOTS; ++i)
        if (p && owners[i].pointer == p) return i;
    return OWNER_SLOTS;
}
static void memory_minimum(void) {
    size_t free_bytes = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    size_t largest = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    if (free_bytes < min_free) min_free = free_bytes;
    if (largest < min_largest) min_largest = largest;
}
static void forget(unsigned i) {
    if (i == OWNER_SLOTS) return;
    if (owners[i].run) {
        live_requested -= owners[i].requested;
        live_actual -= owners[i].actual;
    }
    owners[i] = (owner_t){0};
}
static void remember(void *p, size_t requested, unsigned caller, const char *kind,
                     const void *old) {
    size_t actual = p ? heap_caps_get_allocated_size(p) : 0;
    unsigned id = 0;
    if (p) {
        assert(find_owner(p) == OWNER_SLOTS);
        unsigned i;
        for (i = 0; i < OWNER_SLOTS && owners[i].pointer; ++i) {}
        if (i == OWNER_SLOTS) {
            esp_rom_printf("VTEST_HARNESS_ERROR ledger_overflow=1\n");
            abort();
        }
        id = ++next_id;
        owners[i] = (owner_t){p, requested, actual, id, run_id};
        if (run_id) {
            live_requested += requested;
            live_actual += actual;
            if (live_requested > peak_requested) peak_requested = live_requested;
            if (live_actual > peak_actual) peak_actual = live_actual;
        }
    }
    memory_minimum();
    if (trace || !p)
        esp_rom_printf("VTEST_ALLOC run=%u attempt=%u phase=%u kind=%s id=%u ptr=%08x old=%08x requested=%u actual=%u caller=%08x\n",
            run_id, attempt, phase, kind, id, (unsigned)p, (unsigned)old,
            (unsigned)requested, (unsigned)actual, caller);
}
static bool fail_request(size_t bytes, unsigned caller, const char *kind) {
    ++attempt;
    if ((run_id || command.direct == TEST_REGISTRATION || command.direct == TEST_SERVICE) &&
        failure_target && attempt == failure_target) {
        ++injected;
        esp_rom_printf("VTEST_INJECT run=%u attempt=%u phase=%u kind=%s bytes=%u caller=%08x\n",
                       run_id, attempt, phase, kind, (unsigned)bytes, caller);
        return true;
    }
    return false;
}

// Strong test-only definitions replace the library's weak libc shims.
// ROM printf does not allocate through these shims and preserves events before
// an original decoder crash. No system allocator, DSP or error path is patched.
void *media_lib_module_malloc(const char *module, size_t size) {
    (void)module;
    unsigned caller = (unsigned)__builtin_return_address(0);
    void *p = fail_request(size, caller, "malloc") ? NULL : malloc(size);
    remember(p, size, caller, "malloc", NULL);
    return p;
}
void *media_lib_module_calloc(const char *module, size_t n, size_t size) {
    (void)module;
    unsigned caller = (unsigned)__builtin_return_address(0);
    assert(!size || n <= SIZE_MAX / size);
    void *p = fail_request(n * size, caller, "calloc") ? NULL : calloc(n, size);
    remember(p, n * size, caller, "calloc", NULL);
    return p;
}
void *media_lib_module_realloc(const char *module, void *p, size_t size) {
    (void)module;
    unsigned caller = (unsigned)__builtin_return_address(0);
    uintptr_t old_address = (uintptr_t)p;
    unsigned i = find_owner(p);
    if (p && i == OWNER_SLOTS) {
        ++bad_owners;
        esp_rom_printf("VTEST_BAD_OWNER run=%u op=realloc ptr=%08x caller=%08x\n",
                       run_id, (unsigned)p, caller);
    }
    bool fail = fail_request(size, caller, "realloc");
    void *next = fail ? NULL : realloc(p, size);
    // A failed nonzero realloc retains both the old pointer and its ledger row.
    if (next || (!size && !fail)) forget(i);
    remember(next, size, caller, "realloc", (void *)old_address);
    return next;
}
void media_lib_free(void *p) {
    unsigned i = find_owner(p);
    unsigned caller = (unsigned)__builtin_return_address(0);
    if (p && i == OWNER_SLOTS) {
        ++bad_owners;
        esp_rom_printf("VTEST_BAD_OWNER run=%u op=free ptr=%08x caller=%08x\n",
                       run_id, (unsigned)p, caller);
    }
    if (trace && p)
        esp_rom_printf("VTEST_FREE run=%u id=%u ptr=%08x caller=%08x\n", run_id,
                       i == OWNER_SLOTS ? 0 : owners[i].id, (unsigned)p, caller);
    forget(i);
    free(p); // Preserve the original failure, including an invalid/double free.
}

static unsigned stream_owners(void) {
    unsigned count = 0;
    for (unsigned i = 0; i < OWNER_SLOTS; ++i) count += owners[i].pointer && owners[i].run;
    return count;
}
#include "qemu_vorbis_output.inc"
static int decode_stream(psa_hash_operation_t *hash, uint32_t *pcm_bytes) {
    phase = PH_OPEN;
    esp_audio_simple_dec_handle_t decoder = NULL;
    esp_audio_simple_dec_cfg_t cfg = {
        .dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_OGG, .use_frame_dec = false,
    };
    int result = esp_audio_simple_dec_open(&cfg, &decoder);
    unsigned calls = 0;
    bool layout = false;
    if (result == ESP_AUDIO_ERR_OK) {
        for (size_t pos = 0; pos <= command.ogg_bytes;) {
            size_t size = command.ogg_bytes - pos;
            if (size > sizeof(input)) size = sizeof(input);
            memcpy(input, fixture + pos, size);
            bool eos = !size;
            esp_audio_simple_dec_raw_t raw = {.buffer = input, .len = size, .eos = eos};
            do {
                phase = layout ? PH_DECODE : PH_HEADERS;
                esp_audio_simple_dec_out_t out = {.buffer = pcm, .len = sizeof(pcm)};
                raw.consumed = 0;
                result = esp_audio_simple_dec_process(decoder, &raw, &out);
                memory_minimum();
                if (++calls > MAX_DECODE_CALLS || raw.consumed > raw.len || out.decoded_size > sizeof(pcm)) {
                    esp_rom_printf("VTEST_HARNESS_ERROR invalid_progress=1\n");
                    abort();
                }
                if (result != ESP_AUDIO_ERR_OK) goto closed;
                if (out.decoded_size) {
                    esp_audio_simple_dec_info_t latest = {0};
                    assert(esp_audio_simple_dec_get_info(decoder, &latest) == ESP_AUDIO_ERR_OK);
                    assert(latest.sample_rate == 48000 && latest.channel == 2 && latest.bits_per_sample == 16);
                    layout = true;
                    assert(psa_hash_update(hash, pcm, out.decoded_size) == PSA_SUCCESS);
                    *pcm_bytes += out.decoded_size;
                }
                if (!raw.consumed && !out.decoded_size && !eos) {
                    result = -100; // Harness-observed no progress, not vendor error.
                    goto closed;
                }
                raw.buffer += raw.consumed;
                raw.len -= raw.consumed;
                if (eos) break; // Match the current C3 single EOS call.
            } while (raw.len);
            if (eos) break;
            pos += size;
            if ((calls & 31U) == 0) vTaskDelay(1);
        }
    }
closed:
    esp_rom_printf("VTEST_DECODE run=%u result=%d calls=%u pcm=%u\n", run_id, result, calls, *pcm_bytes);
    phase = PH_CLOSE;
#ifdef CONFIG_YORADIO_VORBIS_REPAIR
    native_aac_decoder_t *aac = NULL;
    uint8_t *workspace = NULL;
    size_t capacity = 0;
    decoder_resources_release(&decoder, &aac, &workspace, &capacity);
#else
    if (decoder) esp_audio_simple_dec_close(decoder);
#endif
    return result;
}

static void cycle(bool direct) {
    ++run_id;
    attempt = injected = 0;
    peak_requested = live_requested;
    peak_actual = live_actual;
    min_free = min_largest = SIZE_MAX;
    uint32_t pcm_bytes = 0;
    psa_hash_operation_t hash = PSA_HASH_OPERATION_INIT;
    assert(psa_hash_setup(&hash, PSA_ALG_SHA_256) == PSA_SUCCESS);
    size_t before_free = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    size_t before_largest = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    esp_rom_printf("VTEST_BEGIN run=%u direct=%u fail_at=%u free=%u largest=%u\n",
        run_id, direct, failure_target, (unsigned)before_free, (unsigned)before_largest);
    int result;
    if (direct) {
        phase = PH_OPEN;
        esp_vorbis_dec_cfg_t cfg = {
            .info_header = (uint8_t *)info_header, .info_size = command.info_bytes,
            .setup_header = (uint8_t *)setup_header, .setup_size = command.setup_bytes,
        };
        void *decoder = NULL;
        result = esp_vorbis_dec_open(&cfg, sizeof(cfg), &decoder);
        esp_rom_printf("VTEST_DIRECT run=%u result=%d handle=%08x\n", run_id, result, (unsigned)decoder);
        phase = PH_CLOSE;
        if (decoder) esp_vorbis_dec_close(decoder);
    } else if (command.direct == TEST_OUTPUT) result = decode_output(&hash, &pcm_bytes);
    else result = decode_stream(&hash, &pcm_bytes);
    bool integrity = heap_caps_check_integrity_all(true);
    size_t after_free = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    size_t after_largest = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    uint8_t digest[32]; size_t length = 0;
    assert(psa_hash_finish(&hash, digest, sizeof(digest), &length) == PSA_SUCCESS && length == 32);
    char hex[65];
    for (unsigned i = 0; i < 32; ++i) sprintf(hex + i * 2, "%02x", digest[i]);
    esp_rom_printf("VTEST_RESULT run=%u result=%d attempts=%u injected=%u live=%u requested=%u actual=%u peak_requested=%u peak_actual=%u min_free=%u min_largest=%u free=%u largest=%u integrity=%u bad_owners=%u stack_free=%u pcm=%u samples=%u sha256=%s\n",
        run_id, result, attempt, injected, stream_owners(), (unsigned)live_requested,
        (unsigned)live_actual, (unsigned)peak_requested, (unsigned)peak_actual,
        (unsigned)min_free, (unsigned)min_largest, (unsigned)after_free,
        (unsigned)after_largest, integrity, bad_owners,
        (unsigned)uxTaskGetStackHighWaterMark(NULL), pcm_bytes, pcm_bytes / 2U, hex);
    for (unsigned i = 0; i < OWNER_SLOTS; ++i) {
        owner_t *o = &owners[i];
        if (o->pointer && o->run)
            esp_rom_printf("VTEST_RETAINED run=%u owner_run=%u id=%u ptr=%08x requested=%u actual=%u\n",
                run_id, o->run, o->id, (unsigned)o->pointer, (unsigned)o->requested, (unsigned)o->actual);
    }
}

static void test_task(void *unused) {
    (void)unused;
    // Let app_main return and the idle task reclaim its stack before measuring
    // the first decoder. Otherwise that unrelated free changes the baseline.
    vTaskDelay(pdMS_TO_TICKS(20));
    const esp_partition_t *part = esp_partition_find_first(
        ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_APP_OTA_1, NULL);
    assert(part && esp_partition_read(part, 0, &command, sizeof(command)) == ESP_OK);
    assert(command.magic == COMMAND_MAGIC && (command.version == COMMAND_VERSION || command.version == 2));
    assert(command.cycles && command.cycles <= 1000 && command.direct <= TEST_OUTPUT);
    size_t header_bytes = sizeof(command);
    if (command.version == 2) {
        assert(command.direct == TEST_OUTPUT && !command.fail_at);
        assert(esp_partition_read(part, header_bytes, &output_command, sizeof(output_command)) == ESP_OK);
        header_bytes += sizeof(output_command);
        assert(output_command.initial_bytes && output_command.initial_bytes <= PCM_BYTES);
        assert(output_command.eos_calls && output_command.eos_calls <= 16);
        assert(output_command.rejected_retries <= 8 && output_command.resize_oom <= 1);
        assert(output_command.input_bytes && output_command.input_bytes <= INPUT_BYTES);
    }
    size_t bytes = command.ogg_bytes + command.info_bytes + command.setup_bytes;
    assert(bytes < part->size - header_bytes);
    const void *mapped; esp_partition_mmap_handle_t mapping;
    assert(esp_partition_mmap(part, 0, bytes + header_bytes, ESP_PARTITION_MMAP_DATA,
                              &mapped, &mapping) == ESP_OK);
    fixture = (const uint8_t *)mapped + header_bytes;
    info_header = fixture + command.ogg_bytes;
    setup_header = info_header + command.info_bytes;
    assert(psa_crypto_init() == PSA_SUCCESS);
    phase = PH_REGISTER; trace = true;
#ifdef CONFIG_YORADIO_VORBIS_REPAIR
    if (command.direct == TEST_REGISTRATION) {
        size_t before = heap_caps_get_free_size(MALLOC_CAP_8BIT);
        size_t largest = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
        failure_target = command.fail_at;
        int result = decoder_register_codecs();
        unsigned remaining = 0;
        for (unsigned i = 0; i < OWNER_SLOTS; ++i) remaining += owners[i].pointer != NULL;
        esp_rom_printf("VTEST_REGISTRATION result=%d injected=%u live=%u free_before=%u free_after=%u largest_before=%u largest_after=%u integrity=%u\n",
            result, injected, remaining, (unsigned)before,
            (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT), (unsigned)largest,
            (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),
            heap_caps_check_integrity_all(true));
        failure_target = 0;
        attempt = injected = 0;
    }
    assert(decoder_register_codecs() == ESP_AUDIO_ERR_OK);
#else
    assert(command.direct <= TEST_HEADER);
    assert(esp_vorbis_dec_register() == ESP_AUDIO_ERR_OK);
    assert(esp_ogg_dec_register() == ESP_AUDIO_ERR_OK);
#endif
    unsigned registration_count = 0; size_t registration_bytes = 0;
    for (unsigned i = 0; i < OWNER_SLOTS; ++i) if (owners[i].pointer) {
        ++registration_count; registration_bytes += owners[i].actual;
    }
    esp_rom_printf("VTEST_REGISTER count=%u actual=%u attempts=%u ledger_bytes=%u pcm_workspace=%u\n",
        registration_count, (unsigned)registration_bytes, attempt,
        (unsigned)sizeof(owners), (unsigned)sizeof(pcm));
    failure_target = command.fail_at;
#ifdef CONFIG_YORADIO_VORBIS_REPAIR
    if (command.direct == TEST_SERVICE) {
        size_t before = heap_caps_get_free_size(MALLOC_CAP_8BIT);
        size_t largest = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
        size_t capacity = 12288; // Ordinary service's initial non-AAC workspace.
        uint8_t *workspace = malloc(capacity);
        assert(workspace);
        esp_audio_simple_dec_handle_t decoder = NULL;
        native_aac_decoder_t *aac = NULL;
        esp_audio_simple_dec_cfg_t cfg = {.dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_OGG};
        attempt = injected = 0;
        phase = PH_OPEN;
        int result = esp_audio_simple_dec_open(&cfg, &decoder);
        bool null_handle = !decoder;
        decoder_resources_release(&decoder, &aac, &workspace, &capacity);
        decoder_resources_release(&decoder, &aac, &workspace, &capacity); // Stop after failed open.
        esp_rom_printf("VTEST_SERVICE result=%d injected=%u null_handle=%u released=%u free_before=%u free_after=%u largest_before=%u largest_after=%u integrity=%u\n",
            result, injected, null_handle, !decoder && !aac && !workspace && !capacity,
            (unsigned)before, (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT),
            (unsigned)largest, (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),
            heap_caps_check_integrity_all(true));
    }
    if (command.direct == TEST_REGISTRATION || command.direct == TEST_SERVICE) {
        failure_target = 0;
        esp_rom_printf("VTEST_RECOVERY_BEGIN\n");
    }
#endif
    for (unsigned i = 0; i < command.cycles; ++i) {
        trace = i == 0;
        cycle(command.direct == TEST_HEADER);
        vTaskDelay(1);
    }
    if (command.direct <= TEST_HEADER && (command.fail_at || command.direct)) {
        failure_target = 0;
        trace = true;
        esp_rom_printf("VTEST_RECOVERY_BEGIN\n");
        cycle(false);
    }
    esp_rom_printf("VTEST_COMPLETE runs=%u\n", run_id);
    esp_partition_munmap(mapping);
    vTaskDelay(pdMS_TO_TICKS(20));
    esp_restart();
}

void app_main(void) {
#ifdef CONFIG_YORADIO_VORBIS_REPAIR
    esp_rom_printf("VTEST_BOOT original_decoder=0 network=0\n");
#else
    esp_rom_printf("VTEST_BOOT original_decoder=1 network=0\n");
#endif
    assert(xTaskCreate(test_task, "vorbis_test", TEST_STACK_BYTES, NULL, 3, NULL) == pdPASS);
}
