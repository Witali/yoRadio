#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "web_file_form.h"

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_SIZE 0x104
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_TIMEOUT 0x107
#define esp_random() UINT32_C(12345)
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define ESP_LOGI(...) ((void)0)
#define ESP_RETURN_ON_FALSE(condition,error,...) do { if (!(condition)) return (error); } while(0)
#define ESP_RETURN_ON_ERROR(expression,...) do { int value=(expression); if(value != ESP_OK) return value; } while(0)
typedef pthread_mutex_t *SemaphoreHandle_t;
static pthread_mutex_t storage_mutex=PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t pause_mutex=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t pause_cond=PTHREAD_COND_INITIALIZER;
static bool no_memory, fail_final, fail_rollback, deny_open_rename, pause_writer, writer_paused, release_writer;
static char root[768];
static unsigned cases;
static const char *TAG="test";

static SemaphoreHandle_t xSemaphoreCreateMutex(void) { return no_memory ? NULL : &storage_mutex; }
static int xSemaphoreTake(SemaphoreHandle_t lock,unsigned timeout) { assert(timeout==1000); return pthread_mutex_lock(lock)==0; }
static void xSemaphoreGive(SemaphoreHandle_t lock) { assert(!pthread_mutex_unlock(lock)); }
static void path(const char *name,char *out,size_t size) { assert(!strncmp(name,"/spiffs/",8)); assert(snprintf(out,size,"%s/%s",root,name+8)>0); }
static FILE *mapped_open(const char *name,const char *mode) { char mapped[1024];path(name,mapped,sizeof(mapped));return fopen(mapped,mode); }
static int mapped_stat(const char *name,struct stat *out) {char mapped[1024];path(name,mapped,sizeof(mapped));return stat(mapped,out);}
static int mapped_remove(const char *name) {char mapped[1024];path(name,mapped,sizeof(mapped));return remove(mapped);}
static int mapped_rename(const char *from,const char *to) {
    if ((fail_final && strstr(from,".tmp") && !strstr(to,".bak")) ||
        (fail_rollback && strstr(from,".bak")) || (deny_open_rename && strstr(to,".bak"))) {errno=EIO;return -1;}
    char a[1024],b[1024];path(from,a,sizeof(a));path(to,b,sizeof(b));
    if (access(b,F_OK)==0) {errno=EEXIST;return -1;} // SPIFFS cannot overwrite on rename.
    int result=rename(a,b);
    if(!result && pause_writer && strstr(to,".bak")) {
        assert(!pthread_mutex_lock(&pause_mutex));writer_paused=true;pthread_cond_broadcast(&pause_cond);
        while(!release_writer) pthread_cond_wait(&pause_cond,&pause_mutex);
        pthread_mutex_unlock(&pause_mutex);
    }
    return result;
}
static size_t strlcpy(char *out,const char *text,size_t cap) {size_t n=strlen(text);if(cap){size_t k=n<cap-1?n:cap-1;memcpy(out,text,k);out[k]=0;}return n;}
typedef struct { struct {uint8_t ssid[32],password[64];struct {int authmode;}threshold;struct{bool capable,required;}pmf_cfg;}sta; } wifi_config_t;
#define WIFI_AUTH_OPEN 0
#define WIFI_MAX_CREDENTIALS 5
static wifi_config_t s_credentials[WIFI_MAX_CREDENTIALS],s_station_config;
static size_t s_credential_count,s_credential_index;
static bool s_have_credentials;

#define stat(...) mapped_stat(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#define fopen(...) mapped_open(__VA_ARGS__)
#include "storage-production.inc"
#include "wifi-production.inc"
#undef fopen
#undef stat
#undef remove
#undef rename

