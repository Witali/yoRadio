#include "cyd_time_platform.h"
#include "headers.inc"
#include "settings.inc"
#include "json_buffer.h"

enum { HTTP_GET = 1, HTTP_POST = 2 };
typedef struct {
    void *handle;
    int method;
    size_t content_len;
    const char *query;
    size_t advertised;
} httpd_req_t;
static char response[2048], status[48], content_type[64];
static unsigned saves, snapshots, sends, close_calls;
static bool close_header, no_store, graceful, snapshot_available = true;
static esp_err_t save_error, send_error;
static unsigned response_operation, fail_response_operation;
static bool query_error;
static time_snapshot_t service_snapshot;
static esp_err_t response_result(void) {
    return ++response_operation == fail_response_operation ? ESP_FAIL : ESP_OK;
}
static esp_err_t httpd_resp_set_status(httpd_req_t *r, const char *s) {
    assert(r); strcpy(status, s); return response_result();
}
static esp_err_t httpd_resp_set_type(httpd_req_t *r, const char *s) {
    assert(r); strcpy(content_type, s); return response_result();
}
static esp_err_t httpd_resp_set_hdr(httpd_req_t *r, const char *k, const char *v) {
    assert(r);
    if (!strcmp(k, "Connection")) { assert(!strcmp(v, "close")); close_header = true; }
    else { assert(!strcmp(k, "Cache-Control") && !strcmp(v, "no-store")); no_store = true; }
    return response_result();
}
static esp_err_t httpd_resp_sendstr(httpd_req_t *r, const char *s) {
    assert(r && strlen(s) < sizeof(response)); strcpy(response, s); sends++; return send_error;
}
static int httpd_req_to_sockfd(httpd_req_t *r) { assert(r); return 27; }
static void native_web_transport_prepare_close(void *h, int fd, bool clean) {
    assert(h == (void *)42 && fd == 27); close_calls++; graceful = clean;
}
static size_t httpd_req_get_url_query_len(httpd_req_t *r) {
    return r->advertised ? r->advertised : r->query ? strlen(r->query) : 0;
}
static esp_err_t httpd_req_get_url_query_str(httpd_req_t *r, char *out, size_t cap) {
    if (query_error || !r->query || strlen(r->query) >= cap) return ESP_FAIL;
    strcpy(out, r->query); return ESP_OK;
}
bool time_service_snapshot(time_snapshot_t *out) {
    snapshots++;
    if (!snapshot_available) return false;
    *out = service_snapshot;
    assert(time_settings_snapshot(&out->settings, &out->desired_revision));
    return true;
}
esp_err_t time_service_save_settings(const time_settings_t *settings) {
    saves++;
    return save_error ? save_error : time_settings_save(settings);
}
#include "web_time.inc"

static void reset(void) {
    response[0] = status[0] = content_type[0] = 0;
    close_header = no_store = graceful = false;
    close_calls = sends = response_operation = fail_response_operation = 0;
    query_error = false; send_error = ESP_OK;
}
static esp_err_t post(const char *query) {
    reset(); httpd_req_t r = {.handle=(void *)42,.method=HTTP_POST,.query=query};
    return web_time_edit_handler(&r);
}
static void unchanged(const time_settings_t *old, uint32_t revision) {
    time_settings_t now; uint32_t after;
    assert(time_settings_snapshot(&now, &after));
    assert(after == revision && !memcmp(old, &now, sizeof(now)));
}
static const char *valid = "utc_offset_minutes=-30&sync_interval_minutes=60&server1=pool.ntp.org&server2=time.nist.gov";

