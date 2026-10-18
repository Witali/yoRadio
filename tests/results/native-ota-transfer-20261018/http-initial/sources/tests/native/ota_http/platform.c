static struct httpd_data hd;
static struct sock_db sd;
static uint64_t now_us,receive_ready,send_ready,maintenance_delay,verify_delay,receive_step;
static unsigned groups,reads,sends,wait_read,wait_write,lookup_count,lookup_fail,allocations;
static unsigned begins,writes,ends,aborts,verifies,activations,maintenance_begins,maintenance_ends,shutdowns,activity;
static bool maintenance,owned,selected,graceful_shutdown,direct_form,no_partition,no_running,fail_calloc,fail_malloc;
static bool fail_maintenance,fail_begin,fail_write,fail_end,fail_verify,fail_activate,sleep_allowed=true;
static int recv_fault,send_fault,select_fault;
static size_t receive_chunk=SIZE_MAX,send_chunk=SIZE_MAX,source_offset,source_size,flash_size,expected_size;
static uint8_t source[32768],flash[32768],image[12000];
static char wire_response[4096],events[256];
static size_t response_size,event_size;
static const char *content_type;
static bool reboot_during_maintenance;
static esp_partition_t active_partition={.address=0x10000,.size=0x1b0000,.type=0,.subtype=0x10,.label="ota_0"};
static esp_partition_t spare_partition={.address=0x1c0000,.size=0x1b0000,.type=0,.subtype=0x11,.label="ota_1"};
static esp_app_desc_t current_app;
static void event(char c) {assert(event_size+1<sizeof(events));events[event_size++]=c;events[event_size]=0;}
int64_t esp_timer_get_time(void) {return (int64_t)now_us;}
void vTaskDelay(TickType_t delay) {now_us+=(uint64_t)delay*1000U;}
TickType_t xTaskGetTickCount(void) {return (TickType_t)(now_us/1000U);}
int xTaskCreate(void (*fn)(void *),const char *name,unsigned stack,void *arg,unsigned priority,TaskHandle_t *task) {
    (void)fn;assert(!strcmp(name,"web_reboot")&&stack==2048&&!arg&&priority==2);++allocations;*task=(void *)1;return pdPASS;
}
void xTaskNotifyGive(TaskHandle_t task) {assert(task==(void *)1);event(shutdowns?(selected?'C':'X'):'N');}
unsigned ulTaskNotifyTake(int clear,TickType_t delay) {(void)clear;(void)delay;abort();}
void vTaskDelete(TaskHandle_t task) {assert(task==(void *)1);}
void esp_restart(void) {abort();}
void *host_malloc(size_t size) {event('R');return fail_malloc?NULL:malloc(size);}
void *host_calloc(size_t a,size_t b) {return fail_calloc?NULL:calloc(a,b);}
bool deep_sleep_clock_begin_activity(void) {if(!sleep_allowed)return false;++activity;return true;}
void deep_sleep_clock_end_activity(void) {assert(activity);--activity;}
void display_settings_note_activity(void) {assert(activity);}
esp_err_t audio_service_maintenance_begin(uint32_t timeout,audio_maintenance_token_t *token) {
    assert(timeout&&timeout<=30000&&!maintenance&&!token->epoch);++maintenance_begins;event('M');
    now_us+=maintenance_delay;
    if(fail_maintenance)return ESP_ERR_TIMEOUT;
    maintenance=true;token->epoch=99;
#ifndef TARGET_C3
    assert(s_reserved_epoch);
    if(reboot_during_maintenance)web_reboot_request(0);
#endif
    return ESP_OK;
}
esp_err_t audio_service_maintenance_end(audio_maintenance_token_t *token,bool resume) {
    assert(token->epoch==99&&maintenance&&resume);token->epoch=0;maintenance=false;++maintenance_ends;event('E');return ESP_OK;
}
const esp_partition_t *esp_ota_get_running_partition(void) {return no_running?NULL:&active_partition;}
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *running) {assert(!no_running&&running==&active_partition);return no_partition?NULL:&spare_partition;}
const esp_app_desc_t *esp_app_get_description(void) {return &current_app;}
esp_err_t esp_ota_begin(const esp_partition_t *partition,size_t size,esp_ota_handle_t *handle) {
    assert(partition==&spare_partition&&size==OTA_WITH_SEQUENTIAL_WRITES&&maintenance&&!owned);
#ifndef TARGET_C3
    assert(direct_form||s_reserved_epoch);
#endif
    ++begins;event('B');if(fail_begin)return ESP_FAIL;owned=true;*handle=42;return ESP_OK;
}
esp_err_t esp_ota_write(esp_ota_handle_t handle,const void *data,size_t size) {
    assert(handle==42&&owned&&maintenance&&size&&size<=4096&&flash_size+size<=sizeof(flash));++writes;event('W');
    if(fail_write)return ESP_FAIL;
    memcpy(flash+flash_size,data,size);flash_size+=size;return ESP_OK;
}
esp_err_t esp_ota_end(esp_ota_handle_t handle) {assert(handle==42&&owned);owned=false;++ends;event('F');return fail_end?ESP_FAIL:ESP_OK;}
esp_err_t esp_ota_abort(esp_ota_handle_t handle) {assert(handle==42&&owned);owned=false;++aborts;event('Z');return ESP_OK;}
esp_err_t esp_image_verify(esp_image_load_mode_t mode,const esp_partition_pos_t *position,esp_image_metadata_t *metadata) {
    assert(mode==ESP_IMAGE_VERIFY&&position->offset==spare_partition.address&&position->size==flash_size&&!owned);++verifies;event('V');
    now_us+=verify_delay;metadata->image_len=expected_size;return fail_verify?ESP_FAIL:ESP_OK;
}
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *partition) {assert(partition==&spare_partition&&!owned&&verifies);++activations;event('A');if(fail_activate)return ESP_FAIL;selected=true;return ESP_OK;}
struct sock_db *httpd_sess_get(httpd_handle_t handle,int socket) {
    assert(handle==&hd&&socket==7);++lookup_count;return lookup_fail==lookup_count?NULL:&sd;
}
bool httpd_valid_req(httpd_req_t *request) {return request==&hd.hd_req;}
void esp_http_server_dispatch_event(int id,void *data,size_t size) {(void)id;(void)data;(void)size;}
int httpd_req_to_sockfd(httpd_req_t *request) {assert(request==&hd.hd_req);return 7;}
esp_err_t httpd_req_get_hdr_value_str(httpd_req_t *request,const char *name,char *value,size_t size) {
    assert(request==&hd.hd_req&&!strcmp(name,"Content-Type"));if(!content_type||strlen(content_type)>=size)return ESP_FAIL;
    strcpy(value,content_type);return ESP_OK;
}
esp_err_t httpd_resp_send_err(httpd_req_t *request,int code,const char *message) {
    assert(code==500);httpd_resp_set_status(request,"500 Internal Server Error");return httpd_resp_sendstr(request,message);
}
static int default_send(httpd_handle_t server,int socket,const char *data,size_t size,int flags) {
    bool write=false;return (int)native_web_transport_send(server,socket,data,size,flags,&write);
}
static int default_receive(httpd_handle_t server,int socket,char *data,size_t size,int flags) {
    bool write=false;return (int)native_web_transport_recv(server,socket,data,size,flags,&write);
}
ssize_t native_web_transport_recv(httpd_handle_t server,int socket,void *data,size_t size,int flags,bool *write) {
    assert(server==&hd&&socket==7);(void)flags;++reads;*write=recv_fault==4;
    if(shutdowns)assert(!"read after shutdown");
    if(now_us<receive_ready){errno=EAGAIN;return -1;}
    if(recv_fault==1)return 0;
    if(recv_fault==2){errno=ECONNRESET;return -1;}
    if(recv_fault==3)return (ssize_t)size+1;
    if(source_offset==source_size)return 0;
    size_t count=source_size-source_offset;if(count>size)count=size;if(count>receive_chunk)count=receive_chunk;
    memcpy(data,source+source_offset,count);source_offset+=count;now_us+=receive_step;return (ssize_t)count;
}
ssize_t native_web_transport_send(httpd_handle_t server,int socket,const void *data,size_t size,int flags,bool *write) {
    assert(server==&hd&&socket==7);(void)flags;++sends;*write=send_fault!=4;
    assert(!shutdowns);
    if(now_us<send_ready){errno=EAGAIN;return -1;}
    if(send_fault==1)return 0;
    if(send_fault==2){errno=EPIPE;return -1;}
    if(send_fault==3)return (ssize_t)size+1;
    size_t count=size<send_chunk?size:send_chunk;assert(response_size+count<sizeof(wire_response));
    memcpy(wire_response+response_size,data,count);response_size+=count;wire_response[response_size]=0;return (ssize_t)count;
}
void native_web_transport_shutdown(httpd_handle_t server,int socket,bool graceful) {assert(server==&hd&&socket==7&&!shutdowns);++shutdowns;graceful_shutdown=graceful;event('S');}
int lwip_select(int nfds,fd_set *readset,fd_set *writeset,fd_set *errors,struct timeval *timeout) {
    assert(nfds==8&&!errors&&!!readset!=!!writeset);uint64_t budget=(uint64_t)timeout->tv_sec*1000000U+(unsigned)timeout->tv_usec;
    if(readset){assert(FD_ISSET(7,readset));++wait_read;}else {assert(FD_ISSET(7,writeset));++wait_write;}
    if(select_fault){errno=select_fault==1?EINTR:EBADF;if(select_fault==1)select_fault=0;return -1;}
    uint64_t ready=hd.hd_req_aux.remaining_len?receive_ready:send_ready;
    if(ready>now_us){uint64_t delay=ready-now_us;if(delay>=budget){now_us+=budget;return 0;}now_us+=delay;}
    return 1;
}
