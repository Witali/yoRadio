#include "native_ota_form.h"

static bool form_fail(native_ota_form_t *form, const char *error) {
    if (!form->error) form->error = form->image.error ? form->image.error : error;
    return false;
}
static bool form_part(mp_event_t event, const uint8_t *data, size_t size, void *context) {
    native_ota_form_t *form = context;
    if (event == MP_BEGIN) {
        char name[24], filename[128]; bool have_filename;
        if (!mp_disposition((const char *)data, name, sizeof(name), filename,
                            sizeof(filename), &have_filename))
            return form_fail(form, "Invalid firmware field headers");
        form->target_part = !strcmp(name, "updatetarget");
        if (form->target_part) {
            if (form->target_seen || form->image_seen || have_filename)
                return form_fail(form, "Duplicate or misplaced firmware target");
            form->target_seen = true;
        } else {
            if (strcmp(name, "update") || form->image_seen || !form->target_seen ||
                !have_filename || !filename[0])
                return form_fail(form, "Expected one selected firmware file after its target");
            if (false)
                return form_fail(form, "Only application OTA is supported");
            form->image_seen = true;
        }
        return true;
    }
    if (form->target_part) {
        if (event == MP_DATA) {
            if (size >= sizeof(form->target) - form->target_length || memchr(data, 0, size))
                return form_fail(form, "Invalid firmware target");
            memcpy(form->target + form->target_length, data, size);
            form->target_length += size;
            form->target[form->target_length] = 0;
        }
        return true;
    }
    if (event == MP_END) { form->image_complete = true; return true; }
    return native_ota_sink_feed(&form->image, data, size) || form_fail(form, "Invalid firmware image");
}
bool native_ota_form_init(native_ota_form_t *form, const char *boundary,
                          const native_ota_policy_t *policy) {
    if (!form) return false;
    memset(form, 0, sizeof(*form));
    if (!native_ota_sink_init(&form->image, policy)) return form_fail(form, "No spare application slot");
    form->partition = form->image.partition;
    if (!mp_init(&form->parser, boundary, form_part, form)) return form_fail(form, "Invalid multipart boundary");
    return true;
}
bool native_ota_form_feed(native_ota_form_t *form, const uint8_t *data, size_t size) {
    if (!form || form->error || form->image.verified || form->image.closed) return false;
    return mp_feed(&form->parser, data, size) || form_fail(form, "Malformed multipart upload");
}
bool native_ota_form_finish(native_ota_form_t *form) {
    if (!form || form->error) return false;
    if (!mp_complete(&form->parser) || !form->image_seen || !form->image_complete)
        return form_fail(form, "Incomplete firmware upload");
    return native_ota_sink_finish(&form->image) || form_fail(form, "Firmware verification failed");
}
bool native_ota_form_activate(native_ota_form_t *form) {
    if (!form || form->error) return false;
    return native_ota_sink_activate(&form->image) || form_fail(form, "Cannot select firmware for boot");
}
void native_ota_form_abort(native_ota_form_t *form) {
    if (form) native_ota_sink_abort(&form->image);
}
