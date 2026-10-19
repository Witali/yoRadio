#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "network_status.h"

#define HTTPD_400_BAD_REQUEST 400
#define HTTPD_500_INTERNAL_SERVER_ERROR 500
typedef struct { size_t content_len; } httpd_req_t;
static network_snapshot_t view;
static esp_err_t snapshot_result, retry_result;
static unsigned snapshot_calls, retry_calls, cases;
static int status;
static bool no_store, json_type;
static char response[1024];
esp_err_t network_service_snapshot(network_snapshot_t *out, uint32_t timeout) {
    assert(timeout == 100); ++snapshot_calls;
    if (snapshot_result == ESP_OK) *out = view;
    return snapshot_result;
}
static esp_err_t network_service_retry_client(void) { ++retry_calls; return retry_result; }
static esp_err_t httpd_resp_set_type(httpd_req_t *r, const char *type) {
    (void)r; json_type = strstr(type, "application/json") != NULL; return ESP_OK;
}
static esp_err_t httpd_resp_set_status(httpd_req_t *r, const char *value) {
    (void)r; assert(sscanf(value, "%d", &status) == 1); return ESP_OK;
}
static esp_err_t httpd_resp_set_hdr(httpd_req_t *r, const char *key, const char *value) {
    (void)r; assert(!strcmp(key, "Cache-Control")); no_store = !strcmp(value, "no-store"); return ESP_OK;
}
static esp_err_t httpd_resp_sendstr(httpd_req_t *r, const char *body) {
    (void)r; assert(strlen(body) < sizeof(response)); strcpy(response, body); return ESP_OK;
}
static esp_err_t httpd_resp_send_err(httpd_req_t *r, int error, const char *body) {
    status = error; return httpd_resp_sendstr(r, body);
}
#include "production.inc"

static void reset(void) {
    status = 200; no_store = json_type = false; response[0] = 0;
    snapshot_calls = retry_calls = 0; snapshot_result = retry_result = ESP_OK; ++cases;
}
int main(void) {
    httpd_req_t request = {0};
    for (unsigned phase = NETWORK_WAIT_START; phase <= NETWORK_AP_IDLE; ++phase) {
        reset(); view = (network_snapshot_t){.phase=phase,.profile_index=NETWORK_NO_PROFILE,
            .target_profile=NETWORK_NO_PROFILE,.rssi_valid=false,
            .power={.generation=phase,.desired_active=phase % 2 != 0,
                .applied_active=phase % 2 == 0,.applied_valid=true,.last_error=ESP_FAIL}};
        assert(network_handler(&request) == ESP_OK && status == 200 && no_store && json_type);
        assert(snapshot_calls == 1 && !retry_calls && strstr(response, "\"rssi_valid\":false"));
        assert(!strstr(response,"password") && !strstr(response,"ssid"));
        printf("JSON=%s\n", response);
    }
    reset(); view = (network_snapshot_t){.phase=(network_phase_t)INT_MAX,
        .epoch=UINT32_MAX,.event_overflows=UINT32_MAX,.profile_count=UINT8_MAX,
        .profile_index=UINT8_MAX,.target_profile=UINT8_MAX,.attempt=UINT8_MAX,
        .profiles_tried=UINT8_MAX,.online=true,.ap_enabled=true,.rssi_valid=true,
        .reconciling=true,.rssi=INT8_MIN,.disconnect_reason=UINT16_MAX,.ipv4=UINT32_MAX,
        .last_error=INT_MIN,.rssi_age_ms=UINT64_MAX,
        .power={.generation=UINT32_MAX,.desired_revision=UINT32_MAX,.applied_revision=UINT32_MAX,
            .desired_active=false,.applied_active=false,.applied_valid=false,.attempts=UINT8_MAX,.last_error=INT_MIN}};
    assert(network_handler(&request) == ESP_OK && status == 200 && no_store && json_type);
    assert(strstr(response,"\"power\":{") && strstr(response,"\"attempts\":255") &&
        strstr(response,"\"desired_revision\":4294967295") && strstr(response,"\"applied_valid\":false"));
    assert(strstr(response,"\"phase\":\"unknown\"")); printf("JSON_MAX=%s\n",response);
    reset(); snapshot_result=ESP_ERR_TIMEOUT;
    assert(network_handler(&request)==ESP_OK && status==503 && no_store && snapshot_calls==1);
    assert(strstr(response,"network_unavailable"));
    reset(); request.content_len=1;
    assert(network_handler(&request)==ESP_FAIL && status==400 && !snapshot_calls);
    reset(); request.content_len=SIZE_MAX;
    assert(network_handler(&request)==ESP_FAIL && status==400 && !snapshot_calls);
    reset(); request.content_len=1;
    assert(reconnect_handler(&request)==ESP_FAIL && status==400 && !retry_calls);
    request.content_len=0;
    reset(); assert(reconnect_handler(&request)==ESP_OK && status==200 && retry_calls==1 && no_store && json_type);
    assert(strstr(response,"\"accepted\":true") && !strstr(response,"connected\":true"));
    const esp_err_t errors[]={ESP_ERR_NOT_FOUND,ESP_ERR_TIMEOUT,ESP_ERR_INVALID_STATE,ESP_FAIL};
    const int statuses[]={400,409,503,503};
    const char *messages[]={"no_active_profiles","retry_pending","network_unavailable","network_unavailable"};
    for(unsigned i=0;i<sizeof(errors)/sizeof(errors[0]);++i) {
        reset();retry_result=errors[i];assert(reconnect_handler(&request)==ESP_OK);
        assert(status==statuses[i] && no_store && json_type && retry_calls==1 && strstr(response,messages[i]));
    }
    printf("PASS network HTTP: %u actual handler cases, bounded status, body close, admission/error mapping\n",cases);
    return 0;
}
