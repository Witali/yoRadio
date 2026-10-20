#include "platform.h"
#include "native_audio_output.h"
#include "native_output_metrics.h"

_Thread_local unsigned critical_depth;
_Thread_local bool in_isr;
static atomic_uint clock_reads;
int64_t esp_timer_get_time(void) {
    CHECK(!critical_depth && !in_isr, "clock_outside_lock_and_isr");
    return (int64_t)atomic_fetch_add(&clock_reads,1)*7;
}
static struct { bool allocated, initialized, running, registered; } driver;
static i2s_event_callbacks_t registered_callbacks;
static unsigned allocations, enables, disables, deletions, preloads, registrations;
static bool fail_registration;
static esp_err_t next_result=ESP_OK;
static size_t next_report=SIZE_MAX;
static uint64_t ledger_requested, ledger_written;
static unsigned ledger_calls, ledger_errors, ledger_timeouts, ledger_shorts;
static uint32_t configured_rate;

void gpio_reset_pin(int pin) { CHECK(pin==26, "pdm_gpio26"); }
void gpio_set_direction(int pin,int mode) { CHECK(pin==26 && mode==GPIO_MODE_OUTPUT, "pdm_pin_mode"); }
void gpio_set_level(int pin,int level) { CHECK(pin==26 && level==0, "pdm_pin_low"); }
void vTaskDelay(unsigned ticks) { CHECK(ticks>0, "delay_nonzero"); }
bool native_audio_settings_get_normalization(void) { return false; }
uint8_t native_audio_settings_get_normalization_gain_db(void) { return 6; }
int8_t native_audio_settings_get_normalization_target_dbfs(void) { return -3; }
uint16_t native_audio_settings_get_normalization_time_ms(void) { return 500; }
uint8_t native_audio_settings_get_volume(void) { return 254; }
int8_t native_audio_settings_get_balance(void) { return 0; }
esp_err_t native_audio_settings_set_volume(uint8_t value) { (void)value; return ESP_OK; }
esp_err_t native_audio_settings_set_balance(int8_t value) { (void)value; return ESP_OK; }
void native_audio_normalizer_configure(bool enabled,uint8_t gain,int8_t target,uint16_t time,uint32_t rate) {
    (void)gain;(void)target;(void)time;CHECK(!enabled && rate, "normalizer_disabled_scope");
}
void native_audio_normalizer_reset(void) {}
void native_audio_normalizer_process_block(int16_t *pcm,size_t frames,uint8_t channels) {
    (void)pcm;(void)frames;(void)channels;CHECK(false,"normalizer_not_exercised");
}
static esp_err_t allocate(void **handle) {
    CHECK(!driver.allocated,"single_driver");
    driver.allocated=true;*handle=&driver;++allocations;return ESP_OK;
}
static void validate(void *handle) { CHECK(handle==&driver && driver.allocated,"driver_ownership"); }
static esp_err_t enable(void *handle) {
    validate(handle);CHECK(!driver.running,"enable_once");driver.running=true;++enables;return ESP_OK;
}
static esp_err_t disable(void *handle) {
    validate(handle);CHECK(driver.running,"disable_running");driver.running=false;++disables;return ESP_OK;
}
static esp_err_t release(void *handle) {
    validate(handle);CHECK(!driver.running,"delete_after_disable");
    memset(&driver,0,sizeof(driver));++deletions;return ESP_OK;
}
static esp_err_t write_driver(void *handle,const void *data,size_t bytes,size_t *written,unsigned timeout) {
    validate(handle);CHECK(driver.running && data && bytes && timeout,"actual_running_driver_call");
    CHECK(!critical_depth && !in_isr,"driver_outside_metric_lock");
    esp_err_t result=next_result;*written=next_report==SIZE_MAX?bytes:next_report;
    next_result=ESP_OK;next_report=SIZE_MAX;
    ++ledger_calls;ledger_requested+=bytes;ledger_written+=*written;
    ledger_errors+=(result!=ESP_OK || *written!=bytes);
    ledger_timeouts+=(result==ESP_ERR_TIMEOUT);ledger_shorts+=(*written<bytes);
    return result;
}
esp_err_t i2s_new_channel(const i2s_chan_config_t *config,i2s_chan_handle_t *handle,void *rx) {
    CHECK(config->id==I2S_NUM_0 && config->role==I2S_ROLE_MASTER && !rx &&
        config->dma_desc_num==8 && config->dma_frame_num==512 &&
        config->auto_clear_after_cb && !config->auto_clear_before_cb,"pdm_hardware_defaults");
    return allocate(handle);
}
esp_err_t i2s_channel_init_pdm_tx_mode(i2s_chan_handle_t handle,const i2s_pdm_tx_config_t *config) {
    validate(handle);CHECK(!driver.running && config->clk_cfg.sample_rate_hz==48000 &&
        config->slot_cfg.data_bit_width==16 && config->slot_cfg.slot_mode==I2S_SLOT_MODE_MONO &&
        config->gpio_cfg.clk==I2S_GPIO_UNUSED && config->gpio_cfg.dout==26 &&
        !config->gpio_cfg.invert_flags.clk_inv,"pdm_clock_pin_slot_defaults");
    driver.initialized=true;configured_rate=48000;return ESP_OK;
}
esp_err_t i2s_channel_register_event_callback(i2s_chan_handle_t handle,const i2s_event_callbacks_t *callbacks,void *context) {
    validate(handle);CHECK(driver.initialized && !driver.running && !preloads && !enables &&
        !context && callbacks->on_send_q_ovf && !callbacks->on_sent &&
        !callbacks->on_recv && !callbacks->on_recv_q_ovf,"register_before_enable_and_preload");
    ++registrations;if(fail_registration)return ESP_FAIL;
    registered_callbacks=*callbacks;driver.registered=true;return ESP_OK;
}
esp_err_t i2s_channel_preload_data(i2s_chan_handle_t handle,const void *data,size_t bytes,size_t *loaded) {
    validate(handle);CHECK(driver.registered && !driver.running && data && bytes==1024,"pdm_preload_after_registration");
    ++preloads;*loaded=bytes;return ESP_OK;
}
esp_err_t i2s_channel_enable(i2s_chan_handle_t handle) {
    CHECK(driver.registered && preloads==8,"pdm_enable_after_all_preloads");return enable(handle);
}
esp_err_t i2s_channel_disable(i2s_chan_handle_t handle) { return disable(handle); }
esp_err_t i2s_del_channel(i2s_chan_handle_t handle) { return release(handle); }
esp_err_t i2s_channel_get_info(i2s_chan_handle_t handle,i2s_chan_info_t *info) {
    validate(handle);info->bclk_hz=6144000;return ESP_OK;
}
esp_err_t i2s_channel_write(i2s_chan_handle_t handle,const void *data,size_t bytes,size_t *written,unsigned timeout) {
    CHECK(timeout==1000,"pdm_timeout_default");return write_driver(handle,data,bytes,written,timeout);
}
esp_err_t dac_continuous_new_channels(const dac_continuous_config_t *config,dac_continuous_handle_t *handle) {
    CHECK(config->chan_mask==DAC_CHANNEL_MASK_CH1 && config->desc_num==6 && config->buf_size==1024 &&
        config->freq_hz==48000 && config->offset==0 && config->clk_src==DAC_DIGI_CLK_SRC_APLL &&
        config->chan_mode==DAC_CHANNEL_MODE_SIMUL,"dac_hardware_defaults");
    configured_rate=config->freq_hz;return allocate(handle);
}
esp_err_t dac_continuous_enable(dac_continuous_handle_t handle) { return enable(handle); }
esp_err_t dac_continuous_disable(dac_continuous_handle_t handle) { return disable(handle); }
esp_err_t dac_continuous_del_channels(dac_continuous_handle_t handle) { return release(handle); }
esp_err_t dac_continuous_write(dac_continuous_handle_t handle,const void *data,size_t bytes,size_t *written,int timeout) {
    CHECK(timeout==(bytes==256?100:1000),"dac_timeout_defaults");
    return write_driver(handle,data,bytes,written,(unsigned)timeout);
}
esp_err_t idf6_dac_output_configure(const i2s_config_t *config,int channel) {
    CHECK(channel==I2S_DAC_CHANNEL_LEFT_EN && config->mode==(I2S_MODE_MASTER|I2S_MODE_TX|I2S_MODE_DAC_BUILT_IN) &&
        config->sample_rate==48000*16 && config->bits_per_sample==I2S_BITS_PER_SAMPLE_16BIT &&
        config->channel_format==I2S_CHANNEL_FMT_RIGHT_LEFT && config->communication_format==I2S_COMM_FORMAT_STAND_MSB &&
        config->intr_alloc_flags==ESP_INTR_FLAG_LEVEL1 && config->dma_buf_count==8 && config->dma_buf_len==512 &&
        !config->use_apll && !config->tx_desc_auto_clear && config->fixed_mclk==I2S_PIN_NO_CHANGE,"legacy_hardware_defaults");
    configured_rate=config->sample_rate;return ESP_OK;
}
esp_err_t idf6_dac_output_begin(void) { void *handle;esp_err_t e=allocate(&handle);return e?e:enable(handle); }
esp_err_t idf6_dac_output_end(void) { esp_err_t e=disable(&driver);return e?e:release(&driver); }
esp_err_t idf6_dac_output_set_sample_rate(unsigned rate) { configured_rate=rate;return ESP_OK; }
esp_err_t idf6_dac_output_write(const void *data,size_t bytes,size_t *written,unsigned timeout) {
    CHECK(timeout==1000,"legacy_timeout_default");return write_driver(&driver,data,bytes,written,timeout);
}

