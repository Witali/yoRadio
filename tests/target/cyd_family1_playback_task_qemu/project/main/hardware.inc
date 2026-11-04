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
