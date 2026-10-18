#pragma once

#include "esp_err.h"
#include "native_state.h"

typedef enum {
    NATIVE_CODEC_AUTO = 0,
    NATIVE_CODEC_MP3,
    NATIVE_CODEC_AAC,
    NATIVE_CODEC_FLAC,
    NATIVE_CODEC_OGG,
} native_codec_t;

typedef struct {
    uint64_t epoch;
} audio_maintenance_token_t;

// ESP_OK is the only permission to erase/write an OTA partition: all owners
// have released old leases and output DMA is stopped. The gate remains held.
// Failure returns epoch=0. Cleanup continues in the owners and automatically
// restores prior playback when safe, unless an explicit Stop cancels resume.
// No owner retains a pointer to this caller-owned token. Play is busy while
// cleanup or maintenance is active. The finite budget includes lock waits;
// it does not promise a successful stop of an unresponsive network/driver.
esp_err_t audio_service_maintenance_begin(uint32_t timeout_ms,
                                         audio_maintenance_token_t *token);
// Consume a successful token and hand completion to the audio owners. ESP_OK
// means accepted, like Play: completion/resume is asynchronous and the gate
// stays held until owners finish. No allocation or blocking control lock.
// Stale/double tokens are rejected. Internal resume preserves URL/codec/label
// and never writes SmartStart/NVS.
esp_err_t audio_service_maintenance_end(audio_maintenance_token_t *token,
                                       bool resume_previous);

esp_err_t audio_service_start(native_state_t *state);
esp_err_t audio_service_play(const char *url, native_codec_t codec);
esp_err_t audio_service_resume(void);
void audio_service_stop(void);
esp_err_t audio_service_suspend_output(void);
esp_err_t audio_service_resume_output(void);
uint8_t audio_service_buffer_fill_percent(void);

