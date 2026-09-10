/* Host-only oracle comparison for a reused960-sample output buffer. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "opus.h"
#include "opus_memory.h"
#define GUARD 0x5a39ce71U
static struct { uint32_t before; int16_t data[960]; uint32_t after; } pcm;
static struct { uint32_t before, data[1536], after; } scratch;
static struct { uint32_t before, data[4096], after; } words;
static unsigned char packet[16384];
static OpusDecoder *decoder;
static unsigned allocations, active, blocks, samples, largest;
static FILE *output;
void *__real_malloc(size_t);
void *__real_calloc(size_t,size_t);
void *__real_realloc(void *,size_t);
void *__wrap_malloc(size_t n) { if(active)++allocations; return __real_malloc(n); }
void *__wrap_calloc(size_t n,size_t z) { if(active)++allocations; return __real_calloc(n,z); }
void *__wrap_realloc(void *p,size_t n) { if(active)++allocations; return __real_realloc(p,n); }
static int consume(void *ctx, int16_t *data, int n) {
    assert(ctx==decoder && data==pcm.data && n>0 && n<=960);
    assert(pcm.before==GUARD && pcm.after==GUARD);
    assert(scratch.before==GUARD && scratch.after==GUARD && words.before==GUARD && words.after==GUARD);
    /* Sink re-entry must not reset the active frame's arena/history. */
    assert(yoradio_opus_decode_bounded(decoder,NULL,0,pcm.data,120)==OPUS_INVALID_STATE);
    assert(fwrite(data,sizeof(*data),n,output)==(size_t)n);
    ++blocks;samples+=(unsigned)n;if((unsigned)n>largest)largest=(unsigned)n;
    /* Real output applies gain in-place. Later frames must not depend on this
       caller-owned PCM after delivery, including mode/overlap transitions. */
    memset(pcm.data,0xa5,sizeof(pcm.data));
    return 0;
}
int main(int argc,char **argv) {
    if(argc==4 && !strcmp(argv[1],"--unpack")) {
        FILE *input=fopen(argv[2],"rb"),*out=fopen(argv[3],"wb");assert(input&&out);
        unsigned count=0;
        for(;;) {
            unsigned char header[2],toc;size_t got=fread(header,1,2,input);
            if(!got)break;
            assert(got==2);unsigned length=header[0]+256U*header[1];
            assert(length&&length<=sizeof(packet)&&fread(packet,1,length,input)==length);
            const unsigned char *frames[48];opus_int16 sizes[48];
            int n=opus_packet_parse(packet,(opus_int32)length,&toc,frames,sizes,NULL);assert(n>0);
            toc&=252U;
            for(int i=0;i<n;i++) {
                unsigned bytes=1U+(unsigned)sizes[i];header[0]=(unsigned char)bytes;header[1]=(unsigned char)(bytes>>8);
                assert(fwrite(header,1,2,out)==2&&fwrite(&toc,1,1,out)==1);
                assert(fwrite(frames[i],1,sizes[i],out)==(size_t)sizes[i]);++count;
            }
        }
        assert(fclose(input)==0&&fclose(out)==0);printf("{\"frames\":%u}\n",count);return 0;
    }
    assert(argc==3);
    FILE *input=fopen(argv[1],"rb");output=fopen(argv[2],"wb");assert(input && output);
    decoder=malloc(opus_decoder_get_size(1));assert(decoder);
    pcm.before=pcm.after=scratch.before=scratch.after=words.before=words.after=GUARD;
    yoradio_opus_memory_bind(scratch.data,sizeof(scratch.data),words.data,sizeof(words.data));
    assert(opus_decoder_init(decoder,48000,1)==OPUS_OK);
    unsigned packets=0;
    for(;;) {
        unsigned char size[2];size_t got=fread(size,1,2,input);
        if(!got)break;
        assert(got==2);
        unsigned length=size[0]+256U*size[1];assert(length && length<=sizeof(packet));
        assert(fread(packet,1,length,input)==length);
        unsigned old=samples;active=1;
        int n=yoradio_opus_decode_blocks_bounded(decoder,packet,(int)length,pcm.data,960,consume,decoder);
        active=0;assert(n>0 && (unsigned)n==samples-old);
        opus_int32 duration=0;assert(opus_decoder_ctl(decoder,OPUS_GET_LAST_PACKET_DURATION(&duration))==OPUS_OK);
        assert(duration==n);++packets;
    }
    assert(!allocations && fclose(input)==0 && fclose(output)==0);
    printf("{\"packets\":%u,\"samples\":%u,\"blocks\":%u,\"largest_block\":%u,\"pcm_bytes\":%zu,\"scratch_bytes\":%zu,\"scratch_words\":%zu,\"allocations\":%u,\"guards\":true,\"sink_mutation\":true,\"reentry_rejected\":true}\n",
        packets,samples,blocks,largest,sizeof(pcm.data),yoradio_opus_scratch_peak_bytes(),yoradio_opus_scratch_peak_words(),allocations);
    free(decoder);return 0;
}
