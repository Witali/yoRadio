// Opt-in bench image only. No Wi-Fi, NVS writes, audio output or sleep modes.
// The exact same application binary also runs in our QEMU fork with icount.
#include <assert.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_attr.h"
#include "esp_cpu.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_private/esp_clk.h"
#include "esp_rom_caps.h"
#include "esp_rom_serial_output.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp32c3/rom/cache.h"
#include "esp_aac_dec.h"
#include "esp_audio_codec_version.h"
#include "esp_audio_simple_dec_default.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_aac_decoder.h"
#include "riscv/rv_utils.h"
#include "soc/extmem_reg.h"
#include "soc/soc.h"
#ifdef YORADIO_HARDWARE_FLASH_TEST
#include "esp_flash.h"
#include "esp_image_format.h"
#include "esp_ota_ops.h"
#include "esp_partition.h"
#include "esp_rom_crc.h"
#include "hal/spimem_flash_ll.h"
#include "soc/spi_mem_reg.h"
#endif

#if defined(CONFIG_YORADIO_DEEP_SLEEP_CLOCK) || !defined(CONFIG_YORADIO_AAC_PLUS)
#error "Cache bench requires full AAC Plus and deep sleep disabled"
#endif

#define FIXTURE(name, symbol) \
    extern const uint8_t name##_start[] asm("_binary_" symbol "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" symbol "_aac_end")
FIXTURE(lc48, "lc_48000_stereo");
FIXTURE(he48, "he_48000_stereo");
FIXTURE(hev2, "hev2_44100_stereo");
static bool s_emulated;
static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
static const uint32_t s_probe[2048] __attribute__((aligned(32))) = {0x12345678};
static volatile uint32_t s_sink;

static int report_v(const char *format, va_list args) {
    char line[768];
    int length = vsnprintf(line, sizeof(line), format, args);
    assert(length >= 0 && length < sizeof(line));
    for (int i = 0; i < length; ++i) esp_rom_output_tx_one_char(line[i]);
    return length;
}
static void report(const char *format, ...) {
    va_list args;
    va_start(args, format);
    report_v(format, args);
    va_end(args);
}

typedef struct {
    uint32_t ticks, us, ibus_access, ibus_miss_raw, dbus_access, dbus_miss_raw;
} measurement_t;

// Executed wholly from internal RAM, with IRQs masked by the caller. ROM cache
// disable invalidates tags; re-enable restores the prior autoload setting.
static void IRAM_ATTR __attribute__((noinline)) cold_cache(void) {
    uint32_t autoload = Cache_Disable_ICache();
    Cache_Enable_ICache(autoload);
}

static inline __attribute__((always_inline)) uint32_t ticks(void) {
    if (s_emulated) {
        uint32_t count;
        __asm__ volatile("csrr %0, minstret" : "=r"(count) :: "memory");
        return count;
    }
    return esp_cpu_get_cycle_count();
}

static inline __attribute__((always_inline)) void counters_clear(void) {
    REG_WRITE(EXTMEM_CACHE_ACS_CNT_CLR_REG,
              EXTMEM_IBUS_ACS_CNT_CLR | EXTMEM_DBUS_ACS_CNT_CLR);
    __asm__ volatile("fence iorw, iorw" ::: "memory");
}
static inline __attribute__((always_inline)) void counters_read(measurement_t *m) {
    m->ibus_access = REG_READ(EXTMEM_IBUS_ACS_CNT_REG);
    m->ibus_miss_raw = REG_READ(EXTMEM_IBUS_ACS_MISS_CNT_REG);
    m->dbus_access = REG_READ(EXTMEM_DBUS_ACS_CNT_REG);
    m->dbus_miss_raw = REG_READ(EXTMEM_DBUS_ACS_FLASH_MISS_CNT_REG);
}

