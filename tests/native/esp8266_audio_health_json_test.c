#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include "sdk_rx_diag.h"
#if YORADIO_ESP8266_SDK_RX_DIAG
void sdk_rx_diag_snapshot(sdk_rx_diag_snapshot_t *s) { memset(s, 0xff, sizeof(*s)); }
static unsigned esp_reset_reason(void) { return UINT_MAX; }
#endif
typedef int esp_err_t;
typedef struct { const char *uri; } httpd_req_t;
#define ESP_FAIL (-1)
typedef struct {
    uint32_t generation, uptime_ms, rx_bytes, pcm_frames, sample_rate;
    uint32_t rx_age_ms, pcm_age_ms, stack_free;
#if YORADIO_ESP8266_OPUS_STREAM_TEST
    uint32_t transport_phase;
    int32_t transport_result, transport_errno;
    uint32_t input_bytes;
#endif
} audio_service_health_t;
typedef struct { uint32_t queue_empty_events, chained_transfers; } native_audio_output_spi_stats_t;
enum { MALLOC_CAP_EXEC = 1 };
static char s_async_message[1088], captured[1088];
static int send_result, prepared, finished, server_errors;
static void prepare_short_response(httpd_req_t *r) { (void)r; ++prepared; }
static esp_err_t finish_short_response(httpd_req_t *r, esp_err_t result) { (void)r; ++finished; return result; }
static void audio_service_health(audio_service_health_t *h) {
    memset(h, 0xff, sizeof(*h));
#if YORADIO_ESP8266_OPUS_STREAM_TEST
    h->transport_result = INT32_MIN; h->transport_errno = INT32_MAX;
#endif
}
static void native_audio_output_get_spi_stats(native_audio_output_spi_stats_t *s) { memset(s, 0xff, sizeof(*s)); }
static unsigned esp_get_free_heap_size(void) { return UINT_MAX; }
static unsigned heap_caps_get_free_size(int cap) { assert(cap == MALLOC_CAP_EXEC); return UINT_MAX; }
static void httpd_resp_set_type(httpd_req_t *r, const char *v) { (void)r; assert(!strcmp(v, "application/json; charset=utf-8")); }
static void httpd_resp_set_hdr(httpd_req_t *r, const char *k, const char *v) { (void)r; assert(!strcmp(k,"Cache-Control") && !strcmp(v,"no-store")); }
#if YORADIO_ESP8266_OPUS_STREAM_TEST || YORADIO_ESP8266_SDK_RX_DIAG
static esp_err_t httpd_resp_send(httpd_req_t *r, const char *body, int size) {
    (void)r; assert(size >= 0 && (size_t)size < sizeof(captured));
    memcpy(captured, body, (size_t)size); captured[size] = 0; return send_result;
}
#endif
#if YORADIO_ESP8266_OPUS_STREAM_TEST
static int audio_service_stage_json(char *body, size_t size) {
    return snprintf(body, size, "{}");
}
#endif
static esp_err_t httpd_resp_send_500(httpd_req_t *r) {
    (void)r; ++server_errors; return -500;
}
static esp_err_t send_string(httpd_req_t *r, const char *body) {
    (void)r; assert(body == s_async_message); assert(strlen(body) < sizeof(captured));
    strcpy(captured, body); return send_result;
}
#include "health_under_test.inc"
int main(void) {
    httpd_req_t request = {.uri = "/api/native/audio"};
    assert(audio_health_handler(&request) == 0);
    assert(prepared == 1 && finished == 1);
    puts(captured);
    send_result = -17;
    assert(audio_health_handler(&request) == -17);
    assert(prepared == 2 && finished == 2);
    assert(server_errors == 0);
    return 0;
}
