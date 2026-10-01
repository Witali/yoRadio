"""Exercise PC16 cache coherence, stream ownership, tails and owner changes."""
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='pc16-cache-') as directory:
    tmp=Path(directory)
    (tmp/'test.c').write_text(r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "packed_complex16_cache.h"
#include "packed_complex16_fast.h"
static uint32_t rng=0x16ca4e01;
static uint32_t random_word(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static int32_t bits(uint32_t x){int32_t y;memcpy(&y,&x,4);return y;}
static unsigned long checks,hits;
static void exercise(size_t count){
    uint32_t *data=calloc(count,4),*exponents=calloc(pc16_exponent_words(count),4);
    assert(data && exponents);pc16_cache_t cache;pc16_cache_init(&cache);
    for(unsigned trial=0;trial<40000;++trial){
        size_t n=trial<count?trial:random_word()%count;
        unsigned slot=n%4; // Stable, disjoint stream ownership, including shared blocks.
        int32_t a,b,c,d;
        hits+=pc16_cache_load(&cache,slot,data,exponents,count,n,&a,&b);
        pc16_load(data,exponents,n,&c,&d);assert(a==c && b==d);++checks;
        assert(pc16_cache_load(&cache,slot,data,exponents,count,n,&a,&b));
        assert(a==c && b==d);++checks;
        if(trial%3){
            int32_t re=bits(random_word()),im=bits(random_word());unsigned e;
            data[n]=pc16_pack_fast(re,im,&e,NULL);
            unsigned shift=(n%8)*4;
            exponents[n/8]=(exponents[n/8]&~(15u<<shift))|(e<<shift);
            pc16_cache_invalidate(&cache,slot,n);
            assert(!pc16_cache_load(&cache,slot,data,exponents,count,n,&a,&b));
            pc16_load(data,exponents,n,&c,&d);assert(a==c && b==d);++checks;
        }
        if(trial%997==0){
            // A new owner, including different exponent words, cannot reuse old entries.
            memset(data,0,count*4);memset(exponents,0,pc16_exponent_words(count)*4);
            pc16_cache_init(&cache);
        }
    }
    free(exponents);free(data);
}
int main(void){
    for(size_t n=1;n<=17;++n)exercise(n);
    exercise(617);exercise(1029);
    assert(hits);printf("PC16_CACHE_PASS checks=%lu hits=%lu cache_bytes=%zu\n",checks,hits,sizeof(pc16_cache_t));
}
''',encoding='utf-8')
    exe=tmp/'test'
    subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',
                    '-fsanitize=address,undefined','-fno-omit-frame-pointer',
                    '-I'+str(ROOT/'idf/esp32c3-oled-native/main'),str(tmp/'test.c'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
