/* Execute the production media/settings/HTTP code with in-memory platform I/O.
 * These tests do not validate ESP-IDF timing, Wi-Fi, TLS or physical display. */
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#include <assert.h>
#include <math.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "settings.h"
#include "display.h"
#include "media.h"
#include "network.h"
#include "services.h"
#include "text.h"
#include "web.h"
#include "dns_packet.h"
#include "factory_settings.h"
#include "../app/services/country_timezones.h"
#include "esp_flash.h"
#include "esp_partition.h"
#include "nvs.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "freertos/FreeRTOS.h"
#include "lwip/sockets.h"
#include "../app/media/photo_worker.h"
#include "factory_photo.h"

static unsigned checks;
#define CHECK(condition) do {++checks;if (!(condition)) {fprintf(stderr,"Check failed at %s:%d: %s\n",__FILE__,__LINE__,#condition);exit(1);}} while (0)
static uint8_t flash_bytes[0x1e7000],saved_nvs[1024];
static uint8_t factory_sector[4096],low_flash[ASSETS_BASE],tail_flash[0x18000];
static uint16_t panel[240*240];
static uint64_t cache_program_bytes,cache_erases;
static unsigned source_read_fault_after,source_read_faults;
static volatile LONG async_open;
static volatile LONG async_begin_failure,async_send_failures;
static size_t saved_nvs_length;
static int64_t clock_us;
static unsigned rendered_pixels,registered_routes,restart_requests,weather_requests;
static unsigned nvs_commits;
static unsigned route_success[48],route_errors[48];
static bool connected, setup_ap = true;
static uint16_t scan_count=1;
static esp_err_t scan_result=ESP_OK,write_result=ESP_OK;
static esp_err_t (*not_found)(httpd_req_t *,httpd_err_code_t);
static const esp_partition_t partition={ASSETS_BASE,sizeof(flash_bytes)};
static const httpd_uri_t *route_table[48];
static httpd_uri_t registered_handlers[48];
static void (*before_body_read)(void);
extern const unsigned char web_setup[],web_settings[],web_photo[];
extern const size_t web_setup_length,web_settings_length,web_photo_length;

int64_t esp_timer_get_time(void) {return clock_us;}
void native_port_enter(portMUX_TYPE *lock)
{while(InterlockedCompareExchange(lock,1,0)!=0)SwitchToThread();}
void native_port_exit(portMUX_TYPE *lock)
{assert(InterlockedExchange(lock,0)==1);}
SemaphoreHandle_t xSemaphoreCreateMutex(void) {return CreateSemaphoreW(NULL,1,1,NULL);}
int xSemaphoreTake(SemaphoreHandle_t m,unsigned ticks) {return WaitForSingleObject(m,ticks)==WAIT_OBJECT_0;}
int xSemaphoreGive(SemaphoreHandle_t m) {return ReleaseSemaphore(m,1,NULL)!=0;}
typedef struct {CRITICAL_SECTION lock;HANDLE items,slots,changed;volatile LONG receive_entered;unsigned capacity,bytes,read,write;uint8_t data[];} native_queue_t;
static native_queue_t *photo_test_queue;
QueueHandle_t xQueueCreate(unsigned count,unsigned bytes)
{native_queue_t *q=calloc(1,sizeof(*q)+(size_t)count*bytes);assert(q);InitializeCriticalSection(&q->lock);q->items=CreateSemaphoreW(NULL,0,count,NULL);q->slots=CreateSemaphoreW(NULL,count,count,NULL);q->changed=CreateEventW(NULL,FALSE,FALSE,NULL);q->capacity=count;q->bytes=bytes;photo_test_queue=q;return q;}
int xQueueSend(QueueHandle_t handle,const void *data,unsigned ticks)
{native_queue_t *q=handle;if(WaitForSingleObject(q->slots,ticks)!=WAIT_OBJECT_0)return 0;EnterCriticalSection(&q->lock);memcpy(q->data+(size_t)q->write*q->bytes,data,q->bytes);q->write=(q->write+1)%q->capacity;LeaveCriticalSection(&q->lock);ReleaseSemaphore(q->items,1,NULL);return 1;}
int xQueueReceive(QueueHandle_t handle,void *data,unsigned ticks)
{native_queue_t *q=handle;InterlockedIncrement(&q->receive_entered);SetEvent(q->changed);if(WaitForSingleObject(q->items,ticks)!=WAIT_OBJECT_0)return 0;EnterCriticalSection(&q->lock);memcpy(data,q->data+(size_t)q->read*q->bytes,q->bytes);q->read=(q->read+1)%q->capacity;LeaveCriticalSection(&q->lock);ReleaseSemaphore(q->slots,1,NULL);return 1;}
typedef struct {void (*task)(void *);void *context;} native_task_t;
static DWORD WINAPI native_task(void *context)
{native_task_t task=*(native_task_t *)context;free(context);task.task(task.context);return 0;}
int xTaskCreate(void (*task)(void *),const char *name,unsigned stack,void *argument,unsigned priority,void *handle)
{(void)stack;(void)priority;(void)handle;if(!strcmp(name,"tv-photo")){native_task_t *start=malloc(sizeof(*start));assert(start);*start=(native_task_t){task,argument};HANDLE thread=CreateThread(NULL,0,native_task,start,0,NULL);assert(thread);SetThreadPriority(thread,THREAD_PRIORITY_LOWEST);CloseHandle(thread);}return 1;}