static void put(const char *name,const void *data,size_t size) {FILE *file=mapped_open(name,"wb");assert(file);assert(fwrite(data,1,size,file)==size);assert(!fclose(file));}
static void text(const char *name,const char *data) {put(name,data,strlen(data));}
static bool equals(const char *name,const char *expected) {FILE *file=mapped_open(name,"rb");if(!file)return false;char data[1024];size_t n=fread(data,1,sizeof(data),file);fclose(file);return n==strlen(expected)&&!memcmp(data,expected,n);}
static void clear(void) {
    const char *names[]={"/spiffs/data/wifi.csv","/spiffs/data/wifi.csv.bak","/spiffs/data/wifi.csv.tmp",
        "/spiffs/data/web-upload-00.tmp","/spiffs/www/style.css.gz","/spiffs/www/style.css.gz.bak","/spiffs/www/style.css"};
    for(size_t i=0;i<sizeof(names)/sizeof(names[0]);++i)mapped_remove(names[i]);
    fail_final=fail_rollback=deny_open_rename=pause_writer=writer_paused=release_writer=false;++cases;
}
static const char *old_wifi="old-fixture\tfixture-old\n";
static const char *new_wifi="new-fixture\tfixture-new\n";
static void *writer(void *unused) {(void)unused;assert(web_upload_publish_file("/spiffs/data/web-upload-00.tmp","/spiffs/www/style.css.gz"));return NULL;}
static void *reader(void *unused) {(void)unused;FILE *file=web_upload_open_file("/spiffs/www/style.css.gz");assert(file);char data[16]={0};assert(fread(data,1,3,file)==3&&!strcmp(data,"new"));fclose(file);return NULL;}

