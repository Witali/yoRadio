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




typedef struct {
    bool available;
    uint32_t completion_queue_drops;
    uint32_t write_errors;
} native_audio_output_health_t;

// Lifetime uint32 counters (modulo 2^32), read as aligned words on C3.
// Completion-queue drops indicate delayed service, not an acoustic gap count.
// Startup, idle and Stop may contribute: compare only sustained-play windows.
// The experimental direct-DMA backend currently reports unavailable.
native_audio_output_health_t native_audio_output_health(void);

#if defined(CONFIG_YORADIO_PIPELINE_PROFILE) || defined(CONFIG_YORADIO_STAGED_DMA_PROFILE)
// Lifetime modulo-2^32 counter; one ISR writer, aligned word read on C3.
// Queue overrun means a completion notification was discarded before reuse.
uint32_t native_audio_output_dma_overruns(void);
#endif

#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
// Embedded in the PCM queue item. The output task owns the item until release;
// neither the decoder nor the DMA ISR may modify it during this interval.
typedef struct native_audio_pcm_lease native_audio_pcm_lease_t;
struct native_audio_pcm_lease {
    native_audio_pcm_lease_t *next;
    void (*release)(native_audio_pcm_lease_t *);
    const uint8_t *data;
    size_t frame_bytes, output_frames;
    uint32_t left_gain, right_gain;
    uint16_t peak;
    uint8_t channels;
    bool current_valid;
    int16_t left, right;
};
esp_err_t native_audio_output_submit_pcm(native_audio_pcm_lease_t *lease,
    uint8_t *data, size_t size, uint8_t bits_per_sample, uint8_t channels,
    void (*release)(native_audio_pcm_lease_t *));
#endif

// Owned by the output task. Flush submits a zero-padded final DMA block; it
// does not wait for the hardware to play it. Discard drops software PCM
// and resampler history on Stop/new stream without draining old samples.
esp_err_t native_audio_output_flush_pcm(void);
void native_audio_output_discard_pcm(void);

esp_err_t native_audio_output_init(void);
esp_err_t native_audio_output_configure(uint32_t input_sample_rate);
esp_err_t native_audio_output_write_pcm(uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels);
void native_audio_output_set_volume(uint8_t volume);
uint8_t native_audio_output_get_volume(void);
void native_audio_output_set_balance(int8_t balance);
int8_t native_audio_output_get_balance(void);
void native_audio_output_request_normalizer_reset(void);
void native_audio_output_idle(void);
esp_err_t native_audio_output_suspend(void);
const char *native_audio_output_name(void);



#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC

// C3 only: aligned single-word stores from one writer per checkpoint. The
// ISR records observations, not FreeRTOS blocked/ready state. A wait flag
// stays set if a queue wakes the task before it is scheduled again.
enum {
    AUDIO_PROBE_OUTPUT_WAIT = 1U,
    AUDIO_PROBE_DECODER_WAIT = 2U,
    AUDIO_PROBE_STREAM_READ = 4U,
    AUDIO_PROBE_PHASE_COUNT = 8U,
    AUDIO_PROBE_EVENTS = 16U,
};
typedef struct {
    uint32_t sequence, timestamp_us, phases;
    uint32_t output_age, pcm_age, input_age, network_age;
} audio_pipeline_probe_event_t;
typedef struct {
    uint32_t output_wait, decoder_wait, stream_read;
    uint32_t output_us, pcm_us, input_us, network_us;
    uint32_t sequence, valid_count;
    uint32_t phase_drops[AUDIO_PROBE_PHASE_COUNT];
    audio_pipeline_probe_event_t events[AUDIO_PROBE_EVENTS];
} audio_pipeline_probe_t;
extern volatile audio_pipeline_probe_t s_audio_pipeline_probe;

#define AUDIO_PROBE_FLAG(field, value) (s_audio_pipeline_probe.field = (value))
#define AUDIO_PROBE_STAMP(field) (s_audio_pipeline_probe.field = (uint32_t)esp_timer_get_time())

