#include "c3_time_settings_platform.h"
#include "runtime.inc"

enum {FAULT_NONE,FAULT_OPEN,FAULT_SET,FAULT_COMMIT};
typedef struct {bool present[5];int number[3];char server[2][35];} saved_t;
static saved_t saved;
static _Thread_local saved_t transaction;
static _Thread_local bool nvs_active;
static _Thread_local unsigned writer;
static atomic_uint nvs_opens,nvs_closes,nvs_commits,fail_at;
static pthread_mutex_t disk=PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t barrier_lock=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t changed=PTHREAD_COND_INITIALIZER;
static bool hold_commit,commit_waiting,commit_released;
static atomic_bool second_waiting;
static unsigned checks;

static SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t p=malloc(sizeof(*p));assert(p&&!pthread_mutex_init(p,NULL));return p;
}
static int xSemaphoreTake(SemaphoreHandle_t p,TickType_t wait) {
    assert(p&&wait!=portMAX_DELAY);
    if(writer==2)atomic_store(&second_waiting,true);
    if(!wait)return pthread_mutex_trylock(p)==0;
    struct timespec until;assert(!clock_gettime(CLOCK_REALTIME,&until));
    until.tv_sec+=wait/1000U;until.tv_nsec+=(long)(wait%1000U)*1000000L;
    if(until.tv_nsec>=1000000000L){++until.tv_sec;until.tv_nsec-=1000000000L;}
    int e=pthread_mutex_timedlock(p,&until);assert(!e||e==ETIMEDOUT);return !e;
}
static void xSemaphoreGive(SemaphoreHandle_t p){assert(!pthread_mutex_unlock(p));}
static size_t strlcpy(char *to,const char *from,size_t size){size_t n=strlen(from);if(size){size_t k=n<size?n:size-1;memcpy(to,from,k);to[k]=0;}return n;}
static int key_id(const char *key) {
    const char *keys[]={"tzh","tzm","timeint","sntp1","sntp2"};
    for(unsigned i=0;i<5;++i)if(!strcmp(key,keys[i]))return (int)i;
    return -1;
}
static esp_err_t nvs_open(const char *space,int mode,nvs_handle_t *out) {
    assert(!strcmp(space,"runtime")&&mode==NVS_READWRITE&&!nvs_active);++nvs_opens;
    if(atomic_load(&fail_at)==FAULT_OPEN)return ESP_FAIL;
    assert(!pthread_mutex_lock(&disk));transaction=saved;assert(!pthread_mutex_unlock(&disk));
    nvs_active=true;*out=1;return ESP_OK;
}
static void nvs_close(nvs_handle_t h){assert(h==1&&nvs_active);nvs_active=false;++nvs_closes;}
static esp_err_t nvs_commit(nvs_handle_t h) {
    assert(h==1&&nvs_active);++nvs_commits;
    if(writer==1&&hold_commit){assert(!pthread_mutex_lock(&barrier_lock));commit_waiting=true;pthread_cond_broadcast(&changed);while(!commit_released)assert(!pthread_cond_wait(&changed,&barrier_lock));assert(!pthread_mutex_unlock(&barrier_lock));}
    if(atomic_load(&fail_at)==FAULT_COMMIT)return ESP_FAIL;
    assert(!pthread_mutex_lock(&disk));saved=transaction;assert(!pthread_mutex_unlock(&disk));return ESP_OK;
}
static esp_err_t read_number(nvs_handle_t h,const char *key,int *out) {
    assert(h==1&&nvs_active);int id=key_id(key);if(id<0||id>=3||!transaction.present[id])return ESP_ERR_NVS_NOT_FOUND;*out=transaction.number[id];return ESP_OK;
}
static esp_err_t nvs_get_u8(nvs_handle_t h,const char *k,uint8_t *out){int n;int e=read_number(h,k,&n);if(!e)*out=(uint8_t)n;return e;}
static esp_err_t nvs_get_i8(nvs_handle_t h,const char *k,int8_t *out){int n;int e=read_number(h,k,&n);if(!e)*out=(int8_t)n;return e;}
static esp_err_t nvs_get_u16(nvs_handle_t h,const char *k,uint16_t *out){int n;int e=read_number(h,k,&n);if(!e)*out=(uint16_t)n;return e;}
static esp_err_t nvs_get_str(nvs_handle_t h,const char *k,char *out,size_t *size){assert(h==1&&nvs_active);int id=key_id(k);if(id<3||!transaction.present[id])return ESP_ERR_NVS_NOT_FOUND;size_t n=strlen(transaction.server[id-3])+1;assert(*size>=n);memcpy(out,transaction.server[id-3],n);*size=n;return ESP_OK;}
static esp_err_t write_number(nvs_handle_t h,const char *key,int value){assert(h==1&&nvs_active);int id=key_id(key);assert(id>=0&&id<3);if(atomic_load(&fail_at)==FAULT_SET)return ESP_FAIL;transaction.present[id]=true;transaction.number[id]=value;return ESP_OK;}
static esp_err_t nvs_set_u8(nvs_handle_t h,const char *k,uint8_t n){return write_number(h,k,n);}
static esp_err_t nvs_set_i8(nvs_handle_t h,const char *k,int8_t n){return write_number(h,k,n);}
static esp_err_t nvs_set_u16(nvs_handle_t h,const char *k,uint16_t n){return write_number(h,k,n);}
static esp_err_t nvs_set_str(nvs_handle_t h,const char *key,const char *value){assert(h==1&&nvs_active);int id=key_id(key);assert(id>=3);if(atomic_load(&fail_at)==FAULT_SET)return ESP_FAIL;transaction.present[id]=true;strlcpy(transaction.server[id-3],value,35);return ESP_OK;}

