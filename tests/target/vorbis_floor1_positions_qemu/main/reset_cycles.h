#pragma once
// Included only by the optional public raw reset fixture, after its helpers.
// Every decoder operation uses the same public handle on its pinned owner task.
#define VORBIS_RESET_SKIP_CONTROL 0

static uint8_t reset_baseline[28160];
static uint32_t reset_baseline_offsets[15];
static unsigned reset_baseline_packets, reset_baseline_bytes, reset_case_calls;
static struct {
    unsigned cases, calls, replay_packets, prefix_packets, retries, replay_pcm, prefix_pcm;
} reset_totals;

static void reset_owner(void) {
    check(checked_owned && checked!=NULL && xPortGetCoreID()==DECODE_CORE,"reset_owner");
}
static void reset_invoke(const char *round,const char *purpose,unsigned attempt) {
    reset_owner();
    if(VORBIS_RESET_SKIP_CONTROL && case_index==0 && !strcmp(round,"1") &&
       !strcmp(purpose,"restart") && attempt==0) {
        printf("VORBIS_RESET_CALL case=%u round=%s purpose=%s attempt=%u called=0 result=SKIPPED core=%d\n",
            case_index,round,purpose,attempt,xPortGetCoreID());
        return;
    }
    int result=esp_audio_dec_reset(checked);
    reset_case_calls++;reset_totals.calls++;
    printf("VORBIS_RESET_CALL case=%u round=%s purpose=%s attempt=%u called=1 result=%d core=%d\n",
        case_index,round,purpose,attempt,result,xPortGetCoreID());
    check(result==ESP_AUDIO_ERR_OK,"reset_result");
}
static void reset_initial(void) {
    reset_case_calls=0;reset_baseline_packets=0;reset_baseline_bytes=0;
    reset_baseline_offsets[0]=0;
    reset_invoke("initial","initial",0);
}
static void reset_capture(unsigned packet,const uint8_t *data,uint32_t size) {
    check(packet==reset_baseline_packets && packet<FIXTURE_PACKETS,"reset_capture_order");
    check(size==fixture_expected_bytes[packet] &&
        size<=sizeof(reset_baseline)-reset_baseline_bytes,"reset_capture_bounds");
    reset_baseline_offsets[packet]=reset_baseline_bytes;
    memcpy(reset_baseline+reset_baseline_bytes,data,size);
    reset_baseline_bytes+=size;
    reset_baseline_offsets[packet+1]=reset_baseline_bytes;
    reset_baseline_packets++;
}
static uint32_t reset_packet(const uint8_t *packets,const uint32_t *offsets,
    unsigned round,const char *phase,unsigned packet) {
    reset_owner();
    check(packet<FIXTURE_PACKETS,"reset_packet_index");
    uint32_t len=offsets[packet+1]-offsets[packet];
    uint32_t expected=reset_baseline_offsets[packet+1]-reset_baseline_offsets[packet];
    esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)packets+offsets[packet],.len=len};
    esp_audio_dec_out_frame_t out={.buffer=pcm.data,.len=sizeof(pcm.data)};
    arm();
    int status=esp_audio_dec_process(checked,&raw,&out);
    guard();
    check(status==ESP_AUDIO_ERR_OK && raw.consumed==len,"reset_packet_result_consumption");
    check(out.decoded_size<=sizeof(pcm.data),"reset_output_bound");
    esp_audio_dec_info_t info={0};
    int info_status=esp_audio_dec_get_info(checked,&info);
    bool correct=info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16;
    check((info_status==ESP_AUDIO_ERR_OK && correct) ||
        (!expected && info_status==ESP_AUDIO_ERR_NOT_FOUND),"reset_public_metadata");
    // Publish actual safe decoded bytes before assertions against expected output.
    // In the skipped-reset control this preserves the nonempty primer witness.
    printf("VORBIS_RESET_PCM case=%u round=%u phase=%s packet=%u consumed=%" PRIu32
        " bytes=%" PRIu32 " info_result=%d sample_rate=%" PRIu32 " channel=%u bits=%u hex=",
        case_index,round,phase,packet,raw.consumed,out.decoded_size,info_status,
        info.sample_rate,(unsigned)info.channel,(unsigned)info.bits_per_sample);
    for(unsigned i=0;i<out.decoded_size;i++) printf("%02x",pcm.data[i]);
    printf("\n");
    if(packet==0) check(out.decoded_size==0,"reset_primer_empty");
    check(out.decoded_size==expected,"reset_packet_output_size");
    check(!memcmp(pcm.data,reset_baseline+reset_baseline_offsets[packet],expected),"reset_baseline_exact");
    if(!(packet&3)) vTaskDelay(1);
    return out.decoded_size;
}
static void reset_tiny_retries(const uint8_t *packets,const uint32_t *offsets) {
    reset_owner();
    const unsigned packet=5;
    uint32_t len=offsets[packet+1]-offsets[packet];
    uint32_t expected=reset_baseline_offsets[packet+1]-reset_baseline_offsets[packet];
    check(expected>1 && expected<=sizeof(pcm.data),"reset_retry_fixture");
    for(unsigned attempt=0;attempt<3;attempt++) {
        esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)packets+offsets[packet],.len=len,.consumed=99};
        esp_audio_dec_out_frame_t out={.buffer=pcm.data,.len=1,.needed_size=99,.decoded_size=99};
        arm();
        int status=esp_audio_dec_process(checked,&raw,&out);
        guard();
        check(status==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH,"reset_retry_result");
        check(raw.consumed==0 && out.decoded_size==0,"reset_retry_consumption");
        check(out.needed_size==expected,"reset_retry_capacity");
        for(unsigned i=0;i<sizeof(pcm.data);i++) check(pcm.data[i]==0xc7,"reset_retry_untouched");
        reset_totals.retries++;
        printf("VORBIS_RESET_RETRY case=%u round=2 packet=5 attempt=%u result=%d consumed=0 decoded=0 needed=%" PRIu32
            " untouched=1 canaries=1 core=%d\n",case_index,attempt,status,out.needed_size,xPortGetCoreID());
    }
}
static void reset_exercise(const floor1_case_t *c,const uint8_t *packets,const uint32_t *offsets) {
    reset_owner();
    check(c->valid && reset_case_calls==1 && reset_baseline_packets==14 && reset_baseline_bytes==28160,
        "reset_complete_baseline");
    printf("VORBIS_RESET_BEGIN case=%u rounds=4 core=%d\n",case_index,xPortGetCoreID());
    unsigned full_packets=0,prefix_packets=0,full_pcm=0,prefix_pcm=0;
    unsigned retries_before=reset_totals.retries;
    const char *round_names[]={"0","1","2","3"};
    for(unsigned round=0;round<4;round++) {
        if(round==1 || round==2) {
            reset_invoke(round_names[round],"prepare",0);
            unsigned limit=round==1 ? 7 : 5;
            for(unsigned packet=0;packet<limit;packet++) {
                prefix_pcm+=reset_packet(packets,offsets,round,"prefix",packet);
                prefix_packets++;
            }
            if(round==2) reset_tiny_retries(packets,offsets);
        }
        for(unsigned attempt=0;attempt<(round==3 ? 3u : 1u);attempt++)
            reset_invoke(round_names[round],"restart",attempt);
        unsigned bytes=0;
        for(unsigned packet=0;packet<FIXTURE_PACKETS;packet++) {
            bytes+=reset_packet(packets,offsets,round,"full",packet);
            full_packets++;
        }
        check(bytes==28160,"reset_round_pcm");full_pcm+=bytes;
        printf("VORBIS_RESET_ROUND case=%u round=%u packets=14 pcm=28160 baseline_exact=1 core=%d\n",
            case_index,round,xPortGetCoreID());
    }
    check(reset_case_calls==9 && full_packets==56 && prefix_packets==12 &&
        reset_totals.retries-retries_before==3 && full_pcm==112640 &&
        prefix_pcm==reset_baseline_offsets[7]+reset_baseline_offsets[5],"reset_complete_case");
    reset_totals.cases++;reset_totals.replay_packets+=full_packets;
    reset_totals.prefix_packets+=prefix_packets;reset_totals.replay_pcm+=full_pcm;
    reset_totals.prefix_pcm+=prefix_pcm;
    printf("VORBIS_RESET_DONE case=%u calls=%u replay_packets=%u prefix_packets=%u retries=3 replay_pcm=%u prefix_pcm=%u core=%d\n",
        case_index,reset_case_calls,full_packets,prefix_packets,full_pcm,prefix_pcm,xPortGetCoreID());
}
static void reset_summary(void) {
    check(reset_totals.cases==8 && reset_totals.calls==72 && reset_totals.replay_packets==448 &&
        reset_totals.prefix_packets==96 && reset_totals.retries==24 && reset_totals.replay_pcm==901120 &&
        reset_totals.prefix_pcm==212992,"reset_complete_matrix");
    printf("VORBIS_RESET_COMPLETE cases=%u calls=%u replay_packets=%u prefix_packets=%u retries=%u replay_pcm=%u prefix_pcm=%u core=%d\n",
        reset_totals.cases,reset_totals.calls,reset_totals.replay_packets,reset_totals.prefix_packets,
        reset_totals.retries,reset_totals.replay_pcm,reset_totals.prefix_pcm,xPortGetCoreID());
}