void vTaskDelay(unsigned ticks) {clock_us+=(int64_t)ticks*1000;}
esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle) {(void)name;(void)mode;*handle=1;return ESP_OK;}
esp_err_t nvs_get_blob(nvs_handle_t handle,const char *key,void *data,size_t *length)
{(void)handle;(void)key;if (!saved_nvs_length) return ESP_ERR_NOT_FOUND;if (*length<saved_nvs_length)return ESP_ERR_INVALID_SIZE;memcpy(data,saved_nvs,saved_nvs_length);*length=saved_nvs_length;return ESP_OK;}
esp_err_t nvs_set_blob(nvs_handle_t handle,const char *key,const void *data,size_t length)
{(void)handle;(void)key;assert(length<=sizeof(saved_nvs));memcpy(saved_nvs,data,length);saved_nvs_length=length;return ESP_OK;}
esp_err_t nvs_commit(nvs_handle_t handle) {(void)handle;++nvs_commits;return ESP_OK;}
esp_err_t esp_flash_read(esp_flash_t *chip,void *data,uint32_t offset,uint32_t length)
{(void)chip;if(offset!=FACTORY_SETTINGS_OFFSET || length>sizeof(factory_sector))return ESP_ERR_INVALID_SIZE;memcpy(data,factory_sector,length);return ESP_OK;}
esp_err_t esp_flash_write(esp_flash_t *chip,const void *data,uint32_t offset,uint32_t length)
{(void)chip;if(write_result!=ESP_OK)return write_result;if(offset!=FACTORY_SETTINGS_OFFSET || length>sizeof(factory_sector))return ESP_ERR_INVALID_SIZE;memcpy(factory_sector,data,length);return ESP_OK;}
esp_err_t esp_flash_erase_region(esp_flash_t *chip,uint32_t offset,uint32_t length)
{(void)chip;assert(offset==FACTORY_SETTINGS_OFFSET && length==4096);memset(factory_sector,255,sizeof(factory_sector));return ESP_OK;}
const esp_partition_t *esp_partition_find_first(unsigned type,unsigned subtype,const char *label)
{(void)type;assert(subtype==0x40 && !strcmp(label,"assets"));return &partition;}
esp_err_t esp_partition_read(const esp_partition_t *p,size_t offset,void *data,size_t length)
{if (offset>p->size || length>p->size-offset) return ESP_ERR_INVALID_SIZE;memcpy(data,flash_bytes+offset,length);return ESP_OK;}
esp_err_t esp_partition_write(const esp_partition_t *p,size_t offset,const void *data,size_t length)
{if (offset>p->size || length>p->size-offset)return ESP_ERR_INVALID_SIZE;const uint8_t *bytes=data;for(size_t i=0;i<length;++i){assert((flash_bytes[offset+i]&bytes[i])==bytes[i]);flash_bytes[offset+i]&=bytes[i];}return ESP_OK;}
esp_err_t esp_partition_erase_range(const esp_partition_t *p,size_t offset,size_t length)
{if(offset>p->size || length>p->size-offset || offset%4096 || length%4096)return ESP_ERR_INVALID_SIZE;memset(flash_bytes+offset,255,length);return ESP_OK;}
static uint8_t *physical(uint32_t at,size_t bytes)
{
    if(at>0x400000 || bytes>0x400000-at)return NULL;
    if(at<ASSETS_BASE)return bytes<=ASSETS_BASE-at ? low_flash+at:NULL;
    at-=ASSETS_BASE;
    if(at<sizeof(flash_bytes))return bytes<=sizeof(flash_bytes)-at ? flash_bytes+at:NULL;
    at-=(uint32_t)sizeof(flash_bytes);
    if(at<sizeof(factory_sector))return bytes<=sizeof(factory_sector)-at ? factory_sector+at:NULL;
    at-=(uint32_t)sizeof(factory_sector);
    return bytes<=sizeof(tail_flash)-at ? tail_flash+at:NULL;
}
int native_photo_read(uint32_t at,void *data,size_t bytes)
{if(at==ASSETS_BASE && bytes==256 && source_read_fault_after && --source_read_fault_after==0){++source_read_faults;return -19;}uint8_t *p=physical(at,bytes);assert(p);memcpy(data,p,bytes);return 0;}
int native_photo_program(uint32_t at,const void *data,size_t bytes)
{uint8_t *p=physical(at,bytes);const uint8_t *input=data;assert(p);for(size_t i=0;i<bytes;++i)assert((p[i]&input[i])==input[i]);for(size_t i=0;i<bytes;++i)p[i]&=input[i];cache_program_bytes+=bytes;return 0;}
int native_photo_erase(uint32_t at)
{assert(at%4096==0);uint8_t *p=physical(at,4096);assert(p);memset(p,255,4096);++cache_erases;return 0;}
void display_blit(int x,int y,int width,int height,const uint16_t *pixels)
{assert(x>=0 && y>=0 && width>0 && height>0 && x+width<=240 && y+height<=240 && pixels);rendered_pixels+=width*height;for(int line=0;line<height;++line)memcpy(panel+(y+line)*240+x,pixels+line*width,(size_t)width*2);}
void display_fill(int x,int y,int width,int height,uint16_t color)
{
    /* Preserve complete pixels for old TJpgd vs new cache producer comparison. */
    assert(x>=0 && y>=0 && width>0 && height>0 && x+width<=240 && y+height<=240);
    for(int line=0;line<height;++line)for(int column=0;column<width;++column)panel[(y+line)*240+x+column]=color;
}

bool network_connected(void) {return connected;}
bool network_ap_active(void) {return setup_ap;}
void network_restart_later(void) {++restart_requests;}
void weather_request_update(void) {++weather_requests;}
esp_err_t network_scan(wifi_ap_record_t *records,uint16_t *count)
{if(scan_result!=ESP_OK)return scan_result;assert(*count>=scan_count);if(scan_count){strcpy((char *)records[0].ssid,"native test");records[0].rssi=-42;}*count=scan_count;return ESP_OK;}

esp_err_t httpd_resp_set_status(httpd_req_t *req,const char *status) {req->status=strtoul(status,NULL,10);return ESP_OK;}
esp_err_t httpd_resp_set_type(httpd_req_t *req,const char *type) {strcpy(req->response_type,type);return ESP_OK;}
esp_err_t httpd_resp_set_hdr(httpd_req_t *req,const char *name,const char *value)
{if(!strcmp(name,"Location"))strcpy(req->location,value);if(!strcmp(name,"Cache-Control"))strcpy(req->cache_control,value);return ESP_OK;}
esp_err_t httpd_resp_send(httpd_req_t *req,const char *data,int length)
{if(req->send_disconnected){InterlockedIncrement(&async_send_failures);return ESP_FAIL;}if(length<0)length=(int)strlen(data);assert((size_t)length<sizeof(req->response));memcpy(req->response,data,length);req->response[length]=0;req->response_length=length;req->response_complete=true;return ESP_OK;}
esp_err_t httpd_resp_send_chunk(httpd_req_t *req,const char *data,int length)
{
    /* Model the SDK's concatenated response body, including its empty final chunk. */
    if(req->response_complete)return ESP_FAIL;
    if(length<0)length=(int)strlen(data);
    if(!length){req->response_complete=true;return ESP_OK;}
    assert((size_t)length<sizeof(req->response)-req->response_length);
    if(length)memcpy(req->response+req->response_length,data,length);
    req->response_length+=length;req->response[req->response_length]=0;return ESP_OK;
}
esp_err_t httpd_resp_send_err(httpd_req_t *req,httpd_err_code_t code,const char *message) {req->status=code;return httpd_resp_send(req,message,-1);}
static const char *header(httpd_req_t *req,const char *name)
{if(!strcmp(name,"Content-Type"))return req->content_type;if(!strcmp(name,"Origin"))return req->origin;if(!strcmp(name,"Host"))return req->host;return NULL;}
size_t httpd_req_get_hdr_value_len(httpd_req_t *req,const char *name) {const char *value=header(req,name);return value?strlen(value):0;}
esp_err_t httpd_req_get_hdr_value_str(httpd_req_t *req,const char *name,char *out,size_t capacity)
{const char *value=header(req,name);if(!value || strlen(value)>=capacity)return ESP_ERR_INVALID_SIZE;strcpy(out,value);return ESP_OK;}
static httpd_req_t *socket_request;
int httpd_req_to_sockfd(httpd_req_t *req) {socket_request=req;return 42;}
int test_getsockopt(int socket,int level,int option,void *value,socklen_t *size)
{
    assert(socket==42 && level==SOL_SOCKET && option==SO_RCVTIMEO && *size==sizeof(struct timeval));
    if(socket_request->fail_timeout_get)return -1;
    struct timeval *timeout=value;
    timeout->tv_sec=(long)(socket_request->recv_timeout_us/1000000);
    timeout->tv_usec=(long)(socket_request->recv_timeout_us%1000000);
    return 0;
}
int test_setsockopt(int socket,int level,int option,const void *value,socklen_t size)
{
    assert(socket==42 && level==SOL_SOCKET && option==SO_RCVTIMEO && size==sizeof(struct timeval));
    if(++socket_request->timeout_set_calls==socket_request->fail_timeout_set_call)return -1;
    const struct timeval *timeout=value;
    socket_request->recv_timeout_us=(int64_t)timeout->tv_sec*1000000+timeout->tv_usec;
    assert(socket_request->recv_timeout_us>0);
    return 0;
}
int test_shutdown(int socket,int how)
{
    assert(socket==42 && how==SHUT_RD);
    socket_request->read_shutdown=true;
    ++socket_request->shutdown_calls;
    return 0;
}
int httpd_req_recv(httpd_req_t *req,char *out,size_t length)
{
    /* Allow a deterministic settings update while an HTTP body is in flight. */
    if(before_body_read) {
        void (*action)(void)=before_body_read;
        before_body_read=NULL;
        action();
    }
    ++req->recv_calls;
    if(req->read_shutdown || req->recv_disconnect)return 0;
    if(req->recv_timeouts || req->recv_step_us>req->recv_timeout_us)
    {
        if(req->recv_timeouts)--req->recv_timeouts;
        clock_us+=req->recv_timeout_us;
        return HTTPD_SOCK_ERR_TIMEOUT;
    }
    clock_us+=req->recv_step_us;
    if(length>req->content_len-req->position)length=req->content_len-req->position;
    unsigned block=req->recv_block_bytes ? req->recv_block_bytes : 137;
    if(length>block)length=block;
    memcpy(out,req->input+req->position,length);req->position+=length;return (int)length;
}
esp_err_t httpd_req_get_url_query_str(httpd_req_t *req,char *out,size_t capacity)
{const char *query=strchr(req->uri,'?');if(!query || strlen(query+1)>=capacity)return ESP_ERR_INVALID_SIZE;strcpy(out,query+1);return ESP_OK;}
esp_err_t httpd_query_key_value(const char *query,const char *key,char *out,size_t capacity)
{size_t n=strlen(key);for(const char *p=query;*p;){if(!strncmp(p,key,n) && p[n]=='='){p+=n+1;size_t length=strcspn(p,"&");if(length>=capacity)return ESP_ERR_INVALID_SIZE;memcpy(out,p,length);out[length]=0;return ESP_OK;}p=strchr(p,'&');if(!p)break;++p;}return ESP_ERR_NOT_FOUND;}
esp_err_t httpd_start(httpd_handle_t *server,const httpd_config_t *config) {(void)config;*server=(void *)1;return ESP_OK;}
esp_err_t httpd_stop(httpd_handle_t server) {(void)server;return ESP_OK;}
esp_err_t httpd_register_uri_handler(httpd_handle_t server,const httpd_uri_t *uri)
{
    /* ESP-IDF copies the registration; its caller may use a temporary descriptor. */
    (void)server;assert(registered_routes<48);
    registered_handlers[registered_routes]=*uri;
    route_table[registered_routes]=&registered_handlers[registered_routes];
    ++registered_routes;return ESP_OK;
}
esp_err_t httpd_register_err_handler(httpd_handle_t server,httpd_err_code_t code,esp_err_t (*handler)(httpd_req_t *,httpd_err_code_t))
{(void)server;assert(code==HTTPD_404_NOT_FOUND);not_found=handler;return ESP_OK;}

