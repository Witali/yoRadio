// Complete public AAC application tasks; transport and public hardware seams.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdio>
#include <cstring>
#include "esp_audio_simple_dec.h"
#include "esp_heap_caps.h"
#include "esp_http_client.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_timer.h"
#include "driver/i2s_pdm.h"
#include "driver/gpio.h"
#include "nvs_flash.h"
#include "board_config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "psa/crypto.h"
extern "C" {
#include "audio_service.h"
#include "native_audio_output.h"
#include "native_audio_settings.h"
#include "aac_public_config.h"
#include "native_network_power.h"
}

#ifdef NDEBUG
#error "The task diagnostic requires assertions"
#endif
#include "contract_types.h"
#include "reference.h"
static const fixture_t *active;
static fixture_t selected_fixture;
static uint32_t output_rate;
static reference_t &expected() {return aac_references[active->reference];}
static size_t fixture_bytes() {size_t bytes=0;for(unsigned i=0;i<active->part_count;++i)bytes+=entries[active->parts[i]].bytes;return bytes;}
static size_t full_pcm() {return expected().pcm_bytes;}
static unsigned copy_encoded(uint8_t *to,size_t position,size_t bytes) {
    unsigned touched=0;
    for(unsigned i=0;i<active->part_count && bytes;++i) {
        const entry_t &entry=entries[active->parts[i]];
        if(position>=entry.bytes) {position-=entry.bytes;continue;}
        size_t n=std::min(bytes,entry.bytes-position);memcpy(to,entry.data+position,n);
        to+=n;bytes-=n;position=0;++touched;
    }
    assert(!bytes);return touched;
}
static constexpr EventBits_t TRANSPORT_HELD = 1, PCM_STARTED = 2, ENDED = 4;
static native_state_t state;
static EventGroupHandle_t events;
static SemaphoreHandle_t output_lock, read_gate;
static TaskHandle_t stream_task_handle, decode_task_handle, output_task_handle;
static std::atomic<unsigned> profiles, opens, closes, live_decoders;
static std::atomic<unsigned> http_cleanup, live_clients, process_calls, resize_requests;
static std::atomic<unsigned> writes, pauses, discard_generation;
static std::atomic<unsigned> discard_calls;
static std::atomic<uint32_t> session_generation;
static std::atomic<uint32_t> http_generation;
static std::atomic<size_t> pcm_bytes, client_position;
static std::atomic<bool> cancelling;
static esp_http_client_handle_t current_client;
static esp_audio_simple_dec_handle_t current_decoder;
static unsigned read_index;
// Test-owned observation state; vendor arguments and application state are never changed.
static unsigned observed_instance, handle_calls, handle_resizes, handle_retries, last_capacity;
static size_t handle_consumed;
static unsigned handle_eos_calls;
static bool handle_drained,hold_announced;
static bool retry_pending;
static uint8_t *retry_buffer;
static uint32_t retry_length;
static bool retry_eos;
static std::atomic<unsigned> initial_capacity_checks, resize_retry_checks, cross_link_reads, output_flushes;
static uint32_t retry_capacity;
static psa_hash_operation_t segment_hash = PSA_HASH_OPERATION_INIT;
static size_t segment_index, segment_bytes;
static psa_hash_operation_t output_hash = PSA_HASH_OPERATION_INIT;
static bool hash_finished;
static char completed_sha[65];
static size_t driver_pcm_bytes;
static bool partial_transport;
static std::atomic<unsigned> public_infos,public_state_infos;

static std::atomic<unsigned> gain_stamps,driver_writes,driver_preloads,driver_created,driver_deleted;
static std::atomic<unsigned> layout_stamps;
enum phase_t { INIT_PHASE,CONFIGURE_PHASE,RATE_CONFIGURE_PHASE,PCM_PHASE,FLUSH_PHASE,PAUSE_PHASE,DISCARD_PHASE,IDLE_PHASE };
static phase_t phase=INIT_PHASE;
struct driver_model_t { bool live,enabled; };
static driver_model_t driver;
static i2s_chan_handle_t driver_handle() {return reinterpret_cast<i2s_chan_handle_t>(&driver);}


static void check(bool condition, const char *reason) {
    if (!condition) {
        printf("CYD_AAC_TASK_FAILURE %s\n", reason);
        fflush(stdout);
        assert(condition);
    }
}
static void owner(int core, unsigned priority) {
    check(xPortGetCoreID() == core && uxTaskPriorityGet(nullptr) == priority, "actual_owner_profile");
}
template<class Predicate> static void wait_until(Predicate predicate, const char *reason) {
    const int64_t deadline=esp_timer_get_time()+30000000;
    while (!predicate()) {
        if (esp_timer_get_time()>=deadline) {
            native_state_t observed;native_state_snapshot(&state,&observed);
            auto input=audio_service_input_health();
            printf("CYD_AAC_TASK_CONTROL_WAIT_TIMEOUT reason=%s live_clients=%u live_decoders=%u discard_sequence=%u discard_snapshot_generation=%u state_generation=%u input_available=%u input_leased=%u input_ready=%u input_reading=%u input_writing=%u\n",
                   reason,live_clients.load(),live_decoders.load(),discard_calls.load(),discard_generation.load(),
                   (unsigned)observed.audio_generation,(unsigned)input.available,(unsigned)input.leased,(unsigned)input.ready,(unsigned)input.reading,(unsigned)input.writing);
        }
        check(esp_timer_get_time() < deadline, reason);
        vTaskDelay(1);
    }
}
static native_state_t snapshot() {
    native_state_t result;
    native_state_snapshot(&state, &result);
    return result;
}
static bool input_quiet() {
    auto health = audio_service_input_health();
    return health.available && health.leased && !health.ready && !health.reading && !health.writing;
}
// Caller must first establish EOF, post-Stop output discard, or maintenance HELD.
static void configure(bool hold) {
    check(!live_clients && !live_decoders && expected().measured, "configure_public_owners_quiet_and_real_reference_measured");
    xSemaphoreTake(output_lock, portMAX_DELAY);
    check(psa_hash_abort(&output_hash) == PSA_SUCCESS, "abort_previous_hash");
    check(psa_hash_setup(&output_hash, PSA_ALG_SHA_256) == PSA_SUCCESS, "start_output_hash");
    check(psa_hash_abort(&segment_hash) == PSA_SUCCESS && psa_hash_setup(&segment_hash,PSA_ALG_SHA_256) == PSA_SUCCESS,"start_segment_hash");
    segment_index=segment_bytes=0;
    driver_pcm_bytes=0;output_rate=0;
    check(native_audio_settings_set_volume(254)==ESP_OK && native_audio_settings_set_balance(0)==ESP_OK &&
          native_audio_settings_set_normalization(false)==ESP_OK,"actual_player_settings");
    partial_transport=hold;
    hold_announced=false;
    cross_link_reads=0;
    hash_finished = false;
    completed_sha[0] = 0;
    pcm_bytes = 0;
    writes = 0;
    cancelling = false;
    xEventGroupClearBits(events, TRANSPORT_HELD | PCM_STARTED | ENDED);
    xSemaphoreGive(output_lock);
}

