#include "ota_upload.h"
bool ota_upload_init(ota_upload_t *u, const char *boundary, const native_ota_policy_t *policy) {
    return native_ota_form_init(u, boundary, policy);
}
bool ota_upload_feed(ota_upload_t *u, const uint8_t *data, size_t size) { return native_ota_form_feed(u, data, size); }
bool ota_upload_finish(ota_upload_t *u) { return native_ota_form_finish(u); }
bool ota_upload_activate(ota_upload_t *u) { return native_ota_form_activate(u); }
void ota_upload_abort(ota_upload_t *u) { native_ota_form_abort(u); }
