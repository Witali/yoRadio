/* Linux/RTOS/filesystem boundaries only; HTTPD and application bodies are frozen C. */
#include <signal.h>
#include <sys/wait.h>
#include <pthread.h>
#include <fcntl.h>
#include <sys/stat.h>
static char directory[]="/tmp/native-wifi-wire-XXXXXX";
static pthread_mutex_t owner_mutex=PTHREAD_MUTEX_INITIALIZER;
static unsigned publications,file_opens,workspace_allocations,workspace_frees;
static unsigned request_deletes,purge_receives,handler_calls,close_prepares,pending_at_handler;
static unsigned foreign_frees,async_begins,async_completes,queued_static;
static unsigned form_erases,chunk_erases;
static bool durable,fail_response,reboot_busy,advance_publication;
static uint64_t clock_offset;
static int64_t handler_started,handler_ended;
static const char *current_mode;
static struct {void *pointer;size_t size;} workspace_blocks[4];
static void *workspace;
static void event_unused(void) {}
static int64_t esp_timer_get_time(void) {struct timespec t;assert(!clock_gettime(CLOCK_MONOTONIC,&t));return (int64_t)t.tv_sec*1000000+t.tv_nsec/1000+(int64_t)clock_offset;}
static void vTaskDelay(unsigned ticks) {struct timespec t={.tv_sec=ticks/1000,.tv_nsec=(long)(ticks%1000)*1000000};while(nanosleep(&t,&t)&&errno==EINTR){} }
static int lwip_select(int n,fd_set *r,fd_set *w,fd_set *e,struct timeval *t) {return select(n,r,w,e,t);}
static bool deep_sleep_clock_begin_activity(void) {++activity_count;return true;}
static void deep_sleep_clock_end_activity(void) {assert(activity_count);--activity_count;}
static void display_settings_note_activity(void) {assert(activity_count);}
static TickType_t xTaskGetTickCount(void) {if(durable)assert(close_prepares==1&&!workspace);return (TickType_t)(esp_timer_get_time()/1000);}
static int xTaskCreate(void (*fn)(void *),const char *name,unsigned stack,void *arg,unsigned priority,TaskHandle_t *task) {(void)fn;assert(!strcmp(name,"web_reboot")&&stack==2048&&!arg&&priority==2);*task=(void *)1;return pdPASS;}
static void xTaskNotifyGive(TaskHandle_t task) {assert(task==(void *)1);if(durable)assert(close_prepares==1&&!workspace);}
static unsigned ulTaskNotifyTake(int clear,TickType_t delay) {(void)clear;(void)delay;abort();}
static void vTaskDelete(TaskHandle_t task) {assert(task==(void *)1);}
static void esp_restart(void) {abort();}
static void mapped_path(const char *path,char *out,size_t size) {bool data=!strncmp(path,"/spiffs/data/",13),www=!strncmp(path,"/spiffs/www/",12);assert(data||www);int n=snprintf(out,size,"%s/%s%s",directory,www?"www-":"",path+(data?13:12));assert(n>0&&(size_t)n<size);}
static FILE *mapped_open(const char *path,const char *mode) {++file_opens;char name[256];mapped_path(path,name,sizeof(name));return fopen(name,mode);}
static int mapped_fd_open(const char *path,int flags,int mode) {++file_opens;char name[256];mapped_path(path,name,sizeof(name));return open(name,flags,mode);}
static int mapped_stat(const char *path,struct stat *out) {char name[256];mapped_path(path,name,sizeof(name));return stat(name,out);}
static int mapped_remove(const char *path) {char name[256];mapped_path(path,name,sizeof(name));return remove(name);}
static int mapped_rename(const char *from,const char *to) {char a[256],b[256];mapped_path(from,a,sizeof(a));mapped_path(to,b,sizeof(b));if(!access(b,F_OK)){errno=EEXIST;return -1;}int r=rename(a,b);if(!r&&strstr(from,"wifi.csv.tmp")){++publications;durable=true;if(advance_publication)clock_offset+=UINT64_C(130000000);}return r;}
static SemaphoreHandle_t xSemaphoreCreateMutex(void) {return &owner_mutex;}
static int xSemaphoreTake(SemaphoreHandle_t lock,unsigned timeout) {assert(lock==&owner_mutex&&timeout==1000);return !pthread_mutex_lock(lock);}
static void xSemaphoreGive(SemaphoreHandle_t lock) {assert(lock==&owner_mutex&&!pthread_mutex_unlock(lock));}
static uint32_t esp_random(void) {return UINT32_C(0x12345678);}
static void esp_fill_random(void *out,size_t size) {memset(out,0x39,size);}
static esp_err_t radio_control_publish_playlist(const char *path,bool (*publish)(const char *,const char *)) {(void)path;(void)publish;return ESP_FAIL;}
static void websocket_service_notify_playlist_changed(void) {}
static void observed_upload_erase(void *p,size_t size) {if(size==sizeof(web_file_form_t))++form_erases;if(size==256)++chunk_erases;native_wifi_erase(p,size);}
static void *response_malloc(size_t size) {return fail_response&&durable?NULL:malloc(size);}
static void *workspace_calloc(size_t count,size_t size) {void *p=calloc(count,size);assert(p);for(size_t i=0;i<4;++i)if(!workspace_blocks[i].pointer){workspace_blocks[i].pointer=p;workspace_blocks[i].size=count*size;++workspace_allocations;workspace=p;return p;}abort();}
static void workspace_free(void *p) {if(!p)return;size_t index=4;for(size_t i=0;i<4;++i)if(workspace_blocks[i].pointer==p){index=i;break;}assert(index<4);for(size_t i=0;i<workspace_blocks[index].size;++i)assert(!((const uint8_t *)p)[i]);workspace_blocks[index].pointer=NULL;++workspace_frees;workspace=NULL;for(size_t i=0;i<4;++i)if(workspace_blocks[i].pointer)workspace=workspace_blocks[i].pointer;free(p);}
static void observed_prepare_close(httpd_handle_t hd,int fd,bool graceful) {assert(!close_prepares);++close_prepares;native_web_transport_prepare_close(hd,fd,graceful);}
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
static int httpd_resp_send_err(httpd_req_t *request,httpd_err_code_t code,const char *message) {assert(code==400||code==404||code==500);return httpd_resp_send_custom_err(request,code==400?"400 Bad Request":code==404?"404 Not Found":"500 Internal Server Error",message);}
static void esp_http_server_dispatch_event(int event,const void *data,size_t size) {assert(data&&size);if(event==HTTP_SERVER_EVENT_DISCONNECTED)++delete_count;}
static size_t strlcpy(char *dst,const char *src,size_t cap) {size_t size=strlen(src);if(cap){size_t n=MIN(cap-1,size);memcpy(dst,src,n);dst[n]=0;}return size;}
static void foreign_free(void *p) {assert(p);++foreign_frees;memset(p,0,32);free(p);}
static esp_err_t httpd_req_async_handler_begin(httpd_req_t *r,httpd_req_t **out) {++async_begins;*out=r;return ESP_OK;}
static esp_err_t httpd_req_async_handler_complete(httpd_req_t *r) {assert(r==&server.hd_req);++async_completes;return ESP_OK;}
static int xQueueSend(void *queue,const void *data,unsigned timeout) {assert(queue&&data&&!timeout);++queued_static;httpd_req_t *request=*(httpd_req_t *const *)data;return (serve_static_boundary(request)==ESP_OK)?pdTRUE:0;}
static const char *web_native_page(void) {return "synthetic static page seam";}
static bool web_ui_available(void) {return true;}
static const char *yoradio_index_html(void) {return "synthetic static page seam";}
static esp_err_t send_recovery_page(httpd_req_t *r) {return httpd_resp_sendstr(r,"synthetic recovery page seam");}
static const char *esp_get_idf_version(void) {return "host-pinned-sdk";}
static void native_state_snapshot(native_state_t *s,native_state_t *out) {*out=*s;}
#ifdef INTEGRATION_TLS
void integration_tls_prepare(const char *);
int integration_tls_open(void *,int);
void integration_tls_close(void *,int);
void integration_tls_release(void);
#endif
