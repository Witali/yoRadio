#include <assert.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "json_buffer.h"
typedef int esp_err_t;
typedef void *httpd_handle_t;
typedef struct { void *lock; bool web_ready; } native_state_t;
typedef struct { int unused; } httpd_req_t;
typedef struct { const char *uri; int method; int (*handler)(httpd_req_t *); } httpd_uri_t;
typedef struct { unsigned stack_size,max_open_sockets,send_wait_timeout,max_uri_handlers;
                 bool lru_purge_enable;void *uri_match_fn; } httpd_config_t;
enum { ESP_OK=0,ESP_ERR_INVALID_ARG=-1,ESP_ERR_INVALID_STATE=-2,ESP_FAIL=-3,
       HTTP_GET=0,HTTP_POST=1,HTTPD_500_INTERNAL_SERVER_ERROR=500 };
#define HTTPD_DEFAULT_CONFIG() ((httpd_config_t){0})
#define CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS 1
#define pdMS_TO_TICKS(x) (x)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
static void *httpd_uri_match_wildcard=(void *)1;
static unsigned allocations, aborted, activated, server_live, route_calls, fail_route;
static unsigned ws_registered,ws_running,stop_calls,server_stopped,server_resets;
static int fail_static,fail_server,fail_ws_register,fail_ws_start,fail_ws_stop,fail_server_stop;
static int fail_storage,fail_reboot,fail_reboot_abort;
static bool storage_ready,reboot_ready,upload_active,ota_active,wifi_active;
static unsigned wifi_get_routes,wifi_post_routes,time_get_routes,time_post_routes;
static unsigned network_settings_get_routes,network_settings_post_routes;
static unsigned reboot_aborted;
static int fail_transport,fail_transport_release;
static bool transport_prepared;
static native_state_t *s_state;
static uint64_t s_health_boot_id;
static char body[1536];
static void esp_fill_random(void *data,size_t size) { memset(data,0x33,size); }
static int xSemaphoreTake(void *lock,unsigned ticks) { assert(lock && ticks==100);return 1; }
static void xSemaphoreGive(void *lock) { assert(lock); }
static const char *native_audio_output_name(void) { return "PDM \"test\""; }
static int httpd_resp_set_type(httpd_req_t *r,const char *v) { (void)r;assert(strstr(v,"application/json"));return 0; }
static int httpd_resp_set_hdr(httpd_req_t *r,const char *k,const char *v) { (void)r;assert(!strcmp(k,"Cache-Control") && !strcmp(v,"no-store"));return 0; }
static int httpd_resp_sendstr(httpd_req_t *r,const char *v) { (void)r;assert(strlen(v)<sizeof(body));snprintf(body,sizeof(body),"%s",v);return 0; }
static int httpd_resp_send_err(httpd_req_t *r,int code,const char *v) { (void)r;(void)code;(void)v;return -1; }
static int network_service_storage_init(void) { if(fail_storage)return fail_storage;storage_ready=true;return 0; }
static int web_reboot_start(void) { assert(storage_ready);if(fail_reboot)return fail_reboot;reboot_ready=true;return 0; }
static int web_reboot_abort(void) { assert(!upload_active && !ota_active && !wifi_active);if(fail_reboot_abort)return fail_reboot_abort;reboot_ready=false;reboot_aborted++;return 0; }
static void web_upload_activate(void) { assert(reboot_ready && server_live && ws_running && route_calls==23);upload_active=true; }
static void web_upload_deactivate(void) { upload_active=false; }
static void web_ota_activate(void) { assert(upload_active && reboot_ready && server_live && ws_running && route_calls==23);ota_active=true; }
static void web_ota_deactivate(void) { ota_active=false; }
static void web_wifi_activate(void) { assert(upload_active && ota_active && reboot_ready && server_live && ws_running && route_calls==23);wifi_active=true; }
static void web_wifi_deactivate(void) { wifi_active=false; }
#define WEB_OTA_MAX_IMAGE_BYTES 0x1B0000U
#define WEB_OTA_MAX_BODY_BYTES (WEB_OTA_MAX_IMAGE_BYTES+4096U)
static int native_web_transport_prepare(httpd_config_t *config) { assert(config->max_open_sockets==5 && reboot_ready);if(fail_transport)return ESP_FAIL;transport_prepared=true;return 0; }
bool native_web_transport_secure(void) { return false; }
static int native_web_transport_release(void) { assert(!server_live);if(fail_transport_release)return ESP_FAIL;transport_prepared=false;return 0; }
static int web_static_start(void) { assert(storage_ready && reboot_ready);if(fail_static)return fail_static;allocations++;return 0; }
static void web_static_abort(void) { assert(!activated && !server_live);aborted++;allocations--; }
static void web_static_activate(void) { assert(server_live && ws_running);activated++; }
static int httpd_start(void **server,const httpd_config_t *config) {
    assert(config->stack_size==6144 && config->max_open_sockets==5 && config->max_uri_handlers==24);
    assert(config->send_wait_timeout==1 && config->lru_purge_enable && config->uri_match_fn);
    if(fail_server)return fail_server;
    server_live++;*server=(void *)1;return 0;
}
static int httpd_stop(void *server) { assert(server && server_live && !ws_running);if(fail_server_stop)return ESP_FAIL;server_live--;server_stopped++;return 0; }
static int web_wifi_info_handler(httpd_req_t *),web_wifi_edit_handler(httpd_req_t *);
static int web_time_info_handler(httpd_req_t *),web_time_edit_handler(httpd_req_t *);
static int web_network_settings_info_handler(httpd_req_t *),web_network_settings_edit_handler(httpd_req_t *);
static int httpd_register_uri_handler(void *server,const httpd_uri_t *route) {
    assert(server && route->handler && route->uri);
    assert(!ota_active && !upload_active && !wifi_active);
    if(!strcmp(route->uri,"/update"))assert(route->method==HTTP_POST);
    if(!strcmp(route->uri,"/api/native/ota"))assert(route->method==HTTP_GET);
    if(!strcmp(route->uri,"/api/native/wifi")) {
        if(route->method==HTTP_GET) {assert(route->handler==web_wifi_info_handler);wifi_get_routes++;}
        else {assert(route->method==HTTP_POST && route->handler==web_wifi_edit_handler);wifi_post_routes++;}
    }
    if(!strcmp(route->uri,"/api/native/time")) {
        if(route->method==HTTP_GET) {assert(route->handler==web_time_info_handler);time_get_routes++;}
        else {assert(route->method==HTTP_POST && route->handler==web_time_edit_handler);time_post_routes++;}
    }
    if(!strcmp(route->uri,"/api/native/network-settings")) {
        if(route->method==HTTP_GET) {assert(route->handler==web_network_settings_info_handler);network_settings_get_routes++;}
        else {assert(route->method==HTTP_POST && route->handler==web_network_settings_edit_handler);network_settings_post_routes++;}
    }
    if(!strcmp(route->uri,"/*"))assert(ws_registered);
    return ++route_calls==fail_route ? ESP_FAIL : ESP_OK;
}
static int websocket_service_register(void *server,native_state_t *state) {
    assert(server && state);if(fail_ws_register)return fail_ws_register;ws_registered++;return 0;
}
static int websocket_service_start(void) {
    assert(ws_registered);if(fail_ws_start)return fail_ws_start;ws_running++;return 0;
}
static int websocket_service_stop(void) { stop_calls++;if(fail_ws_stop)return fail_ws_stop;ws_running=0;return 0; }
static int websocket_service_server_stopped(void *server) { assert(server && !server_live);server_resets++;ws_registered=0;return 0; }
#define HANDLER(name) static int name(httpd_req_t *r) { (void)r;return 0; }
HANDLER(network_handler) HANDLER(status_handler) HANDLER(health_handler) HANDLER(reconnect_handler)
HANDLER(radio_handler) HANDLER(play_handler) HANDLER(stop_handler) HANDLER(settings_handler)
HANDLER(web_static_handler)
HANDLER(web_upload_handler) HANDLER(web_board_upload_handler) HANDLER(web_wifi_upload_handler)
HANDLER(web_ota_handler) HANDLER(web_ota_info_handler)
HANDLER(web_wifi_info_handler) HANDLER(web_wifi_edit_handler)
HANDLER(web_time_info_handler) HANDLER(web_time_edit_handler)
HANDLER(web_network_settings_info_handler) HANDLER(web_network_settings_edit_handler)
#include "web-start.inc"

