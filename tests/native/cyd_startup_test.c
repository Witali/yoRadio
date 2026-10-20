#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "audio_service.h"
#include "decoder_registration.h"
#include "stream_probe.h"
#include "stream_bitrate.h"
#include "audio_power_seam.h"
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
#include "adaptive_input.h"
#endif
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
#include "native_input_reclaim.h"
#endif

typedef void *QueueHandle_t, *RingbufHandle_t;
#define RINGBUF_TYPE_NOSPLIT 1
#define BOARD_TASK_STACK_RADIO_STREAM 6144
#define BOARD_TASK_STACK_AUDIO_DECODER 16384
#define BOARD_TASK_STACK_AUDIO_OUTPUT 4096
#define MALLOC_CAP_8BIT 1
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
static atomic_uint startup_warnings;
#define ESP_LOGW(...) ((void)atomic_fetch_add(&startup_warnings,1))
#define STARTUP_CHECK(value, marker) do { if (!(value)) { \
    fprintf(stderr,"SEMANTIC_FAILURE:%s:%u\n",marker,__LINE__); exit(80); \
} } while(0)
struct test_sem {pthread_mutex_t lock; bool binary;};
struct test_task {
    pthread_t thread;
    pthread_mutex_t lock;
    pthread_cond_t changed;
    TaskFunction_t entry;
    void *argument;
    bool notified, deleted, at_gate;
};
static _Thread_local TaskHandle_t current_task;
static native_state_t state;
static void *allocations[128], *registered[6], *output_memory;
static unsigned allocation_calls, failure_allocation, live_allocations, registration_calls;
static unsigned task_calls, failure_task, registration_failure, output_calls, led_calls;
static unsigned deleted_tasks, tracked_tasks, notifications, queue_writes, scenarios;
static int output_error, led_error;
static bool fail_control;
static atomic_uint ran_tasks;
static TaskHandle_t created_tasks[3];
static void check_not_ready(void);
static void (*allocation_hook)(void);
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
static atomic_uint startup_bind_attempts;
static atomic_bool startup_bind_accepted;
static adaptive_input_t *foreign_pool;
static unsigned tls_original_calls, tls_allocation_probes, health_hook_calls;
typedef void (*failed_allocation_hook_t)(size_t, uint32_t, const char *);
static failed_allocation_hook_t health_hook;
static unsigned health_hook_registrations;
static void tls_during_allocation(void);
static void observe_health_failure(size_t size, uint32_t caps, const char *function) {
    STARTUP_CHECK(size==37 && caps==MALLOC_CAP_8BIT && function,"health_failure_unchanged_arguments");
    ++health_hook_calls;
}
esp_err_t heap_caps_register_failed_alloc_callback(failed_allocation_hook_t hook) {
    ++health_hook_registrations;health_hook=hook;return ESP_OK;
}
void *__real_esp_mbedtls_mem_calloc(size_t count,size_t size) {
    STARTUP_CHECK(count==1 && size==37,"original_tls_calloc_arguments");
    ++tls_original_calls;
    STARTUP_CHECK(health_hook==observe_health_failure && health_hook_registrations==1,"global_health_hook_preserved");
    health_hook(size,MALLOC_CAP_8BIT,"esp_mbedtls_mem_calloc");return NULL;
}
bool __real_native_input_reclaim_bind(adaptive_input_t *input);
#endif

