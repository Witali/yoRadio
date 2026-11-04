// Whole production audio service; synthetic transport and output hardware only.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdio>
#include <cstring>
#include "esp_audio_simple_dec.h"
#include "esp_opus_dec.h"
#include "reference_contract.h"
#include "esp_heap_caps.h"
#include "esp_http_client.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_timer.h"
#include "driver/i2s_pdm.h"
#include "driver/gpio.h"
#include "nvs_flash.h"
#include "board_config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "psa/crypto.h"
extern "C" {
#include "audio_service.h"
#include "native_audio_output.h"
#include "native_audio_settings.h"
#include "native_network_power.h"
}

#ifdef NDEBUG
#error "The task diagnostic requires assertions"
#endif

#include "freertos/ringbuf.h"
#include "esp_attr.h"
#include "sdkconfig.h"
