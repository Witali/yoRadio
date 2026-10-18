/* Actual SDK SNTP core/managed APIs/raw ESP wrappers + old/current donor.
 * Only the scheduler, DNS transport entry, RTOS and system boundaries are
 * seams. DNS is paused before its actual enqueue copies the borrowed name. */
#include "platform.inc"
typedef void *TaskHandle_t;
#define BOARD_TASK_STACK_TIME_SYNC 2048U
#define portMAX_DELAY UINT32_MAX
#define eSetBits 1
static int task_marker;
static unsigned task_creates;
static int xTaskCreate(void(*fn)(void*),const char *name,unsigned stack,void *arg,unsigned priority,TaskHandle_t *out){(void)fn;assert(!strcmp(name,"time_sync")&&stack==2048&&priority==1&&!arg);++task_creates;*out=&task_marker;return pdPASS;}
static int xTaskNotify(TaskHandle_t task,uint32_t events,unsigned action){assert(task==&task_marker&&events&&action==eSetBits);return pdPASS;}
static int xTaskNotifyWait(uint32_t a,uint32_t b,uint32_t *events,unsigned ticks){(void)a;(void)b;(void)events;(void)ticks;assert(!"worker is outside this DNS ownership fixture");return 0;}
static size_t strlcpy(char *to,const char *from,size_t capacity){size_t n=strlen(from);if(capacity){size_t k=n<capacity?n:capacity-1;memcpy(to,from,k);to[k]=0;}return n;}
static const char *esp_err_to_name(int error){(void)error;return "host error";}
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
struct tcpip_api_call_data {unsigned unused;};
#define __containerof(p,type,member) ((type *)((char *)(p)-offsetof(type,member)))
static err_t tcpip_api_call(err_t(*fn)(struct tcpip_api_call_data *),struct tcpip_api_call_data *ctx);
static void host_dns_pause(const char *name);
#include "pinned.inc"
#include "raw-wrappers.inc"
#ifndef OLD_SOURCE
#include "backend.inc"
#endif
#include "runtime_settings.h"
#include "time_service.h"

static runtime_time_settings_t desired={.sync_interval_min=60,.servers={"old-first.example","old-second.example"}};
static pthread_mutex_t schedule=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t schedule_changed=PTHREAD_COND_INITIALIZER;
static struct {void(*fn)(void*);void *ctx;} callbacks[16];
static unsigned callback_head,callback_tail;
static bool pause_dns,dns_waiting,dns_release,ipc_waiting,stop_queued,stop_completed;
static const char *dns_borrowed;
static char dns_before[35],dns_after[35];
static esp_err_t apply_result;

int8_t runtime_settings_get_timezone_hour(void){return desired.timezone_hour;}
uint8_t runtime_settings_get_timezone_minute(void){return desired.timezone_minute;}
uint16_t runtime_settings_get_time_sync_interval_min(void){return desired.sync_interval_min;}
void runtime_settings_get_sntp1(char *out,size_t n){strlcpy(out,desired.servers[0],n);}
void runtime_settings_get_sntp2(char *out,size_t n){strlcpy(out,desired.servers[1],n);}
esp_err_t runtime_settings_get_time_snapshot(runtime_time_settings_t *out,uint32_t timeout){assert(timeout==100);*out=desired;return ESP_OK;}
#include "donor.inc"

