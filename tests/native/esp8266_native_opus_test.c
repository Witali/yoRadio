#include "native_opus.h"
#include "opus.h"
#include "opus_memory.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef union { uint64_t align; uint8_t bytes[32768]; } aligned_buffer;
static aligned_buffer state, scratch, iram;
static int16_t pcm[NATIVE_OPUS_MAX_SAMPLES];
static native_opus_t decoder;
static uint8_t stream[32768];
static size_t stream_size, calls, received;
static uint32_t last_bitrate;
static bool cancel;
static unsigned allocation_count;
/* Real bounded libopus is linked; unexpected heap allocation fails the test. */
void *__wrap_malloc(size_t n) { (void)n; ++allocation_count; return NULL; }
void *__wrap_calloc(size_t n, size_t z) { (void)n; (void)z; ++allocation_count; return NULL; }
void *__wrap_realloc(void *p, size_t n) { (void)p; (void)n; ++allocation_count; return NULL; }
static bool output(void *ctx, const int16_t *data, size_t samples, uint32_t bitrate) {
    assert(ctx == &calls && samples && samples <= 960);
    assert(data >= pcm && data + samples <= pcm + 960);
    for (size_t i=0; i<samples; ++i) assert(data[i] == 0);
    ++calls; received += samples; last_bitrate = bitrate;
    return !cancel;
}
static native_opus_config_t config(void) {
    native_opus_config_t c = {state.bytes,sizeof(state.bytes),scratch.bytes,7680,
        iram.bytes,NATIVE_OPUS_IRAM_BYTES,pcm,960,output,&calls};
    return c;
}
static void init(void) {
    calls=received=0; cancel=false; last_bitrate=0;
    native_opus_config_t c=config(); assert(native_opus_init(&decoder,&c)==0);
}
static void put32(uint8_t *p,uint32_t v) {
    for(unsigned i=0;i<4;++i) p[i]=(uint8_t)(v>>(8*i));
}
static void page(uint32_t serial,uint32_t sequence,unsigned flags,uint64_t granule,
                 const uint8_t *const *packets,const size_t *lengths,unsigned count) {
    const size_t begin=stream_size; uint8_t laces[255]; unsigned nl=0; size_t body=0;
    assert(count<=20);
    for(unsigned i=0;i<count;++i) {
        size_t n=lengths[i]; body+=n;
        while(n>=255) { laces[nl++]=255; n-=255; } laces[nl++]=(uint8_t)n;
    }
    assert(begin+27+nl+body<=sizeof(stream));
    uint8_t *p=stream+begin; memset(p,0,27); memcpy(p,"OggS",4); p[5]=(uint8_t)flags;
    put32(p+6,(uint32_t)granule); put32(p+10,(uint32_t)(granule>>32));
    put32(p+14,serial); put32(p+18,sequence); p[26]=(uint8_t)nl;
    memcpy(p+27,laces,nl); stream_size+=27+nl;
    for(unsigned i=0;i<count;++i) { memcpy(stream+stream_size,packets[i],lengths[i]); stream_size+=lengths[i]; }
    uint32_t crc=0;
    for(size_t i=begin;i<stream_size;++i) {
        crc^=(uint32_t)stream[i]<<24;
        for(unsigned b=0;b<8;++b) crc=(crc<<1)^((crc&0x80000000u)?0x04c11db7u:0);
    }
    put32(p+22,crc);
}
static void one(uint32_t serial,uint32_t sequence,unsigned flags,uint64_t granule,
                const uint8_t *packet,size_t size) {
    page(serial,sequence,flags,granule,&packet,&size,1);
}
static void headers(uint32_t serial,unsigned version,unsigned channels,unsigned skip,
                    int gain,unsigned mapping,size_t size) {
    uint8_t head[32]={'O','p','u','s','H','e','a','d'};
    const uint8_t tags[16]={'O','p','u','s','T','a','g','s'};
    assert(size<=sizeof(head)); head[8]=(uint8_t)version; head[9]=(uint8_t)channels;
    head[10]=(uint8_t)skip; head[11]=(uint8_t)(skip>>8); put32(head+12,44100);
    head[16]=(uint8_t)gain; head[17]=(uint8_t)((unsigned)gain>>8); head[18]=(uint8_t)mapping;
    one(serial,0,2,0,head,size); one(serial,1,0,0,tags,sizeof(tags));
}
static const uint8_t silence[]={0xf8,0xff,0xfe};
static int feed_all(size_t fragment) {
    size_t pos=0;
    for(;;) {
        size_t n=stream_size-pos; if(n>fragment)n=fragment;
        size_t used=SIZE_MAX; uint64_t before=decoder.audio_packets;
        int r=native_opus_feed(&decoder,n?stream+pos:NULL,n,&used);
        assert(used<=n && decoder.audio_packets<=before+1); pos+=used;
        if(r<0)return r;
        if(r==NATIVE_OPUS_PACKET)continue;
        assert(used==n); if(pos==stream_size)return native_opus_finish(&decoder);
    }
}
static void test_memory(void) {
    native_opus_config_t c=config();
    assert(native_opus_decoder_size()>0 && native_opus_decoder_size()<sizeof(state));
    c.decoder_state_bytes=native_opus_decoder_size()-1;
    assert(native_opus_init(&decoder,&c)==NATIVE_OPUS_ERR_MEMORY);
    c=config();c.iram_bytes=16383;assert(native_opus_init(&decoder,&c)==NATIVE_OPUS_ERR_MEMORY);
    c=config();c.scratch=state.bytes;assert(native_opus_init(&decoder,&c)==NATIVE_OPUS_ERR_MEMORY);
    c=config();c.pcm_samples=959;assert(native_opus_init(&decoder,&c)==NATIVE_OPUS_ERR_MEMORY);
    c=config();c.scratch=scratch.bytes+1;assert(native_opus_init(&decoder,&c)==NATIVE_OPUS_ERR_MEMORY);
    c=config();c.decoder_state=&decoder;assert(native_opus_init(&decoder,&c)==NATIVE_OPUS_ERR_MEMORY);
    init();size_t used=12;assert(native_opus_feed(&decoder,NULL,1,&used)==NATIVE_OPUS_ERR_ARGUMENT && used==0);
}
static void test_alignment(void) {
    /* Four-byte addresses are valid for word scratch/history, including on
     * 64-bit hosts; state additionally contains native pointers. */
    for(size_t offset=1;offset<8;++offset) {
        native_opus_config_t c=config();
        c.decoder_state=state.bytes+offset;c.decoder_state_bytes-=offset;
        const bool state_aligned=offset%sizeof(void*)==0 && offset%4==0;
        assert(native_opus_init(&decoder,&c)==(state_aligned?0:NATIVE_OPUS_ERR_MEMORY));
        c=config();c.scratch=scratch.bytes+offset;
        assert(native_opus_init(&decoder,&c)==(offset%4?NATIVE_OPUS_ERR_MEMORY:0));
        c=config();c.iram=iram.bytes+offset;
        assert(native_opus_init(&decoder,&c)==(offset%4?NATIVE_OPUS_ERR_MEMORY:0));
    }
    memset(scratch.bytes,0xa5,sizeof(scratch.bytes));
    memset(iram.bytes,0xa5,sizeof(iram.bytes));
    native_opus_config_t c=config();c.scratch=scratch.bytes+4;c.iram=iram.bytes+4;
    calls=received=0;cancel=false;
    assert(native_opus_init(&decoder,&c)==0);
    stream_size=0;headers(13,1,1,0,0,0,19);
    const uint8_t silk_dtx=0x08,hybrid_dtx=0x68;
    one(13,2,0,960,&silk_dtx,1);one(13,3,0,1920,&hybrid_dtx,1);
    one(13,4,4,2880,silence,sizeof(silence));
    assert(feed_all(7)==0 && received==2880);
    assert(native_opus_reset(&decoder)==0);
    assert(feed_all(7)==0 && received==5760 && calls==6);
    for(size_t i=0;i<4;++i) {
        assert(scratch.bytes[i]==0xa5 && scratch.bytes[4+c.scratch_bytes+i]==0xa5);
        assert(iram.bytes[i]==0xa5 && iram.bytes[4+c.iram_bytes+i]==0xa5);
    }
}
static void test_flash_table_reads(void) {
    /* Both halfword positions, every signed16 value, including the extrema.
     * Use full uint32 storage so the aligned read never crosses an object. */
    for(unsigned value=0;value<65536;++value) {
        yoradio_opus_table_pair table;
        table.half[0]=(int16_t)((int)value-32768);
        table.half[1]=(int16_t)(32767-(int)value);
        yoradio_opus_table_pair pair=yoradio_opus_table_load_pair(&table);
        assert(pair.half[0]==table.half[0] && pair.half[1]==table.half[1]);
        assert(yoradio_opus_table_read16(&table.half[0])==table.half[0]);
        assert(yoradio_opus_table_read16(&table.half[1])==table.half[1]);
    }
}
static void test_headers(void) {
    const unsigned ch[]={0,3,1,1,1},version[]={1,1,16,1,1},mapping[]={0,0,0,1,0};
    const size_t sizes[]={19,19,19,19,20};
    const int error[]={NATIVE_OPUS_ERR_MAPPING,NATIVE_OPUS_ERR_MAPPING,NATIVE_OPUS_ERR_VERSION,
        NATIVE_OPUS_ERR_MAPPING,NATIVE_OPUS_ERR_HEADER};
    for(unsigned i=0;i<5;++i) {
        init();stream_size=0;headers(11,version[i],ch[i],0,0,mapping[i],sizes[i]);
        assert(feed_all(1)==error[i]);size_t used=12;
        assert(native_opus_feed(&decoder,stream,stream_size,&used)==error[i] && used==0);
    }
    for(unsigned v=0;v<=15;v+=5) {
        init();stream_size=0;headers(12,v,2,0,-512,0,v>1?20:19);
        one(12,2,4,960,silence,sizeof(silence));assert(feed_all(7)==0);
        opus_int32 gain=0;assert(opus_decoder_ctl((OpusDecoder*)state.bytes,OPUS_GET_GAIN(&gain))==0);
        assert(gain==-512 && decoder.input_channels==2 && received==960 && decoder.chains==1);
    }
}
static void test_granules(void) {
    for(size_t fragment=1;fragment<=4096;fragment*=4) {
        init();stream_size=0;headers(30,1,1,1200,0,0,19);
        one(30,2,0,960,silence,sizeof(silence));one(30,3,4,1700,silence,sizeof(silence));
        assert(feed_all(fragment)==0 && received==500 && calls==1);
        assert(decoder.decoded_samples==1920 && decoder.output_samples==500 && last_bitrate==1200);
    }
    init();stream_size=0;headers(31,1,2,120,0,0,19);
    one(31,2,0,10960,silence,sizeof(silence));one(31,3,4,11500,silence,sizeof(silence));
    assert(feed_all(4096)==0 && received==1380 && decoder.granule_offset==10000);
    const uint8_t *p[]={silence,silence,silence};const size_t z[]={3,3,3};
    init();stream_size=0;headers(32,1,1,120,0,0,19);page(32,2,4,1100,p,z,3);
    assert(feed_all(4096)==0 && received==980 && calls==2);
    init();stream_size=0;headers(33,1,1,120,0,0,19);page(33,2,4,10000,p,z,3);
    assert(feed_all(3)==0 && received==2760 && decoder.granule_offset==7120);
    const uint64_t invalid[]={959,1000,1921,UINT64_MAX};
    for(unsigned i=0;i<4;++i) {
        init();stream_size=0;headers(34,1,1,0,0,0,19);
        if(!i)one(34,2,0,invalid[i],silence,sizeof(silence));
        else {one(34,2,0,960,silence,sizeof(silence));one(34,3,i==1?0:4,invalid[i],silence,sizeof(silence));}
        int r=feed_all(5);assert(r==NATIVE_OPUS_ERR_GRANULE || (i==3 && r==NATIVE_OPUS_ERR_DEMUX));
    }
    init();stream_size=0;headers(35,1,1,1200,0,0,19);one(35,2,4,960,silence,sizeof(silence));
    assert(feed_all(3)==NATIVE_OPUS_ERR_GRANULE && calls==0);
}
static void test_failures(void) {
    const uint8_t toc[]={0x80,0x90,0x98,0x10,0x18};const unsigned samples[]={120,480,960,1920,2880};
    for(unsigned i=0;i<sizeof(toc);++i) {
        init();stream_size=0;headers(40,1,1,0,0,0,19);one(40,2,4,samples[i],toc+i,1);
        assert(feed_all(1)==(samples[i]<=960?0:NATIVE_OPUS_ERR_DURATION));
        if(samples[i]<=960)assert(received==samples[i]);else assert(!calls && !decoder.audio_packets);
    }
    init();stream_size=0;headers(41,1,1,0,0,0,19);one(41,2,4,960,silence,sizeof(silence));
    cancel=true;assert(feed_all(4096)==NATIVE_OPUS_ERR_CANCELLED && calls==1 && !decoder.output_samples);
    assert(native_opus_finish(&decoder)==NATIVE_OPUS_ERR_CANCELLED && native_opus_reset(&decoder)==0);
    calls=received=0;cancel=false;assert(feed_all(4096)==0 && received==960);
    init();native_opus_config_t c=config();c.scratch_bytes=8;assert(native_opus_init(&decoder,&c)==0);
    assert(feed_all(4096)==NATIVE_OPUS_ERR_MEMORY && decoder.libopus_error==OPUS_ALLOC_FAIL && !calls);
    init();assert(feed_all(4096)==0 && received==960);
    init();--stream_size;assert(feed_all(1)==NATIVE_OPUS_ERR_TRUNCATED);
    init();++stream_size;stream[stream_size-1]^=1;assert(feed_all(4096)==NATIVE_OPUS_ERR_DEMUX && !calls);
    static uint8_t oversized[1537];
    oversized[0]=0xf8;
    init();stream_size=0;headers(42,1,1,0,0,0,19);one(42,2,4,960,oversized,sizeof(oversized));
    assert(feed_all(11)==NATIVE_OPUS_ERR_PACKET_SIZE && !calls);
}
static void test_chains(void) {
    init();stream_size=0;headers(51,1,1,120,-256,0,19);one(51,2,4,900,silence,sizeof(silence));
    headers(52,1,2,240,512,0,19);one(52,2,4,800,silence,sizeof(silence));
    assert(feed_all(4096)==0 && received==1340 && decoder.chains==2 && decoder.audio_packets==2);
    assert(decoder.decoded_samples==1920 && decoder.output_samples==received);
    opus_int32 gain=0;assert(opus_decoder_ctl((OpusDecoder*)state.bytes,OPUS_GET_GAIN(&gain))==0);
    assert(gain==512 && decoder.input_channels==2 && decoder.pre_skip==240);
}