esp_err_t httpd_req_async_handler_begin(httpd_req_t *request,httpd_req_t **copy)
{if(InterlockedCompareExchange(&async_begin_failure,0,0))return ESP_ERR_NO_MEM;assert(!request->async_event);request->async_event=CreateEventW(NULL,TRUE,FALSE,NULL);assert(request->async_event);*copy=malloc(sizeof(**copy));assert(*copy);**copy=*request;(*copy)->async_original=request;InterlockedIncrement(&async_open);return ESP_OK;}
esp_err_t httpd_req_async_handler_complete(httpd_req_t *copy)
{httpd_req_t *original=copy->async_original;assert(original);HANDLE event=copy->async_event;*original=*copy;original->async_original=NULL;InterlockedDecrement(&async_open);free(copy);SetEvent(event);return ESP_OK;}
static httpd_req_t request;
static void prepare(const char *uri,const void *body,size_t length,const char *type)
{memset(&request,0,sizeof(request));request.uri=uri;request.input=body;request.content_len=length;request.content_type=type;request.host="192.168.43.1";request.status=200;request.recv_timeout_us=5000000;}
static void dispatch(httpd_method_t method)
{
    /* Model SDK path selection for the valid origin/absolute targets in these tests.
     * This adapter is not an HTTP parser: real SDK parsing is exercised in QEMU.
     * Keep the complete request URI and attach the registered handler's context. */
    const char *path=request.uri;
    if(!strncmp(path,"http://",7) || !strncmp(path,"https://",8))
    {
        const char *authority=strstr(path,"://")+3;
        path=strpbrk(authority,"/?#");
        CHECK(path && *path=='/');
    }
    size_t length=strcspn(path,"?#");
    for(unsigned i=0;i<registered_routes;++i)
        if(route_table[i]->method==method && strlen(route_table[i]->uri)==length && !memcmp(route_table[i]->uri,path,length))
        {
            request.user_ctx=route_table[i]->user_ctx;
            route_table[i]->handler(&request);
            if(request.async_event){HANDLE event=request.async_event;CHECK(WaitForSingleObject(event,30000)==WAIT_OBJECT_0);CloseHandle(event);request.async_event=NULL;}
            if(request.status==200)++route_success[i];else ++route_errors[i];
            return;
        }
    CHECK(not_found!=NULL);not_found(&request,HTTPD_404_NOT_FOUND);
}
static const char *post(const char *uri,const char *json,unsigned expected)
{prepare(uri,json,strlen(json),"application/json");dispatch(HTTP_POST);CHECK(request.status==expected);return request.response;}
static const char *get(const char *uri)
{prepare(uri,"",0,NULL);dispatch(HTTP_GET);CHECK(request.status==200);return request.response;}

static void test_settings(void)
{
    CHECK(settings_init()==ESP_OK);tv_settings_t s;settings_snapshot(&s);CHECK(settings_valid(&s));
    CHECK(!strcmp(get("/getclocktype"),"0"));
    post("/setclocktype","{\"clocktype\":\"3\"}",200);CHECK(!strcmp(get("/getclocktype"),"3"));
    post("/setclocktype","{\"clocktype\":4}",400);CHECK(!strcmp(get("/getclocktype"),"3"));
    post("/setclocktype","{\"clocktype\":2.1}",400);
    post("/setclocktype","{\"clocktype\":\"99999999999999999999999999\"}",400);
    post("/set_clock_color","{\"index\":0,\"color\":\"#123456\"}",200);CHECK(strstr(get("/get_clock_colors"),"#103452")!=NULL);
    post("/set_clock_color","{\"index\":3,\"color\":\"#ffffff\"}",400);
    post("/set_led_brightness","ledBrightness=73",200);CHECK(strstr(get("/get_led_brightness"),"73")!=NULL);
    post("/set_night_brightness","NightBrightness=19",200);CHECK(strstr(get("/get_night_brightness"),"19")!=NULL);
    post("/set_led_brightness","ledBrightness=101",400);
    post("/settings","{\"tempUnit\":1,\"hourFormat\":1,\"mileDisplay\":1,\"timeSync\":0,\"nightmode\":1}",200);
    post("/settings","{\"tempUnit\":0,\"hourFormat\":2}",400);settings_snapshot(&s);CHECK(s.fahrenheit==1);
    post("/set_checkbox_state","{\"checkbox_id\":\"file2-switch\",\"checked\":false}",200);CHECK(strstr(get("/get_checkbox_state"),"\"file2_switch\":false")!=NULL);
    post("/updateCity","{\"city\":\"London,gb\"}",200);settings_snapshot(&s);CHECK(!strcmp(s.city,"London") && !strcmp(s.country,"GB"));
    post("/updateCity","{\"city\":\"London\"}",400);
    post("/advancedset","{\"ntp\":\"pool.ntp.org\",\"openweathermapKey\":\"\",\"clickCount\":0}",200);CHECK(weather_requests==2);
    post("/set_display_time","{\"display_time\":60}",200);post("/set_display_time","{\"display_time\":61}",400);
    post("/SetNightStartTime","{\"StartTime\":18}",200);post("/SetNightStopTime","{\"StopTime\":12}",200);
    prepare("/settings","{\"hourFormat\":0}",16,"application/json");request.origin="http://evil.example";dispatch(HTTP_POST);CHECK(request.status==400);
    post("/configure","{\"ssid\":\"Home\",\"password\":\"12345678\"}",200);CHECK(restart_requests==1);
    CHECK(settings_flush()==ESP_OK);CHECK(settings_init()==ESP_OK);settings_snapshot(&s);CHECK(!strcmp(s.ssid,"Home") && s.wifi_mode==1);
    CHECK(rgb888_from_rgb565(rgb565_from_rgb888(0xffffff))==0xffffff);
    CHECK(rgb888_from_rgb565(rgb565_from_rgb888(0xff0000))==0xff0000);
}

