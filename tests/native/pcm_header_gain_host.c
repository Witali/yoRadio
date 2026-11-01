/* Application integer-PCM gain; public libopus float CTL is observation only. */
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <opus.h>

static unsigned power_calls, power_mode;
static double counted_power(double base, double exponent)
{
    ++power_calls;
    assert(base == 10.0 && exponent >= -6.4 && exponent < 6.4);
    if (power_mode == 1) return NAN;
    if (power_mode == 2) return INFINITY;
    if (power_mode == 3) return 0;
    if (power_mode == 4) return -1;
    if (power_mode == 5) return 0.5; /* Isolate the documented tie policy. */
    return pow(base, exponent);
}
#define PCM_HEADER_GAIN_POW counted_power
#include "pcm_header_gain.h"
#include "vectors.h"

static unsigned vector_applications, identity_cases, refusal_cases, reuse_cases, overflow_cases;

static void selected_vectors(void)
{
    const unsigned channels[] = {1,2,3,255};
    for (unsigned i = 0; i < sizeof(gain_vectors)/sizeof(gain_vectors[0]); ++i) {
        const reference_vector *v = &gain_vectors[i];
        pcm_header_gain gain = {0};
        unsigned calls = power_calls;
        assert(phg_begin(&gain, 45, v->gain) == PHG_OK);
        assert(power_calls == calls + (v->gain != 0));
        calls = power_calls;
        for (unsigned c = 0; c < sizeof(channels)/sizeof(channels[0]); ++c) {
            uint8_t storage[4096], before[4096];
            memset(storage, 0xa5, sizeof(storage));
            uint8_t *data = storage + 1; /* Deliberately unaligned byte storage. */
            size_t frame = (size_t)channels[c] * v->width;
            assert(3*frame+2 <= sizeof(storage));
            for (unsigned at = 0; at < channels[c]; ++at) {
                memcpy(data+at*v->width, v->input, v->width);
                memcpy(data+frame+at*v->width, v->input, v->width);
                memcpy(data+2*frame+at*v->width, v->input, v->width);
            }
            memcpy(before, storage, sizeof(storage));
            pcm_header_gain saved = gain;
            assert(phg_apply(&gain,45,(pcm_header_gain_format)v->format,(uint8_t)channels[c],
                             data,3*frame,frame,frame) == PHG_OK);
            for (unsigned at = 0; at < channels[c]; ++at)
                assert(!memcmp(data+frame+at*v->width,v->expected,v->width));
            assert(!memcmp(storage,before,frame+1));
            assert(!memcmp(data+2*frame,before+1+2*frame,sizeof(storage)-1-2*frame));
            assert(!memcmp(&gain,&saved,sizeof(gain)) && power_calls == calls);
            ++vector_applications;
        }
        phg_reset(&gain);
        assert(!gain.active);
    }
}

static void full_gain_range(void)
{
    double previous = 0;
    unsigned calls = power_calls;
    for (int32_t value = INT16_MIN; value <= INT16_MAX; ++value) {
        pcm_header_gain gain = {0};
        assert(phg_begin(&gain,9,value) == PHG_OK && isfinite(gain.factor) && gain.factor > previous);
        previous = gain.factor;
        for (unsigned format = PHG_PCM_U8; format <= PHG_PCM_S32LE; ++format) {
            uint8_t silence[8] = {0}, before[8] = {0};
            unsigned width = phg_width((pcm_header_gain_format)format);
            if (format == PHG_PCM_U8) silence[0] = silence[1] = 128;
            memcpy(before,silence,sizeof(silence));
            assert(phg_apply(&gain,9,(pcm_header_gain_format)format,2,silence,width*2u,0,width*2u) == PHG_OK);
            assert(!memcmp(silence,before,sizeof(silence)));
        }
        phg_reset(&gain);
    }
    assert(power_calls == calls + 65535);
    printf("{\"group\":\"full_gain_range\",\"factors\":65536,\"silent_span_applications\":327680,"
           "\"pow_calls\":65535,\"finite_positive_monotone\":true,\"passed\":true}\n");
}

