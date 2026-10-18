#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "vorbis_repair_abi.h"
#include "esp_vorbis_dec.h"
static unsigned allocations, failure_allocation, live, reads, malformed, oom;
static void *tracked[4096];
void *media_lib_module_calloc(const char *name,size_t count,size_t size) {
    (void)name;++allocations;
    if(allocations==failure_allocation)return NULL;
    assert(!size || count<=SIZE_MAX/size);
    // The fixture never needs an unbounded allocation. Reject absurd corrupt
    // setup sizes as allocator pressure, preserving the production failure path.
    if(count*size>16*1024*1024)return NULL;
    void *value=calloc(count,size);assert(value);
    for(unsigned i=0;i<4096;++i)if(!tracked[i]){tracked[i]=value;++live;return value;}
    assert(false);return NULL;
}
void media_lib_free(void *value) {
    if(!value)return;
    for(unsigned i=0;i<4096;++i)if(tracked[i]==value){tracked[i]=NULL;assert(live);--live;free(value);return;}
    assert(!"double/untracked free");
}
long tremor_oggpack_read(oggpack_buffer *bits,int width) {
    ++reads;assert(width>=0 && width<=32 && bits->headend<=INT32_MAX);
    if(bits->headend<0)return -1;
    uint64_t available=(uint64_t)bits->headend*8;
    if((unsigned)width>available-(unsigned)bits->headbit){bits->headend=-1;bits->headbit=0;return -1;}
    uint32_t value=0;
    for(int i=0;i<width;++i) {
        value|=(uint32_t)((*bits->headptr>>bits->headbit)&1U)<<i;
        if(++bits->headbit==8){bits->headbit=0;++bits->headptr;--bits->headend;}
    }
    // Match the signed RV32 return value for 32-bit fields even on LP64 hosts.
    return width==32 && value>INT32_MAX ? (long)((int64_t)value-INT64_C(4294967296)) : (long)value;
}
int tremor_oggpack_eop(oggpack_buffer *bits) {return bits->headend<0;}
int esp_vorbis_dec_decode(void) {return 0;}
int esp_vorbis_dec_reset(void) {return 0;}
int esp_vorbis_dec_close(void) {return 0;}
int esp_audio_dec_register(int kind,const esp_audio_dec_ops_t *operations) {(void)kind;(void)operations;return 0;}
#include "production.inc"
#include "fixtures.inc"

static void release_wrapper(vorbis_wrapper *wrapper) {
    vorbis_info *info=wrapper->dsp->vi;
    repair_dsp_destroy(wrapper->dsp);repair_vorbis_info_clear(info);media_lib_free(info);media_lib_free(wrapper);
}
static void reset(void) {assert(!live);allocations=reads=failure_allocation=0;}
static esp_vorbis_dec_cfg_t config(void) {
    return (esp_vorbis_dec_cfg_t){(uint8_t *)fixture_info,sizeof(fixture_info),(uint8_t *)fixture_setup,sizeof(fixture_setup)};
}
int main(void) {
    esp_vorbis_dec_cfg_t cfg=config();void *handle=NULL;
    assert(__wrap_esp_vorbis_dec_open(&cfg,sizeof(cfg),&handle)==ESP_AUDIO_ERR_OK && handle);
    vorbis_wrapper *wrapper=handle;
    assert(wrapper->dsp->vi->channels==2 && wrapper->dsp->vi->rate==48000);
    unsigned total=allocations;release_wrapper(wrapper);reset();
    const uint32_t bad_sizes[]={INT32_MAX+1U,UINT32_MAX};
    for(unsigned header=0;header<2;++header)for(unsigned i=0;i<2;++i) {
        cfg=config();if(header)cfg.setup_size=bad_sizes[i];else cfg.info_size=bad_sizes[i];
        handle=(void *)1;
        assert(__wrap_esp_vorbis_dec_open(&cfg,sizeof(cfg),&handle)==ESP_AUDIO_ERR_INVALID_PARAMETER);
        assert(!handle && !allocations && !reads);++malformed;
    }
    for(unsigned cut=0;cut<sizeof(fixture_info);++cut) {
        cfg=config();uint8_t *data=cut?malloc(cut):NULL;if(cut){assert(data);memcpy(data,fixture_info,cut);}
        cfg.info_header=data;cfg.info_size=cut;handle=NULL;
        assert(__wrap_esp_vorbis_dec_open(&cfg,sizeof(cfg),&handle)!=ESP_AUDIO_ERR_OK && !handle && !live);
        free(data);reset();++malformed;
    }
    // Every setup byte truncation, with exactly allocated readable storage.
    for(unsigned cut=0;cut<sizeof(fixture_setup);++cut) {
#ifdef CODEC_TRACE_PREFIX
        fprintf(stderr,"setup_prefix=%u\n",cut);
#endif
        cfg=config();uint8_t *data=cut?malloc(cut):NULL;if(cut){assert(data);memcpy(data,fixture_setup,cut);}
        cfg.setup_header=data;cfg.setup_size=cut;handle=NULL;
        assert(__wrap_esp_vorbis_dec_open(&cfg,sizeof(cfg),&handle)!=ESP_AUDIO_ERR_OK && !handle && !live);
        free(data);reset();++malformed;
    }
    for(unsigned index=1;index<=total;++index) {
        cfg=config();failure_allocation=index;handle=NULL;
        assert(__wrap_esp_vorbis_dec_open(&cfg,sizeof(cfg),&handle)!=ESP_AUDIO_ERR_OK && !handle && !live);
        ++oom;reset();
        assert(__wrap_esp_vorbis_dec_open(&cfg,sizeof(cfg),&handle)==ESP_AUDIO_ERR_OK && handle);
        release_wrapper(handle);reset();
    }
    printf("PASS Vorbis actual setup: malformed=%u OOM=%u retry, signed-span rejection before allocation/read; native-pointer ASan/UBSan, vendor DSP excluded\n",malformed,oom);
    return 0;
}