extern "C" BaseType_t __real_xTaskCreatePinnedToCore(TaskFunction_t, const char *, uint32_t,
    void *, UBaseType_t, TaskHandle_t *, BaseType_t);
extern "C" BaseType_t __wrap_xTaskCreatePinnedToCore(TaskFunction_t run, const char *name,
        uint32_t stack, void *arg, UBaseType_t priority, TaskHandle_t *task, BaseType_t core) {
    const char *role = nullptr;
    TaskHandle_t *observed = nullptr;
    if (!strcmp(name, "radio_stream")) {
        check(core == 0 && priority == 3 && stack == 6144, "stream_creation_profile");
        role = "stream"; observed = &stream_task_handle;
    } else if (!strcmp(name, "audio_decode")) {
        check(core == 1 && priority == 5 && stack == 16384, "decode_creation_profile");
        role = "decode"; observed = &decode_task_handle;
    } else if (!strcmp(name, "audio_output")) {
        check(core == 1 && priority == 6 && stack == 4096, "output_creation_profile");
        role = "output"; observed = &output_task_handle;
    }
    BaseType_t result = __real_xTaskCreatePinnedToCore(run, name, stack, arg, priority, task, core);
    if (role) {
        check(result == pdPASS && task && *task, "actual_pipeline_task_created");
        *observed = *task;
        ++profiles;
        printf("CYD_AAC_TASK_PROFILE role=%s core=%d priority=%u stack=%u\n",
            role, (int)core, (unsigned)priority, (unsigned)stack);
    }
    return result;
}

extern "C" esp_http_client_handle_t __real_esp_http_client_init(const esp_http_client_config_t *);
extern "C" esp_err_t __real_esp_http_client_cleanup(esp_http_client_handle_t);
extern "C" esp_http_client_handle_t __wrap_esp_http_client_init(const esp_http_client_config_t *config) {
    owner(0, 3);
    check(!live_clients && !live_decoders, "old_public_owners_released_before_http_init");
    auto client = __real_esp_http_client_init(config);
    check(client, "real_sdk_http_init");
    current_client = client;
    http_generation = snapshot().audio_generation;
    client_position = 0;
    read_index = 0;
    ++live_clients;
    return client;
}
static void client_check(esp_http_client_handle_t client) {
    owner(0, 3);
    check(client == current_client && live_clients == 1, "real_http_identity");
}
extern "C" esp_err_t __wrap_esp_http_client_open(esp_http_client_handle_t client, int write_bytes) {
    client_check(client); check(!write_bytes, "read_only_transport"); return ESP_OK;
}
extern "C" int64_t __wrap_esp_http_client_fetch_headers(esp_http_client_handle_t client) {
    client_check(client); return fixture_bytes();
}
extern "C" int __wrap_esp_http_client_get_status_code(esp_http_client_handle_t client) {
    client_check(client); return 200;
}
extern "C" int __wrap_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int capacity) {
    client_check(client);
    const size_t position=client_position.load();
    const size_t boundary=entries[active->parts[0]].hold_offset;
    if (partial_transport && position>=boundary) {
        check(position==boundary,"independently_counted_early_ADTS_boundary");
        if(!hold_announced) {
            hold_announced=true;
            printf("CYD_AAC_TASK_CONTROL_TRANSPORT_HELD fixture=%s position=%u boundary=%u encoded=%u core=0 priority=3 genuine_read=1\n",
                   active->name,(unsigned)position,(unsigned)boundary,(unsigned)fixture_bytes());
        }
        xEventGroupSetBits(events,TRANSPORT_HELD);xSemaphoreTake(read_gate,pdMS_TO_TICKS(10));return -ESP_ERR_HTTP_EAGAIN;
    }
    static constexpr size_t sizes[]={1,257,17,1024,31,511};
    size_t requested=active->schedule==1?1:active->schedule==2?257:active->schedule==3?4096:sizes[read_index++%6];
    size_t count=std::min<size_t>(capacity,requested);count=std::min(count,fixture_bytes()-position);
    if(partial_transport)count=std::min(count,boundary-position);
    if(count && copy_encoded((uint8_t *)buffer,position,count)>1)++cross_link_reads;
    client_position = position + count;
    return (int)count;
}
extern "C" esp_err_t __wrap_esp_http_client_get_and_clear_last_tls_error(
        esp_http_client_handle_t client, int *error, int *flags) {
    client_check(client); if (error) *error = 0; if (flags) *flags = 0; return ESP_OK;
}
extern "C" bool __wrap_esp_http_client_is_complete_data_received(esp_http_client_handle_t client) {
    client_check(client); return !partial_transport && client_position == (size_t)(fixture_bytes());
}
extern "C" esp_err_t __wrap_esp_http_client_cleanup(esp_http_client_handle_t client) {
    client_check(client);
    esp_err_t result = __real_esp_http_client_cleanup(client);
    check(result == ESP_OK, "real_sdk_http_cleanup");
    current_client = nullptr;
    --live_clients;
    ++http_cleanup;
    return result;
}

