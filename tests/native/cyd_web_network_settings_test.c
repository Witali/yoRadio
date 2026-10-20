#include "platform.h"
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
static char response[1024], status[48], content_type[64];
static unsigned sends, close_calls, snapshots;
static bool close_header, no_store, graceful, query_error;
static esp_err_t runtime_error, send_error;
static unsigned response_operation, fail_response_operation;
static network_snapshot_t service_snapshot;
static esp_err_t response_result(void) {
    return ++response_operation == fail_response_operation ? ESP_FAIL : ESP_OK;
}
static esp_err_t httpd_resp_set_status(httpd_req_t *r, const char *s) {
    CHECK(r, "response_request"); strcpy(status, s); return response_result();
}
static esp_err_t httpd_resp_set_type(httpd_req_t *r, const char *s) {
    CHECK(r, "response_request"); strcpy(content_type, s); return response_result();
}
static esp_err_t httpd_resp_set_hdr(httpd_req_t *r, const char *k, const char *v) {
    CHECK(r, "response_request");
    if (!strcmp(k, "Connection")) { CHECK(!strcmp(v, "close"), "body_close_header"); close_header = true; }
    else { CHECK(!strcmp(k, "Cache-Control") && !strcmp(v, "no-store"), "response_no_store"); no_store = true; }
    return response_result();
}
static esp_err_t httpd_resp_sendstr(httpd_req_t *r, const char *s) {
    CHECK(r && strlen(s) < sizeof(response), "response_bounded");
    strcpy(response, s); sends++; return send_error;
}
static int httpd_req_to_sockfd(httpd_req_t *r) { CHECK(r, "response_request"); return 27; }
static void native_web_transport_prepare_close(void *h, int fd, bool clean) {
    CHECK(h == (void *)42 && fd == 27, "body_transport_close"); close_calls++; graceful = clean;
}
static size_t httpd_req_get_url_query_len(httpd_req_t *r) {
    return r->advertised ? r->advertised : r->query ? strlen(r->query) : 0;
}
static esp_err_t httpd_req_get_url_query_str(httpd_req_t *r, char *out, size_t cap) {
    if (query_error || !r->query || strlen(r->query) >= cap) return ESP_FAIL;
    strcpy(out, r->query); return ESP_OK;
}
esp_err_t network_service_snapshot(network_snapshot_t *out, uint32_t timeout_ms) {
    CHECK(timeout_ms == 25U, "runtime_snapshot_bounded"); snapshots++;
    if (runtime_error) return runtime_error;
    *out = service_snapshot; return ESP_OK;
}
#include "web-network-settings.inc"

