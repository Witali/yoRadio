#include <algorithm>
#include <cassert>
#include <cinttypes>
#include <cstdio>
#include <cstring>

#include "custom_flac_adapter.h"
#include "flac_decoder.h"
#include "esp_chip_info.h"
#include "esp_heap_caps.h"
#include "esp_idf_version.h"
#include "esp_log.h"
#include "esp_partition.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#if ESP_IDF_VERSION != ESP_IDF_VERSION_VAL(6, 0, 2) || !defined(CONFIG_IDF_TARGET_ESP32) || !defined(__XTENSA__)
#error "Require pinned CYD SDK6.0.2 and classic Xtensa ESP32"
#endif
#if defined(CONFIG_FREERTOS_UNICORE) || defined(NDEBUG)
#error "Require dual core and enabled assertions"
#endif
static_assert(FLAC_OUTPUT_FRAMES == 512, "Require actual production callback block");

struct Header { uint32_t magic, version, count, entry_size; };
struct Entry {
    uint32_t id, source_bits, channels, rate, encoded_offset, encoded_bytes, pcm_offset, pcm_bytes;
    char name[64];
};
static_assert(sizeof(Header)==16 && sizeof(Entry)==96, "Host fixture container layout");
struct Result { unsigned id, schedule, pcm_bytes, callbacks, feeds, peak, stack_free; };
struct Context { const uint8_t *blob; size_t size; const Entry *entries; unsigned count; QueueHandle_t results; TaskHandle_t coordinator; };
struct Capture { const Entry *entry; const uint8_t *expected; size_t position; unsigned callbacks; bool abort; };

static bool capture(void *argument, const custom_flac_info_t *info, const uint8_t *pcm, size_t bytes) {
    auto &out = *static_cast<Capture *>(argument);
    assert(xPortGetCoreID()==1);
    assert(info->bits_per_sample==out.entry->source_bits);
    assert(info->pcm_bits_per_sample==16 && info->channels==out.entry->channels && info->sample_rate==out.entry->rate);
    assert(pcm && !(reinterpret_cast<uintptr_t>(pcm)&1U));
    assert(bytes && bytes<=512U*info->channels*2U && bytes%(info->channels*2U)==0);
    assert(out.position<=out.entry->pcm_bytes && bytes<=out.entry->pcm_bytes-out.position);
    assert(std::memcmp(pcm,out.expected+out.position,bytes)==0);
    out.position+=bytes; ++out.callbacks;
    return !out.abort;
}

static Result decode(const Context &context, const Entry &entry, unsigned schedule, bool separate_eof=false) {
    assert(xPortGetCoreID()==1 && FLACDecoder_GetAllocatedBytes()==0);
    assert(heap_caps_check_integrity_all(true));
    custom_flac_decoder_t *decoder=custom_flac_decoder_create(); assert(decoder);
    Capture output={&entry,context.blob+entry.pcm_offset,0,0,false};
    size_t offset=0, peak=0; unsigned feeds=0;
    while(offset<entry.encoded_bytes) {
        size_t bytes=std::min<size_t>(entry.encoded_bytes-offset,schedule ? schedule : entry.encoded_bytes);
        custom_flac_feed_stats_t stats={};
        int result=custom_flac_decoder_feed(decoder,context.blob+entry.encoded_offset+offset,bytes,
            !separate_eof && offset+bytes==entry.encoded_bytes,capture,&output,&stats);
        assert(result>=0);
        peak=std::max(peak,custom_flac_decoder_memory_used(decoder));offset+=bytes;++feeds;
        if(!(feeds&127U))vTaskDelay(1);
    }
    if(separate_eof) {
        custom_flac_feed_stats_t stats={};
        assert(custom_flac_decoder_feed(decoder,nullptr,0,true,capture,&output,&stats)>=0);++feeds;
    }
    assert(output.position==entry.pcm_bytes && output.callbacks);
    custom_flac_decoder_destroy(decoder);
    assert(FLACDecoder_GetAllocatedBytes()==0 && heap_caps_check_integrity_all(true));
    Result result={entry.id,schedule,(unsigned)output.position,output.callbacks,feeds,(unsigned)peak,
        (unsigned)uxTaskGetStackHighWaterMark(nullptr)};
    assert(result.stack_free>0);return result;
}