// Called only by the DMA overrun ISR after an IRAM system-timer read. No
// allocation, locks or logging. Unsigned microsecond ages wrap after about
// 71.58 minutes; select short sustained-play intervals, excluding idle.
// Unlike C3's CPU cycle counter, the system timer includes WFI wait time.
static inline __attribute__((always_inline)) void audio_pipeline_probe_overrun(uint32_t now_us) {
    uint32_t phases = (s_audio_pipeline_probe.output_wait ? AUDIO_PROBE_OUTPUT_WAIT : 0U) |
                      (s_audio_pipeline_probe.decoder_wait ? AUDIO_PROBE_DECODER_WAIT : 0U) |
                      (s_audio_pipeline_probe.stream_read ? AUDIO_PROBE_STREAM_READ : 0U);
    uint32_t sequence = s_audio_pipeline_probe.sequence + 1U;
    volatile audio_pipeline_probe_event_t *event =
        &s_audio_pipeline_probe.events[sequence & (AUDIO_PROBE_EVENTS - 1U)];
    ++s_audio_pipeline_probe.phase_drops[phases];
    event->sequence = sequence;
    event->timestamp_us = now_us;
    event->phases = phases;
    event->output_age = now_us - s_audio_pipeline_probe.output_us;
    event->pcm_age = now_us - s_audio_pipeline_probe.pcm_us;
    event->input_age = now_us - s_audio_pipeline_probe.input_us;
    event->network_age = now_us - s_audio_pipeline_probe.network_us;
    s_audio_pipeline_probe.sequence = sequence;
    if (s_audio_pipeline_probe.valid_count < AUDIO_PROBE_EVENTS) {
        ++s_audio_pipeline_probe.valid_count;
    }
}
_Static_assert(sizeof(audio_pipeline_probe_t) == 516U, "Bound diagnostic RAM");
_Static_assert((AUDIO_PROBE_EVENTS & (AUDIO_PROBE_EVENTS - 1U)) == 0,
               "Event capacity must be a power of two");

// Task context only. Append a bounded diagnostic object to a complete JSON
// response. Copy the volatile state with interrupts masked before calling.
static inline int audio_pipeline_probe_append(char *body, size_t capacity,
    int length, const audio_pipeline_probe_t *probe) {
    if (length < 1 || (size_t)length >= capacity || body[length - 1] != '}' ||
        probe->valid_count > AUDIO_PROBE_EVENTS) return -1;
    --length;
#define PROBE_APPEND(...) do { \
    int added = snprintf(body + length, capacity - (size_t)length, __VA_ARGS__); \
    if (added < 0 || (size_t)added >= capacity - (size_t)length) return -1; \
    length += added; \
} while (0)
    PROBE_APPEND(",\"pipeline\":{\"timer_hz\":1000000,\"sequence\":%lu,\"phase_drops\":[",
                 (unsigned long)probe->sequence);
    for (unsigned index = 0; index < AUDIO_PROBE_PHASE_COUNT; ++index) {
        PROBE_APPEND("%s%lu", index ? "," : "", (unsigned long)probe->phase_drops[index]);
    }
    PROBE_APPEND("],\"events\":[");
    for (unsigned index = 0; index < probe->valid_count; ++index) {
        uint32_t sequence = probe->sequence - probe->valid_count + 1U + index;
        const audio_pipeline_probe_event_t *event =
            &probe->events[sequence & (AUDIO_PROBE_EVENTS - 1U)];
        PROBE_APPEND("%s[%lu,%lu,%lu,%lu,%lu,%lu,%lu]", index ? "," : "",
            (unsigned long)event->sequence, (unsigned long)event->timestamp_us,
            (unsigned long)event->phases, (unsigned long)event->output_age,
            (unsigned long)event->pcm_age, (unsigned long)event->input_age,
            (unsigned long)event->network_age);
    }
    PROBE_APPEND("]}}");
#undef PROBE_APPEND
    return length;
}
#else
#define AUDIO_PROBE_FLAG(field, value) ((void)0)
#define AUDIO_PROBE_STAMP(field) ((void)0)
#endif

