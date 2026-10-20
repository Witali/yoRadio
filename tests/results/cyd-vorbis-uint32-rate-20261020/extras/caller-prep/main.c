// Isolated public raw API rate test. Decoder handles remain opaque.
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "esp_vorbis_dec.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "fixture.h"

#if !defined(RATE_EXPECT_UNSIGNED_REJECTION) || !defined(RATE_LIMITED_POLICY)
#error Select both explicit rate-test policy macros
#endif
#if (RATE_EXPECT_UNSIGNED_REJECTION != 0 && RATE_EXPECT_UNSIGNED_REJECTION != 1) || \
    (RATE_LIMITED_POLICY != 0 && RATE_LIMITED_POLICY != 1) || \
    (RATE_EXPECT_UNSIGNED_REJECTION && RATE_LIMITED_POLICY)
#error Unsupported combination of rate-test policies
#endif
#if RATE_LIMITED_POLICY
#ifndef LIMIT_TO_64kHz
#error Limited policy requires the actual setup cap
#endif
#else
#ifdef LIMIT_TO_64kHz
#error Unrestricted policy must not inherit the optional setup cap
#endif
#endif
_Static_assert(FIXTURE_PACKETS == 68U && FIXTURE_SHORT_BITS == 8U &&
               FIXTURE_ENCODER_LONG_BITS == 11U, "Pinned S256/L2048 fixture");

extern esp_audio_err_t __real_esp_vorbis_dec_open(void *, uint32_t, void **);
extern esp_audio_err_t __real_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *,
    esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);

static const uint32_t rates[] = {48000U,44100U,32000U,24000U,22050U,16000U,
    12000U,11025U,8000U,1U,63999U,64000U,192000U,INT32_MAX,UINT32_C(0x80000000),UINT32_MAX};
typedef struct { uint8_t before[16], data[16384], after[16]; } guarded_pcm_t;
static guarded_pcm_t a_pcm,b_pcm;
static void *vendor,*checked;
static unsigned accepted,rejected,paired_packets;
static uint32_t total_pcm;

