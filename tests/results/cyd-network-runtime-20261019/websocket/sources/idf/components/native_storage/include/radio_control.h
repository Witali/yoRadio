#pragma once

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"
#include "native_state.h"

esp_err_t radio_control_init(native_state_t *state);
esp_err_t radio_control_reindex_playlist(void);
// Validate a staged CSV and build its staged index while holding radio control.
// Publisher serializes filesystem readers and commits or rolls back both files.
// No new CSV is published on invalid input, lock timeout or index-write failure.
typedef bool (*radio_playlist_publisher_t)(const char *csv_temporary,
                                           const char *index_temporary);
esp_err_t radio_control_publish_playlist(const char *csv_temporary,
                                         radio_playlist_publisher_t publisher);
esp_err_t radio_control_play(uint16_t item);
esp_err_t radio_control_stop(void);
esp_err_t radio_control_toggle(void);
esp_err_t radio_control_next(void);
esp_err_t radio_control_previous(void);
bool radio_control_smartstart_enabled(void);
esp_err_t radio_control_set_smartstart_enabled(bool enabled);
uint16_t radio_control_current_item(void);
uint16_t radio_control_playlist_count(void);
typedef struct {
    uint16_t item, count;
    bool smartstart;
    char name[144];
} radio_control_snapshot_t;
bool radio_control_snapshot(radio_control_snapshot_t *snapshot);
void radio_control_current_name(char *name, size_t name_size);