static void reset(void) {
    response[0] = status[0] = content_type[0] = 0;
    close_header = no_store = graceful = query_error = false;
    close_calls = sends = response_operation = fail_response_operation = 0;
    send_error = ESP_OK;
}
static const char *valid = "hostname=Radio-1&ap_timeout_minutes=15";
static esp_err_t post(const char *query) {
    reset(); httpd_req_t r = {.handle=(void *)42,.method=HTTP_POST,.query=query};
    return web_network_settings_edit_handler(&r);
}
static void unchanged(const network_settings_t *old, uint32_t revision) {
    network_settings_t now; uint32_t after;
    CHECK(network_settings_snapshot(&now, &after), "desired_snapshot_available");
    CHECK(after == revision && !memcmp(old, &now, sizeof(now)), "failed_request_never_publishes");
}
static void json_response(void) {
    CHECK(!strcmp(content_type, "application/json; charset=utf-8") && no_store, "json_no_store");
    CHECK(strlen(response) < 768U, "json_capacity_768");
    printf("JSON %s\n", response);
}
int main(int argc, char **argv) {
    CHECK(argc == 2, "fixture_case"); const char *test = argv[1]; unsigned checks = 0;
    if (strcmp(test, "uninitialized")) CHECK(network_settings_init() == ESP_OK, "settings_init");
    httpd_req_t get = {.handle=(void *)42,.method=HTTP_GET};
    if (!strcmp(test, "get")) {
        CHECK(web_network_settings_info_handler(&get) == ESP_OK && !strcmp(status,"200 OK"), "desired_get");
        CHECK(strstr(response,"\"hostname\":\"yoradio\"") && strstr(response,"\"ap_timeout_minutes\":0") &&
              strstr(response,"\"configured_hostname\":null") && strstr(response,"\"hostname_pending\":true"), "unconfigured_is_pending");
        json_response(); checks++;
        strcpy(service_snapshot.settings.configured_hostname,"yoradio");
        service_snapshot.settings.hostname_valid = true; service_snapshot.settings.hostname_revision = 1;
        reset(); CHECK(web_network_settings_info_handler(&get) == ESP_OK, "configured_get");
        CHECK(strstr(response,"\"hostname_pending\":false"), "matching_hostname_is_configured");
        json_response(); checks++;
        CHECK(post("hostname=yoradio&ap_timeout_minutes=30") == ESP_OK, "timeout_only_save");
        reset(); CHECK(web_network_settings_info_handler(&get) == ESP_OK, "timeout_only_get");
        CHECK(strstr(response,"\"desired_revision\":2") && strstr(response,"\"hostname_revision\":1") &&
              strstr(response,"\"hostname_pending\":false"), "timeout_revision_does_not_unapply_hostname");
        json_response(); checks++;
        CHECK(post(valid) == ESP_OK, "changed_hostname_save"); service_snapshot.settings.hostname_revision = 3;
        reset(); CHECK(web_network_settings_info_handler(&get) == ESP_OK, "changed_hostname_get");
        CHECK(strstr(response,"\"hostname_pending\":true") && strstr(response,"\"configured_hostname\":\"yoradio\""),
              "compare_actual_hostname_not_revision"); json_response(); checks++;
        runtime_error = ESP_ERR_TIMEOUT; reset();
        CHECK(web_network_settings_info_handler(&get) == ESP_OK && !strcmp(status,"200 OK"), "runtime_failure_keeps_desired");
        CHECK(strstr(response,"\"runtime_available\":false") && strstr(response,"\"hostname\":\"Radio-1\"") &&
              strstr(response,"\"configured_hostname\":null") && strstr(response,"\"hostname_pending\":true") &&
              strstr(response,"\"hostname_revision\":null") && strstr(response,"\"last_hostname_error\":null") &&
              strstr(response,"\"ap_timeout_armed\":null") && strstr(response,"\"ap_timeout_remaining_ms\":null"), "unknown_runtime_is_explicit");
        json_response(); checks++;
        runtime_error = ESP_OK; service_snapshot.settings.hostname_valid = false;
        service_snapshot.settings.hostname_error = ESP_ERR_NO_MEM; reset();
        CHECK(web_network_settings_info_handler(&get) == ESP_OK, "failed_hostname_get");
        CHECK(strstr(response,"\"configured_hostname\":null") && strstr(response,"\"hostname_pending\":true") &&
              strstr(response,"\"last_hostname_error\":257"), "hostname_failure_not_applied"); json_response(); checks++;
    } else if (!strcmp(test,"valid")) {
        const char *good[] = {valid,"ap_timeout_minutes=0&hostname=a","hostname=Z&ap_timeout_minutes=30",
            "host%6Eame=Radio%2d2&ap_timeout_minutes=%31%30", "hostname=ABCDEFGHIJKLMNOPQRSTUVW&ap_timeout_minutes=1"};
        network_settings_t now; uint32_t revision;
        for (unsigned i=0;i<sizeof(good)/sizeof(*good);i++) {
            CHECK(post(good[i]) == ESP_OK && !strcmp(status,"200 OK"), "valid_complete_save");
            CHECK(!strcmp(response,"{\"saved\":true,\"application_pending\":true,\"rebooting\":false}"), "persistence_not_application");
            CHECK(network_settings_snapshot(&now,&revision) && revision == i+2U && network_settings_valid(&now), "complete_save_advances_revision");
            CHECK(atomic_load(&nvs_commits) == i+1U && !snapshots, "http_save_only_persists"); checks++;
        }
        json_response();
    } else if (!strcmp(test,"invalid")) {
        network_settings_t before; uint32_t revision; CHECK(network_settings_snapshot(&before,&revision), "desired_snapshot_available");
        const char *bad[] = {"", "hostname=x", "ap_timeout_minutes=0", "hostname=x&ap_timeout_minutes=0&extra=x",
            "hostname=x&ap_timeout_minutes=0&hostname=y", "hostname=x&ap_timeout_minutes=0&host%6eame=y",
            "hostname=x&ap_timeout_minutes=0&ap_timeout_%6dinutes=1", "hostname=x&ap_timeout_minutes=0&",
            "hostname=x&&ap_timeout_minutes=0", "hostname=x&ap_timeout_minutes", "=x&ap_timeout_minutes=0",
            "hostname=&ap_timeout_minutes=0", "hostname=a.b&ap_timeout_minutes=0", "hostname=-a&ap_timeout_minutes=0",
            "hostname=a-&ap_timeout_minutes=0", "hostname=a_b&ap_timeout_minutes=0", "hostname=a+b&ap_timeout_minutes=0",
            "hostname=a%00b&ap_timeout_minutes=0", "hostname=a%0Ab&ap_timeout_minutes=0", "hostname=a%7Fb&ap_timeout_minutes=0",
            "hostname=a%&ap_timeout_minutes=0", "hostname=a%2&ap_timeout_minutes=0", "hostname=a%GG&ap_timeout_minutes=0",
            "hostname=%D0%B0&ap_timeout_minutes=0", "hostname=a=b&ap_timeout_minutes=0", "hostname=a%252Db&ap_timeout_minutes=0",
            "hostname=abcdefghijklmnopqrstuvwx&ap_timeout_minutes=0", "hostname=a&ap_timeout_minutes=",
            "hostname=a&ap_timeout_minutes=31", "hostname=a&ap_timeout_minutes=-1", "hostname=a&ap_timeout_minutes=+1",
            "hostname=a&ap_timeout_minutes=%2B1", "hostname=a&ap_timeout_minutes=01", "hostname=a&ap_timeout_minutes=00",
            "hostname=a&ap_timeout_minutes=1.0", "hostname=a&ap_timeout_minutes=1e1", "hostname=a&ap_timeout_minutes=1%20",
            "hostname=a&ap_timeout_minutes=99999999999999999999999", "hostname=a&ap_timeout_minutes=256",
            "host%00name=a&ap_timeout_minutes=0"};
        for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++) {
            CHECK(post(bad[i]) == ESP_OK && !strcmp(status,"400 Bad Request"), "strict_query_rejected");
            CHECK(!atomic_load(&nvs_sets) && !atomic_load(&nvs_commits), "invalid_query_never_persists"); unchanged(&before,revision); checks++;
        }
    } else if (!strcmp(test,"body")) {
        for(unsigned method=HTTP_GET;method<=HTTP_POST;method++) {
            reset(); httpd_req_t r = {.handle=(void *)42,.method=(int)method,.content_len=SIZE_MAX,.query=valid};
            esp_err_t result = method == HTTP_GET ? web_network_settings_info_handler(&r) : web_network_settings_edit_handler(&r);
            CHECK(result == ESP_FAIL && close_calls == 1 && close_header && graceful, "body_never_enters_sdk_purge");
            CHECK(!snapshots && !atomic_load(&nvs_sets) && !strcmp(status,"400 Bad Request"), "body_no_side_effect"); checks++;
            reset(); send_error = ESP_FAIL;
            result = method == HTTP_GET ? web_network_settings_info_handler(&r) : web_network_settings_edit_handler(&r);
            CHECK(result == ESP_FAIL && close_calls == 1 && !graceful, "body_failed_reply_aborts_transport"); checks++;
        }
    } else if (!strcmp(test,"boundaries")) {
        httpd_req_t r={.handle=(void *)42,.method=HTTP_POST,.query=valid,.advertised=193};
        CHECK(web_network_settings_edit_handler(&r)==ESP_OK && !strcmp(status,"400 Bad Request"), "query_limit_192"); checks++;
        r.advertised=192; reset(); CHECK(web_network_settings_edit_handler(&r)==ESP_OK && !strcmp(status,"400 Bad Request"), "query_length_must_match"); checks++;
        r.advertised=0; reset(); query_error=true; CHECK(web_network_settings_edit_handler(&r)==ESP_OK && !strcmp(status,"400 Bad Request"), "query_read_failure"); checks++;
        reset(); r.method=HTTP_GET; CHECK(web_network_settings_info_handler(&r)==ESP_OK && !snapshots, "get_has_no_query"); checks++;
        reset(); r.query=NULL; CHECK(web_network_settings_edit_handler(&r)==ESP_OK && !strcmp(status,"400 Bad Request"), "post_method_required"); checks++;
        CHECK(web_network_settings_info_handler(NULL)==ESP_FAIL && web_network_settings_edit_handler(NULL)==ESP_FAIL, "null_request"); checks++;
        char maximum[193]; size_t length=0; const char *encoded[]={"hostname","ABCDEFGHIJKLMNOPQRSTUVW","ap_timeout_minutes","30"};
        for(unsigned part=0;part<4;part++) {
            for(const unsigned char *at=(const unsigned char *)encoded[part];*at;at++) length+=(size_t)sprintf(maximum+length,"%%%02X",*at);
            if(part<3)maximum[length++]=part==1?'&':'=';
        }
        maximum[length]=0; CHECK(length==156U, "max_encoded_valid_query_156");
        CHECK(post(maximum)==ESP_OK && !strcmp(status,"200 OK"), "encoded_maximum_accepted"); checks++;
        portENTER_CRITICAL(&s_snapshot_lock); s_revision=UINT32_MAX; portEXIT_CRITICAL(&s_snapshot_lock);
        strcpy(service_snapshot.settings.configured_hostname,"ABCDEFGHIJKLMNOPQRSTUVW");
        service_snapshot.settings.hostname_valid=true; service_snapshot.settings.hostname_revision=UINT32_MAX;
        service_snapshot.settings.hostname_error=INT32_MIN; service_snapshot.settings.ap_timeout_armed=true;
        service_snapshot.settings.ap_timeout_remaining_ms=UINT64_MAX; reset();
        CHECK(web_network_settings_info_handler(&get)==ESP_OK && !strcmp(status,"200 OK"), "maximum_json_fields_fit");
        json_response(); checks++;
    } else if (!strcmp(test,"save_errors")) {
        network_settings_t before; uint32_t revision; CHECK(network_settings_snapshot(&before,&revision), "desired_snapshot_available");
        esp_err_t errors[]={ESP_FAIL,ESP_ERR_NO_MEM,ESP_ERR_TIMEOUT,ESP_ERR_INVALID_STATE,ESP_ERR_INVALID_ARG};
        for(unsigned i=0;i<sizeof(errors)/sizeof(*errors);i++) {
            fail_open=errors[i]; CHECK(post(valid)==ESP_OK, "save_error_reply");
            CHECK(!strcmp(status,i==0?"500 Internal Server Error":i==4?"400 Bad Request":"503 Service Unavailable"), "honest_store_status");
            CHECK(!strstr(response,"\"saved\":true"), "failed_storage_never_saved"); unchanged(&before,revision);checks++;
        }
        fail_open=ESP_OK;esp_err_t *faults[]={&fail_set,&fail_commit};
        for(unsigned i=0;i<2;i++) { *faults[i]=ESP_FAIL;CHECK(post(valid)==ESP_OK && !strcmp(status,"500 Internal Server Error"), "failed_storage_never_saved");*faults[i]=ESP_OK;unchanged(&before,revision);checks++; }
        atomic_store(&forced_timeout,atomic_load(&s_write_lock));
        CHECK(post(valid)==ESP_OK && !strcmp(status,"503 Service Unavailable"), "finite_writer_admission_failure");
        atomic_store(&forced_timeout,NULL);unchanged(&before,revision);checks++;
        portENTER_CRITICAL(&s_snapshot_lock);s_revision=UINT32_MAX;portEXIT_CRITICAL(&s_snapshot_lock);
        CHECK(post(valid)==ESP_OK && !strcmp(status,"503 Service Unavailable"), "revision_exhaustion_unavailable"); checks++;
    } else if (!strcmp(test,"uninitialized")) {
        CHECK(web_network_settings_info_handler(&get)==ESP_OK && !strcmp(status,"503 Service Unavailable") && !snapshots, "store_unavailable_not_runtime_default"); checks++;
        CHECK(post(valid)==ESP_OK && !strcmp(status,"503 Service Unavailable") && !atomic_load(&nvs_sets), "uninitialized_post_unavailable"); checks++;
        atomic_store(&fail_mutex,true); vSemaphoreDelete(atomic_exchange(&s_write_lock,NULL));
        CHECK(post(valid)==ESP_OK && !strcmp(status,"503 Service Unavailable"), "writer_oom_unavailable"); checks++;
    } else if (!strcmp(test,"response_errors")) {
        for(unsigned i=1;i<=3;i++) {reset();fail_response_operation=i;CHECK(web_network_settings_info_handler(&get)==ESP_FAIL && !sends, "response_header_failure");checks++;}
        reset();send_error=ESP_FAIL;CHECK(web_network_settings_info_handler(&get)==ESP_FAIL && sends==1, "response_send_failure");checks++;
        reset();httpd_req_t p={.handle=(void *)42,.method=HTTP_POST,.query=valid};send_error=ESP_FAIL;
        CHECK(web_network_settings_edit_handler(&p)==ESP_FAIL && atomic_load(&nvs_commits)==1, "durable_save_survives_reply_failure");checks++;
    } else CHECK(false,"known_case");
    cleanup_semaphores(); printf("PASS %s: %u checks\n",test,checks);return 0;
}