typedef struct {
    uint32_t generation;
    uint32_t sample_rate;
    uint8_t bits_per_sample;
    uint8_t channels;
    uint16_t data_size;
    uint32_t end_of_stream; // Keep the following PCM payload word-aligned.
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
    native_audio_pcm_lease_t lease;
#endif
    uint8_t data[];
} pcm_packet_t;
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
static void finish_pcm_stream(const pcm_packet_t *packet) {
    // native_state checks the generation under its lock: an old completion
    // cannot stop a new Play, even if that command raced this queue read.
    state_set_audio(packet->generation, false,
                    audio_completion_status(packet->end_of_stream));
}
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
static void release_pcm_lease(native_audio_pcm_lease_t *lease) {
    pcm_packet_t *packet = (pcm_packet_t *)((uint8_t *)lease - offsetof(pcm_packet_t, lease));
    vRingbufferReturnItem(s_pcm, packet);
}
#endif
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
static void output_task(void *argument) {
    (void)argument;
#ifdef CONFIG_YORADIO_DEEP_SLEEP_CLOCK
    s_output_task = xTaskGetCurrentTaskHandle();
#endif
    uint32_t sample_rate = 0;
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
    output_flow_t flow = {0};
#endif
    uint32_t generation = atomic_load(&s_generation);
    while (true) {
        uint32_t current_generation = atomic_load(&s_generation);
        if (generation != current_generation) {
            native_audio_output_discard_pcm();
            generation = current_generation;
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
            output_flow_reset(&flow, false);
#endif
        }
#ifdef CONFIG_YORADIO_DEEP_SLEEP_CLOCK
        if (atomic_exchange(&s_suspend_output, false)) {
            s_suspend_result = native_audio_output_suspend();
            xSemaphoreGive(s_output_suspended);
            if (s_suspend_result == ESP_OK) {
                ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
                // Reserve I2S again before the sleep gate admits a new Play.
                // Otherwise TLS/decoder allocations could take its DMA memory.
                s_suspend_result = native_audio_output_configure(
                    sample_rate ? sample_rate : 48000U);
                sample_rate = 0;
                xSemaphoreGive(s_output_suspended);
            }
        }
#endif
        size_t item_size = 0;
        AUDIO_PROBE_STAMP(output_us);
        AUDIO_PROBE_FLAG(output_wait, 1U);
        pcm_packet_t *packet = pipeline_receive(s_pcm, &item_size,
                                                 pdMS_TO_TICKS(5), &flow.empty);
        AUDIO_PROBE_FLAG(output_wait, 0U);
        AUDIO_PROBE_STAMP(output_us);
        if (!packet) {
            native_audio_output_idle();
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
            output_flow_report(&flow, generation);
#endif
            continue;
        }
        current_generation = atomic_load(&s_generation);
        if (generation != current_generation) {
            native_audio_output_discard_pcm();
            generation = current_generation;
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
            output_flow_reset(&flow, false);
#endif
        }
        if (packet->generation != atomic_load(&s_generation)) {
            vRingbufferReturnItem(s_pcm, packet);
            continue;
        }
        if (packet->end_of_stream) {
            esp_err_t flush_result = native_audio_output_flush_pcm();
            if (flush_result != ESP_OK) ESP_LOGW(TAG, "PCM tail flush failed: %s", esp_err_to_name(flush_result));
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
            ESP_LOGI(TAG, "PERF PCM_END: generation=%lu completion=%lu result=%d",
                     (unsigned long)packet->generation,
                     (unsigned long)packet->end_of_stream, (int)flush_result);
#endif
            finish_pcm_stream(packet);
            vRingbufferReturnItem(s_pcm, packet);
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
            output_flow_reset(&flow, false);
#endif
            continue;
        }
        if (packet->sample_rate != sample_rate) {
            esp_err_t result =
                native_audio_output_configure(packet->sample_rate);
            if (result != ESP_OK) {
                ESP_LOGE(TAG, "%s %lu Hz setup failed: %s",
                         native_audio_output_name(),
                         (unsigned long)packet->sample_rate,
                         esp_err_to_name(result));
                vRingbufferReturnItem(s_pcm, packet);
                continue;
            }
            sample_rate = packet->sample_rate;
        }
        AUDIO_PROBE_STAMP(pcm_us);
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
        if (!flow.start_us) output_flow_reset(&flow, true);
        int64_t submit_start = esp_timer_get_time();
#endif
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
        // Ownership transfers even on a write error. The final source tail is
        // retained until another packet completes a DMA block, EOF, or Stop.
        esp_err_t result = native_audio_output_submit_pcm(
            &packet->lease, packet->data, packet->data_size,
            packet->bits_per_sample, packet->channels, release_pcm_lease);
#else
        esp_err_t result = native_audio_output_write_pcm(
            packet->data, packet->data_size, packet->bits_per_sample,
            packet->channels);
        vRingbufferReturnItem(s_pcm, packet);
#endif
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
        pipeline_wait_record(&flow.submit,
            (uint32_t)(esp_timer_get_time() - submit_start), false);
        output_flow_report(&flow, generation);
#endif
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "%s write failed: %s", native_audio_output_name(),
                     esp_err_to_name(result));
        }
    }
}
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