extern "C" esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *, esp_audio_simple_dec_handle_t *);
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,
    esp_audio_simple_dec_raw_t *, esp_audio_simple_dec_out_t *);
extern "C" void __real_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t);
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_open(
        esp_audio_simple_dec_cfg_t *config, esp_audio_simple_dec_handle_t *decoder) {
    owner(1,5);
    check(active && !live_decoders && config->dec_type==ESP_AUDIO_SIMPLE_DEC_TYPE_AAC && !config->use_frame_dec,
          "one_public_AAC_container");
    check(config->dec_cfg && config->cfg_size==sizeof(esp_aac_dec_cfg_t),"actual_public_AAC_configuration_size");
    const esp_aac_dec_cfg_t *aac=(const esp_aac_dec_cfg_t *)config->dec_cfg;
    check(aac->aac_plus_enable && !aac->no_adts_header,"actual_public_AAC_Plus_preference");
    esp_audio_err_t result=__real_esp_audio_simple_dec_open(config,decoder);
    check(result==ESP_AUDIO_ERR_OK && *decoder,"real_vendor_open");
    current_decoder=*decoder;session_generation=snapshot().audio_generation;
    check(session_generation==http_generation,"same_http_generation_for_every_logical_link");
    observed_instance=++opens;handle_calls=handle_resizes=handle_retries=last_capacity=0;
    handle_consumed=0;handle_eos_calls=0;handle_drained=false;
    retry_pending=false;++live_decoders;
    printf("CYD_AAC_TASK_OBS_OPEN fixture=%s instance=%u generation=%u cfg_size=%u aac_plus=1 no_adts_header=0\n",
           active->name,observed_instance,(unsigned)session_generation.load(),(unsigned)config->cfg_size);
    return result;
}
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t decoder,
        esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *frame) {
    owner(1,5);check(live_decoders==1 && decoder==current_decoder,"live_public_process");
    unsigned call=++handle_calls,global_call=process_calls+1;
    uint32_t capacity=frame->len,raw_length=raw->len;bool eos=raw->eos,was_retry=retry_pending;
    bool unchanged=!was_retry || (raw->buffer==retry_buffer && raw->len==retry_length && raw->eos==retry_eos);
    if (call==1) {
        ++initial_capacity_checks;
        printf("CYD_AAC_TASK_OBS_INITIAL fixture=%s instance=%u call=%u global_call=%u capacity=%u\n",
               active->name,observed_instance,call,global_call,(unsigned)capacity);
        check(capacity>=12288,"production_initial_capacity_not_reduced");
    }
    esp_audio_err_t result=__real_esp_audio_simple_dec_process(decoder,raw,frame);
    ++process_calls;last_capacity=capacity;retry_pending=false;
    check(raw->consumed<=raw_length && frame->decoded_size<=capacity,"actual_public_process_bounds");
    handle_consumed+=raw->consumed;
    if(eos)++handle_eos_calls;
    if(eos && result==ESP_AUDIO_ERR_OK && !raw_length && !raw->consumed && !frame->decoded_size)handle_drained=true;
    if (was_retry) {
        ++resize_retry_checks;++handle_retries;
        printf("CYD_AAC_TASK_OBS_RETRY fixture=%s instance=%u call=%u global_call=%u capacity=%u raw_len=%u eos=%u arguments_advanced_once=%u consumed=%u decoded_size=%u needed_size=%u result=%d\n",
               active->name,observed_instance,call,global_call,(unsigned)capacity,(unsigned)raw_length,
               (unsigned)eos,(unsigned)unchanged,(unsigned)raw->consumed,(unsigned)frame->decoded_size,
               (unsigned)frame->needed_size,(int)result);
        check(capacity==retry_capacity && unchanged && result==ESP_AUDIO_ERR_OK,"real_resize_retry");
    }
    if (result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        ++resize_requests;++handle_resizes;
        printf("CYD_AAC_TASK_OBS_RESIZE fixture=%s instance=%u call=%u global_call=%u raw_len=%u consumed=%u decoded_size=%u needed_size=%u capacity=%u eos=%u result=%d\n",
               active->name,observed_instance,call,global_call,(unsigned)raw_length,(unsigned)raw->consumed,
               (unsigned)frame->decoded_size,(unsigned)frame->needed_size,(unsigned)capacity,(unsigned)eos,(int)result);
        check(raw->consumed<=raw_length && !frame->decoded_size && frame->needed_size>capacity,"actual_public_buffer_error");
        retry_pending=true;retry_buffer=raw->buffer+raw->consumed;retry_length=raw_length-raw->consumed;
        retry_eos=eos;retry_capacity=frame->needed_size;
    }
    if (result!=ESP_AUDIO_ERR_OK && result!=ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        printf("CYD_AAC_TASK_OBS_PROCESS_ERROR fixture=%s instance=%u result=%d reference_result=%d raw_len=%u consumed=%u decoded_size=%u\n",
               active->name,observed_instance,(int)result,expected().result,(unsigned)raw_length,(unsigned)raw->consumed,(unsigned)frame->decoded_size);
        check(active->observational && !expected().success && result==expected().result,"observed_public_failure_matches_continuous_reference");
    }
    return result;
}
extern "C" void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t decoder) {
    owner(1,5);check(live_decoders==1 && decoder==current_decoder,"one_public_close");
    __real_esp_audio_simple_dec_close(decoder);current_decoder=nullptr;--live_decoders;++closes;
    printf("CYD_AAC_TASK_OBS_CLOSE fixture=%s instance=%u calls=%u resizes=%u retries=%u last_capacity=%u global_calls=%u input_consumed=%u eos_calls=%u drained=%u\n",
           active->name,observed_instance,handle_calls,handle_resizes,handle_retries,last_capacity,process_calls.load(),
           (unsigned)handle_consumed,handle_eos_calls,(unsigned)handle_drained);
    check(!retry_pending && handle_retries==handle_resizes,"all_observed_retries_completed_before_close");
}

