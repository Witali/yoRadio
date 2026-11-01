/* Independent creator public multistream float decode, then documented stereo matrix.
 * RFC7845 section5.1.1.5 figures4,7,9. Every encoded speaker contributes to at least one side.
 */
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "opus_family1_public.h"
static uint32_t le32(const unsigned char *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void exact(FILE *f,void *p,size_t n){assert(fread(p,1,n,f)==n);}
static int16_t round16(double sample){double scaled=sample*32768.0;return scaled>32767?32767:scaled<-32768?-32768:(int16_t)llround(scaled);}
static void matrix(unsigned c,double m[2][8]) {
    double q=1/sqrt(2.0),s=sqrt(3.0)/2,n;
    memset(m,0,16*sizeof(double));
    if(c==3){n=1/(1+q);m[0][0]=m[1][2]=n;m[0][1]=m[1][1]=n*q;}
    else if(c==6){
        n=2/(1+2*q+s+0.5);double a[2][6]={{1,q,0,s,0.5,q},{0,q,1,0.5,s,q}};
        for(unsigned side=0;side<2;++side)for(unsigned i=0;i<c;++i)m[side][i]=a[side][i]*n;
    } else {
        assert(c==8);n=2/(2+2*q+sqrt(3.0));
        double a[2][8]={{1,q,0,s,0.5,s,0.5,q},{0,q,1,0.5,s,0.5,s,q}};
        for(unsigned side=0;side<2;++side)for(unsigned i=0;i<c;++i)m[side][i]=a[side][i]*n;
    }
    for(unsigned i=0;i<c;++i)assert(m[0][i]!=0 || m[1][i]!=0);
}
int main(int argc,char **argv) {
    assert(argc==5);const uint16_t endian=1;assert(*(const unsigned char *)&endian==1);
    FILE *f=fopen(argv[1],"rb");assert(f);unsigned char head[40];exact(f,head,sizeof(head));assert(!memcmp(head,"OFAM101\0",8));
    unsigned channels=le32(head+8),streams=le32(head+12),coupled=le32(head+16),pre_skip=le32(head+20),
        input_frames=le32(head+24),packets=le32(head+28);
    assert((channels==3 || channels==6 || channels==8) && input_frames==9600 && packets==11 && pre_skip<960);
    int error=0;OpusMSDecoder *decoder=opus_multistream_decoder_create(48000,(int)channels,(int)streams,(int)coupled,head+32,&error);assert(decoder && !error);
    FILE *raw_file=fopen(argv[2],"wb"),*stereo=fopen(argv[3],"wb"),*trim=fopen(argv[4],"wb");assert(raw_file && stereo && trim);
    double m[2][8];matrix(channels,m);float raw[5760*8];int16_t pcm[5760*8],downmix[5760*2];
    double energy[8]={0},contribution[8]={0};uint64_t raw_frames=0,trim_frames=0;unsigned clips=0;
    for(unsigned id=0;id<packets;++id) {
        unsigned char size_bytes[4];exact(f,size_bytes,4);uint32_t n=le32(size_bytes);assert(n && n<=61440);
        unsigned char *packet=malloc(n);assert(packet);exact(f,packet,n);
        int frames=opus_multistream_decode_float(decoder,packet,(int32_t)n,raw,5760,0);free(packet);assert(frames==960);
        for(unsigned i=0;i<(unsigned)frames;++i) {
            for(unsigned ch=0;ch<channels;++ch) {
                double v=raw[i*channels+ch];assert(isfinite(v));energy[ch]+=v*v;
                pcm[i*channels+ch]=round16(v);contribution[ch]+=v*v*(m[0][ch]*m[0][ch]+m[1][ch]*m[1][ch]);
            }
            for(unsigned side=0;side<2;++side) {
                double v=0;for(unsigned ch=0;ch<channels;++ch)v+=raw[i*channels+ch]*m[side][ch];
                downmix[i*2+side]=round16(v);clips+=downmix[i*2+side]==32767 || downmix[i*2+side]==-32768;
            }
            if(raw_frames+i>=pre_skip && raw_frames+i<pre_skip+input_frames) {
                assert(fwrite(downmix+i*2,sizeof(int16_t),2,trim)==2);++trim_frames;
            }
        }
        assert(fwrite(pcm,sizeof(int16_t),(size_t)frames*channels,raw_file)==(size_t)frames*channels);
        assert(fwrite(downmix,sizeof(int16_t),(size_t)frames*2,stereo)==(size_t)frames*2);raw_frames+=(unsigned)frames;
    }
    assert(raw_frames==10560 && trim_frames==input_frames && fgetc(f)==EOF && !ferror(f));
    assert(!fclose(f) && !fclose(raw_file) && !fclose(stereo) && !fclose(trim));opus_multistream_decoder_destroy(decoder);
    printf("{\"libopus\":\"%s\",\"channels\":%u,\"packets\":%u,\"raw_frames\":%" PRIu64 ",\"trim_frames\":%" PRIu64
        ",\"matrix\":[",opus_get_version_string(),channels,packets,raw_frames,trim_frames);
    for(unsigned side=0;side<2;++side){printf("%s[",side?",":"");for(unsigned ch=0;ch<channels;++ch)printf("%s%.17g",ch?",":"",m[side][ch]);printf("]");}
    printf("],\"channel_energy\":[");for(unsigned ch=0;ch<channels;++ch){assert(energy[ch]>0);printf("%s%.17g",ch?",":"",energy[ch]);}
    printf("],\"channel_downmix_contribution_energy\":[");for(unsigned ch=0;ch<channels;++ch){assert(contribution[ch]>0);printf("%s%.17g",ch?",":"",contribution[ch]);}
    printf("],\"stereo_clips\":%u,\"rounding\":\"nearest_ties_away_from_zero_then_clip\",\"numeric_conformance_claim\":false}\n",clips);return 0;
}
