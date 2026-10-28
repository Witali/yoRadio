/* Shared independent flash/OS SHA observers; the producer is now real JPEG. */
#define main synthetic_cache_contract_main
#include "native_test.c"
#undef main
#include "jpeg_backing.h"

static jpeg_nor_t scratch;
static jpeg_backing_t backing;
static uint8_t bitmap[(JPEG_CACHE_SCRATCH_BYTES/4096u+8u)/8u];
static size_t heap_current,heap_peak;
static unsigned decode_attempts;
static unsigned input_calls[128],input_count;
static jpeg_decode_check_t stop_reason;

static void *allocate(void *context,size_t bytes)
{
    /* Actual decoder context/pool requests, excluding OS provider/model buffers. */
    (void)context;void *p=malloc(bytes);if(p){heap_current+=bytes;if(heap_current>heap_peak)heap_peak=heap_current;}return p;
}

static void release(void *context,void *data,size_t bytes)
{
    /* Every decode/fatal path must release exactly the requested allocations. */
    (void)context;CHECK(bytes<=heap_current);heap_current-=bytes;free(data);
}

static jpeg_decode_check_t request_check(void *context)
{
    /* One owner stop cause covers source, output, SHA and all scratch handles. */
    (void)context;return model.allowed ? JPEG_CHECK_OK:stop_reason;
}

static int input(void *context,uint32_t offset,void *data,size_t bytes)
{
    /* The decoder consumes actual persistent bytes; no host-file source shortcut. */
    (void)context;CHECK(input_count<128);input_calls[input_count++]=model.calls+1;
    return jpeg_cache_read_source(&cache,offset,data,bytes);
}

static int output(void *context,uint32_t row,const uint16_t *pixels,uint32_t count)
{
    /* One decode validates the JPEG AND fills the provisional persistent cache. */
    (void)context;return jpeg_cache_write_row(&cache,row,pixels,count);
}

static void open_scratch(void)
{
    /* Same disposable NOR owner/capacity; stable monotonic handles across jobs. */
    jpeg_backing_abort(&backing);
    jpeg_nor_device_t device={&roles[3],FLASH_BYTES,256,read_device,program_device,erase_device};
    CHECK(jpeg_nor_open(&scratch,&device,jpeg_cache_scratch_extents,JPEG_CACHE_SCRATCH_EXTENTS,JPEG_CACHE_SCRATCH_BYTES,jpeg_layout.allowed,jpeg_layout.allowed_count)==0);
    CHECK(jpeg_backing_begin(&backing,&scratch,check,NULL,bitmap,sizeof(bitmap))==0);
}

static jpeg_cache_result_t prepare(jpeg_decoder_t *decoder,uint32_t length,jpeg_decode_diagnostic_t *d,bool *decoded)
{
    /* A cache miss rebuilds once; a verified hit never invokes libjpeg. */
    *decoded=false;jpeg_cache_result_t result=open_cache();if(result)return result;
    result=jpeg_cache_lookup(&cache,0,length);
    if(result==JPEG_CACHE_OK)return result;
    if(result!=JPEG_CACHE_MISS && result!=JPEG_CACHE_VERIFY)return result;
    if(result==JPEG_CACHE_VERIFY){abort_cache();result=open_cache();if(result)return result;}
    result=jpeg_cache_begin(&cache,0,length);if(result)return result;
    open_scratch();jpeg_decode_request_t request={NULL,length,240,240,input,output,request_check};
    *decoded=true;++decode_attempts;
    if(jpeg_decoder_decode(decoder,&request,d)!=JPEG_DECODE_OK)return cache.failed ? cache.last_error:JPEG_CACHE_STATE;
    return jpeg_cache_commit(&cache);
}

static jpeg_cache_result_t draw(const char *path)
{
    /* Read the verified frame without a decode, proving exact cached output bytes. */
    FILE *file=fopen(path,"wb");CHECK(file);uint16_t pixels[240];jpeg_cache_result_t result=JPEG_CACHE_OK;
    for(uint32_t y=0;y<240;++y) {
        result=jpeg_cache_read_row(&cache,y,pixels,240);if(result)break;
        CHECK(fwrite(pixels,2,240,file)==240);
    }
    CHECK(!fclose(file));return result;
}

static void canaries(void)
{
    /* All other photos/caches/immutable resources/settings remain byte-exact. */
    for(uint32_t at=0;at<FLASH_BYTES;at+=4096) {
        bool mutable=inside(at,4096,jpeg_cache_layout.frames[0].extents,jpeg_cache_layout.frames[0].count) ||
                     inside(at,4096,jpeg_cache_scratch_extents,JPEG_CACHE_SCRATCH_EXTENTS);
        for(unsigned b=0;b<2;++b)if(at==jpeg_cache_layout.journal.banks[b])mutable=true;
        if(!mutable)CHECK(!memcmp(flash_data+at,baseline+at,4096));
    }
}

