/* Creator public surround encoder; packet transport has no Ogg implementation. */
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "opus_family1_public.h"
static void put32(FILE *f,uint32_t value) {
    unsigned char p[4];for(unsigned i=0;i<4;++i)p[i]=(unsigned char)(value>>(8*i));assert(fwrite(p,1,4,f)==4);
}
int main(int argc,char **argv) {
    assert(argc==3);int channels=atoi(argv[1]);assert(channels==3 || channels==6 || channels==8);
    int error=0,streams=0,coupled=0,delay=0;unsigned char mapping[8]={0};
    OpusMSEncoder *encoder=opus_multistream_surround_encoder_create(48000,channels,1,&streams,&coupled,mapping,
        PUBLIC_OPUS_APPLICATION_AUDIO,&error);assert(encoder && !error);
    assert(opus_multistream_encoder_ctl(encoder,PUBLIC_OPUS_SET_BITRATE_REQUEST,channels*64000)==0);
    assert(opus_multistream_encoder_ctl(encoder,PUBLIC_OPUS_GET_LOOKAHEAD_REQUEST,&delay)==0 && delay>0 && delay<960);
    const unsigned input_frames=9600,packet_frames=960,packets=(input_frames+(unsigned)delay+packet_frames-1)/packet_frames;
    FILE *f=fopen(argv[2],"wb");assert(f);assert(fwrite("OFAM101\0",1,8,f)==8);
    put32(f,(unsigned)channels);put32(f,(unsigned)streams);put32(f,(unsigned)coupled);put32(f,(unsigned)delay);
    put32(f,input_frames);put32(f,packets);assert(fwrite(mapping,1,8,f)==8);
    float pcm[960*8];unsigned char packet[61440];double energy[8]={0};
    const unsigned frequencies[8]={211,337,463,593,719,853,983,1109};
    for(unsigned frame=0;frame<packets;++frame) {
        for(unsigned i=0;i<packet_frames;++i)for(int channel=0;channel<channels;++channel) {
            unsigned at=frame*packet_frames+i;
            unsigned hz=channel==channels-1 && channels>=6 ? 73:frequencies[channel];
            double sample=at<input_frames ? (0.035+0.003*channel)*sin(6.2831853071795864769*hz*at/48000.0+0.17*channel):0;
            pcm[i*(unsigned)channels+(unsigned)channel]=(float)sample;energy[channel]+=sample*sample;
        }
        int n=opus_multistream_encode_float(encoder,pcm,(int)packet_frames,packet,sizeof(packet));assert(n>0 && n<=61440);
        put32(f,(unsigned)n);assert(fwrite(packet,1,(size_t)n,f)==(size_t)n);
    }
    assert(!fclose(f));opus_multistream_encoder_destroy(encoder);
    printf("{\"libopus\":\"%s\",\"channels\":%d,\"streams\":%d,\"coupled\":%d,\"pre_skip\":%d,\"input_frames\":%u,\"packets\":%u,\"mapping\":[",
        opus_get_version_string(),channels,streams,coupled,delay,input_frames,packets);
    for(int i=0;i<channels;++i)printf("%s%u",i?",":"",mapping[i]);
    printf("],\"input_channel_energy\":[");for(int i=0;i<channels;++i){assert(energy[i]>0);printf("%s%.17g",i?",":"",energy[i]);}
    printf("],\"private_abi_used\":false}\n");return 0;
}