static void test_theme_requests(void)
{
    /* Same-value commands advance only the transient UI revision, never flash data. */
    tv_settings_t original,current;
    uint32_t configuration,selection,next_configuration,next_selection;
    settings_snapshot_with_revisions(&original,&configuration,&selection);
    CHECK(settings_flush()==ESP_OK);
    unsigned committed=nvs_commits;
    char body[32];snprintf(body,sizeof(body),"{\"clocktype\":\"%u\"}",original.theme);
    for(unsigned repeat=0;repeat<3;++repeat) {
        post("/setclocktype",body,200);
        settings_snapshot_with_revisions(&current,&next_configuration,&next_selection);
        CHECK(!memcmp(&current,&original,sizeof(current)));
        CHECK(next_configuration==configuration && next_selection==selection+repeat+1);
        CHECK(settings_flush()==ESP_OK && nvs_commits==committed);
    }
    selection=next_selection;
    post("/setclocktype","{\"clocktype\":4}",400);
    CHECK(settings_select_theme(256)==ESP_ERR_INVALID_ARG);
    CHECK(settings_select_theme((unsigned)-1)==ESP_ERR_INVALID_ARG);
    settings_snapshot_with_revisions(&current,&next_configuration,&next_selection);
    CHECK(next_configuration==configuration && next_selection==selection);
    unsigned theme=(original.theme+1)%4;
    CHECK(settings_select_theme(theme)==ESP_OK);
    settings_snapshot_with_revisions(&current,&next_configuration,&next_selection);
    CHECK(current.theme==theme && next_configuration==configuration+1 && next_selection==selection+1);
    current.day_level=current.day_level==500?400:500;
    CHECK(settings_replace(&current)==ESP_OK);
    settings_snapshot_with_revisions(&current,&configuration,&selection);
    CHECK(configuration==next_configuration+1 && selection==next_selection);
    CHECK(settings_replace(&original)==ESP_OK && settings_flush()==ESP_OK);
    CHECK(settings_init()==ESP_OK);
    settings_snapshot_with_revisions(&current,&configuration,&selection);
    CHECK(!memcmp(&current,&original,sizeof(current)) && configuration==1 && selection==0);
    CHECK(sizeof(tv_settings_t)==364 && current.version==2);
}

static uint32_t le32(const uint8_t *data) {return data[0]|((uint32_t)data[1]<<8)|((uint32_t)data[2]<<16)|((uint32_t)data[3]<<24);}
static void test_factory_settings(void)
{
    /* Exercise an independent original-sector fixture, including mode 2 with
     * an existing SSID: it must stay in setup after a failed station attempt. */
    CHECK(sizeof(tv_settings_t)==364);
    CHECK(offsetof(tv_settings_t,wifi_mode)==341);
    CHECK(offsetof(tv_settings_t,photo_size)==344);
    tv_settings_t s; settings_snapshot(&s);
    uint8_t raw[FACTORY_SETTINGS_BYTES]; memset(raw,255,sizeof(raw));
    CHECK(!factory_settings_decode(raw,&s));
    memcpy(raw+4,"synthetic-ap\0",13);
    memcpy(raw+0x45,"\0",1);
    memcpy(raw+0x86,"10.0.2.2\0",9);
    memcpy(raw+0xc7,"GB\0",3);
    memcpy(raw+0xdb,"London\0",7);
    memcpy(raw+0x11c,"fixture-key\0",12);
    raw[0x160]=2; raw[0x161]=raw[0x162]=raw[0x163]=0;
    raw[0x168]=1; raw[0x169]=raw[0x16a]=raw[0x16b]=0;
    raw[0x1a4]=5; raw[0x1a5]=raw[0x1a6]=raw[0x1a7]=0;
    memcpy(factory_sector,raw,sizeof(raw));
    CHECK(settings_init()==ESP_OK); settings_snapshot(&s);
    CHECK(!strcmp(s.ssid,"synthetic-ap") && !s.password[0] && s.wifi_mode==2);
    CHECK(!strcmp(s.ntp,"10.0.2.2") && !strcmp(s.country,"GB") && !strcmp(s.city,"London"));
    CHECK(!strcmp(s.weather_key,"fixture-key") && s.theme==1 && s.photo_mask==5);
    CHECK(s.colors[0]==0xf800 && s.photo_seconds==5); /* erased fields use defaults */
    s.theme=3; CHECK(settings_replace(&s)==ESP_OK); CHECK(settings_flush()==ESP_OK);
    CHECK(le32(factory_sector+0x160)==2 && le32(factory_sector+0x168)==3);
    CHECK(le32(factory_sector)==5 && le32(factory_sector+0x1a4)==5);
    CHECK(le32(factory_sector+0x1a8)==s.photo_size[0]);
    CHECK(!strcmp((char *)factory_sector+0xdb,"London"));
    CHECK(factory_sector[FACTORY_SETTINGS_BYTES]==255);
    /* Version 2 mode zero is an explicit setup request, not legacy padding. */
    memset(factory_sector,255,sizeof(factory_sector));
    saved_nvs[341]=0;
    CHECK(settings_init()==ESP_OK); settings_snapshot(&s); CHECK(s.wifi_mode==0);
}

static void put32(uint8_t *out, uint32_t value)
{
    /* Build historical persisted fixtures independently of the current C ABI. */
    for (unsigned i=0;i<4;++i) out[i]=(uint8_t)(value>>(8*i));
}

static void legacy_settings_fixture(void)
{
    /* Literal version 1 offsets remain fixed even if the production struct moves. */
    memset(saved_nvs,0,sizeof(saved_nvs)); saved_nvs_length=344;
    put32(saved_nvs,1);
    strcpy((char *)saved_nvs+4,"old-ssid");
    strcpy((char *)saved_nvs+37,"12345678");
    strcpy((char *)saved_nvs+102,"OldCity");
    strcpy((char *)saved_nvs+167,"GB");
    strcpy((char *)saved_nvs+170,"fixture.invalid");
    strcpy((char *)saved_nvs+235,"disabled");
    const uint16_t levels_colors[]={730,180,0x1234,0x4567,0x89ab};
    for(unsigned i=0;i<5;++i) {
        saved_nvs[300+i*2]=(uint8_t)levels_colors[i];
        saved_nvs[301+i*2]=(uint8_t)(levels_colors[i]>>8);
    }
    const uint8_t tail[]={2,4,1,21,7,19,1,1,0,1,1,9,21,2};
    memcpy(saved_nvs+310,tail,sizeof(tail));
    for(unsigned i=0;i<5;++i)put32(saved_nvs+324+i*4,111*(i+1));
}

