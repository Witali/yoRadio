#include "native_state.h"

#include <string.h>

void native_state_init(native_state_t *state) {
    memset(state, 0, sizeof(*state));
    state->lock = xSemaphoreCreateMutex();
    state->network_mode = NATIVE_NETWORK_STARTING;
    strcpy(state->station, "yoRadio native");
    strcpy(state->stream_format, "idle");
}

void native_state_set_network(native_state_t *state,
                              native_network_mode_t mode,
                              uint32_t ipv4) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        state->network_mode = mode;
        state->ipv4 = ipv4;
        xSemaphoreGive(state->lock);
    }
}

void native_state_snapshot(native_state_t *state, native_state_t *snapshot) {
    if (!state || !snapshot) return;
    memset(snapshot, 0, sizeof(*snapshot));
    if (state->lock &&
        xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        SemaphoreHandle_t lock = state->lock;
        memcpy(snapshot, state, sizeof(*snapshot));
        snapshot->lock = NULL;
        xSemaphoreGive(lock);
    }
}

