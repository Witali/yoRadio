/* Reuse bounded file/allocator/RGB output observers, replacing only backing I/O. */
#define main stdio_decoder_driver_main
#include "../jpeg_decoder/driver.c"
#undef main
#include "jpeg_backing.h"
#include "nor_model.h"
#include "scratch_fixture.h"

static jpeg_nor_t nor;
static jpeg_backing_t backing;
static uint8_t bitmap[(SCRATCH_LOGICAL_BYTES/4096u+8u)/8u];
static uint64_t stop_at;
static jpeg_decode_check_t stop_reason;
static jpeg_nor_device_t model_device;

static int storage_check(void *context)
{
    /* Stop a physical job without resetting or rolling back its partial bytes. */
    (void)context;if(stop_at && scratch_model_stats().calls>=stop_at)scratch_model_allow(false);
    return scratch_model_check(NULL);
}

static jpeg_decode_check_t request_check(void *context)
{
    /* This owner knows whether a transport failure came from time or I/O quota. */
    if(storage_check(NULL))return stop_reason;
    return check(context);
}

static int bounded_read(void *context,uint32_t offset,void *data,size_t bytes)
{
    /* Model the real transport's pre/post check around every physical call. */
    (void)context;if(storage_check(NULL))return -78;
    int result=model_device.read(model_device.context,offset,data,bytes);
    return result ? result:storage_check(NULL);
}

static int bounded_program(void *context,uint32_t offset,const void *data,size_t bytes)
{
    /* A compound NOR flush must not issue another page after revocation. */
    (void)context;if(storage_check(NULL))return -78;
    int result=model_device.program(model_device.context,offset,data,bytes);
    return result ? result:storage_check(NULL);
}

static int bounded_erase(void *context,uint32_t offset)
{
    /* The callback already in progress may finish, but later callbacks stop. */
    (void)context;if(storage_check(NULL))return -78;
    int result=model_device.erase_sector(model_device.context,offset);
    return result ? result:storage_check(NULL);
}

static void begin_job(uint64_t physical_fail,uint64_t stop)
{
    /* Fresh counters/checkpoints, retained physical flash and monotonic file IDs. */
    uint64_t calls=scratch_model_stats().calls;jpeg_backing_abort(&backing);REQUIRE(scratch_model_stats().calls==calls);
    stop_at=stop;scratch_model_begin(256,physical_fail,1);model_device=scratch_model_device();
    jpeg_nor_device_t device={NULL,model_device.flash_bytes,model_device.page_bytes,bounded_read,bounded_program,bounded_erase};
    REQUIRE(jpeg_nor_open(&nor,&device,scratch_extents,SCRATCH_EXTENT_COUNT,SCRATCH_LOGICAL_BYTES,scratch_extents,SCRATCH_EXTENT_COUNT)==0);
    REQUIRE(jpeg_backing_begin(&backing,&nor,storage_check,NULL,bitmap,sizeof(bitmap))==0);
}

static void physical(const scratch_model_stats_t *stats)
{
    /* These are per-job issued operations, not cumulative traffic or chip endurance. */
    printf("{\"calls\":%llu,\"read_bytes\":%llu,\"program_bytes\":%llu,\"erases\":%llu,\"fault_hits\":%llu}",
        (unsigned long long)stats->calls,(unsigned long long)stats->read_bytes,(unsigned long long)stats->program_bytes,
        (unsigned long long)stats->erases,(unsigned long long)stats->hits);
}

int main(int argc,char **argv)
{
    /* Same decoder and adapter across jobs; no host temporary backing files. */
    if(argc!=7 && argc!=9 && argc!=10)return 2;
    uint64_t failed=0,stop=0;stop_reason=JPEG_CHECK_CANCELLED;
    if(argc>=9) {
        uint64_t n=strtoull(argv[8],NULL,10);if(!n)return 2;
        if(!strcmp(argv[7],"physical"))failed=n;
        else {
            stop=n;
            if(!strcmp(argv[7],"time"))stop_reason=JPEG_CHECK_TIME;
            else if(!strcmp(argv[7],"budget"))stop_reason=JPEG_CHECK_IO_LIMIT;
            else if(strcmp(argv[7],"cancel"))return 2;
        }
    }
    host_t h={0};begin_job(failed,stop);jpeg_decode_backing_t callbacks=jpeg_backing_callbacks(&backing);
    uint32_t capacity=(uint32_t)strtoul(argv[6],NULL,10);if(capacity>callbacks.capacity)return 2;callbacks.capacity=capacity;
    uint32_t maximum=(uint32_t)strtoul(argv[4],NULL,10);
    jpeg_decoder_config_t config={{&h,allocate,release},callbacks,(size_t)strtoull(argv[5],NULL,10),maximum,maximum};
    jpeg_decode_diagnostic_t diagnostic={0};jpeg_decoder_t *decoder=jpeg_decoder_create(&config,&diagnostic);REQUIRE(decoder);
    scratch_model_stats_t first_physical={0},second_physical={0};uint64_t first_id=0;printf("{");
    for(unsigned cycle=0;cycle<2;++cycle) {
        if(cycle){begin_job(0,0);memset(h.visits,0,sizeof(h.visits));printf(",");}
        const char *path=cycle && argc==10 ? argv[9]:argv[1];h.input=fopen(path,"rb");h.output=fopen(argv[cycle ? 3:2],"wb");
        REQUIRE(h.input && h.output && !fseek(h.input,0,SEEK_END));long length=ftell(h.input);REQUIRE(length>=0 && (uint64_t)length<=UINT32_MAX);h.length=(uint32_t)length;h.next_row=0;
        jpeg_decode_request_t request={&h,h.length,0,0,input,output,request_check};jpeg_decoder_decode(decoder,&request,&diagnostic);
        REQUIRE(!fclose(h.input) && !fclose(h.output));print_result(cycle ? "recovery":"first",&diagnostic,&h);
        REQUIRE(diagnostic.stores_opened==diagnostic.stores_closed && !backing.scratch.active_files && scratch_model_canaries());
        if(!cycle){first_physical=scratch_model_stats();first_id=backing.scratch.next_id;}
        else second_physical=scratch_model_stats();
    }
    uint64_t final_id=backing.scratch.next_id;jpeg_decoder_destroy(decoder);uint64_t calls=scratch_model_stats().calls;jpeg_backing_abort(&backing);
    REQUIRE(!h.current && scratch_model_stats().calls==calls);
    printf(",\"physical_first\":");physical(&first_physical);printf(",\"physical_recovery\":");physical(&second_physical);
    printf(",\"first_last_id\":%llu,\"recovery_last_id\":%llu,\"heap_final\":%llu,\"heap_peak\":%llu}\n",
        (unsigned long long)first_id,(unsigned long long)final_id,(unsigned long long)h.current,(unsigned long long)h.peak);return 0;
}