static void test_settings_migration(void)
{
    /* Preserve every old field, normalize only old padding, reject invalid blobs,
     * and retain the original raw sector's precedence over either native version. */
    static const tv_settings_t expected={.version=TV_SETTINGS_VERSION,.ssid="old-ssid",.password="12345678",
        .city="OldCity",.country="GB",.ntp="fixture.invalid",.weather_key="disabled",
        .day_level=730,.night_level=180,.colors={0x1234,0x4567,0x89ab},
        .theme=2,.animation=4,.date_format=1,.night_start=21,.night_stop=7,.photo_seconds=19,
        .fahrenheit=1,.hour12=1,.miles=0,.browser_time=1,.night_mode=1,.click_count=9,
        .photo_mask=21,.wifi_mode=2,.photo_size={111,222,333,444,555}};
    tv_settings_t s, original;
    settings_snapshot(&original);
    memset(factory_sector,255,sizeof(factory_sector)); legacy_settings_fixture();
    CHECK(settings_init()==ESP_OK); settings_snapshot(&s);
    CHECK(!memcmp(&s,&expected,sizeof(s)) && settings_valid(&s));
    CHECK(settings_flush()==ESP_OK && saved_nvs_length==364 && le32(saved_nvs)==2);
    memset(factory_sector,255,sizeof(factory_sector));
    CHECK(settings_init()==ESP_OK); settings_snapshot(&s); CHECK(!memcmp(&s,&expected,sizeof(s)));
    for(unsigned empty=0;empty<2;++empty) {
        legacy_settings_fixture(); saved_nvs[323]=0; if(empty)saved_nvs[4]=0;
        CHECK(settings_init()==ESP_OK); settings_snapshot(&s);
        CHECK(s.wifi_mode==(empty?2:1) && !strcmp(s.country,"GB"));
    }
    for(unsigned bad=0;bad<4;++bad) {
        legacy_settings_fixture();
        if(bad==0)put32(saved_nvs,99);
        if(bad==1)saved_nvs_length=343;
        if(bad==2)memset(saved_nvs+167,'X',3);
        if(bad==3)memset(saved_nvs+170,'X',65);
        CHECK(settings_init()==ESP_OK); settings_snapshot(&s);
        CHECK(s.version==2 && !strcmp(s.city,"Shenzhen") && !strcmp(s.country,"CN"));
    }
    s=expected; strcpy(s.country,"AU-W"); strcpy(s.city,"Perth");
    factory_settings_encode(&s,factory_sector); legacy_settings_fixture();
    CHECK(settings_init()==ESP_OK); settings_snapshot(&s);
    CHECK(!strcmp(s.country,"AU-W") && !strcmp(s.city,"Perth"));
    CHECK(settings_flush()==ESP_OK && saved_nvs_length==364);
    CHECK(!strcmp((char *)saved_nvs+offsetof(tv_settings_t,country),"AU-W"));
    CHECK(settings_replace(&original)==ESP_OK && settings_flush()==ESP_OK);
}

static void test_regional_settings(void)
{
    /* Every recovered key must survive HTTP, raw import/export and cold settings load. */
    tv_settings_t s,restored;
    uint8_t raw[FACTORY_SETTINGS_BYTES];
    for(unsigned i=0;i<sizeof(country_timezones)/sizeof(country_timezones[0]);++i) {
        char json[128]; snprintf(json,sizeof(json),"{\"city\":\"Fixture,%s\"}",country_timezones[i].country);
        post("/updateCity",json,200); settings_snapshot(&s);
        CHECK(!strcmp(s.country,country_timezones[i].country));
        factory_settings_encode(&s,raw);
        CHECK(!strcmp((char *)raw+0xc7,country_timezones[i].country));
        CHECK(!strcmp((char *)raw+0xdb,"Fixture"));
        restored=s; strcpy(restored.country,"CN");
        CHECK(factory_settings_decode(raw,&restored) && !strcmp(restored.country,s.country));
        CHECK(settings_flush()==ESP_OK && settings_init()==ESP_OK); settings_snapshot(&restored);
        CHECK(!strcmp(restored.country,s.country) && restored.version==TV_SETTINGS_VERSION);
    }
    post("/updateCity","{\"city\":\"Perth,au-w\"}",200); settings_snapshot(&s); CHECK(!strcmp(s.country,"AU-W"));
    post("/updateCity","{\"city\":\"Honolulu\xef\xbc\x8c" "us-h\"}",200); settings_snapshot(&s); CHECK(!strcmp(s.country,"US-H"));
    char city[65],json[160]; memset(city,'C',64); city[64]=0;
    snprintf(json,sizeof(json),"{\"city\":\"%s\xef\xbc\x8c" "ZZ-ABCDEFGHIJKLMNOP\"}",city);
    post("/updateCity",json,200); settings_snapshot(&s);
    CHECK(!strcmp(s.city,city) && strlen(s.country)==19 && settings_valid(&s));
    CHECK(settings_flush()==ESP_OK && settings_init()==ESP_OK); settings_snapshot(&restored);
    CHECK(!strcmp(s.country,restored.country) && !strcmp(restored.city,city));
    const char *invalid[]={"","U","USA","US-","U1","US_1","US-H/","US-H&x","US-H%20","US-ABCDEFGHIJKLMNOPQ"};
    for(unsigned i=0;i<sizeof(invalid)/sizeof(invalid[0]);++i) {
        snprintf(json,sizeof(json),"{\"city\":\"Fixture,%s\"}",invalid[i]);
        post("/updateCity",json,400); settings_snapshot(&restored); CHECK(!memcmp(&s,&restored,sizeof(s)));
    }
    factory_settings_encode(&s,raw); memset(raw+0xc7,'A',20);
    CHECK(!factory_settings_decode(raw,&restored));
    post("/updateCity","{\"city\":\"London,GB\"}",200);
}

static void test_utf8(void)
{
    /* Check scalar boundaries, malformed sequences and complete-prefix byte budgets. */
    static const struct { const char *text; size_t bytes; uint32_t scalar; size_t consumed; } cases[] = {
        {"A",1,0x41,1}, {"\xc2\x80",2,0x80,2}, {"\xdf\xbf",2,0x7ff,2},
        {"\xe0\xa0\x80",3,0x800,3}, {"\xe2\x82\xac",3,0x20ac,3},
        {"\xf0\x90\x80\x80",4,0x10000,4}, {"\xf4\x8f\xbf\xbf",4,0x10ffff,4},
        {"\xc0\x80",2,0xfffd,1}, {"\xe0\x80\x80",3,0xfffd,1},
        {"\xed\xa0\x80",3,0xfffd,1}, {"\xf4\x90\x80\x80",4,0xfffd,1},
        {"\xe2" "A",2,0xfffd,1}, {"\xc2\xa2",1,0xfffd,1}, {"\x80",1,0xfffd,1}
    };
    for (unsigned i=0;i<sizeof(cases)/sizeof(cases[0]);++i) {
        size_t consumed=99;
        CHECK(text_utf8_decode(cases[i].text,cases[i].bytes,&consumed)==cases[i].scalar);
        CHECK(consumed==cases[i].consumed);
    }
    size_t consumed=99;
    CHECK(text_utf8_decode(NULL,4,&consumed)==0 && consumed==0);
    CHECK(text_utf8_decode("A",0,&consumed)==0 && consumed==0);
    CHECK(text_utf8_decode("A",1,NULL)==0);
    CHECK(text_utf8_decode("",1,&consumed)==0 && consumed==0);
    char output[20];
    CHECK(text_utf8_copy(output,sizeof(output),"1234567890123\xc3\xa9",15)==15);
    CHECK(!strcmp(output,"1234567890123\xc3\xa9"));
    CHECK(text_utf8_copy(output,sizeof(output),"12345678901234\xc3\xa9",15)==14);
    CHECK(!strcmp(output,"12345678901234"));
    CHECK(text_utf8_copy(output,sizeof(output),"\xe2" "A",15)==2 && !strcmp(output,"?A"));
    CHECK(text_utf8_copy(output,3,"\xe2\x82\xac",15)==0 && !output[0]);
    CHECK(text_utf8_copy(output,4,"\xe2\x82\xac",15)==3 && !strcmp(output,"\xe2\x82\xac"));
    strcpy(output,"\xc0\x80" "A");
    CHECK(text_utf8_copy(output,sizeof(output),output,15)==3 && !strcmp(output,"??A"));
    unsigned char guards[6]; memset(guards,0xa5,sizeof(guards));
    CHECK(text_utf8_copy((char *)guards+1,4,"\xe2\x82\xac",15)==3);
    CHECK(guards[0]==0xa5 && guards[4]==0 && guards[5]==0xa5);
    CHECK(text_utf8_copy(output,1,"A",15)==0 && !output[0]);
    output[0]='X'; CHECK(text_utf8_copy(output,0,"A",15)==0 && output[0]=='X');
    CHECK(text_utf8_copy(output,sizeof(output),NULL,15)==0 && !output[0]);
}