static void verify_metrics(const char *marker) {
    native_output_metrics_t view=native_output_metrics_snapshot();
    CHECK(view.writes==ledger_calls && view.requested_bytes==ledger_requested &&
        view.written_bytes==ledger_written && view.errors==ledger_errors &&
        view.timeouts==ledger_timeouts && view.short_writes==ledger_shorts,marker);
    CHECK(!view.saturated && !view.invalid_time_samples,"unsaturated_valid_metrics");
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    CHECK(view.timing_enabled && view.timing_samples==ledger_calls && view.write_us==ledger_calls*7ULL &&
        view.max_write_us==(ledger_calls?7U:0U) && atomic_load(&clock_reads)==ledger_calls*2U,"diagnostic_actual_call_timing");
#else
    CHECK(!view.timing_enabled && !view.timing_samples && !view.write_us && !view.max_write_us &&
        !atomic_load(&clock_reads),"quiet_no_clock_reads");
#endif
}
static void configure(void) {
    CHECK(native_audio_output_init()==ESP_OK,"public_init");
    verify_metrics("init_has_no_driver_writes");
    CHECK(native_audio_output_configure(48000)==ESP_OK,"public_configure");
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM
    CHECK(ledger_calls==2 && ledger_requested==1408 && preloads==8 && registrations==1,"pdm_prime_driver_units");
    CHECK(native_output_metrics_snapshot().queue_drops_available,"successful_registration_observed");
#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC
    CHECK(ledger_calls==1 && ledger_requested==1024,"dac_prime_driver_units");
    CHECK(!native_output_metrics_snapshot().queue_drops_available,"dac_no_queue_claim");
#else
    CHECK(ledger_calls==3 && ledger_requested==16384,"legacy_prime_driver_units");
    CHECK(!native_output_metrics_snapshot().queue_drops_available,"legacy_no_queue_claim");
#endif
    verify_metrics("prime_writes_accounted");
    CHECK(allocations==1 && enables==1 && driver.running && configured_rate,"configured_driver");
}
static void finish(void) {
    CHECK(native_audio_output_pause()==ESP_OK,"public_pause");
    CHECK(!driver.allocated && disables==1 && deletions==1,"public_cleanup");
    verify_metrics("pause_retains_cumulative_metrics");
}
static size_t frames_for_single_driver_call(void) {
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC
    return 16;
#else
    return 512;
#endif
}
static esp_err_t write_pcm(size_t frames) {
    uint8_t pcm[7000]={0};CHECK(frames*2<=sizeof(pcm),"test_pcm_bounds");
    return native_audio_output_write_pcm(pcm,frames*2,16,1);
}
static void write_outcomes(void) {
    configure();
    size_t frames=frames_for_single_driver_call();
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC
    const size_t requested=512;
#else
    const size_t requested=1024;
#endif
    const struct { esp_err_t result; size_t reported; } outcomes[]={
        {ESP_OK,requested},{ESP_FAIL,requested/2},{ESP_ERR_TIMEOUT,0},
        {ESP_OK,requested-1},{ESP_OK,requested+7},{ESP_ERR_TIMEOUT,requested}};
    for(size_t i=0;i<sizeof(outcomes)/sizeof(outcomes[0]);++i) {
        unsigned before=ledger_calls;uint64_t bytes_before=ledger_requested;
        next_result=outcomes[i].result;next_report=outcomes[i].reported;
        esp_err_t expected=outcomes[i].result!=ESP_OK?outcomes[i].result:
            (outcomes[i].reported==requested?ESP_OK:ESP_FAIL);
        CHECK(write_pcm(frames)==expected,"public_write_result");
        CHECK(ledger_calls==before+1 && ledger_requested==bytes_before+requested,"actual_pcm_driver_units");
        verify_metrics("actual_write_result_telemetry");
    }
    finish();
}
static void full_tail_idle(void) {
    configure();
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC
    unsigned before=ledger_calls;uint64_t bytes=ledger_requested;
    CHECK(write_pcm(3200)==ESP_OK,"dac_full_and_tail");
    CHECK(ledger_calls==before+2 && ledger_requested==bytes+3200,"dac_full_tail_units");
    verify_metrics("dac_full_tail_telemetry");
    before=ledger_calls;bytes=ledger_requested;next_result=ESP_ERR_TIMEOUT;next_report=12;
    native_audio_output_idle();
    CHECK(ledger_calls==before+1 && ledger_requested==bytes+256,"dac_idle_units");
    verify_metrics("dac_idle_telemetry");
#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM
    unsigned before=ledger_calls;uint64_t bytes=ledger_requested;
    CHECK(write_pcm(7)==ESP_OK && ledger_calls==before,"pdm_partial_is_buffered");
    CHECK(native_audio_output_flush_pcm()==ESP_OK,"pdm_public_flush");
    CHECK(ledger_calls==before+1 && ledger_requested==bytes+1024,"pdm_padded_flush_units");
    verify_metrics("pdm_flush_telemetry");
    native_audio_output_idle();CHECK(ledger_calls==before+1,"pdm_idle_no_driver_call");
#else
    unsigned before=ledger_calls;uint64_t bytes=ledger_requested;
    CHECK(write_pcm(100)==ESP_OK,"legacy_full_and_tail");
    CHECK(ledger_calls==before+2 && ledger_requested==bytes+6400,"legacy_full_tail_units");
    verify_metrics("legacy_full_tail_telemetry");
    before=ledger_calls;bytes=ledger_requested;next_result=ESP_ERR_TIMEOUT;next_report=12;
    native_audio_output_idle();
    CHECK(ledger_calls==before+1 && ledger_requested==bytes+6144,"legacy_idle_stops_after_error");
    verify_metrics("legacy_idle_telemetry");
#endif
    finish();
}
static void paused_excluded(void) {
    configure();
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM
    CHECK(write_pcm(7)==ESP_OK,"pre_pause_buffered_pcm");
#endif
    unsigned before=ledger_calls;
    native_audio_output_request_pause(true);
    CHECK(write_pcm(3200)==ESP_ERR_INVALID_STATE,"public_early_pause");
    native_audio_output_idle();
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM
    CHECK(native_audio_output_flush_pcm()==ESP_ERR_INVALID_STATE,"pdm_flush_early_pause");
#else
    CHECK(native_audio_output_flush_pcm()==ESP_OK,"empty_flush");
#endif
    CHECK(ledger_calls==before,"paused_has_no_driver_calls");
    verify_metrics("paused_requests_excluded");finish();
}
static void registration_failure(void) {
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM
    CHECK(native_audio_output_init()==ESP_OK,"public_init");fail_registration=true;
    CHECK(native_audio_output_configure(48000)==ESP_FAIL,"registration_error_propagated");
    CHECK(registrations==1 && !preloads && !enables && !driver.allocated && deletions==1 && !disables,"registration_failure_cleanup_before_enable");
    native_output_metrics_t view=native_output_metrics_snapshot();
    CHECK(!view.queue_drops_available && !view.completion_queue_drops,"failed_registration_unavailable");
    verify_metrics("failed_registration_no_writes");
#else
    CHECK(false,"pdm_only_case");
#endif
}
static void *isr_thread(void *unused) {
    (void)unused;in_isr=true;
    for(unsigned i=0;i<10000;++i) {
        i2s_event_data_t event={0};
        CHECK(!registered_callbacks.on_send_q_ovf(&driver,&event,NULL),"registered_callback_no_task_wakeup");
    }
    in_isr=false;return NULL;
}
static void callback_concurrent(void) {
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM
    configure();native_output_metrics_t base=native_output_metrics_snapshot();
    pthread_t thread;CHECK(!pthread_create(&thread,NULL,isr_thread,NULL),"isr_thread_start");
    for(unsigned i=0;i<100;++i) {
        CHECK(write_pcm(512)==ESP_OK,"concurrent_actual_pcm");
        native_output_metrics_t view=native_output_metrics_snapshot();
        CHECK(view.requested_bytes-base.requested_bytes==(uint64_t)(view.writes-base.writes)*1024 &&
            view.written_bytes==view.requested_bytes && !view.errors && view.completion_queue_drops<=10000 &&
            view.queue_drops_available,"coherent_public_snapshot");
    }
    CHECK(!pthread_join(thread,NULL),"isr_thread_join");
    CHECK(native_output_metrics_snapshot().completion_queue_drops==10000,"registered_isr_hook_count");
    verify_metrics("concurrent_writer_metrics");finish();
    native_output_metrics_t view=native_output_metrics_snapshot();
    CHECK(view.queue_drops_available && view.completion_queue_drops==10000,"pause_retains_queue_observations");
#else
    CHECK(false,"pdm_only_case");
#endif
}
int main(int argc,char **argv) {
    CHECK(argc==2,"case_argument");
    if(!strcmp(argv[1],"writes"))write_outcomes();
    else if(!strcmp(argv[1],"full-tail-idle"))full_tail_idle();
    else if(!strcmp(argv[1],"paused"))paused_excluded();
    else if(!strcmp(argv[1],"registration-failure"))registration_failure();
    else if(!strcmp(argv[1],"callback-concurrent"))callback_concurrent();
    else CHECK(false,"known_case");
    printf("PASS:%s\n",argv[1]);return 0;
}
