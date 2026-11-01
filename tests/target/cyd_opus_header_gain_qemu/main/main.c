/* Observe unchanged public Ogg/Opus output gain; no application gain is added. */
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
#ifdef NDEBUG
#error "The diagnostic requires assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "Classic ESP32/LX6 only"
#endif
extern const uint8_t fixture_start[] asm("_binary_gains_bin_start");
extern const uint8_t fixture_end[] asm("_binary_gains_bin_end");
typedef struct {uint32_t magic,version,count,entry_size;} header_t;
typedef struct {char name[16];int32_t gain_q8;uint32_t offset,bytes,reserved;} entry_t;
_Static_assert(sizeof(header_t)==16 && sizeof(entry_t)==32,"fixture transport ABI");
static uint8_t pcm[24576];
static size_t stable_heap;
static unsigned cases;
typedef struct {
    esp_audio_simple_dec_handle_t decoder;
    psa_hash_operation_t hash;
    decoder_pending_input_t pending;
    uint64_t bytes,energy,absolute,nonzero,clips;
    size_t consumed;
    unsigned calls,frames,coalesces,data_eos,empty_eos;
    uint32_t peak;
    bool drained;
} stream_t;
typedef struct {uint8_t sha[32];uint64_t bytes,energy,absolute,nonzero,clips;uint32_t peak;} result_t;

