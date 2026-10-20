#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "http_request_buffer.h"

enum { ESP_FAIL=-1, ESP_ERR_TIMEOUT=0x107, ESP_ERR_INVALID_STATE=0x103 };
#define MAX_HTTP_REDIRECTS 5
#define TAG "test-audio"
#define CHECK(label,condition) do { if (!(condition)) { \
    printf("SEMANTIC_FAILURE:%s:%d\n",label,__LINE__); exit(80); } } while(0)

typedef struct {
    uint32_t interval, bitrate_kbps;
    bool seen, valid;
} stream_headers_t;

typedef struct {
    int status, open_result, redirect_result;
    int64_t length, open_us, headers_us;
    bool invalid_headers;
    uint32_t interval, bitrate;
} response_t;

struct test_client {
    bool tx_live, async, pending_body, partial_headers;
    int release_result;
};

static response_t responses[6];
static stream_headers_t *live_headers;
static int64_t clock_us, deadline_us=10000;
static unsigned opens, fetches, statuses, redirects, closes, releases, debug_logs;
static unsigned stages, fetched_at, status_at;
static int timeouts[16];
static unsigned timeout_count;

static int64_t esp_timer_get_time(void) { return clock_us; }
static int esp_http_client_set_timeout_ms(esp_http_client_handle_t client, int ms) {
    (void)client; CHECK("timeout_capacity",timeout_count<16);
    timeouts[timeout_count++]=ms; return ESP_OK;
}
static int esp_http_client_open(esp_http_client_handle_t client, int length) {
    CHECK("get_has_no_request_body",length==0);
    CHECK("headers_reset_for_each_request",live_headers->valid && !live_headers->seen &&
          live_headers->interval==0 && live_headers->bitrate_kbps==0);
    CHECK("bounded_request_count",opens<6);
    response_t *response=&responses[opens++];
    ++stages; clock_us+=response->open_us;
    /* The sender's real lazy allocation is covered by the separate SDK suite. */
    client->tx_live=true;
    return response->open_result;
}
static int64_t esp_http_client_fetch_headers(esp_http_client_handle_t client) {
    CHECK("request_retained_until_fetch",client->tx_live);
    response_t *response=&responses[opens-1];
    ++fetches; fetched_at=++stages; clock_us+=response->headers_us;
    live_headers->valid=!response->invalid_headers;
    live_headers->seen=response->interval!=0;
    live_headers->interval=response->interval;
    live_headers->bitrate_kbps=response->bitrate;
    return response->length;
}
static int esp_http_client_get_status_code(esp_http_client_handle_t client) {
    CHECK("request_retained_until_status",client->tx_live);
    ++statuses; status_at=++stages;
    return responses[opens-1].status;
}
static int esp_http_client_set_redirection(esp_http_client_handle_t client) {
    CHECK("redirect_retains_request",client->tx_live);
    ++redirects; ++stages; return responses[opens-1].redirect_result;
}
static int esp_http_client_close(esp_http_client_handle_t client) {
    CHECK("redirect_close_retains_request",client->tx_live);
    ++closes; ++stages; return ESP_OK;
}
#ifdef CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE
esp_err_t yoradio_http_client_release_request_buffer(esp_http_client_handle_t client) {
    ++releases; unsigned released_at=++stages;
    CHECK("release_after_final_headers",fetches==opens && statuses==fetches &&
          fetched_at<status_at && status_at<released_at);
    CHECK("release_final_success_only",responses[opens-1].status>=200 &&
          responses[opens-1].status<300 && responses[opens-1].length>=0);
    CHECK("release_before_deadline",clock_us<deadline_us);
    CHECK("invalid_headers_retain_request",live_headers->valid);
    /* Explicit SDK seam: actual rejection guards execute in the SDK suite. */
    int result=client->async || client->pending_body || client->partial_headers
        ? ESP_ERR_INVALID_STATE : client->release_result;
    if (result==ESP_OK) client->tx_live=false;
    return result;
}
static const char *esp_err_to_name(int error) {
    CHECK("debug_only_for_rejected_release",error!=ESP_OK); return "rejected";
}
static void debug_log(const char *tag, const char *format, const char *error) {
    CHECK("rejection_debug_message",!strcmp(tag,TAG) &&
          !strcmp(format,"HTTP request buffer retained: %s") && !strcmp(error,"rejected"));
    ++debug_logs;
}
#define ESP_LOGD(tag,format,error) debug_log(tag,format,error)
#endif

#include "production.inc"

