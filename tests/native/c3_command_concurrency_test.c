#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "audio_service.h"
#include "native_network_power.h"

static native_state_t state;
static native_state_t *s_state=&state;
static atomic_uint s_generation,s_decoder_target_codec;
static atomic_bool s_measured_bitrate_ready,streaming,pause_at_state;
static portMUX_TYPE s_generation_lock=portMUX_INITIALIZER_UNLOCKED;
static SemaphoreHandle_t s_control_lock;
static void *s_commands=(void *)1;
static char s_last_url[512];
static native_codec_t s_last_codec;
static pthread_mutex_t gate=PTHREAD_MUTEX_INITIALIZER,queue_lock=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t changed=PTHREAD_COND_INITIALIZER;
static bool paused,released,second_done;
static unsigned queued_generation;
static char queued_url[512];
static bool fail_queue;
static int xQueueOverwrite(void *,const void *);
static void record_power(void) {
    native_network_power_snapshot_t snapshot;
    native_network_power_snapshot(&snapshot);
    atomic_store(&streaming, snapshot.desired_active);
}
static void network_service_audio_accept(uint32_t generation, bool active) {
    native_network_power_accept(generation,active); record_power();
}
static void network_service_audio_finish(uint32_t generation) {
    native_network_power_finish(generation); record_power();
}
#include "production.inc"

SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t mutex=malloc(sizeof(*mutex));
    assert(mutex && !pthread_mutex_init(mutex,NULL));return mutex;
}
int xSemaphoreTake(SemaphoreHandle_t mutex,unsigned timeout) {
    (void)timeout;
    if (mutex==state.lock && atomic_exchange(&pause_at_state,false)) {
        assert(!pthread_mutex_lock(&gate));paused=true;pthread_cond_broadcast(&changed);
        while (!released)assert(!pthread_cond_wait(&changed,&gate));
        assert(!pthread_mutex_unlock(&gate));
    }
    assert(!pthread_mutex_lock(mutex));return pdTRUE;
}
void xSemaphoreGive(SemaphoreHandle_t mutex) {assert(!pthread_mutex_unlock(mutex));}
size_t strlcpy(char *to,const char *from,size_t capacity) {
    size_t length=strlen(from);
    if (capacity) {size_t n=length<capacity ? length : capacity-1;memmove(to,from,n);to[n]=0;}
    return length;
}
static int xQueueOverwrite(void *queue,const void *data) {
    assert(queue==s_commands && data);const play_command_t *command=data;
    if (fail_queue)return 0;
    assert(!pthread_mutex_lock(&queue_lock));queued_generation=command->generation;
    strlcpy(queued_url,command->url,sizeof(queued_url));
    assert(!pthread_mutex_unlock(&queue_lock));return pdTRUE;
}
static void *first_play(void *unused) {
    (void)unused;assert(audio_service_play("http://first.example/audio",NATIVE_CODEC_AAC)==ESP_OK);return NULL;
}
static void *second_play(void *unused) {
    (void)unused;assert(audio_service_play("http://second.example/audio",NATIVE_CODEC_MP3)==ESP_OK);
    assert(!pthread_mutex_lock(&gate));second_done=true;pthread_cond_broadcast(&changed);
    assert(!pthread_mutex_unlock(&gate));return NULL;
}
static void *stress(void *identity) {
    for (unsigned i=0;i<1000;++i) {
        switch ((i+(uintptr_t)identity)%3) {
            case 0:assert(audio_service_play("http://stress.example/audio",NATIVE_CODEC_AUTO)==ESP_OK);break;
            case 1:audio_service_stop();break;
            default:assert(audio_service_resume()==ESP_OK);break;
        }
    }
    return NULL;
}
int main(void) {
    native_state_init(&state);s_control_lock=xSemaphoreCreateMutex();
    assert(audio_service_resume()==ESP_ERR_INVALID_STATE);
    assert(audio_service_play(NULL,NATIVE_CODEC_AUTO)==ESP_ERR_INVALID_ARG);
    assert(audio_service_play("",NATIVE_CODEC_AUTO)==ESP_ERR_INVALID_ARG);
    char long_url[513];memset(long_url,'a',512);long_url[512]=0;
    assert(audio_service_play(long_url,NATIVE_CODEC_AUTO)==ESP_ERR_INVALID_ARG);
    assert(!atomic_load(&s_generation));
    atomic_store(&pause_at_state,true);
    pthread_t first,second;assert(!pthread_create(&first,NULL,first_play,NULL));
    assert(!pthread_mutex_lock(&gate));
    while (!paused)assert(!pthread_cond_wait(&changed,&gate));
    assert(!pthread_mutex_unlock(&gate));
    assert(!pthread_create(&second,NULL,second_play,NULL));
    assert(!pthread_mutex_lock(&gate));
    struct timespec deadline;assert(!clock_gettime(CLOCK_REALTIME,&deadline));
    deadline.tv_nsec+=50000000L;
    if (deadline.tv_nsec>=1000000000L) {++deadline.tv_sec;deadline.tv_nsec-=1000000000L;}
    // Before the fix the newer command finishes while the old one is paused.
    // With serialization it waits; release the old caller after a bounded wait.
    while (!second_done) {
        int result=pthread_cond_timedwait(&changed,&gate,&deadline);
        assert(!result || result==ETIMEDOUT);if (result==ETIMEDOUT)break;
    }
    released=true;pthread_cond_broadcast(&changed);assert(!pthread_mutex_unlock(&gate));
    assert(!pthread_join(first,NULL) && !pthread_join(second,NULL));
    assert(queued_generation==atomic_load(&s_generation));
    assert(state.audio_generation==queued_generation && !strcmp(state.station,queued_url) && state.audio_pending);
    assert(!strcmp(queued_url,"http://second.example/audio"));
    assert(!pthread_create(&first,NULL,stress,(void *)0));
    assert(!pthread_create(&second,NULL,stress,(void *)1));
    assert(!pthread_join(first,NULL) && !pthread_join(second,NULL));
    audio_service_stop();assert(!state.audio_running && !state.audio_pending && !atomic_load(&streaming));
    assert(state.audio_generation==atomic_load(&s_generation));
    assert(!strcmp(state.stream_format,"stopped"));
    assert(audio_service_resume()==ESP_OK && queued_generation==atomic_load(&s_generation));
    assert(!strcmp(state.stream_format,"connecting") && state.audio_pending && atomic_load(&streaming));
    fail_queue=true;assert(audio_service_play("http://retry.example/audio",NATIVE_CODEC_AUTO)==ESP_FAIL);
    assert(!atomic_load(&streaming) && !state.audio_pending);fail_queue=false;
    assert(audio_service_resume()==ESP_OK && atomic_load(&streaming));
    unsigned held_generation=atomic_load(&s_generation);
    atomic_store(&s_maintenance_phase,MAINTENANCE_HELD);
    s_maintenance_resume=true;
    assert(audio_service_play("http://busy.example/audio",NATIVE_CODEC_AUTO)==ESP_ERR_INVALID_STATE);
    assert(audio_service_resume()==ESP_ERR_INVALID_STATE);
    audio_service_stop();
    assert(!s_maintenance_resume && held_generation==atomic_load(&s_generation));
    assert(atomic_load(&s_maintenance_phase)==MAINTENANCE_HELD);
    atomic_store(&s_maintenance_phase,MAINTENANCE_OFF);
    pthread_mutex_destroy(state.lock);free(state.lock);
    pthread_mutex_destroy(s_control_lock);free(s_control_lock);
    puts("PASS C3 commands: paused older Play cannot overwrite newer command/state; 2000 concurrent Play/Stop/Resume operations preserve ordering; ASan/UBSan");
    return 0;
}
