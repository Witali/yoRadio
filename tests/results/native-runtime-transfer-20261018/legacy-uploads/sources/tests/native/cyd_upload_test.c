#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "native_wifi_store.h"
#include "native_wifi_file.h"

typedef int esp_err_t;
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef struct {struct {uint8_t ssid[32],password[64];}sta;} wifi_config_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_SIZE 0x104
#define ESP_ERR_TIMEOUT 0x107
#define ESP_RETURN_ON_FALSE(condition,error,...) do {if (!(condition)) return (error);} while (0)
#define ESP_RETURN_ON_ERROR(expression,...) do {int result_ = (expression); if (result_ != ESP_OK) return result_;} while (0)
#define pdTRUE 1
#define pdMS_TO_TICKS(ms) (ms)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define CONFIG_SPIFFS_OBJ_NAME_LEN 32
#define WIFI_MAX_FILE_BYTES 800U
#define WIFI_MAX_FILE_NETWORKS 5U

typedef struct {
    size_t content_len, actual_len, offset, fragment;
    const uint8_t *body;
    const char *content_type;
    char status[64], response[160], connection[16], location[32];
    unsigned recv_calls, responses, timeouts;
    bool response_error;
} httpd_req_t;
static char root[768];
static unsigned scenarios, allocations, frees, outstanding, opens, writes, syncs, closes;
static unsigned publishes, playlist_reindexes, playlist_notifications, reboot_requests;
static unsigned io_closes;
static bool reboot_pending;
static uint64_t reboot_reserved;
static unsigned max_write, interrupt_writes, short_write;
static size_t write_bytes;
static int64_t time_us, delay_us, receive_us;
static bool reboot_ready, no_memory, open_error, write_error, sync_error, close_error;
static bool wifi_write_error, wifi_flush_error, wifi_close_error, rename_final_error, rename_rollback_error;
static bool remove_raw_error, fail_index, fail_publish_second;
static wifi_config_t s_station_config;
static SemaphoreHandle_t s_wifi_save_lock;
static SemaphoreHandle_t s_storage_lock;
static httpd_req_t *current_request;
static bool pause_publish,publish_paused,release_publish,reader_attempted;
static _Thread_local bool is_reader;
static pthread_mutex_t coordination = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t coordinated = PTHREAD_COND_INITIALIZER;
static pthread_mutex_t mutexes[] = {PTHREAD_MUTEX_INITIALIZER,PTHREAD_MUTEX_INITIALIZER};
static unsigned created_mutexes;
static SemaphoreHandle_t xSemaphoreCreateMutex(void) {assert(created_mutexes < 2); return &mutexes[created_mutexes++];}
static int xSemaphoreTake(SemaphoreHandle_t lock, unsigned timeout) {
    assert(timeout == 1000);
    if(is_reader&&lock==s_storage_lock){pthread_mutex_lock(&coordination);reader_attempted=true;pthread_cond_broadcast(&coordinated);pthread_mutex_unlock(&coordination);}
    return !pthread_mutex_lock(lock);
}
static void xSemaphoreGive(SemaphoreHandle_t lock) {assert(!pthread_mutex_unlock(lock));}
static int64_t esp_timer_get_time(void) {return time_us;}
static void vTaskDelay(unsigned ticks) {assert(ticks == 1); time_us += delay_us;}
static bool web_reboot_ready(void) {return reboot_ready;}
typedef struct {uint64_t epoch;} web_reboot_lease_t;
static esp_err_t web_reboot_reserve(web_reboot_lease_t *lease) {
    if(!reboot_ready||reboot_pending||reboot_reserved)return ESP_ERR_INVALID_STATE;
    lease->epoch=reboot_reserved=1;return ESP_OK;
}
static esp_err_t web_reboot_cancel(web_reboot_lease_t *lease) {
    assert(lease->epoch&&lease->epoch==reboot_reserved);lease->epoch=reboot_reserved=0;return ESP_OK;
}
static esp_err_t web_reboot_commit(web_reboot_lease_t *lease,unsigned delay) {
    assert(delay==750&&current_request&&current_request->responses==1&&io_closes==1);
    web_reboot_cancel(lease);reboot_pending=true;++reboot_requests;return ESP_OK;
}
// Deliberate old fixture seam. The canonical Wi-Fi HTTP/wire suites compile
// actual scoped I/O and pinned SDK functions; this suite retains file faults.
typedef struct {bool attached;} native_wifi_request_io_t;
static native_wifi_request_io_t model_io;
static native_wifi_request_io_t *native_wifi_request_io_open(httpd_req_t *request,
    uint64_t idle,uint64_t overall,void *payload,void (*dispose)(void *)) {
    assert(request&&idle==10000000&&overall==120000000&&!payload&&!dispose&&!model_io.attached);
    model_io.attached=true;return &model_io;
}
static bool native_wifi_request_io_progress(httpd_req_t *request) {assert(request&&model_io.attached);return true;}
static void native_wifi_request_io_response(native_wifi_request_io_t *io) {assert(io==&model_io&&io->attached);}
static void native_wifi_request_io_close(httpd_req_t *request,native_wifi_request_io_t *io,bool ok,bool drain) {
    (void)ok;(void)drain;assert(request&&!io_closes);++io_closes;
    if(io){assert(io==&model_io&&io->attached);io->attached=false;}
}
static void esp_fill_random(void *data,size_t size) {memset(data,0x41,size);}
static void websocket_service_notify_playlist_changed(void) {++playlist_notifications;}
static esp_err_t radio_control_publish_playlist(const char *,bool (*)(const char *,const char *));
static esp_err_t network_service_validate_credentials_file(const uint8_t *,size_t);
static esp_err_t network_service_save_credentials_file(const uint8_t *,size_t);
static esp_err_t network_service_save_credentials(const char *,const char *);

