#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "audio_service.h"
#include "native_network_power.h"

static native_state_t state, *s_state=&state;
static atomic_uint s_generation,s_decoder_target_codec,s_failed_generation;
static atomic_bool s_measured_bitrate_ready;
static portMUX_TYPE s_generation_lock=portMUX_INITIALIZER_UNLOCKED;
static SemaphoreHandle_t s_control_lock;
static void *s_commands=(void *)1;
static char s_last_url[512];
static native_codec_t s_last_codec;
static unsigned queued_generation,groups;
static bool fail_queue,finish_in_queue;
static pthread_mutex_t gate=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t changed=PTHREAD_COND_INITIALIZER;
static bool finish_blocked,finish_entered,finish_allowed;
static uint32_t delayed_generation;
static void network_service_audio_accept(uint32_t generation,bool active){native_network_power_accept(generation,active);}
static void network_service_audio_finish(uint32_t generation){
    assert(!pthread_mutex_lock(&gate));
    if(finish_blocked&&generation==delayed_generation){finish_entered=true;pthread_cond_broadcast(&changed);while(!finish_allowed)assert(!pthread_cond_wait(&changed,&gate));}
    assert(!pthread_mutex_unlock(&gate));native_network_power_finish(generation);
}
static int xQueueOverwrite(void *,const void *);
#include "controls-types.inc"
#ifdef POWER_CYD
static atomic_uint s_start_state=AUDIO_START_READY;
#endif
#include "controls.inc"
static int xQueueOverwrite(void *queue,const void *data){
    assert(queue==s_commands&&data);const play_command_t *command=data;
    native_network_power_snapshot_t power;native_network_power_snapshot(&power);
    assert(power.generation==command->generation&&power.desired_active);
    if(fail_queue)return 0;
    queued_generation=command->generation;
    if(finish_in_queue)network_service_audio_finish(command->generation);
    return pdTRUE;
}
size_t strlcpy(char *out,const char *text,size_t capacity){size_t size=strlen(text);if(capacity){size_t n=size<capacity-1?size:capacity-1;memmove(out,text,n);out[n]=0;}return size;}
static void expect(bool active){native_network_power_snapshot_t power;native_network_power_snapshot(&power);assert(power.generation==atomic_load(&s_generation)&&power.desired_active==active);++groups;}
static void *old_finish(void *unused){(void)unused;network_service_audio_finish(delayed_generation);return NULL;}
int main(void){
    native_state_init(&state);s_control_lock=xSemaphoreCreateMutex();
    assert(audio_service_play(NULL,NATIVE_CODEC_AUTO)==ESP_ERR_INVALID_ARG);
    assert(audio_service_play("http://one.invalid/audio",NATIVE_CODEC_AAC)==ESP_OK);expect(true);
    delayed_generation=atomic_load(&s_generation);finish_blocked=true;
    pthread_t thread;assert(!pthread_create(&thread,NULL,old_finish,NULL));
    assert(!pthread_mutex_lock(&gate));while(!finish_entered)assert(!pthread_cond_wait(&changed,&gate));assert(!pthread_mutex_unlock(&gate));
    assert(audio_service_play("http://two.invalid/audio",NATIVE_CODEC_MP3)==ESP_OK);expect(true);
    assert(!pthread_mutex_lock(&gate));finish_allowed=true;pthread_cond_broadcast(&changed);assert(!pthread_mutex_unlock(&gate));
    assert(!pthread_join(thread,NULL));finish_blocked=false;expect(true);
    uint32_t playing=atomic_load(&s_generation);audio_service_stop();expect(false);
    native_network_power_receive(playing);expect(false);
#ifndef POWER_CYD
    assert(audio_service_resume()==ESP_OK);expect(true);
#endif
    fail_queue=true;assert(audio_service_play("http://fail.invalid/audio",NATIVE_CODEC_AUTO)==ESP_FAIL);expect(false);fail_queue=false;
    finish_in_queue=true;assert(audio_service_play("http://short.invalid/audio",NATIVE_CODEC_AAC)==ESP_OK);expect(false);finish_in_queue=false;
    assert(queued_generation==atomic_load(&s_generation));
    assert(audio_service_play("http://next.invalid/audio",NATIVE_CODEC_AAC)==ESP_OK);expect(true);
    audio_service_stop();expect(false);
    pthread_mutex_destroy(state.lock);free(state.lock);pthread_mutex_destroy(s_control_lock);free(s_control_lock);
    printf("PASS actual control/power: %u groups; accept before queue, immediate EOF, stale finish barrier, Stop/old receive, queue failure\n",groups);
}