int main(int argc,char **argv) {
    assert(argc==2);strlcpy(root,argv[1],sizeof(root));
    char directory[1024];snprintf(directory,sizeof(directory),"%s/data",root);assert(!mkdir(directory,0700)||errno==EEXIST);
    snprintf(directory,sizeof(directory),"%s/www",root);assert(!mkdir(directory,0700)||errno==EEXIST);
    no_memory=true;assert(web_upload_storage_init()==ESP_ERR_NO_MEM);
    assert(!web_upload_publish_file("/spiffs/tmp","/spiffs/live")&&!web_upload_open_file("/spiffs/live"));
    no_memory=false;assert(web_upload_storage_init()==ESP_OK);
#ifdef CURRENT_PRIVATE_STORE
    assert(network_service_storage_init()==ESP_OK);
#endif
#ifdef ROWS_ONLY
    clear();char row[256];memset(row,'x',159);strcpy(row+159,"phantom\tfixture\nallowed\tfixture\n");
    text("/spiffs/data/wifi.csv",row);assert(read_credentials(&s_station_config));
    assert(s_credential_count==1&&!strcmp((char *)s_station_config.sta.ssid,"allowed"));
    return 0;
#endif
    clear();text("/spiffs/data/wifi.csv",old_wifi);fail_final=true;
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi,strlen(new_wifi))==ESP_FAIL);
    assert(equals("/spiffs/data/wifi.csv",old_wifi));
    clear();text("/spiffs/data/wifi.csv",old_wifi);fail_final=fail_rollback=true;
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi,strlen(new_wifi))==ESP_FAIL);
    assert(equals("/spiffs/data/wifi.csv.bak",old_wifi));
    fail_final=fail_rollback=false;assert(read_credentials(&s_station_config));assert(s_credential_count==1);
    assert(equals("/spiffs/data/wifi.csv",old_wifi));
    clear();text("/spiffs/data/wifi.csv",old_wifi);
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi,strlen(new_wifi))==ESP_OK);
    assert(equals("/spiffs/data/wifi.csv",new_wifi)&&s_credential_count==1);
    clear();text("/spiffs/data/wifi.csv",old_wifi);
    assert(network_service_save_credentials_file((const uint8_t *)"invalid",7)!=ESP_OK&&equals("/spiffs/data/wifi.csv",old_wifi));
    clear();
    char oversized[256];memset(oversized,'x',159);strcpy(oversized+159,"phantom\tfixture\nallowed\tfixture\n");
    text("/spiffs/data/wifi.csv",oversized);assert(read_credentials(&s_station_config));
    assert(s_credential_count==1&&!strcmp((char *)s_station_config.sta.ssid,"allowed"));
    clear();const char embedded[]="invalid\tfixture\0suffix\nallowed\tfixture\n";
    put("/spiffs/data/wifi.csv",embedded,sizeof(embedded)-1);assert(read_credentials(&s_station_config));
    assert(s_credential_count==1&&!strcmp((char *)s_station_config.sta.ssid,"allowed"));
    clear();text("/spiffs/data/wifi.csv","bad\tfixture\textra\nbad\rname\tfixture\nbad\tfixture\rjunk\nallowed\t\r\n");
    assert(read_credentials(&s_station_config)&&s_credential_count==1&&!s_station_config.sta.password[0]);
    clear();text("/spiffs/data/wifi.csv","a\t1\nb\t2\nc\t3\nd\t4\ne\t5\nf\t6\n");
    assert(read_credentials(&s_station_config)&&s_credential_count==5);
    clear();text("/spiffs/www/style.css.gz","old");text("/spiffs/data/web-upload-00.tmp","new");fail_final=true;
    assert(!publish_file(0,"style.css.gz",false)&&equals("/spiffs/www/style.css.gz","old"));
    clear();text("/spiffs/www/style.css.gz","old");text("/spiffs/data/web-upload-00.tmp","new");fail_final=fail_rollback=true;
    assert(!publish_file(0,"style.css.gz",false)&&equals("/spiffs/www/style.css.gz.bak","old"));
    fail_final=fail_rollback=false;FILE *recovered=web_upload_open_file("/spiffs/www/style.css.gz");assert(recovered);fclose(recovered);
    assert(equals("/spiffs/www/style.css.gz","old"));
    clear();text("/spiffs/www/style.css.gz","old");text("/spiffs/www/style.css","obsolete");text("/spiffs/data/web-upload-00.tmp","new");
    assert(publish_file(0,"style.css.gz",false)&&equals("/spiffs/www/style.css.gz","new"));assert(!mapped_open("/spiffs/www/style.css","rb"));
    clear();text("/spiffs/www/style.css.gz","old");text("/spiffs/data/web-upload-00.tmp","new");
    char oversized_name[200];memset(oversized_name,'a',sizeof(oversized_name));memcpy(oversized_name+sizeof(oversized_name)-4,".gz",4);
    assert(!publish_file(0,oversized_name,false)&&equals("/spiffs/www/style.css.gz","old"));
    clear();text("/spiffs/www/style.css.gz","old");text("/spiffs/data/web-upload-00.tmp","new");
    FILE *open_reader=web_upload_open_file("/spiffs/www/style.css.gz");assert(open_reader);deny_open_rename=true;
    assert(!publish_file(0,"style.css.gz",false)&&equals("/spiffs/www/style.css.gz","old"));fclose(open_reader);
    clear();text("/spiffs/www/style.css.gz","old");text("/spiffs/data/web-upload-00.tmp","new");pause_writer=true;
    pthread_t publish_thread,open_thread;assert(!pthread_create(&publish_thread,NULL,writer,NULL));
    pthread_mutex_lock(&pause_mutex);while(!writer_paused)pthread_cond_wait(&pause_cond,&pause_mutex);pthread_mutex_unlock(&pause_mutex);
    assert(!pthread_create(&open_thread,NULL,reader,NULL));
    pthread_mutex_lock(&pause_mutex);release_writer=true;pthread_cond_broadcast(&pause_cond);pthread_mutex_unlock(&pause_mutex);
    pthread_join(publish_thread,NULL);pthread_join(open_thread,NULL);
    printf("PASS C3 storage/network: %u fixture groups, rename rollback/recovery, serialized reader, bounded physical rows; credentials not logged\n",cases);
    return 0;
}