static void test_live_join(void) {
    const uint8_t *packets[]={silence,silence,silence,silence,silence};
    const size_t lengths[]={3,3,3,3,3};
    init();stream_size=0;headers(91,1,2,356,0,0,19);
    page(91,2534,0,UINT64_C(10522378560),packets,lengths,5);
    page(91,2535,4,UINT64_C(10522383360),packets,lengths,5);
    assert(!decoder.demux.allow_live_join);
    assert(feed_all(1024)==NATIVE_OPUS_ERR_DEMUX && !calls);
    assert(decoder.demux_error==OGG_OPUS_DEMUX_ERR_SEQUENCE);
    assert(native_opus_reset(&decoder)==0 && !decoder.demux.allow_live_join);
    assert(feed_all(1024)==NATIVE_OPUS_ERR_DEMUX && !calls);
    native_opus_config_t c=config();
    assert(native_opus_init_ex(&decoder,&c,true)==0);
    assert(feed_all(1024)==0 && received==9600-356 && calls==10);
    assert(decoder.granule_offset==UINT64_C(10522373760));
    assert(native_opus_reset(&decoder)==0 && decoder.demux.allow_live_join);
    calls=received=0;
    assert(feed_all(7)==0 && received==9600-356 && calls==10);
    puts("Native live join: strict default, pre-skip, 64-bit granules and reset PASS");
}