static unsigned guards(const Context &context) {
    const Entry *selected=nullptr;
    for(unsigned index=0;index<context.count;++index)
        if(!std::strcmp(context.entries[index].name,"flac-24bit-mid-verbatim"))selected=&context.entries[index];
    assert(selected);const Entry &entry=*selected; unsigned checks=0;
    for(size_t cut=0;cut<42U;++cut) {
        custom_flac_decoder_t *decoder=custom_flac_decoder_create();assert(decoder);
        Capture output={&entry,context.blob+entry.pcm_offset,0,0,false};custom_flac_feed_stats_t stats={};
        assert(custom_flac_decoder_feed(decoder,context.blob+entry.encoded_offset,cut,true,capture,&output,&stats)<0);
        assert(output.position==0);custom_flac_decoder_destroy(decoder);
        assert(!FLACDecoder_GetAllocatedBytes() && heap_caps_check_integrity_all(true));++checks;
    }
    for(unsigned kind=0;kind<3U;++kind) {
        uint8_t bytes[42];std::memcpy(bytes,context.blob+entry.encoded_offset,sizeof(bytes));
        if(kind==0)bytes[0]='X';
        if(kind==1){bytes[5]=1;bytes[6]=0;bytes[7]=1;}
        if(kind==2){bytes[15]=1;bytes[16]=0;bytes[17]=1;}
        custom_flac_decoder_t *decoder=custom_flac_decoder_create();assert(decoder);
        Capture output={&entry,context.blob+entry.pcm_offset,0,0,false};custom_flac_feed_stats_t stats={};
        assert(custom_flac_decoder_feed(decoder,bytes,sizeof(bytes),true,capture,&output,&stats)<0);
        assert(output.position==0);custom_flac_decoder_destroy(decoder);
        assert(!FLACDecoder_GetAllocatedBytes() && heap_caps_check_integrity_all(true));++checks;
    }
    {
        custom_flac_decoder_t *decoder=custom_flac_decoder_create();assert(decoder);
        Capture output={&entry,context.blob+entry.pcm_offset,0,0,true};custom_flac_feed_stats_t stats={};
        assert(custom_flac_decoder_feed(decoder,context.blob+entry.encoded_offset,entry.encoded_bytes,
            true,capture,&output,&stats)==-8);
        assert(output.callbacks==1);custom_flac_decoder_destroy(decoder);
        assert(!FLACDecoder_GetAllocatedBytes() && heap_caps_check_integrity_all(true));++checks;
    }
    (void)decode(context,entry,127,true);++checks;
    (void)decode(context,entry,0);++checks;
    return checks;
}

static void owner(void *argument) {
    auto &context=*static_cast<Context *>(argument);
    assert(xPortGetCoreID()==1);
    constexpr unsigned schedules[]={0,1,127,2048};
    for(unsigned index=0;index<context.count;++index)for(unsigned schedule:schedules) {
        Result result=decode(context,context.entries[index],schedule);
        assert(xQueueSend(context.results,&result,pdMS_TO_TICKS(30000))==pdPASS);vTaskDelay(1);
    }
    unsigned checks=guards(context);assert(checks==48U);
    assert(xTaskNotify(context.coordinator,checks,eSetValueWithOverwrite)==pdPASS);
    assert(ulTaskNotifyTake(pdTRUE,pdMS_TO_TICKS(30000))==1U);
    vTaskDelete(nullptr);
}

