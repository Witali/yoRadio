// Public raw APIs only. Every opened handle remains opaque.
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "esp_vorbis_dec.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "banks_contract.h"
#include "banks_data.h" // Future root-frozen encoded payload arrays; not fabricated by this prep.
_Static_assert(sizeof(block_banks)/sizeof(block_banks[0])==3,"all three banks required");

#ifdef LIMIT_TO_64kHz
#error Unrestricted setup.c compiler context is required independently too
#endif
#if defined(BLOCK_MATRIX_PROFILE_CYD) == defined(BLOCK_MATRIX_PROFILE_C3)
#error Select exactly one explicit target profile
#endif
#if defined(BLOCK_MATRIX_PROFILE_CYD)
#if !defined(CONFIG_IDF_TARGET_ESP32) || !CONFIG_IDF_TARGET_ESP32
#error CYD profile requires actual ESP32/Xtensa configuration
#endif
#define PREFIX "CYD_VORBIS_BLOCK_"
#define WORKER_CORE 1
#else
#if !defined(CONFIG_IDF_TARGET_ESP32C3) || !CONFIG_IDF_TARGET_ESP32C3
#error C3 profile requires actual ESP32-C3/RV32 configuration
#endif
#define PREFIX "C3_VORBIS_BLOCK_"
#define WORKER_CORE 0
#endif
#if !defined(BLOCK_MATRIX_MINIMAL_RATE_REBIND_VERIFIED) || BLOCK_MATRIX_MINIMAL_RATE_REBIND_VERIFIED != 1
#error Independent minimal48000-to192000 host validation is required before launch
#endif
#ifndef BLOCK_MATRIX_DATA_MANIFEST_SHA256
#error Bind the root-frozen encoded-bank manifest
#endif

extern esp_audio_err_t __real_esp_vorbis_dec_open(void *, uint32_t, void **);
extern esp_audio_err_t __real_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *,
    esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);
static void *vendor, *checked;
typedef struct { uint8_t before[16], data[16384], after[16]; } guarded_pcm_t;
static guarded_pcm_t vendor_pcm, checked_pcm;
static const block_bank_t *active;
static unsigned active_short, active_long, active_packet;
static uint32_t cases_done, packets_done, groups_done;
static uint64_t pcm_done;
static const char *const transition_name[4] = {"SS", "SL", "LS", "LL"};

