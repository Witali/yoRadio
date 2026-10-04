#include "aac_fill_parser.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void put(uint8_t *data,unsigned cursor,unsigned value,unsigned width) {
    for(unsigned i=0;i<width;++i) {
        unsigned mask=1u<<(7-(cursor+i)%8);
        if((value>>(width-1-i))&1)data[(cursor+i)/8]|=mask;
        else data[(cursor+i)/8]&=~mask;
    }
}
// Independent bit-at-a-time oracle, deliberately unlike the production loads.
static unsigned peek(const uint8_t *data,unsigned start,unsigned width) {
    unsigned value=0;
    for(unsigned i=0;i<width;++i)value=value*2+((data[(start+i)/8]>>(7-(start+i)%8))&1);
    return value;
}

static unsigned valid_cases,truncated_cases,invalid_states;

static void valid(const uint8_t *source,unsigned begin,unsigned payload,unsigned count,
                  unsigned extension,unsigned full) {
    unsigned end=payload+count*8,bytes=(end+7)/8;
    uint8_t *data=malloc(bytes);assert(data);memcpy(data,source,bytes);
    aac_fill_stream_t stream,expected;
    memset(&stream,0x39,sizeof(stream));stream.elements=full;stream.core_elements=1;
    expected=stream;
    if(count && !full && (extension==13 || extension==14)) {
        expected.elements=1;
        expected.element[0].extension_type=extension;
        expected.element[0].payload_bytes=count;
        expected.element[0].payload[0]=peek(data,payload+4,4);
        for(unsigned i=1;i<count;++i)expected.element[0].payload[i]=peek(data,payload+i*8,8);
    }
    aac_fill_bits_t bits={data,begin,end,bytes,0};
    assert(aac_fill_sbr(&stream,&bits));
    assert(bits.used_bits==end && !memcmp(&stream,&expected,sizeof(stream)));
    bits.used_bits=begin;assert(aac_fill_skip(&bits) && bits.used_bits==end);
    free(data);++valid_cases;
}

static void truncated(const uint8_t *source,unsigned begin,unsigned available) {
    unsigned bytes=(available+7)/8;
    uint8_t *data=bytes?malloc(bytes):NULL;
    if(bytes) { assert(data);memcpy(data,source,bytes); }
    aac_fill_stream_t stream,expected;
    memset(&stream,0x39,sizeof(stream));stream.elements=0;stream.core_elements=1;expected=stream;
    aac_fill_bits_t bits={data,begin,available,bytes,0};
    assert(!aac_fill_sbr(&stream,&bits));
    assert(bits.used_bits==bytes*8 && !memcmp(&stream,&expected,sizeof(stream)));
    bits.used_bits=begin;
    assert(!aac_fill_skip(&bits) && bits.used_bits==bytes*8);
    free(data);++truncated_cases;
}

int main(void) {
    uint8_t data[280];
    for(unsigned alignment=0;alignment<8;++alignment)
    for(unsigned encoding=0;encoding<271;++encoding) {
        unsigned count=encoding<15?encoding:encoding-1;
        unsigned payload=alignment+(encoding<15?4:12),end=payload+count*8;
        memset(data,0xa5,sizeof(data));
        put(data,alignment,encoding<15?encoding:15,4);
        if(encoding>=15)put(data,alignment+4,encoding-15,8);
        for(unsigned extension=0;extension<16;++extension) {
            if(count)put(data,payload,extension,4);
            for(unsigned full=0;full<2;++full)valid(data,alignment,payload,count,extension,full);
        }
        if(count)put(data,payload,13,4);
        // Every whole-byte prefix, all incomplete count-header bits and the
        // last seven payload bits. Buffers have no readable padding under ASan.
        for(unsigned cut=0;cut<end;cut+=8)truncated(data,alignment,cut);
        for(unsigned cut=0;cut<payload;++cut)truncated(data,alignment,cut);
        for(unsigned cut=end>7?end-7:0;cut<end;++cut)truncated(data,alignment,cut);
    }
    for(int slot=-1;slot<=2;slot+=3) {
        aac_fill_stream_t stream,expected;
        memset(&stream,0x39,sizeof(stream));stream.elements=slot;expected=stream;
        uint8_t input[2]={0x1d,0x80}; // count=1, SBR=13, payload nibble=8
        aac_fill_bits_t bits={input,0,12,2,0};
        assert(!aac_fill_sbr(&stream,&bits) && bits.used_bits==16);
        assert(!memcmp(&stream,&expected,sizeof(stream)));++invalid_states;
    }
    aac_fill_bits_t invalid={data,UINT32_MAX,16,2,0};
    assert(!aac_fill_skip(&invalid) && invalid.used_bits==16);++invalid_states;
    invalid=(aac_fill_bits_t){NULL,0,16,2,0};
    assert(!aac_fill_skip(&invalid) && invalid.used_bits==16);++invalid_states;
    printf("AAC_FIL_HOST_PASS valid=%u truncated=%u invalid_state=%u padding=0\n",
           valid_cases,truncated_cases,invalid_states);
}
