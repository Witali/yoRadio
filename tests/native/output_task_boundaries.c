#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include <stdatomic.h>
typedef int esp_err_t;
enum { ESP_OK, ESP_FAIL };
#define pdMS_TO_TICKS(x) (x)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
/* PRODUCTION_OUTPUT_HEADER */
/* PRODUCTION_PACKET_TYPE */
static atomic_uint s_generation;
static void *s_pcm=(void *)1;
static jmp_buf done;
static char events[128];
static size_t event_count;
static unsigned returned[8], action_count, next_action, completed, cases;
static bool change_on_write, change_on_flush;
static int flush_result, configure_result;
static pcm_packet_t *packets[8];
typedef struct { int packet; bool change; uint32_t generation; } action_t;
static action_t actions[8];
static void event(char c) {assert(event_count+1<sizeof(events));events[event_count++]=c;events[event_count]=0;}
static void *receive(void *ring,size_t *size,unsigned wait) {
    assert(ring==s_pcm && wait==5);
    if(next_action==action_count) longjmp(done,1);
    action_t a=actions[next_action++];
    if(a.change) atomic_store(&s_generation,a.generation);
    *size=sizeof(pcm_packet_t)+4;
    return a.packet<0?NULL:packets[a.packet];
}
#define pipeline_receive(ring,size,wait,ignored) receive(ring,size,wait)
static void vRingbufferReturnItem(void *ring,void *packet) {
    assert(ring==s_pcm);bool found=false;
    for(unsigned i=0;i<8;++i) if(packets[i]==packet) {assert(!returned[i]++);found=true;break;}
    assert(found);event('R');
}
static const char *audio_completion_status(unsigned reason) {(void)reason;return "Finished";}
static void state_set_audio(uint32_t generation,bool playing,const char *status) {
    assert(!playing && !strcmp(status,"Finished"));event('E');
    if(generation==atomic_load(&s_generation)) ++completed;
}
/* PRODUCTION_FINISH */
/* PRODUCTION_RELEASE */
void native_audio_output_discard_pcm(void) {event('D');}
esp_err_t native_audio_output_flush_pcm(void) {
    event('F');if(change_on_flush) atomic_fetch_add(&s_generation,1);return flush_result;
}
esp_err_t native_audio_output_configure(uint32_t rate) {assert(rate==44100 || rate==48000);event('C');return configure_result;}
void native_audio_output_idle(void) {event('I');}
const char *native_audio_output_name(void) {return "test";}
esp_err_t native_audio_output_write_pcm(uint8_t *data,size_t bytes,uint8_t bits,uint8_t channels) {
    assert(data && bytes==4 && bits==16 && channels==2);event('W');
    if(change_on_write) {change_on_write=false;atomic_fetch_add(&s_generation,1);}
    return ESP_OK;
}
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
esp_err_t native_audio_output_submit_pcm(native_audio_pcm_lease_t *lease,uint8_t *data,
    size_t bytes,uint8_t bits,uint8_t channels,void (*release)(native_audio_pcm_lease_t *)) {
    int result=native_audio_output_write_pcm(data,bytes,bits,channels);release(lease);return result;
}
#endif
/* PRODUCTION_OUTPUT_TASK */
static void reset(uint32_t generation) {
    atomic_store(&s_generation,generation);event_count=action_count=next_action=completed=0;
    memset(events,0,sizeof(events));memset(returned,0,sizeof(returned));
    change_on_write=change_on_flush=false;flush_result=configure_result=ESP_OK;
    for(unsigned i=0;i<8;++i) {free(packets[i]);packets[i]=NULL;}
}
static void packet(unsigned id,uint32_t gen,unsigned rate,bool eof) {
    packets[id]=calloc(1,sizeof(pcm_packet_t)+4);assert(packets[id]);
    *packets[id]=(pcm_packet_t){.generation=gen,.sample_rate=rate,.bits_per_sample=16,
                               .channels=2,.data_size=4,.end_of_stream=eof};
}
static void enqueue(int id,bool change,uint32_t gen) {actions[action_count++]=(action_t){id,change,gen};}
static void check(const char *expected,unsigned expected_completed) {
    if(!setjmp(done)) output_task(NULL);
    if(strcmp(events,expected)) fprintf(stderr,"case=%u expected=%s actual=%s\n",cases,expected,events);
    assert(!strcmp(events,expected) && completed==expected_completed);
    for(unsigned i=0;i<action_count;++i) if(actions[i].packet>=0) assert(returned[actions[i].packet]==1);
    ++cases;
}
int main(void) {
    reset(7);packet(0,7,48000,false);packet(1,7,48000,true);
    enqueue(0,false,0);enqueue(1,false,0);check("CWRFER",1);

    reset(7);packet(0,7,48000,false);packet(1,8,48000,false);packet(2,8,48000,true);
    enqueue(0,false,0);enqueue(1,true,8);enqueue(2,false,0);check("CWRDWRFER",1);

    reset(7);packet(0,7,48000,false);packet(1,8,48000,false);
    enqueue(0,false,0);enqueue(-1,true,8);enqueue(1,false,0);check("CWRIDWR",0);

    reset(7);packet(0,7,48000,true);enqueue(0,true,8);check("DR",0);

    reset(7);packet(0,7,48000,false);packet(1,7,44100,false);
    enqueue(0,false,0);enqueue(1,false,0);check("CWRCWR",0);

    reset(7);packet(0,7,48000,false);packet(1,7,48000,true);
    flush_result=ESP_FAIL;enqueue(0,false,0);enqueue(1,false,0);check("CWRFER",1);

    reset(7);packet(0,7,48000,false);packet(1,8,48000,false);change_on_write=true;
    enqueue(0,false,0);enqueue(1,false,0);check("CWRDWR",0);

    reset(7);packet(0,7,48000,true);change_on_flush=true;
    enqueue(0,false,0);check("FERD",0);

    reset(UINT32_MAX);packet(0,0,48000,false);enqueue(0,true,0);check("DCWR",0);

    reset(7);packet(0,7,48000,false);configure_result=ESP_FAIL;
    enqueue(0,false,0);check("CR",0);
    reset(0);printf("PASS actual output_task boundary cases=%u\n",cases);
}