static runtime_time_settings_t snapshot(void){runtime_time_settings_t out;assert(runtime_settings_get_time_snapshot(&out,100)==ESP_OK);return out;}
static bool equal(const runtime_time_settings_t *a,const runtime_time_settings_t *b){return a->timezone_hour==b->timezone_hour&&a->timezone_minute==b->timezone_minute&&a->sync_interval_min==b->sync_interval_min&&!strcmp(a->servers[0],b->servers[0])&&!strcmp(a->servers[1],b->servers[1]);}
static esp_err_t set_case(unsigned id){switch(id){case 0:return runtime_settings_set_timezone_hour(-7);case 1:return runtime_settings_set_timezone_minute(45);case 2:return runtime_settings_set_time_sync_interval_min(1440);case 3:return runtime_settings_set_sntp1("first.example");default:return runtime_settings_set_sntp2("second.example");}}
static void check_unchanged(const runtime_time_settings_t *old){runtime_time_settings_t now=snapshot();assert(equal(old,&now));++checks;}
static void check_timeout(void) {
    runtime_time_settings_t sentinel;memset(&sentinel,0xa5,sizeof(sentinel));runtime_time_settings_t out=sentinel;
    assert(xSemaphoreTake(s_string_lock,0));
    assert(runtime_settings_get_time_snapshot(&out,5)==ESP_ERR_TIMEOUT);
    assert(!memcmp(&out,&sentinel,sizeof(out)));xSemaphoreGive(s_string_lock);++checks;
}
static void check_setter_timeout(void) {
    for(unsigned i=0;i<5;++i){runtime_time_settings_t old=snapshot();unsigned before=nvs_opens;
        assert(xSemaphoreTake(s_string_lock,0));esp_err_t result=set_case(i);
        assert(nvs_opens==before);assert(result==ESP_ERR_TIMEOUT);xSemaphoreGive(s_string_lock);check_unchanged(&old);}
}
static void check_failures(void) {
    for(unsigned stage=FAULT_OPEN;stage<=FAULT_COMMIT;++stage)for(unsigned i=0;i<5;++i){runtime_time_settings_t old=snapshot();saved_t prior=saved;fail_at=stage;assert(set_case(i)==ESP_FAIL);fail_at=FAULT_NONE;assert(!nvs_active);assert(!memcmp(&prior,&saved,sizeof(saved)));check_unchanged(&old);}
}
static void *first_writer(void *unused){(void)unused;writer=1;assert(runtime_settings_set_sntp1("transaction-one.example")==ESP_OK);return NULL;}
static void *second_writer(void *unused){(void)unused;writer=2;assert(runtime_settings_set_sntp1("transaction-two.example")==ESP_OK);return NULL;}
static void check_concurrent(void) {
    hold_commit=true;pthread_t one,two;assert(!pthread_create(&one,NULL,first_writer,NULL));
    assert(!pthread_mutex_lock(&barrier_lock));while(!commit_waiting)assert(!pthread_cond_wait(&changed,&barrier_lock));assert(!pthread_mutex_unlock(&barrier_lock));
    runtime_time_settings_t sentinel;memset(&sentinel,0xa5,sizeof(sentinel));runtime_time_settings_t out=sentinel;
    assert(runtime_settings_get_time_snapshot(&out,5)==ESP_ERR_TIMEOUT);
    assert(!memcmp(&out,&sentinel,sizeof(out)));
    unsigned before=nvs_opens;assert(!pthread_create(&two,NULL,second_writer,NULL));
    struct timespec brief={0,1000000L};while(!atomic_load(&second_waiting))nanosleep(&brief,NULL);
    assert(nvs_opens==before);
    assert(!pthread_mutex_lock(&barrier_lock));commit_released=true;pthread_cond_broadcast(&changed);assert(!pthread_mutex_unlock(&barrier_lock));
    assert(!pthread_join(one,NULL)&&!pthread_join(two,NULL));
    runtime_time_settings_t now=snapshot();assert(!strcmp(now.servers[0],"transaction-two.example"));assert(!strcmp(now.servers[0],saved.server[0]));++checks;
}
static void check_bounds(void) {
    unsigned opens=nvs_opens;
    assert(runtime_settings_set_timezone_hour(-13)==ESP_ERR_INVALID_ARG);
    assert(runtime_settings_set_timezone_hour(15)==ESP_ERR_INVALID_ARG);
    assert(runtime_settings_set_timezone_minute(60)==ESP_ERR_INVALID_ARG);
    assert(runtime_settings_set_timezone_minute(1)==ESP_ERR_INVALID_ARG);
    assert(runtime_settings_set_time_sync_interval_min(14)==ESP_ERR_INVALID_ARG);
    assert(runtime_settings_set_time_sync_interval_min(1441)==ESP_ERR_INVALID_ARG);
    const char *bad[]={""," ","a/b","a\\b","a\tb","a\x7f","a\"b"};
    for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);++i){assert(runtime_settings_set_sntp1(bad[i])==ESP_ERR_INVALID_ARG);assert(runtime_settings_set_sntp2(bad[i])==ESP_ERR_INVALID_ARG);++checks;}
    char long_name[36];memset(long_name,'a',35);long_name[35]=0;assert(runtime_settings_set_sntp1(long_name)==ESP_ERR_INVALID_ARG);assert(nvs_opens==opens);
    for(int h=-12;h<=14;++h){assert(runtime_settings_set_timezone_hour((int8_t)h)==ESP_OK);assert(snapshot().timezone_hour==h);++checks;}
    for(unsigned m=0;m<=45;m+=15){assert(runtime_settings_set_timezone_minute((uint8_t)m)==ESP_OK);assert(snapshot().timezone_minute==m);++checks;}
    assert(runtime_settings_set_time_sync_interval_min(15)==ESP_OK);assert(runtime_settings_set_time_sync_interval_min(1440)==ESP_OK);
    long_name[34]=0;assert(runtime_settings_set_sntp1(long_name)==ESP_OK);assert(strlen(snapshot().servers[0])==34);
    // The donor's accepted punctuation policy and hour/minute shape remain.
    assert(runtime_settings_set_sntp2("[2001:db8::1]")==ESP_OK);++checks;
}
int main(int argc,char **argv) {
    const char *which=argc>1?argv[1]:"all";
    runtime_time_settings_t out;memset(&out,0x5a,sizeof(out));runtime_time_settings_t before=out;
    assert(runtime_settings_get_time_snapshot(&out,0)==ESP_ERR_INVALID_STATE);assert(!memcmp(&out,&before,sizeof(out)));
    if(!strcmp(which,"invalid_load")){
        for(unsigned i=0;i<5;++i)saved.present[i]=true;
        saved.number[0]=-13;saved.number[1]=7;saved.number[2]=14;
        strcpy(saved.server[0],"bad name");strcpy(saved.server[1],"bad\\name");
    }
    assert(runtime_settings_init()==ESP_OK);runtime_time_settings_t defaults=snapshot();
    assert(defaults.timezone_hour==0&&!defaults.timezone_minute&&defaults.sync_interval_min==60);
    assert(!strcmp(defaults.servers[0],"pool.ntp.org")&&!strcmp(defaults.servers[1],"time.nist.gov"));++checks;
    assert(runtime_settings_get_time_snapshot(NULL,0)==ESP_ERR_INVALID_ARG);++checks;
    assert(runtime_settings_get_time_snapshot(&out,UINT32_MAX)==ESP_OK);++checks;
    if(!strcmp(which,"all")||!strcmp(which,"snapshot_timeout"))check_timeout();
    if(!strcmp(which,"all")||!strcmp(which,"setter_timeout"))check_setter_timeout();
    if(!strcmp(which,"all")||!strcmp(which,"failures"))check_failures();
    if(!strcmp(which,"all")||!strcmp(which,"bounds"))check_bounds();
    if(!strcmp(which,"all")||!strcmp(which,"concurrent"))check_concurrent();
    if(!strcmp(which,"all")){
        for(unsigned i=0;i<5;++i)assert(set_case(i)==ESP_OK);
        assert(runtime_settings_init()==ESP_OK);runtime_time_settings_t loaded=snapshot();
        assert(loaded.timezone_hour==-7&&loaded.timezone_minute==45&&loaded.sync_interval_min==1440);
        assert(!strcmp(loaded.servers[0],"first.example")&&!strcmp(loaded.servers[1],"second.example"));++checks;
        char original[35];memcpy(original,s_sntp1,sizeof(original));memset(s_sntp1,'x',sizeof(s_sntp1));out=before;
        assert(runtime_settings_get_time_snapshot(&out,0)==ESP_ERR_INVALID_STATE);assert(!memcmp(&out,&before,sizeof(out)));memcpy(s_sntp1,original,sizeof(original));++checks;
    }
    assert(!pthread_mutex_destroy(s_string_lock));free(s_string_lock);
    printf("PASS C3 time settings %s checks=%u; actual runtime unit, NVS/RTOS seams; no target flash claim\n",which,checks);
    return 0;
}