static void process(stream_t *s,uint8_t *data,uint32_t bytes,bool eos,bool adapted) {
    esp_audio_simple_dec_raw_t raw={.buffer=data,.len=bytes,.eos=eos};
    bool owned=false;
    if(adapted)assert(decoder_pending_input_prepare(&s->pending,data,bytes,&raw.buffer,&raw.len,&owned)==DECODER_PENDING_INPUT_OK);
    do {
        esp_audio_simple_dec_out_t frame={.buffer=pcm,.len=sizeof(pcm)};
        raw.consumed=0;
        if(raw.eos){if(raw.len)++s->data_eos;else ++s->empty_eos;}
        esp_audio_err_t r=esp_audio_simple_dec_process(s->decoder,&raw,&frame);
        assert(r==ESP_AUDIO_ERR_OK && raw.consumed<=raw.len && frame.decoded_size<=sizeof(pcm));
        raw.buffer+=raw.consumed;raw.len-=raw.consumed;s->consumed+=raw.consumed;++s->calls;
        if(frame.decoded_size) {
            esp_audio_simple_dec_info_t info={0};
            assert(esp_audio_simple_dec_get_info(s->decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16 && frame.decoded_size%4==0);
            assert(psa_hash_update(&s->hash,pcm,frame.decoded_size)==PSA_SUCCESS);
            s->bytes+=frame.decoded_size;++s->frames;
            for(unsigned i=0;i<frame.decoded_size;i+=2) {
                uint32_t value=(uint32_t)pcm[i]|((uint32_t)pcm[i+1]<<8);
                int64_t sample=value<32768 ? (int64_t)value:(int64_t)value-65536;
                uint32_t magnitude=(uint32_t)(sample<0 ? -sample:sample);
                s->energy+=(uint64_t)(sample*sample);s->absolute+=magnitude;
                s->nonzero+=sample!=0;s->clips+=sample==-32768 || sample==32767;
                if(magnitude>s->peak)s->peak=magnitude;
            }
        }
        if(!(s->calls&31U))vTaskDelay(1);
        if(!raw.consumed && !frame.decoded_size) {
            if(raw.eos){assert(!raw.len);s->drained=true;}
            else {
                assert(adapted && raw.len);
                assert(decoder_pending_input_retain(&s->pending,raw.buffer,raw.len,owned)==DECODER_PENDING_INPUT_OK);
                ++s->coalesces;
            }
            break;
        }
    } while(raw.len || raw.eos);
}

static result_t decode(unsigned id,const entry_t *entry,unsigned chunk) {
    size_t before=esp_get_free_heap_size();
    stream_t s={.hash=PSA_HASH_OPERATION_INIT};
    const uint8_t *body=fixture_start+entry->offset;
    assert(body[26]==1 && body[27]==19 && !memcmp(body+28,"OpusHead",8));
    int32_t gain=(int32_t)body[44]|((int32_t)body[45]<<8);if(gain>=32768)gain-=65536;
    assert(gain==entry->gain_q8 && !entry->reserved);
    esp_audio_simple_dec_cfg_t cfg={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG,.use_frame_dec=false};
    assert(esp_audio_simple_dec_open(&cfg,&s.decoder)==ESP_AUDIO_ERR_OK && s.decoder);
    assert(psa_hash_setup(&s.hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    size_t fed=0;
    if(chunk==entry->bytes){process(&s,(uint8_t *)body,entry->bytes,true,false);fed=entry->bytes;}
    else while(fed<entry->bytes) {
        size_t n=entry->bytes-fed;if(n>chunk)n=chunk;
        process(&s,(uint8_t *)body+fed,(uint32_t)n,fed+n==entry->bytes,true);fed+=n;
    }
    assert(s.drained && s.consumed==entry->bytes && fed==entry->bytes && s.bytes==2115840 && s.nonzero && s.energy);
    result_t result={.bytes=s.bytes,.energy=s.energy,.absolute=s.absolute,.nonzero=s.nonzero,.clips=s.clips,.peak=s.peak};
    size_t hash_bytes=0;assert(psa_hash_finish(&s.hash,result.sha,32,&hash_bytes)==PSA_SUCCESS && hash_bytes==32);
    assert(psa_hash_abort(&s.hash)==PSA_SUCCESS);
    esp_audio_simple_dec_close(s.decoder);decoder_pending_input_clear(&s.pending);
    assert(heap_caps_check_integrity_all(true));
    char hex[65];for(unsigned i=0;i<32;++i)sprintf(hex+2*i,"%02x",(unsigned)result.sha[i]);
    size_t after=esp_get_free_heap_size();
    printf("OPUS_GAIN_CASE id=%u gain_q8=%" PRId32 " chunk=%u input=%u calls=%u frames=%u pcm=%" PRIu64
           " sha256=%s energy=%" PRIu64 " absolute=%" PRIu64 " nonzero=%" PRIu64 " clips=%" PRIu64 " peak=%" PRIu32
           " data_eos=%u empty_eos=%u coalesces=%u before=%u after=%u stack_free=%u core=%d priority=%u\n",
           id,gain,chunk,(unsigned)s.consumed,s.calls,s.frames,s.bytes,hex,s.energy,s.absolute,s.nonzero,s.clips,s.peak,
           s.data_eos,s.empty_eos,s.coalesces,(unsigned)before,(unsigned)after,
           (unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));fflush(stdout);
    if(!cases)stable_heap=after;else assert(before==after && after==stable_heap);
    ++cases;vTaskDelay(1);return result;
}

static void worker(void *unused) {
    (void)unused;
    assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK &&
           esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    assert(psa_crypto_init()==PSA_SUCCESS);
    size_t before=esp_get_free_heap_size();assert(decoder_register_codecs()==ESP_AUDIO_ERR_OK);
    const header_t *header=(const header_t *)fixture_start;
    assert(header->magic==UINT32_C(0x4f47474e) && header->version==1 && header->count==3 && header->entry_size==sizeof(entry_t));
    const entry_t *entries=(const entry_t *)(header+1);
    for(unsigned id=0;id<3;++id) {
        const entry_t *e=entries+id;
        assert(e->offset>=112 && e->offset<(size_t)(fixture_end-fixture_start) && e->bytes==706319 &&
               e->bytes<=(size_t)(fixture_end-fixture_start)-e->offset);
        result_t whole=decode(id,e,e->bytes),split=decode(id,e,257);
        assert(whole.bytes==split.bytes && !memcmp(whole.sha,split.sha,32) && whole.energy==split.energy &&
               whole.absolute==split.absolute && whole.nonzero==split.nonzero && whole.clips==split.clips && whole.peak==split.peak);
    }
    decoder_unregister_codecs();assert(cases==6 && heap_caps_check_integrity_all(true));size_t after=esp_get_free_heap_size();
    printf("OPUS_GAIN_COMPLETE cases=6 core=1 registry_before=%u heap_free=%u retained=%d heap_min=%u stack_free=%u heap_integrity=1\n",
           (unsigned)before,(unsigned)after,(int)before-(int)after,(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)uxTaskGetStackHighWaterMark(NULL));fflush(stdout);esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0);
    printf("OPUS_GAIN_BEGIN target=esp32 coordinator=0 worker=1 stack=16384 priority=3 output_capacity=24576 variants=3\n");fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker,"opusgain",16384,NULL,3,NULL,1)==pdPASS);
    while(true)vTaskDelay(portMAX_DELAY);
}
