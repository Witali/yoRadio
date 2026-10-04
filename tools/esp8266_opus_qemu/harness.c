/* Execute an unchanged linked Opus decoder, not ESP8266 SDK startup.
 * The sim board's generous RAM is NOT evidence of firmware RAM headroom.
 * Firmware decoder/scratch functions and setjmp/longjmp are used as linked.
 */
#include <stdint.h>
#include <stddef.h>
#include "fixtures.h"
#ifndef QEMU_SELF_TESTS
#define QEMU_SELF_TESTS 1
#endif
#ifndef QEMU_FAULT_GUARD
#define QEMU_FAULT_GUARD 0
#endif

extern int opus_decoder_get_size(int channels);
extern int opus_decoder_init(void *decoder, int rate, int channels);
extern void yoradio_opus_memory_bind(void *, size_t, void *, size_t);
extern int yoradio_opus_decode_bounded(void *, const unsigned char *, int, int16_t *, int);
extern size_t yoradio_opus_scratch_peak_bytes(void);
extern size_t yoradio_opus_scratch_peak_words(void);

#define GUARD 0x5a39ce71u
static struct { uint32_t pre[2], data[6144 / 4], post[2]; } bytes;
/* Separate word arena in the actual IRAM address range. QEMU does not by
 * itself enforce ESP8266's word-only data access restriction. */
#define WORDS ((volatile uint32_t *)0x40108000u)
#define WORD_CAPACITY 16384u
static struct { uint32_t pre[2], data[24000 / 4], post[2]; } state;
static struct { uint32_t pre[2]; int16_t data[5760]; uint32_t post[2]; } pcm;
static unsigned state_bytes;
static uint32_t first_hash;

static void write_text(const char *p, unsigned n) {
    register unsigned a2 __asm__("a2") = 4;
    register unsigned a3 __asm__("a3") = 1;
    register const char *a4 __asm__("a4") = p;
    register unsigned a5 __asm__("a5") = n;
    __asm__ volatile("simcall" : "+a"(a2), "+a"(a3) : "a"(a4), "a"(a5) : "memory");
}
static void text(const char *s) { unsigned n=0; while(s[n]) ++n; write_text(s,n); }
static void hex32(uint32_t v) {
    static const char digits[]="0123456789abcdef";
    char b[9]; for(unsigned i=0;i<8;++i) b[i]=digits[(v>>(28-i*4))&15];
    b[8]=' '; write_text(b,9);
}
void qemu_trap(unsigned cause, unsigned pc, unsigned address) {
    text("TRAP "); hex32(cause); hex32(pc); hex32(address); text("\n");
    register unsigned a2 __asm__("a2")=1, a3 __asm__("a3")=90;
    __asm__ volatile("simcall" : "+a"(a2), "+a"(a3) :: "memory");
    for(;;) {}
}
static int guards(void) {
    const unsigned char *s=(const unsigned char *)state.data;
    for(unsigned i=state_bytes;i<sizeof(state.data);++i) if(s[i]!=0xa5) return 0;
    return *(volatile uint32_t *)0x3fff6000u==0xa5a5a5a5u &&
        bytes.pre[0]==GUARD && bytes.pre[1]==GUARD && bytes.post[0]==GUARD && bytes.post[1]==GUARD &&
        state.pre[0]==GUARD && state.pre[1]==GUARD && state.post[0]==GUARD && state.post[1]==GUARD &&
        pcm.pre[0]==GUARD && pcm.pre[1]==GUARD && pcm.post[0]==GUARD && pcm.post[1]==GUARD &&
        WORDS[0]==GUARD && WORDS[1]==GUARD && WORDS[4098]==GUARD && WORDS[4099]==GUARD;
}
static void initialize_guards(void) {
    for(unsigned i=0;i<sizeof(state.data)/4;++i) state.data[i]=0xa5a5a5a5u;
    for(unsigned i=0;i<2;++i) {
        bytes.pre[i]=bytes.post[i]=state.pre[i]=state.post[i]=pcm.pre[i]=pcm.post[i]=GUARD;
        WORDS[i]=WORDS[4098+i]=GUARD;
    }
}
static void emit_pcm(int samples) {
    static const char digits[]="0123456789abcdef";
    char line[133];
    for(int i=0;i<samples;) {
        unsigned p=0; line[p++]='P'; line[p++]=' ';
        for(unsigned j=0;j<32 && i<samples;++j,++i) {
            uint16_t v=(uint16_t)pcm.data[i];
            line[p++]=digits[(v>>4)&15]; line[p++]=digits[v&15];
            line[p++]=digits[(v>>12)&15]; line[p++]=digits[(v>>8)&15];
        }
        line[p++]='\n'; write_text(line,p);
    }
}
static uint32_t pcm_hash(int samples) {
    uint32_t h=2166136261u;
    for(int i=0;i<samples;++i) { uint16_t v=(uint16_t)pcm.data[i];h=(h^(v&255))*16777619u;h=(h^(v>>8))*16777619u; }
    return h;
}
uint32_t q_udiv(uint32_t,uint32_t);
uint32_t q_umod(uint32_t,uint32_t);
int32_t q_sdiv(int32_t,int32_t);
uint64_t q_muldi(uint64_t,uint64_t);
int qemu_main(void) {
    const unsigned decoder_bytes=opus_decoder_get_size(1);
    text("STATE "); hex32(decoder_bytes); text("\n");
    if(!decoder_bytes || decoder_bytes>sizeof(state.data)) return 10;
    state_bytes=decoder_bytes;
    if(q_udiv(0xffffffffu,3)!=0x55555555u || q_umod(0xffffffffu,0x80000000u)!=0x7fffffffu ||
       q_sdiv(-2000000000,3)!=-666666666 || q_muldi(0xffffffffffffffffull,0xffffffffffffffffull)!=1ull ||
       q_muldi(0x123456789abcdef0ull,0xfedcba9876543210ull)!=0x236d88fe5618cf00ull) return 15;
    for(unsigned f=0;f<FIXTURE_COUNT;++f) {
        initialize_guards();
        yoradio_opus_memory_bind(bytes.data,sizeof(bytes.data),(void *)(WORDS+2),WORD_CAPACITY);
        int result=opus_decoder_init(state.data,48000,1);
        if(result) { text("INIT "); hex32((uint32_t)result); return 11; }
        text("BEGIN "); text(fixtures[f].name); text("\n");
        unsigned samples=0,packets=0,offset=0;
        while(offset<fixtures[f].bytes) {
            if(fixtures[f].bytes-offset<2) return 12;
            const unsigned char *p=fixtures[f].data+offset;
            unsigned n=p[0]|((unsigned)p[1]<<8); offset+=2;
            if(!n || offset+n>fixtures[f].bytes) return 12;
            result=yoradio_opus_decode_bounded(state.data,p+2,n,pcm.data,5760);
            if(result<=0 || result>5760) { text("DECODE ");hex32(result);hex32(packets);text("\n"); return 13; }
            if(!guards()) return 14;
            if(!packets) first_hash=pcm_hash(result);
            emit_pcm(result); samples+=(unsigned)result; ++packets; offset+=n;
        }
        text("END "); hex32(samples);hex32(packets);hex32(yoradio_opus_scratch_peak_bytes());
        hex32(yoradio_opus_scratch_peak_words());text("\n");
#if QEMU_SELF_TESTS
        const unsigned char *p=fixtures[f].data;
        unsigned n=p[0]|((unsigned)p[1]<<8);
        /* Force bounded scratch OOM, then explicitly rebuild state. */
        yoradio_opus_memory_bind(bytes.data,16,(void *)(WORDS+2),WORD_CAPACITY);
        if(opus_decoder_init(state.data,48000,1)) return 16;
        if(yoradio_opus_decode_bounded(state.data,p+2,n,pcm.data,5760)!=-7 || !guards()) return 17;
        yoradio_opus_memory_bind(bytes.data,sizeof(bytes.data),(void *)(WORDS+2),WORD_CAPACITY);
        if(opus_decoder_init(state.data,48000,1)) return 18;
        result=yoradio_opus_decode_bounded(state.data,p+2,n,pcm.data,5760);
        if(result<=0 || pcm_hash(result)!=first_hash || !guards()) return 19;
        text("RECOVERY PASS\n");
#endif
    }
    if(QEMU_FAULT_GUARD) bytes.post[0]^=1;
    if(!guards()) return 20;
    unsigned untouched=0; volatile uint32_t *stack=(volatile uint32_t *)0x3fff6000u;
    while(untouched<2048 && stack[untouched]==0xa5a5a5a5u) ++untouched;
    text("STACK_USED ");hex32(8192-untouched*4);text("\n");
    text("PASS\n"); return 0;
}

