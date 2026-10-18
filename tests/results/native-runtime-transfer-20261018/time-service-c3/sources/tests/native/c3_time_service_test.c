#include "c3_time_service_platform.h"
static int tested_setenv(const char *,const char *,int);
static void tested_tzset(void);
#define setenv tested_setenv
#define tzset tested_tzset
#include "service.inc"
#undef setenv
#undef tzset

enum {CALLER,WORKER,CALLBACK};
static _Thread_local unsigned role;
struct host_task {pthread_t thread;pthread_mutex_t lock;pthread_cond_t changed;uint32_t events;bool stopping;void(*entry)(void*);void *arg;};
static atomic_uint created_mutexes,deleted_mutexes,created_tasks,snapshots,backend_inits,applies,restarts,sync_notes;
static atomic_uint active_backend,max_backend;
static atomic_bool fail_mutex,fail_task,fail_env,backend_ready,constructor_barrier;
static atomic_bool second_lock_waiting,worker_lock_waiting;
static _Thread_local bool second_caller;
static atomic_int snapshot_error,init_error,apply_error,restart_error;
static pthread_mutex_t settings_lock=PTHREAD_MUTEX_INITIALIZER;
static runtime_time_settings_t desired={.sync_interval_min=60,.servers={"first.example","second.example"}};
static pthread_mutex_t spy_lock=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t spy_changed=PTHREAD_COND_INITIALIZER;
static native_time_sntp_config_t last_config;
static native_time_sntp_sync_cb_t sync_callback;
static void *sync_context;
static bool hold_apply,apply_waiting,apply_released;
static unsigned constructor_arrivals;
static unsigned tz_changes;
static int result_a,result_b;