static void record(const char *name,jpeg_cache_result_t result,const jpeg_decode_diagnostic_t *d,bool decoded)
{
    /* Domain-specific failures stay separate; rows are not published on errors. */
    printf("\"%s\":{\"cache_result\":%u,\"decoder_status\":\"%s\",\"decoded\":%s,\"callback_error\":%d,\"pool_peak\":%llu,\"required\":%llu,\"available\":%llu,\"rows\":%u,\"calls\":%u,\"program_bytes\":%llu,\"read_bytes\":%llu,\"erases\":%u,\"physical_fault_hits\":%u,\"hash_fault_hits\":%u,\"stop\":%u,\"source_calls\":%llu,\"frame_program_bytes\":%llu,\"scratch_program_bytes\":%llu,\"source_required\":%u,\"source_available\":%u,\"ready\":%s}",
        name,result,decoded ? jpeg_decoder_status_name(d->status):"not-run",decoded ? "true":"false",d->callback_error,(unsigned long long)d->pool_peak,
        (unsigned long long)d->required,(unsigned long long)d->available,d->rows,model.calls,(unsigned long long)model.program_bytes,(unsigned long long)model.read_bytes,model.erases,
        model.hits,model.hash_hits,model.allowed ? 0:stop_reason,(unsigned long long)model.role_calls[0],(unsigned long long)model.role_program_bytes[1],(unsigned long long)model.role_program_bytes[3],cache.required,cache.available,cache.journal.entries[0].ready ? "true":"false");
    printf(",\"%s_input_calls\":[",name);for(unsigned i=0;i<input_count;++i)printf("%s%u",i ? ",":"",input_calls[i]);printf("]");
}

int main(int argc,char **argv)
{
    /* Two full cache epochs over retained physical bytes and one reusable decoder. */
    if(argc!=4 && argc!=6)return 2;
    unsigned physical_fail=0,hash_fail=0,stop=0,fault_mode=1;stop_reason=JPEG_CHECK_CANCELLED;
    if(argc==6) {
        unsigned ordinal=(unsigned)strtoul(argv[5],NULL,10);if(!ordinal)return 2;
        if(!strcmp(argv[4],"physical"))physical_fail=ordinal;
        else if(!strcmp(argv[4],"silent")){physical_fail=ordinal;fault_mode=6;}
        else if(!strcmp(argv[4],"hash"))hash_fail=ordinal;
        else {stop=ordinal;if(!strcmp(argv[4],"time"))stop_reason=JPEG_CHECK_TIME;else if(!strcmp(argv[4],"budget"))stop_reason=JPEG_CHECK_IO_LIMIT;else if(strcmp(argv[4],"cancel"))return 2;}
    }
    CHECK(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)>=0);
    for(size_t i=0;i<FLASH_BYTES;++i)flash_data[i]=(uint8_t)(i*17u+(i>>9));
    for(unsigned b=0;b<2;++b)memset(flash_data+jpeg_cache_layout.journal.banks[b],0xff,4096);
    FILE *file=fopen(argv[1],"rb");CHECK(file && !fseek(file,0,SEEK_END));long length=ftell(file);
    CHECK(length>0 && !fseek(file,0,SEEK_SET));
    /* Oversized files exercise the actual capacity API without overflowing or
     * truncating the real source slot merely to make a decoder test pass. */
    if((uint32_t)length<=jpeg_cache_layout.journal.source_limit)
        CHECK(fread(flash_data+jpeg_cache_layout.source_offsets[0],1,(size_t)length,file)==(size_t)length);
    CHECK(!fclose(file));
    memcpy(baseline,flash_data,FLASH_BYTES);
    hash_provider=(jpeg_guard_sha256_t){NULL,hash_begin,hash_update,hash_finish,hash_reset};
    devices=(jpeg_cache_devices_t){
        {&roles[0],FLASH_BYTES,256,read_device,NULL,NULL},
        {&roles[1],FLASH_BYTES,256,read_device,program_device,erase_device},
        {&roles[2],FLASH_BYTES,256,read_device,program_device,erase_device}};
    fresh(0,0,0,0);open_scratch();jpeg_decoder_config_t config={{NULL,allocate,release},jpeg_backing_callbacks(&backing),65536,240,240};
    jpeg_decode_diagnostic_t d={0};jpeg_decoder_t *decoder=jpeg_decoder_create(&config,&d);CHECK(decoder);printf("{");
    for(unsigned cycle=0;cycle<2;++cycle) {
        if(cycle)printf(",");fresh(cycle ? 0:physical_fail,fault_mode,cycle ? 0:stop,cycle ? 0:hash_fail);input_count=0;
        d=(jpeg_decode_diagnostic_t){0};
        bool decoded;jpeg_cache_result_t result=prepare(decoder,(uint32_t)length,&d,&decoded);
        if(!result)result=draw(argv[cycle ? 3:2]);else {FILE *empty=fopen(argv[cycle ? 3:2],"wb");CHECK(empty && !fclose(empty));}
        record(cycle ? "recovery":"first",result,&d,decoded);
        canaries();abort_cache();unsigned calls=model.calls;jpeg_backing_abort(&backing);CHECK(model.calls==calls);
    }
    jpeg_decoder_destroy(decoder);CHECK(!heap_current && !live_hash && BCryptCloseAlgorithmProvider(algorithm,0)>=0);
    printf(",\"decode_attempts\":%u,\"heap_final\":%zu,\"heap_peak\":%zu}\n",decode_attempts,heap_current,heap_peak);return 0;
}