extern "C" void app_main(void) {
    assert(xPortGetCoreID()==0);esp_chip_info_t chip;esp_chip_info(&chip);
    assert(chip.model==CHIP_ESP32 && chip.cores==2 && heap_caps_check_integrity_all(true));
    esp_log_level_set("custom_flac",ESP_LOG_WARN);
    printf("CYD_FLAC_QEMU_BOOT target=esp32 sdk=%s arch=xtensa cores=2 owner_core=1 coordinator_core=0 output_frames=512\n",esp_get_idf_version());
    const esp_partition_t *part=esp_partition_find_first(ESP_PARTITION_TYPE_DATA,(esp_partition_subtype_t)0x40,"fixtures");
    assert(part && part->address==0x100000U && part->size==0x300000U);
    const void *mapped=nullptr;esp_partition_mmap_handle_t mapping;
    assert(esp_partition_mmap(part,0,part->size,ESP_PARTITION_MMAP_DATA,&mapped,&mapping)==ESP_OK);
    auto *header=static_cast<const Header *>(mapped);
    assert(header->magic==0x514c4643U && header->version==1U && header->count==130U && header->entry_size==sizeof(Entry));
    auto *entries=reinterpret_cast<const Entry *>(header+1);
    for(unsigned index=0;index<header->count;++index) {
        const Entry &entry=entries[index];assert(entry.id==index && std::memchr(entry.name,0,sizeof(entry.name)));
        assert(entry.source_bits>=4 && entry.source_bits<=24 && entry.channels>=1 && entry.channels<=2 && entry.rate==48000);
        assert(entry.encoded_offset>=sizeof(Header)+header->count*sizeof(Entry) && entry.encoded_offset<part->size);
        assert(entry.encoded_bytes && entry.encoded_bytes<=part->size-entry.encoded_offset);
        assert(entry.pcm_offset>=entry.encoded_offset+entry.encoded_bytes && entry.pcm_offset<part->size);
        assert(entry.pcm_bytes && entry.pcm_bytes<=part->size-entry.pcm_offset && entry.pcm_bytes%(entry.channels*2U)==0);
        if(index)assert(entry.encoded_offset>=entries[index-1].pcm_offset+entries[index-1].pcm_bytes);
    }
    QueueHandle_t results=xQueueCreate(4,sizeof(Result));assert(results);
    Context context={static_cast<const uint8_t *>(mapped),part->size,entries,header->count,results,xTaskGetCurrentTaskHandle()};
    TaskHandle_t decoder_owner=nullptr;
    assert(xTaskCreatePinnedToCore(owner,"custom_flac_test",16384,&context,3,&decoder_owner,1)==pdPASS);
    unsigned seen[130]={},total=0;
    for(unsigned index=0;index<520U;++index) {
        Result result;assert(xQueueReceive(results,&result,pdMS_TO_TICKS(30000))==pdPASS);
        assert(result.id<130U);unsigned slot=result.schedule==0?0:result.schedule==1?1:result.schedule==127?2:3;
        assert(result.schedule==0||result.schedule==1||result.schedule==127||result.schedule==2048);
        assert(!(seen[result.id]&(1U<<slot)));seen[result.id]|=1U<<slot;
        assert(result.pcm_bytes==entries[result.id].pcm_bytes && result.callbacks && result.feeds && result.stack_free>0);
        printf("CYD_FLAC_QEMU_CASE {\"id\":%u,\"schedule\":%u,\"pcm_bytes\":%u,\"callbacks\":%u,\"feeds\":%u,\"decoder_peak\":%u,\"stack_free\":%u}\n",
            result.id,result.schedule,result.pcm_bytes,result.callbacks,result.feeds,result.peak,result.stack_free);++total;
    }
    uint32_t checks=0;assert(xTaskNotifyWait(0,UINT32_MAX,&checks,pdMS_TO_TICKS(30000))==pdPASS && checks==48U);
    for(unsigned mask:seen)assert(mask==15U);
    assert(total==520U && !FLACDecoder_GetAllocatedBytes() && heap_caps_check_integrity_all(true));
    printf("CYD_FLAC_QEMU_COMPLETE fixtures=130 cases=520 guards=%" PRIu32 " byte_compare=1 heap_integrity=1 owner_core=1 coordinator_core=0 actual_cyd_task=0 oom_injection=0 hardware=0\n",checks);
    fflush(stdout);xTaskNotifyGive(decoder_owner);vTaskDelay(pdMS_TO_TICKS(50));
    vQueueDelete(results);esp_partition_munmap(mapping);esp_restart();
}