static int httpd_req_get_hdr_value_str(httpd_req_t *request, const char *name, char *out, size_t cap) {
    assert(!strcmp(name, "Content-Type"));
    if (!request->content_type || strlen(request->content_type) >= cap) return ESP_FAIL;
    strcpy(out, request->content_type); return ESP_OK;
}
static int httpd_req_recv(httpd_req_t *request, char *buffer, size_t cap) {
    assert(cap && cap <= 256); ++request->recv_calls; time_us += receive_us;
    if (request->timeouts) {--request->timeouts; return HTTPD_SOCK_ERR_TIMEOUT;}
    size_t count = request->actual_len - request->offset;
    if (count > cap) count = cap;
    if (count > request->fragment) count = request->fragment;
    memcpy(buffer, request->body + request->offset, count); request->offset += count;
    return (int)count;
}
static esp_err_t httpd_resp_set_hdr(httpd_req_t *request, const char *name, const char *value) {
    if (!strcmp(name, "Connection")) {assert(strlen(value) < sizeof(request->connection)); strcpy(request->connection,value);}
    else if (!strcmp(name, "Location")) {assert(strlen(value) < sizeof(request->location)); strcpy(request->location,value);}
    else assert(!strcmp(name,"Cache-Control") && !strcmp(value,"no-store"));
    return ESP_OK;
}
static esp_err_t httpd_resp_set_status(httpd_req_t *request, const char *status) {
    assert(strlen(status) < sizeof(request->status)); strcpy(request->status,status); return ESP_OK;
}
static esp_err_t httpd_resp_set_type(httpd_req_t *request, const char *type) {
    (void)request; assert(!strcmp(type,"text/plain; charset=utf-8")); return ESP_OK;
}
static esp_err_t httpd_resp_sendstr(httpd_req_t *request, const char *body) {
    assert(strlen(body) < sizeof(request->response)); strcpy(request->response,body); ++request->responses;
    return request->response_error ? ESP_FAIL : ESP_OK;
}
static void path(const char *name, char *out, size_t cap) {
    assert(!strncmp(name,"/spiffs/",8)); int size = snprintf(out,cap,"%s/%s",root,name+8);
    assert(size > 0 && (size_t)size < cap);
}
static FILE *mapped_fopen(const char *name, const char *mode) {char out[1024]; path(name,out,sizeof(out)); return fopen(out,mode);}
static size_t mapped_fwrite(const void *data,size_t width,size_t count,FILE *file) {
    if(wifi_write_error) return fwrite(data,width,count/2U,file);
    return fwrite(data,width,count,file);
}
static int mapped_fflush(FILE *file) {int result=fflush(file); return wifi_flush_error ? EOF : result;}
static int mapped_fclose(FILE *file) {int result=fclose(file); return wifi_close_error ? EOF : result;}
static int mapped_stat(const char *name,struct stat *info) {char out[1024];path(name,out,sizeof(out));return stat(out,info);}
static int mapped_remove(const char *name) {
    if(current_request && !strcmp(name,"/spiffs/www/theme.css")) {
        // Replacement and raw-file cleanup must exclude recovery/open readers.
        assert(s_storage_lock && pthread_mutex_trylock(s_storage_lock)==EBUSY);
    }
    if(remove_raw_error && !strcmp(name,"/spiffs/www/theme.css")){errno=EIO;return -1;}
    char out[1024];path(name,out,sizeof(out));return remove(out);
}
static int mapped_rename(const char *from,const char *to) {
    bool committing=strstr(from,".tmp") && !strstr(to,".bak");
    if(committing) ++publishes;
    if((committing && (rename_final_error || (fail_publish_second && publishes==2))) ||
       (rename_rollback_error && strstr(from,".bak"))){errno=EIO;return -1;}
    char source[1024],target[1024];path(from,source,sizeof(source));path(to,target,sizeof(target));
    if(!access(target,F_OK)){errno=EEXIST;return -1;}
    int result=rename(source,target);
    if(!result&&pause_publish&&strstr(to,".bak")){
        pthread_mutex_lock(&coordination);publish_paused=true;pthread_cond_broadcast(&coordinated);
        while(!release_publish)pthread_cond_wait(&coordinated,&coordination);
        pthread_mutex_unlock(&coordination);
    }
    return result;
}
static int mapped_open(const char *name,int flags,int mode) {
    ++opens; if(open_error){errno=ENOSPC;return -1;}
    char out[1024];path(name,out,sizeof(out));return open(out,flags,mode);
}
static ssize_t mapped_write(int fd,const void *data,size_t size) {
    assert(size && size<=2048); ++writes; if(size>max_write) max_write=(unsigned)size;
    if(interrupt_writes){--interrupt_writes;errno=EINTR;return -1;}
    if(write_error){errno=ENOSPC;return -1;}
    if(short_write && size>short_write) size=short_write;
    ssize_t result=write(fd,data,size);if(result>0)write_bytes+=(size_t)result;return result;
}
static int mapped_fsync(int fd) {++syncs;int result=fsync(fd);if(sync_error){errno=EIO;return -1;}return result;}
static int mapped_close(int fd) {++closes;int result=close(fd);if(close_error){errno=EIO;return -1;}return result;}
static void *allocate(size_t size) {assert(size==2048);++allocations;if(no_memory)return NULL;void *result=malloc(size);if(result)++outstanding;return result;}
static void release(void *data) {if(data){++frees;assert(outstanding);--outstanding;}free(data);}
static size_t strlcpy(char *out,const char *source,size_t cap) {size_t size=strlen(source);if(cap){size_t n=size<cap-1U?size:cap-1U;memcpy(out,source,n);out[n]=0;}return size;}

