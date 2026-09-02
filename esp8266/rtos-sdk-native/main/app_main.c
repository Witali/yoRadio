#include "esp_log.h"
#include "esp_system.h"
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "board_config.h"
#include "spi_pdm_config.h"
#include "audio_service.h"
#if CONFIG_YORADIO_OLED
#include "display_service.h"
#endif
#include "input_service.h"
#include "native_audio_output.h"
#include "native_state.h"
#include "network_service.h"
#include "nvs_flash.h"
#include "persistent_settings.h"
#include "playlist_service.h"
#include "radio_control.h"
#include "storage_service.h"
#if CONFIG_YORADIO_STATUS_LED
#include "status_led.h"
#endif
#include "time_service.h"
#include "web_service.h"

static const char *TAG = "yoradio8266";

#if YORADIO_ESP8266_CODEC_RAM_BENCHMARK
void codec_ram_benchmark_run(void);
#endif
#if YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
void audio_output_benchmark_run(void);
#endif

void app_main(void) {
#if YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
    ESP_LOGI(TAG, "isolated generated-PCM audio output benchmark; "
                  "Wi-Fi and codecs disabled");
    audio_output_benchmark_run();
    for (;;) vTaskDelay(portMAX_DELAY);
#elif YORADIO_ESP8266_CODEC_RAM_BENCHMARK
    ESP_LOGI(TAG, "isolated codec RAM benchmark; Wi-Fi and audio output disabled");
    codec_ram_benchmark_run();
    for (;;) vTaskDelay(portMAX_DELAY);
#else
    native_state_init();
    ESP_LOGI(TAG, "yoRadio ESP8266 RTOS SDK native starting");
    ESP_LOGI(TAG, "CPU: %u MHz; free heap: %u",
             CONFIG_ESP8266_DEFAULT_CPU_FREQ_MHZ,
             esp_get_free_heap_size());
#if YORADIO_ESP8266_SPI_PDM
    ESP_LOGI(TAG,
             "profile: HTTP only, Helix MP3/AAC, SPI-PDM GPIO %d at %u Hz",
             BOARD_SPI_PDM_DATA_GPIO, BOARD_SPI_PDM_BIT_RATE_HZ);
#elif YORADIO_ESP8266_I2S_PDM
    ESP_LOGI(TAG,
             "profile: HTTP only, Helix MP3/AAC, I2S-PDM DMA GPIO %d, "
             "carrier %u Hz, PDM%u x%u; UART RX ignored",
             BOARD_I2S_DATA_GPIO, BOARD_I2S_PDM_CARRIER_HZ,
             BOARD_I2S_PDM_OVERSAMPLE, BOARD_I2S_PDM_REPEAT);
#else
    ESP_LOGI(TAG, "profile: HTTP only, Helix MP3/AAC, I2S GPIO %d/%d/%d",
             BOARD_I2S_DATA_GPIO, BOARD_I2S_BCLK_GPIO,
             BOARD_I2S_LRCLK_GPIO);
#endif

    esp_err_t result = nvs_flash_init();
    if (result == ESP_ERR_NVS_NO_FREE_PAGES) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        result = nvs_flash_init();
    }
    ESP_ERROR_CHECK(result);
    ESP_ERROR_CHECK(persistent_settings_init());
#if CONFIG_YORADIO_OLED
    ESP_ERROR_CHECK(display_service_start());
#else
    ESP_LOGI(TAG, "OLED disabled: WebUI-only low-memory profile");
#endif
    ESP_ERROR_CHECK(audio_service_init());
    /* Install the I2S/SLC ISR and allocate its fixed DMA ring before Wi-Fi
     * starts consuming and fragmenting the small ESP8266 heap. The ring emits
     * neutral PDM until decoded PCM becomes available. */
    ESP_ERROR_CHECK(native_audio_output_init());
#if CONFIG_YORADIO_STATUS_LED
    ESP_ERROR_CHECK(status_led_init());
#endif
    result = storage_service_init();
    if (result == ESP_OK) {
        result = playlist_service_init();
        if (result != ESP_OK && result != ESP_ERR_NOT_FOUND)
            ESP_LOGE(TAG, "Playlist initialization failed: %s",
                     esp_err_to_name(result));
        native_state_set_station_count(playlist_service_count());
    }
    esp_err_t radio_result = radio_control_init();
    if (radio_result != ESP_OK && radio_result != ESP_ERR_NOT_FOUND)
        ESP_LOGW(TAG, "Radio control initialization: %s",
                 esp_err_to_name(radio_result));
    ESP_ERROR_CHECK(input_service_start());
    ESP_ERROR_CHECK(time_service_start());
    ESP_ERROR_CHECK(network_service_start());
    ESP_ERROR_CHECK(web_service_start());

    for (;;) {
        radio_control_flush_pending();
        network_service_poll();
        web_service_poll();
#if CONFIG_YORADIO_STATUS_LED
        status_led_poll();
#endif
        vTaskDelay(pdMS_TO_TICKS(250));
    }
#endif
}