int main(int argc,char **argv) {
    CHECK("case_argument",argc==2);
    const char *name=argv[1];
    for (unsigned i=0;i<6;++i) responses[i]=(response_t){.status=200,.length=100};
    struct test_client client={.tx_live=true};
    stream_headers_t headers={.interval=999,.bitrate_kbps=888,.seen=true,.valid=false};
    live_headers=&headers;
    int expected=ESP_OK; unsigned expected_opens=1, expected_release=1;
    bool repeat=false;
    if (!strcmp(name,"success200")) {}
    else if (!strcmp(name,"success204")) responses[0].status=204;
    else if (!strcmp(name,"success299")) responses[0].status=299;
    else if (!strcmp(name,"zero-length")) responses[0].length=0;
    else if (!strcmp(name,"large-length")) responses[0].length=INT64_MAX;
    else if (!strncmp(name,"redirect",8) && strlen(name)==11) {
        responses[0].status=atoi(name+8);expected_opens=2;
    } else if (!strcmp(name,"five-redirects")) {
        for (unsigned i=0;i<5;++i) responses[i].status=302;
        expected_opens=6;
    } else if (!strcmp(name,"redirect-limit")) {
        for (unsigned i=0;i<6;++i) responses[i].status=301;
        expected_opens=6;expected=ESP_FAIL;expected_release=0;
    } else if (!strcmp(name,"redirect-rejected")) {
        responses[0].status=307;responses[0].redirect_result=0x123;
        expected=0x123;expected_release=0;
    } else if (!strcmp(name,"status199") || !strcmp(name,"status300") ||
               !strcmp(name,"status400") || !strcmp(name,"status500")) {
        responses[0].status=atoi(name+6);expected=ESP_FAIL;expected_release=0;
    } else if (!strcmp(name,"open-failed")) {
        responses[0].open_result=0x321;expected=0x321;expected_release=0;
    } else if (!strcmp(name,"fetch-failed")) {
        responses[0].length=-1;expected=ESP_FAIL;expected_release=0;
    } else if (!strcmp(name,"deadline-before")) {
        clock_us=deadline_us;expected=ESP_ERR_TIMEOUT;expected_opens=0;expected_release=0;
    } else if (!strcmp(name,"deadline-open")) {
        responses[0].open_us=deadline_us;expected=ESP_ERR_TIMEOUT;expected_release=0;
    } else if (!strcmp(name,"deadline-fetch") || !strcmp(name,"deadline-fetch-over")) {
        responses[0].headers_us=deadline_us+(!strcmp(name,"deadline-fetch-over"));
        expected=ESP_ERR_TIMEOUT;expected_release=0;
    } else if (!strcmp(name,"timeout-rounding")) {
        clock_us=1234;deadline_us=10001;responses[0].open_us=1001;
    } else if (!strcmp(name,"invalid-headers")) {
        responses[0].invalid_headers=true;expected_release=0;
    } else if (!strcmp(name,"rejected-state")) client.release_result=ESP_ERR_INVALID_STATE;
    else if (!strcmp(name,"async-rejected")) client.async=true;
    else if (!strcmp(name,"body-rejected")) client.pending_body=true;
    else if (!strcmp(name,"partial-rejected")) client.partial_headers=true;
    else if (!strcmp(name,"repeated-open")) repeat=true;
    else if (!strcmp(name,"metadata-reset")) {
        responses[0].status=302;responses[0].interval=123;responses[0].bitrate=64;
        responses[1].status=308;responses[1].interval=456;responses[1].bitrate=128;
        responses[2].interval=789;responses[2].bitrate=192;expected_opens=3;
    } else CHECK("known_case",false);
    int result=open_stream(&client,&headers,deadline_us);
    CHECK("release_rejection_preserves_success",result==expected);
    if (repeat) {
        result=open_stream(&client,&headers,deadline_us);
        CHECK("repeated_request_success",result==ESP_OK);
        expected_opens=2;expected_release=2;
    }
    CHECK("request_count_preserved",opens==expected_opens);
#ifdef CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE
    CHECK("accepted_get_release_count",releases==expected_release);
    bool rejected=client.release_result!=ESP_OK || client.async || client.pending_body || client.partial_headers;
    CHECK("rejected_release_keeps_request",client.tx_live==(expected_release==0 || rejected));
    CHECK("rejection_debug_only",debug_logs==(rejected ? expected_release : 0));
#else
    CHECK("disabled_no_release",releases==0 && client.tx_live && debug_logs==0);
    (void)expected_release;
#endif
    if (!strcmp(name,"metadata-reset"))
        CHECK("only_final_response_metadata",headers.interval==789 && headers.bitrate_kbps==192);
    if (!strcmp(name,"timeout-rounding"))
        CHECK("existing_timeout_rounding",timeout_count==2 && timeouts[0]==9 && timeouts[1]==8);
    /* This externally visible trace must be identical with the option off/on. */
    printf("PASS:%s result=%d opens=%u fetches=%u statuses=%u redirects=%u closes=%u "
           "timeouts=%u first_timeout=%d last_timeout=%d now=%lld interval=%u bitrate=%u valid=%d seen=%d\n",
           name,result,opens,fetches,statuses,redirects,closes,timeout_count,
           timeout_count?timeouts[0]:0,timeout_count?timeouts[timeout_count-1]:0,
           (long long)clock_us,headers.interval,headers.bitrate_kbps,headers.valid,headers.seen);
    return 0;
}