#include "web_file_form.h"
#include "credential_line.h"
#define stat(...) mapped_stat(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#include "native_wifi_store.c"
#define fopen(...) mapped_fopen(__VA_ARGS__)
#define fwrite(...) mapped_fwrite(__VA_ARGS__)
#define fflush(...) mapped_fflush(__VA_ARGS__)
#define fclose(...) mapped_fclose(__VA_ARGS__)
#include "native_wifi_file.c"
#define open(...) mapped_open(__VA_ARGS__)
#define write(...) mapped_write(__VA_ARGS__)
#define fsync(...) mapped_fsync(__VA_ARGS__)
#define close(...) mapped_close(__VA_ARGS__)
#define malloc(...) allocate(__VA_ARGS__)
#define free(...) release(__VA_ARGS__)
#ifdef TEST_C3_UPLOAD
#define websocket_service_reboot_ready web_reboot_ready
#define websocket_reboot_lease_t web_reboot_lease_t
#define websocket_service_reboot_reserve web_reboot_reserve
#define websocket_service_reboot_cancel web_reboot_cancel
#define websocket_service_reboot_commit web_reboot_commit
#define web_upload_activate() ((void)0)
#include "c3-upload-production.inc"
#else
#include "cyd-upload-production.inc"
#endif
#include "cyd-wifi-production.inc"
#undef free
#undef malloc
#undef close
#undef fsync
#undef write
#undef open
#undef fclose
#undef fflush
#undef fwrite
#undef fopen
#undef rename
#undef remove
#undef stat

