#define OTA_HTTP_TEST
#include "esp32c3_ota_test.c"
#include "web_ota.c"

static int activity, replies, notifications, deleted, stopped, notes;
static int status_code, transport_error;
static bool sleeping, task_failure, send_failure;
static size_t read_offset;
static int64_t now_us;
static const char *content_type;
static char response[512];
static bool half_closed;
int httpd_req_to_sockfd(httpd_req_t *req) { (void)req; return 42; }
int setsockopt(int fd, int level, int option, const void *value, socklen_t size) {
    (void)fd; (void)level; (void)option; (void)value; (void)size; return 0;
}
int shutdown(int fd, int how) { assert(fd==42 && how==SHUT_WR && replies); half_closed=true; return 0; }
ssize_t recv(int fd, void *buffer, size_t size, int flags) {
    (void)buffer; (void)size; assert(fd==42 && flags==MSG_DONTWAIT && half_closed);
    errno=EAGAIN; return -1;
}
bool deep_sleep_clock_begin_activity(void) {
    if (sleeping) return false;
    ++activity; return true;
}
void deep_sleep_clock_end_activity(void) { assert(activity > 0); --activity; }
void display_settings_note_activity(void) { ++notes; }
void audio_service_stop(void) { ++stopped; }
int64_t esp_timer_get_time(void) { return now_us; }
void vTaskDelay(unsigned n) { now_us += n * 1000; }
void esp_restart(void) { assert(0 && "reboot task must wait for notification"); }
void ulTaskNotifyTake(int b, unsigned n) { (void)b; (void)n; }
int xTaskCreate(void (*fn)(void *), const char *name, unsigned stack, void *arg,
                 unsigned priority, TaskHandle_t *task) {
    (void)fn; (void)name; (void)stack; (void)arg; (void)priority;
    assert(!selects); if (task_failure) return 0; *task=(void *)1; return pdPASS;
}
void vTaskDelete(TaskHandle_t task) { assert(task == (void *)1); ++deleted; }
void xTaskNotifyGive(TaskHandle_t task) {
    assert(task == (void *)1 && replies && activity == 1 && selects == 1);
    ++notifications;
}
void esp_app_get_elf_sha256(char *out, size_t size) { snprintf(out, size, "abcdef"); }
int httpd_req_get_hdr_value_str(httpd_req_t *req, const char *name, char *out, size_t size) {
    (void)req; assert(!strcmp(name, "Content-Type"));
    if (!content_type || strlen(content_type) >= size) return ESP_FAIL;
    strcpy(out, content_type); return ESP_OK;
}
int httpd_req_recv(httpd_req_t *req, char *out, size_t size) {
    (void)req;
    if (transport_error == 1) return 0;
    if (transport_error == 2) { now_us += 5000000; return HTTPD_SOCK_ERR_TIMEOUT; }
    if (read_offset >= body_size) return 0;
    if (size > body_size - read_offset) size = body_size - read_offset;
    if (size > 139) size = 139;
    memcpy(out, body + read_offset, size); read_offset += size;
    // A slow but progressing upload must hit the absolute deadline too.
    if (transport_error == 3) now_us += 5000000;
    return (int)size;
}
int httpd_resp_set_type(httpd_req_t *r, const char *t) { (void)r; (void)t; return ESP_OK; }
int httpd_resp_set_status(httpd_req_t *r, const char *s) {
    (void)r; status_code = atoi(s); return ESP_OK;
}
int httpd_resp_set_hdr(httpd_req_t *r, const char *k, const char *v) {
    (void)r; (void)k; (void)v; return ESP_OK;
}
int httpd_resp_sendstr(httpd_req_t *r, const char *text) {
    (void)r; assert(activity || sleeping || s_reboot_pending);
    ++replies; snprintf(response, sizeof(response), "%s", text);
    return send_failure ? ESP_FAIL : ESP_OK;
}
static void reset_http(void) {
    reset(); activity = replies = notifications = deleted = stopped = notes = 0;
    sleeping = task_failure = send_failure = s_reboot_pending = false;
    status_code = 200; transport_error = 0; read_offset = 0; now_us = 0;
    half_closed=false;
    content_type = "multipart/form-data; boundary=\"test-boundary\"";
    esp_image_header_t header = {.magic=ESP_IMAGE_HEADER_MAGIC, .chip_id=5};
    memset(image, 0, sizeof(image)); memcpy(image, &header, sizeof(header));
    memcpy(image+32, &app, sizeof(app));
    make_body("firmware", sizeof(image), "\r\n--test-boundary--\r\n");
}
int main(void) {
    for (int scenario=0; scenario<14; ++scenario) {
        reset_http(); httpd_req_t req = {.content_len=body_size};
        if (scenario>=1 && scenario<=5) inject=scenario;
        if (scenario==6) content_type="application/octet-stream";
        if (scenario==7) req.content_len=spare.size+2049;
        if (scenario>=8 && scenario<=10) transport_error=scenario-7;
        if (scenario==11) task_failure=true;
        if (scenario==12) sleeping=true;
        if (scenario==13) { s_reboot_pending=true; activity=1; }
        int result=web_ota_handler(&req);
        if (!scenario) {
            assert(result==ESP_OK && status_code==200 && !strcmp(response,"OK"));
            assert(activity==1 && notifications==1 && !deleted);
        } else {
            assert(result==ESP_FAIL && status_code>=400 && !notifications);
            assert(!open_handle && activity==(scenario==13 ? 1 : 0));
            assert(selects==(scenario==5 ? 1U : 0U));
            assert(deleted==(scenario==5 ? 1 : 0));
            assert(half_closed);
        }
        assert(replies==1);
    }
    reset_http(); httpd_req_t req={.content_len=body_size}; send_failure=true;
    assert(web_ota_handler(&req)==ESP_FAIL);
    // Once otadata has been committed, a disconnected browser cannot cancel boot.
    assert(notifications==1 && activity==1 && s_reboot_pending);
    reset_http(); strcpy(app.version, "test\"\\\nversion");
    assert(web_ota_info_handler(&req)==ESP_OK && activity==0 && notes==1);
    assert(strstr(response,"test\\u0022\\u005c\\u000aversion"));
    assert(strstr(response,"\"app_elf_sha256\":\"0000000000000000000000000000000000000000000000000000000000000000\""));
    puts("C3 OTA HTTP deadlines, failure cleanup, deep-sleep lease and reboot ordering passed");
}