static native_state_t state={.lock=(void *)1};
static void reset(void) {
    atomic_store(&s_started,false);state.web_ready=false;
    allocations=aborted=activated=server_live=route_calls=ws_registered=ws_running=0;
    stop_calls=server_stopped=server_resets=fail_route=0;
    fail_static=fail_server=fail_ws_register=fail_ws_start=fail_ws_stop=0;
    fail_server_stop=0;
    fail_storage=fail_reboot=fail_reboot_abort=0;
    storage_ready=reboot_ready=upload_active=ota_active=wifi_active=false;reboot_aborted=0;
    wifi_get_routes=wifi_post_routes=time_get_routes=time_post_routes=0;
    network_settings_get_routes=network_settings_post_routes=0;
    fail_transport=fail_transport_release=0;transport_prepared=false;
}
static void assert_failure(void) {
    assert(web_service_start(&state)==ESP_FAIL);
    assert(!atomic_load(&s_started) && !state.web_ready && !server_live && !allocations && !activated && !ws_running && !upload_active && !ota_active && !wifi_active && !reboot_ready && !transport_prepared);
    assert(aborted==1);
}
int main(void) {
    assert(web_service_start(NULL)==ESP_ERR_INVALID_ARG);
    native_state_t invalid={0};assert(web_service_start(&invalid)==ESP_ERR_INVALID_ARG);
    reset();fail_storage=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && !allocations && !reboot_ready && !atomic_load(&s_started));
    reset();fail_reboot=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && !allocations && !aborted && !atomic_load(&s_started));
    reset();fail_static=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && !allocations && !aborted && !reboot_ready && reboot_aborted==1);
    reset();fail_server=ESP_FAIL;assert_failure();assert(!server_stopped && !server_resets);
    reset();fail_transport=ESP_FAIL;assert_failure();assert(!server_live);
    for(unsigned i=1;i<=23;++i) { reset();fail_route=i;assert_failure();assert(server_stopped==1 && server_resets==1); }
    reset();fail_ws_register=ESP_FAIL;assert_failure();assert(server_resets==1);
    reset();fail_ws_start=ESP_FAIL;assert_failure();
    reset();assert(web_service_start(&state)==ESP_OK);
    assert(atomic_load(&s_started) && state.web_ready && allocations==1 && server_live==1 && activated==1 && route_calls==23 && upload_active && ota_active && wifi_active && reboot_ready);
    assert(wifi_get_routes==1 && wifi_post_routes==1 && time_get_routes==1 && time_post_routes==1);
    assert(network_settings_get_routes==1 && network_settings_post_routes==1);
    assert(web_service_start(&state)==ESP_ERR_INVALID_STATE);
    httpd_req_t request={0};assert(capabilities_handler(&request)==ESP_OK);printf("CAPABILITIES=%s\n",body);
    reset();fail_ws_start=ESP_FAIL;fail_ws_stop=ESP_FAIL;
    assert(web_service_start(&state)==ESP_FAIL && server_live && allocations && !activated);
    assert(atomic_load(&s_started) && !server_stopped && !server_resets && !aborted);
    assert(reboot_ready && !upload_active && !ota_active);
    reset();fail_route=2;fail_server_stop=ESP_FAIL;
    assert(web_service_start(&state)==ESP_FAIL && server_live && allocations && reboot_ready && atomic_load(&s_started));
    assert(!upload_active && !ota_active && !server_stopped && !server_resets && !aborted && !reboot_aborted);
    assert(transport_prepared);
    reset();fail_route=2;fail_transport_release=ESP_FAIL;
    assert(web_service_start(&state)==ESP_FAIL && !server_live && allocations && reboot_ready && atomic_load(&s_started));
    assert(server_resets==1 && !aborted && !reboot_aborted && transport_prepared);
    reset();fail_server=ESP_FAIL;fail_reboot_abort=ESP_FAIL;
    assert(web_service_start(&state)==ESP_FAIL && !server_live && !allocations && reboot_ready && atomic_load(&s_started));
    puts("PASS HTTP startup: invalid state, every route failure, WS/worker/server rollback, duplicate start, retained resources on stop timeout");
    return 0;
}
