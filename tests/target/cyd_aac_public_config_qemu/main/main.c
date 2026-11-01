/* Public Espressif AAC configuration; no private codec ABI or wrappers. */
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
#include "aac_public_config.h"

#ifdef NDEBUG
#error "The native diagnostic requires assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32 || !CONFIG_YORADIO_AAC_PLUS
#error "This diagnostic requires classic ESP32 and the public AAC-Plus preference"
#endif
extern const uint8_t fixture_start[] asm("_binary_fixtures_bin_start");
extern const uint8_t fixture_end[] asm("_binary_fixtures_bin_end");
typedef struct { uint32_t magic, version, count, entry_size; } header_t;
typedef struct {
    char name[64];
    uint32_t offset, size, rate, channels, core_rate, core_channels, frames, pcm;
} entry_t;
_Static_assert(sizeof(header_t)==16 && sizeof(entry_t)==96,"fixture data ABI");
static uint8_t *pcm;
static uint32_t capacity;
static size_t stable_heap;
static unsigned case_count, scoped_opens;

typedef struct {
    esp_audio_simple_dec_handle_t decoder;
    psa_hash_operation_t hash;
    decoder_pending_input_t pending;
    size_t input;
    uint64_t bytes, samples, stereo_differences;
    uint32_t rate, channels, bits;
    unsigned calls, frames, resizes, coalesces;
    bool drained;
} stream_t;
typedef struct { uint8_t sha[32]; uint64_t bytes; uint32_t rate, channels; } identity_t;
typedef struct { bool original_plus, overwritten_plus, outer_config_cleared; } open_observation_t;

/* All configuration storage belongs to this helper's stack. Mutate valid
 * public fields after synchronous open, then return before any decoding. */
static __attribute__((noinline)) esp_audio_err_t open_scoped(unsigned mode,
    esp_audio_simple_dec_handle_t *decoder,open_observation_t *observation) {
    esp_aac_dec_cfg_t aac=mode==2 ? native_aac_public_config() : (esp_aac_dec_cfg_t)ESP_AAC_DEC_CONFIG_DEFAULT();
    assert(aac.aac_plus_enable==(mode==2));
    esp_audio_simple_dec_cfg_t cfg={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_AAC,
        .dec_cfg=mode ? &aac : NULL,.cfg_size=mode ? sizeof(aac) : 0,.use_frame_dec=false};
    observation->original_plus=aac.aac_plus_enable;
    esp_audio_err_t result=esp_audio_simple_dec_open(&cfg,decoder);
    volatile esp_aac_dec_cfg_t *owned=&aac;
    owned->aac_plus_enable=!observation->original_plus;
    owned->sample_rate=8000;owned->channel=1;owned->bits_per_sample=8;
    observation->overwritten_plus=owned->aac_plus_enable;
    volatile esp_audio_simple_dec_cfg_t *outer=&cfg;
    outer->dec_cfg=NULL;outer->cfg_size=0;outer->use_frame_dec=true;
    observation->outer_config_cleared=outer->dec_cfg==NULL && !outer->cfg_size && outer->use_frame_dec;
    assert(observation->overwritten_plus!=observation->original_plus && observation->outer_config_cleared);
    ++scoped_opens;
    return result;
}

static void process(stream_t *s,uint8_t *data,uint32_t bytes,bool eos) {
    esp_audio_simple_dec_raw_t raw={.buffer=data,.len=bytes,.eos=eos};
    bool owned=false;
    assert(decoder_pending_input_prepare(&s->pending,data,bytes,&raw.buffer,&raw.len,&owned)==DECODER_PENDING_INPUT_OK);
    do {
        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=capacity};
        raw.consumed=0;
        esp_audio_err_t result=esp_audio_simple_dec_process(s->decoder,&raw,&out);
        ++s->calls;
        assert(raw.consumed<=raw.len && out.decoded_size<=capacity);
        raw.buffer+=raw.consumed; raw.len-=raw.consumed; s->input+=raw.consumed;
        if (!(s->calls&31U)) vTaskDelay(1);
        if (result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            assert(!out.decoded_size && out.needed_size>capacity);
            uint8_t *larger=realloc(pcm,out.needed_size); assert(larger);
            pcm=larger;capacity=out.needed_size;++s->resizes;
            continue;
        }
        if (result!=ESP_AUDIO_ERR_OK) {
            printf("AAC_PUBLIC_ERROR result=%d len=%" PRIu32 " consumed=%" PRIu32 " eos=%u\n",
                   result,raw.len,raw.consumed,(unsigned)raw.eos);fflush(stdout);
        }
        assert(result==ESP_AUDIO_ERR_OK);
        if (out.decoded_size) {
            esp_audio_simple_dec_info_t info={0};
            assert(esp_audio_simple_dec_get_info(s->decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate && (info.channel==1 || info.channel==2) && info.bits_per_sample==16);
            assert(out.decoded_size%(info.channel*2)==0);
            if(s->frames) assert(s->rate==info.sample_rate && s->channels==info.channel && s->bits==info.bits_per_sample);
            s->rate=info.sample_rate;s->channels=info.channel;s->bits=info.bits_per_sample;
            assert(psa_hash_update(&s->hash,out.buffer,out.decoded_size)==PSA_SUCCESS);
            s->bytes+=out.decoded_size;s->samples+=out.decoded_size/(info.channel*2);++s->frames;
            if(info.channel==2) for(unsigned i=0;i<out.decoded_size;i+=4) {
                if(pcm[i]!=pcm[i+2] || pcm[i+1]!=pcm[i+3]) ++s->stereo_differences;
            }
        }
        if (!raw.consumed && !out.decoded_size) {
            if(raw.eos) { assert(!raw.len);s->drained=true; }
            else {
                assert(raw.len);
                assert(decoder_pending_input_retain(&s->pending,raw.buffer,raw.len,owned)==DECODER_PENDING_INPUT_OK);
                ++s->coalesces;
            }
            break;
        }
    } while(raw.len || raw.eos);
}