static void stop(const char *why) {
    if (why) printf(PREFIX "FAILURE bank=%s short=%u long=%u packet=%u reason=%s\n",
        active ? active->name : "none", active_short, active_long, active_packet, why);
    if (vendor) { esp_vorbis_dec_close(vendor); vendor = NULL; }
    if (checked) { esp_vorbis_dec_close(checked); checked = NULL; }
    fflush(stdout);
    esp_restart();
    for (;;) vTaskDelay(portMAX_DELAY);
}
static void need(bool ok, const char *why) { if (!ok) stop(why); }
static void arm(guarded_pcm_t *pcm, uint8_t fill) {
    memset(pcm->before, 0xa5, 16); memset(pcm->data, fill, sizeof(pcm->data));
    memset(pcm->after, 0x5a, 16);
}
static void guards(const guarded_pcm_t *pcm) {
    for (unsigned i=0; i<16; ++i)
        need(pcm->before[i]==0xa5 && pcm->after[i]==0x5a, "public_output_canaries");
}
static void close_handles(void) {
    if (vendor) { void *h=vendor; vendor=NULL; need(esp_vorbis_dec_close(h)==ESP_AUDIO_ERR_OK,"vendor_close"); }
    if (checked) { void *h=checked; checked=NULL; need(esp_vorbis_dec_close(h)==ESP_AUDIO_ERR_OK,"checked_close"); }
}
static void metadata(const esp_audio_dec_info_t *info, const char *side) {
    bool ok=info->sample_rate==192000 && info->channel==2 && info->bits_per_sample==16;
    if (!ok) printf(PREFIX "METADATA bank=%s short=%u long=%u packet=%u side=%s sample_rate=%" PRIu32
        " channel=%u bits=%u\n",active->name,active_short,active_long,active_packet,side,
        info->sample_rate,(unsigned)info->channel,(unsigned)info->bits_per_sample);
    need(ok,"public_metadata_every_packet");
}
static uint32_t rate(const uint8_t *p) {
    return (uint32_t)p[5] | (uint32_t)p[6]<<8 | (uint32_t)p[7]<<16 | (uint32_t)p[8]<<24;
}
static uint32_t expected_bytes(const block_bank_t *bank, unsigned packet, unsigned s, unsigned l) {
    if (!packet) return 0;
    return (1U << (bank->modes[packet-1] ? l : s)) + (1U << (bank->modes[packet] ? l : s));
}
static void validate_bank(const block_bank_t *bank, unsigned index) {
    static const char *const names[3]={"identity","transitions","minimal"};
    static const uint32_t counts[3]={68,70,14}, rates[3]={192000,192000,48000};
    static const char *const patterns[3]={NULL,NULL,"SSLLLSLSSSLLSS"};
    need(bank->name && !strcmp(bank->name,names[index]) && bank->source_rate==rates[index], "bank_identity");
    need(bank->info && bank->setup && bank->audio && bank->modes && bank->offsets, "bank_payload_pointers");
    need(bank->info_size==23 && bank->setup_size && bank->info[4]==2 && rate(bank->info)==bank->source_rate,
        "raw_header_payload_contract");
    need(bank->packet_count==counts[index] && bank->modes_count==counts[index] &&
        bank->offsets_count==counts[index]+1 && bank->offsets[0]==0 &&
        bank->offsets[counts[index]]==bank->audio_size, "bank_packet_vectors");
    for (unsigned p=0; p<bank->packet_count; ++p) {
        uint8_t mode=bank->modes[p];
        uint8_t expected=index==0 ? (p!=0) : index==1 ? (p!=0 && p!=1 && p!=4) : (patterns[index][p]=='L');
        need(mode==expected && bank->offsets[p]<bank->offsets[p+1] && bank->offsets[p+1]<=bank->audio_size,
            "bank_mode_offsets");
        uint8_t first=bank->audio[bank->offsets[p]];
        need((first & 3U)==(mode << 1), "public_packet_type_mode");
        if (mode && p) need(((first>>2)&1U)==bank->modes[p-1], "public_previous_window_flag");
        if (mode && p+1<bank->packet_count) need(((first>>3)&1U)==bank->modes[p+1], "public_next_window_flag");
    }
}
static void compare(const block_bank_t *bank, unsigned s, unsigned l) {
    active_short=1U<<s; active_long=1U<<l; active_packet=0;
    need(!vendor && !checked, "fresh_case_handles");
    uint8_t ai_header[23], bi_header[23];
    memcpy(ai_header,bank->info,23); ai_header[21]=(uint8_t)(s | l<<4);
    for (unsigned i=0; i<4; ++i) ai_header[5+i]=(uint8_t)(192000U >> (8*i));
    memcpy(bi_header,ai_header,23);
    esp_vorbis_dec_cfg_t a_cfg={.info_header=ai_header,.info_size=23,
        .setup_header=(uint8_t *)bank->setup,.setup_size=bank->setup_size};
    esp_vorbis_dec_cfg_t b_cfg=a_cfg; b_cfg.info_header=bi_header;
    int ar=__real_esp_vorbis_dec_open(&a_cfg,sizeof(a_cfg),&vendor);
    need(ar==ESP_AUDIO_ERR_OK && vendor,"vendor_open_required");
    int br=esp_vorbis_dec_open(&b_cfg,sizeof(b_cfg),&checked);
    need(br==ESP_AUDIO_ERR_OK && checked,"checked_open_required");
    printf(PREFIX "CASE_BEGIN bank=%s short=%u long=%u packets=%" PRIu32
        " rate=192000 vendor_open=%d checked_open=%d handles=1 core=%d\n",
        bank->name,active_short,active_long,bank->packet_count,ar,br,xPortGetCoreID());
    uint32_t total=0, expected_total=0, transition_count[4]={0}, transition_pcm[4]={0}, nonzero[4]={0};
    esp_audio_dec_info_t ai={0}, bi={0}; // Lifetime: exactly this opened handle pair, not each packet.
    for (unsigned p=0; p<bank->packet_count; ++p) {
        active_packet=p;
        uint32_t size=bank->offsets[p+1]-bank->offsets[p], expected=expected_bytes(bank,p,s,l);
        uint8_t *data=(uint8_t *)bank->audio+bank->offsets[p];
        esp_audio_dec_in_raw_t a={.buffer=data,.len=size}, b=a;
        esp_audio_dec_out_frame_t ao={.buffer=vendor_pcm.data,.len=sizeof(vendor_pcm.data)};
        esp_audio_dec_out_frame_t bo={.buffer=checked_pcm.data,.len=sizeof(checked_pcm.data)};
        arm(&vendor_pcm,0xa7); ar=__real_esp_vorbis_dec_decode(vendor,&a,&ao,&ai); guards(&vendor_pcm);
        need(ar==ESP_AUDIO_ERR_OK && a.consumed==size && ao.decoded_size==expected &&
            ao.decoded_size<=sizeof(vendor_pcm.data),"vendor_complete_packet_required");
        metadata(&ai,"vendor");
        arm(&checked_pcm,0xc9); br=esp_vorbis_dec_decode(checked,&b,&bo,&bi); guards(&checked_pcm);
        need(br==ESP_AUDIO_ERR_OK && b.consumed==size && bo.decoded_size==expected &&
            bo.decoded_size<=sizeof(checked_pcm.data),"checked_complete_packet_required");
        metadata(&bi,"checked");
        need(!memcmp(vendor_pcm.data,checked_pcm.data,expected),"byte_exact_vendor_pcm");
        uint32_t nz=0;
        for (unsigned i=0; i<expected; ++i) nz += checked_pcm.data[i]!=0;
        unsigned kind=p ? 2U*bank->modes[p-1]+bank->modes[p] : 0;
        if (p) { ++transition_count[kind]; transition_pcm[kind]+=expected; nonzero[kind]+=nz; }
        total+=bo.decoded_size; expected_total+=expected; ++packets_done;
        printf(PREFIX "PACKET bank=%s short=%u long=%u packet=%u expected=%" PRIu32
            " vendor_consumed=%" PRIu32 " checked_consumed=%" PRIu32 " pcm=%" PRIu32
            " vendor_rate=%" PRIu32 " checked_rate=%" PRIu32
            " vendor_channel=%u checked_channel=%u vendor_bits=%u checked_bits=%u"
            " exact=1 canaries=1 transition=%s nonzero=%" PRIu32 " core=%d\n",
            bank->name,active_short,active_long,p,size,a.consumed,b.consumed,bo.decoded_size,
            ai.sample_rate,bi.sample_rate,(unsigned)ai.channel,(unsigned)bi.channel,
            (unsigned)ai.bits_per_sample,(unsigned)bi.bits_per_sample,p ? transition_name[kind] : "P",nz,xPortGetCoreID());
        if (!(p & 15U)) vTaskDelay(1);
    }
    need(total==expected_total,"case_complete_pcm");
    for (unsigned k=0; k<4; ++k) if (transition_count[k]) {
        need(nonzero[k]>0,"nonzero_each_present_transition"); ++groups_done;
        printf(PREFIX "TRANSITION bank=%s short=%u long=%u kind=%s packets=%" PRIu32
            " pcm=%" PRIu32 " nonzero=%" PRIu32 " core=%d\n",bank->name,active_short,active_long,
            transition_name[k],transition_count[k],transition_pcm[k],nonzero[k],xPortGetCoreID());
    }
    close_handles(); ++cases_done; pcm_done+=total;
    printf(PREFIX "CASE_COMPLETE bank=%s short=%u long=%u packets=%" PRIu32
        " pcm=%" PRIu32 " handles_closed=1 core=%d\n",bank->name,active_short,active_long,bank->packet_count,total,xPortGetCoreID());
}
static void task(void *unused) {
    (void)unused; need(xPortGetCoreID()==WORKER_CORE,"worker_core");
    for (unsigned bank_index=0; bank_index<3; ++bank_index) {
        active=&block_banks[bank_index]; active_short=active_long=active_packet=0; validate_bank(active,bank_index);
        printf(PREFIX "BANK_BEGIN bank=%s packets=%" PRIu32 " source_rate=%" PRIu32
            " target_rate=192000 core=%d\n",active->name,active->packet_count,active->source_rate,xPortGetCoreID());
        uint32_t before_cases=cases_done, before_packets=packets_done, before_groups=groups_done;
        uint64_t before_pcm=pcm_done;
        for (unsigned s=6; s<=13; ++s) for (unsigned l=s; l<=13; ++l) compare(active,s,l);
        need(cases_done-before_cases==36 && packets_done-before_packets==36*active->packet_count,"bank_complete_cases");
        printf(PREFIX "BANK_COMPLETE bank=%s cases=36 paired_packets=%" PRIu32
            " pcm=%" PRIu64 " transition_groups=%" PRIu32 " core=%d\n",active->name,
            packets_done-before_packets,pcm_done-before_pcm,groups_done-before_groups,xPortGetCoreID());
    }
    need(cases_done==108 && packets_done==5472 && groups_done==360,"full108_case_matrix");
    printf(PREFIX "COMPLETE banks=3 cases=108 paired_packets=5472 pcm=%" PRIu64
        " transition_groups=360 core=%d\n",pcm_done,xPortGetCoreID());
    stop(NULL);
}
void app_main(void) {
    need(xPortGetCoreID()==0,"coordinator_core0");
    printf(PREFIX "BEGIN banks=3 cases=108 paired_packets=5472 target_rate=192000 coordinator=0 worker=%d"
        " minimal_source_rate=48000 minimal_rate_rebind=1 manifest=%s\n",WORKER_CORE,BLOCK_MATRIX_DATA_MANIFEST_SHA256);
    need(xTaskCreatePinnedToCore(task,"public_blocks",16384,NULL,3,NULL,WORKER_CORE)==pdPASS,"create_public_block_worker");
}