static void stop(const char *reason) {
    if (reason) printf("CYD_VORBIS_RATE_FAILURE %s\n",reason);
    if (vendor) { esp_vorbis_dec_close(vendor); vendor=NULL; }
    if (checked) { esp_vorbis_dec_close(checked); checked=NULL; }
    fflush(stdout);
    esp_restart();
    for (;;) vTaskDelay(portMAX_DELAY);
}
static void check(bool condition,const char *reason) { if (!condition) stop(reason); }
static unsigned core(void) {
    unsigned value=(unsigned)xPortGetCoreID(); check(value==1U,"worker_core1"); return value;
}
static void close_handles(void) {
    if (vendor) { void *h=vendor; vendor=NULL; check(esp_vorbis_dec_close(h)==ESP_AUDIO_ERR_OK,"vendor_close"); }
    if (checked) { void *h=checked; checked=NULL; check(esp_vorbis_dec_close(h)==ESP_AUDIO_ERR_OK,"checked_close"); }
}
static void arm(guarded_pcm_t *p,uint8_t fill) {
    memset(p->before,0xa5,sizeof(p->before)); memset(p->data,fill,sizeof(p->data)); memset(p->after,0x5a,sizeof(p->after));
}
static void guards(const guarded_pcm_t *p) {
    for (unsigned i=0;i<16;++i) check(p->before[i]==0xa5 && p->after[i]==0x5a,"output_canaries");
}
static void header(uint8_t *out,uint32_t rate) {
    memcpy(out,fixture_info,sizeof(fixture_info));
    for (unsigned i=0;i<4;++i) out[5+i]=(uint8_t)(rate>>(8*i));
    out[21]=(uint8_t)(8U|(11U<<4)); // Both handles use original S256/L2048.
}
static esp_vorbis_dec_cfg_t config(uint8_t *info) {
    return (esp_vorbis_dec_cfg_t){.info_header=info,.info_size=sizeof(fixture_info),
        .setup_header=(uint8_t *)fixture_setup,.setup_size=sizeof(fixture_setup)};
}
static uint32_t expected_bytes(unsigned packet) {
    if (!packet) return 0;
    unsigned before=fixture_long_mode[packet-1]?2048U:256U;
    unsigned now=fixture_long_mode[packet]?2048U:256U;
    return (before+now); // /4 frames * stereo * sizeof(int16_t).
}
static void zero_header(void) {
    uint8_t info[sizeof(fixture_info)]; header(info,0); esp_vorbis_dec_cfg_t cfg=config(info);
    int result=esp_vorbis_dec_open(&cfg,sizeof(cfg),&checked);
    check(result==ESP_AUDIO_ERR_FAIL && !checked,"zero_rate_rejection_required");
    close_handles();
    printf("CYD_VORBIS_RATE_ZERO_REJECT rate=0 result=%d handle=0 handles_closed=1 core=%u\n",result,core());
}
static void compare(unsigned index,uint32_t rate) {
    uint8_t golden[sizeof(fixture_info)],candidate[sizeof(fixture_info)];
    header(golden,192000U); header(candidate,rate);
    for (unsigned i=0;i<sizeof(golden);++i)
        check((i>=5U && i<9U) || golden[i]==candidate[i],"rate_only_identification");
    esp_vorbis_dec_cfg_t a_cfg=config(golden),b_cfg=config(candidate);
    int ar=__real_esp_vorbis_dec_open(&a_cfg,sizeof(a_cfg),&vendor);
    check(ar==ESP_AUDIO_ERR_OK && vendor,"golden192000_open_required");
    int br=esp_vorbis_dec_open(&b_cfg,sizeof(b_cfg),&checked);
    printf("CYD_VORBIS_RATE_CASE_OPEN index=%u rate=%" PRIu32 " golden_rate=192000 vendor_open=%d checked_open=%d vendor_handle=%u checked_handle=%u header_error=%u core=%u\n",
           index,rate,ar,br,(unsigned)(vendor!=NULL),(unsigned)(checked!=NULL),
           (unsigned)(br==ESP_AUDIO_ERR_FAIL && !checked),core());
    bool limited=RATE_LIMITED_POLICY && rate>=64000U;
    bool unsigned_reject=RATE_EXPECT_UNSIGNED_REJECTION && rate>INT32_MAX;
    if (limited || unsigned_reject) {
        check(br==ESP_AUDIO_ERR_FAIL && !checked,limited?"limited_rate_rejection_required":"baseline_unsigned_rejection_required");
        close_handles(); ++rejected;
        printf("CYD_VORBIS_RATE_CASE_REJECT index=%u rate=%" PRIu32 " result=%d header_error=1 handles_closed=1 core=%u\n",index,rate,br,core());
        return;
    }
    check(br==ESP_AUDIO_ERR_OK && checked,rate>INT32_MAX?"legal_unsigned_rate_open_required":"legal_rate_open_required");
    esp_audio_dec_info_t a_info={0},b_info={0}; // Retained separately for each opened handle, including priming.
    uint32_t pcm=0,nonzero=0;
    for (unsigned packet=0;packet<FIXTURE_PACKETS;++packet) {
        uint32_t size=fixture_offsets[packet+1]-fixture_offsets[packet];
        esp_audio_dec_in_raw_t a={.buffer=(uint8_t *)fixture_packets+fixture_offsets[packet],.len=size},b=a;
        esp_audio_dec_out_frame_t ao={.buffer=a_pcm.data,.len=sizeof(a_pcm.data)},bo={.buffer=b_pcm.data,.len=sizeof(b_pcm.data)};
        arm(&a_pcm,0xa7); ar=__real_esp_vorbis_dec_decode(vendor,&a,&ao,&a_info); guards(&a_pcm);
        arm(&b_pcm,0xc9); br=esp_vorbis_dec_decode(checked,&b,&bo,&b_info); guards(&b_pcm);
        check(ar==ESP_AUDIO_ERR_OK && br==ar && a.consumed==size && b.consumed==size,"packet_result_and_consumption");
        check(ao.decoded_size==expected_bytes(packet) && bo.decoded_size==ao.decoded_size &&
              bo.decoded_size<=sizeof(b_pcm.data),"packet_pcm_size");
        check(!memcmp(a_pcm.data,b_pcm.data,bo.decoded_size),"packet_exact_pcm");
        if (a_info.sample_rate!=192000U || b_info.sample_rate!=rate || a_info.channel!=2 || b_info.channel!=2 ||
            a_info.bits_per_sample!=16 || b_info.bits_per_sample!=16)
            printf("RATE_METADATA rate=%" PRIu32 " packet=%u vendor_rate=%" PRIu32 " checked_rate=%" PRIu32 " vendor_channel=%u checked_channel=%u vendor_bits=%u checked_bits=%u\n",
                rate,packet,a_info.sample_rate,b_info.sample_rate,(unsigned)a_info.channel,(unsigned)b_info.channel,
                (unsigned)a_info.bits_per_sample,(unsigned)b_info.bits_per_sample);
        check(a_info.sample_rate==192000U && b_info.sample_rate==rate && a_info.channel==2 && b_info.channel==2 &&
              a_info.bits_per_sample==16 && b_info.bits_per_sample==16,"packet_public_metadata");
        uint32_t nz=0; for (unsigned i=0;i<bo.decoded_size;++i) nz+=b_pcm.data[i]!=0;
        pcm+=bo.decoded_size; nonzero+=nz; ++paired_packets;
        printf("CYD_VORBIS_RATE_PACKET index=%u rate=%" PRIu32 " packet=%u expected=%" PRIu32 " vendor_consumed=%" PRIu32 " checked_consumed=%" PRIu32 " pcm=%" PRIu32
            " vendor_rate=%" PRIu32 " checked_rate=%" PRIu32 " vendor_channel=%u checked_channel=%u vendor_bits=%u checked_bits=%u exact=1 canaries=1 nonzero=%" PRIu32 " core=%u\n",
            index,rate,packet,size,a.consumed,b.consumed,bo.decoded_size,a_info.sample_rate,b_info.sample_rate,
            (unsigned)a_info.channel,(unsigned)b_info.channel,(unsigned)a_info.bits_per_sample,(unsigned)b_info.bits_per_sample,nz,core());
        if (!(packet&15U)) vTaskDelay(1); // Yield the pinned worker to the watchdog/idle task.
    }
    check(pcm==FIXTURE_RAW2048_BYTES && nonzero,"complete_nonzero_pcm");
    close_handles(); ++accepted; total_pcm+=pcm;
    printf("CYD_VORBIS_RATE_CASE_COMPLETE index=%u rate=%" PRIu32 " packets=68 pcm=%" PRIu32 " nonzero=%" PRIu32 " handles_closed=1 core=%u\n",index,rate,pcm,nonzero,core());
}
static void task(void *unused) {
    (void)unused; printf("CYD_VORBIS_RATE_WORKER core=%u\n",core());
    zero_header();
    for (unsigned i=0;i<sizeof(rates)/sizeof(rates[0]);++i) compare(i,rates[i]);
    unsigned want_rejected=RATE_LIMITED_POLICY?5U:RATE_EXPECT_UNSIGNED_REJECTION?2U:0U;
    check(rejected==want_rejected && accepted==16U-want_rejected && paired_packets==68U*accepted &&
          total_pcm==FIXTURE_RAW2048_BYTES*accepted,"complete_case_accounting");
    printf("CYD_VORBIS_RATE_COMPLETE cases=16 accepted=%u rejected=%u paired_packets=%u pcm=%" PRIu32 " zero_rejected=1 core=%u\n",
           accepted,rejected,paired_packets,total_pcm,core());
    stop(NULL);
}
void app_main(void) {
    unsigned coordinator=(unsigned)xPortGetCoreID(); check(coordinator==0U,"coordinator_core0");
    printf("CYD_VORBIS_RATE_BEGIN expected_unsigned_rejection=%d limited_policy=%d cases=16 short=256 long=2048 golden_rate=192000 coordinator=%u\n",
           RATE_EXPECT_UNSIGNED_REJECTION,RATE_LIMITED_POLICY,coordinator);
    check(xTaskCreatePinnedToCore(task,"public_rate",16384,NULL,3,NULL,1)==pdPASS,"create_core1_rate_task");
}
