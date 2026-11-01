/* Host-only public raw libopus float decode followed by RFC 7845 header gain. */
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct OpusDecoder OpusDecoder;
extern OpusDecoder *opus_decoder_create(int32_t,int,int *);
extern int opus_decode_float(OpusDecoder *,const unsigned char *,int32_t,float *,int,int);
extern int opus_packet_get_nb_samples(const unsigned char *,int32_t,int32_t);
extern void opus_decoder_destroy(OpusDecoder *);
extern const char *opus_get_version_string(void);
static uint32_t le32(const unsigned char *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint64_t le64(const unsigned char *p){return (uint64_t)le32(p)|(uint64_t)le32(p+4)<<32;}
static void exact(FILE *f,void *p,size_t n){assert(fread(p,1,n,f)==n);}
int main(int argc,char **argv){
    assert(argc==3);const uint16_t endian=1;assert(*(const unsigned char *)&endian==1);
    FILE *f=fopen(argv[1],"rb");assert(f);unsigned char head[32];exact(f,head,sizeof(head));
    assert(!memcmp(head,"OGAIN01\0",8) && le32(head+8)==48000 && le32(head+12)==2);
    uint64_t expected_frames=le64(head+16);uint32_t packets=le32(head+24),encoded_gain=le32(head+28);
    int64_t gain_q8=encoded_gain<=INT32_MAX ? (int64_t)encoded_gain:(int64_t)encoded_gain-INT64_C(4294967296);
    assert(expected_frames==528960 && packets==551 && (gain_q8==0 || gain_q8==1536 || gain_q8==-1536));
    double factor=pow(10.0,(double)gain_q8/(20.0*256.0));
    int error=0;OpusDecoder *decoder=opus_decoder_create(48000,2,&error);assert(decoder && !error);
    FILE *output=fopen(argv[2],"wb");assert(output);
    float raw[5760*2];int16_t pcm[5760*2];
    uint64_t frames=0,energy=0,absolute=0,nonzero=0,clips=0;uint32_t peak=0;
    double raw_peak=0,raw_energy=0;
    for(uint32_t i=0;i<packets;++i){
        unsigned char size_bytes[4];exact(f,size_bytes,4);uint32_t n=le32(size_bytes);assert(n && n<=65536);
        unsigned char *packet=malloc(n);assert(packet);exact(f,packet,n);
        int expected=opus_packet_get_nb_samples(packet,(int32_t)n,48000);assert(expected>0 && expected<=5760);
        int decoded=opus_decode_float(decoder,packet,(int32_t)n,raw,5760,0);free(packet);assert(decoded==expected);
        frames+=(unsigned)decoded;assert(frames<=expected_frames);
        for(unsigned j=0;j<(unsigned)decoded*2;++j){
            double value=raw[j];assert(isfinite(value));raw_energy+=value*value;
            if(fabs(value)>raw_peak)raw_peak=fabs(value);
            double scaled=value*32768.0*factor;
            int64_t sample=scaled>32767.0 ? 32767:scaled<-32768.0 ? -32768:llround(scaled);
            assert(sample>=-32768 && sample<=32767);pcm[j]=(int16_t)sample;
            uint32_t magnitude=(uint32_t)(sample<0 ? -sample:sample);
            energy+=(uint64_t)(sample*sample);absolute+=magnitude;nonzero+=sample!=0;clips+=sample==-32768 || sample==32767;
            if(magnitude>peak)peak=magnitude;
        }
        assert(fwrite(pcm,sizeof(*pcm),(unsigned)decoded*2,output)==(unsigned)decoded*2);
    }
    assert(frames==expected_frames && fgetc(f)==EOF && !ferror(f) && !fclose(f) && !fclose(output));
    opus_decoder_destroy(decoder);
    printf("{\"reference\":\"%s\",\"gain_q8\":%" PRId64 ",\"factor\":%.17g,\"packets\":%" PRIu32
           ",\"raw_frames\":%" PRIu64 ",\"pcm_bytes\":%" PRIu64 ",\"energy\":%" PRIu64
           ",\"absolute\":%" PRIu64 ",\"nonzero\":%" PRIu64 ",\"clips\":%" PRIu64 ",\"peak\":%" PRIu32
           ",\"raw_float_peak\":%.17g,\"raw_float_energy\":%.17g,\"rounding\":\"nearest_ties_away_from_zero_then_clip\","
           "\"library_header_gain_used\":false,\"numeric_conformance_claim\":false}\n",
           opus_get_version_string(),gain_q8,factor,packets,frames,frames*4,energy,absolute,nonzero,clips,peak,raw_peak,raw_energy);
    return 0;
}
