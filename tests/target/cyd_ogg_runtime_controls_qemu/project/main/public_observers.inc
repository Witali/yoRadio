// Public function forwarding only. No private decoder layout or state mutation.
static unsigned simple_depth,raw_next_slot;
static esp_audio_simple_dec_handle_t simple_handle;
static unsigned simple_instance,simple_calls,simple_resizes,simple_retries;
static bool simple_retry,simple_drained;
static uint8_t *simple_retry_pointer;
static uint32_t simple_retry_length,simple_retry_capacity;
static bool simple_retry_eos;
struct raw_watch_t {
    void *handle;const esp_opus_dec_cfg_t *config_address;esp_opus_dec_cfg_t config;
    unsigned instance,stream,calls,resizes,retries;
    uint64_t consumed,decoded;
    bool retry;uint8_t *retry_pointer;uint32_t retry_length,retry_capacity;
};
static raw_watch_t raw_watches[8];
static raw_watch_t &raw_watch(void *handle) {
    for(auto &row:raw_watches)if(row.handle==handle)return row;
    check(false,"real_raw_public_handle_identity");return raw_watches[0];
}
static const link_t *decode_link() {check(decode_link_index<active->count,"actual_decoder_link_order");return active->links[decode_link_index];}
static void record_open(const char *kind,unsigned instance,unsigned stream,int result) {
    session_generation=snapshot().audio_generation;
    check(session_generation==http_generation,"same_HTTP_generation_for_logical_decoder");
    printf("CYD_F1_OBS_OPEN fixture=%s link=%u kind=%s instance=%u stream=%u generation=%u result=%d live=%u\n",active->name,decode_link_index,kind,instance,stream,(unsigned)session_generation.load(),result,live_decoders.load());
}
extern "C" esp_audio_err_t __real_esp_opus_dec_open(void *,uint32_t,void **);
extern "C" esp_audio_err_t __real_esp_opus_dec_decode(void *,esp_audio_dec_in_raw_t *,esp_audio_dec_out_frame_t *,esp_audio_dec_info_t *);
extern "C" esp_audio_err_t __real_esp_opus_dec_close(void *);
extern "C" esp_audio_err_t __wrap_esp_opus_dec_open(void *configuration,uint32_t bytes,void **handle) {
    if(simple_depth)return __real_esp_opus_dec_open(configuration,bytes,handle);
    owner(1,5);auto link=decode_link();check(link->layout==1 && link->needed && bytes==sizeof(esp_opus_dec_cfg_t),"public_raw_selected_only_for_family1");
    if(!live_decoders)raw_next_slot=0;
    check(raw_next_slot<link->needed && configuration && handle,"real_raw_open_slot_bounds");
    auto cfg=static_cast<const esp_opus_dec_cfg_t *>(configuration);unsigned stream=link->needed_ids[raw_next_slot++];
    check(cfg->sample_rate==48000 && cfg->channel==(stream<link->coupled?2:1) && cfg->frame_duration==ESP_OPUS_DEC_FRAME_DURATION_INVALID &&
          cfg->self_delimited==(stream+1<link->streams),"original_stream_number_and_public_raw_configuration");
    ++runtime_sdk_depth;auto result=__real_esp_opus_dec_open(configuration,bytes,handle);--runtime_sdk_depth;
    if(result!=ESP_AUDIO_ERR_OK || !*handle)++public_failures;
    if(!*handle){record_open("raw",0,stream,result);return result;}
    raw_watch_t *watch=nullptr;for(auto &row:raw_watches)if(!row.handle){watch=&row;break;}
    check(watch,"free_observer_slot");*watch={};watch->handle=*handle;watch->config_address=cfg;watch->config=*cfg;
    watch->stream=stream;watch->instance=++opens;++live_decoders;record_open("raw",watch->instance,stream,result);return result;
}
extern "C" esp_audio_err_t __wrap_esp_opus_dec_decode(void *handle,esp_audio_dec_in_raw_t *raw,esp_audio_dec_out_frame_t *frame,esp_audio_dec_info_t *info) {
    if(simple_depth)return __real_esp_opus_dec_decode(handle,raw,frame,info);
    owner(1,5);auto &watch=raw_watch(handle);uint32_t input=raw->len,capacity=frame->len;
    bool retry=watch.retry,advanced=!retry || (raw->buffer==watch.retry_pointer && raw->len==watch.retry_length && capacity==watch.retry_capacity);
    ++runtime_sdk_depth;auto result=__real_esp_opus_dec_decode(handle,raw,frame,info);--runtime_sdk_depth;++watch.calls;++process_calls;watch.consumed+=raw->consumed;watch.decoded+=frame->decoded_size;
    check(raw->len==input && raw->consumed<=input && frame->decoded_size<=capacity,"real_public_raw_byte_bounds");
    if(retry){++watch.retries;++resize_retry_checks;check(advanced,"genuine_raw_resize_retry_arguments");}
    watch.retry=false;
    if(result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        ++watch.resizes;++resize_requests;runtime_raw_growth_observed=true;check(!frame->decoded_size && frame->needed_size>capacity && frame->needed_size<=23040,"bounded_real_raw_buffer_request");
        watch.retry=true;watch.retry_pointer=raw->buffer+raw->consumed;watch.retry_length=input-raw->consumed;watch.retry_capacity=frame->needed_size;
    }
    printf("CYD_F1_OBS_CALL fixture=%s link=%u kind=raw instance=%u stream=%u call=%u input=%u consumed=%u capacity=%u decoded=%u needed=%u retry=%u advanced=%u result=%d\n",active->name,decode_link_index,watch.instance,watch.stream,watch.calls,(unsigned)input,(unsigned)raw->consumed,(unsigned)capacity,(unsigned)frame->decoded_size,(unsigned)frame->needed_size,(unsigned)retry,(unsigned)advanced,result);
    if(result!=ESP_AUDIO_ERR_OK && result!=ESP_AUDIO_ERR_BUFF_NOT_ENOUGH)++public_failures;
    if(frame->decoded_size)check(info->sample_rate==48000 && info->channel==watch.config.channel && info->bits_per_sample==16 && !(frame->decoded_size%(2u*info->channel)),"every_real_raw_output_geometry");
    return result;
}
extern "C" esp_audio_err_t __wrap_esp_opus_dec_close(void *handle) {
    if(simple_depth)return __real_esp_opus_dec_close(handle);
    owner(1,5);auto &watch=raw_watch(handle);check(watch.config_address && !memcmp(watch.config_address,&watch.config,sizeof(watch.config)),"stable_public_config_through_real_close");
    ++runtime_sdk_depth;auto result=__real_esp_opus_dec_close(handle);--runtime_sdk_depth;
    printf("CYD_F1_OBS_CLOSE fixture=%s link=%u kind=raw instance=%u stream=%u calls=%u consumed=%llu decoded=%llu resizes=%u retries=%u pending=%u buffer_pending=%u result=%d\n",active->name,decode_link_index,watch.instance,watch.stream,watch.calls,(unsigned long long)watch.consumed,(unsigned long long)watch.decoded,watch.resizes,watch.retries,(unsigned)(result!=ESP_AUDIO_ERR_OK),(unsigned)watch.retry,result);
    if(result==ESP_AUDIO_ERR_OK) {watch={};++closes;--live_decoders;if(!live_decoders)++decode_link_index;}
    return result;
}
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *,esp_audio_simple_dec_handle_t *);
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,esp_audio_simple_dec_raw_t *,esp_audio_simple_dec_out_t *);
extern "C" void __real_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t);
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,esp_audio_simple_dec_handle_t *handle) {
    owner(1,5);check(!live_decoders && decode_link()->layout==0 && cfg->dec_type==ESP_AUDIO_SIMPLE_DEC_TYPE_OGG && !cfg->use_frame_dec,"verified_legacy_head_selects_one_simple_owner");
    ++runtime_sdk_depth;++simple_depth;auto result=__real_esp_audio_simple_dec_open(cfg,handle);--simple_depth;--runtime_sdk_depth;
    if(result!=ESP_AUDIO_ERR_OK || !*handle)++public_failures;
    if(!*handle){record_open("simple",0,0,result);return result;}
    simple_handle=*handle;simple_instance=++opens;++live_decoders;simple_calls=simple_resizes=simple_retries=0;simple_retry=simple_drained=false;
    record_open("simple",simple_instance,0,result);return result;
}
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t handle,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *frame) {
    owner(1,5);check(handle==simple_handle && live_decoders==1,"real_live_simple_process");uint32_t input=raw->len,capacity=frame->len;bool retry=simple_retry;
    bool advanced=!retry || (raw->buffer==simple_retry_pointer && input==simple_retry_length && capacity==simple_retry_capacity && raw->eos==simple_retry_eos);
    if(!simple_calls)check(capacity==12288,"legacy_initial_capacity_restored_after_raw_link");
    ++runtime_sdk_depth;++simple_depth;auto result=__real_esp_audio_simple_dec_process(handle,raw,frame);--simple_depth;--runtime_sdk_depth;++simple_calls;++process_calls;
    check(raw->consumed<=input && frame->decoded_size<=capacity,"real_simple_byte_bounds");simple_retry=false;
    if(retry){++simple_retries;++resize_retry_checks;check(advanced,"genuine_simple_resize_retry_arguments");}
    if(result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        ++simple_resizes;++resize_requests;check(!frame->decoded_size && frame->needed_size>capacity,"genuine_simple_buffer_growth");
        simple_retry=true;simple_retry_pointer=raw->buffer+raw->consumed;simple_retry_length=input-raw->consumed;simple_retry_capacity=frame->needed_size;simple_retry_eos=raw->eos;
    }
    if(raw->eos && result==ESP_AUDIO_ERR_OK && !input && !raw->consumed && !frame->decoded_size)simple_drained=true;
    printf("CYD_F1_OBS_CALL fixture=%s link=%u kind=simple instance=%u stream=0 call=%u input=%u consumed=%u capacity=%u decoded=%u needed=%u retry=%u advanced=%u eos=%u result=%d\n",active->name,decode_link_index,simple_instance,simple_calls,(unsigned)input,(unsigned)raw->consumed,(unsigned)capacity,(unsigned)frame->decoded_size,(unsigned)frame->needed_size,(unsigned)retry,(unsigned)advanced,(unsigned)raw->eos,result);
    if(result!=ESP_AUDIO_ERR_OK && result!=ESP_AUDIO_ERR_BUFF_NOT_ENOUGH)++public_failures;
    return result;
}
extern "C" void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t handle) {
    owner(1,5);check(handle==simple_handle && live_decoders==1,"genuine_public_simple_close_identity");
    ++runtime_sdk_depth;++simple_depth;__real_esp_audio_simple_dec_close(handle);--simple_depth;--runtime_sdk_depth;
    printf("CYD_F1_OBS_CLOSE fixture=%s link=%u kind=simple instance=%u stream=0 calls=%u drained=%u resizes=%u retries=%u pending=0 buffer_pending=%u result=0\n",active->name,decode_link_index,simple_instance,simple_calls,(unsigned)simple_drained,simple_resizes,simple_retries,(unsigned)simple_retry);
    simple_handle=nullptr;++closes;--live_decoders;++decode_link_index;
}
