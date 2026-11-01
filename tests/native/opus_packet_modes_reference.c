/* Independent complete-packet synthesis through opaque creator public APIs. */
#include "opus_packet_modes_public.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t le32(const unsigned char *p) {
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
static void exact(FILE *f,void *data,size_t bytes) { assert(fread(data,1,bytes,f)==bytes); }
static void pcm(FILE *f,const int16_t *samples,size_t count) {
    for(size_t i=0;i<count;++i) {
        uint16_t value=(uint16_t)samples[i];unsigned char b[2]={(unsigned char)value,(unsigned char)(value>>8)};
        assert(fwrite(b,1,2,f)==2);
    }
}
static void same_frames(const unsigned char *a,int na,const unsigned char *b,int nb) {
    const unsigned char *fa[48],*fb[48];int16_t sa[48],sb[48];unsigned char ta,tb;int oa,ob;
    int ca=opus_packet_parse(a,na,&ta,fa,sa,&oa),cb=opus_packet_parse(b,nb,&tb,fb,sb,&ob);
    assert(ca>0 && ca==cb && (ta&252)==(tb&252));
    for(int i=0;i<ca;++i)assert(sa[i]==sb[i] && !memcmp(fa[i],fb[i],(size_t)sa[i]));
}
int main(int argc,char **argv) {
    assert(argc==5);FILE *input=fopen(argv[1],"rb"),*raw=fopen(argv[2],"wb"),*trim=fopen(argv[3],"wb"),*metadata=fopen(argv[4],"w");
    assert(input && raw && trim && metadata);unsigned char head[28];exact(input,head,sizeof(head));assert(!memcmp(head,"OPMODE1\0",8));
    unsigned channels=le32(head+8),skip=le32(head+12),logical=le32(head+16),packets=le32(head+20);
    assert((channels==1 || channels==2) && packets && packets<=192);
    OpusDecoder *decoder[3];int error=0;
    for(unsigned i=0;i<3;++i){decoder[i]=opus_decoder_create(48000,(int)channels,&error);assert(decoder[i] && !error);}
    OpusRepacketizer *rp=opus_repacketizer_create();assert(rp);
    unsigned char packet[65536],repacked[65536],padded[65536];int16_t output[3][5760*2];
    uint64_t total=0,trim_frames=0,nonzero=0,zero_frames=0;double energy=0;
    for(unsigned n=0;n<packets;++n) {
        unsigned char size[4];exact(input,size,4);unsigned bytes=le32(size);assert(bytes && bytes<=61440);exact(input,packet,bytes);
        const unsigned char *frames[48];int16_t sizes[48];unsigned char toc=0;int offset=0;
        int count=opus_packet_parse(packet,(int32_t)bytes,&toc,frames,sizes,&offset);assert(count>0 && count<=48);
        int samples=opus_packet_get_nb_samples(packet,(int32_t)bytes,48000);
        assert(samples>0 && samples<=5760 && opus_packet_get_nb_frames(packet,(int32_t)bytes)==count &&
            opus_packet_get_samples_per_frame(packet,48000)*count==samples);
        unsigned zeros=0;for(int i=0;i<count;++i){assert(sizes[i]>=0 && sizes[i]<=1275);zeros+=(sizes[i]==0);}
        zero_frames+=zeros;
        assert(opus_repacketizer_init(rp)==rp && opus_repacketizer_cat(rp,packet,(int32_t)bytes)==0);
        int nr=opus_repacketizer_out(rp,repacked,sizeof(repacked));assert(nr>0);same_frames(packet,(int)bytes,repacked,nr);
        memcpy(padded,packet,bytes);assert(opus_packet_pad(padded,(int32_t)bytes,(int32_t)bytes+513)==0);
        same_frames(packet,(int)bytes,padded,(int)bytes+513);
        int np=opus_packet_unpad(padded,(int32_t)bytes+513);assert(np>0);same_frames(packet,(int)bytes,padded,np);
        assert(opus_decode(decoder[0],packet,(int32_t)bytes,output[0],5760,0)==samples);
        assert(opus_decode(decoder[1],repacked,nr,output[1],5760,0)==samples);
        assert(opus_decode(decoder[2],padded,np,output[2],5760,0)==samples);
        assert(!memcmp(output[0],output[1],(size_t)samples*channels*2) &&
               !memcmp(output[0],output[2],(size_t)samples*channels*2));
        pcm(raw,output[0],(size_t)samples*channels);
        uint64_t first=total<skip?skip:total,last=total+(unsigned)samples;
        if(last>(uint64_t)skip+logical)last=(uint64_t)skip+logical;
        if(last>first){pcm(trim,output[0]+(first-total)*channels,(size_t)(last-first)*channels);trim_frames+=last-first;}
        for(int i=0;i<samples*(int)channels;++i){double x=output[0][i];nonzero+=(x!=0);energy+=x*x;}
        fprintf(metadata,"{\"packet\":%u,\"bytes\":%u,\"toc\":%u,\"config\":%u,\"code\":%u,\"channels\":%d,\"frames\":%d,\"samples\":%d,\"zero_frames\":%u,\"sizes\":[",
            n,bytes,toc,toc>>3,toc&3,opus_packet_get_nb_channels(packet),count,samples,zeros);
        for(int i=0;i<count;++i)fprintf(metadata,"%s%d",i?",":"",sizes[i]);
        fprintf(metadata,"],\"repacketize_pad_unpad_frames_exact\":true,\"decoded_pcm_exact\":true}\n");
        total+=(unsigned)samples;
    }
    assert(fgetc(input)==EOF && !ferror(input) && trim_frames==logical && total==(uint64_t)skip+logical+13 && nonzero && energy>0);
    assert(!fclose(input) && !fclose(raw) && !fclose(trim) && !fclose(metadata));
    for(unsigned i=0;i<3;++i){opus_decoder_destroy(decoder[i]);}
    opus_repacketizer_destroy(rp);
    printf("{\"libopus\":\"%s\",\"channels\":%u,\"packets\":%u,\"raw_frames\":%" PRIu64 ",\"pre_skip\":%u,\"logical_frames\":%u,\"raw_bytes\":%" PRIu64 ",\"trim_bytes\":%" PRIu64 ",\"zero_length_coded_frames\":%" PRIu64 ",\"nonzero_samples\":%" PRIu64 ",\"energy\":%.17g,\"three_full_decodes_exact\":true,\"private_abi_used\":false}\n",
        opus_get_version_string(),channels,packets,total,skip,logical,total*channels*2,(uint64_t)logical*channels*2,zero_frames,nonzero,energy);
    return 0;
}