static uint8_t body[120000];
static size_t body_size;
static void append(const void *data,size_t size){assert(body_size+size<sizeof(body));memcpy(body+body_size,data,size);body_size+=size;}
static void add_text(const char *text){append(text,strlen(text));}
static void part(const char *field,const char *name,const void *data,size_t size) {
    char header[512];int n=snprintf(header,sizeof(header),"--fixture\r\nContent-Disposition: form-data; name=\"%s\"%s%s%s\r\n\r\n",
        field,name?"; filename=\"":"",name?name:"",name?"\"":"");
    assert(n>0&&(size_t)n<sizeof(header));append(header,(size_t)n);append(data,size);add_text("\r\n");
}
static void end(void){add_text("--fixture--\r\n");}
static void put(const char *name,const void *data,size_t size){FILE *file=mapped_fopen(name,"wb");assert(file&&fwrite(data,1,size,file)==size&&!fclose(file));}
static void text(const char *name,const char *data){put(name,data,strlen(data));}
static esp_err_t radio_control_publish_playlist(const char *csv,bool (*publish)(const char *,const char *)) {
    ++playlist_reindexes;
    if(fail_index)return ESP_FAIL;
    const char *index="/spiffs/data/index.dat.tmp";
    text(index,"synthetic index candidate seam");
    bool ok=publish(csv,index);mapped_remove(index);return ok?ESP_OK:ESP_FAIL;
}
static bool equals_bytes(const char *name,const void *expected,size_t size){FILE *file=mapped_fopen(name,"rb");if(!file)return false;uint8_t content[100000];size_t count=fread(content,1,sizeof(content),file);assert(!ferror(file)&&!fclose(file));return count==size&&!memcmp(content,expected,size);}
static bool equals(const char *name,const char *expected){return equals_bytes(name,expected,strlen(expected));}
static bool exists(const char *name){char out[1024];path(name,out,sizeof(out));return !access(out,F_OK);}
static void clear(void) {
    assert(!outstanding&&!model_io.attached); no_memory=open_error=write_error=sync_error=close_error=false;
    io_closes=0;reboot_pending=false;reboot_reserved=0;
    wifi_write_error=wifi_flush_error=wifi_close_error=rename_final_error=rename_rollback_error=false;
    remove_raw_error=fail_index=fail_publish_second=false;reboot_ready=true;
    pause_publish=publish_paused=release_publish=reader_attempted=false;
    time_us=0;delay_us=1000;receive_us=0;body_size=0;
    allocations=frees=opens=writes=syncs=closes=publishes=0;max_write=interrupt_writes=short_write=0;write_bytes=0;
    playlist_reindexes=playlist_notifications=reboot_requests=0;
    const char *names[]={"/spiffs/www/theme.css","/spiffs/www/theme.css.gz","/spiffs/www/theme.css.gz.bak",
        "/spiffs/www/second.css.gz","/spiffs/www/second.css.gz.bak","/spiffs/data/playlist.csv","/spiffs/data/playlist.csv.bak",
        "/spiffs/data/index.dat","/spiffs/data/index.dat.bak","/spiffs/data/index.dat.tmp",
        "/spiffs/data/wifi.csv","/spiffs/data/wifi.csv.bak","/spiffs/data/wifi.csv.tmp",
        "/spiffs/www/abcdefghijklmnopqrs.gz","/spiffs/www/abcdefghijklmnopqrst.gz"};
    for(size_t i=0;i<sizeof(names)/sizeof(names[0]);++i)mapped_remove(names[i]);
    for(unsigned i=0;i<WEB_FILE_FORM_MAX_FILES;++i){char name[64];temporary_path(i,name,sizeof(name));mapped_remove(name);}
    for(unsigned i=0;i<WEB_FILE_FORM_MAX_FILES+1U;++i){char name[64];snprintf(name,sizeof(name),"/spiffs/www/f%02u.gz",i);mapped_remove(name);strcat(name,".bak");mapped_remove(name);}
    web_upload_activate();++scenarios;
}
static httpd_req_t request(size_t fragment) {return (httpd_req_t){.content_len=body_size,.actual_len=body_size,.body=body,.fragment=fragment,.content_type="multipart/form-data; boundary=fixture"};}
static esp_err_t execute(httpd_req_t *request,web_form_mode_t mode) {
    wifi_config_t active=s_station_config;current_request=request;esp_err_t result=handle_upload(request,mode);current_request=NULL;
    assert(!memcmp(&active,&s_station_config,sizeof(active))&&!outstanding&&request->responses==1&&io_closes==1&&!model_io.attached);
    assert(!strcmp(request->connection,"close"));
    for(unsigned i=0;i<WEB_FILE_FORM_MAX_FILES;++i){char name[64];temporary_path(i,name,sizeof(name));assert(!exists(name));}
    return result;
}
static void simple_asset(void){part("www","theme.css.gz","new",3);end();}
static void reject_body(web_form_mode_t mode) {text("/spiffs/www/theme.css.gz","old");httpd_req_t req=request(7);assert(execute(&req,mode)==ESP_FAIL);assert(equals("/spiffs/www/theme.css.gz","old")&&!publishes&&!reboot_requests&&!playlist_notifications);}
static void *publish_thread(void *argument){httpd_req_t *req=argument;assert(execute(req,WEB_FORM_BOARD)==ESP_FAIL);return NULL;}
static void *static_reader_thread(void *argument){(void)argument;is_reader=true;FILE *file=web_upload_open_file("/spiffs/www/theme.css.gz");assert(file);char contents[8]={0};assert(fread(contents,1,sizeof(contents)-1U,file)==3&&!strcmp(contents,"new")&&!fclose(file));return NULL;}
int main(int argc,char **argv) {
    assert(argc==2&&strlen(argv[1])<sizeof(root));strcpy(root,argv[1]);char directory[1024];
    snprintf(directory,sizeof(directory),"%s/data",root);assert(!mkdir(directory,0700)||errno==EEXIST);
    snprintf(directory,sizeof(directory),"%s/www",root);assert(!mkdir(directory,0700)||errno==EEXIST);
    assert(network_service_storage_init()==ESP_OK);memset(&s_station_config,0x5a,sizeof(s_station_config));
    httpd_req_t req;
#ifndef TEST_C3_UPLOAD
    clear();simple_asset();web_upload_deactivate();req=request(1);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!req.recv_calls&&!allocations&&!opens&&!publishes&&strstr(req.status,"503"));
