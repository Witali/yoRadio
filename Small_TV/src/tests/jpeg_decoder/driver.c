/* Host adapter exercises the real portable decoder API; no network/LCD/device. */
#include "jpeg_decoder.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REQUIRE(v) do{if(!(v)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(1);}}while(0)
enum {NONE,ALLOC,INPUT,OUTPUT,OPEN,READ,WRITE,CLOSE,CANCEL,TIME,BUDGET,COUNT};
static const char *names[]={"none","alloc","input","output","open","read","write","close","cancel","time","budget"};
typedef struct {
    FILE *input,*output;
    uint32_t length,next_row;
    struct {FILE *file;uint64_t id;uint32_t bytes;} files[16];
    uint64_t next_id,current,peak,visits[COUNT],ordinal,hits;
    unsigned fault;
} host_t;

static int fail(host_t *h,unsigned kind)
{ /* One actual callback fails once; the allocator may legitimately retry. */
    ++h->visits[kind];int hit=kind==h->fault && h->visits[kind]==h->ordinal;if(hit)++h->hits;return hit;
}
static void *allocate(void *context,size_t bytes)
{ /* Track context and library pools, including retained permanent allocations. */
    host_t *h=context;if(fail(h,ALLOC))return NULL;void *data=malloc(bytes);
    if(data){h->current+=bytes;if(h->current>h->peak)h->peak=h->current;}return data;
}
static void release(void *context,void *data,size_t bytes)
{ /* A double free or accounting underflow is a test failure, not a recovery. */
    host_t *h=context;REQUIRE(bytes<=h->current);h->current-=bytes;free(data);
}
static int input(void *context,uint32_t offset,void *data,size_t bytes)
{ /* A failing transfer really reads a partial prefix. */
    host_t *h=context;REQUIRE(offset<=h->length && bytes<=h->length-offset);
    int error=fail(h,INPUT);if(fseek(h->input,(long)offset,SEEK_SET))return -90;
    size_t got=fread(data,1,error && bytes ? bytes-1 : bytes,h->input);return error || got!=bytes ? -77 : 0;
}
static int output(void *context,uint32_t y,const uint16_t *pixels,uint32_t count)
{ /* Real output is partial on failure; row publication remains the owner contract. */
    host_t *h=context;REQUIRE(y==h->next_row && count<=240);int error=fail(h,OUTPUT);
    size_t got=fwrite(pixels,sizeof(*pixels),error && count ? count-1 : count,h->output);
    if(error || got!=count)return -88;++h->next_row;return 0;
}
static jpeg_decode_check_t check(void *context)
{ /* Distinct reasons must survive both pre/post callback checkpoints. */
    host_t *h=context;if(fail(h,CANCEL))return JPEG_CHECK_CANCELLED;
    if(fail(h,TIME))return JPEG_CHECK_TIME;if(fail(h,BUDGET))return JPEG_CHECK_IO_LIMIT;return JPEG_CHECK_OK;
}
static unsigned slot(host_t *h,uint64_t id,uint32_t offset,size_t bytes)
{ /* Validate every backing callback independently of the decoder. */
    for(unsigned i=0;i<16;++i)if(h->files[i].file && h->files[i].id==id) {
        REQUIRE(offset<=h->files[i].bytes && bytes<=h->files[i].bytes-offset);return i;
    }
    REQUIRE(0);return 0;
}
static int open_store(void *context,uint32_t bytes,bool coefficients,uint64_t *handle)
{ /* Failed opens own nothing. Storage kind is accepted but stdio stays an oracle. */
    host_t *h=context;(void)coefficients;if(fail(h,OPEN))return -31;unsigned i=0;
    while(i<16 && h->files[i].file)++i;REQUIRE(i<16);
    FILE *file=tmpfile();if(!file)return -32;
    h->files[i].file=file;h->files[i].id=++h->next_id;h->files[i].bytes=bytes;*handle=h->next_id;return 0;
}
static int read_store(void *context,uint64_t id,uint32_t offset,void *data,size_t bytes)
{ /* Preserve partial read errors through the native API. */
    host_t *h=context;unsigned i=slot(h,id,offset,bytes);int error=fail(h,READ);
    if(fseek(h->files[i].file,(long)offset,SEEK_SET))return -33;
    size_t got=fread(data,1,error && bytes ? bytes-1 : bytes,h->files[i].file);return error || got!=bytes ? -34 : 0;
}
static int write_store(void *context,uint64_t id,uint32_t offset,const void *data,size_t bytes)
{ /* The test uses real partial file writes, not just fake failure counters. */
    host_t *h=context;unsigned i=slot(h,id,offset,bytes);int error=fail(h,WRITE);
    if(fseek(h->files[i].file,(long)offset,SEEK_SET))return -35;
    size_t got=fwrite(data,1,error && bytes ? bytes-1 : bytes,h->files[i].file);return error || got!=bytes ? -36 : 0;
}
static int close_store(void *context,uint64_t id)
{ /* Even an injected close error actually releases its handle during unwind. */
    host_t *h=context;unsigned i=slot(h,id,0,0);int error=fail(h,CLOSE);
    int result=fclose(h->files[i].file);h->files[i].file=NULL;return error || result ? -37 : 0;
}
static void print_result(const char *name,const jpeg_decode_diagnostic_t *d,const host_t *h)
{ /* External categories and exact limits are observable without libjpeg headers. */
    printf("\"%s\":{\"status\":\"%s\",\"detail\":%u,\"library_error\":%d,\"parameter\":%d,\"callback_error\":%d,"
           "\"required\":%llu,\"available\":%llu,\"available_known\":%s,\"pool_peak\":%llu,\"pool_retained\":%zu,"
           "\"backing_required\":%llu,\"backing_peak\":%llu,\"input_bytes\":%llu,\"width\":%u,\"height\":%u,\"rows\":%u,"
           "\"opened\":%u,\"closed\":%u,\"context_bytes\":%zu,\"reused_object\":%s,\"fault_hits\":%llu,\"visits\":{",
           name,jpeg_decoder_status_name(d->status),(unsigned)d->detail,d->library_error,d->library_parameter,d->callback_error,
           (unsigned long long)d->required,(unsigned long long)d->available,d->available_known ? "true":"false",
           (unsigned long long)d->pool_peak,d->pool_retained,(unsigned long long)d->backing_required,
           (unsigned long long)d->backing_peak,(unsigned long long)d->input_bytes,d->width,d->height,d->rows,
           d->stores_opened,d->stores_closed,d->context_bytes,d->reused_object ? "true":"false",(unsigned long long)h->hits);
    for(unsigned i=1;i<COUNT;++i)printf("%s\"%s\":%llu",i==1 ? "":",",names[i],(unsigned long long)h->visits[i]);
    printf("}");
    printf("}");
}