/* Functional ROM substitutes: their instructions/timing are NOT Espressif ROM.
 * Names and trampolines are explicit; no decoder instruction is changed. */
void *q_memcpy(void *d,const void *s,size_t n) {
    unsigned char *a=d; const unsigned char *b=s;
    for(size_t i=0;i<n;++i) a[i]=b[i]; return d;
}
void *q_memmove(void *d,const void *s,size_t n) {
    unsigned char *a=d; const unsigned char *b=s;
    if((uintptr_t)a>(uintptr_t)b) while(n) { --n; a[n]=b[n]; }
    else for(size_t i=0;i<n;++i) a[i]=b[i]; return d;
}
void *q_memset(void *d,int v,size_t n) {
    unsigned char *a=d; for(size_t i=0;i<n;++i) a[i]=(unsigned char)v; return d;
}
uint32_t q_udiv(uint32_t n,uint32_t d) {
    if(!d) { qemu_trap(0xd1,0,0); return 0; }
    uint32_t q=0,r=0;
    for(int i=31;i>=0;--i) { unsigned high=r>>31;r=(r<<1)|((n>>i)&1);if(high||r>=d){r-=d;q|=1u<<i;} }
    return q;
}
uint32_t q_umod(uint32_t n,uint32_t d) { return n-q_udiv(n,d)*d; }
int32_t q_sdiv(int32_t n,int32_t d) {
    unsigned neg=(n<0)^(d<0);uint32_t a=n<0?0u-(uint32_t)n:(uint32_t)n;
    uint32_t b=d<0?0u-(uint32_t)d:(uint32_t)d,v=q_udiv(a,b);
    return (int32_t)(neg?0u-v:v);
}
uint64_t q_muldi(uint64_t a,uint64_t b) {
    uint32_t al=(uint32_t)a,bl=(uint32_t)b;
    uint32_t a0=al&65535,a1=al>>16,b0=bl&65535,b1=bl>>16;
    uint32_t w0=a0*b0,t=a1*b0+(w0>>16),w1=t&65535,w2=t>>16;
    w1+=a0*b1;
    uint32_t lo=(w1<<16)|(w0&65535),hi=a1*b1+w2+(w1>>16);
    hi+=(uint32_t)(a>>32)*bl+al*(uint32_t)(b>>32);
    return ((uint64_t)hi<<32)|lo;
}