static void test_weather(void)
{
    /* Values come from a synthetic OpenWeather Kelvin payload, not live data. */
    tv_settings_t s; settings_snapshot(&s);
    const char body[]={"{\"main\":{\"temp\":293.99,\"humidity\":73,\"temp_min\":292.2,\"temp_max\":295.8},"
        "\"wind\":{\"speed\":3.7,\"deg\":350},\"timezone\":3600,"
        "\"weather\":[{\"icon\":\"02d\",\"main\":\"Clouds\",\"description\":\"scattered clouds\"}]}"};
    weather_snapshot_t weather;
    CHECK(weather_parse_response(body,strlen(body),&s,&weather));
    CHECK(weather.valid && weather.temperature_c==20 && weather.humidity==73);
    CHECK(fabs(weather.temperature_min_c-19.05)<0.000001 && fabs(weather.temperature_max_c-22.65)<0.000001);
    CHECK(weather.wind_mps==3.7 && weather.timezone_seconds==3600);
    CHECK(!strcmp(weather.main,"Clouds") && !strcmp(weather.description,"scattered cloud"));
    CHECK(!strcmp(weather.wind_direction,"North") && !strcmp(weather.icon,"02d"));
    CHECK(!strcmp(weather.city,"London") && !strcmp(weather.country,"GB"));
    const char unicode[]={"{\"main\":{\"temp\":293,\"humidity\":50},\"wind\":{\"speed\":1},"
        "\"weather\":[{\"icon\":\"02d\",\"main\":\"12345678901234\xc3\xa9\","
        "\"description\":\"1234567890123\xc3\xa9\"}]}"};
    CHECK(weather_parse_response(unicode,strlen(unicode),&s,&weather));
    CHECK(!strcmp(weather.main,"12345678901234"));
    CHECK(!strcmp(weather.description,"1234567890123\xc3\xa9"));
    CHECK(!weather_parse_response("{}",2,&s,&weather));
    CHECK(!weather_parse_response(body,10,&s,&weather));
    const char invalid[]={"{\"main\":{\"temp\":293,\"humidity\":101},\"wind\":{\"speed\":1},\"weather\":[{\"icon\":\"02d\"}]}"};
    CHECK(!weather_parse_response(invalid,strlen(invalid),&s,&weather));
    const char cold[]={"{\"main\":{\"temp\":270.9,\"humidity\":0},\"wind\":{\"speed\":0,\"deg\":90},\"weather\":[{\"icon\":\"13n\"}]}"};
    CHECK(weather_parse_response(cold,strlen(cold),&s,&weather));
    CHECK(weather.temperature_c==-2 && !strcmp(weather.wind_direction,"East"));
    /* Literal factory strings and all half-open sector boundaries, including
     * 348.75/360 wrapping to North. A Ghidra symbol name hides its hyphen. */
    static const char *directions[]={"North","North-Northeast","Northeast","East-Northeast",
        "East","East-Southeast","Southeast","South-Southeast","South","South-Southwest",
        "Southwest","West-Southwest","West","West-Northwest","Northwest","North-Northwest"};
    char directional[256];
    for(unsigned i=0;i<16;++i){
        const double angles[]={i*22.5, i*22.5+11.25, i*22.5+11.25-0.00001};
        for(unsigned j=0;j<3;++j){
            snprintf(directional,sizeof(directional),"{\"main\":{\"temp\":293,\"humidity\":50},"
                "\"wind\":{\"speed\":1,\"deg\":%.5f},\"weather\":[{\"icon\":\"02d\"}]}",angles[j]);
            CHECK(weather_parse_response(directional,strlen(directional),&s,&weather));
            CHECK(!strcmp(weather.wind_direction,directions[j==1?(i+1)%16:i]));
        }
    }
}
static void test_assets(void)
{
    CHECK(media_init()==ESP_OK);tv_settings_t s;settings_snapshot(&s);
    uint16_t *expected=malloc(sizeof(panel));CHECK(expected);
    for(unsigned i=0;i<PHOTO_COUNT;++i) {
        CHECK(media_draw_jpeg(ASSETS_BASE+i*PHOTO_SLOT_BYTES,s.photo_size[i],0,0)==ESP_OK);
        memcpy(expected,panel,sizeof(panel));rendered_pixels=0;
        CHECK(media_draw_photo(i)==ESP_OK);CHECK(rendered_pixels==240*240);
        CHECK(!memcmp(expected,panel,sizeof(panel)));
        uint64_t programs=cache_program_bytes,erases=cache_erases;
        memset(panel,0,sizeof(panel));CHECK(media_draw_photo_cached(i)==ESP_OK);
        CHECK(!memcmp(expected,panel,sizeof(panel)));
        CHECK(cache_program_bytes==programs && cache_erases==erases);
    }
    free(expected);
    unsigned frames=0;const unsigned counts[]={19,15,25,16,23};
    for(unsigned animation=0;animation<5;++animation){CHECK(media_animation_frames(animation)==counts[animation]);for(unsigned frame=0;frame<counts[animation];++frame){rendered_pixels=0;CHECK(media_draw_animation(animation,frame,83,143)==ESP_OK);CHECK(rendered_pixels==74*74);++frames;}}
    CHECK(frames==98);CHECK(media_draw_animation(0,19,0,0)!=ESP_OK);
    static const char *const codes[]={"01d","01n","02d","02n","03d","03n","04d","04n","09d","09n","10d","10n","11d","11n","13d","13n","50d","50n"};
    for(unsigned i=0;i<18;++i){rendered_pixels=0;CHECK(media_draw_weather(codes[i],178,155)==ESP_OK);CHECK(rendered_pixels==3600);}
    const unsigned offsets[]={0x3ba800,0x3be400,0x3c2000,0x3c5c00};
    for(unsigned i=0;i<4;++i)CHECK(media_draw_jpeg(offsets[i],WEATHER_SLOT_BYTES,0,0)==ESP_OK);
    uint8_t data[4];CHECK(media_read(ASSETS_BASE-1,data,4)!=ESP_OK);CHECK(media_read(ASSETS_BASE+partition.size-2,data,4)!=ESP_OK);
    CHECK(le32(flash_bytes+ANIMATION_BASE-ASSETS_BASE+3)<=ANIMATION_SLOT_BYTES);
}

static void upload_entire(unsigned slot,const uint8_t *photo,size_t length,bool valid)
{
    unsigned chunks=(unsigned)(length+4095)/4096;
    CHECK(photo_upload_start(slot,(uint32_t)length,chunks)==ESP_OK);
    CHECK(media_draw_photo(0)!=ESP_OK);
    for(unsigned i=0;i<chunks;++i){size_t block=length-i*4096;if(block>4096)block=4096;CHECK(photo_upload_chunk(slot,i,chunks,photo+i*4096,block)==ESP_OK);}
    CHECK((photo_upload_finish(slot)==ESP_OK)==valid);
}