static void identity_and_ties(void)
{
    const unsigned channels[] = {1,2,3,255};
    pcm_header_gain gain = {0};
    unsigned calls = power_calls;
    assert(phg_begin(&gain,7,0) == PHG_OK && gain.factor == 1.0 && power_calls == calls);
    for (unsigned format = PHG_PCM_U8; format <= PHG_PCM_S32LE; ++format)
    for (unsigned c = 0; c < sizeof(channels)/sizeof(channels[0]); ++c) {
        uint8_t storage[4096], before[4096];
        for (unsigned i = 0; i < sizeof(storage); ++i) storage[i] = (uint8_t)(i*73u+11u);
        memcpy(before,storage,sizeof(storage));
        size_t frame=(size_t)channels[c]*phg_width((pcm_header_gain_format)format);
        assert(phg_apply(&gain,7,(pcm_header_gain_format)format,(uint8_t)channels[c],storage+1,3*frame,frame,frame) == PHG_OK);
        assert(!memcmp(storage,before,sizeof(storage)) && power_calls == calls);
        assert(phg_apply(&gain,7,(pcm_header_gain_format)format,(uint8_t)channels[c],NULL,0,0,0) == PHG_OK);
        ++identity_cases;
    }
    phg_reset(&gain);
    power_mode=5;
    assert(phg_begin(&gain,8,1) == PHG_OK); /* Controlled exact factor0.5. */
    uint8_t ties[] = {1,0,255,255,3,0,253,255};
    const uint8_t expected[] = {1,0,255,255,2,0,254,255};
    assert(phg_apply(&gain,8,PHG_PCM_S16LE,1,ties,sizeof(ties),0,sizeof(ties)) == PHG_OK);
    assert(!memcmp(ties,expected,sizeof(ties)));
    phg_reset(&gain);power_mode=0;
    assert(phg_begin(&gain,8,1)==PHG_OK);
    gain.factor=DBL_MAX; /* Owned-state corruption guard, not a legal header factor. */
    const uint8_t peaks[5][12]={
        {128,255,0}, {0,127,128}, {0,0,255,127,0,128},
        {0,0,0,255,255,127,0,0,128}, {0,0,0,0,255,255,255,127,0,0,0,128}
    };
    for(unsigned format=PHG_PCM_U8;format<=PHG_PCM_S32LE;++format) {
        uint8_t values[12];memcpy(values,peaks[format],sizeof(values));
        size_t n=3u*phg_width((pcm_header_gain_format)format);
        assert(phg_apply(&gain,8,(pcm_header_gain_format)format,1,values,n,0,n)==PHG_OK);
        assert(!memcmp(values,peaks[format],sizeof(values)));++overflow_cases;
    }
    phg_reset(&gain);
}

static void refused(pcm_header_gain *gain,uint32_t generation,pcm_header_gain_format format,
                    uint8_t channels,uint8_t *data,size_t total,size_t offset,size_t bytes,
                    pcm_header_gain_status expected)
{
    uint8_t before[16];
    pcm_header_gain saved;
    if (gain) memcpy(&saved,gain,sizeof(saved));
    if (data) memcpy(before,data,sizeof(before));
    unsigned calls=power_calls;
    assert(phg_apply(gain,generation,format,channels,data,total,offset,bytes) == expected);
    if (gain) assert(!memcmp(gain,&saved,sizeof(saved)));
    if (data) assert(!memcmp(before,data,sizeof(before)));
    assert(power_calls == calls);++refusal_cases;
}

static void transactions_and_reuse(void)
{
    pcm_header_gain gain = {0};uint8_t data[16];memset(data,0x7f,sizeof(data));
    refused(&gain,1,PHG_PCM_S16LE,1,data,sizeof(data),0,sizeof(data),PHG_INVALID);
    assert(phg_begin(NULL,1,1) == PHG_INVALID);
    assert(phg_begin(&gain,1,INT16_MIN-1) == PHG_INVALID);
    assert(phg_begin(&gain,1,INT16_MAX+1) == PHG_INVALID);
    for (unsigned mode=1; mode<=4; ++mode) {
        pcm_header_gain saved=gain;power_mode=mode;
        assert(phg_begin(&gain,1,1) == PHG_MATH && !memcmp(&gain,&saved,sizeof(gain)));
    }
    power_mode=0;assert(phg_begin(&gain,1,1536) == PHG_OK);
    pcm_header_gain saved=gain;unsigned calls=power_calls;
    assert(phg_begin(&gain,2,-1536) == PHG_INVALID && !memcmp(&gain,&saved,sizeof(gain)) && power_calls==calls);
    refused(NULL,1,PHG_PCM_S16LE,1,data,16,0,16,PHG_INVALID);
    refused(&gain,2,PHG_PCM_S16LE,1,data,16,0,16,PHG_INVALID);
    refused(&gain,1,(pcm_header_gain_format)99,1,data,16,0,16,PHG_INVALID);
    refused(&gain,1,PHG_PCM_S16LE,0,data,16,0,16,PHG_INVALID);
    refused(&gain,1,PHG_PCM_S16LE,1,NULL,16,0,16,PHG_INVALID);
    refused(&gain,1,PHG_PCM_S16LE,1,data,16,17,0,PHG_INVALID);
    refused(&gain,1,PHG_PCM_S16LE,1,data,16,4,13,PHG_INVALID);
    refused(&gain,1,PHG_PCM_S16LE,1,data,16,SIZE_MAX,4,PHG_INVALID);
    refused(&gain,1,PHG_PCM_S16LE,2,data,15,0,4,PHG_UNALIGNED);
    refused(&gain,1,PHG_PCM_S16LE,2,data,16,2,4,PHG_UNALIGNED);
    refused(&gain,1,PHG_PCM_S16LE,2,data,16,4,2,PHG_UNALIGNED);
    const double invalid_factors[]={NAN,INFINITY,-INFINITY,0,-1};
    for (unsigned i=0;i<sizeof(invalid_factors)/sizeof(invalid_factors[0]);++i) {
        gain.factor=invalid_factors[i];
        refused(&gain,1,PHG_PCM_S16LE,1,data,16,0,16,PHG_INVALID);
    }
    for (unsigned cycle=0;cycle<64;++cycle) {
        phg_reset(&gain);assert(!gain.active && !gain.factor);
        uint8_t sample[]={1,0};
        assert(phg_begin(&gain,cycle,cycle&1u?1536:-1536) == PHG_OK);
        refused(&gain,cycle+1,PHG_PCM_S16LE,1,data,16,0,16,PHG_INVALID);
        assert(phg_apply(&gain,cycle,PHG_PCM_S16LE,1,sample,sizeof(sample),0,sizeof(sample))==PHG_OK);
        assert(sample[0]==(cycle&1u?2:1) && !sample[1]);++reuse_cases;
    }
    phg_reset(&gain);phg_reset(NULL);
}

