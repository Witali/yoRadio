// Compare checked FIL parsing against the actual pinned decoder, not a mock.
#include "aac_fill_parser.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

void __real_getfill(aac_fill_bits_t *);
void __real_get_sbr_bitstream(aac_fill_stream_t *,aac_fill_bits_t *);

static void put(uint8_t *data,unsigned *cursor,unsigned value,unsigned width) {
    for(unsigned i=width;i>0;--i,++*cursor) {
        unsigned mask=1u<<(7-*cursor%8);
        data[*cursor/8]=(data[*cursor/8]&~mask)|(((value>>(i-1))&1)?mask:0);
    }
}

void qemu_aac_fill_test(void) {
    uint8_t data[280];aac_fill_stream_t native,checked;
    unsigned cases=0;
    // All count encodings (including escape=0), bit alignments, extension
    // types and both empty/full SBR slots. Padding only protects the native
    // implementation's wide loads; the host test gives the new parser none.
    for(unsigned alignment=0;alignment<8;++alignment)
    for(unsigned encoding=0;encoding<271;++encoding)
    for(unsigned extension=0;extension<16;++extension)
    for(unsigned full=0;full<2;++full) {
        memset(data,0xa5,sizeof(data));unsigned cursor=alignment;
        unsigned count=encoding<15?encoding:encoding-1;
        put(data,&cursor,encoding<15?encoding:15,4);
        if(encoding>=15)put(data,&cursor,encoding-15,8);
        if(count) { unsigned payload=cursor;put(data,&payload,extension,4); }
        unsigned end=cursor+count*8, bytes=(end+7)/8;
        aac_fill_bits_t before={data,alignment,end,bytes,0},nb=before,cb=before;
        memset(&native,0x39,sizeof(native));native.elements=full;native.core_elements=1;
        checked=native;
        __real_get_sbr_bitstream(&native,&nb);
        assert(aac_fill_sbr(&checked,&cb));
        assert(nb.used_bits==end && cb.used_bits==end);
        assert(!memcmp(&native,&checked,sizeof(native)));
        nb=before;cb=before;
        __real_getfill(&nb);assert(aac_fill_skip(&cb));
        assert(nb.used_bits==end && cb.used_bits==end);
        if(++cases%512==0)vTaskDelay(1);
    }
    // Reproduce the vendor's logical overread using padded backing storage:
    // a complete count header advertises 269 bytes in a declared two-byte input.
    // Direct native calls stay inside data[], but read beyond input_length.
    memset(data,0xa5,sizeof(data));unsigned cursor=0;
    put(data,&cursor,15,4);put(data,&cursor,255,8);put(data,&cursor,AAC_FIL_SBR,4);
    memset(&native,0,sizeof(native));checked=native;
    aac_fill_bits_t nb={data,0,16,2,0},cb=nb;
    __real_get_sbr_bitstream(&native,&nb);
    assert(nb.used_bits>nb.available_bits && native.element[0].payload[2]);
    assert(!aac_fill_sbr(&checked,&cb) && cb.used_bits==16 && !checked.elements);
    unsigned sbr_overrun=nb.used_bits;
    nb=(aac_fill_bits_t){data,0,16,2,0};cb=nb;
    __real_getfill(&nb);
    assert(nb.used_bits>nb.available_bits);
    assert(!aac_fill_skip(&cb) && cb.used_bits==16);
    printf("AAC_FIL_NATIVE_OVERRUN sbr_cursor=%u fill_cursor=%u frame_bits=16 checked_cursor=16\n",
           sbr_overrun,(unsigned)nb.used_bits);
    printf("AAC_FIL_PARSER_PASS valid_cases=%u count_encodings=271 alignments=8 extension_types=16 slot_states=2\n",cases);
}