static void test_uploads(void)
{
    tv_settings_t s;settings_snapshot(&s);size_t length=s.photo_size[0];uint8_t *photo=malloc(length);CHECK(photo!=NULL);memcpy(photo,flash_bytes,length);
    CHECK(photo_upload_start(0,PHOTO_SLOT_BYTES+1,26)!=ESP_OK);CHECK(photo_upload_start(5,100,1)!=ESP_OK);CHECK(photo_upload_start(0,100,2)!=ESP_OK);
    unsigned chunks=(unsigned)(length+4095)/4096;
    CHECK(photo_upload_start(0,(uint32_t)length,chunks)==ESP_OK);CHECK(photo_upload_start(1,100,1)!=ESP_OK);
    CHECK(photo_upload_chunk(0,1,chunks,photo+4096,4096)!=ESP_OK);
    CHECK(photo_upload_chunk(0,0,chunks,photo,4096)==ESP_OK);CHECK(photo_upload_chunk(0,0,chunks,photo,4096)==ESP_OK);
    photo[0]^=1;CHECK(photo_upload_chunk(0,0,chunks,photo,4096)!=ESP_OK);photo[0]^=1;
    CHECK(photo_upload_finish(0)!=ESP_OK);
    for(unsigned i=1;i<chunks;++i){size_t block=length-i*4096;if(block>4096)block=4096;CHECK(photo_upload_chunk(0,i,chunks,photo+i*4096,block)==ESP_OK);}
    CHECK(photo_upload_finish(0)==ESP_OK);CHECK(!memcmp(photo,flash_bytes,length));
    uint8_t *unsafe=malloc(length+8);CHECK(unsafe!=NULL);memcpy(unsafe,photo,2);const uint8_t exif[]={255,0xe1,0,6,'E','X','I','F'};memcpy(unsafe+2,exif,8);memcpy(unsafe+10,photo+2,length-2);
    upload_entire(1,unsafe,length+8,false);settings_snapshot(&s);CHECK(s.photo_size[1]==0);
    memcpy(unsafe,photo,length);memcpy(unsafe+length,exif,8);unsafe[length+6]=255;unsafe[length+7]=0xd9;
    upload_entire(1,unsafe,length+8,false); /* A decoder alone ignores trailing metadata. */
    uint8_t wrong_size[]={255,0xd8,255,0xc0,0,8,8,0,100,0,100,3,255,0xda,0,2,255,0xd9};upload_entire(1,wrong_size,sizeof(wrong_size),false);
    CHECK(photo_upload_start(2,100,1)==ESP_OK);clock_us+=120000001;CHECK(!media_upload_active());CHECK(photo_upload_start(2,100,1)==ESP_OK);clock_us+=120000001;
    free(unsafe);free(photo);
}

static size_t append_part(char *body,size_t pos,const char *name,const void *data,size_t length)
{pos+=sprintf(body+pos,"--test-boundary\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n",name);memcpy(body+pos,data,length);pos+=length;memcpy(body+pos,"\r\n",2);return pos+2;}
static void test_multipart(void)
{
    char body[6000];uint8_t binary[20]={255,0xd8,0,'-', '-', '-',13,10};size_t pos=0;
    CHECK(photo_upload_start(4,sizeof(binary),1)==ESP_OK);
    pos=append_part(body,pos,"chunk",binary,sizeof(binary));pos=append_part(body,pos,"file_number","5",1);pos=append_part(body,pos,"chunk_index","0",1);pos=append_part(body,pos,"total_chunks","1",1);pos+=sprintf(body+pos,"--test-boundary--\r\n");
    prepare("/upload_chunk",body,pos,"multipart/form-data; boundary=test-boundary");dispatch(HTTP_POST);CHECK(request.status==200);CHECK(!memcmp(flash_bytes+4*PHOTO_SLOT_BYTES,binary,sizeof(binary)));
    prepare("/upload_chunk",body,pos-4,"multipart/form-data; boundary=test-boundary");dispatch(HTTP_POST);CHECK(request.status==400);
    prepare("/upload_chunk",body,pos,"multipart/form-data; boundary=incorrect");dispatch(HTTP_POST);CHECK(request.status==400);
    clock_us+=120000001;
    prepare("/get_Photo_File?file=1&chunk=0&size=10240","",0,NULL);web_photo_get(&request);CHECK(request.status==200 && request.response_length==10240);
    prepare("/get_Photo_File?file=1&chunk=100&size=12288","",0,NULL);web_photo_get(&request);CHECK(request.status==400);
}

static void test_dns(void)
{
    const uint8_t question[]={0x12,0x34,1,0,0,1,0,0,0,0,0,0,3,'w','w','w',7,'e','x','a','m','p','l','e',3,'c','o','m',0,0,1,0,1};
    uint8_t packet[514];memset(packet,0x5a,sizeof(packet));memcpy(packet,question,sizeof(question));
    size_t length=captive_dns_reply(packet,sizeof(question),512);CHECK(length==sizeof(question)+16);CHECK(packet[0]==0x12 && packet[1]==0x34 && packet[7]==1);CHECK(!memcmp(packet+length-4,"\xc0\xa8\x2b\x01",4));CHECK(packet[512]==0x5a && packet[513]==0x5a);
    for(size_t n=0;n<sizeof(question);++n){memcpy(packet,question,sizeof(question));CHECK(captive_dns_reply(packet,n,512)==0);}
    memcpy(packet,question,sizeof(question));CHECK(captive_dns_reply(packet,sizeof(question),sizeof(question)+15)==0);
    memcpy(packet,question,sizeof(question));packet[12]=0xc0;CHECK(captive_dns_reply(packet,sizeof(question),512)==0);
    memcpy(packet,question,sizeof(question));packet[12]=64;CHECK(captive_dns_reply(packet,sizeof(question),512)==0);
    memcpy(packet,question,sizeof(question));packet[5]=2;CHECK(captive_dns_reply(packet,sizeof(question),512)==0);
    memcpy(packet,question,sizeof(question));packet[30]=28;CHECK(captive_dns_reply(packet,sizeof(question),512)==sizeof(question));CHECK(packet[7]==0);
    memset(packet,0,512);packet[5]=1;size_t pos=12;for(unsigned i=0;i<4;++i){packet[pos++]=63;memset(packet+pos,'a',63);pos+=63;}packet[pos++]=0;packet[pos++]=0;packet[pos++]=1;packet[pos++]=0;packet[pos++]=1;CHECK(captive_dns_reply(packet,pos,512)==0);
    CHECK(captive_dns_reply(packet,513,512)==0);
}

static void test_advanced_page(void)
{
    /* The editor must show the saved NTP hostname without exposing markup or the key. */
    tv_settings_t original,s;
    settings_snapshot(&original);s=original;
    strcpy(s.ntp,"clock-test.invalid");
    strcpy(s.weather_key,"never-render-this-fixture-key");
    CHECK(settings_replace(&s)==ESP_OK);
    const char *html=get("/advanced");
    CHECK(strstr(html,"value=\"clock-test.invalid\"")!=NULL);
    CHECK(strstr(html,s.weather_key)==NULL);
    strcpy(s.ntp,"time\"><&'host");
    CHECK(settings_replace(&s)==ESP_OK);
    html=get("/advanced");
    CHECK(strstr(html,"value=\"time&quot;&gt;&lt;&amp;&#39;host\"")!=NULL);
    CHECK(strstr(html,s.ntp)==NULL && strstr(html,s.weather_key)==NULL);
    memset(s.ntp,'\"',sizeof(s.ntp)-1);s.ntp[sizeof(s.ntp)-1]=0;
    CHECK(settings_replace(&s)==ESP_OK);
    html=get("/advanced");
    char escaped[6*(sizeof(s.ntp)-1)+1];
    for(unsigned i=0;i<sizeof(s.ntp)-1;++i)memcpy(escaped+6*i,"&quot;",6);
    escaped[sizeof(escaped)-1]=0;
    CHECK(strstr(html,escaped)!=NULL && strstr(html,s.weather_key)==NULL);
    s.ntp[0]=0;CHECK(settings_replace(&s)==ESP_OK);
    html=get("/advanced");
    CHECK(strstr(html,"value=\"\"")!=NULL && strstr(html,"</body></html>")!=NULL);
    CHECK(settings_replace(&original)==ESP_OK);
}

