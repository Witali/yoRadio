static struct httpd_data hd;
static struct sock_db sd;
static uint64_t clock_us, receive_ready, send_ready, receive_step, publish_delay;
static unsigned groups, receives, sends, wait_read, wait_write, close_prepares, activity;
static unsigned publications, workspace_allocations, workspace_frees;
static bool fail_workspace, fail_response, fail_store, store_busy, sleep_allowed=true, committed_file;
static bool receive_wants_write, send_wants_read;
static size_t source_size, source_offset, response_size, receive_chunk=SIZE_MAX, send_chunk=SIZE_MAX;
static uint8_t source[5000];
static char response[5000], events[128];
static size_t event_size;
static const char *type;
static void *http_workspace;
static size_t http_workspace_size;
static char directory[]="/tmp/native-wifi-http-XXXXXX";
static pthread_mutex_t owner_mutex=PTHREAD_MUTEX_INITIALIZER;
static unsigned async_begins, async_completes, queued_static, file_opens;
static void event(char c) {assert(event_size+1<sizeof(events));events[event_size++]=c;events[event_size]=0;}
static void mapped_path(const char *path,char *out,size_t size) {
    assert(!strncmp(path,"/spiffs/data/",13));
    int count=snprintf(out,size,"%s/%s",directory,path+13);assert(count>0&&(size_t)count<size);
}
FILE *mapped_open(const char *path,const char *mode) {++file_opens;char name[256];mapped_path(path,name,sizeof(name));return fopen(name,mode);}
int mapped_stat(const char *path,struct stat *out) {char name[256];mapped_path(path,name,sizeof(name));return stat(name,out);}
int mapped_remove(const char *path) {char name[256];mapped_path(path,name,sizeof(name));return remove(name);}
int mapped_rename(const char *from,const char *to) {
    if(fail_store&&strstr(from,".tmp")){errno=EIO;return -1;}
    char a[256],b[256];mapped_path(from,a,sizeof(a));mapped_path(to,b,sizeof(b));
    if(!access(b,F_OK)){errno=EEXIST;return -1;} // Match SPIFFS no-overwrite rename.
    int result=rename(a,b);
    if(!result&&strstr(from,".tmp")){++publications;committed_file=true;clock_us+=publish_delay;event('P');}
    return result;
}
SemaphoreHandle_t xSemaphoreCreateMutex(void) {return &owner_mutex;}
int xSemaphoreTake(SemaphoreHandle_t lock,unsigned timeout) {assert(lock==&owner_mutex&&timeout==1000);return store_busy?0:!pthread_mutex_lock(lock);}
void xSemaphoreGive(SemaphoreHandle_t lock) {assert(lock==&owner_mutex&&!pthread_mutex_unlock(lock));}
uint32_t esp_random(void) {return UINT32_C(0x12345678);}
void esp_fill_random(void *out,size_t size) {memset(out,0x39,size);}
esp_err_t web_upload_storage_init(void) {return ESP_OK;}
int64_t esp_timer_get_time(void) {return (int64_t)clock_us;}
void vTaskDelay(TickType_t delay) {clock_us+=(uint64_t)delay*1000U;}
TickType_t xTaskGetTickCount(void) {if(committed_file){assert(close_prepares==1&&!http_workspace);event('C');}return (TickType_t)(clock_us/1000U);}
int xTaskCreate(void (*fn)(void *),const char *name,unsigned stack,void *arg,unsigned priority,TaskHandle_t *task) {
    assert(fn&&!strcmp(name,"web_reboot")&&stack==2048&&!arg&&priority==2);*task=(void *)1;return pdPASS;
}
void xTaskNotifyGive(TaskHandle_t task) {assert(task==(void *)1);}
unsigned ulTaskNotifyTake(int clear,TickType_t delay) {(void)clear;(void)delay;abort();}
void vTaskDelete(TaskHandle_t task) {assert(task==(void *)1);}
void esp_restart(void) {abort();}
bool deep_sleep_clock_begin_activity(void) {if(!sleep_allowed)return false;++activity;return true;}
void deep_sleep_clock_end_activity(void) {assert(activity);--activity;}
void display_settings_note_activity(void) {assert(activity);}
void *response_malloc(size_t size) {event('R');return fail_response?NULL:malloc(size);}
void *workspace_calloc(size_t a,size_t b) {
    if(fail_workspace)return NULL;
    assert(!http_workspace);http_workspace=calloc(a,b);http_workspace_size=a*b;
    assert(http_workspace);++workspace_allocations;return http_workspace;
}
void workspace_free(void *p) {
    assert(p&&p==http_workspace);
    const uint8_t *bytes=p;for(size_t i=0;i<http_workspace_size;++i)assert(!bytes[i]);
    ++workspace_frees;http_workspace=NULL;event('F');free(p);
}
struct sock_db *httpd_sess_get(httpd_handle_t server,int socket) {assert(server==&hd&&socket==7);return &sd;}
bool httpd_valid_req(httpd_req_t *request) {return request==&hd.hd_req;}
void esp_http_server_dispatch_event(int id,void *data,size_t size) {(void)id;(void)data;(void)size;}
int httpd_req_to_sockfd(httpd_req_t *request) {assert(request==&hd.hd_req);return 7;}
esp_err_t httpd_req_get_hdr_value_str(httpd_req_t *request,const char *key,char *out,size_t size) {
    assert(request==&hd.hd_req&&!strcmp(key,"Content-Type"));
    if(!type||strlen(type)>=size)return ESP_FAIL;
    strcpy(out,type);return ESP_OK;
}
esp_err_t httpd_resp_send_err(httpd_req_t *request,int code,const char *message) {
    assert(code==500||code==404);httpd_resp_set_status(request,code==404?"404 Not Found":"500 Internal Server Error");return httpd_resp_sendstr(request,message);
}
esp_err_t httpd_req_async_handler_begin(httpd_req_t *request,httpd_req_t **out) {++async_begins;*out=request;return ESP_OK;}
esp_err_t httpd_req_async_handler_complete(httpd_req_t *request) {assert(request==&hd.hd_req);++async_completes;return ESP_OK;}
int xQueueSend(void *queue,const void *data,unsigned timeout) {assert(queue&&data&&!timeout);++queued_static;return pdTRUE;}
ssize_t native_web_transport_recv(httpd_handle_t server,int socket,void *data,size_t size,int flags,bool *write) {
    assert(server==&hd&&socket==7&&!close_prepares);(void)flags;++receives;*write=receive_wants_write;
    if(clock_us<receive_ready){errno=EAGAIN;return -1;}
    if(source_offset==source_size)return 0;
    size_t count=source_size-source_offset;if(count>size)count=size;if(count>receive_chunk)count=receive_chunk;
    memcpy(data,source+source_offset,count);source_offset+=count;clock_us+=receive_step;return (ssize_t)count;
}
ssize_t native_web_transport_send(httpd_handle_t server,int socket,const void *data,size_t size,int flags,bool *write) {
    assert(server==&hd&&socket==7&&!close_prepares);(void)flags;++sends;*write=!send_wants_read;
    if(clock_us<send_ready){errno=EAGAIN;return -1;}
    size_t count=size<send_chunk?size:send_chunk;assert(response_size+count<sizeof(response));
    memcpy(response+response_size,data,count);response_size+=count;response[response_size]=0;event('S');return (ssize_t)count;
}
void native_web_transport_prepare_close(httpd_handle_t server,int socket,bool graceful) {
    assert(server==&hd&&socket==7&&!close_prepares);(void)graceful;++close_prepares;event('T');
}
int lwip_select(int count,fd_set *readset,fd_set *writeset,fd_set *errors,struct timeval *timeout) {
    assert(count==8&&!errors&&!!readset!=!!writeset);
    if(readset)++wait_read;else ++wait_write;
    uint64_t budget=(uint64_t)timeout->tv_sec*1000000U+(unsigned)timeout->tv_usec;
    uint64_t ready=hd.hd_req_aux.remaining_len?receive_ready:send_ready;
    if(ready>clock_us){uint64_t delay=ready-clock_us;if(delay>=budget){clock_us+=budget;return 0;}clock_us+=delay;}
    return 1;
}
static int default_send(httpd_handle_t server,int socket,const char *data,size_t size,int flags) {
    bool writable;return (int)native_web_transport_send(server,socket,data,size,flags,&writable);
}
static int default_receive(httpd_handle_t server,int socket,char *data,size_t size,int flags) {
    bool writable;return (int)native_web_transport_recv(server,socket,data,size,flags,&writable);
}