static identity_t decode(unsigned id,const entry_t *e,unsigned mode,unsigned chunk) {
    assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3);
    size_t before=esp_get_free_heap_size();
    stream_t s={.hash=PSA_HASH_OPERATION_INIT};
    open_observation_t observed={0};
    assert(open_scoped(mode,&s.decoder,&observed)==ESP_AUDIO_ERR_OK && s.decoder);
    printf("AAC_PUBLIC_OPEN instance=%u mode=%u cfg_present=%u original_plus=%u overwritten_plus=%u outer_cleared=%u scope_returned=1\n",
           scoped_opens,mode,(unsigned)(mode!=0),(unsigned)observed.original_plus,
           (unsigned)observed.overwritten_plus,(unsigned)observed.outer_config_cleared);fflush(stdout);
    assert(psa_hash_setup(&s.hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    size_t fed=0;
    while(fed<e->size) {
        size_t n=e->size-fed;if(n>chunk)n=chunk;
        process(&s,(uint8_t *)fixture_start+e->offset+fed,(uint32_t)n,false);fed+=n;
    }
    process(&s,(uint8_t *)fixture_start+e->offset+e->size,0,true);
    assert(s.drained && s.input==e->size && s.bytes && s.frames);
    identity_t result={.bytes=s.bytes,.rate=s.rate,.channels=s.channels};size_t hash_size=0;
    assert(psa_hash_finish(&s.hash,result.sha,sizeof(result.sha),&hash_size)==PSA_SUCCESS && hash_size==32);
    assert(psa_hash_abort(&s.hash)==PSA_SUCCESS);
    char hex[65];for(unsigned i=0;i<32;++i)sprintf(hex+i*2,"%02x",result.sha[i]);
    esp_audio_simple_dec_close(s.decoder);decoder_pending_input_clear(&s.pending);
    assert(heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    printf("AAC_PUBLIC_CASE id=%u name=%s mode=%u chunk=%u input=%u calls=%u frames=%u pcm=%" PRIu64
           " sha256=%s rate=%" PRIu32 " channels=%" PRIu32 " bits=%" PRIu32 " samples=%" PRIu64
           " stereo_differences=%" PRIu64 " resizes=%u coalesces=%u before=%u after=%u stack_free=%u core=%d priority=%u\n",
           id,e->name,mode,chunk,(unsigned)s.input,s.calls,s.frames,s.bytes,hex,s.rate,s.channels,s.bits,s.samples,
           s.stereo_differences,s.resizes,s.coalesces,(unsigned)before,(unsigned)after,
           (unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    fflush(stdout);
    if(!case_count)stable_heap=after;
    else assert(before==after && after==stable_heap);
    ++case_count;
    if(mode==2) {
        assert(s.rate==e->rate && s.channels==e->channels && s.bytes==e->pcm);
        assert(s.samples==(uint64_t)e->frames*(e->rate==e->core_rate ? 1024U:2048U));
        if(e->channels==2)assert(s.stereo_differences);
    }
    vTaskDelay(1);return result;
}

static void equal(identity_t a,identity_t b) {
    assert(a.bytes==b.bytes && a.rate==b.rate && a.channels==b.channels && !memcmp(a.sha,b.sha,32));
}
static void worker(void *unused) {
    (void)unused;
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    assert(psa_crypto_init()==PSA_SUCCESS);
    capacity=12288;pcm=malloc(capacity);assert(pcm);
    size_t registry_before=esp_get_free_heap_size();
    assert(decoder_register_codecs()==ESP_AUDIO_ERR_OK);
    const header_t *h=(const header_t *)fixture_start;
    assert(h->magic==UINT32_C(0x41414350) && h->version==1 && h->count==6 && h->entry_size==sizeof(entry_t));
    const entry_t *entries=(const entry_t *)(h+1);
    for(unsigned id=0;id<h->count;++id) {
        const entry_t *e=&entries[id];
        assert(e->offset>=16+6*96 && e->offset<(size_t)(fixture_end-fixture_start));
        assert(e->size<=(size_t)(fixture_end-fixture_start)-e->offset && e->size);
        identity_t baseline=decode(id,e,0,e->size),off=decode(id,e,1,e->size),on=decode(id,e,2,e->size);
        equal(baseline,off);
        if(e->rate==e->core_rate)equal(off,on);
        else assert(off.rate==e->core_rate && on.rate==2*off.rate && off.bytes!=on.bytes);
        equal(on,decode(id,e,2,4096));equal(on,decode(id,e,2,257));equal(on,decode(id,e,2,1));
    }
    decoder_unregister_codecs();
    size_t after=esp_get_free_heap_size();
    assert(case_count==36 && scoped_opens==36 && heap_caps_check_integrity_all(true));
    printf("AAC_PUBLIC_COMPLETE cases=36 core=1 registry_before=%u heap_free=%u retained=%d heap_min=%u stack_free=%u capacity=%u scoped_opens=%u heap_integrity=1\n",
           (unsigned)registry_before,(unsigned)after,(int)registry_before-(int)after,
           (unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),(unsigned)capacity,scoped_opens);
    free(pcm);fflush(stdout);esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0);
    printf("AAC_PUBLIC_BEGIN target=esp32 coordinator=0 worker=1 stack=16384 priority=3 initial_capacity=12288 fixtures=6\n");fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker,"aacpublic",16384,NULL,3,NULL,1)==pdPASS);
    while(true)vTaskDelay(portMAX_DELAY);
}