static void *tracked_malloc(size_t size) {
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    tls_during_allocation();
#endif
    if(allocation_hook){void (*hook)(void)=allocation_hook;allocation_hook=NULL;hook();}
    ++allocation_calls;if(allocation_calls==failure_allocation)return NULL;
    void *value=malloc(size);assert(value);
    for(unsigned i=0;i<128;++i)if(!allocations[i]) {
        allocations[i]=value;++live_allocations;return value;
    }
    assert(!"allocation tracker full");return NULL;
}
static void *tracked_calloc(size_t count,size_t size) {
    assert(!count || size<=SIZE_MAX/count);void *value=tracked_malloc(count*size);
    if(value)memset(value,0,count*size);
    return value;
}
static void tracked_free(void *value) {
    if(!value)return;
    for(unsigned i=0;i<128;++i)if(allocations[i]==value) {
        allocations[i]=NULL;assert(live_allocations);--live_allocations;free(value);return;
    }
    assert(!"untracked/double free");
}
SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    check_not_ready();SemaphoreHandle_t value=tracked_calloc(1,sizeof(*value));
    if(value)assert(!pthread_mutex_init(&value->lock,NULL));
    return value;
}
SemaphoreHandle_t xSemaphoreCreateBinary(void) {
    SemaphoreHandle_t value=xSemaphoreCreateMutex();if(value)value->binary=true;return value;
}
int xSemaphoreTake(SemaphoreHandle_t value,unsigned timeout) {
    (void)timeout;assert(value);
    if(value->binary)return pdFALSE;
    assert(!pthread_mutex_lock(&value->lock));return pdTRUE;
}
int xSemaphoreGive(SemaphoreHandle_t value) {
    assert(value);if(!value->binary)assert(!pthread_mutex_unlock(&value->lock));return pdTRUE;
}
void vSemaphoreDelete(SemaphoreHandle_t value) {
    assert(value && !pthread_mutex_destroy(&value->lock));tracked_free(value);
}
TickType_t xTaskGetTickCount(void) {return 0;}
void vTaskDelay(unsigned ticks) {(void)ticks;assert(!"no queue waits in startup tests");}
size_t strlcpy(char *to,const char *from,size_t capacity) {
    size_t size=strlen(from);
    if(capacity){size_t copy=size<capacity ? size : capacity-1;memcpy(to,from,copy);to[copy]=0;}
    return size;
}
static void *xQueueCreate(unsigned count,size_t size) {
    check_not_ready();assert(count==1);return tracked_malloc(count*size);
}
static void vQueueDelete(void *queue) {tracked_free(queue);}
static void *xRingbufferCreate(size_t size,unsigned type) {
    check_not_ready();assert(type==RINGBUF_TYPE_NOSPLIT);return tracked_malloc(size);
}
static void vRingbufferDelete(void *ring) {tracked_free(ring);}
static int xQueueOverwrite(void *queue,const void *data) {
    assert(queue && data);++queue_writes;return pdTRUE;
}
static int native_audio_output_init(void) {
    check_not_ready();++output_calls;if(output_error)return output_error;
    assert(!output_memory);output_memory=tracked_malloc(64);
    return output_memory ? ESP_OK : ESP_ERR_NO_MEM;
}
static int audio_level_led_init(void) {check_not_ready();++led_calls;return led_error;}
static const char *native_audio_output_name(void) {return "host startup seam";}
/* Startup/control tests exclude output-driver maintenance behavior. */
static void native_audio_output_request_pause(bool requested) {(void)requested;}
static size_t heap_caps_get_free_size(unsigned caps) {(void)caps;return 10000;}
static void stream_task(void *), decoder_task(void *), output_task(void *);
static void vTaskDelete(TaskHandle_t task) {
    if(!task){assert(current_task);pthread_exit(NULL);}
    assert(!pthread_mutex_lock(&task->lock));task->deleted=true;
    assert(!pthread_cond_broadcast(&task->changed));assert(!pthread_mutex_unlock(&task->lock));
    assert(!pthread_join(task->thread,NULL));
    assert(!pthread_mutex_destroy(&task->lock) && !pthread_cond_destroy(&task->changed));
    for(unsigned i=0;i<3;++i)if(created_tasks[i]==task)created_tasks[i]=NULL;
    free(task);++deleted_tasks;
}
static uint32_t ulTaskNotifyTake(int clear,unsigned timeout) {
    assert(clear==pdTRUE && timeout==portMAX_DELAY && current_task);
    TaskHandle_t task=current_task;assert(!pthread_mutex_lock(&task->lock));
    task->at_gate=true;assert(!pthread_cond_broadcast(&task->changed));
    while(!task->notified && !task->deleted)
        assert(!pthread_cond_wait(&task->changed,&task->lock));
    bool deleted=task->deleted;assert(!pthread_mutex_unlock(&task->lock));
    if(deleted)pthread_exit(NULL);
    return 1;
}
static void *task_entry(void *argument) {
    current_task=argument;current_task->entry(current_task->argument);assert(false);return NULL;
}
static int xTaskCreatePinnedToCore(TaskFunction_t function,const char *name,uint32_t stack,
                                  void *argument,unsigned priority,TaskHandle_t *out,int core) {
    check_not_ready();unsigned index=task_calls++;
    assert(index<3 && out && argument);
    assert(stack==(index==0 ? 6144U : index==1 ? 16384U : 4096U));
    assert(priority==(index==0 ? 3U : index==1 ? 5U : 6U));
    assert(core==(index==0 ? 0 : 1) && name && *name);
    if(index+1==failure_task)return pdFALSE;
    TaskHandle_t task=calloc(1,sizeof(*task));assert(task);
    assert(!pthread_mutex_init(&task->lock,NULL) && !pthread_cond_init(&task->changed,NULL));
    task->entry=function;task->argument=argument;*out=created_tasks[index]=task;
    assert(!pthread_create(&task->thread,NULL,task_entry,task));
    // Force the SMP scheduling case in which a new task runs immediately,
    // before startup can allocate the next task or initialize its output.
    assert(!pthread_mutex_lock(&task->lock));
    while(!task->at_gate)assert(!pthread_cond_wait(&task->changed,&task->lock));
    assert(!pthread_mutex_unlock(&task->lock));return pdPASS;
}
static void xTaskNotifyGive(TaskHandle_t task) {
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    STARTUP_CHECK(atomic_load(&startup_bind_attempts)==1,"bind_before_first_notification");
#endif
    assert(task);++notifications;assert(!pthread_mutex_lock(&task->lock));
    task->notified=true;assert(!pthread_cond_broadcast(&task->changed));
    assert(!pthread_mutex_unlock(&task->lock));
}
void native_health_track_task(native_health_task_t role,void *task) {
    assert(role<=NATIVE_HEALTH_OUTPUT && task==created_tasks[role]);++tracked_tasks;
}
static int register_one(unsigned index) {
    check_not_ready();++registration_calls;assert(index<6 && !registered[index]);
    registered[index]=tracked_malloc(8);
    if(!registered[index])return ESP_AUDIO_ERR_MEM_LACK;
    // Deliberately leave a partial entry behind on an injected API error.
    return registration_failure==registration_calls ? ESP_FAIL : ESP_AUDIO_ERR_OK;
}
esp_audio_err_t esp_mp3_dec_register(void) {return register_one(0);}
esp_audio_err_t esp_aac_dec_register(void) {return register_one(1);}
esp_audio_err_t esp_flac_dec_register(void) {return register_one(2);}
esp_audio_err_t esp_vorbis_dec_register(void) {return register_one(3);}
esp_audio_err_t esp_opus_dec_register(void) {return register_one(4);}
esp_audio_err_t esp_audio_simple_dec_register_default(void) {return register_one(5);}
void esp_audio_simple_dec_unregister_default(void) {tracked_free(registered[5]);registered[5]=NULL;}
void esp_audio_dec_unregister_all(void) {
    for(unsigned i=0;i<5;++i){tracked_free(registered[i]);registered[i]=NULL;}
}

