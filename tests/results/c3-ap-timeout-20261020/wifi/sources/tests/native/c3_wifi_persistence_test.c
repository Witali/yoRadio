#define _GNU_SOURCE
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

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_SIZE 0x104
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_TIMEOUT 0x107
#define esp_random() UINT32_C(12345)
#define ESP_RETURN_ON_FALSE(condition,error,...) do {if (!(condition)) return (error);} while (0)
#define ESP_RETURN_ON_ERROR(expression,...) do {int result_ = (expression); if (result_ != ESP_OK) return result_;} while (0)
#define ESP_LOGI(...) ((void)0)
#define pdTRUE 1
#define pdMS_TO_TICKS(ms) (ms)
#define WIFI_AUTH_OPEN 0
#define WIFI_MAX_CREDENTIALS 5
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef struct {struct {uint8_t ssid[32],password[64];struct {int authmode;}threshold;struct {bool capable,required;}pmf_cfg;}sta;} wifi_config_t;
static wifi_config_t s_credentials[WIFI_MAX_CREDENTIALS],s_station_config;
static size_t s_credential_count,s_credential_index;
static bool s_have_credentials;
static pthread_mutex_t storage_mutex=PTHREAD_MUTEX_INITIALIZER;
static bool no_mutex;
static SemaphoreHandle_t xSemaphoreCreateMutex(void){return no_mutex?NULL:&storage_mutex;}
static int xSemaphoreTake(SemaphoreHandle_t lock,unsigned timeout){assert(timeout==1000);return !pthread_mutex_lock(lock);}
static void xSemaphoreGive(SemaphoreHandle_t lock){assert(!pthread_mutex_unlock(lock));}

static char root[768];
static const char *live="/spiffs/data/wifi.csv",*temporary="/spiffs/data/wifi.csv.tmp",*backup="/spiffs/data/wifi.csv.bak";
static const char *old_data="old-first\told-pass\nold-second\tsecond-pass\n";
enum failure {NONE,OPEN_OOM,OPEN_IO,WRITE_SHORT,FLUSH,CLOSE_FILE,LIVE_STAT,RENAME_OLD,RENAME_FINAL,BOTH_RENAMES};
static enum failure failure;
static bool committed,post_commit_open_oom,post_commit_read_error;
static unsigned scenarios,opens,writes,flushes,closes,read_opens_after_commit,publish_attempts;
static ssize_t cookie_read(void *context,char *buffer,size_t capacity){(void)context;(void)buffer;(void)capacity;errno=EIO;return -1;}
static void path(const char *name,char *out,size_t capacity){assert(!strncmp(name,"/spiffs/",8));int size=snprintf(out,capacity,"%s/%s",root,name+8);assert(size>0&&(size_t)size<capacity);}
static FILE *mapped_open(const char *name,const char *mode){++opens;
    if(!strcmp(name,temporary)&&strchr(mode,'w')&&(failure==OPEN_OOM||failure==OPEN_IO)){errno=failure==OPEN_OOM?ENOMEM:EIO;return NULL;}
    if(committed&&!strcmp(name,live)&&strchr(mode,'r')){++read_opens_after_commit;if(post_commit_open_oom){errno=ENOMEM;return NULL;}if(post_commit_read_error){cookie_io_functions_t io={.read=cookie_read};return fopencookie(NULL,"r",io);}}
    char out[1024];path(name,out,sizeof(out));return fopen(out,mode);}
static size_t mapped_write(const void *data,size_t width,size_t count,FILE *file){++writes;return fwrite(data,width,failure==WRITE_SHORT?count/2U:count,file);}
static int mapped_flush(FILE *file){++flushes;int result=fflush(file);if(failure==FLUSH){errno=EIO;return EOF;}return result;}
static int mapped_close(FILE *file){++closes;int result=fclose(file);if(failure==CLOSE_FILE){errno=EIO;return EOF;}return result;}
static int mapped_stat(const char *name,struct stat *info){if(failure==LIVE_STAT&&!strcmp(name,live)){errno=EIO;return -1;}char out[1024];path(name,out,sizeof(out));return stat(out,info);}
static int mapped_remove(const char *name){char out[1024];path(name,out,sizeof(out));return remove(out);}
static int mapped_rename(const char *from,const char *to){
    bool installing=!strcmp(from,temporary);
    if(installing)++publish_attempts;
    if((failure==RENAME_OLD&&!strcmp(from,live))||((failure==RENAME_FINAL||failure==BOTH_RENAMES)&&installing)||(failure==BOTH_RENAMES&&!strcmp(from,backup))){errno=EIO;return -1;}
    char source[1024],target[1024];path(from,source,sizeof(source));path(to,target,sizeof(target));if(!access(target,F_OK)){errno=EEXIST;return -1;}
    int result=rename(source,target);if(!result&&installing)committed=true;return result;}
