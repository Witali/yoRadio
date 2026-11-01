/* PLATFORM */
#include <math.h>
#include <stdlib.h>
#include <unistd.h>

static int pdm_release(bool ramp) { (void)ramp; return ESP_OK; }
static int idf6_dac_output_end(void) { return ESP_OK; }
#if TEST_PDM
static void *s_pdm = (void *)1;
static bool s_pdm_running = true;
static int16_t s_sample_buffer[512];
static bool s_resampler_has_previous;
static int16_t s_resampler_previous;
static uint32_t s_resampler_next_phase;
static int i2s_channel_write(void *handle, const void *data, size_t size,
                              size_t *written, unsigned timeout) {
    (void)handle; (void)timeout;
    if (write_result != ESP_OK) { *written = 0; return write_result; }
    *written = size; return capture(data, size);
}
#endif
/* PRODUCTION */
#include "surround_vectors.h"
void reference_owner(void);
void surround_reference_configure(bool,uint8_t,int8_t,uint16_t,uint32_t);
void surround_reference_process(int16_t *,uint8_t);
unsigned surround_normalizer_calls(void);
static FILE *trace;
static unsigned vector_cases, stream_cases, controls, fraction;

static void append(const void *bytes, size_t count) {
    assert(count <= sizeof(expected)-expected_size);
    memcpy(expected+expected_size, bytes, count); expected_size += count;
}
static void output_reference(int16_t sample) {
#if TEST_PDM
    append(&sample, sizeof(sample));
#elif TEST_DAC
    int shifted = sample < 0 ? -((-(int)sample+255)/256) : sample/256;
    uint8_t code = (uint8_t)(shifted+128); append(&code, 1);
#else
    unsigned value = (unsigned)((int)sample+32768);
    for (unsigned phase=0;phase<16;++phase) {
        unsigned code=value/256;
        if (code==255) fraction=0;
        else {unsigned sum=fraction+value%256;code+=sum/256;fraction=sum%256;}
        uint32_t word=code*0x01000100U;append(&word,4);
    }
#endif
}
static void reset_case(void) {
    native_audio_output_discard_pcm();
    assert(s_channel_layout==PCM_CHANNEL_LAYOUT_LEGACY && !s_layout_channels && !s_header_gain.active);
    surround_reference_configure(enabled,gain_db,target_dbfs,time_ms,48000);
    fraction=0;captured_size=expected_size=0;
}
static void finish_case(void) {
#if TEST_PDM
    int16_t zero=0;
    while ((expected_size/2)%512) append(&zero,2);
#endif
    assert(native_audio_output_flush_pcm()==ESP_OK);
    assert(s_channel_layout==PCM_CHANNEL_LAYOUT_LEGACY && !s_header_gain.active);
    if(captured_size!=expected_size || memcmp(captured,expected,expected_size)) {
        size_t at=0;while(at<captured_size && at<expected_size && captured[at]==expected[at])++at;
        fprintf(stderr,"surround mismatch vectors=%u streams=%u offset=%zu actual_size=%zu expected_size=%zu\n",
                vector_cases,stream_cases,at,captured_size,expected_size);
        assert(!"surround output differs");
    }
}
static int coefficient(unsigned v,unsigned b) {return (int)(((int64_t)v*b*32768+2032)/4064);}
static int scaled(int16_t sample,unsigned gain) {
    int64_t n=(int64_t)sample*gain;
    return (int)(n<0?-((-n+16384)/32768):(n+16384)/32768);
}
static int16_t mono_reference(const int16_t *samples,unsigned channels,int gain) {
    int gl=coefficient(volume,channels>1 && balance<0?16+balance:16);
    int gr=coefficient(volume,balance>0?16-balance:16);
    int16_t result;
    if(channels<=2 && !gain) {
        int left=scaled(samples[0],gl);
        result=(int16_t)(channels==1?left:(left+scaled(samples[1],gr))/2);
    } else {
        long double value=0, factor=powl(10.0L,(long double)gain/5120.0L);
        if(channels<=2) value=(long double)samples[0]*gl+(channels>1?(long double)samples[1]*gr:0);
        else {
            bool equal=true;
            for(unsigned c=1;c<channels;++c)equal=equal && samples[c]==samples[0];
            if(equal)value=(long double)samples[0]*(gl+gr)*(channels<=4?1:2);
            else for(unsigned c=0;c<channels;++c)
                value+=samples[c]*(reference_left[channels-1][c]*gl+reference_right[channels-1][c]*gr);
        }
        value*=factor/(channels==1?32768.0L:65536.0L);
        result=value>=32767?32767:value<=-32768?-32768:
            (int16_t)(value>=0?(int32_t)(value+0.5L):-(int32_t)(-value+0.5L));
    }
    fprintf(trace,"%u,%d,%u,%d",channels,gain,volume,balance);
    for(unsigned c=0;c<channels;++c)fprintf(trace,",%d",samples[c]);
    fprintf(trace,",%d\n",result);return result;
}
static void encode(uint8_t *to,unsigned bits,int16_t sample) {
    int64_t value=bits==8?sample/256:(int64_t)sample*(INT64_C(1)<<(bits-16));
    if(bits>16)value+=(INT64_C(1)<<(bits-16))-1;
    for(unsigned byte=0;byte<bits/8;++byte)to[byte]=(uint8_t)((uint64_t)value>>(8*byte));
}
static int16_t project(const uint8_t *p,unsigned bits) {
    uint64_t raw=0;for(unsigned b=0;b<bits/8;++b)raw|=(uint64_t)p[b]<<(8*b);
    int64_t n=raw&(UINT64_C(1)<<(bits-1))?(int64_t)raw-(INT64_C(1)<<bits):(int64_t)raw;
    if(bits==8)return (int16_t)(n*256);
    int64_t div=INT64_C(1)<<(bits-16);
    return (int16_t)(n<0?-((-n+div-1)/div):n/div);
}
static void vectors(void) {
    for(size_t i=0;i<sizeof(surround_vectors)/sizeof(*surround_vectors);++i) {
        const surround_vector *v=surround_vectors+i;
        enabled=false;volume=v->volume;balance=v->balance;reset_case();
        uint8_t input[35]={0};size_t frame=v->channels*(v->bits/8);
        for(unsigned c=0;c<v->channels;++c)encode(input+1+c*(v->bits/8),v->bits,v->samples[c]);
        assert(native_audio_output_set_channel_layout(PCM_CHANNEL_LAYOUT_VORBIS,(uint8_t)v->channels)==ESP_OK);
        assert(native_audio_output_set_header_gain((int16_t)v->gain)==ESP_OK);
        output_reference((int16_t)v->expected);
        assert(native_audio_output_write_pcm(input+1,frame+(frame>1?1:0),(uint8_t)v->bits,(uint8_t)v->channels)==ESP_OK);
        finish_case();++vector_cases;
    }
}
static void packet(const uint8_t *input,size_t frames,unsigned bits,unsigned channels,int gain) {
    assert(native_audio_output_set_channel_layout(PCM_CHANNEL_LAYOUT_VORBIS,(uint8_t)channels)==ESP_OK);
    assert(native_audio_output_set_header_gain((int16_t)gain)==ESP_OK);
    for(size_t frame=0;frame<frames;++frame) {
        int16_t samples[8];
        for(unsigned c=0;c<channels;++c)samples[c]=project(input+(frame*channels+c)*(bits/8),bits);
        surround_reference_process(samples,(uint8_t)channels);
        output_reference(mono_reference(samples,channels,gain));
    }
    assert(native_audio_output_write_pcm(input,frames*channels*(bits/8),(uint8_t)bits,(uint8_t)channels)==ESP_OK);
    ++stream_cases;
}
static void streams(void) {
    uint8_t *mapping=mmap(NULL,32768,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    assert(mapping!=MAP_FAILED);uint8_t *input=mapping+1;
    for(size_t n=0;n<32760;++n)input[n]=(uint8_t)(n*137u+n/11u);
    assert(!mprotect(mapping,32768,PROT_READ));
    const unsigned widths[]={8,16,24,32};
    for(unsigned normalized=0;normalized<2;++normalized)
        for(unsigned width=0;width<4;++width)for(unsigned channels=1;channels<=8;++channels) {
            unsigned bits=widths[width];enabled=normalized;volume=1;balance=-7;reset_case();
            packet(input,257,bits,channels,48*256);
            packet(input,127,bits,channels,-6*256);
            volume=127;balance=11;packet(input,257,bits,channels,0);
            finish_case();
            for(unsigned split=0;split<2;++split) {
                volume=127;balance=0;reset_case();
                if(!split)packet(input,513,bits,channels,6*256);
                else {packet(input,127,bits,channels,6*256);packet(input+127*channels*(bits/8),386,bits,channels,6*256);}
                finish_case();
            }
        }
    assert(!munmap(mapping,32768));
}
static void metadata_controls(void) {
    enabled=false;volume=254;balance=0;reset_case();
    assert(native_audio_output_set_channel_layout(PCM_CHANNEL_LAYOUT_VORBIS,8)==ESP_OK);
    pcm_speaker_mix before;
    memcpy(&before,&s_speaker_mix,sizeof(before));
    assert(native_audio_output_set_channel_layout(PCM_CHANNEL_LAYOUT_VORBIS,9)==ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_set_channel_layout((pcm_channel_layout)255,8)==ESP_ERR_NOT_SUPPORTED);
    assert(native_audio_output_set_channel_layout(PCM_CHANNEL_LAYOUT_LEGACY,0)==ESP_ERR_NOT_SUPPORTED);
    assert(s_channel_layout==PCM_CHANNEL_LAYOUT_VORBIS && s_layout_channels==8 && !memcmp(&before,&s_speaker_mix,sizeof(before)));
    uint8_t pcm[64]={0};
    assert(native_audio_output_write_pcm(pcm,12,16,6)==ESP_ERR_NOT_SUPPORTED && !captured_size);
    controls+=4;
    native_audio_output_discard_pcm();
    assert(native_audio_output_set_channel_layout(PCM_CHANNEL_LAYOUT_LEGACY,255)==ESP_OK);
    assert(native_audio_output_set_channel_layout(PCM_CHANNEL_LAYOUT_VORBIS,1)==ESP_OK);
    assert(native_audio_output_pause()==ESP_OK && s_channel_layout==PCM_CHANNEL_LAYOUT_LEGACY && !s_layout_channels);
    ++controls;
}
int main(int argc,char **argv) {
    assert(argc==2);trace=fopen(argv[1],"w");assert(trace);reference_owner();
    assert(native_audio_output_configure(48000)==ESP_OK);
    vectors();streams();metadata_controls();
    assert(surround_normalizer_calls()>0 && sizeof(s_normalizer_scratch)==512);
    assert(!fclose(trace));
    printf("PASS surround output vectors=%u packets=%u controls=%u scratch=512\n",vector_cases,stream_cases,controls);
}