#include "http_contracts.inc"
#include "http_captive.inc"
#include "city_theme.inc"
#include "photo_owner.inc"
#include "photo_prefetch.inc"

static void digest(const void *data,size_t bytes,char output[65])
{
    /* Independent OS digest covers the full row-major RGB565 panel bytes. */
    BCRYPT_ALG_HANDLE algorithm;BCRYPT_HASH_HANDLE hash;uint8_t value[32];
    CHECK(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)==0);
    CHECK(BCryptCreateHash(algorithm,&hash,NULL,0,NULL,0,0)==0);
    CHECK(BCryptHashData(hash,(PUCHAR)data,(ULONG)bytes,0)==0);
    CHECK(BCryptFinishHash(hash,value,32,0)==0);
    CHECK(BCryptDestroyHash(hash)==0);CHECK(BCryptCloseAlgorithmProvider(algorithm,0)==0);
    for(unsigned i=0;i<32;++i)sprintf(output+i*2,"%02x",value[i]);
}

static void test_extended_photos(const char *folder)
{
    /* Actual HTTP worker path accepts12-bit CMYK, gives precise resource
     * refusals and recovers, while ordinary settings and other slots survive. */
    const char *names[]={"flat-cmyk-progressive-12.jpg","flat-sampling44-8.jpg","flat-sampling44-12.jpg","flat-cmyk-progressive-12.jpg"};
    const char *fixture_hash[]={"bd841b2529a90c4e02b8043154c79de008ada85bd50d2dca4baf7223f2505ed4",NULL,NULL,"bd841b2529a90c4e02b8043154c79de008ada85bd50d2dca4baf7223f2505ed4"};
    char others_before[65],others_after[65];digest(flash_bytes,4*PHOTO_SLOT_BYTES,others_before);
    tv_settings_t before,after;settings_snapshot(&before);
    extern size_t native_photo_available,native_photo_service_free;
    for(unsigned case_number=0;case_number<4;++case_number) {
        char path[1024];snprintf(path,sizeof(path),"%s/%s",folder,names[case_number]);
        FILE *file=fopen(path,"rb");CHECK(file);uint8_t image[4096];size_t bytes=fread(image,1,sizeof(image),file);CHECK(bytes>4 && bytes<sizeof(image));CHECK(fgetc(file)==EOF);fclose(file);
        if(fixture_hash[case_number]){char value[65];digest(image,bytes,value);CHECK(!strcmp(value,fixture_hash[case_number]));}
        if(case_number==0) {
            /* Refuse the context allocation before any decoder/backing work,
             * retain exact resource reason, then reuse the same owner normally. */
            CHECK(photo_upload_start(4,(uint32_t)bytes,1)==ESP_OK);
            CHECK(photo_upload_chunk(4,0,1,image,bytes)==ESP_OK);
            native_photo_available=1;photo_diagnostic_t diagnostic;
            CHECK(photo_upload_finish_detailed(4,&diagnostic)!=ESP_OK);
            CHECK(diagnostic.status==PHOTO_MEMORY && diagnostic.required>1 && diagnostic.available==1);
            char reason[192];photo_diagnostic_describe(&diagnostic,reason,sizeof(reason));
            CHECK(strstr(reason,"heap-headroom; required=") && strstr(reason,"available=1"));
            CHECK(!media_upload_active());settings_snapshot(&after);CHECK(after.photo_size[4]==0);
            native_photo_available=SIZE_MAX;
            CHECK(photo_upload_start(4,(uint32_t)bytes,1)==ESP_OK);
            CHECK(photo_upload_chunk(4,0,1,image,bytes)==ESP_OK);
            native_photo_service_free=1;
            CHECK(photo_upload_finish_detailed(4,&diagnostic)!=ESP_OK);
            CHECK(diagnostic.status==PHOTO_MEMORY && diagnostic.service_memory && diagnostic.required==16384 && diagnostic.available==1);
            photo_diagnostic_describe(&diagnostic,reason,sizeof(reason));
            CHECK(!strcmp(reason,"service-heap-reserve; required=16384 available=1"));
            CHECK(!media_upload_active());settings_snapshot(&after);CHECK(after.photo_size[4]==0);
            native_photo_service_free=SIZE_MAX;
        }
        char json[192];snprintf(json,sizeof(json),"{\"file_number\":5,\"file_size\":%u,\"total_chunks\":1}",(unsigned)bytes);
        post("/start_upload",json,200);
        char body[5000];size_t position=append_part(body,0,"file_number","5",1);
        position=append_part(body,position,"chunk_index","0",1);position=append_part(body,position,"total_chunks","1",1);position=append_part(body,position,"chunk",image,bytes);
        memcpy(body+position,"--test-boundary--\r\n",19);position+=19;
        prepare("/upload_chunk",body,position,"multipart/form-data; boundary=test-boundary");dispatch(HTTP_POST);CHECK(request.status==200);
        bool valid=case_number==0 || case_number==3;
        post("/finish_upload","{\"file_number\":5,\"file_name\":\"file5.jpg\"}",valid ? 200:400);
        settings_snapshot(&after);CHECK(after.photo_size[4]==(valid ? bytes:0));
        if(valid) {
            uint64_t programs=cache_program_bytes,erases=cache_erases;
            CHECK(media_draw_photo_cached(4)==ESP_OK);char value[65];digest(panel,sizeof(panel),value);
            CHECK(!strcmp(value,"09d3a79920a60f62fd5be6adb090f666dbcacc0cbc6412df450fbf14003efda6"));
            CHECK(cache_program_bytes==programs && cache_erases==erases);
        } else if(case_number==1) {
            CHECK(strstr(request.response,"backing-capacity"));CHECK(strstr(request.response,"required=524288 available=460800"));
        } else {
            CHECK(strstr(request.response,"library-pool-limit"));CHECK(strstr(request.response,"required=70760 available=65536"));
        }
    }
    digest(flash_bytes,4*PHOTO_SLOT_BYTES,others_after);CHECK(!strcmp(others_before,others_after));
    after.photo_size[4]=before.photo_size[4];CHECK(!memcmp(&before,&after,sizeof(before)));
}

int main(int argc,char **argv)
{
    memset(factory_sector,255,sizeof(factory_sector));memset(low_flash,255,sizeof(low_flash));memset(tail_flash,255,sizeof(tail_flash));
    CHECK(argc==4);FILE *file=fopen(argv[1],"rb");CHECK(file!=NULL);CHECK(fread(flash_bytes,1,sizeof(flash_bytes),file)==sizeof(flash_bytes));CHECK(fgetc(file)==EOF);fclose(file);
    CHECK(web_start()==ESP_OK);CHECK(registered_routes==40);
    for(unsigned i=0;i<registered_routes;++i)for(unsigned j=i+1;j<registered_routes;++j)CHECK(route_table[i]->method!=route_table[j]->method || strcmp(route_table[i]->uri,route_table[j]->uri));
    test_settings();test_theme_requests();test_city_theme_requests();test_factory_settings();test_settings_migration();test_regional_settings();test_utf8();test_weather();test_assets();test_http_contracts();test_advanced_page();test_uploads();test_multipart();test_dns();test_http_captive();
    for(unsigned i=0;i<registered_routes;++i)CHECK(route_success[i]>0);
    test_photo_owner_lifetime();test_photo_owner_stale();test_photo_owner_retry();
    test_photo_prefetch_policy();test_photo_prefetch_failed_source();test_photo_prefetch_cancel_retry();
    test_extended_photos(argv[3]);
    CHECK(async_open==0);
    if(argc>=3)write_native_report(argv[2]);
    printf("PASS: %u checks; 107 JPEGs, 98 animation frames, 18 BMPs; factory settings, Kelvin weather, flash uploads and HTTP handlers\n",checks);
    return 0;
}