static void wait_for(bool *condition) {
    struct timespec until;assert(!clock_gettime(CLOCK_REALTIME,&until));until.tv_sec+=3;
    assert(!pthread_mutex_lock(&schedule));
    while(!*condition){int e=pthread_cond_timedwait(&schedule_changed,&schedule,&until);assert(e==0);}
    assert(!pthread_mutex_unlock(&schedule));
}
static int tcpip_callback(void(*fn)(void*),void *ctx) {
    assert(!pthread_mutex_lock(&schedule));assert(callback_tail<16);
    callbacks[callback_tail].fn=fn;callbacks[callback_tail].ctx=ctx;++callback_tail;
    if(fn==do_stop){stop_queued=true;pthread_cond_broadcast(&schedule_changed);}
    assert(!pthread_mutex_unlock(&schedule));return ERR_OK;
}
static void drain_callbacks(void) {
    assert(in_tcpip);
    for(;;){assert(!pthread_mutex_lock(&schedule));
        if(callback_head==callback_tail){assert(!pthread_mutex_unlock(&schedule));return;}
        void(*fn)(void*)=callbacks[callback_head].fn;void *ctx=callbacks[callback_head++].ctx;
        assert(!pthread_mutex_unlock(&schedule));fn(ctx);
        if(fn==do_stop){assert(!pthread_mutex_lock(&schedule));stop_completed=true;assert(!pthread_mutex_unlock(&schedule));}
    }
}
static void before_ipc(void) {
    assert(!in_tcpip);assert(!pthread_mutex_lock(&schedule));
    if(pause_dns){ipc_waiting=true;pthread_cond_broadcast(&schedule_changed);}
    assert(!pthread_mutex_unlock(&schedule));
    assert(!pthread_mutex_lock(&tcpip_lock));in_tcpip=true;drain_callbacks();
}
static void after_ipc(void){assert(in_tcpip);in_tcpip=false;assert(!pthread_mutex_unlock(&tcpip_lock));}
static err_t tcpip_api_call(err_t(*fn)(struct tcpip_api_call_data *),struct tcpip_api_call_data *ctx){before_ipc();err_t e=fn(ctx);after_ipc();return e;}
static esp_err_t esp_netif_tcpip_exec(esp_err_t(*fn)(void*),void *ctx){++ipc_calls;before_ipc();esp_err_t e=fn(ctx);after_ipc();return e;}
static void flush_async(void){before_ipc();after_ipc();}
static void host_dns_pause(const char *name) {
    if(!pause_dns)return;
    assert(in_tcpip);assert(!pthread_mutex_lock(&schedule));dns_borrowed=name;strlcpy(dns_before,name,sizeof(dns_before));dns_waiting=true;pthread_cond_broadcast(&schedule_changed);
    while(!dns_release)assert(!pthread_cond_wait(&schedule_changed,&schedule));
    strlcpy(dns_after,name,sizeof(dns_after));assert(!pthread_mutex_unlock(&schedule));
}
static void *request_thread(void *unused){(void)unused;assert(!pthread_mutex_lock(&tcpip_lock));in_tcpip=true;sntp_request(NULL);in_tcpip=false;assert(!pthread_mutex_unlock(&tcpip_lock));return NULL;}
static void *apply_thread(void *unused){(void)unused;apply_result=time_service_apply();return NULL;}

int main(void) {
    time_service_notify_network_ready();assert(time_service_apply()==ESP_OK);flush_async();assert(sntp_enabled()&&task_creates==1);
    assert(!strcmp(sntp_getservername(0),"old-first.example"));
    pause_dns=true;pthread_t request,apply;assert(!pthread_create(&request,NULL,request_thread,NULL));wait_for(&dns_waiting);
    assert(!strcmp(dns_before,"old-first.example"));
    strcpy(desired.servers[0],"new-first.example");strcpy(desired.servers[1],"new-second.example");
    assert(!pthread_create(&apply,NULL,apply_thread,NULL));wait_for(&ipc_waiting);
    assert(!pthread_mutex_lock(&schedule));
    bool overwritten=strcmp(dns_borrowed,dns_before)!=0;
#ifdef OLD_SOURCE
    assert(stop_queued&&!stop_completed&&sntp_enabled());
    assert(overwritten);
#else
    assert(!stop_queued&&!stop_completed&&sntp_enabled());
    assert(!overwritten);
#endif
    dns_release=true;pthread_cond_broadcast(&schedule_changed);assert(!pthread_mutex_unlock(&schedule));
    assert(!pthread_join(request,NULL)&&!pthread_join(apply,NULL));assert(apply_result==ESP_OK);pause_dns=false;flush_async();
    assert(!strcmp(sntp_getservername(0),"new-first.example"));
#ifdef OLD_SOURCE
    assert(!strcmp(dns_after,"new-first.example")&&stop_completed);
#else
    assert(!strcmp(dns_after,"old-first.example"));
#endif
    bool copied=false;for(unsigned i=0;i<DNS_TABLE_SIZE;++i)if(dns_requests[i].found&&!strcmp(dns_table[i].name,dns_after))copied=true;
    assert(copied); // The actual pinned DNS enqueue copied what it read.
    assert(!pthread_mutex_lock(&tcpip_lock));in_tcpip=true;sntp_stop();in_tcpip=false;assert(!pthread_mutex_unlock(&tcpip_lock));
    if(s_storage){free(s_storage);s_storage=NULL;}cleanup_sems();assert(udp_created==udp_removed);
#ifdef OLD_SOURCE
    puts("NEGATIVE_CONTROL_FAIL: actual historical C3 apply overwrote borrowed DNS name before queued SDK stop ACK");return 1;
#else
    puts("PASS C3 lifetime: actual adapter/shared backend + pinned SDK/DNS; paused pre-enqueue name remains immutable through checked rebind");return 0;
#endif
}
