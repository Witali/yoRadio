// Laboratory-only probe: no settings writes and no change to flash mode.
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include "sdkconfig.h"
#include "esp_flash.h"
#include "esp_image_format.h"
#include "esp_ota_ops.h"
#include "esp_partition.h"
#include "esp_private/esp_clk.h"
#include "esp_rom_crc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "hal/spimem_flash_ll.h"
#include "soc/soc.h"
#include "soc/spi_mem_reg.h"

enum { kReadPasses = 4, kCaptureGraceMs = 8000, kExpectedFlashMHz = 80 };

void __real_app_main(void);

static bool probe(void)
{
    const uint32_t ctrl = REG_READ(SPI_MEM_CTRL_REG(0));
    const uint32_t clock = REG_READ(SPI_MEM_CLOCK_REG(0));
    const uint32_t mode_mask = SPI_MEM_FREAD_QIO | SPI_MEM_FREAD_DIO |
                               SPI_MEM_FREAD_QUAD | SPI_MEM_FREAD_DUAL;
#if CONFIG_ESPTOOLPY_FLASHMODE_QIO
    const uint32_t expected = SPI_MEM_FREAD_QIO;
    const char *mode = "qio";
#elif CONFIG_ESPTOOLPY_FLASHMODE_DIO
    const uint32_t expected = SPI_MEM_FREAD_DIO;
    const char *mode = "dio";
#else
#error "Probe supports matched DIO/QIO 80 MHz builds"
#endif
    const unsigned source_mhz = spimem_flash_ll_get_source_freq_mhz();
    const unsigned divider = (clock & SPI_MEM_CLK_EQU_SYSCLK) ? 1 :
        ((clock >> SPI_MEM_CLKCNT_N_S) & SPI_MEM_CLKCNT_N_V) + 1;
    uint32_t jedec = 0, size = 0;
    const esp_err_t id_result = esp_flash_read_id(NULL, &jedec);
    const esp_err_t size_result = esp_flash_get_physical_size(NULL, &size);
    printf("FLASH_PROBE_ENV expected=%s ctrl=0x%08" PRIx32
           " clock=0x%08" PRIx32 " source_mhz=%u divider=%u actual_mhz=%u"
           " cpu_hz=%d jedec=0x%06" PRIx32 " physical_bytes=%" PRIu32 "\n",
           mode, ctrl, clock, source_mhz, divider, source_mhz / divider,
           esp_clk_cpu_freq(), jedec, size);
    if (id_result != ESP_OK || size_result != ESP_OK ||
        (ctrl & mode_mask) != expected || source_mhz != kExpectedFlashMHz * divider ||
        size != 4U * 1024U * 1024U || esp_clk_cpu_freq() != 160000000) {
        return false;
    }
    const esp_partition_t *part = esp_ota_get_running_partition();
    if (!part) return false;
    const esp_partition_pos_t pos = {.offset = part->address, .size = part->size};
    esp_image_metadata_t meta = {0};
    if (esp_image_verify(ESP_IMAGE_VERIFY_SILENT, &pos, &meta) != ESP_OK) return false;
    const void *mapped = NULL;
    esp_partition_mmap_handle_t handle;
    if (esp_partition_mmap(part, 0, meta.image_len, ESP_PARTITION_MMAP_DATA,
                           &mapped, &handle) != ESP_OK) return false;
    bool equal = true;
    uint32_t first_crc = 0;
    for (unsigned pass = 1; pass <= kReadPasses; ++pass) {
        const uint32_t crc = esp_rom_crc32_le(0, mapped, meta.image_len);
        if (pass == 1) first_crc = crc;
        equal = equal && crc == first_crc;
        printf("FLASH_PROBE_READ pass=%u offset=0x%08" PRIx32
               " bytes=%" PRIu32 " crc32=0x%08" PRIx32 "\n",
               pass, part->address, meta.image_len, crc);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    esp_partition_munmap(handle);
    return equal; // Host also checks every CRC against the exact saved app.bin.
}

void __wrap_app_main(void)
{
    vTaskDelay(pdMS_TO_TICKS(kCaptureGraceMs));
    const bool ok = probe();
    printf("FLASH_PROBE_%s normal_app_follows=1\n", ok ? "PASS" : "FAIL");
    fflush(stdout);
    __real_app_main(); // Keep WebUI/recovery available even when a check fails.
}
