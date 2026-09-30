#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "ota_upload.c"

static esp_partition_t active = {0x10000, 16384, "app0"};
static esp_partition_t spare = {0x1e0000, 16384, "app1"};
static esp_app_desc_t app = {.magic_word = ESP_APP_DESC_MAGIC_WORD,
    .project_name = "yoradio_esp32c3_oled_native"};
static uint8_t image[10000], flash[16384], body[22000];
static size_t body_size, written, metadata_size;
static unsigned begins, ends, aborts, selects;
static bool open_handle, no_partition, conflict;
static int inject;

const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *p) {
    (void)p; return no_partition ? NULL : conflict ? &active : &spare;
}
const esp_partition_t *esp_ota_get_running_partition(void) { return &active; }
const esp_app_desc_t *esp_app_get_description(void) { return &app; }
esp_err_t esp_ota_begin(const esp_partition_t *p, size_t size, esp_ota_handle_t *h) {
    assert(p == &spare && size == OTA_WITH_SEQUENTIAL_WRITES && !open_handle);
    ++begins;
    if (inject == 1) return ESP_FAIL;
    open_handle = true; *h = 42; return ESP_OK;
}
esp_err_t esp_ota_write(esp_ota_handle_t h, const void *data, size_t size) {
    assert(h == 42 && open_handle && size <= 4096 && written + size <= spare.size);
    if (inject == 2) return ESP_FAIL;
    memcpy(flash + written, data, size); written += size; return ESP_OK;
}
esp_err_t esp_ota_end(esp_ota_handle_t h) {
    assert(h == 42 && open_handle); open_handle = false; ++ends;
    return inject == 3 ? ESP_FAIL : ESP_OK;
}
esp_err_t esp_ota_abort(esp_ota_handle_t h) {
    assert(h == 42 && open_handle); open_handle = false; ++aborts; return ESP_OK;
}
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *p) {
    assert(p == &spare && !open_handle && ends == 1); ++selects;
    return inject == 5 ? ESP_FAIL : ESP_OK;
}
esp_err_t esp_image_get_metadata(const esp_partition_pos_t *p, esp_image_metadata_t *m) {
    assert(p->offset == spare.address && p->size == spare.size);
    m->image_len = metadata_size; return inject == 4 ? ESP_FAIL : ESP_OK;
}
static void reset(void) {
    written = begins = ends = aborts = selects = 0;
    open_handle = no_partition = conflict = false; inject = 0;
    spare.size = sizeof(flash); metadata_size = sizeof(image);
    memset(flash, 0xa5, sizeof(flash));
}
static void make_body(const char *target, size_t length, const char *tail) {
    int prefix = snprintf((char *)body, sizeof(body),
        "--test-boundary\r\nContent-Disposition: form-data; name=\"updatetarget\"\r\n\r\n%s"
        "\r\n--test-boundary\r\nContent-Disposition: form-data; name=\"update\"; filename=\"app.bin\""
        "\r\nContent-Type: application/octet-stream\r\n\r\n", target);
    assert(length <= sizeof(image));
    memcpy(body + prefix, image, length);
    memcpy(body + prefix + length, tail, strlen(tail));
    body_size = (size_t)prefix + length + strlen(tail);
}
#ifndef OTA_HTTP_TEST
static bool receive(ota_upload_t *u, size_t step, size_t size) {
    for (size_t i = 0; i < size; i += step) {
        size_t n = size - i; if (n > step) n = step;
        if (!ota_upload_feed(u, body + i, n)) return false;
    }
    return ota_upload_finish(u);
}
int main(void) {
    _Static_assert(sizeof(esp_image_header_t) == 24, "image header ABI");
    _Static_assert(sizeof(esp_app_desc_t) == 256, "app description ABI");
    for (size_t i = 0; i < sizeof(image); ++i) image[i] = (uint8_t)(i * 71);
    esp_image_header_t header = {.magic = ESP_IMAGE_HEADER_MAGIC, .chip_id = 5};
    memcpy(image, &header, sizeof(header)); memcpy(image + 32, &app, sizeof(app));
    memcpy(image + 420, "\r\n--test-boundaryX-not-a-boundary", 33);
    const char *tail = "\r\n--test-boundary--\r\n";
    make_body("firmware", sizeof(image), tail);
    for (size_t step = 1; step <= 600; ++step) {
        reset(); ota_upload_t u; assert(ota_upload_init(&u, "test-boundary"));
        assert(receive(&u, step, body_size));
        assert(!selects && begins == 1 && ends == 1 && !aborts);
        assert(written == sizeof(image) && !memcmp(flash, image, written));
        assert(ota_upload_activate(&u) && selects == 1);
        ota_upload_abort(&u); assert(!aborts);
    }
    for (size_t cut = 0; cut < body_size - 4; ++cut) {
        reset(); ota_upload_t u; assert(ota_upload_init(&u, "test-boundary"));
        assert(!receive(&u, 777, cut)); assert(!ota_upload_activate(&u));
        ota_upload_abort(&u); assert(!open_handle && !selects);
    }
    // SDK failures must never select the image or double-free an ended handle.
    for (int error = 1; error <= 5; ++error) {
        reset(); inject = error; ota_upload_t u;
        assert(ota_upload_init(&u, "test-boundary"));
        bool ok = receive(&u, 1000, body_size);
        assert(!(ok && ota_upload_activate(&u)));
        ota_upload_abort(&u); assert(!open_handle);
        assert(selects == (error == 5 ? 1U : 0U));
        assert(aborts == (error == 2 ? 1U : 0U));
    }
    // Wrong chip, bootloader/bogus description and another project: no erase.
    const size_t offsets[] = {0, 12, 32, 80};
    for (size_t i = 0; i < sizeof(offsets)/sizeof(offsets[0]); ++i) {
        image[offsets[i]] ^= 0x40; make_body("fw", sizeof(image), tail);
        reset(); ota_upload_t u; assert(ota_upload_init(&u, "test-boundary"));
        assert(!receive(&u, 123, body_size)); ota_upload_abort(&u);
        assert(!begins && !selects); image[offsets[i]] ^= 0x40;
    }
    const char *bad_targets[] = {"spiffs", "", "firmware-extra", "firmware-0123456789"};
    for (size_t i=0; i<sizeof(bad_targets)/sizeof(bad_targets[0]); ++i) {
        make_body(bad_targets[i], sizeof(image), tail); reset(); ota_upload_t u;
        assert(ota_upload_init(&u, "test-boundary"));
        assert(!receive(&u, 1, body_size)); ota_upload_abort(&u); assert(!begins);
    }
    for (int mode=0; mode<5; ++mode) {
        reset(); ota_upload_t u;
        if (mode == 0) spare.size = sizeof(image)-1;
        if (mode == 1) metadata_size = sizeof(image)-1; // extra byte
        if (mode == 2) metadata_size = sizeof(image)+1; // stale flash tail
        make_body("fw", sizeof(image), mode == 3 ? "\r\n--test-boundary--\r\nJUNK" :
            mode == 4 ? "\r\n--test-boundary\r\nContent-Disposition: form-data; name=\"update\"\r\n\r\nx\r\n--test-boundary--\r\n" : tail);
        assert(ota_upload_init(&u, "test-boundary"));
        assert(!receive(&u, 8192, body_size)); ota_upload_abort(&u);
        assert(!open_handle && !selects);
    }
    reset(); ota_upload_t u;
    no_partition = true; assert(!ota_upload_init(&u, "test-boundary"));
    no_partition = false; conflict = true; assert(!ota_upload_init(&u, "test-boundary"));
    conflict = false; assert(!ota_upload_init(&u, "bad\r\nboundary"));
    reset(); make_body("fw", sizeof(image), tail);
    assert(ota_upload_init(&u, "test-boundary"));
    assert(receive(&u, 1234, body_size) && ota_upload_activate(&u));
    puts("C3 OTA streaming, partition selection and failure cleanup tests passed");
}
#endif