static esp_audio_err_t IRAM_ATTR __attribute__((noinline)) measure_decode(native_aac_decoder_t *decoder,
                 esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *out,
                 bool cold, measurement_t *m) {
    taskENTER_CRITICAL(&s_lock);
    if (cold && !s_emulated) cold_cache();
    counters_clear();
    int64_t before_us = esp_timer_get_time();
    uint32_t before = ticks();
    esp_audio_err_t result = native_aac_decoder_process(decoder, raw, out);
    m->ticks = ticks() - before;
    m->us = (uint32_t)(esp_timer_get_time() - before_us);
    counters_read(m);
    taskEXIT_CRITICAL(&s_lock);
    return result;
}

static measurement_t IRAM_ATTR __attribute__((noinline)) probe(unsigned lines, bool cold) {
    measurement_t m;
    volatile const uint32_t *data = s_probe;
    taskENTER_CRITICAL(&s_lock);
    if (cold && !s_emulated) cold_cache();
    counters_clear();
    uint32_t sum = 0;
    int64_t before_us = esp_timer_get_time();
    uint32_t before = ticks();
    for (unsigned line = 0; line < lines; ++line) sum += data[line * 8];
    m.ticks = ticks() - before;
    m.us = (uint32_t)(esp_timer_get_time() - before_us);
    counters_read(&m);
    s_sink = sum;
    taskEXIT_CRITICAL(&s_lock);
    return m;
}

static void cache_probes(void) {
    const unsigned sizes[] = {1, 8, 64, 256};
    for (unsigned i = 0; i < sizeof(sizes) / sizeof(sizes[0]); ++i) {
        unsigned lines = sizes[i];
        for (unsigned run = 1; run <= 8; ++run) {
            measurement_t cold = probe(lines, true);
            measurement_t warm = probe(lines, false);
            report("CACHE_PROBE lines=%u run=%u cold_ticks=%u warm_ticks=%u "
                   "cold_i=%u warm_i=%u cold_d=%u warm_d=%u cold_da=%u warm_da=%u\n",
                   lines, run, cold.ticks, warm.ticks, cold.ibus_miss_raw, warm.ibus_miss_raw,
                   cold.dbus_miss_raw, warm.dbus_miss_raw, cold.dbus_access, warm.dbus_access);
        }
    }
}

