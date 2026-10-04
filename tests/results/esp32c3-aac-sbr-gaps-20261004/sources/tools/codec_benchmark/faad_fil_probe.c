// Trace only syntax spans in a separate, pinned FAAD parser build.
// The generator verifies this trace before removing a complete SBR element.
#include "common.h"
#include "structs.h"
#include "neaacdec.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

static unsigned frame_index;
void yoradio_trace_fil(unsigned begin, unsigned payload, unsigned end,
                       unsigned type, unsigned count) {
    printf("FIL %u %u %u %u %u %u\n",frame_index,begin,payload,end,type,count);
}

int main(int argc,char **argv) {
    assert(argc==2);
    FILE *f=fopen(argv[1],"rb");assert(f);
    assert(!fseek(f,0,SEEK_END));long length=ftell(f);rewind(f);assert(length>0);
    unsigned char *data=calloc(1,length+1024);assert(data);
    assert(fread(data,1,length,f)==(size_t)length);fclose(f);
    NeAACDecHandle decoder=NeAACDecOpen();assert(decoder);
    unsigned long rate;unsigned char channels;
    long pos=NeAACDecInit(decoder,data,length,&rate,&channels);assert(pos==0);
    while(pos+7<=length) {
        assert(data[pos]==0xff && (data[pos+1]&0xf6)==0xf0);
        unsigned size=((data[pos+3]&3)<<11)|(data[pos+4]<<3)|(data[pos+5]>>5);
        assert(size>=7 && pos+size<=length);
        NeAACDecFrameInfo info;
        void *pcm=NeAACDecDecode(decoder,&info,data+pos,size);
        printf("FRAME %u %u %lu %lu %lu %u %u %u %u\n",frame_index,size,
               info.bytesconsumed,info.samples,info.samplerate,info.channels,
               info.error,info.sbr,((NeAACDecStruct *)decoder)->ps_used_global!=0);
        assert(pcm && !info.error && info.bytesconsumed==size);
        pos+=size;++frame_index;
    }
    assert(pos==length);NeAACDecClose(decoder);free(data);return 0;
}
