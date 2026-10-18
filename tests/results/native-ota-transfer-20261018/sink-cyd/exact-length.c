#include "native_ota_sink.h"

#include <string.h>
#include "esp_app_desc.h"
#include "esp_image_format.h"

static bool fail(native_ota_sink_t *sink, const char *message) {
    if (!sink->error) sink->error = message;
    sink->closed = true;
    return false;
}

static bool flush(native_ota_sink_t *sink) {
    if (esp_ota_write(sink->handle, sink->buffer, sink->buffered) != ESP_OK)
        return fail(sink, "Flash write failed");
    sink->buffered = 0;
    return true;
}

static bool begin(native_ota_sink_t *sink) {
    esp_image_header_t header;
    esp_image_segment_header_t segment;
    esp_app_desc_t description;
    memcpy(&header, sink->buffer, sizeof(header));
    memcpy(&segment, sink->buffer + sizeof(header), sizeof(segment));
    memcpy(&description, sink->buffer + sizeof(header) + sizeof(segment),
           sizeof(description));
    if (header.magic != ESP_IMAGE_HEADER_MAGIC ||
        header.chip_id != sink->policy.expected_chip ||
        !header.segment_count || header.segment_count > ESP_IMAGE_MAX_SEGMENTS ||
        header.hash_appended > 1 || segment.data_len < sizeof(description) ||
        segment.data_len % 4 || segment.data_len > sink->limit - sizeof(header) - sizeof(segment) ||
        description.magic_word != ESP_APP_DESC_MAGIC_WORD ||
        memcmp(description.project_name, sink->policy.expected_project,
               sizeof(description.project_name)) != 0)
        return fail(sink, "Choose an application image for this board and project");
    if (sink->policy.before_flash(sink->policy.context) != ESP_OK)
        return fail(sink, "Cannot enter OTA maintenance");
    sink->maintenance_entered = true;
    if (esp_ota_begin(sink->partition, OTA_WITH_SEQUENTIAL_WRITES,
                      &sink->handle) != ESP_OK)
        return fail(sink, "Cannot start OTA in the spare application slot");
    sink->started = true;
    return true;
}

bool native_ota_sink_init(native_ota_sink_t *sink,
                          const native_ota_policy_t *policy) {
    if (!sink) return false;
    memset(sink, 0, sizeof(*sink));
    if (!policy || !policy->image_limit || !policy->before_flash ||
        !policy->expected_project[0] ||
        !memchr(policy->expected_project, 0, sizeof(policy->expected_project)))
        return fail(sink, "Invalid OTA policy");
    sink->policy = *policy;
    const esp_partition_t *running = esp_ota_get_running_partition();
    if (!running) return fail(sink, "No running application partition");
    sink->partition = esp_ota_get_next_update_partition(running);
    const esp_partition_t *target = sink->partition;
    if (!target || target->type != ESP_PARTITION_TYPE_APP ||
        target->subtype < ESP_PARTITION_SUBTYPE_APP_OTA_MIN ||
        target->subtype >= ESP_PARTITION_SUBTYPE_APP_OTA_MAX ||
        target->flash_chip != running->flash_chip ||
        ((uint64_t)target->address < (uint64_t)running->address + running->size &&
         (uint64_t)running->address < (uint64_t)target->address + target->size))
        return fail(sink, "No spare OTA application partition");
    sink->limit = target->size < policy->image_limit ? target->size : policy->image_limit;
    if (sink->limit < sizeof(esp_image_header_t) +
                      sizeof(esp_image_segment_header_t) + sizeof(esp_app_desc_t))
        return fail(sink, "Application slot is too small");
    return true;
}

bool native_ota_sink_feed(native_ota_sink_t *sink,
                          const uint8_t *data, size_t size) {
    if (!sink || sink->error || sink->closed || sink->verified || !sink->partition)
        return false;
    if ((!data && size) || size > sink->limit - sink->received)
        return fail(sink, "Firmware exceeds the application size limit");
    sink->received += size;
    while (size) {
        size_t count = sizeof(sink->buffer) - sink->buffered;
        if (count > size) count = size;
        memcpy(sink->buffer + sink->buffered, data, count);
        sink->buffered += count;
        data += count;
        size -= count;
        if (!sink->started && sink->buffered >= sizeof(esp_image_header_t) +
            sizeof(esp_image_segment_header_t) + sizeof(esp_app_desc_t) &&
            !begin(sink)) return false;
        if (sink->buffered == sizeof(sink->buffer) && !flush(sink)) return false;
    }
    return true;
}

bool native_ota_sink_finish(native_ota_sink_t *sink) {
    if (!sink || sink->error) return false;
    if (sink->activated) return true;
    if (sink->closed) return false;
    if (sink->verified) return true;
    if (!sink->started) return fail(sink, "Incomplete application image");
    if (sink->buffered && !flush(sink)) return false;
    esp_err_t result = esp_ota_end(sink->handle);
    sink->started = false; // Public SDK contract consumes the handle on every result.
    if (result != ESP_OK) return fail(sink, "Firmware image verification failed");
    esp_image_metadata_t metadata;
    esp_partition_pos_t position = {
        .offset = sink->partition->address, .size = sink->received,
    };
    if (esp_image_verify(ESP_IMAGE_VERIFY, &position, &metadata) != ESP_OK ||
        false)
        return fail(sink, "Upload length does not match the verified application image");
    sink->verified = true;
    return true;
}

bool native_ota_sink_activate(native_ota_sink_t *sink) {
    if (!sink || sink->error) return false;
    if (sink->activated) return true;
    if (!sink->verified || sink->closed) return false;
    if (esp_ota_set_boot_partition(sink->partition) != ESP_OK)
        return fail(sink, "Cannot select the new application for boot");
    sink->activated = sink->closed = true;
    return true;
}

void native_ota_sink_abort(native_ota_sink_t *sink) {
    if (!sink) return;
    if (sink->started) {
        (void)esp_ota_abort(sink->handle);
        sink->started = false;
    }
    sink->closed = true;
    if (!sink->activated) sink->verified = false;
}