#ifdef YORADIO_HARDWARE_FLASH_TEST
// Read the cache controller, not just the requested sdkconfig or image header.
// This diagnostic is specific to C3 at its normal PLL/CPU configuration.
static void flash_check(void) {
    assert(!s_emulated);
    uint32_t ctrl = REG_READ(SPI_MEM_CTRL_REG(0));
    uint32_t clock = REG_READ(SPI_MEM_CLOCK_REG(0));
    const uint32_t mode_mask = SPI_MEM_FREAD_QIO | SPI_MEM_FREAD_DIO |
                               SPI_MEM_FREAD_QUAD | SPI_MEM_FREAD_DUAL;
#if CONFIG_ESPTOOLPY_FLASHMODE_QIO
    const uint32_t expected_mode = SPI_MEM_FREAD_QIO;
#elif CONFIG_ESPTOOLPY_FLASHMODE_DIO
    const uint32_t expected_mode = SPI_MEM_FREAD_DIO;
#else
#error "Flash comparison supports only DIO and QIO"
#endif
    unsigned source_mhz = spimem_flash_ll_get_source_freq_mhz();
    unsigned divider = (clock & SPI_MEM_CLK_EQU_SYSCLK) ? 1 :
        ((clock >> SPI_MEM_CLKCNT_N_S) & SPI_MEM_CLKCNT_N_V) + 1;
    unsigned mhz = source_mhz / divider;
    uint32_t id, size;
    ESP_ERROR_CHECK(esp_flash_read_id(NULL, &id));
    ESP_ERROR_CHECK(esp_flash_get_physical_size(NULL, &size));
    report("FLASH_ENV configured=%s configured_mhz=%s ctrl=0x%08" PRIx32
           " clock=0x%08" PRIx32 " source_mhz=%u divider=%u actual_mhz=%u"
           " jedec=0x%06" PRIx32 " physical_bytes=%" PRIu32 "\n",
           CONFIG_ESPTOOLPY_FLASHMODE, CONFIG_ESPTOOLPY_FLASHFREQ,
           ctrl, clock, source_mhz, divider, mhz, id, size);
    assert((ctrl & mode_mask) == expected_mode);
    assert(mhz == (unsigned)atoi(CONFIG_ESPTOOLPY_FLASHFREQ));

    const esp_partition_t *part = esp_ota_get_running_partition();
    assert(part);
    esp_partition_pos_t pos = {.offset = part->address, .size = part->size};
    esp_image_metadata_t meta = {0};
    ESP_ERROR_CHECK(esp_image_verify(ESP_IMAGE_VERIFY_SILENT, &pos, &meta));
    const void *mapped;
    esp_partition_mmap_handle_t handle;
    ESP_ERROR_CHECK(esp_partition_mmap(part, 0, meta.image_len,
                                    ESP_PARTITION_MMAP_DATA, &mapped, &handle));
    uint32_t previous = 0;
    for (unsigned pass = 1; pass <= 16; ++pass) {
        taskENTER_CRITICAL(&s_lock);
        cold_cache();
        taskEXIT_CRITICAL(&s_lock);
        // ROM CRC reads through SPI0/cache over an image larger than the cache.
        // Host validation also compares every CRC with the saved app.bin bytes.
        uint32_t crc = esp_rom_crc32_le(0, mapped, meta.image_len);
        report("FLASH_READ pass=%u offset=0x%08" PRIx32 " bytes=%" PRIu32
               " crc32=0x%08" PRIx32 "\n", pass, part->address, meta.image_len, crc);
        assert(pass == 1 || crc == previous);
        previous = crc;
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    esp_partition_munmap(handle);
}
#endif

static void profile(const char *name, const uint8_t *start, const uint8_t *end,
                    unsigned rate, unsigned expected_samples, unsigned round, bool cold) {
    uint8_t *input = malloc(2048), *pcm = malloc(16384);
    native_aac_decoder_t *decoder = native_aac_decoder_create();
    assert(input && pcm && decoder);
    // One warm-up to allocate and initialize all decoder state, then three
    // measured passes. Input/PCM, allocation, checks and logs are outside timing.
    for (unsigned pass = 0; pass <= 3; ++pass) {
        uint64_t work = 0, us = 0, ia = 0, im = 0, da = 0, dm = 0;
        unsigned samples = 0, frames = 0, calls = 0, max_us = 0;
        for (const uint8_t *p = start; p < end;) {
            size_t size = end - p;
            if (size > 2048) size = 2048;
            memcpy(input, p, size);
            esp_audio_simple_dec_raw_t raw = {.buffer = input, .len = size};
            while (raw.len) {
                esp_audio_simple_dec_out_t out = {.buffer = pcm, .len = 16384};
                measurement_t m;
                esp_audio_err_t result = measure_decode(decoder, &raw, &out, cold && pass, &m);
                assert(result == ESP_AUDIO_ERR_OK);
                assert(raw.consumed <= raw.len && (raw.consumed || out.decoded_size));
                raw.buffer += raw.consumed;
                raw.len -= raw.consumed;
                work += m.ticks; us += m.us;
                ia += m.ibus_access; im += m.ibus_miss_raw;
                da += m.dbus_access; dm += m.dbus_miss_raw;
                if (m.us > max_us) max_us = m.us;
                ++calls;
                if (out.decoded_size) {
                    esp_audio_simple_dec_info_t info;
                    assert(native_aac_decoder_get_info(decoder, &info) == ESP_AUDIO_ERR_OK);
                    assert(info.sample_rate == rate && info.channel == 2 && info.bits_per_sample == 16);
                    assert(out.decoded_size % 4 == 0);
                    samples += out.decoded_size / 4;
                    ++frames;
                }
            }
            p += size;
        }
        assert(samples == expected_samples);
        assert(heap_caps_check_integrity_all(true));
        if (pass) report("CACHE_DECODE case=%s round=%u mode=%s pass=%u ticks=%" PRIu64
            " us=%" PRIu64 " ia=%" PRIu64 " im_raw=%" PRIu64 " da=%" PRIu64 " dm_raw=%" PRIu64
            " samples=%u rate=%u channels=2 frames=%u calls=%u max_us=%u stack_free=%u\n",
            name, round, cold ? "cold" : "continuous", pass, work, us, ia, im, da, dm,
            samples, rate, frames, calls, max_us, (unsigned)uxTaskGetStackHighWaterMark(NULL));
        vTaskDelay(pdMS_TO_TICKS(20));
    }
    native_aac_decoder_destroy(decoder);
    free(input); free(pcm);
    assert(heap_caps_check_integrity_all(true));
}

static void bench_task(void *unused) {
    (void)unused;
    // QEMU's ESP-specific CSR implementation returns zero for PCER. Physical
    // IDF startup selects cycle event 1. Validate it instead of guessing from
    // zero cache counters. This is specific to the recorded QEMU fork/version.
    uint32_t pcer = RV_READ_CSR(CSR_PCER_MACHINE);
    s_emulated = pcer == 0;
    if (!s_emulated) esp_rom_output_set_as_console(ESP_ROM_USB_SERIAL_DEVICE_NUM);
    esp_log_set_vprintf(report_v);
    vTaskDelay(pdMS_TO_TICKS(8000)); // Let the host attach its passive USB reader.
    report("CACHE_HW_ENV target=esp32c3 runtime=%s cpu_hz=%d pcer=%u codec_version=%s "
           "deep_sleep=0 irq_masked=1 flash_mode=%s flash_mhz=%u\n",
           s_emulated ? "qemu" : "hardware", esp_clk_cpu_freq(), pcer,
           esp_audio_codec_get_version(), CONFIG_ESPTOOLPY_FLASHMODE,
           (unsigned)atoi(CONFIG_ESPTOOLPY_FLASHFREQ));
    assert(s_emulated || pcer == 1);
    assert(esp_clk_cpu_freq() == 160000000);
#ifdef YORADIO_HARDWARE_FLASH_TEST
    flash_check();
#endif
    if (s_emulated) {
        uint32_t before, after;
        __asm__ volatile("csrr %0, minstret\n.rept 1024\nnop\n.endr\ncsrr %1, minstret"
                         : "=r"(before), "=r"(after) :: "memory");
        report("CACHE_ICOUNT_PROBE nops=1024 instructions=%u\n", after - before);
        assert(after - before == 1025);
    }
    cache_probes();
    assert(esp_aac_dec_register() == ESP_AUDIO_ERR_OK);
    assert(esp_audio_simple_dec_register_default() == ESP_AUDIO_ERR_OK);
    for (unsigned round = 1; round <= 4; ++round) {
        // Alternate mode order to expose systematic drift.
        for (unsigned order = 0; order < 2; ++order) {
            bool cold = (round + order) % 2 == 0;
            profile("lc48000_stereo", lc48_start, lc48_end, 48000, 26624, round, cold);
            profile("he48000_stereo", he48_start, he48_end, 48000, 30720, round, cold);
            profile("hev2_44100_stereo", hev2_start, hev2_end, 44100, 30720, round, cold);
        }
    }
    report("CACHE_HW_PASS runtime=%s\n", s_emulated ? "qemu" : "hardware");
    if (s_emulated) { vTaskDelay(10); esp_restart(); }
    vTaskDelete(NULL);
}

void app_main(void) {
    assert(xTaskCreate(bench_task, "cache_bench", 20480, NULL, 3, NULL) == pdPASS);
}
