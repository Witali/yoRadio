#include "ota_upload.h"

#include "esp_app_format.h"
#include "esp_image_format.h"

static bool fail(ota_upload_t *u, const char *message) {
    u->error = message;
    return false;
}

static bool flush(ota_upload_t *u) {
    if (esp_ota_write(u->handle, u->buffer, u->buffered) != ESP_OK)
        return fail(u, "Flash write failed");
    u->buffered = 0;
    return true;
}

static bool check_header(ota_upload_t *u) {
    esp_image_header_t header;
    esp_app_desc_t description;
    memcpy(&header, u->buffer, sizeof(header));
    memcpy(&description,
           u->buffer + sizeof(header) + sizeof(esp_image_segment_header_t),
           sizeof(description));
    if (header.magic != ESP_IMAGE_HEADER_MAGIC ||
        header.chip_id != ESP_CHIP_ID_ESP32C3 ||
        description.magic_word != ESP_APP_DESC_MAGIC_WORD ||
        memcmp(description.project_name, esp_app_get_description()->project_name,
               sizeof(description.project_name)) != 0)
        return fail(u, "Choose ESP32-C3 OLED native app.bin for this board");
    if (esp_ota_begin(u->partition, OTA_WITH_SEQUENTIAL_WRITES,
                      &u->handle) != ESP_OK)
        return fail(u, "Cannot start OTA in the spare application slot");
    u->started = true;
    return true;
}

static bool part(mp_event_t event, const uint8_t *data, size_t size, void *ctx) {
    ota_upload_t *u = ctx;
    if (event == MP_BEGIN) {
        char name[24];
        if (!mp_parameter((const char *)data, "name", name, sizeof(name)))
            return fail(u, "Missing upload field name");
        u->target_part = strcmp(name, "updatetarget") == 0;
        if (u->target_part) {
            if (u->target_seen || u->image_seen)
                return fail(u, "Duplicate or misplaced firmware target");
            u->target_seen = true;
        } else {
            if (strcmp(name, "update") || u->image_seen || !u->target_seen)
                return fail(u, "Expected one firmware file after its target");
            if (strcmp(u->target, "fw") && strcmp(u->target, "firmware"))
                return fail(u, "Only application OTA is supported; use Board for WebUI files");
            u->image_seen = true;
        }
        return true;
    }
    if (u->target_part) {
        if (event == MP_DATA) {
            if (size >= sizeof(u->target) - u->target_length ||
                memchr(data, 0, size)) return fail(u, "Invalid firmware target");
            memcpy(u->target + u->target_length, data, size);
            u->target_length += size;
            u->target[u->target_length] = 0;
        }
        return true;
    }
    if (event == MP_END) {
        u->image_complete = true;
        return true;
    }
    if (size > u->partition->size - u->received)
        return fail(u, "Firmware exceeds the application slot size");
    u->received += size;
    while (size) {
        size_t count = sizeof(u->buffer) - u->buffered;
        if (count > size) count = size;
        memcpy(u->buffer + u->buffered, data, count);
        u->buffered += count;
        data += count;
        size -= count;
        if (!u->started && u->buffered >= sizeof(esp_image_header_t) +
            sizeof(esp_image_segment_header_t) + sizeof(esp_app_desc_t) &&
            !check_header(u)) return false;
        if (u->buffered == sizeof(u->buffer) && !flush(u)) return false;
    }
    return true;
}

bool ota_upload_init(ota_upload_t *u, const char *boundary) {
    memset(u, 0, sizeof(*u));
    u->partition = esp_ota_get_next_update_partition(NULL);
    const esp_partition_t *running = esp_ota_get_running_partition();
    if (!u->partition || !running || u->partition->address == running->address)
        return fail(u, "No spare application slot");
    if (!mp_init(&u->parser, boundary, part, u))
        return fail(u, "Invalid multipart boundary");
    return true;
}

bool ota_upload_feed(ota_upload_t *u, const uint8_t *data, size_t size) {
    if (u->error || u->verified) return false;
    if (!mp_feed(&u->parser, data, size)) {
        if (!u->error) u->error = "Malformed multipart upload";
        return false;
    }
    return true;
}

bool ota_upload_finish(ota_upload_t *u) {
    if (u->error) return false;
    if (!mp_complete(&u->parser) || !u->image_complete || !u->started)
        return fail(u, "Incomplete firmware upload");
    if (u->buffered && !flush(u)) return false;
    esp_err_t result = esp_ota_end(u->handle);
    u->started = false; // ESP-IDF consumes the handle even on failure.
    if (result != ESP_OK) return fail(u, "Firmware image verification failed");
    /* Also reject a truncated upload over old flash contents, and trailing
     * bytes such as a merged flash image. esp_ota_end alone allows a tail. */
    esp_image_metadata_t metadata;
    esp_partition_pos_t position = {
        .offset = u->partition->address, .size = u->partition->size,
    };
    if (esp_image_get_metadata(&position, &metadata) != ESP_OK ||
        metadata.image_len != u->received)
        return fail(u, "Upload length does not match the application image");
    u->verified = true;
    return true;
}

bool ota_upload_activate(ota_upload_t *u) {
    if (!u->verified || u->error) return false;
    if (esp_ota_set_boot_partition(u->partition) != ESP_OK)
        return fail(u, "Cannot select the new application for boot");
    return true;
}

void ota_upload_abort(ota_upload_t *u) {
    if (u->started) {
        (void)esp_ota_abort(u->handle);
        u->started = false;
    }
    u->verified = false;
}