#endif
    clear();simple_asset();reboot_ready=false;req=request(1);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!req.recv_calls&&!allocations&&!opens&&!publishes&&strstr(req.status,"503"));
    clear();simple_asset();text("/spiffs/data/web-upload-00.tmp","retained");reboot_ready=false;req=request(1);assert(handle_upload(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals("/spiffs/data/web-upload-00.tmp","retained")&&!req.recv_calls&&!opens&&!allocations);
    const size_t splits[]={1,2,3,7,31,71,128,255,256};
    uint8_t payload[5000];for(size_t i=0;i<sizeof(payload);++i)payload[i]=(uint8_t)(i*37U);
    for(size_t i=0;i<sizeof(splits)/sizeof(splits[0]);++i){clear();text("/spiffs/www/theme.css.gz","old");text("/spiffs/www/theme.css","obsolete");part("www","theme.css.gz",payload,sizeof(payload));end();req=request(splits[i]);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals_bytes("/spiffs/www/theme.css.gz",payload,sizeof(payload))&&!exists("/spiffs/www/theme.css"));assert(allocations==1&&frees==1&&opens==1&&closes==1&&writes==3&&max_write==2048&&write_bytes==5000&&!playlist_notifications&&!reboot_requests);}
    clear();part("www","theme.css.gz",payload,sizeof(payload));part("www","second.css.gz",payload,sizeof(payload));end();req=request(17);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&allocations==1&&opens==2&&closes==2&&writes==6&&write_bytes==10000);
    clear();simple_asset();interrupt_writes=1;short_write=1;req=request(13);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals("/spiffs/www/theme.css.gz","new")&&writes==4&&write_bytes==3);
    for(unsigned f=0;f<5;++f){clear();simple_asset();text("/spiffs/www/theme.css.gz","old");no_memory=f==0;open_error=f==1;write_error=f==2;sync_error=f==3;close_error=f==4;req=request(1);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals("/spiffs/www/theme.css.gz","old")&&!publishes);}
    clear();simple_asset();text("/spiffs/www/theme.css.gz","old");rename_final_error=true;req=request(31);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals("/spiffs/www/theme.css.gz","old"));
    clear();simple_asset();text("/spiffs/www/theme.css.gz","old");rename_final_error=rename_rollback_error=true;req=request(31);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!exists("/spiffs/www/theme.css.gz")&&equals("/spiffs/www/theme.css.gz.bak","old"));rename_final_error=rename_rollback_error=false;FILE *recovered=web_upload_open_file("/spiffs/www/theme.css.gz");assert(recovered&&!fclose(recovered)&&equals("/spiffs/www/theme.css.gz","old"));
    clear();simple_asset();text("/spiffs/www/theme.css","obsolete");remove_raw_error=true;req=request(31);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals("/spiffs/www/theme.css.gz","new")&&equals("/spiffs/www/theme.css","obsolete"));
    clear();part("www","theme.css.gz","first",5);part("www","second.css.gz","second",6);end();text("/spiffs/www/theme.css.gz","oldfirst");text("/spiffs/www/second.css.gz","oldsecond");fail_publish_second=true;req=request(7);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals("/spiffs/www/theme.css.gz","first")&&equals("/spiffs/www/second.css.gz","oldsecond"));

    for(size_t i=0;i<sizeof(splits)/sizeof(splits[0]);++i){clear();part("ssid",NULL," fixture ",9);part("pass",NULL," pass ",6);end();req=request(splits[i]);assert(execute(&req,WEB_FORM_CREDENTIALS)==ESP_FAIL&&equals("/spiffs/data/wifi.csv"," fixture \t pass \n")&&reboot_requests==1&&!allocations&&!strcmp(req.status,"303 See Other")&&!strcmp(req.location,"/"));}
    clear();part("ssid",NULL,"fixture",7);part("pass",NULL,"",0);end();req=request(1);req.response_error=true;assert(execute(&req,WEB_FORM_CREDENTIALS)==ESP_FAIL&&equals("/spiffs/data/wifi.csv","fixture\t\n")&&reboot_requests==1);
    clear();part("wifile","wifi.csv","first\tpass\nsecond\t\r\n",20);end();req=request(1);assert(execute(&req,WEB_FORM_UPLOAD)==ESP_FAIL&&reboot_requests==1&&!allocations);wifi_config_t loaded={0};assert(read_credentials(&loaded)&&!strcmp((char *)loaded.sta.ssid,"first"));
    for(unsigned f=0;f<4;++f){clear();text("/spiffs/data/wifi.csv","old\tpass\n");part("wifile","wifi.csv",f==0?"invalid":"new\tpass\n",f==0?7:9);end();wifi_write_error=f==1;wifi_flush_error=f==2;wifi_close_error=f==3;req=request(3);assert(execute(&req,WEB_FORM_UPLOAD)==ESP_FAIL&&equals("/spiffs/data/wifi.csv","old\tpass\n")&&!reboot_requests);}
    clear();part("www","theme.css.gz","new",3);part("data","wifi.csv","invalid",7);end();reject_body(WEB_FORM_BOARD);
    clear();part("plfile","playlist.csv","station\thttps://fixture.invalid/audio\n",38);end();req=request(2);assert(execute(&req,WEB_FORM_UPLOAD)==ESP_FAIL&&playlist_reindexes==1&&playlist_notifications==1&&!reboot_requests);
    clear();text("/spiffs/data/playlist.csv","old playlist");text("/spiffs/data/index.dat","old index");part("plfile","playlist.csv","station\thttps://fixture.invalid/audio\n",38);end();fail_index=true;req=request(2);assert(execute(&req,WEB_FORM_UPLOAD)==ESP_FAIL&&playlist_reindexes==1&&!playlist_notifications&&!reboot_requests&&equals("/spiffs/data/playlist.csv","old playlist")&&equals("/spiffs/data/index.dat","old index"));
    clear();text("/spiffs/data/playlist.csv","old playlist");text("/spiffs/data/index.dat","old index");part("plfile","playlist.csv","station\thttps://fixture.invalid/audio\n",38);end();fail_publish_second=true;req=request(2);assert(execute(&req,WEB_FORM_UPLOAD)==ESP_FAIL&&!playlist_notifications&&equals("/spiffs/data/playlist.csv","old playlist")&&equals("/spiffs/data/index.dat","old index"));

    clear();simple_asset();body_size-=5;reject_body(WEB_FORM_BOARD);
    clear();simple_asset();add_text("invalid");reject_body(WEB_FORM_BOARD);
    clear();simple_asset();body[body_size-1]='x';reject_body(WEB_FORM_BOARD);
    clear();part("www","theme.css.gz","",0);end();reject_body(WEB_FORM_BOARD);
    clear();part("www","theme.css.gz","first",5);part("www","theme.css.gz","second",6);end();reject_body(WEB_FORM_BOARD);
    clear();part("www","theme.css","raw",3);end();reject_body(WEB_FORM_BOARD);
    clear();part("www","theme..css.gz","raw",3);end();reject_body(WEB_FORM_BOARD);
    const char *aliases[]={"theme.css.gz.gz","theme.css.gz.bak.gz","theme.tmp.gz"};
    for(size_t i=0;i<sizeof(aliases)/sizeof(aliases[0]);++i){
        clear();text("/spiffs/www/theme.css.gz","old");text("/spiffs/www/theme.css.gz.bak","retained");
        part("www","theme.css.gz","first",5);part("www",aliases[i],"second",6);end();
        reject_body(WEB_FORM_BOARD);
        assert(equals("/spiffs/www/theme.css.gz","old")&&equals("/spiffs/www/theme.css.gz.bak","retained"));
    }
    clear();part("unknown","theme.css.gz","raw",3);end();reject_body(WEB_FORM_BOARD);
    clear();part("www","abcdefghijklmnopqrs.gz","new",3);end();req=request(1);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&exists("/spiffs/www/abcdefghijklmnopqrs.gz"));
    clear();part("www","theme.css.gz","new",3);part("www","abcdefghijklmnopqrst.gz","invalid",7);end();reject_body(WEB_FORM_BOARD);
    clear();simple_asset();req=request(1);req.content_len=96U*1024U+1U;assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!req.recv_calls&&!opens&&!allocations);
    clear();simple_asset();req=request(1);req.content_len=4097;assert(execute(&req,WEB_FORM_CREDENTIALS)==ESP_FAIL&&!req.recv_calls&&!opens&&!allocations);
    clear();simple_asset();req=request(1);req.content_len=0;assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!req.recv_calls);
    clear();simple_asset();req=request(1);req.actual_len-=5;assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!publishes);
    clear();simple_asset();req=request(1);req.content_type="multipart/form-data; x-boundary=fixture";assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!req.recv_calls);
    clear();simple_asset();req=request(1);req.content_type="Multipart/Form-Data; boundary=\"fixture\"";assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL);
    clear();simple_asset();req=request(1);receive_us=11000000;assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!publishes);
    clear();simple_asset();req=request(1);receive_us=2000000;assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&time_us>=120000000&&!publishes);
    clear();simple_asset();req=request(1);req.timeouts=11;delay_us=1000000;assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&time_us>=10000000&&!publishes);
    clear();simple_asset();req=request(1);req.timeouts=2;assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL);
    clear();for(unsigned i=0;i<WEB_FILE_FORM_MAX_FILES;++i){char name[32];snprintf(name,sizeof(name),"f%02u.gz",i);part("www",name,"new",3);}end();req=request(17);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&allocations==1&&opens==WEB_FILE_FORM_MAX_FILES&&publishes==WEB_FILE_FORM_MAX_FILES);
    clear();for(unsigned i=0;i<WEB_FILE_FORM_MAX_FILES+1U;++i){char name[32];snprintf(name,sizeof(name),"f%02u.gz",i);part("www",name,"new",3);}end();req=request(17);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&!publishes);
    clear();part("www","theme.css.gz","",0);end();size_t overhead=body_size;body_size=0;static uint8_t large[WEB_UPLOAD_MAX];memset(large,'x',sizeof(large));part("www","theme.css.gz",large,WEB_UPLOAD_MAX-overhead);end();assert(body_size==WEB_UPLOAD_MAX);req=request(256);assert(execute(&req,WEB_FORM_BOARD)==ESP_FAIL&&equals_bytes("/spiffs/www/theme.css.gz",large,WEB_UPLOAD_MAX-overhead)&&allocations==1&&max_write==2048);
    clear();simple_asset();text("/spiffs/www/theme.css.gz","old");pause_publish=true;req=request(3);pthread_t writer,reader;
    assert(!pthread_create(&writer,NULL,publish_thread,&req));pthread_mutex_lock(&coordination);
    while(!publish_paused){pthread_cond_wait(&coordinated,&coordination);}pthread_mutex_unlock(&coordination);
    assert(!pthread_create(&reader,NULL,static_reader_thread,NULL));pthread_mutex_lock(&coordination);
    while(!reader_attempted)pthread_cond_wait(&coordinated,&coordination);
    release_publish=true;pthread_cond_broadcast(&coordinated);pthread_mutex_unlock(&coordination);
    assert(!pthread_join(writer,NULL)&&!pthread_join(reader,NULL));
    printf("PASS uploads: %u scenarios; actual full multipart handler/sink/storage and CYD Wi-Fi APIs, receive fragmentation/time budgets, IO and rollback faults, bounded names/heap, complete-before-publication, readiness gate, partial batch semantics and response-independent reboot\n",scenarios);
    return 0;
}