int main(int argc, char **argv) {
    assert(argc == 2 && time_settings_init() == ESP_OK);
    service_snapshot.available = true;
    service_snapshot.last_sync_age_ms = -1;
    const char *test = argv[1]; unsigned checks = 0;
    if (!strcmp(test, "get")) {
        httpd_req_t r = {.handle=(void *)42,.method=HTTP_GET};
        assert(web_time_info_handler(&r) == ESP_OK);
        assert(strstr(response, "\"clock_valid\":false") && strstr(response, "\"utc_epoch\":null") &&
               strstr(response, "\"local_time\":null") && strstr(response, "\"last_sync_age_ms\":null"));
        assert(strstr(response, "\"server1\":\"pool.ntp.org\"") && no_store);
        printf("JSON %s\n", response); checks++;
        service_snapshot.clock_valid = service_snapshot.network_ready = true;
        service_snapshot.synchronized_this_boot = true;
        service_snapshot.utc_epoch = INT64_C(1704067200);
        service_snapshot.last_sync_epoch = INT64_C(1704067100);
        service_snapshot.last_sync_age_ms = INT64_C(1234567890123);
        service_snapshot.applied_revision = 1;
        service_snapshot.last_apply_error = ESP_ERR_TIMEOUT;
        service_snapshot.local_time = (struct tm){.tm_year=123,.tm_mon=11,.tm_mday=31,.tm_hour=23,.tm_min=30};
        reset(); assert(web_time_info_handler(&r) == ESP_OK);
        assert(strstr(response, "\"local_time\":\"2023-12-31T23:30:00\"") &&
               strstr(response, "\"last_sync_age_ms\":1234567890123") &&
               strstr(response, "\"last_apply_error\":263"));
        printf("JSON %s\n", response); checks++;
        snapshot_available = false; reset();
        assert(web_time_info_handler(&r) == ESP_OK && !strcmp(status,"503 Service Unavailable")); checks++;
    } else if (!strcmp(test, "valid")) {
        assert(post(valid) == ESP_OK && !strcmp(status,"200 OK") && saves == 1 && nvs_commits == 1);
        assert(!strcmp(response,"{\"saved\":true,\"application_pending\":true}"));
        time_settings_t now; uint32_t revision;
        assert(time_settings_snapshot(&now,&revision) && revision == 2 && now.utc_offset_minutes == -30); checks++;
        const char *good[] = {
            "server2=&server1=255.255.255.255&sync_interval_minutes=15&utc_offset_minutes=-720",
            "utc_offset_minutes=840&sync_interval_minutes=1440&server1=a&server2=B-2.example",
            "utc%5foffset_minutes=%2D30&sync_interval_minutes=60&server1=pool%2Entp.org&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&server2="};
        for (unsigned i=0;i<sizeof(good)/sizeof(*good);i++) {
            assert(post(good[i]) == ESP_OK && !strcmp(status,"200 OK"));
            assert(time_settings_snapshot(&now,&revision) && time_settings_valid(&now)); checks++;
        }
        assert(now.server_count == 1 && !now.servers[1][0]);
        printf("JSON %s\n", response);
    } else if (!strcmp(test, "invalid")) {
        time_settings_t before; uint32_t revision;
        assert(time_settings_snapshot(&before,&revision));
        const char *bad[] = {
            "", "utc_offset_minutes=0", "utc_offset_minutes=0&sync_interval_minutes=60&server1=a",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a&server2=&extra=x",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a&server2=&server1=b",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a&server2=&server%31=b",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a&server2=&",
            "utc_offset_minutes=0&&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a&server2",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a%00b&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a%0Ab&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a%7Fb&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a%&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a%2&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a%GG&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a+b&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a%252Eb&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a=b&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=https%3A%2F%2Fa&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=%D0%B0&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=01.2.3.4&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60&server1=a&server2=a..b",
            "utc_offset_minutes=-735&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=855&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=1&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=+30&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=%2B30&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=030&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=-&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=999999999999999999999999&sync_interval_minutes=60&server1=a&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=-60&server1=a&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=14&server1=a&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=1441&server1=a&server2=",
            "utc_offset_minutes=0&sync_interval_minutes=60.0&server1=a&server2="};
        for (unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++) {
            assert(post(bad[i]) == ESP_OK && !strcmp(status,"400 Bad Request"));
            assert(!saves && !nvs_commits); unchanged(&before,revision); checks++;
        }
    } else if (!strcmp(test, "body")) {
        for (unsigned method=HTTP_GET;method<=HTTP_POST;method++) {
            reset(); httpd_req_t r = {.handle=(void *)42,.method=(int)method,.content_len=SIZE_MAX,.query=valid};
            esp_err_t result = method == HTTP_GET ? web_time_info_handler(&r) : web_time_edit_handler(&r);
            assert(result == ESP_FAIL && close_calls == 1 && close_header && graceful);
            assert(!saves && !snapshots && !strcmp(status,"400 Bad Request")); checks++;
            reset(); send_error = ESP_FAIL;
            result = method == HTTP_GET ? web_time_info_handler(&r) : web_time_edit_handler(&r);
            assert(result == ESP_FAIL && close_calls == 1 && !graceful); checks++;
        }
    } else if (!strcmp(test, "boundaries")) {
        httpd_req_t r = {.handle=(void *)42,.method=HTTP_POST,.query=valid,.advertised=513};
        assert(web_time_edit_handler(&r)==ESP_OK && !strcmp(status,"400 Bad Request") && !saves); checks++;
        r.advertised=512; reset(); assert(web_time_edit_handler(&r)==ESP_OK && !saves); checks++;
        r.advertised=0; query_error=true; assert(web_time_edit_handler(&r)==ESP_OK && !saves); checks++;
        reset(); r.method=HTTP_GET; assert(web_time_info_handler(&r)==ESP_OK && !snapshots); checks++;
        reset(); r.query=NULL; assert(web_time_edit_handler(&r)==ESP_OK && !saves); checks++;
        assert(web_time_edit_handler(NULL)==ESP_FAIL && web_time_info_handler(NULL)==ESP_FAIL); checks++;
        char long_query[514]; memset(long_query,'x',513);long_query[513]=0;r.method=HTTP_POST;r.query=long_query;
        assert(web_time_edit_handler(&r)==ESP_OK && !saves); checks++;
    } else if (!strcmp(test, "save_errors")) {
        time_settings_t before;uint32_t revision;assert(time_settings_snapshot(&before,&revision));
        esp_err_t errors[]={ESP_ERR_TIMEOUT,ESP_ERR_INVALID_STATE,ESP_ERR_NO_MEM,ESP_ERR_INVALID_ARG,ESP_FAIL};
        for(unsigned i=0;i<sizeof(errors)/sizeof(*errors);i++){
            save_error=errors[i]; assert(post(valid)==ESP_OK);
            assert(strcmp(status,"200 OK"));
            assert(!strcmp(status,i<3?"503 Service Unavailable":i==3?"400 Bad Request":"500 Internal Server Error"));
            assert(!strstr(response,"\"saved\":true")); unchanged(&before,revision);checks++;
        }
        save_error=0;unsigned *faults[]={&fail_nvs_open,&fail_nvs_set,&fail_nvs_commit};
        for(unsigned i=0;i<3;i++){*faults[i]=1;assert(post(valid)==ESP_OK && !strcmp(status,"500 Internal Server Error"));*faults[i]=0;unchanged(&before,revision);checks++;}
        forced_timeout=atomic_load(&s_write_lock);assert(post(valid)==ESP_OK && !strcmp(status,"503 Service Unavailable"));forced_timeout=NULL;unchanged(&before,revision);checks++;
    } else if (!strcmp(test, "response_errors")) {
        httpd_req_t r={.handle=(void *)42,.method=HTTP_GET};
        for(unsigned i=1;i<=3;i++){reset();fail_response_operation=i;assert(web_time_info_handler(&r)==ESP_FAIL && !sends);checks++;}
        reset();send_error=ESP_FAIL;assert(web_time_info_handler(&r)==ESP_FAIL && sends==1);checks++;
        reset();httpd_req_t p={.handle=(void *)42,.method=HTTP_POST,.query=valid};send_error=ESP_FAIL;
        assert(web_time_edit_handler(&p)==ESP_FAIL && nvs_commits==1);checks++;
    } else assert(!"unknown case");
    cleanup_sems(); printf("PASS %s: %u checks\n",test,checks); return 0;
}