int main(int argc,char **argv)
{ /* Two cycles retain the same decoder, including recovery after a fatal error. */
    if(argc!=7 && argc!=9 && argc!=10)return 2;host_t h={0};
    if(argc>=9){for(unsigned i=1;i<COUNT;++i)if(!strcmp(argv[7],names[i]))h.fault=i;h.ordinal=strtoull(argv[8],NULL,10);if(!h.fault || !h.ordinal)return 2;}
    uint32_t maximum=(uint32_t)strtoul(argv[4],NULL,10);
    jpeg_decoder_config_t config={{&h,allocate,release},{&h,(uint32_t)strtoul(argv[6],NULL,10),open_store,read_store,write_store,close_store},(size_t)strtoull(argv[5],NULL,10),maximum,maximum};
    jpeg_decode_diagnostic_t diagnostic={0};jpeg_decoder_t *decoder=jpeg_decoder_create(&config,&diagnostic);
    printf("{");
    for(unsigned cycle=0;cycle<2;++cycle) {
        const char *path=cycle && argc==10 ? argv[9] : argv[1];h.input=fopen(path,"rb");h.output=fopen(argv[cycle ? 3:2],"wb");
        REQUIRE(h.input && h.output);REQUIRE(!fseek(h.input,0,SEEK_END));long length=ftell(h.input);REQUIRE(length>=0 && (uint64_t)length<=UINT32_MAX);h.length=(uint32_t)length;h.next_row=0;
        if(cycle){h.fault=NONE;h.hits=0;memset(h.visits,0,sizeof(h.visits));if(!decoder)decoder=jpeg_decoder_create(&config,&diagnostic);printf(",");}
        if(decoder){jpeg_decode_request_t request={&h,h.length,0,0,input,output,check};jpeg_decoder_decode(decoder,&request,&diagnostic);}
        REQUIRE(!fclose(h.input) && !fclose(h.output));print_result(cycle ? "recovery":"first",&diagnostic,&h);
        REQUIRE(diagnostic.stores_opened==diagnostic.stores_closed);for(unsigned i=0;i<16;++i)REQUIRE(!h.files[i].file);
    }
    jpeg_decoder_destroy(decoder);REQUIRE(!h.current);printf(",\"heap_final\":%llu,\"heap_peak\":%llu}\n",(unsigned long long)h.current,(unsigned long long)h.peak);return 0;
}
