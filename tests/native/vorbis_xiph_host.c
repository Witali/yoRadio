/* Resource regressions and the unchanged original31 public raw PCM corpus. */
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "vorbis/codec.h"
#include "vorbis_xiph_alloc.h"
#include "cases.h"

extern int xiph_arena_tests(void);
extern int xiph_book_tests(void);
extern int xiph_bitreader_tests(void);
static int16_t samples[32768];
static const uint64_t canary=UINT64_C(0xa194d6f02b387c55);
_Static_assert(__BYTE_ORDER__==__ORDER_LITTLE_ENDIAN__,"S16LE capture");
static void write32(FILE *out,uint32_t value){
    unsigned char bytes[4]={(unsigned char)value,(unsigned char)(value>>8),
        (unsigned char)(value>>16),(unsigned char)(value>>24)};
    assert(fwrite(bytes,1,4,out)==4);
}
static int16_t convert(float input){
    assert(isfinite(input));double value=(double)input*32768.0;
    if(value>=32767.0)return 32767;
    if(value<=-32768.0)return -32768;
    double lower=floor(value),fraction=value-lower;int32_t result=(int32_t)lower;
    if(fraction>0.5 || (fraction==0.5 && result%2!=0))result++;
    return (int16_t)result;
}
typedef struct {unsigned char *base,*bytes;size_t size;const uint8_t *original;} guarded_t;
static guarded_t packet_bytes(const uint8_t *original,size_t size){
    guarded_t value={0};assert(size && size<=SIZE_MAX-16);
    value.base=malloc(size+16);assert(value.base);value.bytes=value.base+8;
    value.size=size;value.original=original;memcpy(value.base,&canary,8);
    memcpy(value.bytes,original,size);memcpy(value.bytes+size,&canary,8);return value;
}
static void packet_clear(guarded_t *value){
    uint64_t first,last;memcpy(&first,value->base,8);memcpy(&last,value->bytes+value->size,8);
    assert(first==canary && last==canary && !memcmp(value->bytes,value->original,value->size));free(value->base);
}
static ogg_packet packet(guarded_t *bytes,int number,int64_t granule,int bos,int eos){
    ogg_packet value;memset(&value,0,sizeof(value));value.packet=bytes->bytes;
    value.bytes=(long)bytes->size;value.packetno=number;value.granulepos=granule;
    value.b_o_s=bos;value.e_o_s=eos;return value;
}
static void capture(FILE *out,uint32_t index){
    const xiph_case_t *test=&xiph_cases[index];vorbis_info info;vorbis_comment comment;
    size_t initial_live=xiph_port_test_live(),initial_bytes=xiph_port_test_bytes();
    vorbis_dsp_state dsp;vorbis_block block;vorbis_info_init(&info);vorbis_comment_init(&comment);
    const uint8_t *headers[]={test->identification,test->comment,test->setup};
    uint32_t sizes[]={test->identification_bytes,test->comment_bytes,test->setup_bytes};
    for(int h=0;h<3;h++){
        guarded_t input=packet_bytes(headers[h],sizes[h]);ogg_packet p=packet(&input,h,0,h==0,0);
        assert(vorbis_synthesis_headerin(&info,&comment,&p)==0);packet_clear(&input);
    }
    assert(vorbis_synthesis_init(&dsp,&info)==0 && vorbis_block_init(&dsp,&block)==0);
    assert(info.rate==(long)test->rate && info.channels==(int)test->channels);
    assert(vorbis_info_blocksize(&info,0)==(long)test->short_block);
    assert(vorbis_info_blocksize(&info,1)==(long)test->long_block);
    write32(out,index);write32(out,test->rate);write32(out,test->channels);write32(out,test->packet_count);
    uint32_t total=0;
    for(uint32_t p=0;p<test->packet_count;p++){
        uint32_t start=test->offsets[p],end=test->offsets[p+1];assert(start<end && end<=test->audio_bytes);
        guarded_t input=packet_bytes(test->audio+start,end-start);
        ogg_packet data=packet(&input,(int)p+3,test->granules[p],0,p+1==test->packet_count);
        assert(vorbis_synthesis(&block,&data)==0 && vorbis_synthesis_blockin(&dsp,&block)==0);
        uint32_t count=0,frames=0;float **pcm=NULL;int available;
        while((available=vorbis_synthesis_pcmout(&dsp,&pcm))>0){
            assert(pcm && (size_t)count+(size_t)available*test->channels<=sizeof(samples)/sizeof(*samples));
            for(int i=0;i<available;i++)for(int ch=0;ch<info.channels;ch++)samples[count++]=convert(pcm[ch][i]);
            frames+=(uint32_t)available;assert(vorbis_synthesis_read(&dsp,available)==0);
        }
        assert(available==0 && frames==test->frames[p] && count==frames*test->channels);
        packet_clear(&input);write32(out,p);write32(out,frames);write32(out,count*2);
        assert(fwrite(samples,2,count,out)==count);total+=count*2;
    }
    assert(total==test->pcm_bytes);assert(vorbis_block_clear(&block)==0);
    vorbis_dsp_clear(&dsp);vorbis_comment_clear(&comment);vorbis_info_clear(&info);
    assert(xiph_port_test_live()==initial_live && xiph_port_test_bytes()==initial_bytes);
}
int main(int argc,char **argv){
    assert(argc==2 && !xiph_port_test_live() && !xiph_port_test_bytes());
    int arena=xiph_arena_tests(),books=xiph_book_tests(),bits=xiph_bitreader_tests();
    assert(arena==11 && books>0 && bits>0);
    assert(!xiph_port_test_live() && !xiph_port_test_bytes());xiph_port_test_reset(0);
    printf("RESOURCE_CHECKS arena=%d books=%d bits=%d live=0\n",arena,books,bits);fflush(stdout);
    FILE *out=fopen(argv[1],"wb");assert(out);assert(fwrite("XIPHRES1",1,8,out)==8);write32(out,XIPH_CASE_COUNT);
    for(uint32_t i=0;i<XIPH_CASE_COUNT;i++)capture(out,i);
    assert(!fclose(out) && !xiph_port_test_live() && !xiph_port_test_bytes());
    printf("RESOURCE_PASS arena=%d books=%d cases=%u packets=%u pcm_bytes=%u live=0\n",arena,books,(unsigned)XIPH_CASE_COUNT,(unsigned)XIPH_TOTAL_PACKETS,(unsigned)XIPH_EXPECTED_PCM_BYTES);
    return 0;
}
