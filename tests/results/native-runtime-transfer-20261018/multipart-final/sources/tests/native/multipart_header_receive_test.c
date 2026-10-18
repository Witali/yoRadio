#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "web_file_form.h"
#include "native_wifi_store.h"

typedef struct { size_t content_len, cursor; const char *body; } httpd_req_t;
#define ESP_OK 0
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
static const char *content_type;
static int httpd_req_get_hdr_value_str(httpd_req_t *request, const char *name,
                                      char *out, size_t size) {
    (void)request; assert(!strcmp(name, "Content-Type"));
    int length = snprintf(out, size, "%s", content_type);
    return length >= 0 && (size_t)length < size ? ESP_OK : -1;
}
static int httpd_req_recv(httpd_req_t *request, char *out, size_t size) {
    assert(request->cursor <= request->content_len);
    if (size > request->content_len - request->cursor) size = request->content_len - request->cursor;
    memcpy(out, request->body + request->cursor, size); request->cursor += size;
    return (int)size;
}
static int64_t esp_timer_get_time(void) { static int64_t time; return time += 100; }
static void vTaskDelay(unsigned ticks) { (void)ticks; }
// Header/receiver-only seam; the canonical HTTP fixture owns context and TLS.
#define native_wifi_request_io_progress(request) ((void)(request), true)
#include "receive-production.inc"

static bool parse(const char *type, const char *header, web_form_mode_t mode) {
    char body[1024];
    int length = snprintf(body, sizeof(body), "--test\r\n%s\r\n\r\nfixture\r\n--test--\r\n", header);
    assert(length >= 0 && (size_t)length < sizeof(body));
    content_type = type;
    httpd_req_t request = {.content_len=(size_t)length,.body=body};
    web_file_form_t form = {.mode=mode};
    return receive_form(&request, &form);
}

int main(int argc, char **argv) {
    assert(argc == 2);
    unsigned test = (unsigned)strtoul(argv[1], NULL, 10);
    if (test == 0) {
        assert(!parse("multipart/form-data; x-boundary=test",
                      "Content-Disposition: form-data; name=\"ssid\"", WEB_FORM_CREDENTIALS));
    } else if (test == 1) {
        assert(!parse("multipart/form-data; boundary=test",
                      "Content-Type: text/plain; name=\"ssid\"", WEB_FORM_CREDENTIALS));
    } else if (test == 2) {
        assert(!parse("multipart/form-data; boundary=test",
                      "Content-Disposition: form-data; name=\"ssid\"; NAME=\"pass\"", WEB_FORM_CREDENTIALS));
    } else if (test == 3) {
        assert(!parse("multipart/form-data; boundary=test; boundary=wrong",
                      "Content-Disposition: form-data; name=\"ssid\"", WEB_FORM_CREDENTIALS));
    } else {
        assert(parse("MULTIPART/FORM-DATA; BOUNDARY = \"test\"",
                     "content-disposition: FORM-DATA; NAME = ssid", WEB_FORM_CREDENTIALS));
    }
    printf("PASS actual C3 receive_form header case %u\n", test);
    return 0;
}
