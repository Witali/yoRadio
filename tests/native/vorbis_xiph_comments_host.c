/* Independent metadata API fixture: no header/DSP/packet decoding. */
#include <assert.h>
#include <stdio.h>
#include "vorbis_xiph_alloc.h"
extern int xiph_comment_tests(void);
int main(void){
    assert(!xiph_port_test_live() && !xiph_port_test_bytes());
    int cases=xiph_comment_tests();
    assert(cases>0 && !xiph_port_test_live() && !xiph_port_test_bytes());
    printf("COMMENT_PASS cases=%d live=%zu bytes=%zu\n",cases,xiph_port_test_live(),xiph_port_test_bytes());
    return 0;
}
