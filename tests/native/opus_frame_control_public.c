/* Creator-only frame/packet cadence and float/integer observations.
 * Public APIs: https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html
 * https://opus-codec.org/docs/opus_api-1.5/group__opus__repacketizer.html
 * No private decoder state, configuration, layout or replacement arithmetic.
 */
#include "opus_packet_modes_public.h"
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern int opus_decode_float(OpusDecoder *,const unsigned char *,int32_t,float *,int,int);
extern int32_t opus_repacketizer_out_range(OpusRepacketizer *,int,int,unsigned char *,int32_t);
extern void opus_pcm_soft_clip(float *,int,int,float *);

static uint32_t le32(const unsigned char *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void put32(FILE *f,uint32_t n){unsigned char p[4];for(unsigned i=0;i<4;++i)p[i]=(unsigned char)(n>>(i*8));assert(fwrite(p,1,4,f)==4);}
static void exact(FILE *f,void *p,size_t n){assert(fread(p,1,n,f)==n);}
static FILE *output(const char *folder,const char *name){char path[4096];int n=snprintf(path,sizeof(path),"%s/%s",folder,name);assert(n>0 && n<(int)sizeof(path));FILE *f=fopen(path,"wb");assert(f);return f;}
static void s16(FILE *f,const int16_t *pcm,size_t count){for(size_t i=0;i<count;++i){uint16_t u=(uint16_t)pcm[i];unsigned char p[2]={(unsigned char)u,(unsigned char)(u>>8)};assert(fwrite(p,1,2,f)==2);}}
static void f32(FILE *f,const float *pcm,size_t count){_Static_assert(sizeof(float)==4,"float32 observation");for(size_t i=0;i<count;++i){uint32_t u;assert(isfinite(pcm[i]));memcpy(&u,pcm+i,4);put32(f,u);}}
static int16_t quantize(float x){double y=(double)x*32768.0;if(y>=32767)return 32767;if(y<=-32768)return -32768;return (int16_t)(y>=0?(int32_t)(y+0.5):-(int32_t)(-y+0.5));}
int main(int argc,char **argv) {
    assert(argc==3);FILE *input=fopen(argv[1],"rb");assert(input);unsigned char head[28];exact(input,head,28);assert(!memcmp(head,"OPMODE1\0",8));
    unsigned channels=le32(head+8),count=le32(head+20);assert((channels==1 || channels==2) && count==4);
    const char *names[]={"aggregate-s16.pcm","elementary-s16.pcm","aggregate-float.f32","elementary-float.f32",
        "aggregate-hard-s16.pcm","elementary-hard-s16.pcm","aggregate-soft-s16.pcm","elementary-soft-s16.pcm","elementary.packets"};
    FILE *files[9];for(unsigned i=0;i<9;++i)files[i]=output(argv[2],names[i]);
    assert(fwrite(head,1,28,files[8])==28);
    OpusDecoder *dec[4];int error=0;for(unsigned i=0;i<4;++i){dec[i]=opus_decoder_create(48000,(int)channels,&error);assert(dec[i] && !error);}
    OpusRepacketizer *rp=opus_repacketizer_create();assert(rp);
    unsigned char packet[65536],single[1276];int16_t integer[2][11520],quantized[11520];float floats[2][11520],soft[2][11520],soft_memory[2][2]={{0}};
    uint64_t total=0,unequal_integer=0,unequal_float=0;unsigned frame_count=0,frame_duration=0;double max_float_error=0,peak=0;int max_integer_error=0;
    for(unsigned packet_no=0;packet_no<count;++packet_no) {
        unsigned char b[4];exact(input,b,4);unsigned bytes=le32(b);assert(bytes && bytes<=61440);exact(input,packet,bytes);
        const unsigned char *frames[48];int16_t lengths[48];unsigned char toc;int offset=0;
        int frames_n=opus_packet_parse(packet,(int32_t)bytes,&toc,frames,lengths,&offset);assert(frames_n>0 && frames_n<=48);
        int duration=opus_packet_get_samples_per_frame(packet,48000),samples=opus_packet_get_nb_samples(packet,(int32_t)bytes,48000);
        assert(duration*frames_n==samples && samples<=5760);frame_duration=(unsigned)duration;
        assert(opus_decode(dec[0],packet,(int32_t)bytes,integer[0],5760,0)==samples);
        assert(opus_decode_float(dec[2],packet,(int32_t)bytes,floats[0],5760,0)==samples);
        assert(opus_repacketizer_init(rp)==rp && opus_repacketizer_cat(rp,packet,(int32_t)bytes)==0);
        for(int frame=0;frame<frames_n;++frame) {
            assert(lengths[frame]>0); /* This control excludes PLC completely. */
            int n=opus_repacketizer_out_range(rp,frame,frame+1,single,sizeof(single));assert(n>1 && (single[0]&3)==0);
            const unsigned char *one[48];int16_t size[48];unsigned char t;int o;
            assert(opus_packet_parse(single,n,&t,one,size,&o)==1 && size[0]==lengths[frame] && !memcmp(one[0],frames[frame],(size_t)size[0]));
            assert(opus_decode(dec[1],single,n,integer[1]+frame*duration*(int)channels,5760-frame*duration,0)==duration);
            assert(opus_decode_float(dec[3],single,n,floats[1]+frame*duration*(int)channels,5760-frame*duration,0)==duration);
            memcpy(soft[1]+frame*duration*(int)channels,floats[1]+frame*duration*(int)channels,(size_t)duration*channels*4);
            opus_pcm_soft_clip(soft[1]+frame*duration*(int)channels,duration,(int)channels,soft_memory[1]);
            put32(files[8],(unsigned)n);assert(fwrite(single,1,(size_t)n,files[8])==(size_t)n);++frame_count;
        }
        memcpy(soft[0],floats[0],(size_t)samples*channels*4);opus_pcm_soft_clip(soft[0],samples,(int)channels,soft_memory[0]);
        for(unsigned variant=0;variant<2;++variant) {
            s16(files[variant],integer[variant],(size_t)samples*channels);f32(files[2+variant],floats[variant],(size_t)samples*channels);
            for(int i=0;i<samples*(int)channels;++i){quantized[i]=quantize(floats[variant][i]);}
            s16(files[4+variant],quantized,(size_t)samples*channels);
            for(int i=0;i<samples*(int)channels;++i){quantized[i]=quantize(soft[variant][i]);}
            s16(files[6+variant],quantized,(size_t)samples*channels);
        }
        int packet_max=0;double packet_float_max=0,packet_peak=0;uint64_t out_of_range=0;
        for(int i=0;i<samples*(int)channels;++i) {
            int difference=abs((int)integer[0][i]-integer[1][i]);if(difference>packet_max)packet_max=difference;
            if(difference>max_integer_error){max_integer_error=difference;}
            unequal_integer+=(difference!=0);
            double difference_f=fabs((double)floats[0][i]-floats[1][i]);assert(isfinite(difference_f));
            if(difference_f>packet_float_max){packet_float_max=difference_f;}
            if(difference_f>max_float_error){max_float_error=difference_f;}
            unequal_float+=(difference_f!=0);double magnitude=fabs((double)floats[0][i]);
            if(magnitude>packet_peak){packet_peak=magnitude;}
            if(magnitude>peak){peak=magnitude;}
            out_of_range+=(magnitude>1.0);
        }
        printf("{\"packet\":%u,\"frames\":%d,\"frame_samples\":%d,\"samples\":%d,\"int16_cadence_max_error\":%d,\"float_cadence_max_error\":%.17g,\"float_peak\":%.17g,\"float_outside_unit_samples\":%" PRIu64 "}\n",
            packet_no,frames_n,duration,samples,packet_max,packet_float_max,packet_peak,out_of_range);total+=(unsigned)samples;
    }
    assert(fgetc(input)==EOF && !ferror(input));assert(!fclose(input));assert(fseek(files[8],20,SEEK_SET)==0);put32(files[8],frame_count);put32(files[8],frame_duration);
    for(unsigned i=0;i<9;++i){assert(!fclose(files[i]));}for(unsigned i=0;i<4;++i){opus_decoder_destroy(dec[i]);}opus_repacketizer_destroy(rp);
    printf("{\"summary\":true,\"libopus\":\"%s\",\"packets\":%u,\"elementary_packets\":%u,\"raw_frames\":%" PRIu64 ",\"channels\":%u,\"integer_unequal_samples\":%" PRIu64 ",\"integer_max_error\":%d,\"float_unequal_samples\":%" PRIu64 ",\"float_max_error\":%.17g,\"float_peak\":%.17g,\"private_abi_used\":false,\"numeric_tolerance_applied\":false}\n",
        opus_get_version_string(),count,frame_count,total,channels,unequal_integer,max_integer_error,unequal_float,max_float_error,peak);
    return 0;
}
