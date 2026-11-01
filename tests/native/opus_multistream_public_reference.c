/* Framing oracle: opaque public creator single-stream and multistream decoders. */
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "opus_family1_public.h"
typedef struct OpusDecoder OpusDecoder;
extern OpusDecoder *opus_decoder_create(int32_t,int,int *);
extern int opus_decode_float(OpusDecoder *,const unsigned char *,int32_t,float *,int,int);
extern void opus_decoder_destroy(OpusDecoder *);
static uint32_t le32(const unsigned char *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void exact(FILE *f,void *p,size_t n){assert(fread(p,1,n,f)==n);}
static int16_t round16(double value){double x=value*32768.0;return x>32767?32767:x<-32768?-32768:(int16_t)llround(x);}
int main(int argc,char **argv) {
    assert(argc==3);const uint16_t endian=1;assert(*(const unsigned char *)&endian==1);
    FILE *f=fopen(argv[1],"rb");assert(f);unsigned char head[40];exact(f,head,40);assert(!memcmp(head,"MSPUB01\0",8));
    unsigned channels=le32(head+8),streams=le32(head+12),coupled=le32(head+16),packets=le32(head+28);
    assert((channels==3 || channels==6 || channels==8) && streams+coupled==channels && streams<=5 && packets==11);
    int error=0;OpusMSDecoder *multi=opus_multistream_decoder_create(48000,(int)channels,(int)streams,(int)coupled,head+32,&error);assert(multi && !error);
    OpusDecoder *single[5]={0};FILE *output[5]={0};uint64_t frame_counts[5]={0};
    for(unsigned s=0;s<streams;++s) {
        single[s]=opus_decoder_create(48000,s<coupled?2:1,&error);assert(single[s] && !error);
        char path[4096];int n=snprintf(path,sizeof(path),"%s-stream%u.pcm",argv[2],s);assert(n>0 && (unsigned)n<sizeof(path));output[s]=fopen(path,"wb");assert(output[s]);
    }
    char mapped_path[4096];int n=snprintf(mapped_path,sizeof(mapped_path),"%s-mapped.pcm",argv[2]);assert(n>0 && (unsigned)n<sizeof(mapped_path));
    FILE *mapped_file=fopen(mapped_path,"wb");assert(mapped_file);double max_delta=0;uint64_t frames=0;
    float multi_pcm[5760*8],single_pcm[5760*2],columns[5760*8];int16_t pcm[5760*8];
    for(unsigned id=0;id<packets;++id) {
        unsigned char length[4];exact(f,length,4);uint32_t bytes=le32(length);assert(bytes && bytes<=61440);
        unsigned char *packet=malloc(bytes);assert(packet);exact(f,packet,bytes);
        assert(opus_multistream_decode_float(multi,packet,(int32_t)bytes,multi_pcm,5760,0)==960);unsigned offset=0;
        for(unsigned s=0;s<streams;++s) {
            unsigned char desc[16];exact(f,desc,16);unsigned begin=le32(desc),original_bytes=le32(desc+4),common_bytes=le32(desc+8),delimited=le32(desc+12);
            assert(begin==offset && original_bytes && common_bytes && original_bytes<=61440 && common_bytes<=original_bytes && delimited==(s+1<streams));
            unsigned char *original=malloc(original_bytes),*common=malloc(common_bytes);assert(original && common);
            exact(f,original,original_bytes);exact(f,common,common_bytes);assert(begin+original_bytes<=bytes && !memcmp(original,packet+begin,original_bytes));
            unsigned width=s<coupled?2:1,first=s<coupled?2*s:s+coupled;
            assert(opus_decode_float(single[s],common,(int32_t)common_bytes,single_pcm,5760,0)==960);
            for(unsigned i=0;i<960;++i)for(unsigned ch=0;ch<width;++ch) {
                float value=single_pcm[i*width+ch];assert(isfinite(value));columns[i*channels+first+ch]=value;pcm[i*width+ch]=round16(value);
            }
            assert(fwrite(pcm,sizeof(int16_t),960*width,output[s])==960*width);frame_counts[s]+=960;offset+=original_bytes;free(original);free(common);
        }
        assert(offset==bytes);free(packet);
        for(unsigned i=0;i<960;++i)for(unsigned ch=0;ch<channels;++ch) {
            unsigned index=head[32+ch];assert(index<channels);double value=columns[i*channels+index],delta=fabs(value-multi_pcm[i*channels+ch]);
            if(delta>max_delta)max_delta=delta;
            pcm[i*channels+ch]=round16(value);
        }
        assert(fwrite(pcm,sizeof(int16_t),960*channels,mapped_file)==960*channels);frames+=960;
    }
    assert(fgetc(f)==EOF && !ferror(f) && !fclose(f) && !fclose(mapped_file) && max_delta==0 && frames==10560);
    opus_multistream_decoder_destroy(multi);for(unsigned s=0;s<streams;++s){assert(frame_counts[s]==10560 && !fclose(output[s]));opus_decoder_destroy(single[s]);}
    printf("{\"creator\":\"%s\",\"channels\":%u,\"streams\":%u,\"packets\":%u,\"frames_per_stream\":%" PRIu64
        ",\"maximum_mapped_float_difference\":%.17g,\"exact_creator_multistream_match\":true,\"private_abi_used\":false}\n",
        opus_get_version_string(),channels,streams,packets,frames,max_delta);return 0;
}
