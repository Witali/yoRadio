#pragma once

#include "native_wifi_store.h"

// Exact bounded native edit schema. Rejects unknown/duplicate members, wrong
// types, invalid UTF-8/Unicode escapes, decoded NUL and trailing input. The
// output is erased on failure; caller erases successful newly supplied values.
native_wifi_result_t native_wifi_json_decode(const uint8_t *body, size_t size,
                                            native_wifi_edit_t *out);
// Produces password-free valid UTF-8 JSON. Invalid legacy SSID bytes are shown
// as U+FFFD, with ssid_utf8:false; omission on an unchanged edit preserves them.
bool native_wifi_json_metadata(const native_wifi_metadata_t *metadata,
                               char *out, size_t capacity, size_t *size);