// Only public driver calls are hardware seams; the complete renderer is real.
static void hex_digest(const uint8_t digest[32],char hex[65]) {
    for (unsigned i=0;i<32;++i) snprintf(hex+2*i,3,"%02x",(unsigned)digest[i]);
}
static void render(const uint8_t *,size_t bytes) {
    xSemaphoreTake(output_lock,portMAX_DELAY);check(bytes && !(bytes%2),"actual_PDM_driver_geometry");
    driver_pcm_bytes+=bytes;xEventGroupSetBits(events,PCM_STARTED);xSemaphoreGive(output_lock);
}
extern "C" esp_err_t __wrap_gpio_reset_pin(gpio_num_t pin) {check(pin==BOARD_AUDIO_DATA,"audio_gpio_reset");return ESP_OK;}
extern "C" esp_err_t __wrap_gpio_set_direction(gpio_num_t pin,gpio_mode_t mode) {check(pin==BOARD_AUDIO_DATA && mode==GPIO_MODE_OUTPUT,"audio_gpio_direction");return ESP_OK;}
extern "C" esp_err_t __wrap_gpio_set_level(gpio_num_t pin,uint32_t level) {check(pin==BOARD_AUDIO_DATA && !level,"audio_gpio_low");return ESP_OK;}
extern "C" esp_err_t __wrap_i2s_new_channel(const i2s_chan_config_t *cfg,i2s_chan_handle_t *tx,i2s_chan_handle_t *rx) {
    owner(1,6);check(!driver.live && tx && !rx && cfg->dma_desc_num==8 && cfg->dma_frame_num==512,"real_pdm_channel_configuration");
    driver.live=true;driver.enabled=false;*tx=driver_handle();++driver_created;return ESP_OK;
}
extern "C" esp_err_t __wrap_i2s_del_channel(i2s_chan_handle_t handle) {
    owner(1,6);check(handle==driver_handle() && driver.live && !driver.enabled,"pdm_delete_after_disable");driver.live=false;++driver_deleted;return ESP_OK;
}
extern "C" esp_err_t __wrap_i2s_channel_init_pdm_tx_mode(i2s_chan_handle_t handle,const i2s_pdm_tx_config_t *cfg) {
    owner(1,6);check(handle==driver_handle() && driver.live && cfg->clk_cfg.sample_rate_hz==48000 && cfg->gpio_cfg.dout==BOARD_AUDIO_DATA,"actual_pdm_clock_and_pin");return ESP_OK;
}
extern "C" esp_err_t __wrap_i2s_channel_enable(i2s_chan_handle_t handle) {owner(1,6);check(handle==driver_handle() && driver.live && !driver.enabled,"pdm_enable");driver.enabled=true;return ESP_OK;}
extern "C" esp_err_t __wrap_i2s_channel_disable(i2s_chan_handle_t handle) {owner(1,6);check(handle==driver_handle() && driver.live && driver.enabled,"pdm_disable");driver.enabled=false;return ESP_OK;}
extern "C" esp_err_t __wrap_i2s_channel_register_event_callback(i2s_chan_handle_t handle,const i2s_event_callbacks_t *callbacks,void *) {
    owner(1,6);check(handle==driver_handle() && driver.live && callbacks->on_send_q_ovf,"actual_pdm_callback_registration");return ESP_OK;
}
extern "C" esp_err_t __wrap_i2s_channel_get_info(i2s_chan_handle_t handle,i2s_chan_info_t *info) {
    owner(1,6);check(handle==driver_handle() && driver.live && info,"actual_pdm_info_request");*info={};info->bclk_hz=48000u*64u;return ESP_OK;
}
extern "C" esp_err_t __wrap_i2s_channel_preload_data(i2s_chan_handle_t handle,const void *data,size_t bytes,size_t *loaded) {
    owner(1,6);check(handle==driver_handle() && driver.live && !driver.enabled && phase==CONFIGURE_PHASE && data && bytes==1024,"separate_bias_preload");*loaded=bytes;++driver_preloads;return ESP_OK;
}
extern "C" esp_err_t __wrap_i2s_channel_write(i2s_chan_handle_t handle,const void *data,size_t bytes,size_t *written,uint32_t) {
    owner(1,6);check(handle==driver_handle() && driver.live && driver.enabled && data && written && bytes && !(bytes%2),"actual_pdm_write");
    ++driver_writes;if (phase==PCM_PHASE || phase==FLUSH_PHASE || phase==RATE_CONFIGURE_PHASE) render((const uint8_t *)data,bytes);
    else check(phase==CONFIGURE_PHASE || phase==PAUSE_PHASE,"bias_writes_classified_separately");
    *written=bytes;
    // A real DMA write blocks; the diagnostic public-driver seam must also
    // leave both enabled idle watchdogs runnable during the long full matrix.
    vTaskDelay(1);return ESP_OK;
}
extern "C" esp_err_t __real_native_audio_output_configure(uint32_t);
extern "C" esp_err_t __wrap_native_audio_output_configure(uint32_t rate) {
    owner(1,6);check(rate>=8000 && rate<=48000,"actual_output_rate");output_rate=rate;
    // A running PDM channel has no startup ramp. Its configure-time old-rate
    // flush contains real audio, which stays separate from initial bias writes.
    phase=driver.live && driver.enabled?RATE_CONFIGURE_PHASE:CONFIGURE_PHASE;
    auto result=__real_native_audio_output_configure(rate);phase=IDLE_PHASE;return result;
}
extern "C" esp_err_t __real_native_audio_output_set_header_gain(int16_t);
extern "C" esp_err_t __wrap_native_audio_output_set_header_gain(int16_t gain) {
    owner(1,6);check(gain==0,"ordinary_AAC_has_zero_Opus_header_gain");++gain_stamps;return __real_native_audio_output_set_header_gain(gain);
}
extern "C" esp_err_t __real_native_audio_output_set_channel_layout(pcm_channel_layout,uint8_t);
extern "C" esp_err_t __wrap_native_audio_output_set_channel_layout(pcm_channel_layout layout,uint8_t channels) {
    owner(1,6);
    check(segment_index<expected().run_count && layout==PCM_CHANNEL_LAYOUT_LEGACY &&
          channels==expected().runs[segment_index].channels,"ordinary_AAC_ordered_legacy_layout_metadata");
    ++layout_stamps;return __real_native_audio_output_set_channel_layout(layout,channels);
}
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_get_info(esp_audio_simple_dec_handle_t,esp_audio_simple_dec_info_t *);
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_get_info(esp_audio_simple_dec_handle_t decoder,esp_audio_simple_dec_info_t *info) {
    owner(1,5);check(decoder==current_decoder && live_decoders==1,"public_AAC_info_owner");
    auto result=__real_esp_audio_simple_dec_get_info(decoder,info);
    if(result==ESP_AUDIO_ERR_OK) {++public_infos;printf("CYD_AAC_TASK_INFO fixture=%s generation=%u rate=%u channels=%u bits=%u\n",active->name,(unsigned)session_generation.load(),(unsigned)info->sample_rate,(unsigned)info->channel,(unsigned)info->bits_per_sample);}
    return result;
}
extern "C" bool __real_native_state_set_stream_info(native_state_t *,uint32_t,const native_stream_info_t *);
extern "C" bool __wrap_native_state_set_stream_info(native_state_t *state_ptr,uint32_t generation,const native_stream_info_t *info) {
    owner(1,5);check(state_ptr==&state && info && !strcmp(info->codec,"AAC") && info->format_is_pcm && !info->channels_are_core,"truthful_public_PCM_metadata");
    bool result=__real_native_state_set_stream_info(state_ptr,generation,info);
    if(result) {
        ++public_state_infos;
        auto view=snapshot();const bool current=view.audio_generation==generation && !view.audio_failed;
        char details[80]={};native_state_format_stream_details(&view,details,sizeof(details));
        const bool pcm_label=strstr(details," PCM ") && !strstr(details,"HE");
        if(current) check(view.format_is_pcm && !view.channels_are_core && view.sample_rate_hz==info->sample_rate_hz &&
                          view.channels==info->channels && view.bits_per_sample==info->bits_per_sample && pcm_label,
                          "actual_current_state_and_formatter_report_confirmed_PCM");
        printf("CYD_AAC_TASK_STATE_INFO fixture=%s generation=%u rate=%u channels=%u bits=%u format_is_pcm=1 source_AOT_inferred=0 state_current=%u pcm_label=%u\n",active->name,(unsigned)generation,(unsigned)info->sample_rate_hz,(unsigned)info->channels,(unsigned)info->bits_per_sample,(unsigned)current,(unsigned)pcm_label);
    }
    return result;
}
extern "C" esp_err_t __real_native_audio_output_write_pcm(const uint8_t *,size_t,uint8_t,uint8_t);
extern "C" esp_err_t __wrap_native_audio_output_write_pcm(const uint8_t *data,size_t size,uint8_t bits,uint8_t channels) {
    owner(1,6);xSemaphoreTake(output_lock,portMAX_DELAY);
    check(!hash_finished && bits==16 && channels && channels<=2 && size && !(size%(channels*2)),"source_AAC_PCM_geometry");
    size_t position=pcm_bytes.load();check(position<=full_pcm() && size<=full_pcm()-position,"source_complete_reference_bounds");
    check(psa_hash_update(&output_hash,data,size)==PSA_SUCCESS,"hash_every_original_AAC_PCM_byte");
    size_t at=0;
    while(at<size) {
        check(segment_index<expected().run_count,"confirmed_metadata_run_bound");
        const pcm_run_t &run=expected().runs[segment_index];
        check(output_rate==run.rate && bits==run.bits && channels==run.channels,"actual_queued_PCM_geometry_matches_continuous_public_reference");
        const size_t n=std::min(size-at,run.bytes-segment_bytes);
        check(psa_hash_update(&segment_hash,data+at,n)==PSA_SUCCESS,"all_actual_metadata_run_PCM");at+=n;segment_bytes+=n;
        if(segment_bytes==run.bytes) {
            uint8_t digest[32];size_t used=0;char hex[65];check(psa_hash_finish(&segment_hash,digest,32,&used)==PSA_SUCCESS && used==32,"finish_actual_metadata_run");hex_digest(digest,hex);
            check(!strcmp(hex,run.sha),"complete_same_vendor_metadata_run_hash");
            printf("CYD_AAC_TASK_PCM_RUN fixture=%s index=%u rate=%u channels=%u bits=%u pcm_bytes=%u sha256=%s\n",active->name,(unsigned)segment_index,(unsigned)run.rate,(unsigned)run.channels,(unsigned)run.bits,(unsigned)segment_bytes,hex);
            ++segment_index;segment_bytes=0;if(segment_index<expected().run_count)check(psa_hash_setup(&segment_hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"next_actual_metadata_run");
        }
    }
    pcm_bytes=position+size;++writes;
    uint8_t before[32],after[32];size_t used=0;
    check(psa_hash_compute(PSA_ALG_SHA_256,data,size,before,32,&used)==PSA_SUCCESS && used==32,"source_readonly_before");
    xSemaphoreGive(output_lock);
    phase=PCM_PHASE;auto result=__real_native_audio_output_write_pcm(data,size,bits,channels);phase=IDLE_PHASE;
    check(psa_hash_compute(PSA_ALG_SHA_256,data,size,after,32,&used)==PSA_SUCCESS && used==32 && !memcmp(before,after,32),"renderer_keeps_borrowed_pcm_immutable");
    return result;
}
extern "C" esp_err_t __real_native_audio_output_flush_pcm(void);
extern "C" esp_err_t __wrap_native_audio_output_flush_pcm(void) {
    owner(1,6);phase=FLUSH_PHASE;auto result=__real_native_audio_output_flush_pcm();phase=IDLE_PHASE;
    xSemaphoreTake(output_lock,portMAX_DELAY);
    check(result==ESP_OK && !hash_finished && pcm_bytes==full_pcm() && segment_index==expected().run_count && !live_decoders,"complete_reference_before_actual_terminal_PCM");
    uint8_t digest[32];size_t used=0;check(psa_hash_finish(&output_hash,digest,32,&used)==PSA_SUCCESS && used==32,"finish_complete_AAC_PCM");hex_digest(digest,completed_sha);
    check(!strcmp(completed_sha,expected().sha),"whole_same_vendor_AAC_PCM_hash");
    hash_finished=true;++output_flushes;xEventGroupSetBits(events,ENDED);xSemaphoreGive(output_lock);return result;
}
extern "C" void __real_native_audio_output_discard_pcm(void);
extern "C" void __wrap_native_audio_output_discard_pcm(void) {
    owner(1,6);phase=DISCARD_PHASE;__real_native_audio_output_discard_pcm();phase=IDLE_PHASE;
    xSemaphoreTake(output_lock,portMAX_DELAY);
    discard_generation=snapshot().audio_generation;
    unsigned sequence=++discard_calls;
    printf("CYD_AAC_TASK_CONTROL_DISCARD fixture=%s sequence=%u time_us=%llu snapshot_generation=%u core=1 priority=6 pcm_bytes=%u driver_pcm_bytes=%u writes=%u driver_writes=%u real_returned=1\n",
           active->name,sequence,(unsigned long long)esp_timer_get_time(),discard_generation.load(),
           (unsigned)pcm_bytes.load(),(unsigned)driver_pcm_bytes,writes.load(),driver_writes.load());
    xSemaphoreGive(output_lock);
}
extern "C" esp_err_t __real_native_audio_output_pause(void);
extern "C" esp_err_t __wrap_native_audio_output_pause(void) {
    owner(1,6);check(!live_clients && !live_decoders,"three_owners_quiet_before_real_pause");phase=PAUSE_PHASE;auto result=__real_native_audio_output_pause();phase=IDLE_PHASE;++pauses;return result;
}
extern "C" void __real_native_audio_output_idle(void);
extern "C" void __wrap_native_audio_output_idle(void) {owner(1,6);phase=IDLE_PHASE;__real_native_audio_output_idle();}
extern "C" esp_err_t audio_level_led_init(void) { return ESP_OK; }
extern "C" void audio_level_led_update_peak(uint16_t peak) { (void)peak; }
extern "C" void audio_level_led_update_pcm(const uint8_t *data, size_t size, uint8_t bits, uint8_t channels) {
    (void)data; (void)size; (void)bits; (void)channels;
}
extern "C" void network_service_audio_accept(uint32_t generation, bool active) { native_network_power_accept(generation, active); }
extern "C" void network_service_audio_receive(uint32_t generation) { native_network_power_receive(generation); }
extern "C" void network_service_audio_finish(uint32_t generation) { native_network_power_finish(generation); }

static void play(const char *url, native_codec_t codec = NATIVE_CODEC_AAC) {
    check(audio_service_play(url, codec) == ESP_OK, "actual_public_play");
}
static void complete() {
    wait_until([] { return (xEventGroupGetBits(events) & ENDED) != 0; }, "bounded_full_output_eof");
    wait_until([] { return !live_clients && !live_decoders && input_quiet(); }, "bounded_public_cleanup");
    wait_until([] {
        auto info = snapshot();
        return !info.audio_running && !info.audio_pending && info.audio_failed!=expected().success;
    }, "public_final_eof_state");
    check(heap_caps_check_integrity_all(true), "complete_heap_integrity");
}
static void held() {
    wait_until([] { return (xEventGroupGetBits(events) & (TRANSPORT_HELD | PCM_STARTED)) ==
                              (TRANSPORT_HELD | PCM_STARTED); }, "hold_after_actual_pcm");
    check(live_clients == 1 && live_decoders == 1 && pcm_bytes > 0 && pcm_bytes < full_pcm() &&
          client_position < (size_t)(fixture_bytes()), "genuine_partial_stream");
    check(!(xEventGroupGetBits(events) & ENDED), "partial_stream_not_flushed");
}
static void memory_record(const char *stage) {
    printf("CYD_AAC_TASK_MEMORY fixture=%s stage=%s heap_free=%u heap_min=%u largest_internal=%u\n",
           active->name,stage,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
}
static void print_full_result(const char *prefix) {
    printf("%s fixture=%s reference=%u schedule=%u observed_only=%u expected_success=%u input_delivered=%u pcm_bytes=%u sha256=%s runs=%u opens=%u closes=%u http_cleanup=%u writes=%u header_zero=1 driver_pcm_bytes=%u cross_part_reads=%u\n",prefix,active->name,active->reference,active->schedule,(unsigned)active->observational,(unsigned)expected().success,(unsigned)client_position.load(),(unsigned)pcm_bytes.load(),completed_sha,(unsigned)segment_index,opens.load(),closes.load(),http_cleanup.load(),writes.load(),(unsigned)driver_pcm_bytes,cross_link_reads.load());
    check(fflush(stdout)==0,"flush_complete_AAC_case");memory_record("EOF_DONE");
}
static void lifecycle(const fixture_t &fixture) {
    active=&fixture;unsigned base=opens.load(),clients=http_cleanup.load();
    const entry_t &source=entries[active->parts[0]];
    printf("CYD_AAC_TASK_FIXTURE fixture=%s encoded=%u hold_offset=%u hold_after_frame=3\n",active->name,(unsigned)fixture_bytes(),(unsigned)source.hold_offset);
    configure(false);play("http://fixture/T0",NATIVE_CODEC_AUTO);complete();
    check(opens==base+1 && closes==base+1 && http_cleanup==clients+1,"first_instance_cleanup");
    print_full_result("CYD_AAC_TASK_CASE id=T0 ordered_eof=1");

    configure(true);play("http://fixture/T1-old");held();cancelling=true;
    unsigned before_discard=discard_calls.load();
    uint32_t before_generation=snapshot().audio_generation;
    int64_t stop_request_us=esp_timer_get_time();
    printf("CYD_AAC_TASK_CONTROL_STOP_REQUEST fixture=%s time_us=%llu before_sequence=%u before_generation=%u core=0\n",
           active->name,(unsigned long long)stop_request_us,before_discard,(unsigned)before_generation);
    audio_service_stop();
    uint32_t stopped_generation=snapshot().audio_generation;
    printf("CYD_AAC_TASK_CONTROL_STOP_RETURN fixture=%s time_us=%llu stop_generation=%u before_sequence=%u current_sequence=%u\n",
           active->name,(unsigned long long)esp_timer_get_time(),(unsigned)stopped_generation,before_discard,discard_calls.load());
    // Real discard has no generation parameter. Its contemporaneous public
    // snapshot may precede Stop's separate state publication. Correlate the
    // actual output-owner completion event to this request sequence instead.
    wait_until([before_discard] {return !live_clients && !live_decoders && discard_calls==before_discard+1 && input_quiet();},"stop_output_owner_and_public_cleanup");
    uint32_t discarded_generation=discard_generation.load();size_t stopped_pcm=pcm_bytes.load();
    check(stopped_generation==before_generation+1 && stopped_pcm>0 && stopped_pcm<full_pcm() &&
          !strcmp(snapshot().stream_format,"stopped") && !(xEventGroupGetBits(events)&ENDED),"stopped_partial_output");
    unsigned stopped_writes=writes.load(),stopped_driver=driver_writes.load();size_t stopped_mono=driver_pcm_bytes;
    vTaskDelay(pdMS_TO_TICKS(25));
    auto stop_health=audio_service_input_health();auto stopped_state=snapshot();
    check(discard_calls==before_discard+1 && !live_clients && !live_decoders && input_quiet() &&
          pcm_bytes==stopped_pcm && driver_pcm_bytes==stopped_mono && writes==stopped_writes && driver_writes==stopped_driver &&
          !(xEventGroupGetBits(events)&ENDED) && stopped_state.audio_generation==stopped_generation &&
          !stopped_state.audio_running && !stopped_state.audio_pending && !stopped_state.audio_failed &&
          !strcmp(stopped_state.stream_format,"stopped"),"real_stop_discard_and_all_owners_stay_quiet");
    printf("CYD_AAC_TASK_CONTROL_STOP_QUIET fixture=%s time_us=%llu stop_generation=%u discard_sequence=%u discard_snapshot_generation=%u live_decoders=%u live_clients=%u input_available=%u input_leased=%u input_ready=%u input_reading=%u input_writing=%u pcm_bytes=%u driver_pcm_bytes=%u writes=%u driver_writes=%u quiet_ticks=25 no_eof=1\n",
           active->name,(unsigned long long)esp_timer_get_time(),(unsigned)stopped_generation,discard_calls.load(),(unsigned)discarded_generation,
           live_decoders.load(),live_clients.load(),(unsigned)stop_health.available,(unsigned)stop_health.leased,(unsigned)stop_health.ready,(unsigned)stop_health.reading,(unsigned)stop_health.writing,
           (unsigned)stopped_pcm,(unsigned)stopped_mono,stopped_writes,stopped_driver);
    memory_record("STOP_QUIET");configure(false);play("http://fixture/T1-reopen");complete();
    check(opens==base+3 && closes==base+3 && http_cleanup==clients+3,"stop_reopen_instance_cleanup");
    char prefix[256];
    snprintf(prefix,sizeof(prefix),"CYD_AAC_TASK_CASE id=T1 stop_reopen=1 partial_pcm=%u stop_generation=%u discard_snapshot_generation=%u discard_after_request=1 stop_quiet=1",(unsigned)stopped_pcm,(unsigned)stopped_generation,(unsigned)discarded_generation);
    print_full_result(prefix);

    configure(true);play("http://fixture/T2");held();cancelling=true;unsigned previous_pauses=pauses.load();
    audio_maintenance_token_t token={};
    check(audio_service_maintenance_begin(10000,&token)==ESP_OK && token.epoch,"actual_three_owner_maintenance");
    check(!live_clients && !live_decoders && pauses>previous_pauses && input_quiet(),"maintenance_all_owners_quiet");
    size_t held_pcm=pcm_bytes.load();check(held_pcm>0 && held_pcm<full_pcm() && !(xEventGroupGetBits(events)&ENDED),"maintenance_partial_output");
    memory_record("MAINTENANCE_HELD");
    check(audio_service_play("http://fixture/blocked",NATIVE_CODEC_AAC)==ESP_ERR_INVALID_STATE,"play_blocked_while_held");
    auto stale=token;configure(false);
    check(audio_service_maintenance_end(&token,true)==ESP_OK && !token.epoch,"valid_resume_token_consumed");
    check(audio_service_maintenance_end(&stale,true)==ESP_ERR_INVALID_STATE,"stale_resume_token_rejected");complete();
    check(opens==base+5 && closes==base+5 && http_cleanup==clients+5,"resume_instance_cleanup");
    snprintf(prefix,sizeof(prefix),"CYD_AAC_TASK_CASE id=T2 maintenance_resume=1 partial_pcm=%u held_quiet=1 play_blocked=1 token_consumed=1 stale_rejected=1",(unsigned)held_pcm);
    print_full_result(prefix);
}
extern "C" void app_main(void) {
    check(xPortGetCoreID()==0,"coordinator_core");
    printf("CYD_AAC_TASK_BOOT sdk=%s actual_tasks=1 actual_output=1 public_config_only=1 hardware=0\n",esp_get_idf_version());
    events=xEventGroupCreate();output_lock=xSemaphoreCreateMutex();read_gate=xSemaphoreCreateBinary();aac_reference_events=events;
    check(events && output_lock && read_gate && psa_crypto_init()==PSA_SUCCESS,"actual_synchronization_and_crypto");
    check(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK,"both_idle_watchdogs_enabled");
    check(xTaskCreatePinnedToCore(aac_public_reference_worker,"aac_reference",16384,nullptr,3,nullptr,1)==pdPASS,"genuine_public_reference_worker");
    wait_until([]{return (xEventGroupGetBits(events)&AAC_REFERENCE_DONE)!=0;},"bounded_public_reference_phase");vTaskDelay(2);
    check(nvs_flash_init()==ESP_OK && native_audio_settings_init()==ESP_OK,"actual_fresh_settings");
    native_state_init(&state);check(state.lock && native_health_start() && audio_service_start(&state)==ESP_OK,"actual_audio_service_start");check(profiles==3,"original_task_profiles");
    for(unsigned i=0;i<AAC_BASE_COUNT;++i) {
        lifecycle(base_fixtures[i]);
        for(unsigned schedule=1;schedule<=3;++schedule) {
            selected_fixture=base_fixtures[i];selected_fixture.schedule=schedule;active=&selected_fixture;
            configure(false);play("http://fixture/aac-complete",NATIVE_CODEC_AUTO);complete();print_full_result("CYD_AAC_TASK_CASE id=FULL");
        }
    }
    unsigned observed_failures=0;
    for(unsigned i=0;i<AAC_OBSERVATION_COUNT;++i)for(unsigned schedule=0;schedule<3;++schedule) {
        selected_fixture=observation_fixtures[i];selected_fixture.schedule=schedule;active=&selected_fixture;
        configure(false);play("http://fixture/aac-continuous",NATIVE_CODEC_AUTO);complete();print_full_result("CYD_AAC_TASK_CASE id=OBSERVATION");
        if(!expected().success)++observed_failures;
    }
    audio_maintenance_token_t final_token={};check(audio_service_maintenance_begin(10000,&final_token)==ESP_OK,"final_public_quiescence");
    auto faults=native_health_snapshot().faults;
    check(!faults.output_failures && !faults.stream_failures && !faults.allocation_failures && faults.decoder_failures==observed_failures,"no_unexpected_pipeline_failures");
    check(opens==60 && closes==60 && http_cleanup==60 && output_flushes==48 && !live_clients && !live_decoders && !driver.live && driver_created==driver_deleted && input_quiet() && heap_caps_check_integrity_all(true),"all_real_AAC_owners_and_heap");
    printf("CYD_AAC_TASK_COMPLETE cases=48 base_cases=36 public_observations=12 reference_cases=10 opens=%u closes=%u http_cleanup=%u process_calls=%u initial_capacity_checks=%u resizes=%u retries=%u output_flushes=%u public_infos=%u public_state_infos=%u header_zero_stamps=%u legacy_layout_stamps=%u driver_created=%u driver_deleted=%u driver_writes=%u preloads=%u observed_public_failures=%u stream_stack_free=%u decode_stack_free=%u output_stack_free=%u heap_free=%u heap_min=%u largest_internal=%u heap_integrity=1 hardware=0 independent_codec_conformance=0 private_abi=0 reset_hooks=0\n",opens.load(),closes.load(),http_cleanup.load(),process_calls.load(),initial_capacity_checks.load(),resize_requests.load(),resize_retry_checks.load(),output_flushes.load(),public_infos.load(),public_state_infos.load(),gain_stamps.load(),layout_stamps.load(),driver_created.load(),driver_deleted.load(),driver_writes.load(),driver_preloads.load(),observed_failures,(unsigned)uxTaskGetStackHighWaterMark(stream_task_handle),(unsigned)uxTaskGetStackHighWaterMark(decode_task_handle),(unsigned)uxTaskGetStackHighWaterMark(output_task_handle),(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
    check(fflush(stdout)==0,"flush_complete_observations");esp_restart();
}
