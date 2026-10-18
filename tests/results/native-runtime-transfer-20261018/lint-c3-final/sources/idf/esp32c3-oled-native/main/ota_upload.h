#pragma once
#include "native_ota_form.h"
// Compatibility entry points; explicit image/maintenance policy is portable.
typedef native_ota_form_t ota_upload_t;
bool ota_upload_init(ota_upload_t *, const char *, const native_ota_policy_t *);
bool ota_upload_feed(ota_upload_t *, const uint8_t *, size_t);
bool ota_upload_finish(ota_upload_t *);
bool ota_upload_activate(ota_upload_t *);
void ota_upload_abort(ota_upload_t *);
