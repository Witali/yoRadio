/* Platform seams only. HTTP parser/session/body/response algorithms are SDK C. */
#include <signal.h>
#include <sys/wait.h>
static esp_partition_t active_partition={.address=0x10000,.size=0x1b0000,.type=0,.subtype=0x10,.label="ota_0"};
static esp_partition_t spare_partition={.address=0x1c0000,.size=0x1b0000,.type=0,.subtype=0x11,.label="ota_1"};
static esp_app_desc_t current_app;
static uint8_t image[12000],flash[12000];
static size_t flash_size;
static unsigned ota_begins,ota_ends,ota_aborts,ota_verifies,ota_activations,audio_begins,audio_ends;
static unsigned workspace_allocations,workspace_frees,request_deletes,purge_receives,handler_calls,shutdown_calls,pending_at_handler;
static bool maintenance,handle_owned,selected,fail_response,fail_maintenance;
static void *workspace;
static int64_t handler_started,handler_ended;

static int64_t esp_timer_get_time(void) {struct timespec t;assert(!clock_gettime(CLOCK_MONOTONIC,&t));return (int64_t)t.tv_sec*1000000+t.tv_nsec/1000;}
static void vTaskDelay(unsigned ticks) {struct timespec t={.tv_sec=ticks/1000,.tv_nsec=(long)(ticks%1000)*1000000};while(nanosleep(&t,&t)&&errno==EINTR){} }
static int lwip_select(int n,fd_set *r,fd_set *w,fd_set *e,struct timeval *t) {return select(n,r,w,e,t);}
static bool deep_sleep_clock_begin_activity(void) {++activity_count;return true;}
static void deep_sleep_clock_end_activity(void) {assert(activity_count);--activity_count;}
static void display_settings_note_activity(void) {assert(activity_count);}
static TickType_t xTaskGetTickCount(void) {if(selected)assert(shutdown_calls==1);return (TickType_t)(esp_timer_get_time()/1000);}
static int xTaskCreate(void (*fn)(void *),const char *name,unsigned stack,void *arg,unsigned priority,TaskHandle_t *task) {
    (void)fn;assert(!strcmp(name,"web_reboot")&&stack==2048&&!arg&&priority==2);*task=(void *)1;return pdPASS;
}
static void xTaskNotifyGive(TaskHandle_t task) {assert(task==(void *)1);if(selected)assert(shutdown_calls==1);}
static unsigned ulTaskNotifyTake(int clear,TickType_t delay) {(void)clear;(void)delay;abort();}
static void vTaskDelete(TaskHandle_t task) {assert(task==(void *)1);}
static void esp_restart(void) {abort();}
static esp_err_t audio_service_maintenance_begin(uint32_t timeout,audio_maintenance_token_t *token) {
    assert(timeout&&timeout<=30000&&!token->epoch&&!maintenance);++audio_begins;
    if(fail_maintenance)return ESP_ERR_TIMEOUT;maintenance=true;token->epoch=42;return ESP_OK;
}
static esp_err_t audio_service_maintenance_end(audio_maintenance_token_t *token,bool resume) {
    assert(token->epoch==42&&maintenance&&resume);++audio_ends;token->epoch=0;maintenance=false;return ESP_OK;
}
const esp_partition_t *esp_ota_get_running_partition(void) {return &active_partition;}
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *partition) {assert(partition==&active_partition);return &spare_partition;}
const esp_app_desc_t *esp_app_get_description(void) {return &current_app;}
esp_err_t esp_ota_begin(const esp_partition_t *partition,size_t size,esp_ota_handle_t *handle) {
    assert(partition==&spare_partition&&size==OTA_WITH_SEQUENTIAL_WRITES&&maintenance&&!handle_owned);
#ifndef TARGET_C3
    assert(s_reserved_epoch);
#else
    assert(s_reboot_reserved_epoch&&activity_count==1);
#endif
    ++ota_begins;handle_owned=true;*handle=42;return ESP_OK;
}
esp_err_t esp_ota_write(esp_ota_handle_t handle,const void *data,size_t size) {
    assert(handle==42&&handle_owned&&maintenance&&size&&size<=4096&&flash_size+size<=sizeof(flash));
    memcpy(flash+flash_size,data,size);flash_size+=size;return ESP_OK;
}
esp_err_t esp_ota_end(esp_ota_handle_t handle) {assert(handle==42&&handle_owned);handle_owned=false;++ota_ends;return ESP_OK;}
esp_err_t esp_ota_abort(esp_ota_handle_t handle) {assert(handle==42&&handle_owned);handle_owned=false;++ota_aborts;return ESP_OK;}
esp_err_t esp_image_verify(esp_image_load_mode_t mode,const esp_partition_pos_t *position,esp_image_metadata_t *metadata) {
    assert(mode==ESP_IMAGE_VERIFY&&position->offset==spare_partition.address&&position->size==flash_size&&!handle_owned);
    ++ota_verifies;metadata->image_len=sizeof(image);return flash_size==sizeof(image)&&!memcmp(flash,image,sizeof(image))?ESP_OK:ESP_FAIL;
}
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *partition) {assert(partition==&spare_partition&&!handle_owned&&ota_verifies);++ota_activations;selected=true;return ESP_OK;}
static void *response_malloc(size_t size) {return fail_response&&selected?NULL:malloc(size);}
static void *workspace_calloc(size_t count,size_t size) {assert(!workspace);workspace=calloc(count,size);assert(workspace);++workspace_allocations;return workspace;}
static void workspace_free(void *context) {if(!context)return;assert(context==workspace&&workspace_frees<workspace_allocations);++workspace_frees;workspace=NULL;free(context);}
static void observed_prepare_close(httpd_handle_t server_handle,int fd,bool graceful) {assert(!shutdown_calls);++shutdown_calls;native_web_transport_prepare_close(server_handle,fd,graceful);}
static bool httpd_valid_req(httpd_req_t *r) {return r&&r->handle==&server&&r->aux==&server.hd_req_aux&&server.hd_req_aux.sd==&session;}
static struct sock_db *httpd_sess_get(httpd_handle_t hd,int fd) {assert(hd==&server);return fd>=0&&session.fd==fd?&session:NULL;}
#ifndef INTEGRATION_TLS
static ssize_t native_web_transport_send(httpd_handle_t hd,int fd,const void *data,size_t size,int flags,bool *write) {assert(hd==&server&&fd==session.fd);*write=true;return send(fd,data,size,flags|MSG_NOSIGNAL);}
static ssize_t native_web_transport_recv(httpd_handle_t hd,int fd,void *data,size_t size,int flags,bool *write) {assert(hd==&server&&fd==session.fd);*write=false;return recv(fd,data,size,flags);}
static void native_web_transport_shutdown(httpd_handle_t hd,int fd,bool graceful) {(void)graceful;assert(hd==&server&&fd==session.fd&&!shutdown(fd,SHUT_RDWR));}
static void native_web_transport_prepare_close(httpd_handle_t hd,int fd,bool graceful) {(void)graceful;assert(hd==&server&&fd==session.fd);}
#endif
static int default_send(httpd_handle_t hd,int fd,const char *data,size_t size,int flags) {assert(hd==&server);return (int)send(fd,data,size,flags|MSG_NOSIGNAL);}
static int default_receive(httpd_handle_t hd,int fd,char *data,size_t size,int flags) {assert(hd==&server);return (int)recv(fd,data,size,flags);}
static esp_err_t httpd_sess_trigger_close(httpd_handle_t hd,int fd) {assert(hd==&server&&fd==session.fd);++queued_close_calls;return ESP_OK;}
static esp_err_t httpd_queue_work(httpd_handle_t hd,httpd_work_fn_t fn,void *context) {(void)hd;(void)fn;(void)context;abort();}
static int httpd_req_handle_err(httpd_req_t *request,int status) {snprintf(response_status,sizeof(response_status),"%d",status);(void)request;return ESP_FAIL;}
static int httpd_resp_send_custom_err(httpd_req_t *request,const char *status,const char *message) {httpd_resp_set_status(request,status);return httpd_resp_sendstr(request,message);}
static int httpd_resp_send_err(httpd_req_t *request,httpd_err_code_t code,const char *message) {
    assert(code==HTTPD_500_INTERNAL_SERVER_ERROR);return httpd_resp_send_custom_err(request,"500 Internal Server Error",message);
}
static void esp_http_server_dispatch_event(int event,const void *data,size_t size) {assert(data&&size);if(event==HTTP_SERVER_EVENT_DISCONNECTED)++delete_count;}
static size_t strlcpy(char *dst,const char *src,size_t cap) {size_t size=strlen(src);if(cap){size_t n=MIN(cap-1,size);memcpy(dst,src,n);dst[n]=0;}return size;}
static esp_err_t observed_handler(httpd_req_t *request) {
    ++handler_calls;pending_at_handler=session.pending_len;handler_started=esp_timer_get_time();
    esp_err_t result=web_ota_handler(request);handler_ended=esp_timer_get_time();
    assert(result==
#ifdef NEGATIVE_OTA_RETURN_OK
        ESP_OK
#else
        ESP_FAIL
#endif
        &&workspace_allocations==workspace_frees&&!workspace&&!request->sess_ctx);
    return result;
}
static esp_err_t observed_info(httpd_req_t *request) {
    ++handler_calls;handler_started=esp_timer_get_time();
    esp_err_t result=web_ota_info_handler(request);handler_ended=esp_timer_get_time();return result;
}
