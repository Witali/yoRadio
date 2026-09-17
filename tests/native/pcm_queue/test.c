#define _DEFAULT_SOURCE
#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include "audio_pcm_queue.h"
#include "freertos/task.h"

struct mock_task { pthread_t thread; pthread_mutex_t mutex; pthread_cond_t event;
    unsigned notifications; void (*entry)(void *); void *arg; };
static struct mock_task producer={.mutex=PTHREAD_MUTEX_INITIALIZER,.event=PTHREAD_COND_INITIALIZER};
static struct mock_task worker={.mutex=PTHREAD_MUTEX_INITIALIZER,.event=PTHREAD_COND_INITIALIZER};
static pthread_mutex_t critical=PTHREAD_MUTEX_INITIALIZER;
static _Thread_local struct mock_task *current;
static _Thread_local unsigned depth;
static atomic_bool finish, writing;
static atomic_uint generation, write_delay, fail_call, write_calls, progressed;
static atomic_uint worker_priority;
static int16_t actual[150000], expected[150000];
static size_t actual_count, expected_count;
void mock_enter(void) { assert(!depth);pthread_mutex_lock(&critical);++depth; }
void mock_exit(void) { assert(depth==1);--depth;pthread_mutex_unlock(&critical); }
static void *entry(void *p) { current=p;current->entry(current->arg);return NULL; }
int xTaskCreate(void (*fn)(void *),const char *name,unsigned stack,void *arg,
                unsigned priority,TaskHandle_t *task) {
    assert(!YORADIO_ESP8266_OPUS_PCM_APP_TASK); /* no hidden extra task */
    assert(!strcmp(name,"pcm-output") && stack==AUDIO_PCM_QUEUE_STACK_BYTES && priority==6);
    worker.entry=fn;worker.arg=arg;*task=&worker;
    assert(!pthread_create(&worker.thread,NULL,entry,&worker));return pdPASS;
}
TaskHandle_t xTaskGetCurrentTaskHandle(void) { return current?current:&producer; }
unsigned uxTaskPriorityGet(TaskHandle_t task) { assert(task==&worker);return worker_priority; }
void vTaskPrioritySet(TaskHandle_t task,unsigned priority) {
    assert(!depth && task==&worker && (priority==2 || priority==6));worker_priority=priority;
}
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
static void app_pump(void *unused) {
    (void)unused;
    for (;;) {
        audio_pcm_queue_poll();
        if (!audio_pcm_queue_pending()) ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
    }
}
#endif
void xTaskNotifyGive(TaskHandle_t task) {
    assert(!depth && task);pthread_mutex_lock(&task->mutex);
    ++task->notifications;pthread_cond_signal(&task->event);pthread_mutex_unlock(&task->mutex);
}
uint32_t ulTaskNotifyTake(int clear,TickType_t ticks) {
    assert(!depth && clear);struct mock_task *task=xTaskGetCurrentTaskHandle();
    pthread_mutex_lock(&task->mutex);
    while(!task->notifications && !finish) {
        if(ticks==portMAX_DELAY)pthread_cond_wait(&task->event,&task->mutex);
        else {
            struct timespec t;clock_gettime(CLOCK_REALTIME,&t);t.tv_nsec+=(long)ticks*1000000L;
            t.tv_sec+=t.tv_nsec/1000000000L;t.tv_nsec%=1000000000L;
            if(pthread_cond_timedwait(&task->event,&task->mutex,&t))break;
        }
    }
    if(finish && task==&worker){pthread_mutex_unlock(&task->mutex);pthread_exit(NULL);}
    unsigned n=task->notifications;task->notifications=0;
    pthread_mutex_unlock(&task->mutex);return n;
}
unsigned uxTaskGetStackHighWaterMark(TaskHandle_t task) { assert(task==&worker);return 777; }
void vTaskDelete(TaskHandle_t task) {
    assert(task==&worker && !writing);finish=true;xTaskNotifyGive(task);
    assert(!pthread_join(worker.thread,NULL));
}
int64_t esp_timer_get_time(void) {
    struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000000LL+t.tv_nsec/1000;
}
static bool valid(uint32_t value) { return generation==value; }
static void progress(uint32_t value,size_t count) { if(valid(value))progressed+=count; }
esp_err_t native_audio_output_write(int16_t *pcm,size_t count,uint32_t rate,uint8_t channels) {
    assert(!depth && rate==48000 && channels==1 && count && count<=512);
    writing=true;unsigned call=++write_calls;usleep(write_delay);
    if(call==fail_call){writing=false;return ESP_FAIL;}
    assert(actual_count+count<sizeof(actual)/sizeof(*actual));
    for(size_t i=0;i<count;++i)actual[actual_count++]=pcm[i];
    /* Simulate normalizer/gain modifying a buffer while it is consumer-owned. */
    memset(pcm,0xa5,count*sizeof(*pcm));writing=false;return ESP_OK;
}
static int16_t *begin(unsigned gen) {
    generation=gen;int16_t *pool=malloc(AUDIO_PCM_QUEUE_SLOTS*AUDIO_PCM_QUEUE_FRAMES*sizeof(int16_t));assert(pool);
    assert(audio_pcm_queue_begin(pool,AUDIO_PCM_QUEUE_SLOTS*AUDIO_PCM_QUEUE_FRAMES,gen)==ESP_OK);return pool;
}
static void submit(unsigned frame,unsigned skip) {
    int16_t *pcm=NULL;assert(audio_pcm_queue_acquire(NULL,&pcm,960)==0 && pcm);
    for(unsigned i=0;i<960;++i)pcm[i]=(int16_t)((frame*991U+i*17U)%65536U);
    for(unsigned i=skip;i<960;++i)expected[expected_count++]=pcm[i];
    assert(audio_pcm_queue_submit(pcm+skip,960-skip));
    assert(!audio_pcm_queue_submit(pcm+skip,960-skip)); /* duplicate handoff */
}
int main(void) {
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    current=&worker;worker_priority=2;
#endif
    assert(audio_pcm_queue_init(valid,progress)==ESP_OK);
    assert(audio_pcm_queue_init(valid,progress)==ESP_ERR_INVALID_STATE);
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    current=&producer;
    assert(!audio_pcm_queue_poll()); /* only the registered app may read */
    worker.entry=app_pump;worker.arg=NULL;
    assert(!pthread_create(&worker.thread,NULL,entry,&worker));
#endif
    assert(audio_pcm_queue_begin(NULL,1920,1)==ESP_ERR_INVALID_ARG);
    write_delay=100;int16_t *pool=begin(1);
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    assert(worker_priority==6);
    audio_pcm_queue_record_service(100,10); /* no PCM yet: startup not measured */
    audio_pcm_queue_health_t empty;audio_pcm_queue_health(&empty);
    assert(!empty.service_calls && !empty.service_us && !empty.service_misses);
#endif
    assert(audio_pcm_queue_begin(pool,AUDIO_PCM_QUEUE_SLOTS*AUDIO_PCM_QUEUE_FRAMES,1)==ESP_ERR_INVALID_STATE);
    int16_t *pcm=NULL;assert(audio_pcm_queue_acquire(NULL,&pcm,961)==-108);
    assert(audio_pcm_queue_acquire(NULL,&pcm,960)==0);
    assert(!audio_pcm_queue_submit(pcm+950,20));audio_pcm_queue_release(NULL,pcm);
    for(unsigned i=0;i<120;++i)submit(i,i%7==0?120:0);
    audio_pcm_queue_drain();audio_pcm_queue_health_t h;audio_pcm_queue_health(&h);
    assert(h.submitted_frames==expected_count && h.output_frames==expected_count);
    assert(h.stack_free==777 && !h.ready_frames && !h.error);
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    audio_pcm_queue_record_service(7,2);audio_pcm_queue_record_service(11,3);
    audio_pcm_queue_health(&h);
    assert(h.service_calls==2 && h.service_us==18 && h.service_max_us==11 && h.service_misses==5);
#endif
    audio_pcm_queue_stop();assert(!writing);free(pool);
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    assert(worker_priority==2);
    audio_pcm_queue_record_service(100,10);audio_pcm_queue_health(&h);
    assert(h.service_calls==2 && h.service_us==18 && h.service_misses==5);
#endif
    assert(actual_count==expected_count && !memcmp(actual,expected,actual_count*sizeof(*actual)));
    assert(progressed==actual_count);assert(audio_pcm_queue_acquire(NULL,&pcm,960)==-108);
    /* Stop during an in-flight consumer read; freeing the pool must be safe. */
    for(unsigned i=0;i<25;++i) {
        write_delay=10000;pool=begin(10+i);submit(i,0);
        for(unsigned n=0;!writing && n<2000;++n)usleep(1000);
        assert(writing);generation=1000;
        audio_pcm_queue_stop();assert(!writing);
        memset(pool,0xcc,AUDIO_PCM_QUEUE_SLOTS*AUDIO_PCM_QUEUE_FRAMES*sizeof(int16_t));free(pool);
    }
    /* A physical-output error returns ownership, cancels producers and permits reuse. */
    write_delay=100;pool=begin(1001);fail_call=write_calls+1;submit(3,0);
    audio_pcm_queue_drain();audio_pcm_queue_health(&h);assert(h.error==(uint32_t)ESP_FAIL);
    assert(audio_pcm_queue_acquire(NULL,&pcm,960)==-108);
    audio_pcm_queue_stop();free(pool);fail_call=0;
    pool=begin(1002);submit(4,120);audio_pcm_queue_drain();audio_pcm_queue_health(&h);
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    assert(!h.service_calls && !h.service_us && !h.service_max_us && !h.service_misses);
#endif
    assert(!h.error && h.output_frames==840);audio_pcm_queue_stop();free(pool);
    audio_pcm_queue_deinit();audio_pcm_queue_deinit();
#if YORADIO_ESP8266_OPUS_PCM_APP_TASK
    assert(!finish); /* deinit must never delete the existing app task */
    vTaskDelete(&worker);
#endif
    puts("PCM queue PASS: exact order, bounded slots, trim, backpressure, 25 in-flight stops, error/reuse; no ISR work");
    return 0;
}