#define malloc tracked_malloc
#define calloc tracked_calloc
#define free tracked_free
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
#define adaptive_input_attach_control real_adaptive_input_attach_control
#include "adaptive-production.inc"
#undef adaptive_input_attach_control
bool adaptive_input_attach_control(adaptive_input_t *input,void *storage,size_t capacity) {
    check_not_ready();return !fail_control && real_adaptive_input_attach_control(input,storage,capacity);
}
#endif
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
static uint8_t s_start_control[256];
static bool s_start_control_attached;
#endif
#include "production.inc"
#undef malloc
#undef calloc
#undef free

#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
bool __wrap_native_input_reclaim_bind(adaptive_input_t *input) {
    STARTUP_CHECK(atomic_load(&s_start_state)==AUDIO_START_READY,"bind_after_ready_commit");
    STARTUP_CHECK(!notifications && !atomic_load(&ran_tasks),"bind_before_owner_execution");
    STARTUP_CHECK(input && input==s_encoded,"bind_actual_encoded_pointer");
    STARTUP_CHECK(atomic_fetch_add(&startup_bind_attempts,1)==0,"one_startup_bind_attempt");
    bool result=__real_native_input_reclaim_bind(input);
    atomic_store(&startup_bind_accepted,result);return result;
}
static void tls_during_allocation(void) {
    if(atomic_load(&s_start_state)!=AUDIO_STARTING || foreign_pool)return;
    STARTUP_CHECK(!atomic_load(&startup_bind_attempts),"allocation_before_publication");
    unsigned before=tls_original_calls;
    adaptive_input_stats_t stats=adaptive_input_stats(s_encoded);
    STARTUP_CHECK(!__wrap_esp_mbedtls_mem_calloc(1,37),"unbound_tls_failure_stays_null");
    STARTUP_CHECK(tls_original_calls==before+1,"unbound_tls_original_once");
    adaptive_input_stats_t after=adaptive_input_stats(s_encoded);
    STARTUP_CHECK(stats.resident==after.resident && stats.released==after.released,"unbound_tls_no_reclaim");
    if(s_encoded)STARTUP_CHECK(native_input_reclaim_detach(s_encoded)==NATIVE_INPUT_RECLAIM_WRONG_OWNER,"unbound_pool_not_published");
    ++tls_allocation_probes;
}
#endif
static void assert_no_bind(void) {
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    STARTUP_CHECK(!atomic_load(&startup_bind_attempts),"failed_start_never_publishes");
#endif
}
static void check_not_ready(void) {
    // State initialization itself occurs before attempting service startup.
    if(atomic_load(&s_start_state)!=AUDIO_STARTING)return;
    unsigned generation=atomic_load(&s_generation),writes=queue_writes;
    assert(audio_service_start(&state)==ESP_ERR_INVALID_STATE);
    assert(audio_service_play("http://fixture/audio",NATIVE_CODEC_AUTO)==ESP_ERR_INVALID_STATE);
    audio_service_stop();assert(generation==atomic_load(&s_generation) && writes==queue_writes);
    assert(!audio_service_input_health().available && !atomic_load(&ran_tasks));
}
static void run_task(void *argument) {
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    STARTUP_CHECK(atomic_load(&startup_bind_attempts)==1,"owners_observe_bind_attempt");
#endif
    assert(!argument && atomic_load(&s_start_state)==AUDIO_START_READY);
    assert(s_commands && s_encoded && s_pcm && s_control_lock && s_stream_buffer && output_memory);
    atomic_fetch_add(&ran_tasks,1);
}
static void stream_task(void *argument) {run_task(argument);}
static void decoder_task(void *argument) {run_task(argument);}
static void output_task(void *argument) {run_task(argument);}
static void wait_for_tasks(void) {
    struct timespec pause={0,1000000};
    for(unsigned attempt=0;atomic_load(&ran_tasks)<3 && attempt<2000;++attempt)nanosleep(&pause,NULL);
    assert(atomic_load(&ran_tasks)==3);
}
static void assert_clean(void) {
    assert(atomic_load(&s_start_state)==AUDIO_START_OFF);
    assert(!s_state && !s_commands && !s_encoded && !s_pcm && !s_control_lock && !s_stream_buffer);
    for(unsigned i=0;i<3;++i)assert(!created_tasks[i]);
    for(unsigned i=0;i<6;++i)assert(!registered[i]);
    unsigned foreign_allocations=0;
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    if(foreign_pool)foreign_allocations=adaptive_input_stats(foreign_pool).resident+3U;
#endif
    assert(live_allocations==1U+(output_memory ? 1U : 0U)+foreign_allocations);
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    assert(!s_start_control_attached && !s_encoded_control_attached);
#endif
    unsigned generation=atomic_load(&s_generation),writes=queue_writes;
    assert(audio_service_play("http://fixture/audio",NATIVE_CODEC_AUTO)==ESP_ERR_INVALID_STATE);
    audio_service_stop();assert(generation==atomic_load(&s_generation) && writes==queue_writes);
}
static void clean_success(void) {
    wait_for_tasks();TaskHandle_t tasks[3];memcpy(tasks,created_tasks,sizeof(tasks));
    // Join every ordinary owner before detaching the non-owning registry.
    // The following production discard is test teardown, not a runtime API.
    for(unsigned i=0;i<3;++i){vTaskDelete(tasks[i]);tasks[i]=NULL;}
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    native_input_reclaim_detach_result_t detached=native_input_reclaim_detach(s_encoded);
    STARTUP_CHECK(detached==(foreign_pool?NATIVE_INPUT_RECLAIM_WRONG_OWNER:NATIVE_INPUT_RECLAIM_DETACHED),"public_detach_before_test_destroy");
#endif
    discard_pipeline_startup(tasks,true);assert_clean();
}
static void reset_case(void) {
    assert_clean();tracked_free(output_memory);output_memory=NULL;
    s_output_initialized=s_led_initialized=false;
    allocation_calls=failure_allocation=registration_calls=registration_failure=0;
    task_calls=failure_task=output_calls=led_calls=deleted_tasks=tracked_tasks=notifications=queue_writes=0;
    output_error=led_error=0;fail_control=false;atomic_store(&ran_tasks,0);
    atomic_store(&startup_warnings,0);
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    atomic_store(&startup_bind_attempts,0);atomic_store(&startup_bind_accepted,false);
#endif
    ++scenarios;
}
static void retry_success(void) {
    failure_allocation=failure_task=registration_failure=0;output_error=led_error=0;fail_control=false;
    unsigned old_output_calls=output_calls,old_led_calls=led_calls;
    bool had_output=s_output_initialized,had_led=s_led_initialized;
    task_calls=registration_calls=tracked_tasks=notifications=0;atomic_store(&ran_tasks,0);
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    atomic_store(&startup_bind_attempts,0);atomic_store(&startup_bind_accepted,false);
#endif
    assert(audio_service_start(&state)==ESP_OK);
    assert(output_calls==old_output_calls+(had_output ? 0U : 1U));
    assert(led_calls==old_led_calls+(had_led ? 0U : 1U));
    assert(tracked_tasks==3 && notifications==3);
    assert(audio_service_start(&state)==ESP_ERR_INVALID_STATE);
    assert(audio_service_play("http://fixture/audio",NATIVE_CODEC_AUTO)==ESP_OK && queue_writes);
    audio_service_stop();assert(!state.audio_pending && !strcmp(state.stream_format,"stopped"));
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    native_input_health_t health=audio_service_input_health();assert(health.available && health.leased && health.resident>=4);
#else
    assert(!audio_service_input_health().available);
#endif
    clean_success();
}
static pthread_mutex_t start_gate=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t start_changed=PTHREAD_COND_INITIALIZER;
static bool paused,release_start;
static void pause_start(void) {
    assert(!pthread_mutex_lock(&start_gate));paused=true;pthread_cond_broadcast(&start_changed);
    while(!release_start)assert(!pthread_cond_wait(&start_changed,&start_gate));
    assert(!pthread_mutex_unlock(&start_gate));
}
static void *concurrent_start(void *unused) {
    (void)unused;assert(audio_service_start(&state)==ESP_OK);return NULL;
}
int main(void) {
    native_state_init(&state);
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    STARTUP_CHECK(heap_caps_register_failed_alloc_callback(observe_health_failure)==ESP_OK,"install_existing_health_hook");
#endif
    assert(audio_service_start(NULL)==ESP_ERR_INVALID_ARG);
    native_state_t bad={0};assert(audio_service_start(&bad)==ESP_ERR_INVALID_ARG);
    // The initial service is OFF but s_state has never been assigned.
    assert_clean();reset_case();
    assert(audio_service_start(&state)==ESP_OK);
    unsigned total_allocations=allocation_calls,total_registrations=registration_calls;
    clean_success();
    for(unsigned index=1;index<=total_allocations;++index) {
        reset_case();failure_allocation=index;
        int result=audio_service_start(&state);
        if(result==ESP_OK) {
            // Adaptive storage above its four-slot minimum is best effort.
            clean_success();
        } else {
            assert(result==ESP_ERR_NO_MEM && !atomic_load(&ran_tasks) && !notifications && !tracked_tasks);
            assert_no_bind();assert_clean();
        }
        retry_success();
    }
    for(unsigned index=1;index<=total_registrations;++index) {
        reset_case();registration_failure=index;
        assert(audio_service_start(&state)==ESP_FAIL && registration_calls==index);
        assert(!atomic_load(&ran_tasks) && !notifications && !tracked_tasks);assert_no_bind();assert_clean();retry_success();
    }
    for(unsigned index=1;index<=3;++index) {
        reset_case();failure_task=index;
        assert(audio_service_start(&state)==ESP_ERR_NO_MEM && task_calls==index && deleted_tasks==index-1);
        assert(!atomic_load(&ran_tasks) && !notifications && !tracked_tasks);assert_no_bind();assert_clean();retry_success();
    }
    reset_case();output_error=ESP_FAIL;
    assert(audio_service_start(&state)==ESP_FAIL && deleted_tasks==3);
    assert_no_bind();assert_clean();retry_success();
    reset_case();led_error=ESP_FAIL;
    assert(audio_service_start(&state)==ESP_FAIL && s_output_initialized && output_memory && !s_led_initialized);
    assert_no_bind();assert_clean();retry_success();
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    reset_case();fail_control=true;
    assert(audio_service_start(&state)==ESP_ERR_NO_MEM);assert_no_bind();assert_clean();retry_success();
#endif
    reset_case();allocation_hook=pause_start;
    pthread_t thread;assert(!pthread_create(&thread,NULL,concurrent_start,NULL));
    assert(!pthread_mutex_lock(&start_gate));
    while(!paused)assert(!pthread_cond_wait(&start_changed,&start_gate));
    check_not_ready();release_start=true;pthread_cond_broadcast(&start_changed);
    assert(!pthread_mutex_unlock(&start_gate) && !pthread_join(thread,NULL));clean_success();
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    // A pre-existing unrelated owner makes the optional startup bind fail.
    // It must retain the foreign pool and leave READY/tasks/playback intact.
    reset_case();foreign_pool=adaptive_input_create(8192,2048,1024);
    STARTUP_CHECK(foreign_pool && __real_native_input_reclaim_bind(foreign_pool),"bind_foreign_owner");
    adaptive_input_stats_t foreign_before=adaptive_input_stats(foreign_pool);
    STARTUP_CHECK(audio_service_start(&state)==ESP_OK,"bind_collision_keeps_success");
    wait_for_tasks();
    STARTUP_CHECK(atomic_load(&s_start_state)==AUDIO_START_READY && notifications==3 && tracked_tasks==3 &&
        !deleted_tasks && atomic_load(&startup_bind_attempts)==1 && !atomic_load(&startup_bind_accepted),"collision_no_ready_rollback");
    STARTUP_CHECK(atomic_load(&startup_warnings)==1,"collision_warning_only");
    adaptive_input_stats_t foreign_after=adaptive_input_stats(foreign_pool);
    STARTUP_CHECK(foreign_after.resident==foreign_before.resident && foreign_after.released==foreign_before.released,"collision_keeps_foreign_pool");
    STARTUP_CHECK(audio_service_play("http://fixture/after-bind-collision",NATIVE_CODEC_AUTO)==ESP_OK && queue_writes,"collision_playback_still_accepted");
    adaptive_input_stats_t own_before=adaptive_input_stats(s_encoded);
    STARTUP_CHECK(!__wrap_esp_mbedtls_mem_calloc(1,37),"bound_foreign_tls_failure");
    foreign_after=adaptive_input_stats(foreign_pool);
    adaptive_input_stats_t own_after=adaptive_input_stats(s_encoded);
    STARTUP_CHECK(foreign_after.resident==foreign_after.minimum && foreign_after.released>foreign_before.released &&
        own_after.resident==own_before.resident && own_after.released==own_before.released,"collision_preserves_foreign_binding");
    clean_success();
    STARTUP_CHECK(native_input_reclaim_detach(foreign_pool)==NATIVE_INPUT_RECLAIM_DETACHED,"detach_foreign_after_owners_quiesce");
    adaptive_input_destroy(foreign_pool);foreign_pool=NULL;
    STARTUP_CHECK(health_hook==observe_health_failure && health_hook_registrations==1 && health_hook_calls==tls_original_calls && tls_allocation_probes,"global_health_hook_preserved_at_exit");
    printf("reclaim_probes=%u original_tls_calls=%u health_callback_calls=%u\n",tls_allocation_probes,tls_original_calls,health_hook_calls);
#endif
    tracked_free(output_memory);output_memory=NULL;
    vSemaphoreDelete(state.lock);assert(!live_allocations);
    puts("PASS CYD startup: every allocation/task/registration failure, rollback/retry, notification gate, concurrent/reentrant controls, permanent output init retained; ASan/UBSan");
    printf("scenarios=%u allocation_failure_points=%u registration_failure_points=%u\n",scenarios,total_allocations,total_registrations);
    return 0;
}