typedef struct { FILE *golden; bool positioned; size_t samples; } capture_output_t;
static bool capture_output(void *ctx,const int16_t *data,size_t samples,uint32_t bitrate) {
    capture_output_t *capture=ctx;
    assert(bitrate==56000);
    if(!capture->positioned) {
        assert(fseek(capture->golden,(long)decoder.pre_skip*2,SEEK_SET)==0);
        capture->positioned=true;
    }
    for(size_t i=0;i<samples;++i) {
        const int lo=fgetc(capture->golden),hi=fgetc(capture->golden);
        assert(lo!=EOF && hi!=EOF);
        assert((uint16_t)data[i]==(uint16_t)((unsigned)lo|((unsigned)hi<<8)));
    }
    capture->samples+=samples;
    return true;
}
static int feed_capture(FILE *file) {
    uint8_t input[1024];
    size_t size;
    while((size=fread(input,1,sizeof(input),file))!=0) {
        size_t pos=0;
        for(;;) {
            size_t used=SIZE_MAX;
            const int result=native_opus_feed(&decoder,input+pos,size-pos,&used);
            assert(used<=size-pos);pos+=used;
            if(result<0)return result;
            if(result==NATIVE_OPUS_PACKET)continue;
            assert(pos==size);break;
        }
    }
    assert(!ferror(file));
    return 0;
}
static void test_live_capture(const char *filename,const char *golden_path) {
    FILE *file=fopen(filename,"rb"),*golden=fopen(golden_path,"rb");
    assert(file && golden);
    capture_output_t capture={golden,false,0};
    native_opus_config_t c=config();c.output=capture_output;c.output_ctx=&capture;
    c.scratch_bytes=6144;
    assert(native_opus_init(&decoder,&c)==0);
    assert(feed_capture(file)==NATIVE_OPUS_ERR_DEMUX);
    assert(decoder.demux_error==OGG_OPUS_DEMUX_ERR_SEQUENCE && !capture.samples);
    assert(native_opus_init_ex(&decoder,&c,true)==0);
    for(unsigned repeat=0;repeat<2;++repeat) {
        assert(fseek(file,0,SEEK_SET)==0);
        capture.positioned=false;capture.samples=0;
        assert(feed_capture(file)==0);
        assert(decoder.audio_packets==675 && decoder.decoded_samples==648000);
        assert(decoder.output_samples==647644 && capture.samples==647644);
        assert(fgetc(golden)==EOF && !ferror(golden));
        assert(native_opus_finish(&decoder)==NATIVE_OPUS_ERR_TRUNCATED);
        assert(native_opus_reset(&decoder)==0 && decoder.demux.allow_live_join);
    }
    assert(fclose(file)==0 && fclose(golden)==0);
    puts("Intense live capture: input1024 scratch6144, 675 packets, 647644 PCM samples exact twice PASS");
}

int main(int argc,char **argv) {
    test_memory();test_alignment();test_flash_table_reads();test_headers();test_granules();test_failures();test_chains();
    test_live_join();
    assert(argc==1 || argc==3);
    if(argc==3)test_live_capture(argv[1],argv[2]);
    assert(allocation_count==0);
    printf("Native Opus PASS: state=%zu adapter=%zu PCM=%zu no allocations\n",native_opus_decoder_size(),sizeof(decoder),sizeof(pcm));
    return 0;
}