static void creator_observation(void)
{
    int error=0;OpusEncoder *encoder=opus_encoder_create(48000,2,OPUS_APPLICATION_AUDIO,&error);
    assert(encoder && error==OPUS_OK);
    opus_int16 input[960*2];
    for(unsigned i=0;i<960;++i)input[2*i]=input[2*i+1]=(opus_int16)(6000*sin((double)i*0.08));
    unsigned char packet[4000];int bytes=opus_encode(encoder,input,960,packet,sizeof(packet));
    assert(bytes>0);opus_encoder_destroy(encoder);
    const int gains[]={INT16_MIN,-1536,-256,-1,0,1,256,1536,INT16_MAX};
    for(unsigned g=0;g<sizeof(gains)/sizeof(gains[0]);++g) {
        OpusDecoder *plain=opus_decoder_create(48000,2,&error);assert(plain && !error);
        OpusDecoder *adjusted=opus_decoder_create(48000,2,&error);assert(adjusted && !error);
        assert(opus_decoder_ctl(adjusted,OPUS_SET_GAIN(gains[g]))==OPUS_OK);
        int actual=0;assert(opus_decoder_ctl(adjusted,OPUS_GET_GAIN(&actual))==OPUS_OK && actual==gains[g]);
        float baseline[960*2],with_gain[960*2];
        assert(opus_decode_float(plain,packet,bytes,baseline,960,0)==960 &&
               opus_decode_float(adjusted,packet,bytes,with_gain,960,0)==960);
        pcm_header_gain gain={0};assert(phg_begin(&gain,1,gains[g])==PHG_OK);
        double max_difference=0,max_reference=0,energy=0;unsigned differing=0;
        for(unsigned i=0;i<960*2;++i) {
            assert(isfinite(baseline[i]) && isfinite(with_gain[i]));
            double expected=(double)baseline[i]*gain.factor;
            double difference=fabs((double)with_gain[i]-expected);
            if(difference>max_difference)max_difference=difference;
            if(fabs(expected)>max_reference)max_reference=fabs(expected);
            energy+=difference*difference;differing+=difference!=0;
        }
        printf("{\"creator\":\"%s\",\"gain_q8\":%d,\"samples\":1920,\"factor\":%.17g,"
               "\"max_absolute_difference\":%.17g,\"max_reference_magnitude\":%.17g,"
               "\"difference_energy\":%.17g,\"differing_samples\":%u,"
               "\"numerical_acceptance_bound\":null,\"numeric_conformance_claim\":false,\"passed\":true}\n",
               opus_get_version_string(),gains[g],gain.factor,max_difference,max_reference,energy,differing);
        phg_reset(&gain);opus_decoder_destroy(plain);opus_decoder_destroy(adjusted);
    }
}

int main(void)
{
    selected_vectors();full_gain_range();identity_and_ties();transactions_and_reuse();creator_observation();
    printf("{\"suite\":\"pcm-header-gain-host\",\"reference_vectors\":%zu,\"vector_applications\":%u,"
           "\"identity_cases\":%u,\"refusal_cases\":%u,\"reuse_cases\":%u,"
           "\"overflow_guard_cases\":%u,"
           "\"creator_observations\":9,\"rounding\":\"nearest_ties_away_from_zero\","
           "\"production_integrated\":false,\"passed\":true}\n",
           sizeof(gain_vectors)/sizeof(gain_vectors[0]),vector_applications,identity_cases,refusal_cases,reuse_cases,overflow_cases);
    return 0;
}
