/* Exhaustive header bounds plus independent public creator differential tests. */
#include "opus_family1_mapping.h"
#include "opus_multistream_framing.h"
#include "opus_family1_public.h"
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct OpusDecoder OpusDecoder;
extern OpusDecoder *opus_decoder_create(int32_t,int,int *);
extern int opus_decode_float(OpusDecoder *,const unsigned char *,int32_t,float *,int,int);
extern void opus_decoder_destroy(OpusDecoder *);
static unsigned assertions;
#define CHECK(x) do {assert(x);++assertions;} while(0)
static void put16(uint8_t *p,int value){unsigned u=(unsigned)value&65535u;p[0]=(uint8_t)u;p[1]=(uint8_t)(u>>8);}
static void header(uint8_t head[40],unsigned c,unsigned n,unsigned m,const uint8_t *mapping) {
    memset(head,0,40);memcpy(head,"OpusHead",8);head[8]=15;head[9]=(uint8_t)c;head[12]=0x80;head[13]=0xbb;
    head[18]=1;head[19]=(uint8_t)n;head[20]=(uint8_t)m;memcpy(head+21,mapping,c);
}
static void check_views(const opus_family1_plan *plan) {
    uint8_t storage[8][17];of1_pcm_buffer buffers[8]={{0}};of1_channel_view views[8];
    for(unsigned slot=0;slot<plan->needed;++slot) {
        unsigned width=plan->stream_channels[slot],stream=plan->stream_id[slot];buffers[slot]=(of1_pcm_buffer){storage[slot]+1,4u*width*2u};
        unsigned first=stream<plan->coupled?stream*2u:stream+plan->coupled;
        for(unsigned frame=0;frame<4;++frame)for(unsigned ch=0;ch<width;++ch)put16(storage[slot]+1+(frame*width+ch)*2u,(int)(frame*1000u+first+ch+1u));
    }
    CHECK(of1_channel_views(plan,buffers,plan->needed,4,views)==OF1_OK);
    uint8_t out[32];size_t written=999;CHECK(of1_gather_s16(views,plan->channels,1,2,out,sizeof(out),&written)==OF1_OK);
    CHECK(written==2u*plan->channels*2u);
    for(unsigned frame=0;frame<2;++frame)for(unsigned speaker=0;speaker<plan->channels;++speaker) {
        unsigned expected=plan->map[speaker]==255?0:(frame+1u)*1000u+plan->map[speaker]+1u;
        unsigned at=(frame*plan->channels+speaker)*2u;CHECK(((unsigned)out[at]|(unsigned)out[at+1]<<8)==expected);
        if(plan->map[speaker]==255)CHECK(views[speaker].silence && !views[speaker].data);
        for(unsigned other=0;other<speaker;++other)if(plan->map[speaker]==plan->map[other])CHECK(views[speaker].data==views[other].data && views[speaker].stride==views[other].stride);
    }
}
static void header_boundaries(void) {
    uint64_t pairs=0,all_counts=0,indices=0;uint8_t head[40],map[8];opus_family1_plan plan;
    for(unsigned n=1;n<=255;++n)for(unsigned m=0;m<=n && n+m<=255;++m) {
        unsigned decoded=n+m;++pairs;
        for(unsigned c=1;c<=8;++c) {
            for(unsigned i=0;i<c;++i)map[i]=i%3u==2u?255u:(uint8_t)(i%2u?0:decoded-1u);
            header(head,c,n,m,map);CHECK(of1_plan_header(head,21u+c+3u,&plan)==OF1_OK);
            CHECK(plan.channels==c && plan.streams==n && plan.coupled==m && plan.needed<=c && plan.input_rate==48000);
            check_views(&plan);++all_counts;
        }
        for(unsigned index=0;index<decoded;++index) {
            map[0]=(uint8_t)index;header(head,1,n,m,map);CHECK(of1_plan_header(head,22,&plan)==OF1_OK);
            CHECK(plan.needed==1 && plan.speaker_slot[0]==0 && plan.stream_id[0]==(index<2*m?index/2:index-m) &&
                plan.stream_channels[0]==(index<2*m?2:1) && plan.speaker_channel[0]==(index<2*m?index%2:0));++indices;
        }
    }
    CHECK(pairs==16511 && all_counts==132088 && indices>2000000);
    memset(map,255,sizeof(map));header(head,8,255,0,map);put16(head+10,65535);put16(head+16,-32768);
    CHECK(of1_plan_header(head,29,&plan)==OF1_OK && plan.needed==0 && plan.pre_skip==65535 && plan.header_gain_q8==INT16_MIN);check_views(&plan);
    put16(head+16,32767);CHECK(of1_plan_header(head,29,&plan)==OF1_OK && plan.header_gain_q8==INT16_MAX);
    memset(&plan,0xa5,sizeof(plan));opus_family1_plan unchanged=plan;
    head[19]=0;CHECK(of1_plan_header(head,29,&plan)==OF1_INVALID && !memcmp(&plan,&unchanged,sizeof(plan)));head[19]=255;
    head[20]=1;CHECK(of1_plan_header(head,29,&plan)==OF1_INVALID);head[20]=0;
    head[8]=16;CHECK(of1_plan_header(head,29,&plan)==OF1_VERSION);head[8]=1;head[18]=2;CHECK(of1_plan_header(head,29,&plan)==OF1_OTHER_FAMILY);head[18]=1;
    head[9]=9;CHECK(of1_plan_header(head,30,&plan)==OF1_INVALID);head[9]=8;CHECK(of1_plan_header(head,28,&plan)==OF1_INVALID);
    map[0]=1;header(head,1,1,0,map);CHECK(of1_plan_header(head,22,&plan)==OF1_INVALID);
    printf("{\"suite\":\"headers-and-views\",\"valid_nm_pairs\":%" PRIu64 ",\"all_channel_counts\":%" PRIu64 ",\"all_decoded_indices\":%" PRIu64 "}\n",pairs,all_counts,indices);
}
static void framing_boundaries(void) {
    static const uint8_t examples[][16]={{0xf8,3,'a','b','c'},{0xf9,3,'a','b','c','d','e','f'},
        {0xfa,2,3,'A','B','x','y','z'},{0xfb,3,2,'a','b','c','d','e','f'},
        {0xfb,0x83,1,2,3,'A','B','C','D','E','F'},{0xfb,0x42,3,2,'a','b','c','d',0,0,0},{0xf8,0}};
    static const unsigned lengths[]={5,8,8,9,11,11,2},extra[]={1,1,1,1,1,1,1},frames[]={1,2,2,3,3,2,1};
    for(unsigned i=0;i<7;++i) {
        uint8_t packet[32];memcpy(packet,examples[i],lengths[i]);memset(packet+lengths[i],0xa5,8);opus_elementary_view view;
        CHECK(omf_element(packet,lengths[i]+8,true,&view)==OMF_OK && view.bytes==lengths[i] && view.extra_bytes==extra[i] && view.frames==frames[i]);
        uint8_t common[32];memcpy(common,packet,view.extra_offset);memcpy(common+view.extra_offset,packet+view.extra_offset+view.extra_bytes,view.bytes-view.extra_offset-view.extra_bytes);
        CHECK(omf_element(common,view.bytes-view.extra_bytes,false,&view)==OMF_OK && view.frames==frames[i]);
    }
    uint8_t packet[61441];for(unsigned i=0;i<254;++i){packet[2*i]=0xf8;packet[2*i+1]=0;}packet[508]=0xf8;
    uint8_t selected[8]={254,0,128,1,127,253,52,51};opus_elementary_view views[8];uint16_t samples=777;
    CHECK(omf_family01_packet(packet,509,255,selected,8,views,&samples)==OMF_OK && samples==960);
    for(unsigned i=0;i<8;++i)CHECK(views[i].data==packet+selected[i]*2u && views[i].bytes==(selected[i]==254?1u:2u));
    CHECK(omf_family01_packet(packet,509,255,NULL,0,NULL,&samples)==OMF_OK && samples==960);
    memset(views,0xa5,sizeof(views));opus_elementary_view unchanged[8];memcpy(unchanged,views,sizeof(views));samples=777;
    packet[2*17]=0xf0;CHECK(omf_family01_packet(packet,509,255,selected,8,views,&samples)==OMF_INVALID && samples==777 && !memcmp(views,unchanged,sizeof(views)));
    packet[2*17]=0xf8;packet[2*17+1]=3;CHECK(omf_family01_packet(packet,509,255,NULL,0,NULL,&samples)==OMF_INVALID);
    memset(packet,0,sizeof(packet));packet[0]=0xfb;packet[1]=0x41;memset(packet+2,255,240);packet[242]=237;
    CHECK(omf_family01_packet(packet,61440,1,NULL,0,NULL,&samples)==OMF_OK && samples==960);
    CHECK(omf_family01_packet(packet,61441,1,NULL,0,NULL,&samples)==OMF_PACKET_POLICY);
    CHECK(omf_family01_packet(NULL,61441,1,NULL,0,NULL,&samples)==OMF_INVALID);
    static const uint8_t invalid[][4]={{0xf8},{0xf8,255},{0xfb,0},{0xfb,49},{0xfb,7},{0xf9,1,2,3},{0xfa,5,1,2}};
    static const unsigned size[]={1,2,2,2,2,4,4};
    for(unsigned i=0;i<7;++i){opus_elementary_view out;CHECK(omf_element(invalid[i],size[i],i<5,&out)==OMF_INVALID);}
    puts("{\"suite\":\"framing-boundaries\",\"streams255\":true,\"unused_streams_validated\":true,\"packet61440\":true,\"policy61441\":true}");
}
static void view_boundaries(void) {
    uint8_t head[40],map[3]={0,2,1},a[17]={0},b[9]={0};header(head,3,2,1,map);opus_family1_plan plan;
    CHECK(of1_plan_header(head,24,&plan)==OF1_OK);of1_pcm_buffer input[2]={{a+1,16},{b+1,8}};
    of1_channel_view views[8],saved[8];memset(views,0xa5,sizeof(views));memcpy(saved,views,sizeof(views));
    CHECK(of1_channel_views(&plan,input,1,4,views)==OF1_INVALID && !memcmp(views,saved,sizeof(views)));
    input[1].bytes=7;CHECK(of1_channel_views(&plan,input,2,4,views)==OF1_INVALID && !memcmp(views,saved,sizeof(views)));input[1].bytes=8;
    CHECK(of1_channel_views(&plan,input,2,4,views)==OF1_OK);uint8_t output[24],unchanged[24];memset(output,0x5a,sizeof(output));memcpy(unchanged,output,sizeof(output));size_t written=999;
    CHECK(of1_gather_s16(views,3,0,4,output,23,&written)==OF1_INVALID && written==999 && !memcmp(output,unchanged,sizeof(output)));
    CHECK(of1_gather_s16(views,3,SIZE_MAX,1,output,24,&written)==OF1_INVALID && written==999);
    CHECK(of1_gather_s16(views,3,0,1,NULL,24,&written)==OF1_INVALID && written==999);
    views[2].stride=3;CHECK(of1_gather_s16(views,3,0,1,output,24,&written)==OF1_INVALID && !memcmp(output,unchanged,sizeof(output)));
    CHECK(of1_channel_views(&plan,input,2,4,views)==OF1_OK && of1_gather_s16(views,3,4,0,NULL,0,&written)==OF1_OK && written==0);
}
static int16_t round16(double v){double x=v*32768.0;return x>32767?32767:x<-32768?-32768:(int16_t)llround(x);}
static void exact(FILE *f,void *p,size_t n){CHECK(fread(p,1,n,f)==n);}
static void creator_case(const char *transport,unsigned c,const uint8_t *map,unsigned case_id) {
    FILE *f=fopen(transport,"rb");CHECK(f);uint8_t source_head[40];exact(f,source_head,40);CHECK(!memcmp(source_head,"OFAM101\0",8));
    unsigned n=of1_le32(source_head+12),m=of1_le32(source_head+16),packets=of1_le32(source_head+28);CHECK(n<=5 && packets==11);
    uint8_t head[40];header(head,c,n,m,map);opus_family1_plan plan;CHECK(of1_plan_header(head,21u+c,&plan)==OF1_OK);
    int error=0;OpusMSDecoder *multi=opus_multistream_decoder_create(48000,(int)c,(int)n,(int)m,map,&error);CHECK(multi && !error);
    OpusDecoder *single[8]={0};for(unsigned slot=0;slot<plan.needed;++slot){single[slot]=opus_decoder_create(48000,plan.stream_channels[slot],&error);CHECK(single[slot] && !error);}
    float reference[5760*8],separate[8][5760*2];uint8_t pcm[8][5760*4+1],output[97*8*2];uint64_t samples_checked=0;
    for(unsigned packet_id=0;packet_id<packets;++packet_id) {
        uint8_t length[4];exact(f,length,4);unsigned bytes=of1_le32(length);CHECK(bytes && bytes<=61440);uint8_t *packet=malloc(bytes);CHECK(packet);exact(f,packet,bytes);
        opus_elementary_view views[8];uint16_t samples=0;CHECK(omf_family01_packet(packet,bytes,(uint8_t)n,plan.stream_id,plan.needed,views,&samples)==OMF_OK && samples==960);
        CHECK(opus_multistream_decode_float(multi,packet,(int32_t)bytes,reference,5760,0)==samples);of1_pcm_buffer buffers[8]={{0}};
        for(unsigned slot=0;slot<plan.needed;++slot) {
            opus_elementary_view *v=views+slot;size_t common_bytes=v->bytes-v->extra_bytes;uint8_t *common=malloc(common_bytes);CHECK(common);
            memcpy(common,v->data,v->extra_offset);memcpy(common+v->extra_offset,v->data+v->extra_offset+v->extra_bytes,v->bytes-v->extra_offset-v->extra_bytes);
            CHECK(opus_decode_float(single[slot],common,(int32_t)common_bytes,separate[slot],5760,0)==samples);free(common);
            unsigned width=plan.stream_channels[slot];for(unsigned i=0;i<samples*width;++i)put16(pcm[slot]+1+i*2u,round16(separate[slot][i]));
            buffers[slot]=(of1_pcm_buffer){pcm[slot]+1,(size_t)samples*width*2u};
        }
        of1_channel_view channel_views[8];CHECK(of1_channel_views(&plan,buffers,plan.needed,samples,channel_views)==OF1_OK);
        for(unsigned frame=0;frame<samples;++frame)for(unsigned channel=0;channel<c;++channel) {
            unsigned slot=plan.speaker_slot[channel];float actual=slot==OF1_SILENCE?0:separate[slot][frame*plan.stream_channels[slot]+plan.speaker_channel[channel]];
            CHECK(actual==reference[frame*c+channel]);++samples_checked;
        }
        for(size_t start=0;start<samples;start+=97) {
            size_t count=samples-start;if(count>97)count=97;size_t written=0;CHECK(of1_gather_s16(channel_views,(uint8_t)c,start,count,output,sizeof(output),&written)==OF1_OK && written==count*c*2u);
            for(size_t i=0;i<count*c;++i){uint8_t expected[2];put16(expected,round16(reference[start*c+i]));CHECK(output[2*i]==expected[0] && output[2*i+1]==expected[1]);}
        }
        free(packet);
    }
    CHECK(fgetc(f)==EOF && !ferror(f) && !fclose(f));opus_multistream_decoder_destroy(multi);for(unsigned slot=0;slot<plan.needed;++slot)opus_decoder_destroy(single[slot]);
    printf("{\"suite\":\"creator-differential\",\"case\":%u,\"channels\":%u,\"streams\":%u,\"coupled\":%u,\"needed_handles\":%u,\"packets\":11,\"float_samples_exact\":%" PRIu64 ",\"bounded_gather_exact\":true}\n",
        case_id,c,n,m,(unsigned)plan.needed,samples_checked);
}
static void creator_extreme(unsigned n,unsigned m) {
    uint8_t map[8]={254,0,254,255,128,1,253,255},head[40],packet[509];header(head,8,n,m,map);opus_family1_plan plan;
    CHECK(of1_plan_header(head,29,&plan)==OF1_OK && plan.needed<=8);
    for(unsigned s=0;s+1<n;++s){packet[s*2]=0xf8;packet[s*2+1]=0;}packet[(n-1)*2]=0xf8;
    unsigned bytes=n*2-1;opus_elementary_view views[8];uint16_t samples=0;
    CHECK(omf_family01_packet(packet,bytes,(uint8_t)n,plan.stream_id,plan.needed,views,&samples)==OMF_OK && samples==960);
    int error=0;OpusMSDecoder *multi=opus_multistream_decoder_create(48000,8,(int)n,(int)m,map,&error);CHECK(multi && !error);float reference[960*8];
    CHECK(opus_multistream_decode_float(multi,packet,(int32_t)bytes,reference,960,0)==960);
    for(unsigned i=0;i<960*8;++i)CHECK(reference[i]==0);
    for(unsigned slot=0;slot<plan.needed;++slot) {
        OpusDecoder *single=opus_decoder_create(48000,plan.stream_channels[slot],&error);CHECK(single && !error);float pcm[960*2];
        const uint8_t toc=views[slot].data[0];CHECK(opus_decode_float(single,&toc,1,pcm,960,0)==960);
        for(unsigned i=0;i<960u*plan.stream_channels[slot];++i)CHECK(pcm[i]==0);
        opus_decoder_destroy(single);
    }
    opus_multistream_decoder_destroy(multi);
    printf("{\"suite\":\"creator-extreme-plc\",\"streams\":%u,\"coupled\":%u,\"decoded_channels\":%u,\"needed_handles\":%u,\"original_packet_bytes\":%u,\"frames\":960,\"exact\":true}\n",
        n,m,n+m,(unsigned)plan.needed,bytes);
}
int main(int argc,char **argv) {
    const uint16_t endian=1;CHECK(*(const uint8_t *)&endian==1);header_boundaries();framing_boundaries();view_boundaries();unsigned creator_cases=0;
    if(argc==4) {
        const uint8_t defaults[3][8]={{0,2,1},{0,4,1,2,3,5},{0,6,1,2,3,4,5,7}};const unsigned counts[3]={3,6,8};
        for(unsigned i=0;i<3;++i)creator_case(argv[i+1],counts[i],defaults[i],creator_cases++);
        const uint8_t variants[8][8]={{7},{6,0},{5,5,255},{7,0,6,1},{255,255,255,255,255},{0,1,2,3,4,5},{7,7,6,5,0,255,1},{0,7,0,7,255,5,6,255}};
        for(unsigned c=1;c<=8;++c)creator_case(argv[3],c,variants[c-1],creator_cases++);
        creator_extreme(255,0);creator_extreme(128,127);
    } else CHECK(argc==1);
    printf("{\"suite\":\"opus-family1-helpers\",\"passed\":true,\"assertions\":%u,\"creator_cases\":%u,\"production_integrated\":false}\n",assertions,creator_cases);return 0;
}
