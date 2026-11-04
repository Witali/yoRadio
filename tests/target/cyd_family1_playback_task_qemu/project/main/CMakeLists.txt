set(M "$ENV{CYD_FAMILY1_PLAYBACK_TASK_FROZEN_ROOT}/idf/esp32-cyd2usb-native/main")
idf_component_register(SRCS "main.cpp" "reference_control.c" "direct_reference.c"
    "${M}/audio_service.c" "${M}/native_state.c" "${M}/native_health.c"
    "${M}/decoder_registration.c" "${M}/native_audio_output.c" "${M}/native_output_metrics.c"
    INCLUDE_DIRS "." "${M}" "$ENV{CYD_FAMILY1_PLAYBACK_TASK_FROZEN_ROOT}/idf/components/audio_level_led"
    "$ENV{CYD_FAMILY1_PLAYBACK_TASK_FROZEN_ROOT}/idf/components/native_wifi_store/include"
    REQUIRES native_stream native_network_power native_audio_settings native_audio_normalizer nvs_flash
    esp_driver_i2s esp_audio_codec esp_http_client esp-tls esp_netif esp_ringbuf esp_timer esp_system
    esp_driver_gpio mbedtls heap freertos log)
target_compile_options(${COMPONENT_LIB} PRIVATE -fstack-usage)
foreach(symbol esp_http_client_init esp_http_client_open esp_http_client_fetch_headers
    esp_http_client_get_status_code esp_http_client_read esp_http_client_get_and_clear_last_tls_error
    esp_http_client_is_complete_data_received esp_http_client_cleanup
    esp_audio_simple_dec_open esp_audio_simple_dec_process esp_audio_simple_dec_close
    esp_opus_dec_open esp_opus_dec_decode esp_opus_dec_close xTaskCreatePinnedToCore vTaskDelay
    heap_caps_malloc heap_caps_free heap_caps_register_failed_alloc_callback realloc
    native_audio_output_configure native_audio_output_set_channel_layout native_audio_output_set_header_gain
    native_audio_output_write_pcm native_audio_output_flush_pcm native_audio_output_pause
    native_audio_output_discard_pcm native_audio_output_idle
    native_state_set_stream_info
    native_audio_output_request_pause audio_service_maintenance_begin
    i2s_new_channel i2s_del_channel i2s_channel_init_pdm_tx_mode i2s_channel_enable i2s_channel_disable
    i2s_channel_write i2s_channel_preload_data i2s_channel_register_event_callback i2s_channel_get_info
    gpio_reset_pin gpio_set_direction gpio_set_level)
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=${symbol}")
endforeach()
target_add_binary_data(${COMPONENT_LIB} "${CMAKE_CURRENT_LIST_DIR}/fixtures.bin" BINARY)
