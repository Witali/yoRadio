#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

typedef enum {
    NATIVE_NETWORK_STARTING = 0,
    NATIVE_NETWORK_CLIENT,
    NATIVE_NETWORK_ACCESS_POINT,
    NATIVE_NETWORK_ERROR,
} native_network_mode_t;

typedef struct {
    SemaphoreHandle_t lock;
    native_network_mode_t network_mode;
    bool web_ready;
    bool audio_running;
    bool audio_pending;
    uint32_t audio_generation;
    int8_t wifi_rssi;
    uint32_t ipv4;
    char station[96];
    char stream_format[48];
    char title[192];
} native_state_t;

void native_state_init(native_state_t *state);
void native_state_set_network(native_state_t *state,
                              native_network_mode_t mode,
                              uint32_t ipv4);
void native_state_snapshot(native_state_t *state, native_state_t *snapshot);
void native_state_begin_audio(native_state_t *state, uint32_t generation,
                              const char *station, const char *format);
void native_state_set_audio(native_state_t *state, uint32_t generation,
                            bool running, const char *format);
void native_state_set_title(native_state_t *state, uint32_t generation,
                            const char *title);
void native_state_set_station(native_state_t *state, const char *station);
void native_state_set_pending(native_state_t *state, uint32_t generation, bool pending);
void native_state_set_connecting(native_state_t *state, uint32_t generation);

