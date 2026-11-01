// Whole production audio service; synthetic transport and output hardware only.
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
#include "native_network_power.h"
}

#ifdef NDEBUG
#error "The task diagnostic requires assertions"
#endif
extern const uint8_t opus20_start[] asm("_binary_fixture20_ogg_start");
extern const uint8_t opus20_end[] asm("_binary_fixture20_ogg_end");
extern const uint8_t opus120_start[] asm("_binary_fixture120_ogg_start");
extern const uint8_t opus120_end[] asm("_binary_fixture120_ogg_end");
extern const uint8_t vorbis_start[] asm("_binary_fixturevorbis_ogg_start");
extern const uint8_t vorbis_end[] asm("_binary_fixturevorbis_ogg_end");
struct patch_t { uint32_t offset; size_t size; const uint8_t *data; };
struct link_t { const uint8_t *begin,*end; const char *name,*family,*sha; int16_t gain;
                const patch_t *patches;size_t patch_count,max_page; };
struct fixture_t { const char *name;const link_t *links[9];size_t count;uint8_t volume;const char *mono[9];bool dump_stock; };
#include "reference.h"
static const fixture_t *active;
static size_t fixture_bytes() {
    size_t n=0; for (size_t i=0;i<active->count;++i) n+=(size_t)(active->links[i]->end-active->links[i]->begin);
    return n;
}
static size_t full_pcm() { return active->count*FULL_PCM_SINGLE; }
static size_t full_mono() { return active->count*FULL_MONO_SINGLE; }
static unsigned copy_encoded(uint8_t *to,size_t position,size_t bytes) {
    unsigned touched=0;
    for (size_t i=0;i<active->count && bytes;++i) {
        const link_t *link=active->links[i];size_t size=(size_t)(link->end-link->begin);
        if (position>=size) { position-=size;continue; }
        size_t n=std::min(size-position,bytes);
        memcpy(to,link->begin+position,n);
        for (size_t j=0;j<link->patch_count;++j) {
            const patch_t &patch=link->patches[j];
            size_t first=std::max(position,(size_t)patch.offset),last=std::min(position+n,(size_t)patch.offset+patch.size);
            if (first<last) memcpy(to+first-position,patch.data+first-patch.offset,last-first);
        }
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
static std::atomic<unsigned> writes, metadata_checks, pauses, discard_generation;
static std::atomic<unsigned> discard_calls;
static std::atomic<uint32_t> session_generation;
static std::atomic<uint32_t> http_generation;
static std::atomic<size_t> pcm_bytes, client_position;
static std::atomic<bool> hold_after_pcm, hold_reads, cancelling;
static esp_http_client_handle_t current_client;
static esp_audio_simple_dec_handle_t current_decoder;
static unsigned read_index;
// Test-owned observation state; vendor arguments and application state are never changed.
static unsigned observed_instance, handle_calls, handle_resizes, handle_retries, last_capacity;
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
static psa_hash_operation_t render_hash=PSA_HASH_OPERATION_INIT,render_link_hash=PSA_HASH_OPERATION_INIT;
static size_t render_bytes,render_link_index,render_link_bytes,raw_dump_bytes;
static bool raw_dump_done;
static char render_sha[65];
static std::atomic<unsigned> gain_stamps,driver_writes,driver_preloads,driver_created,driver_deleted;
enum phase_t { INIT_PHASE,CONFIGURE_PHASE,PCM_PHASE,FLUSH_PHASE,PAUSE_PHASE,DISCARD_PHASE,IDLE_PHASE };
static phase_t phase=INIT_PHASE;
struct driver_model_t { bool live,enabled; };
static driver_model_t driver;
static i2s_chan_handle_t driver_handle() {return reinterpret_cast<i2s_chan_handle_t>(&driver);}


static void check(bool condition, const char *reason) {
    if (!condition) {
        printf("CYD_OGG_GAIN_TASK_FAILURE %s\n", reason);
        fflush(stdout);
        assert(condition);
    }
}
static void owner(int core, unsigned priority) {
    check(xPortGetCoreID() == core && uxTaskPriorityGet(nullptr) == priority, "actual_owner_profile");
}
template<class Predicate> static void wait_until(Predicate predicate, const char *reason) {
    const bool first_stock_eof=!strcmp(reason,"bounded_full_output_eof") &&
        active && active->dump_stock && !raw_dump_done;
    const int64_t budget_us=first_stock_eof?90000000:30000000;
    const int64_t deadline=esp_timer_get_time()+budget_us;
    if (first_stock_eof) printf("CYD_OGG_GAIN_CONTROL_CAPTURE_WAIT fixture=%s fixed_budget_ms=90000 ordinary_budget_ms=30000 whole_qemu_budget_ms=600000\n",active->name);
    while (!predicate()) {
        if (esp_timer_get_time()>=deadline) {
            native_state_t observed;native_state_snapshot(&state,&observed);
            auto input=audio_service_input_health();
            printf("CYD_OGG_GAIN_CONTROL_WAIT_TIMEOUT reason=%s live_clients=%u live_decoders=%u discard_sequence=%u discard_snapshot_generation=%u state_generation=%u input_available=%u input_leased=%u input_ready=%u input_reading=%u input_writing=%u\n",
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
    check(!live_clients && !live_decoders, "configure_public_owners_quiet");
    xSemaphoreTake(output_lock, portMAX_DELAY);
    check(psa_hash_abort(&output_hash) == PSA_SUCCESS, "abort_previous_hash");
    check(psa_hash_setup(&output_hash, PSA_ALG_SHA_256) == PSA_SUCCESS, "start_output_hash");
    check(psa_hash_abort(&segment_hash) == PSA_SUCCESS && psa_hash_setup(&segment_hash,PSA_ALG_SHA_256) == PSA_SUCCESS,"start_segment_hash");
    segment_index=segment_bytes=0;
    check(psa_hash_abort(&render_hash)==PSA_SUCCESS && psa_hash_setup(&render_hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"start_render_hash");
    check(psa_hash_abort(&render_link_hash)==PSA_SUCCESS && psa_hash_setup(&render_link_hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"start_render_link_hash");
    render_bytes=render_link_index=render_link_bytes=0;render_sha[0]=0;
    check(native_audio_settings_set_volume(active->volume)==ESP_OK && native_audio_settings_set_balance(0)==ESP_OK &&
          native_audio_settings_set_normalization(false)==ESP_OK,"actual_player_settings");
    cross_link_reads=0;
    hash_finished = false;
    completed_sha[0] = 0;
    pcm_bytes = 0;
    writes = 0;
    metadata_checks = 0;
    cancelling = false;
    hold_after_pcm = hold;
    hold_reads = false;
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
        printf("CYD_OGG_GAIN_TASK_PROFILE role=%s core=%d priority=%u stack=%u\n",
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
    if (hold_reads) {
        xEventGroupSetBits(events, TRANSPORT_HELD);
        xSemaphoreTake(read_gate, pdMS_TO_TICKS(10));
        return -ESP_ERR_HTTP_EAGAIN;
    }
    static constexpr size_t sizes[] = {1, 257, 17, 1024, 31, 511};
    size_t position = client_position.load();
    size_t count = std::min<size_t>(capacity, sizes[read_index++ % 6]);
    count = std::min(count, (size_t)(fixture_bytes()) - position);
    if (count && copy_encoded((uint8_t *)buffer,position,count)>1) ++cross_link_reads;
    client_position = position + count;
    return (int)count;
}
extern "C" esp_err_t __wrap_esp_http_client_get_and_clear_last_tls_error(
        esp_http_client_handle_t client, int *error, int *flags) {
    client_check(client); if (error) *error = 0; if (flags) *flags = 0; return ESP_OK;
}
extern "C" bool __wrap_esp_http_client_is_complete_data_received(esp_http_client_handle_t client) {
    client_check(client); return !hold_reads && client_position == (size_t)(fixture_bytes());
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
    check(active && !live_decoders && config->dec_type==ESP_AUDIO_SIMPLE_DEC_TYPE_OGG && !config->use_frame_dec,
          "one_public_ogg_container");
    esp_audio_err_t result=__real_esp_audio_simple_dec_open(config,decoder);
    check(result==ESP_AUDIO_ERR_OK && *decoder,"real_vendor_open");
    current_decoder=*decoder;session_generation=snapshot().audio_generation;
    check(session_generation==http_generation,"same_http_generation_for_every_logical_link");
    observed_instance=++opens;handle_calls=handle_resizes=handle_retries=last_capacity=0;
    retry_pending=false;++live_decoders;
    printf("CYD_OGG_GAIN_OBS_OPEN fixture=%s instance=%u generation=%u\n",
           active->name,observed_instance,(unsigned)session_generation.load());
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
        printf("CYD_OGG_GAIN_OBS_INITIAL fixture=%s instance=%u call=%u global_call=%u capacity=%u\n",
               active->name,observed_instance,call,global_call,(unsigned)capacity);
        check(capacity>=12288,"production_initial_capacity_not_reduced");
    }
    esp_audio_err_t result=__real_esp_audio_simple_dec_process(decoder,raw,frame);
    ++process_calls;last_capacity=capacity;retry_pending=false;
    if (was_retry) {
        ++resize_retry_checks;++handle_retries;
        printf("CYD_OGG_GAIN_OBS_RETRY fixture=%s instance=%u call=%u global_call=%u capacity=%u raw_len=%u eos=%u arguments_advanced_once=%u consumed=%u decoded_size=%u needed_size=%u result=%d\n",
               active->name,observed_instance,call,global_call,(unsigned)capacity,(unsigned)raw_length,
               (unsigned)eos,(unsigned)unchanged,(unsigned)raw->consumed,(unsigned)frame->decoded_size,
               (unsigned)frame->needed_size,(int)result);
        check(capacity==retry_capacity && unchanged && result==ESP_AUDIO_ERR_OK,"real_resize_retry");
    }
    if (result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        ++resize_requests;++handle_resizes;
        printf("CYD_OGG_GAIN_OBS_RESIZE fixture=%s instance=%u call=%u global_call=%u raw_len=%u consumed=%u decoded_size=%u needed_size=%u capacity=%u eos=%u result=%d\n",
               active->name,observed_instance,call,global_call,(unsigned)raw_length,(unsigned)raw->consumed,
               (unsigned)frame->decoded_size,(unsigned)frame->needed_size,(unsigned)capacity,(unsigned)eos,(int)result);
        check(raw->consumed<=raw_length && !frame->decoded_size && frame->needed_size>capacity,"actual_public_buffer_error");
        retry_pending=true;retry_buffer=raw->buffer+raw->consumed;retry_length=raw_length-raw->consumed;
        retry_eos=eos;retry_capacity=frame->needed_size;
    }
    check(result==ESP_AUDIO_ERR_OK || result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH,"valid_vendor_process_result");
    return result;
}
extern "C" void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t decoder) {
    owner(1,5);check(live_decoders==1 && decoder==current_decoder,"one_public_close");
    __real_esp_audio_simple_dec_close(decoder);current_decoder=nullptr;--live_decoders;++closes;
    printf("CYD_OGG_GAIN_OBS_CLOSE fixture=%s instance=%u calls=%u resizes=%u retries=%u last_capacity=%u global_calls=%u\n",
           active->name,observed_instance,handle_calls,handle_resizes,handle_retries,last_capacity,process_calls.load());
    check(!retry_pending && handle_retries==handle_resizes,"all_observed_retries_completed_before_close");
}

// Only public driver calls are hardware seams; the complete renderer is real.
static void hex_digest(const uint8_t digest[32],char hex[65]) {
    for (unsigned i=0;i<32;++i) snprintf(hex+2*i,3,"%02x",(unsigned)digest[i]);
}
static void render(const uint8_t *data,size_t bytes) {
    xSemaphoreTake(output_lock,portMAX_DELAY);
    check(bytes%2==0 && render_bytes<=full_mono(),"actual_driver_mono_geometry");
    size_t count=std::min(bytes,full_mono()-render_bytes);
    check(phase==FLUSH_PHASE || count==bytes,"no_extra_pcm_before_final_flush");
    for (size_t i=count;i<bytes;++i) check(data[i]==0,"only_zero_padding_after_logical_mono");
    check(psa_hash_update(&render_hash,data,count)==PSA_SUCCESS,"hash_actual_driver_mono");
    size_t at=0;
    while (at<count) {
        check(render_link_index<active->count,"render_link_bound");
        size_t n=std::min(count-at,FULL_MONO_SINGLE-render_link_bytes);
        check(psa_hash_update(&render_link_hash,data+at,n)==PSA_SUCCESS,"hash_actual_render_link");
        render_link_bytes+=n;render_bytes+=n;at+=n;
        if (render_link_bytes==FULL_MONO_SINGLE) {
            uint8_t digest[32];size_t used=0;char hex[65];
            check(psa_hash_finish(&render_link_hash,digest,32,&used)==PSA_SUCCESS && used==32,"finish_render_link");hex_digest(digest,hex);
            if (active->mono[render_link_index]) check(!strcmp(hex,active->mono[render_link_index]),"exact_independent_decimal_mono");
            printf("CYD_OGG_GAIN_RENDER_LINK fixture=%s index=%u codec=%s gain_q8=%d volume=%u bytes=%u sha256=%s\n",
                   active->name,(unsigned)render_link_index,active->links[render_link_index]->name,
                   (int)active->links[render_link_index]->gain,(unsigned)active->volume,(unsigned)render_link_bytes,hex);
            ++render_link_index;render_link_bytes=0;
            if (render_link_index<active->count) check(psa_hash_setup(&render_link_hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"start_next_render_link");
        }
    }
    if (count) {
        if (hold_after_pcm.exchange(false)) hold_reads=true;
        xEventGroupSetBits(events,PCM_STARTED);
    }
    xSemaphoreGive(output_lock);
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
    ++driver_writes;if (phase==PCM_PHASE || phase==FLUSH_PHASE) render((const uint8_t *)data,bytes);
    else check(phase==CONFIGURE_PHASE || phase==PAUSE_PHASE,"bias_writes_classified_separately");
    *written=bytes;
    // A real DMA write blocks; the diagnostic public-driver seam must also
    // leave both enabled idle watchdogs runnable during the long full matrix.
    vTaskDelay(1);return ESP_OK;
}
extern "C" esp_err_t __real_native_audio_output_configure(uint32_t);
extern "C" esp_err_t __wrap_native_audio_output_configure(uint32_t rate) {
    owner(1,6);check(rate==48000,"actual_output_rate");phase=CONFIGURE_PHASE;auto result=__real_native_audio_output_configure(rate);phase=IDLE_PHASE;return result;
}
extern "C" esp_err_t __real_native_audio_output_set_header_gain(int16_t);
extern "C" esp_err_t __wrap_native_audio_output_set_header_gain(int16_t gain) {
    owner(1,6);size_t index=pcm_bytes.load()/FULL_PCM_SINGLE;
    check(active && index<active->count && gain==active->links[index]->gain,"actual_queued_header_gain_metadata");
    ++gain_stamps;return __real_native_audio_output_set_header_gain(gain);
}
static void dump_stock(const uint8_t *data,size_t bytes) {
    if (!active->dump_stock || raw_dump_done) return;
    static const char digits[]="0123456789abcdef";char hex[513];
    for (size_t at=0;at<bytes;) {
        size_t n=std::min((size_t)256,bytes-at);
        for (size_t i=0;i<n;++i) {hex[2*i]=digits[data[at+i]>>4];hex[2*i+1]=digits[data[at+i]&15];}hex[2*n]=0;
        printf("CYD_OGG_GAIN_STOCK offset=%u size=%u hex=%s\n",(unsigned)raw_dump_bytes,(unsigned)n,hex);
        raw_dump_bytes+=n;at+=n;
    }
    check(raw_dump_bytes<=FULL_PCM_SINGLE,"stock_capture_bounds");
    if (raw_dump_bytes==FULL_PCM_SINGLE) raw_dump_done=true;
    vTaskDelay(1); // Observation-only UART work must leave the real idle watchdog runnable.
}
extern "C" esp_err_t __real_native_audio_output_write_pcm(const uint8_t *,size_t,uint8_t,uint8_t);
extern "C" esp_err_t __wrap_native_audio_output_write_pcm(const uint8_t *data,size_t size,uint8_t bits,uint8_t channels) {
    owner(1,6);xSemaphoreTake(output_lock,portMAX_DELAY);
    check(!hash_finished && bits==16 && channels==2 && size && !(size%4),"source_pcm_geometry");
    auto info=snapshot();
    if (info.audio_generation==session_generation) {check(!strcmp(info.codec,"OGG") && info.sample_rate_hz==48000 && info.channels==2 && info.bits_per_sample==16,"actual_source_metadata");++metadata_checks;}
    else check(cancelling,"cancelled_old_source_generation");
    size_t position=pcm_bytes.load();check(position<=full_pcm() && size<=full_pcm()-position,"source_full_bounds");
    check(psa_hash_update(&output_hash,data,size)==PSA_SUCCESS,"hash_all_unchanged_source_pcm");
    size_t at=0;
    while (at<size) {
        check(segment_index<active->count,"source_link_bound");size_t n=std::min(size-at,FULL_PCM_SINGLE-segment_bytes);
        check(psa_hash_update(&segment_hash,data+at,n)==PSA_SUCCESS,"hash_source_link");at+=n;segment_bytes+=n;
        if (segment_bytes==FULL_PCM_SINGLE) {
            uint8_t digest[32];size_t used=0;char hex[65];check(psa_hash_finish(&segment_hash,digest,32,&used)==PSA_SUCCESS && used==32,"finish_source_link");hex_digest(digest,hex);
            check(!strcmp(hex,active->links[segment_index]->sha),"exact_unchanged_stock_logical_pcm");
            printf("CYD_OGG_GAIN_LINK fixture=%s index=%u codec=%s bytes=%u sha256=%s\n",active->name,(unsigned)segment_index,active->links[segment_index]->name,(unsigned)segment_bytes,hex);
            ++segment_index;segment_bytes=0;if(segment_index<active->count)check(psa_hash_setup(&segment_hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"next_source_link_hash");
        }
    }
    pcm_bytes=position+size;++writes;
    uint8_t before[32],after[32];size_t used=0;
    check(psa_hash_compute(PSA_ALG_SHA_256,data,size,before,32,&used)==PSA_SUCCESS && used==32,"source_readonly_before");
    dump_stock(data,size);xSemaphoreGive(output_lock);
    phase=PCM_PHASE;auto result=__real_native_audio_output_write_pcm(data,size,bits,channels);phase=IDLE_PHASE;
    check(psa_hash_compute(PSA_ALG_SHA_256,data,size,after,32,&used)==PSA_SUCCESS && used==32 && !memcmp(before,after,32),"renderer_keeps_borrowed_pcm_immutable");
    return result;
}
extern "C" esp_err_t __real_native_audio_output_flush_pcm(void);
extern "C" esp_err_t __wrap_native_audio_output_flush_pcm(void) {
    owner(1,6);phase=FLUSH_PHASE;auto result=__real_native_audio_output_flush_pcm();phase=IDLE_PHASE;
    xSemaphoreTake(output_lock,portMAX_DELAY);
    check(result==ESP_OK && !hash_finished && pcm_bytes==full_pcm() && render_bytes==full_mono() && segment_index==active->count && render_link_index==active->count && !live_decoders,"all_links_precede_single_actual_eof");
    uint8_t digest[32];size_t used=0;check(psa_hash_finish(&output_hash,digest,32,&used)==PSA_SUCCESS && used==32,"finish_source_hash");hex_digest(digest,completed_sha);
    check(psa_hash_finish(&render_hash,digest,32,&used)==PSA_SUCCESS && used==32,"finish_driver_mono_hash");hex_digest(digest,render_sha);
    hash_finished=true;++output_flushes;xEventGroupSetBits(events,ENDED);xSemaphoreGive(output_lock);return result;
}
extern "C" void __real_native_audio_output_discard_pcm(void);
extern "C" void __wrap_native_audio_output_discard_pcm(void) {
    owner(1,6);phase=DISCARD_PHASE;__real_native_audio_output_discard_pcm();phase=IDLE_PHASE;
    xSemaphoreTake(output_lock,portMAX_DELAY);
    discard_generation=snapshot().audio_generation;
    unsigned sequence=++discard_calls;
    printf("CYD_OGG_GAIN_CONTROL_DISCARD fixture=%s sequence=%u time_us=%llu snapshot_generation=%u core=1 priority=6 pcm_bytes=%u mono_bytes=%u writes=%u driver_writes=%u real_returned=1\n",
           active->name,sequence,(unsigned long long)esp_timer_get_time(),discard_generation.load(),
           (unsigned)pcm_bytes.load(),(unsigned)render_bytes,writes.load(),driver_writes.load());
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

static void play(const char *url, native_codec_t codec = NATIVE_CODEC_OGG) {
    check(audio_service_play(url, codec) == ESP_OK, "actual_public_play");
}
static void complete() {
    wait_until([] { return (xEventGroupGetBits(events) & ENDED) != 0; }, "bounded_full_output_eof");
    wait_until([] { return !live_clients && !live_decoders && input_quiet(); }, "bounded_public_cleanup");
    wait_until([] {
        auto info = snapshot();
        return !info.audio_running && !info.audio_pending && !info.audio_failed && !strcmp(info.stream_format, "stream ended");
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
    printf("CYD_OGG_GAIN_MEMORY fixture=%s stage=%s heap_free=%u heap_min=%u largest_internal=%u\n",
           active->name,stage,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
}
static void print_full_result(const char *prefix) {
    printf("%s fixture=%s pcm_bytes=%u sha256=%s opens=%u closes=%u http_cleanup=%u writes=%u metadata=1\n",
           prefix,active->name,(unsigned)pcm_bytes.load(),completed_sha,opens.load(),closes.load(),http_cleanup.load(),writes.load());
    printf("CYD_OGG_GAIN_RENDER_CASE fixture=%s mono_bytes=%u sha256=%s volume=%u\n",active->name,(unsigned)render_bytes,render_sha,(unsigned)active->volume);
    check(fflush(stdout)==0,"flush_case_record");memory_record("EOF_DONE");
}
static void lifecycle(const fixture_t &fixture) {
    active=&fixture;unsigned base=opens.load(),clients=http_cleanup.load();
    size_t maximum_page=active->links[0]->max_page;
    printf("CYD_OGG_GAIN_TASK_FIXTURE fixture=%s encoded=%u max_page=%u\n",
           active->name,(unsigned)fixture_bytes(),(unsigned)maximum_page);
    configure(false);play("http://fixture/T0",NATIVE_CODEC_AUTO);complete();
    check(opens==base+1 && closes==base+1 && http_cleanup==clients+1,"first_instance_cleanup");
    print_full_result("CYD_OGG_GAIN_TASK_CASE id=T0 ordered_eof=1");

    configure(true);play("http://fixture/T1-old");held();cancelling=true;
    unsigned before_discard=discard_calls.load();
    uint32_t before_generation=snapshot().audio_generation;
    int64_t stop_request_us=esp_timer_get_time();
    printf("CYD_OGG_GAIN_CONTROL_STOP_REQUEST fixture=%s time_us=%llu before_sequence=%u before_generation=%u core=0\n",
           active->name,(unsigned long long)stop_request_us,before_discard,(unsigned)before_generation);
    audio_service_stop();
    uint32_t stopped_generation=snapshot().audio_generation;
    printf("CYD_OGG_GAIN_CONTROL_STOP_RETURN fixture=%s time_us=%llu stop_generation=%u before_sequence=%u current_sequence=%u\n",
           active->name,(unsigned long long)esp_timer_get_time(),(unsigned)stopped_generation,before_discard,discard_calls.load());
    // Real discard has no generation parameter. Its contemporaneous public
    // snapshot may precede Stop's separate state publication. Correlate the
    // actual output-owner completion event to this request sequence instead.
    wait_until([before_discard] {return !live_clients && !live_decoders && discard_calls==before_discard+1 && input_quiet();},"stop_output_owner_and_public_cleanup");
    uint32_t discarded_generation=discard_generation.load();size_t stopped_pcm=pcm_bytes.load();
    check(stopped_generation==before_generation+1 && stopped_pcm>0 && stopped_pcm<full_pcm() &&
          !strcmp(snapshot().stream_format,"stopped") && !(xEventGroupGetBits(events)&ENDED),"stopped_partial_output");
    unsigned stopped_writes=writes.load(),stopped_driver=driver_writes.load();size_t stopped_mono=render_bytes;
    vTaskDelay(pdMS_TO_TICKS(25));
    auto stop_health=audio_service_input_health();auto stopped_state=snapshot();
    check(discard_calls==before_discard+1 && !live_clients && !live_decoders && input_quiet() &&
          pcm_bytes==stopped_pcm && render_bytes==stopped_mono && writes==stopped_writes && driver_writes==stopped_driver &&
          !(xEventGroupGetBits(events)&ENDED) && stopped_state.audio_generation==stopped_generation &&
          !stopped_state.audio_running && !stopped_state.audio_pending && !stopped_state.audio_failed &&
          !strcmp(stopped_state.stream_format,"stopped"),"real_stop_discard_and_all_owners_stay_quiet");
    printf("CYD_OGG_GAIN_CONTROL_STOP_QUIET fixture=%s time_us=%llu stop_generation=%u discard_sequence=%u discard_snapshot_generation=%u live_decoders=%u live_clients=%u input_available=%u input_leased=%u input_ready=%u input_reading=%u input_writing=%u pcm_bytes=%u mono_bytes=%u writes=%u driver_writes=%u quiet_ticks=25 no_eof=1\n",
           active->name,(unsigned long long)esp_timer_get_time(),(unsigned)stopped_generation,discard_calls.load(),(unsigned)discarded_generation,
           live_decoders.load(),live_clients.load(),(unsigned)stop_health.available,(unsigned)stop_health.leased,(unsigned)stop_health.ready,(unsigned)stop_health.reading,(unsigned)stop_health.writing,
           (unsigned)stopped_pcm,(unsigned)stopped_mono,stopped_writes,stopped_driver);
    memory_record("STOP_QUIET");configure(false);play("http://fixture/T1-reopen");complete();
    check(opens==base+3 && closes==base+3 && http_cleanup==clients+3,"stop_reopen_instance_cleanup");
    char prefix[256];
    snprintf(prefix,sizeof(prefix),"CYD_OGG_GAIN_TASK_CASE id=T1 stop_reopen=1 partial_pcm=%u stop_generation=%u discard_snapshot_generation=%u discard_after_request=1 stop_quiet=1",(unsigned)stopped_pcm,(unsigned)stopped_generation,(unsigned)discarded_generation);
    print_full_result(prefix);

    configure(true);play("http://fixture/T2");held();cancelling=true;unsigned previous_pauses=pauses.load();
    audio_maintenance_token_t token={};
    check(audio_service_maintenance_begin(10000,&token)==ESP_OK && token.epoch,"actual_three_owner_maintenance");
    check(!live_clients && !live_decoders && pauses>previous_pauses && input_quiet(),"maintenance_all_owners_quiet");
    size_t held_pcm=pcm_bytes.load();check(held_pcm>0 && held_pcm<full_pcm() && !(xEventGroupGetBits(events)&ENDED),"maintenance_partial_output");
    memory_record("MAINTENANCE_HELD");
    check(audio_service_play("http://fixture/blocked",NATIVE_CODEC_OGG)==ESP_ERR_INVALID_STATE,"play_blocked_while_held");
    auto stale=token;configure(false);
    check(audio_service_maintenance_end(&token,true)==ESP_OK && !token.epoch,"valid_resume_token_consumed");
    check(audio_service_maintenance_end(&stale,true)==ESP_ERR_INVALID_STATE,"stale_resume_token_rejected");complete();
    check(opens==base+5 && closes==base+5 && http_cleanup==clients+5,"resume_instance_cleanup");
    snprintf(prefix,sizeof(prefix),"CYD_OGG_GAIN_TASK_CASE id=T2 maintenance_resume=1 partial_pcm=%u held_quiet=1 play_blocked=1 token_consumed=1 stale_rejected=1",(unsigned)held_pcm);
    print_full_result(prefix);
}
extern "C" void app_main(void) {
    check(xPortGetCoreID()==0 && opus20_end-opus20_start==706319 && opus120_end-opus120_start==707097 && vorbis_end-vorbis_start==703584,"coordinator_and_complete_fixtures");
    printf("CYD_OGG_GAIN_TASK_BOOT actual_audio_service_tu=1 actual_output_tu=1 sdk=%s coordinator=0 hardware=0\n",esp_get_idf_version());
    events=xEventGroupCreate();output_lock=xSemaphoreCreateMutex();read_gate=xSemaphoreCreateBinary();
    check(events && output_lock && read_gate && psa_crypto_init()==PSA_SUCCESS,"actual_test_sync_and_crypto");
    check(nvs_flash_init()==ESP_OK && native_audio_settings_init()==ESP_OK,"actual_fresh_nvs_and_settings");
    check(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK,"both_idle_watchdogs_enabled");
    native_state_init(&state);check(state.lock && native_health_start() && audio_service_start(&state)==ESP_OK,"actual_audio_service_start");check(profiles==3,"original_task_profiles");
    for (unsigned i=0;i<3;++i) lifecycle(lifecycles[i]);
    for (unsigned i=0;i<FULL_CASE_COUNT;++i) {
        active=&full_cases[i];configure(false);play("http://fixture/gain-full",NATIVE_CODEC_AUTO);complete();
        print_full_result("CYD_OGG_GAIN_TASK_CASE id=FULL complete_gain=1");
    }
    active=&chain_fixture;unsigned before_opens=opens.load(),before_clients=http_cleanup.load(),before_flushes=output_flushes.load();
    configure(false);play("http://fixture/gain-chain",NATIVE_CODEC_AUTO);complete();
    check(opens==before_opens+9 && closes==opens && http_cleanup==before_clients+1 && output_flushes==before_flushes+1 && cross_link_reads>0,"nine_gain_links_one_http_generation_eof");
    printf("CYD_OGG_GAIN_TASK_CHAIN links=9 one_http=1 same_generation=1 single_eof=1 cross_link_reads=%u pcm_bytes=%u mono_bytes=%u source_sha=%s render_sha=%s opens=%u closes=%u http_cleanup=%u\n",cross_link_reads.load(),(unsigned)pcm_bytes.load(),(unsigned)render_bytes,completed_sha,render_sha,opens.load(),closes.load(),http_cleanup.load());
    memory_record("CHAIN_DONE");audio_maintenance_token_t final_token={};check(audio_service_maintenance_begin(10000,&final_token)==ESP_OK,"final_public_quiescence");
    auto faults=native_health_snapshot().faults;check(!faults.decoder_failures && !faults.output_failures && !faults.stream_failures && !faults.allocation_failures,"no_pipeline_faults");
    check(opens==38 && closes==38 && http_cleanup==30 && output_flushes==24 && !live_clients && !live_decoders && !driver.live && driver_created==driver_deleted && raw_dump_done && raw_dump_bytes==FULL_PCM_SINGLE && input_quiet() && heap_caps_check_integrity_all(true),"final_actual_owners_driver_and_heap");
    printf("CYD_OGG_GAIN_TASK_COMPLETE cases=24 actual_audio_service_tu=1 actual_output_tu=1 opens=%u closes=%u http_cleanup=%u live_decoders=0 live_clients=0 process_calls=%u resizes=%u retries=%u gain_stamps=%u driver_writes=%u preloads=%u driver_created=%u driver_deleted=%u output_flushes=%u stream_stack_free=%u decode_stack_free=%u output_stack_free=%u heap_free=%u heap_min=%u largest_internal=%u heap_integrity=1 hardware=0 native_pending_vorbis_oracle=1\n",
          opens.load(),closes.load(),http_cleanup.load(),process_calls.load(),resize_requests.load(),resize_retry_checks.load(),gain_stamps.load(),driver_writes.load(),driver_preloads.load(),driver_created.load(),driver_deleted.load(),output_flushes.load(),
          (unsigned)uxTaskGetStackHighWaterMark(stream_task_handle),(unsigned)uxTaskGetStackHighWaterMark(decode_task_handle),(unsigned)uxTaskGetStackHighWaterMark(output_task_handle),(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
    check(fflush(stdout)==0,"flush_observations");esp_restart();
}
