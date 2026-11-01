// New stock public-API diagnostic: complete PCM is observed, never modified.
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_audio_simple_dec.h"
#include "psa/crypto.h"
#include "decoder_registration.h"
#include "window_ranges.h"

#ifdef NDEBUG
#error "PCM capture requires assertions"
#endif
extern const uint8_t short_start[] asm("_binary_fixture20_ogg_start");
extern const uint8_t short_end[] asm("_binary_fixture20_ogg_end");
extern const uint8_t long_start[] asm("_binary_fixture120_ogg_start");
extern const uint8_t long_end[] asm("_binary_fixture120_ogg_end");
static uint8_t pcm[24576];

static void hex_digest(const uint8_t digest[32], char hex[65]) {
    for (unsigned i=0;i<32;++i) snprintf(hex+2*i,3,"%02x",(unsigned)digest[i]);
}

static void print_pcm(const char *name, const uint8_t *data, size_t bytes,
                      uint64_t offset, unsigned *sequence) {
    static const char digits[]="0123456789abcdef";
    char hex[513];
    for (size_t at=0;at<bytes;) {
        size_t length=bytes-at;
        if (length>256) length=256;
        for (size_t j=0;j<length;++j) {
            unsigned byte=data[at+j];
            hex[2*j]=digits[byte>>4];hex[2*j+1]=digits[byte&15];
        }
        hex[2*length]=0;
        printf("EOPC_DATA id=%s seq=%u offset=%" PRIu64 " size=%u hex=%s\n",
               name,(*sequence)++,offset+at,(unsigned)length,hex);
        at+=length;
    }
}

static void decode(const char *name, const uint8_t *start, const uint8_t *end,
                   uint64_t begin, uint64_t finish) {
    assert(heap_caps_check_integrity_all(true));
    size_t before=esp_get_free_heap_size();
    esp_audio_simple_dec_cfg_t config={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG,
                                      .use_frame_dec=false};
    esp_audio_simple_dec_handle_t decoder=NULL;
    assert(esp_audio_simple_dec_open(&config,&decoder)==ESP_AUDIO_ERR_OK && decoder);
    psa_hash_operation_t hash=PSA_HASH_OPERATION_INIT,window_hash=PSA_HASH_OPERATION_INIT;
    assert(psa_hash_setup(&hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    assert(psa_hash_setup(&window_hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)start,.len=(uint32_t)(end-start),.eos=true};
    uint64_t bytes=0,window_bytes=0;
    unsigned calls=0,frames=0,sequence=0;
    size_t consumed=0;
    for (;;) {
        esp_audio_simple_dec_out_t frame={.buffer=pcm,.len=sizeof(pcm)};
        raw.consumed=0;
        esp_audio_err_t status=esp_audio_simple_dec_process(decoder,&raw,&frame);
        assert(status==ESP_AUDIO_ERR_OK);
        assert(raw.consumed<=raw.len && frame.decoded_size<=sizeof(pcm));
        consumed+=raw.consumed;
        if (raw.consumed) raw.buffer+=raw.consumed;
        raw.len-=raw.consumed;
        ++calls;
        if (frame.decoded_size) {
            esp_audio_simple_dec_info_t info={0};
            assert(esp_audio_simple_dec_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16);
            assert(frame.decoded_size%4==0);
            assert(psa_hash_update(&hash,frame.buffer,frame.decoded_size)==PSA_SUCCESS);
            uint64_t first=bytes>begin*4?bytes:begin*4;
            uint64_t last=bytes+frame.decoded_size;
            if (last>finish*4) last=finish*4;
            if (first<last) {
                assert(psa_hash_update(&window_hash,frame.buffer+(size_t)(first-bytes),(size_t)(last-first))==PSA_SUCCESS);
                window_bytes+=last-first;
            }
            print_pcm(name,frame.buffer,frame.decoded_size,bytes,&sequence);
            bytes+=frame.decoded_size;++frames;
        }
        if (!(calls&31U)) vTaskDelay(1);
        if (!raw.consumed && !frame.decoded_size) { assert(!raw.len);break; }
    }
    assert(consumed==(size_t)(end-start) && frames && window_bytes==(finish-begin)*4);
    uint8_t digest[32],window_digest[32];size_t digest_bytes=0;
    assert(psa_hash_finish(&hash,digest,32,&digest_bytes)==PSA_SUCCESS && digest_bytes==32);
    assert(psa_hash_finish(&window_hash,window_digest,32,&digest_bytes)==PSA_SUCCESS && digest_bytes==32);
    assert(psa_hash_abort(&hash)==PSA_SUCCESS && psa_hash_abort(&window_hash)==PSA_SUCCESS);
    esp_audio_simple_dec_close(decoder);
    assert(heap_caps_check_integrity_all(true));
    char hex[65],window_hex[65];hex_digest(digest,hex);hex_digest(window_digest,window_hex);
    printf("EOPC_CASE id=%s input=%u calls=%u frames=%u pcm=%" PRIu64 " sha256=%s"
           " window_begin=%" PRIu64 " window_end=%" PRIu64 " window_bytes=%" PRIu64 " window_sha256=%s"
           " sample_rate=48000 channels=2 bits=16 heap_before=%u heap_after=%u stack_free=%u core=%d priority=%u\n",
           name,(unsigned)consumed,calls,frames,bytes,hex,begin,finish,window_bytes,window_hex,
           (unsigned)before,(unsigned)esp_get_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),
           xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    assert(fflush(stdout)==0);
}

static void worker(void *unused) {
    (void)unused;
    assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK &&
           esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    assert(psa_crypto_init()==PSA_SUCCESS && decoder_register_codecs()==ESP_AUDIO_ERR_OK);
    decode("F20",short_start,short_end,SHORT_WINDOW_BEGIN,SHORT_WINDOW_END);
    decode("F120",long_start,long_end,LONG_WINDOW_BEGIN,LONG_WINDOW_END);
    decoder_unregister_codecs();
    assert(heap_caps_check_integrity_all(true));
    printf("EOPC_COMPLETE cases=2 core=1 priority=3 heap_free=%u heap_min=%u stack_free=%u heap_integrity=1\n",
           (unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout)==0);esp_restart();
}

void app_main(void) {
    assert(xPortGetCoreID()==0 && short_end-short_start==706319 && long_end-long_start==707097);
    printf("EOPC_BEGIN coordinator=0 worker=1 priority=3 stack=16384 output_capacity=24576 fixtures=2\n");
    assert(fflush(stdout)==0);
    assert(xTaskCreatePinnedToCore(worker,"opusposition",16384,NULL,3,NULL,1)==pdPASS);
    while (true) vTaskDelay(portMAX_DELAY);
}