static void wait_until(bool (*predicate)(void)) {
    struct timespec start,now;assert(!clock_gettime(CLOCK_MONOTONIC,&start));
    while(!predicate()){
        assert(!clock_gettime(CLOCK_MONOTONIC,&now));
        assert(now.tv_sec-start.tv_sec<3);
        struct timespec pause={0,1000000L};nanosleep(&pause,NULL);
    }
}
static bool has_apply(void){return atomic_load(&applies)>0;}
static bool has_restart(void){return atomic_load(&restarts)>0;}
static bool has_two_applies(void){return atomic_load(&applies)>=2;}
static bool second_at_gate(void){return atomic_load(&second_lock_waiting)||has_two_applies();}
static bool worker_at_gate(void){return atomic_load(&worker_lock_waiting)||atomic_load(&restarts)>0;}
static bool no_backend(void){return !atomic_load(&active_backend);}
static bool first_apply_waiting(void){assert(!pthread_mutex_lock(&spy_lock));bool b=apply_waiting;assert(!pthread_mutex_unlock(&spy_lock));return b;}
static SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    assert(role!=CALLBACK);
    if(atomic_exchange(&fail_mutex,false))return NULL;
    SemaphoreHandle_t p=malloc(sizeof(*p));assert(p&&!pthread_mutex_init(p,NULL));++created_mutexes;
    if(atomic_load(&constructor_barrier)){
        assert(!pthread_mutex_lock(&spy_lock));++constructor_arrivals;pthread_cond_broadcast(&spy_changed);
        while(constructor_arrivals<2)assert(!pthread_cond_wait(&spy_changed,&spy_lock));
        assert(!pthread_mutex_unlock(&spy_lock));
    }
    return p;
}
static int xSemaphoreTake(SemaphoreHandle_t p,unsigned wait) {assert(role!=CALLBACK&&p&&wait==portMAX_DELAY);if(second_caller)second_lock_waiting=true;if(role==WORKER)worker_lock_waiting=true;assert(!pthread_mutex_lock(p));return pdTRUE;}
static void xSemaphoreGive(SemaphoreHandle_t p){assert(role!=CALLBACK);assert(!pthread_mutex_unlock(p));}
static void vSemaphoreDelete(SemaphoreHandle_t p){assert(role!=CALLBACK);assert(!pthread_mutex_destroy(p));free(p);++deleted_mutexes;}
static void *run_task(void *p){struct host_task *task=p;role=WORKER;task->entry(task->arg);return NULL;}
static int xTaskCreate(void(*entry)(void*),const char *name,unsigned stack,void *arg,unsigned priority,TaskHandle_t *out) {
    assert(role!=CALLBACK&&!strcmp(name,"time_sync")&&stack==2048&&priority==1);
    if(atomic_exchange(&fail_task,false))return 0;
    struct host_task *task=calloc(1,sizeof(*task));assert(task);
    assert(!pthread_mutex_init(&task->lock,NULL)&&!pthread_cond_init(&task->changed,NULL));
    task->entry=entry;task->arg=arg;assert(!pthread_create(&task->thread,NULL,run_task,task));*out=task;++created_tasks;return pdPASS;
}
static int xTaskNotify(TaskHandle_t task,uint32_t bits,unsigned action) {
    assert(task&&action==eSetBits);assert(!pthread_mutex_lock(&task->lock));task->events|=bits;pthread_cond_broadcast(&task->changed);assert(!pthread_mutex_unlock(&task->lock));return pdPASS;
}
static int xTaskNotifyWait(uint32_t entry,uint32_t exit,uint32_t *bits,unsigned timeout) {
    assert(role==WORKER&&!entry&&exit==UINT32_MAX&&timeout==portMAX_DELAY);
    TaskHandle_t task;
    while(!(task=atomic_load(&s_time_sync_task))){struct timespec pause={0,1000000L};nanosleep(&pause,NULL);}
    assert(!pthread_mutex_lock(&task->lock));while(!task->events&&!task->stopping)assert(!pthread_cond_wait(&task->changed,&task->lock));
    if(task->stopping){assert(!pthread_mutex_unlock(&task->lock));pthread_exit(NULL);}
    *bits=task->events;task->events=0;assert(!pthread_mutex_unlock(&task->lock));return pdTRUE;
}
static size_t strlcpy(char *to,const char *from,size_t capacity){size_t n=strlen(from);if(capacity){size_t k=n<capacity?n:capacity-1;memcpy(to,from,k);to[k]=0;}return n;}
static int tested_setenv(const char *key,const char *value,int replace){assert(role!=CALLBACK&&!strcmp(key,"TZ")&&replace==1);if(atomic_exchange(&fail_env,false))return -1;++tz_changes;return setenv(key,value,replace);}
static void tested_tzset(void){assert(role!=CALLBACK);tzset();}
esp_err_t runtime_settings_get_time_snapshot(runtime_time_settings_t *out,uint32_t timeout) {
    assert(role!=CALLBACK&&timeout==100);++snapshots;
    if(atomic_load(&snapshot_error))return atomic_load(&snapshot_error);
    assert(!pthread_mutex_lock(&settings_lock));*out=desired;assert(!pthread_mutex_unlock(&settings_lock));return ESP_OK;
}
esp_err_t native_time_sntp_init(native_time_sntp_sync_cb_t callback,void *context) {
    assert(role!=CALLBACK);++backend_inits;
    if(atomic_load(&init_error))return atomic_load(&init_error);
    assert(!pthread_mutex_lock(&spy_lock));if(sync_callback)assert(sync_callback==callback&&sync_context==context);sync_callback=callback;sync_context=context;assert(!pthread_mutex_unlock(&spy_lock));return ESP_OK;
}
void native_time_sntp_notify_network_ready(void){assert(role==CALLBACK);atomic_store(&backend_ready,true);}
static void backend_enter(void) {assert(role!=CALLBACK&&atomic_load(&backend_ready));unsigned active=atomic_fetch_add(&active_backend,1)+1;assert(active==1);atomic_store(&max_backend,active);}
static void backend_leave(void){assert(atomic_fetch_sub(&active_backend,1)==1);}
esp_err_t native_time_sntp_apply(const native_time_sntp_config_t *config) {
    backend_enter();assert(config->server_count==2);++applies;
    assert(!pthread_mutex_lock(&spy_lock));
    if(hold_apply){apply_waiting=true;pthread_cond_broadcast(&spy_changed);while(!apply_released)assert(!pthread_cond_wait(&spy_changed,&spy_lock));}
    int result=atomic_load(&apply_error);if(!result)last_config=*config;assert(!pthread_mutex_unlock(&spy_lock));backend_leave();return result;
}
esp_err_t native_time_sntp_restart(void){backend_enter();++restarts;int e=atomic_load(&restart_error);backend_leave();return e;}
static void ready(void){unsigned previous=role;role=CALLBACK;time_service_notify_network_ready();role=previous;}
static void complete_sync(void){unsigned previous=role;role=CALLBACK;struct timeval tv={1704067200,0};sync_callback(sync_context,&tv);role=previous;++sync_notes;}
static void release_apply(void){assert(!pthread_mutex_lock(&spy_lock));apply_released=true;pthread_cond_broadcast(&spy_changed);assert(!pthread_mutex_unlock(&spy_lock));}
static void *caller_a(void *unused){(void)unused;result_a=time_service_apply();return NULL;}
static void *caller_b(void *unused){(void)unused;second_caller=true;result_b=time_service_apply();return NULL;}
static void set_desired(int hour,unsigned minute,const char *server){assert(!pthread_mutex_lock(&settings_lock));desired.timezone_hour=(int8_t)hour;desired.timezone_minute=(uint8_t)minute;strlcpy(desired.servers[0],server,35);assert(!pthread_mutex_unlock(&settings_lock));}
static void check_timezone(int hour,unsigned minute,const char *expected,int local_hour,int local_minute,int day){
    set_desired(hour,minute,"first.example");assert(time_service_apply()==ESP_OK);assert(!strcmp(getenv("TZ"),expected));
    // Existing OLED/deep-sleep consumers call localtime_r, rather than parsing
    // TZ. Exercise the real host libc conversion and the previous-day edge.
    time_t epoch=1704067200;struct tm local;
    assert(localtime_r(&epoch,&local));
    assert(local.tm_hour==local_hour&&local.tm_min==local_minute&&local.tm_mday==day);
}
static void settle_controller(void){SemaphoreHandle_t p=atomic_load(&s_control_lock);assert(p);assert(!pthread_mutex_lock(p));assert(!pthread_mutex_unlock(p));}
static void cleanup(void) {
    wait_until(no_backend);SemaphoreHandle_t lock=atomic_load(&s_control_lock);
    if(lock){assert(!pthread_mutex_lock(lock));assert(!pthread_mutex_unlock(lock));}
    TaskHandle_t task=atomic_load(&s_time_sync_task);
    if(task){assert(!pthread_mutex_lock(&task->lock));task->stopping=true;pthread_cond_broadcast(&task->changed);assert(!pthread_mutex_unlock(&task->lock));assert(!pthread_join(task->thread,NULL));pthread_mutex_destroy(&task->lock);pthread_cond_destroy(&task->changed);free(task);}
    if(lock)vSemaphoreDelete(lock);
    assert(created_mutexes==deleted_mutexes);
}
int main(int argc,char **argv) {
    assert(argc==2);const char *which=argv[1];assert(!setenv("TZ","UTC+9:00",1));tzset();
    if(!strcmp(which,"offline")){check_timezone(5,45,"UTC-5:45",5,45,1);assert(!applies&&!restarts&&s_apply_pending);ready();wait_until(has_apply);wait_until(no_backend);settle_controller();assert(!s_apply_pending&&s_backend_applied);}
    else if(!strcmp(which,"early_ip")){ready();assert(time_service_apply()==ESP_OK);assert(applies==1&&!s_apply_pending);}
    else if(!strcmp(which,"snapshot_failure")){snapshot_error=ESP_ERR_TIMEOUT;assert(time_service_apply()==ESP_ERR_TIMEOUT);assert(!backend_inits&&!applies&&!tz_changes&&!strcmp(getenv("TZ"),"UTC+9:00"));}
    else if(!strcmp(which,"init_failure")){init_error=ESP_ERR_NO_MEM;assert(time_service_apply()==ESP_ERR_NO_MEM);assert(!applies&&!tz_changes);}
    else if(!strcmp(which,"setenv_failure")){ready();fail_env=true;assert(time_service_apply()==ESP_FAIL);assert(!applies&&s_apply_pending&&!strcmp(getenv("TZ"),"UTC+9:00"));}
    else if(!strcmp(which,"apply_failure")){ready();apply_error=ESP_FAIL;assert(time_service_apply()==ESP_FAIL);assert(applies==1&&s_apply_pending&&!s_backend_applied);apply_error=0;assert(time_service_apply()==ESP_OK);assert(!s_apply_pending&&applies==2);}
    else if(!strcmp(which,"restart_failure")){ready();assert(time_service_apply()==ESP_OK);restart_error=ESP_FAIL;ready();wait_until(has_restart);wait_until(no_backend);settle_controller();assert(s_apply_pending);restart_error=0;ready();wait_until(has_two_applies);wait_until(no_backend);settle_controller();assert(!s_apply_pending&&restarts==1);}
    else if(!strcmp(which,"task_failure")){fail_task=true;assert(time_service_apply()==ESP_ERR_NO_MEM);assert(!created_tasks&&!backend_inits&&!tz_changes);assert(time_service_apply()==ESP_OK&&created_tasks==1);}
    else if(!strcmp(which,"mutex_oom")){fail_mutex=true;assert(time_service_apply()==ESP_ERR_NO_MEM);assert(!created_tasks&&!snapshots&&!tz_changes);assert(time_service_apply()==ESP_OK);}
    else if(!strcmp(which,"concurrent_start")){constructor_barrier=true;pthread_t a,b;assert(!pthread_create(&a,NULL,caller_a,NULL)&&!pthread_create(&b,NULL,caller_b,NULL));assert(!pthread_join(a,NULL)&&!pthread_join(b,NULL));assert(result_a==ESP_OK&&result_b==ESP_OK&&created_tasks==1&&created_mutexes==2&&deleted_mutexes==1);}
    else if(!strcmp(which,"serialized_order")||!strcmp(which,"reconnect_serialized")){
        ready();hold_apply=true;pthread_t a,b;assert(!pthread_create(&a,NULL,caller_a,NULL));wait_until(first_apply_waiting);unsigned before=snapshots;
        if(!strcmp(which,"serialized_order")){set_desired(-7,30,"new.example");assert(!pthread_create(&b,NULL,caller_b,NULL));wait_until(second_at_gate);}
        else {ready();complete_sync();wait_until(worker_at_gate);}
        assert(snapshots==before);assert(active_backend==1);
        release_apply();assert(!pthread_join(a,NULL));
        if(!strcmp(which,"serialized_order")){assert(!pthread_join(b,NULL));assert(result_a==ESP_OK&&result_b==ESP_OK);assert(!strcmp(last_config.servers[0],"new.example")&&!strcmp(getenv("TZ"),"UTC+7:30"));}
        else {wait_until(has_restart);wait_until(no_backend);assert(sync_notes==1);}
        assert(max_backend==1);
    }
    else if(!strcmp(which,"timezone")){check_timezone(-12,45,"UTC+12:45",11,15,31);check_timezone(14,45,"UTC-14:45",14,45,1);check_timezone(-5,30,"UTC+5:30",18,30,31);check_timezone(0,30,"UTC-0:30",0,30,1);check_timezone(0,0,"UTC+0:00",0,0,1);}
    else assert(!"unknown case");
    assert(created_tasks<=1);cleanup();printf("PASS C3 time adapter %s; actual worker/control code, RTOS/settings/backend seams\n",which);return 0;
}
