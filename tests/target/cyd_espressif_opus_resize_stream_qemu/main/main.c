// Fragmented public Ogg/Opus resize; production caller policy is observed first.
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_audio_simple_dec.h"
#include "psa/crypto.h"
#include "decoder_registration.h"
#include "decoder_pending_input.h"
#include "decoder_eof_input.h"
#ifdef NDEBUG
#error "The streaming resize diagnostic requires assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "Only the ESP32 LX6 target is supported"
#endif
extern const uint8_t fixture_start[] asm("_binary_fixture_ogg_start");
extern const uint8_t fixture_end[] asm("_binary_fixture_ogg_end");
static uint8_t reference_sha[32];
static uint64_t reference_bytes;
enum { DRAINED=0, DECODE_ERROR=1, INVALID_SIZE=2, NO_PROGRESS=3,
       INVALID_RESIZE=4, ALLOCATION_FAILED=5, CALL_BOUND=6 };
typedef struct {
    esp_audio_simple_dec_handle_t decoder;
    psa_hash_operation_t hash;
    decoder_pending_input_t pending;
    uint8_t *output;
    size_t capacity,consumed,pending_max;
    uint64_t pcm_bytes;
    unsigned calls,frames,feeds,coalesces,resizes,error_consumed,empty_retries;
    unsigned data_eos_calls,empty_eos_calls,outcome,chunk;
    int last_result;
    bool adapted,honor,drained,failed;
    const char *strategy;
} stream_t;
static void fail(stream_t *s,unsigned outcome) {s->outcome=outcome; s->failed=true;}
static void process(stream_t *s,uint8_t *data,uint32_t length,bool eos) {
    esp_audio_simple_dec_raw_t raw={.buffer=data,.len=length,.eos=eos};
    bool owned=false,retry=false;
    if (s->adapted && decoder_pending_input_prepare(&s->pending,data,length,&raw.buffer,&raw.len,&owned)
            !=DECODER_PENDING_INPUT_OK) {fail(s,ALLOCATION_FAILED); return;}
    while ((raw.len || raw.eos || retry) && !s->failed) {
        if (s->calls>=2000000) {fail(s,CALL_BOUND); break;}
        if (retry && !raw.len && !raw.eos) ++s->empty_retries;
        retry=false;
        uint32_t before_len=raw.len;
        esp_audio_simple_dec_out_t out={.buffer=s->output,.len=s->capacity};
        raw.consumed=0;
        if (raw.eos) {if (raw.len) ++s->data_eos_calls; else ++s->empty_eos_calls;}
        esp_audio_err_t result=esp_audio_simple_dec_process(s->decoder,&raw,&out);
        s->last_result=result; ++s->calls;
        if (!(s->calls&31U)) vTaskDelay(1);
        if (result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            printf("EOSR_RESIZE strategy=%s chunk=%u call=%u len_before=%u raw_len=%u consumed=%u decoded_size=%u needed_size=%u capacity=%u eos=%u result=%d advance_on_error=%u\n",
                   s->strategy,s->chunk,s->calls,(unsigned)before_len,(unsigned)raw.len,(unsigned)raw.consumed,
                   (unsigned)out.decoded_size,(unsigned)out.needed_size,(unsigned)s->capacity,(unsigned)raw.eos,(int)result,(unsigned)s->honor);
            assert(fflush(stdout)==0);
            ++s->resizes; s->error_consumed+=raw.consumed;
            if (raw.len!=before_len || raw.consumed>raw.len) {fail(s,INVALID_SIZE); break;}
            if (out.needed_size<=s->capacity || out.needed_size>24576) {fail(s,INVALID_RESIZE); break;}
            uint8_t *larger=realloc(s->output,out.needed_size);
            if (!larger) {fail(s,ALLOCATION_FAILED); break;}
            s->output=larger; s->capacity=out.needed_size;
            if (s->honor) {
                if (raw.consumed) raw.buffer+=raw.consumed;
                raw.len-=raw.consumed; s->consumed+=raw.consumed;
                // A parsed frame may remain after the error consumed the final
                // byte of this nonterminal fragment. Permit its empty retry.
                retry=true;
            }
            continue;
        }
        if (result!=ESP_AUDIO_ERR_OK) {
            printf("EOSR_ERROR strategy=%s chunk=%u call=%u raw_len=%u consumed=%u decoded_size=%u needed_size=%u capacity=%u eos=%u result=%d\n",
                   s->strategy,s->chunk,s->calls,(unsigned)raw.len,(unsigned)raw.consumed,(unsigned)out.decoded_size,
                   (unsigned)out.needed_size,(unsigned)s->capacity,(unsigned)raw.eos,(int)result);
            assert(fflush(stdout)==0);
            fail(s,DECODE_ERROR); break;
        }
        if (raw.len!=before_len || raw.consumed>raw.len || out.decoded_size>s->capacity) {fail(s,INVALID_SIZE); break;}
        if (raw.consumed) raw.buffer+=raw.consumed;
        raw.len-=raw.consumed; s->consumed+=raw.consumed;
        if (out.decoded_size) {
            esp_audio_simple_dec_info_t info={0};
            assert(esp_audio_simple_dec_get_info(s->decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16 && out.decoded_size%4==0);
            assert(psa_hash_update(&s->hash,out.buffer,out.decoded_size)==PSA_SUCCESS);
            s->pcm_bytes+=out.decoded_size; ++s->frames;
        }
        if (!raw.consumed && !out.decoded_size) {
            if (raw.eos) {
                if (raw.len) fail(s,NO_PROGRESS);
                else s->drained=true;
            } else if (raw.len) {
                if (!s->adapted || decoder_pending_input_retain(&s->pending,raw.buffer,raw.len,owned)
                        !=DECODER_PENDING_INPUT_OK) fail(s,ALLOCATION_FAILED);
                else {
                    ++s->coalesces;
                    if (s->pending.size>s->pending_max) s->pending_max=s->pending.size;
                }
            }
            break;
        }
        if (!raw.eos && !raw.len) break;
    }
}

static bool decode(unsigned chunk,bool adapted,bool honor,bool *consumed_on_resize) {
    assert(heap_caps_check_integrity_all(true));
    size_t before=esp_get_free_heap_size();
    stream_t s={.hash=PSA_HASH_OPERATION_INIT,.capacity=adapted?12288:24576,
        .chunk=chunk,.adapted=adapted,.honor=honor,
        .strategy=adapted?(honor?"honor_consumed":"current_unchanged"):"baseline"};
    s.output=malloc(s.capacity); assert(s.output);
    esp_audio_simple_dec_cfg_t config={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG,.use_frame_dec=false};
    assert(esp_audio_simple_dec_open(&config,&s.decoder)==ESP_AUDIO_ERR_OK && s.decoder);
    assert(psa_hash_setup(&s.hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    size_t length=(size_t)(fixture_end-fixture_start),fed=0;
    decoder_eof_input_t eof={0};
    if (!adapted) {process(&s,(uint8_t *)fixture_start,(uint32_t)length,true); fed=length; s.feeds=1;}
    else while (!s.failed && !s.drained) {
        uint32_t count=(uint32_t)(length-fed); if (count>chunk) count=chunk;
        decoder_eof_segment_t segments[2]; uint8_t previous=0;
        unsigned n=decoder_eof_input_prepare(&eof,true,(uint8_t *)fixture_start+fed,count,!count,&previous,segments);
        fed+=count; if (count) ++s.feeds;
        for (unsigned i=0;i<n && !s.failed;++i) process(&s,segments[i].data,segments[i].size,segments[i].eos);
    }
    uint8_t digest[32]; char hex[65]; size_t digest_size=0;
    assert(psa_hash_finish(&s.hash,digest,sizeof(digest),&digest_size)==PSA_SUCCESS && digest_size==sizeof(digest));
    assert(psa_hash_abort(&s.hash)==PSA_SUCCESS);
    for (unsigned i=0;i<sizeof(digest);++i) snprintf(hex+2*i,3,"%02x",digest[i]);
    bool complete=!s.failed && s.drained && fed==length && s.consumed==length && !s.pending.size && !eof.present;
    esp_audio_simple_dec_close(s.decoder);
    decoder_pending_input_clear(&s.pending); decoder_eof_input_clear(&eof); free(s.output);
    assert(heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    if (!adapted) {assert(complete && s.frames && s.pcm_bytes && !s.resizes); reference_bytes=s.pcm_bytes; memcpy(reference_sha,digest,sizeof(digest));}
    bool match=complete && s.pcm_bytes==reference_bytes && !memcmp(reference_sha,digest,sizeof(digest));
    printf("EOSR_CASE strategy=%s chunk=%u complete=%u outcome=%u fed=%u input=%u calls=%u frames=%u pcm=%" PRIu64
           " sha256=%s feeds=%u coalesces=%u pending_max=%u resizes=%u error_consumed=%u empty_retries=%u data_eos_calls=%u empty_eos_calls=%u final_capacity=%u match=%u before=%u after=%u stack_free=%u core=%d priority=%u last_result=%d\n",
           s.strategy,chunk,(unsigned)complete,s.outcome,(unsigned)fed,(unsigned)s.consumed,s.calls,s.frames,s.pcm_bytes,hex,
           s.feeds,s.coalesces,(unsigned)s.pending_max,s.resizes,s.error_consumed,s.empty_retries,s.data_eos_calls,s.empty_eos_calls,
           (unsigned)s.capacity,(unsigned)match,(unsigned)before,(unsigned)after,(unsigned)uxTaskGetStackHighWaterMark(NULL),
           xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL),s.last_result);
    assert(fflush(stdout)==0);
    if (adapted) assert(before==after);
    assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3);
    *consumed_on_resize=s.error_consumed>0;
    vTaskDelay(1);
    return match;
}
static void worker(void *unused) {
    (void)unused;
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    assert(psa_crypto_init()==PSA_SUCCESS);
    size_t before=esp_get_free_heap_size();
    assert(decoder_register_codecs()==ESP_AUDIO_ERR_OK);
    bool consumed=false;
    assert(decode((unsigned)(fixture_end-fixture_start),false,false,&consumed));
    unsigned fallback=0; bool current_all=true;
    const unsigned chunks[]={4096,257,1};
    for (unsigned i=0;i<3;++i) {
        bool match=decode(chunks[i],true,false,&consumed);
        current_all=current_all && match;
        if (!match || consumed) {++fallback; decode(chunks[i],true,true,&consumed);}
    }
    decoder_unregister_codecs();
    assert(heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    printf("EOSR_COMPLETE target=esp32 current_cases=3 honor_cases=%u core=1 current_playback_matches=%u registry_before=%u heap_free=%u retained=%d heap_min=%u stack_free=%u heap_integrity=1\n",
           fallback,(unsigned)current_all,(unsigned)before,(unsigned)after,(int)before-(int)after,
           (unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout)==0);
    esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0 && fixture_end-fixture_start==707097);
    printf("EOSR_BEGIN target=esp32 coordinator=0 worker=1 stack=16384 priority=3 initial_capacity=12288 baseline_capacity=24576 fixture=707097\n");
    assert(fflush(stdout)==0);
    assert(xTaskCreatePinnedToCore(worker,"opusstreamresize",16384,NULL,3,NULL,1)==pdPASS);
    while (true) vTaskDelay(portMAX_DELAY);
}
