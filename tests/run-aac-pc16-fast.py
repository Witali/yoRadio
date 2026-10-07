"""Check optimized PC16 packing against the previously qualified implementation."""
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='pc16-fast-') as directory:
    tmp=Path(directory)
    (tmp/'test.c').write_text(r'''
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "packed_complex16_fast.h"
static unsigned long checked;
static int32_t bits(uint32_t x){int32_t y;memcpy(&y,&x,4);return y;}
static void check(int32_t r,int32_t i){
    unsigned ea,eb,ca,cb;
    uint32_t a=pc16_pack(r,i,&ea,&ca),b=pc16_pack_fast(r,i,&eb,&cb);
    assert(a==b && ea==eb && ca==cb);++checked;
}
int main(void){
    uint32_t seed=0x16faa032;
    for(unsigned n=0;n<2000000;++n){
        seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;int32_t r=bits(seed);
        seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;check(r,bits(seed));
    }
    for(unsigned shift=1;shift<=16;++shift)for(int m=-32768;m<=32767;++m){
        int64_t value=(int64_t)m*(1u<<shift);
        for(int d=-1;d<=1;++d){int64_t x=value+d;
            if(x>=INT32_MIN && x<=INT32_MAX){check((int32_t)x,0);check(0,(int32_t)x);}
        }
    }
    check(INT32_MIN,INT32_MAX);check(INT32_MAX,INT32_MIN);check(0,0);
    printf("PC16_FAST_PASS pairs=%lu words, exponents and saturation counts identical\n",checked);
}
''')
    exe=tmp/'test'
    subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=undefined',
                    '-I'+str(ROOT/'idf/esp32c3-oled-native/main'),str(tmp/'test.c'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