static size_t strlcpy(char *out,const char *source,size_t cap){size_t size=strlen(source);if(cap){size_t count=size<cap-1U?size:cap-1U;memcpy(out,source,count);out[count]=0;}return size;}
static esp_err_t network_service_save_credentials_file(const uint8_t *,size_t);
#include "credential_line.h"
#define stat(...) mapped_stat(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#define fopen(...) mapped_open(__VA_ARGS__)
#define fwrite(...) mapped_write(__VA_ARGS__)
#define fflush(...) mapped_flush(__VA_ARGS__)
#define fclose(...) mapped_close(__VA_ARGS__)
#include "c3-storage-production.inc"
#include "c3-wifi-production.inc"
#undef fclose
#undef fflush
#undef fwrite
#undef fopen
#undef rename
#undef remove
#undef stat

typedef struct {wifi_config_t profiles[WIFI_MAX_CREDENTIALS],station;size_t count,index;bool have;} profile_snapshot_t;
static profile_snapshot_t snapshot(void){profile_snapshot_t result={0};memcpy(result.profiles,s_credentials,sizeof(s_credentials));result.station=s_station_config;result.count=s_credential_count;result.index=s_credential_index;result.have=s_have_credentials;return result;}
static void unchanged(const profile_snapshot_t *before){assert(!memcmp(before->profiles,s_credentials,sizeof(s_credentials))&&!memcmp(&before->station,&s_station_config,sizeof(s_station_config))&&before->count==s_credential_count&&before->index==s_credential_index&&before->have==s_have_credentials);}
static void text(const char *name,const void *data,size_t size){char out[1024];path(name,out,sizeof(out));FILE *file=fopen(out,"wb");assert(file&&fwrite(data,1,size,file)==size&&!fclose(file));}
static bool equals(const char *name,const void *data,size_t size){char out[1024],contents[1024];path(name,out,sizeof(out));FILE *file=fopen(out,"rb");if(!file)return false;size_t count=fread(contents,1,sizeof(contents),file);assert(!ferror(file)&&!fclose(file));return count==size&&!memcmp(contents,data,size);}
static bool exists(const char *name){char out[1024];path(name,out,sizeof(out));return !access(out,F_OK);}
static void reset(void){failure=NONE;committed=post_commit_open_oom=post_commit_read_error=false;read_opens_after_commit=publish_attempts=0;const char *names[]={live,temporary,backup};for(size_t index=0;index<3;++index)mapped_remove(names[index]);text(live,old_data,strlen(old_data));assert(read_credentials(&s_station_config)&&s_credential_count==2);s_credential_index=1;s_station_config=s_credentials[1];s_have_credentials=true;++scenarios;}
static void reject(const void *data,size_t size){reset();profile_snapshot_t before=snapshot();unsigned opened=opens,written=writes;assert(network_service_validate_credentials_file(data,size)!=ESP_OK);assert(network_service_save_credentials_file(data,size)!=ESP_OK);assert(equals(live,old_data,strlen(old_data))&&opens==opened&&writes==written&&!publish_attempts);unchanged(&before);}
static void accept(const char *data,size_t count,const char *first,const char *password){
    reset();profile_snapshot_t before=snapshot();
    assert(network_service_validate_credentials_file((const uint8_t *)data,strlen(data))==ESP_OK);
    assert(network_service_save_credentials_file((const uint8_t *)data,strlen(data))==ESP_OK);
    assert(equals(live,data,strlen(data)));
#ifdef CURRENT_PRIVATE_STORE
    unchanged(&before);native_wifi_metadata_t meta;
    committed=false;assert(network_service_wifi_metadata(&meta)==NATIVE_WIFI_OK&&meta.count==count&&!strcmp(meta.profiles[0].ssid,first));
    assert(read_credentials(&s_station_config)); // Explicit next-boot loader boundary.
#else
    (void)before;
#endif
    assert(s_credential_count==count&&!s_credential_index&&s_have_credentials);
    assert(!strcmp((char *)s_station_config.sta.ssid,first)&&!strcmp((char *)s_station_config.sta.password,password)&&s_station_config.sta.threshold.authmode==WIFI_AUTH_OPEN&&s_station_config.sta.pmf_cfg.capable&&!s_station_config.sta.pmf_cfg.required);
    profile_snapshot_t applied=snapshot();committed=false;assert(read_credentials(&s_station_config));unchanged(&applied);
}
#ifdef CURRENT_PRIVATE_STORE
static void *desired_writer(void *opaque) {
    unsigned index=(unsigned)(uintptr_t)opaque;
    for(unsigned iteration=0;iteration<20;++iteration) {
        native_wifi_metadata_t meta;assert(network_service_wifi_metadata(&meta)==NATIVE_WIFI_OK&&meta.count==2);
        native_wifi_edit_t edit={0};strcpy(edit.revision,meta.revision);edit.count=meta.count;
        for(size_t row=0;row<meta.count;++row)strcpy(edit.profiles[row].id,meta.profiles[row].id);
        edit.profiles[0].ssid_present=true;
        snprintf(edit.profiles[0].ssid,sizeof(edit.profiles[0].ssid),"writer-%u-%u",index,iteration);
        native_wifi_result_t result=network_service_wifi_edit(&edit);
        assert(result==NATIVE_WIFI_OK||result==NATIVE_WIFI_CONFLICT);
    }
    return NULL;
}
#endif
int main(int argc,char **argv){assert(argc>=2&&strlen(argv[1])<sizeof(root));strcpy(root,argv[1]);char directory[1024];snprintf(directory,sizeof(directory),"%s/data",root);assert(!mkdir(directory,0700)||errno==EEXIST);
    no_mutex=true;assert(web_upload_storage_init()==ESP_ERR_NO_MEM);no_mutex=false;assert(web_upload_storage_init()==ESP_OK);
#ifdef CURRENT_PRIVATE_STORE
    assert(network_service_save_credentials("s","p")==ESP_ERR_INVALID_STATE);
    assert(network_service_storage_init()==ESP_OK);
#endif
    if(argc==3){reset();if(!strcmp(argv[2],"cr")){const char invalid[]="new\tpass\rother\tpass\n";assert(network_service_validate_credentials_file((const uint8_t *)invalid,sizeof(invalid)-1U)!=ESP_OK);}
        else{assert(!strcmp(argv[2],"reload"));post_commit_open_oom=true;const char *valid="new-first\tpass\nnew-second\tsecond\n";assert(network_service_save_credentials_file((const uint8_t *)valid,strlen(valid))==ESP_OK&&s_have_credentials&&s_credential_count==2&&!read_opens_after_commit);}return 0;}
    accept("new\tpass\nsecond\t\n",2,"new","pass");accept(" new \t pass \r\nsecond\t\r\n",2," new "," pass ");accept("new\tpass",1,"new","pass");accept("new\tpass\r",1,"new","pass");accept("\r\n\nnew\t\n\r\n",1,"new","");accept("a\t1\nb\t2\nc\t3\nd\t4\ne\t5\n",5,"a","1");
    char ssid[32],password[64],row[128];memset(ssid,'s',31);ssid[31]=0;memset(password,'p',63);password[63]=0;snprintf(row,sizeof(row),"%s\t%s\n",ssid,password);accept(row,1,ssid,password);
    char limit[800];memset(limit,'\n',799);memcpy(limit,"a\t1\n",4);limit[799]=0;accept(limit,1,"a","1");
    char ssid32[33],password64[65];memset(ssid32,'s',32);ssid32[32]=0;memset(password64,'p',64);password64[64]=0;
    snprintf(row,sizeof(row),"%s\tpass\n",ssid32);reject(row,strlen(row));snprintf(row,sizeof(row),"ssid\t%s\n",password64);reject(row,strlen(row));
    reset();profile_snapshot_t single_before=snapshot();assert(network_service_save_credentials(ssid,password)==ESP_OK);
#ifdef CURRENT_PRIVATE_STORE
    unchanged(&single_before);committed=false;assert(read_credentials(&s_station_config));
#else
    (void)single_before;
#endif
    assert(s_credential_count==1&&!strcmp((char *)s_station_config.sta.ssid,ssid)&&!strcmp((char *)s_station_config.sta.password,password));
    const char *invalid[]={"","\n\r\n","without separator\n","\tpass\n","new\tpass\textra\n","new\tpass\rother\tpass\n","bad\rssid\tpass\n","new\tpa\rss\n","new\tpass\r\r\n","valid\tpass\ninvalid","a\t1\nb\t2\nc\t3\nd\t4\ne\t5\nf\t6\n"};for(size_t index=0;index<sizeof(invalid)/sizeof(invalid[0]);++index)reject(invalid[index],strlen(invalid[index]));const char nul[]="new\tpa\0ss\n";reject(nul,sizeof(nul)-1U);reject(NULL,10);reject(row,0);reject(row,800);reject(row,SIZE_MAX);
    memset(ssid,'s',32);memset(password,'p',64);reset();profile_snapshot_t before=snapshot();assert(network_service_save_credentials(ssid,"pass")!=ESP_OK&&network_service_save_credentials("ssid",password)!=ESP_OK);assert(network_service_save_credentials("ssid\tpass\nother","pass")!=ESP_OK&&network_service_save_credentials("ssid","pass\nother\tpass")!=ESP_OK);assert(network_service_save_credentials(NULL,"pass")!=ESP_OK&&network_service_save_credentials("ssid",NULL)!=ESP_OK);unchanged(&before);assert(equals(live,old_data,strlen(old_data)));
    reset();before=snapshot();assert(network_service_save_credentials(" open ","")==ESP_OK);
#ifdef CURRENT_PRIVATE_STORE
    unchanged(&before);committed=false;assert(read_credentials(&s_station_config));
#endif
    assert(s_credential_count==1&&!strcmp((char *)s_station_config.sta.ssid," open ")&&!s_station_config.sta.password[0]);
    const enum failure failures[]={OPEN_OOM,OPEN_IO,WRITE_SHORT,FLUSH,CLOSE_FILE,LIVE_STAT,RENAME_OLD,RENAME_FINAL,BOTH_RENAMES};
    const char *valid="new-first\tpass\nnew-second\tsecond\n";
    for(size_t index=0;index<sizeof(failures)/sizeof(failures[0]);++index){reset();before=snapshot();failure=failures[index];assert(network_service_save_credentials_file((const uint8_t *)valid,strlen(valid))==ESP_FAIL);unchanged(&before);if(failure==BOTH_RENAMES)assert(equals(backup,old_data,strlen(old_data))&&!exists(live));else assert(equals(live,old_data,strlen(old_data)));failure=NONE;FILE *file=web_upload_open_file(live);assert(file&&!fclose(file)&&equals(live,old_data,strlen(old_data)));assert(network_service_save_credentials_file((const uint8_t *)valid,strlen(valid))==ESP_OK&&s_have_credentials&&s_credential_count==2);}
    for(unsigned mode=0;mode<2;++mode){reset();before=snapshot();post_commit_open_oom=mode==0;post_commit_read_error=mode==1;assert(network_service_save_credentials_file((const uint8_t *)valid,strlen(valid))==ESP_OK&&!read_opens_after_commit);assert(equals(live,valid,strlen(valid)));
#ifdef CURRENT_PRIVATE_STORE
        unchanged(&before);
#else
        assert(s_credential_count==2&&s_have_credentials&&!s_credential_index);
#endif
    }
    reset();assert(!mapped_remove(live));memset(s_credentials,0,sizeof(s_credentials));memset(&s_station_config,0,sizeof(s_station_config));s_credential_count=s_credential_index=0;s_have_credentials=false;before=snapshot();assert(network_service_save_credentials_file((const uint8_t *)valid,strlen(valid))==ESP_OK&&equals(live,valid,strlen(valid)));
#ifdef CURRENT_PRIVATE_STORE
    unchanged(&before);committed=false;assert(read_credentials(&s_station_config)&&s_credential_count==2);
    reset();before=snapshot();native_wifi_metadata_t meta;assert(network_service_wifi_metadata(&meta)==NATIVE_WIFI_OK);
    native_wifi_edit_t deletion={0};strcpy(deletion.revision,meta.revision);
    assert(network_service_wifi_edit(&deletion)==NATIVE_WIFI_OK&&equals(live,"",0));unchanged(&before);
    text(backup,old_data,strlen(old_data));committed=false;
    s_have_credentials=read_credentials(&s_station_config); // Same next-boot admission assignment as production start.
    assert(!s_have_credentials&&!s_credential_count&&equals(live,"",0));
    assert(network_service_wifi_metadata(&meta)==NATIVE_WIFI_OK&&!meta.count);
    reset();before=snapshot();pthread_t writers[2];
    for(unsigned index=0;index<2;++index)assert(!pthread_create(&writers[index],NULL,desired_writer,(void *)(uintptr_t)index));
    for(unsigned index=0;index<2;++index)assert(!pthread_join(writers[index],NULL));
    unchanged(&before);assert(network_service_wifi_metadata(&meta)==NATIVE_WIFI_OK&&meta.count==2);
    assert(!strcmp((char *)s_station_config.sta.ssid,"old-second"));
#else
    assert(s_have_credentials&&s_credential_count==2&&!s_credential_index);
#endif
    assert(writes&&flushes&&closes);printf("PASS C3 Wi-Fi persistence: %u scenarios; actual five-profile validator/save/boot reader, LF/CRLF/EOF/terminal-CR parity, malformed precommit rejection, IO/rollback preserves complete active state, no postcommit read/OOM failure, bounded SSID/password and retry\n",scenarios);return 0;}
