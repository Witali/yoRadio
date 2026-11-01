/* Complete public encoder packets from synthetic audio, with observed TOCs. */
#include "opus_packet_modes_public.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void put32(FILE *f,uint32_t n) {
    unsigned char b[4];for(unsigned i=0;i<4;++i)b[i]=(unsigned char)(n>>(i*8));
    assert(fwrite(b,1,4,f)==4);
}
int main(int argc,char **argv) {
    assert(argc==7);
    int mode=atoi(argv[1]),samples=atoi(argv[2]),vbr=atoi(argv[3]),count=atoi(argv[4]);
    int channels=mode==2?2:1,error=0,delay=0;
    assert(mode>=0 && mode<=2 && samples>=120 && samples<=2880 && count>=4 && count<=192);
    int app=mode==2?PM_APPLICATION_RESTRICTED_LOWDELAY:PM_APPLICATION_VOIP;
    OpusEncoder *e=opus_encoder_create(48000,channels,app,&error);assert(e && !error);
    assert(opus_encoder_ctl(e,PM_SET_BITRATE,mode==0?12000:mode==1?24000:128000)==0);
    assert(opus_encoder_ctl(e,PM_SET_VBR,vbr)==0);
    assert(opus_encoder_ctl(e,PM_SET_BANDWIDTH,mode==0?PM_BANDWIDTH_WIDEBAND:
        mode==1?PM_BANDWIDTH_SUPERWIDEBAND:PM_BANDWIDTH_FULLBAND)==0);
    if(mode<2)assert(opus_encoder_ctl(e,PM_SET_SIGNAL,PM_SIGNAL_VOICE)==0);
    assert(opus_encoder_ctl(e,PM_GET_LOOKAHEAD,&delay)==0 && delay>=0);
    int total=samples*count,logical=total-delay-13;assert(logical>0);
    int signal_frames=logical<total*3/4?logical:total*3/4;
    FILE *f=fopen(argv[5],"wb"),*metadata=fopen(argv[6],"w");assert(f && metadata);
    assert(fwrite("OPMODE1\0",1,8,f)==8);
    put32(f,(unsigned)channels);put32(f,(unsigned)delay);put32(f,(unsigned)logical);
    put32(f,(unsigned)count);put32(f,(unsigned)samples);
    float pcm[2880*2];unsigned char packet[61440];unsigned configs[32]={0},codes[4]={0};
    for(int n=0;n<count;++n) {
        for(int at=0;at<samples;++at)for(int c=0;c<channels;++c) {
            int pos=n*samples+at;
            double envelope=((pos/137)%5+1)*0.012;
            /* A complete final quarter is real encoded silence, distinct
             * from the absent coded frames inserted by the RFC reframer. */
            double x=pos<signal_frames?envelope*(sin(6.2831853071795864769*(187+59*c)*pos/48000.0)+
                0.3*sin(6.2831853071795864769*977*pos/48000.0)):0;
            pcm[at*channels+c]=(float)x;
        }
        int bytes=opus_encode_float(e,pcm,samples,packet,sizeof(packet));assert(bytes>0 && bytes<=61440);
        int config=packet[0]>>3,observed=config<12?0:config<16?1:2;
        if(observed!=mode){fprintf(stderr,"unexpected observed mode requested=%d observed=%d config=%d packet=%d\n",mode,observed,config,n);abort();}
        assert(opus_packet_get_nb_samples(packet,bytes,48000)==samples);
        put32(f,(unsigned)bytes);assert(fwrite(packet,1,(size_t)bytes,f)==(size_t)bytes);
        ++configs[config];++codes[packet[0]&3];
        fprintf(metadata,"{\"packet\":%d,\"bytes\":%d,\"toc\":%u,\"config\":%d,\"mode\":%d,\"code\":%u,\"samples\":%d,\"frames\":%d}\n",
            n,bytes,packet[0],config,observed,packet[0]&3,samples,opus_packet_get_nb_frames(packet,bytes));
    }
    assert(!fclose(f) && !fclose(metadata));opus_encoder_destroy(e);
    printf("{\"libopus\":\"%s\",\"mode\":%d,\"channels\":%d,\"pre_skip\":%d,\"logical_frames\":%d,\"packets\":%d,\"packet_samples\":%d,\"vbr\":%d,\"input_signal_frames\":%d,\"input_silent_frames\":%d,\"configs\":[",
        opus_get_version_string(),mode,channels,delay,logical,count,samples,vbr,signal_frames,total-signal_frames);
    for(unsigned i=0;i<32;++i)printf("%s%u",i?",":"",configs[i]);
    printf("],\"codes\":[%u,%u,%u,%u],\"private_abi_used\":false}\n",codes[0],codes[1],codes[2],codes[3]);
    return 0;
}
