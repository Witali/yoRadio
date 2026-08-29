#include "native_state.h"

#include <string.h>

static SemaphoreHandle_t s_lock;
static native_state_t s_state;

void native_state_init(void) {
    s_lock = xSemaphoreCreateMutex();
    memset(&s_state, 0, sizeof(s_state));
    s_state.network_mode = NETWORK_STARTING;
    s_state.station_index = 1;
    strcpy(s_state.station, "yoRadio ESP8266");
}

void native_state_snapshot(native_state_t *output) {
    if (!output) return;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    *output = s_state;
    xSemaphoreGive(s_lock);
}

void native_state_update(const native_state_t *input) {
    if (!input) return;
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_state = *input;
    xSemaphoreGive(s_lock);
}

void native_state_set_network(network_mode_t mode) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_state.network_mode = mode;
    xSemaphoreGive(s_lock);
}

void native_state_set_ip(const char *ip) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    if (ip) {
        strncpy(s_state.ip, ip, sizeof(s_state.ip) - 1);
        s_state.ip[sizeof(s_state.ip) - 1] = '\0';
    } else {
        s_state.ip[0] = '\0';
    }
    xSemaphoreGive(s_lock);
}

void native_state_set_wifi_rssi(int8_t rssi) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_state.wifi_rssi = rssi;
    xSemaphoreGive(s_lock);
}

void native_state_set_station_count(uint16_t count) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_state.station_count = count;
    xSemaphoreGive(s_lock);
}

void native_state_set_audio(bool playing, bool connecting, const char *error) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_state.playing = playing;
    s_state.connecting = connecting;
    if (error) {
        strncpy(s_state.error, error, sizeof(s_state.error) - 1);
        s_state.error[sizeof(s_state.error) - 1] = '\0';
    } else {
        s_state.error[0] = '\0';
    }
    if (!playing && !connecting) s_state.title[0] = '\0';
    xSemaphoreGive(s_lock);
}

void native_state_set_title(const char *title) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    strncpy(s_state.title, title ? title : "", sizeof(s_state.title) - 1);
    s_state.title[sizeof(s_state.title) - 1] = '\0';
    xSemaphoreGive(s_lock);
}

void native_state_set_stream(codec_type_t codec, uint32_t bitrate_kbps,
                             uint32_t sample_rate_hz, uint8_t channels) {
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_state.codec = codec;
    s_state.bitrate_kbps = bitrate_kbps;
    s_state.sample_rate_hz = sample_rate_hz;
    s_state.channels = channels;
    xSemaphoreGive(s_lock);
}

const char *native_codec_name(codec_type_t codec) {
    if (codec == CODEC_HELIX_MP3) return "MP3";
    if (codec == CODEC_HELIX_AAC) return "AAC";
    return "";
}
