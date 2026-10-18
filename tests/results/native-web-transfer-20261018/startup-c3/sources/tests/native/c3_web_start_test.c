#include <assert.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef int esp_err_t;
typedef void *httpd_handle_t;
typedef struct {void *lock;bool web_ready;} native_state_t;
typedef struct {int unused;} httpd_req_t;
typedef struct {const char *uri;int method;int (*handler)(httpd_req_t *);} httpd_uri_t;
typedef struct {unsigned stack_size,max_open_sockets,max_uri_handlers,send_wait_timeout,server_port;
    int task_priority,core_id;bool lru_purge_enable;void *uri_match_fn;} httpd_config_t;
enum {ESP_OK=0,ESP_FAIL=-1,ESP_ERR_INVALID_ARG=-2,ESP_ERR_INVALID_STATE=-3,HTTP_GET=0,HTTP_POST=1};
#define HTTPD_DEFAULT_CONFIG() ((httpd_config_t){.task_priority=5,.core_id=-1,.server_port=80})
#define CONFIG_YORADIO_WEB_STATIC_WORKERS 2
#define CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS 1
#define WEB_MAX_OPEN_SOCKETS 7
#define pdMS_TO_TICKS(x) (x)
#define ESP_LOGI(...) ((void)0)
#define ESP_RETURN_ON_ERROR(expression,...) do {int err_=(expression);if(err_!=ESP_OK)return err_;}while(0)
static native_state_t *s_state;
static uint64_t s_health_boot_id;
static atomic_bool s_started;
static void *s_static_request_queue,*s_static_worker_tasks[2];
static void *httpd_uri_match_wildcard=(void *)1;
static unsigned storage_calls,prepare_calls,worker_starts,deleted_workers,deleted_queues,release_calls,route_calls;
static bool server_live,prepared,secure;
static int fail_storage,fail_prepare,fail_workers,fail_server,fail_release,fail_route,fail_ws;
static void esp_fill_random(void *out,size_t size){memset(out,0x5a,size);}
static int web_upload_storage_init(void){storage_calls++;return fail_storage;}
static int native_web_transport_prepare(httpd_config_t *config){
    prepare_calls++;if(fail_prepare)return fail_prepare;prepared=true;
    assert(config->stack_size==8192 && config->max_open_sockets==7);
    if(secure){config->stack_size=10240;config->max_open_sockets=3;config->server_port=443;}return ESP_OK;
}
bool native_web_transport_secure(void){return secure;}
static int native_web_transport_release(void){assert(!server_live);release_calls++;if(fail_release)return fail_release;prepared=false;return ESP_OK;}
static int start_static_workers(void){assert(prepared);worker_starts++;if(fail_workers)return fail_workers;
    s_static_request_queue=(void *)1;s_static_worker_tasks[0]=(void *)2;s_static_worker_tasks[1]=(void *)3;return ESP_OK;}
static void vTaskDelete(void *task){assert(task);deleted_workers++;}
static void vQueueDelete(void *queue){assert(queue);deleted_queues++;}
static int httpd_start(void **server,const httpd_config_t *config){
    assert(prepared && config->task_priority==5 && config->core_id==-1 && config->max_uri_handlers==15);
    assert(config->stack_size==(secure?10240U:8192U) && config->max_open_sockets==(secure?3U:7U));
    assert(config->server_port==(secure?443U:80U) && config->lru_purge_enable && config->uri_match_fn);
    if(fail_server)return fail_server;*server=(void *)1;server_live=true;return ESP_OK;
}
static int httpd_register_uri_handler(void *server,const httpd_uri_t *route){
    assert(server_live && server && route->uri && route->handler);return ++route_calls==(unsigned)fail_route?ESP_FAIL:ESP_OK;
}
static int websocket_service_register(void *server,native_state_t *state){assert(server_live && server && state);return fail_ws;}
static int xSemaphoreTake(void *lock,unsigned ticks){assert(lock && ticks==100);return 1;}
static void xSemaphoreGive(void *lock){assert(lock);}
#define HANDLER(name) static int name(httpd_req_t *req){(void)req;return ESP_OK;}
HANDLER(status_handler) HANDLER(health_handler) HANDLER(web_ota_handler) HANDLER(web_ota_info_handler)
HANDLER(sleep_guarded_reconnect_handler) HANDLER(sleep_guarded_play_handler) HANDLER(sleep_guarded_stop_handler)
HANDLER(sleep_guarded_upload_handler) HANDLER(webboard_page_handler) HANDLER(sleep_guarded_webboard_upload_handler)
HANDLER(sleep_guarded_emergency_handler) HANDLER(sleep_guarded_recovery_wifi_handler) HANDLER(web_memory_handler) HANDLER(static_handler)
#include "web-start.inc"

static native_state_t state={.lock=(void *)1};
static void reset(void){
    atomic_store(&s_started,false);state.web_ready=false;
    s_static_request_queue=NULL;memset(s_static_worker_tasks,0,sizeof(s_static_worker_tasks));
    storage_calls=prepare_calls=worker_starts=deleted_workers=deleted_queues=release_calls=route_calls=0;
    server_live=prepared=secure=false;fail_storage=fail_prepare=fail_workers=fail_server=fail_release=fail_route=fail_ws=0;
}
int main(void){
    assert(web_service_start(NULL)==ESP_ERR_INVALID_ARG);
    native_state_t invalid={0};assert(web_service_start(&invalid)==ESP_ERR_INVALID_ARG);
    reset();fail_storage=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && !atomic_load(&s_started) && !prepare_calls);
    reset();fail_prepare=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && !atomic_load(&s_started) && !worker_starts && !release_calls);
    reset();fail_workers=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && !atomic_load(&s_started) && !prepared && release_calls==1);
    reset();fail_server=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && !atomic_load(&s_started) && !prepared);
    assert(deleted_workers==2 && deleted_queues==1 && !s_static_request_queue && !s_static_worker_tasks[0] && !s_static_worker_tasks[1]);
    reset();fail_server=fail_release=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && atomic_load(&s_started) && prepared && !server_live);
    for(int route=1;route<=14;route++){
        reset();fail_route=route;assert(web_service_start(&state)==ESP_FAIL && atomic_load(&s_started) && server_live && prepared && !state.web_ready);
        assert(!deleted_workers && !deleted_queues && !release_calls);
        assert(web_service_start(&state)==ESP_ERR_INVALID_STATE && worker_starts==1 && storage_calls==1);
    }
    reset();fail_ws=ESP_FAIL;assert(web_service_start(&state)==ESP_FAIL && server_live && prepared && atomic_load(&s_started));
    for(unsigned mode=0;mode<2;mode++){
        reset();secure=mode;assert(web_service_start(&state)==ESP_OK && state.web_ready && route_calls==14);
        assert(web_service_start(&state)==ESP_ERR_INVALID_STATE && storage_calls==1 && prepare_calls==1 && worker_starts==1);
    }
    puts("PASS C3 web startup: pre-listener failure rollback, TLS/plain configuration, every route failure retains live ownership, duplicate-start gate, priority/core preserved");
    return 0;
}
