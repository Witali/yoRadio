/* Field-model platform seams. HTTPD, settings and transport C stay unchanged. */
#include <pthread.h>
#include <signal.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <sys/time.h>

typedef unsigned TickType_t, nvs_handle_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define pdTRUE 1
#define pdMS_TO_TICKS(v) (v)
#define NVS_READONLY 0
#define NVS_READWRITE 1
#define ESP_ERR_NVS_NOT_FOUND 0x1102
#define ESP_ERR_NVS_TYPE_MISMATCH 0x1103
typedef pthread_mutex_t *SemaphoreHandle_t;
static SemaphoreHandle_t setting_mutex;
static SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    assert(!setting_mutex);setting_mutex=malloc(sizeof(*setting_mutex));
    assert(setting_mutex&&!pthread_mutex_init(setting_mutex,NULL));return setting_mutex;
}
static int xSemaphoreTake(SemaphoreHandle_t lock,unsigned ticks) {
    assert(lock==setting_mutex&&ticks==100);assert(!pthread_mutex_lock(lock));return pdTRUE;
}
static int xSemaphoreGive(SemaphoreHandle_t lock) {assert(!pthread_mutex_unlock(lock));return pdTRUE;}
static void vSemaphoreDelete(SemaphoreHandle_t lock) {assert(lock==setting_mutex);assert(!pthread_mutex_destroy(lock));free(lock);setting_mutex=NULL;}
static uint8_t stored_record[82],pending_record[82];
static size_t stored_size,pending_size;
static bool stored_present,fail_commit,snapshot_available=true;
static unsigned nvs_opens,nvs_sets,nvs_commits,save_calls,snapshot_calls;
static esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle) {
    assert(!strcmp(name,"native_time"));++nvs_opens;
    if(mode==NVS_READONLY&&!stored_present)return ESP_ERR_NVS_NOT_FOUND;
    *handle=7;return ESP_OK;
}
static void nvs_close(nvs_handle_t handle) {assert(handle==7);}
static esp_err_t nvs_get_blob(nvs_handle_t handle,const char *name,void *out,size_t *size) {
    assert(handle==7&&!strcmp(name,"cfg"));if(!stored_present)return ESP_ERR_NVS_NOT_FOUND;
    if(!out){*size=stored_size;return ESP_OK;}assert(*size>=stored_size);
    memcpy(out,stored_record,stored_size);*size=stored_size;return ESP_OK;
}
static esp_err_t nvs_set_blob(nvs_handle_t handle,const char *name,const void *data,size_t size) {
    assert(handle==7&&!strcmp(name,"cfg")&&size==82);++nvs_sets;
    memcpy(pending_record,data,size);pending_size=size;return ESP_OK;
}
static esp_err_t nvs_commit(nvs_handle_t handle) {
    assert(handle==7);++nvs_commits;if(fail_commit)return ESP_FAIL;
    memcpy(stored_record,pending_record,pending_size);stored_size=pending_size;stored_present=true;return ESP_OK;
}
static time_snapshot_t snapshot_fields;
bool time_service_snapshot(time_snapshot_t *out) {
    ++snapshot_calls;if(!snapshot_available)return false;*out=snapshot_fields;
    return time_settings_snapshot(&out->settings,&out->desired_revision);
}
esp_err_t time_service_save_settings(const time_settings_t *settings) {++save_calls;return time_settings_save(settings);}

static unsigned handler_calls,request_deletes,purge_calls,purge_positive_bytes,prepare_closes;
static bool in_purge;
static int64_t handler_started,handler_ended;
void integration_transport_prepare(const char *,bool);
int integration_transport_open(void *,int);
void integration_transport_close(void *,int);
void integration_transport_release(void);
static int64_t esp_timer_get_time(void) {struct timespec t;assert(!clock_gettime(CLOCK_MONOTONIC,&t));return (int64_t)t.tv_sec*1000000+t.tv_nsec/1000;}
static int lwip_select(int n,fd_set *r,fd_set *w,fd_set *e,struct timeval *t) {return select(n,r,w,e,t);}
static void vTaskDelay(unsigned ticks) {struct timespec t={.tv_nsec=(long)ticks*1000000};while(nanosleep(&t,&t)&&errno==EINTR){}}
static bool httpd_valid_req(httpd_req_t *r) {return r&&r->handle==&server&&r->aux==&server.hd_req_aux&&server.hd_req_aux.sd==&session;}
static struct sock_db *httpd_sess_get(httpd_handle_t hd,int fd) {assert(hd==&server);return fd>=0&&session.fd==fd?&session:NULL;}
static esp_err_t httpd_sess_trigger_close(httpd_handle_t hd,int fd) {assert(hd==&server&&fd==session.fd);++queued_close_calls;return ESP_OK;}
static esp_err_t httpd_queue_work(httpd_handle_t hd,httpd_work_fn_t fn,void *ctx) {(void)hd;(void)fn;(void)ctx;abort();}
static void esp_http_server_dispatch_event(int event,const void *data,size_t size) {assert(data&&size);if(event==HTTP_SERVER_EVENT_DISCONNECTED)++delete_count;}
static size_t strlcpy(char *out,const char *text,size_t cap) {size_t n=strlen(text);if(cap){size_t copy=MIN(n,cap-1);memcpy(out,text,copy);out[copy]=0;}return n;}
static void observed_prepare_close(httpd_handle_t hd,int fd,bool graceful) {++prepare_closes;native_web_transport_prepare_close(hd,fd,graceful);}
static esp_err_t observed_handler(httpd_req_t *request) {
    ++handler_calls;handler_started=esp_timer_get_time();
    esp_err_t result=request->method==HTTP_GET?web_time_info_handler(request):web_time_edit_handler(request);
    handler_ended=esp_timer_get_time();return result;
}
