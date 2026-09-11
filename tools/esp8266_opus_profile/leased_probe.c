/* Host-only ownership oracle. Hold frame A while libopus decodes frame B. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "opus.h"
#include "opus_memory.h"
#define GUARD 0x5a39ce71U
static struct { uint32_t before; int16_t data[960]; uint32_t after; } pool[2];
static struct { uint32_t before, data[1536], after; } scratch;
static struct { uint32_t before, data[4096], after; } words;
static unsigned char packet[16384];
static OpusDecoder *decoder;
static unsigned active, allocations, blocks, samples, largest, acquisitions, aborts;
static unsigned pending_slot, pending_count, next_slot, held[2];
static uint32_t pending_hash;
static int cancel_acquire, cancel_output, null_acquire, unaligned_acquire;
static FILE *output;
void *__real_malloc(size_t);
void *__real_calloc(size_t,size_t);
void *__real_realloc(void *,size_t);
void *__wrap_malloc(size_t n) { if(active)++allocations; return __real_malloc(n); }
void *__wrap_calloc(size_t n,size_t z) { if(active)++allocations; return __real_calloc(n,z); }
void *__wrap_realloc(void *p,size_t n) { if(active)++allocations; return __real_realloc(p,n); }
static uint32_t hash(const int16_t *data, unsigned count) {
    uint32_t value=2166136261U;
    for(unsigned i=0;i<count;++i) value=(value^(uint16_t)data[i])*16777619U;
    return value;
}
static void guards(void) {
    for(unsigned i=0;i<2;++i) assert(pool[i].before==GUARD && pool[i].after==GUARD);
    assert(scratch.before==GUARD && scratch.after==GUARD && words.before==GUARD && words.after==GUARD);
    if(pending_count) assert(hash(pool[pending_slot].data,pending_count)==pending_hash);
}
static unsigned slot(int16_t *p) {
    for(unsigned i=0;i<2;++i) if(p==pool[i].data)return i;
    assert(0);return 0;
}
static void drain(void) {
    if(!pending_count)return;
    guards();assert(held[pending_slot]);
    if(output)assert(fwrite(pool[pending_slot].data,sizeof(int16_t),pending_count,output)==pending_count);
    memset(pool[pending_slot].data,0xa5,sizeof(pool[pending_slot].data));
    held[pending_slot]=0;pending_count=0;
}
static void aborted(void *ctx,int16_t *data) {
    assert(ctx==decoder);
    if(unaligned_acquire) {
        assert(data==(int16_t*)((unsigned char*)pool[next_slot^1U].data+1));
        held[next_slot^1U]=0;
    } else { unsigned s=slot(data);assert(held[s]);held[s]=0; }
    ++aborts;
}
static int acquire(void *ctx,int16_t **data,int count);
static int consume(void *ctx,int16_t *data,int count);
static void reentry(void) {
    assert(yoradio_opus_decode_bounded(decoder,NULL,0,pool[0].data,120)==OPUS_INVALID_STATE);
    const unsigned char silence[]={0xf8,0xff,0xfe};
    assert(yoradio_opus_decode_leased_bounded(decoder,silence,sizeof(silence),960,
        acquire,consume,aborted,decoder)==OPUS_INVALID_STATE);
}
static int acquire(void *ctx,int16_t **data,int count) {
    assert(ctx==decoder && count>0 && count<=960);guards();reentry();
    ++acquisitions;
    if(cancel_acquire && acquisitions==(unsigned)cancel_acquire)return -777;
    if(null_acquire)return 0;
    unsigned s=next_slot;next_slot^=1U;
    assert(!held[s]);held[s]=1;*data=pool[s].data;
    if(unaligned_acquire)*data=(int16_t*)((unsigned char*)*data+1);
    return 0;
}
static int consume(void *ctx,int16_t *data,int count) {
    assert(ctx==decoder && count>0 && count<=960);guards();reentry();
    unsigned s=slot(data);assert(held[s]);
    /* The previous frame is still unchanged AFTER the next decode finished. */
    drain();++blocks;
    if(cancel_output && blocks==(unsigned)cancel_output)return -778;
    pending_slot=s;pending_count=(unsigned)count;pending_hash=hash(data,pending_count);
    samples+=(unsigned)count;if((unsigned)count>largest)largest=(unsigned)count;
    return 0;
}
static void init(void) {
    drain();assert(!held[0] && !held[1]);
    acquisitions=aborts=blocks=samples=largest=next_slot=0;
    cancel_acquire=cancel_output=null_acquire=unaligned_acquire=0;
    yoradio_opus_memory_bind(scratch.data,sizeof(scratch.data),words.data,sizeof(words.data));
    assert(opus_decoder_init(decoder,48000,1)==OPUS_OK);
}
static void failure_tests(void) {
    const unsigned char packed[]={0xfb,3,0xff,0xfe,0xff,0xfe,0xff,0xfe};
    init();active=1;
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),961,
        acquire,consume,aborted,decoder)==OPUS_BAD_ARG);assert(!acquisitions);
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),960,
        acquire,consume,NULL,decoder)==OPUS_BAD_ARG);assert(!acquisitions);
    cancel_acquire=2;
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),960,
        acquire,consume,aborted,decoder)==-777);
    assert(acquisitions==2 && blocks==1 && !aborts && pending_count==960);
    active=0;init();cancel_output=2;active=1;
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),960,
        acquire,consume,aborted,decoder)==-778);
    assert(acquisitions==2 && blocks==2 && aborts==1 && !held[0] && !held[1]);
    active=0;init();null_acquire=1;active=1;
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),960,
        acquire,consume,aborted,decoder)==OPUS_BAD_ARG);
    assert(acquisitions==1 && !blocks && !aborts);
    active=0;init();unaligned_acquire=1;active=1;
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),960,
        acquire,consume,aborted,decoder)==OPUS_BAD_ARG);
    assert(acquisitions==1 && !blocks && aborts==1 && !held[0] && !held[1]);
    active=0;init();
    /* Preserve initialized persistent history but force decode-time scratch OOM. */
    yoradio_opus_memory_bind(scratch.data,8,words.data,sizeof(words.data));
    assert(opus_decoder_init(decoder,48000,1)==OPUS_OK);active=1;
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),960,
        acquire,consume,aborted,decoder)==OPUS_ALLOC_FAIL);
    assert(acquisitions==1 && !blocks && aborts==1 && !held[0] && !held[1]);
    active=0;guards();init();active=1;
    assert(yoradio_opus_decode_leased_bounded(decoder,packed,sizeof(packed),960,
        acquire,consume,aborted,decoder)==2880);
    active=0;drain();assert(samples==2880 && !held[0] && !held[1]);
}
int main(int argc,char **argv) {
    assert(argc==3);FILE *input=fopen(argv[1],"rb");assert(input);
    decoder=malloc(opus_decoder_get_size(1));assert(decoder);
    for(unsigned i=0;i<2;++i)pool[i].before=pool[i].after=GUARD;
    scratch.before=scratch.after=words.before=words.after=GUARD;
    failure_tests();init();output=fopen(argv[2],"wb");assert(output);
    unsigned packets=0;
    for(;;) {
        unsigned char size[2];size_t got=fread(size,1,2,input);if(!got)break;
        assert(got==2);unsigned length=size[0]+256U*size[1];
        assert(length && length<=sizeof(packet) && fread(packet,1,length,input)==length);
        unsigned old=samples;active=1;
        int n=yoradio_opus_decode_leased_bounded(decoder,packet,(int)length,960,
            acquire,consume,aborted,decoder);
        active=0;assert(n>0 && (unsigned)n==samples-old);guards();++packets;
        opus_int32 duration=0;assert(opus_decoder_ctl(decoder,OPUS_GET_LAST_PACKET_DURATION(&duration))==OPUS_OK);
        assert(duration==n);
    }
    drain();guards();assert(!held[0] && !held[1] && !allocations && !aborts);
    assert(fclose(input)==0 && fclose(output)==0);
    printf("{\"packets\":%u,\"samples\":%u,\"blocks\":%u,\"largest_block\":%u,\"pcm_bytes\":%zu,\"scratch_bytes\":%zu,\"scratch_words\":%zu,\"allocations\":%u,\"guards\":true,\"sink_mutation\":true,\"reentry_rejected\":true,\"delayed_consumer\":true,\"failure_cleanup\":true}\n",
        packets,samples,blocks,largest,2*sizeof(pool[0].data),yoradio_opus_scratch_peak_bytes(),yoradio_opus_scratch_peak_words(),allocations);
    free(decoder);return 0;
}
