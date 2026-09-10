/* Test-only inclusion of the real static mode and rate functions. The unused
 * mode constructors are renamed by the runner and discarded by section GC. */
#ifdef PULSE_PROBE_ENTRY
#include "../../esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/modes.c"
#include <assert.h>
#include <stdint.h>

#if YORADIO_OPUS_PULSE_WORD_ENABLED
uint32_t pulse_const_repeat(const void *p) {
    return yoradio_opus_pulse_word(p)+yoradio_opus_pulse_word(p);
}
#endif

#if YORADIO_OPUS_PULSE_WORD_ENABLED && defined(YORADIO_OPUS_PULSE_TEST_HOOKS)
static unsigned long pulse_reads;
static unsigned pulse_tables;
void yoradio_opus_pulse_test_word(const void *p) {
    const uintptr_t a=(uintptr_t)p;
    assert(!(a&3U));
    const void *tables[]={cache_index50,cache_bits50,cache_caps50};
    const unsigned sizes[]={sizeof(cache_index50),sizeof(cache_bits50),sizeof(cache_caps50)};
    int found=0;
    for(unsigned i=0;i<3;i++) if(a>=(uintptr_t)tables[i] && a+4<=(uintptr_t)tables[i]+sizes[i]) {
        found=1;pulse_tables|=1U<<i;
    }
    assert(found);pulse_reads++;
}
unsigned long pulse_test_reads(void) {return pulse_reads;}
unsigned pulse_test_tables(void) {return pulse_tables;}
#endif

int PULSE_PROBE_ENTRY(int kind,int lm,int band,int value) {
    const CELTMode *m=static_mode_list[0];
    switch(kind) {
    case 0:return yoradio_opus_pulse_read16(&m->cache.index[value]);
    case 1:return bits2pulses(m,band,lm,value);
    case 2:return pulses2bits(m,band,lm,value);
    case 3:return yoradio_opus_pulse_read8(&m->cache.bits[value]);
    case 4:return yoradio_opus_pulse_read8(&m->cache.caps[value]);
    default:assert(0);return -1;
    }
}
#else
#include <assert.h>
#include <stdio.h>
int pulse_reference(int,int,int,int);
int pulse_candidate(int,int,int,int);
unsigned long pulse_test_reads(void);
unsigned pulse_test_tables(void);
int main(void) {
    unsigned cases=0,rows=0;
    for(int kind=0;kind<=4;kind+=kind==0?3:1) {
        const int count=kind==0?105:kind==3?392:168;
        for(int i=0;i<count;i++) {
            assert(pulse_reference(kind,0,0,i)==pulse_candidate(kind,0,0,i));cases++;
        }
    }
    for(int lm=-1;lm<=3;lm++) for(int band=0;band<21;band++) {
        int index=pulse_reference(0,0,0,(lm+1)*21+band);
        if(index<0) continue;
        rows++;
        const int max=pulse_reference(3,0,0,index);
        for(int bits=-1;bits<=2048;bits++) {
            int a=pulse_reference(1,lm,band,bits),b=pulse_candidate(1,lm,band,bits);
            assert(a==b);cases++;
        }
        for(int q=0;q<=max;q++) {
            assert(pulse_reference(2,lm,band,q)==pulse_candidate(2,lm,band,q));cases++;
        }
    }
    assert(pulse_test_tables()==7);
    printf("{\"passed\":true,\"cases\":%u,\"rows\":%u,\"word_reads\":%lu,\"tables\":%u}\n",
           cases,rows,pulse_test_reads(),pulse_test_tables());
    return 0;
}
#endif
