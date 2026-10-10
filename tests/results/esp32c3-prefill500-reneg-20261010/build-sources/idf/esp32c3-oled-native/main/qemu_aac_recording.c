// QEMU-only exact PCM capture through the real adapter, using the existing
// disposable app1 recording envelope. No network, board or production path.
#include "native_aac_decoder.h"
#include "decoder_pcm.h"
#include "esp_heap_caps.h"
#include "esp_partition.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { RECORDING_MAGIC=0x31504642, GUARD_BYTES=16, CAPTURE_BYTES=256 };
typedef struct {
    uint32_t magic, bytes, rate, channels, sbr, probe_options[3];
} recording_header_t;
_Static_assert(sizeof(recording_header_t)==32,"Existing QEMU recording envelope");

static uint8_t *new_pcm(void) {
    uint8_t *p=malloc(NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);assert(p);
    memset(p,0xa5,NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);return p+GUARD_BYTES;
}
static void guard(const uint8_t *p) {
    for(unsigned i=0;i<GUARD_BYTES;++i)
        assert(p[(int)i-GUARD_BYTES]==0xa5 && p[NATIVE_AAC_PCM_FRAME_BYTES+i]==0xa5);
}
static void capture(unsigned frame,const recording_header_t *header,const uint8_t *p,unsigned bytes) {
    static const char digits[]="0123456789abcdef";
    char hex[2*CAPTURE_BYTES+1];
    printf("AAC_RECORD_PCM_FRAME frame=%u rate=%" PRIu32 " channels=%" PRIu32 " bytes=%u\n",
           frame,header->rate,header->channels,bytes);
    for(unsigned offset=0;offset<bytes;offset+=CAPTURE_BYTES) {
        unsigned count=bytes-offset;if(count>CAPTURE_BYTES)count=CAPTURE_BYTES;
        for(unsigned i=0;i<count;++i){hex[2*i]=digits[p[offset+i]>>4];hex[2*i+1]=digits[p[offset+i]&15];}
        hex[2*count]=0;
        printf("AAC_RECORD_PCM_DATA frame=%u offset=%u hex=%s\n",frame,offset,hex);
    }
}

void qemu_aac_recording_test(void) {
    const esp_partition_t *partition=esp_partition_find_first(
        ESP_PARTITION_TYPE_APP,ESP_PARTITION_SUBTYPE_APP_OTA_1,NULL);assert(partition);
    recording_header_t header;
    assert(esp_partition_read(partition,0,&header,sizeof(header))==ESP_OK);
    if(header.magic!=RECORDING_MAGIC)return;
    assert(header.bytes && header.bytes<=partition->size-sizeof(header));
    assert(header.rate>=8000 && header.rate<=96000 && header.channels>=1 && header.channels<=2);
    const void *mapped;esp_partition_mmap_handle_t handle;
    assert(esp_partition_mmap(partition,0,sizeof(header)+header.bytes,ESP_PARTITION_MMAP_DATA,&mapped,&handle)==ESP_OK);
    const uint8_t *start=(const uint8_t *)mapped+sizeof(header),*p=start,*end=p+header.bytes;
    native_aac_decoder_t *a=native_aac_decoder_create(),*b=native_aac_decoder_create();assert(a && b);
    uint8_t *left=new_pcm(),*right=new_pcm();unsigned frames=0,calls=0,samples=0;
    const char *previous_label=NULL;unsigned previous_channels=0;
    const unsigned chunks[]={1,7,193,997,31};
    printf("AAC_RECORD_BEGIN bytes=%" PRIu32 " rate=%" PRIu32 " channels=%" PRIu32 "\n",
           header.bytes,header.rate,header.channels);
    while(p<end) {
        unsigned count=end-p,chunk=chunks[calls++%(sizeof(chunks)/sizeof(chunks[0]))];if(count>chunk)count=chunk;
        esp_audio_simple_dec_raw_t ar={.buffer=(uint8_t *)p,.len=count},br=ar;
        esp_audio_simple_dec_out_t ao={.buffer=left,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        esp_audio_simple_dec_out_t bo={.buffer=right,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        memset(left,0x55,NATIVE_AAC_PCM_FRAME_BYTES);memset(right,0xaa,NATIVE_AAC_PCM_FRAME_BYTES);
        assert(native_aac_decoder_process(a,&ar,&ao)==ESP_AUDIO_ERR_OK);
        assert(native_aac_decoder_process(b,&br,&bo)==ESP_AUDIO_ERR_OK);
        guard(left);guard(right);
        assert(ar.consumed<=count && ar.consumed==br.consumed && (ar.consumed || ao.decoded_size));
        assert(ao.decoded_size<=NATIVE_AAC_PCM_FRAME_BYTES && ao.decoded_size==bo.decoded_size);
        assert(!memcmp(left,right,ao.decoded_size));p+=ar.consumed;
        if(ao.decoded_size) {
            esp_audio_simple_dec_info_t info;
            assert(native_aac_decoder_get_info(a,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==header.rate && info.channel==header.channels && info.bits_per_sample==16);
            bool pcm_only,other_pcm_only;
            const char *label=native_aac_decoder_label(a,&info,&pcm_only);
            assert(!strcmp(label,native_aac_decoder_label(b,&info,&other_pcm_only)) && pcm_only==other_pcm_only);
            unsigned source_channels=native_aac_decoder_source_channels(a);
            assert(source_channels==native_aac_decoder_source_channels(b));
            if(!previous_label || strcmp(previous_label,label) || previous_channels!=source_channels) {
                printf("AAC_RECORD_FORMAT frame=%u label=%s source_channels=%u pcm_channels=%u rate=%" PRIu32 " pcm_only=%u\n",
                       frames,label,source_channels,info.channel,info.sample_rate,pcm_only);
                previous_label=label;previous_channels=source_channels;
            }
            assert(ao.decoded_size%(sizeof(int16_t)*header.channels)==0);
            samples+=ao.decoded_size/sizeof(int16_t);capture(frames++,&header,left,ao.decoded_size);
            vTaskDelay(1);
        }
    }
    native_aac_decoder_destroy(a);native_aac_decoder_destroy(b);
    free(left-GUARD_BYTES);free(right-GUARD_BYTES);esp_partition_munmap(handle);
    assert(frames && samples && heap_caps_check_integrity_all(true));
    printf("AAC_RECORD_PASS consumed=%" PRIu32 " frames=%u channel_samples=%u calls=%u poison_patterns=2 heap=valid\n",
           header.bytes,frames,samples,calls);
}
