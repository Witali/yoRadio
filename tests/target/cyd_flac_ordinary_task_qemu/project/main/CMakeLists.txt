set(M "$ENV{CYD_FLAC_TASK_FROZEN_ROOT}/idf/esp32-cyd2usb-native/main")
idf_component_register(SRCS "main.cpp" "${M}/audio_service.c" "${M}/native_state.c" "${M}/native_health.c" "${M}/decoder_registration.c"
 INCLUDE_DIRS "." "${M}" "$ENV{CYD_FLAC_TASK_FROZEN_ROOT}/idf/components/audio_level_led"
 "$ENV{CYD_FLAC_TASK_FROZEN_ROOT}/idf/components/native_wifi_store/include"
 REQUIRES native_stream native_network_power custom_flac custom_codec_support esp_audio_codec
 esp_http_client esp-tls esp_netif esp_ringbuf esp_timer esp_system esp_partition esp_driver_gpio mbedtls heap freertos log)
target_compile_definitions(${COMPONENT_LIB} PRIVATE FLAC_OUTPUT_FRAMES=512 FLAC_SEGMENTED_WORKSPACE=1)
foreach(symbol esp_http_client_init esp_http_client_open esp_http_client_fetch_headers esp_http_client_get_status_code
 esp_http_client_read esp_http_client_get_and_clear_last_tls_error esp_http_client_is_complete_data_received esp_http_client_cleanup
 custom_flac_decoder_create custom_flac_decoder_feed custom_flac_decoder_destroy xTaskCreatePinnedToCore)
 target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=${symbol}")
endforeach()
