#pragma once

#include "native_wifi_store.h"

// Private path configuration. The credential owner serializes both helpers and
// ALL other writes to these names; initialize before exposing networking/WebUI.
// A boot-time tolerant network loader may remain independent of strict edits.
typedef struct {
    const char *live;
    const char *temporary;
    const char *backup;
} native_wifi_file_t;

native_wifi_result_t native_wifi_file_read(const native_wifi_file_t *paths,
                                          uint8_t *data, size_t capacity,
                                          size_t *size);
// Accepts validated CSV from the store, including its explicit delete-all size0.
// Retains the existing fflush/fclose + native_file_replace durability contract.
native_wifi_result_t native_wifi_file_publish(const native_wifi_file_t *paths,
                                             const uint8_t *data, size_t size);
