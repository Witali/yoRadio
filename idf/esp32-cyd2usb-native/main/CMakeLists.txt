get_filename_component(YORADIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio" ABSOLUTE)

set(NATIVE_SRCS
  "app_main.c"
  "audio_service.c"
  "decoder_registration.c"
  "radio_control.c"
  "cyd_display.c"
  "native_audio_output.c"
  "native_state.c"
  "native_health.c"
  "native_health_json.c"
  "network_service.c"
  "web_service.c"
  "web_static.c"
  "web_pages.cpp"
  "websocket_service.c")

if(CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC)
  if(NOT DEFINED ENV{YORADIO_LEGACY_IDF})
    message(FATAL_ERROR "YORADIO_LEGACY_IDF is not set; use build.ps1")
  endif()
  file(TO_CMAKE_PATH "$ENV{YORADIO_LEGACY_IDF}" LEGACY_IDF)
  list(APPEND NATIVE_SRCS
    "compat/idf5_legacy_dac_backend.cpp"
    "${LEGACY_IDF}/components/driver/deprecated/i2s_legacy.c")
  set_source_files_properties(
    "${LEGACY_IDF}/components/driver/deprecated/i2s_legacy.c"
    PROPERTIES COMPILE_OPTIONS
      "-include;hal/i2s_periph.h;-I${LEGACY_IDF}/components/hal/esp32/include;-Wno-error=unused-but-set-parameter")
endif()

idf_component_register(
  SRCS ${NATIVE_SRCS}
  INCLUDE_DIRS "." "compat"
  REQUIRES
    efuse
    esp_adc
    esp_driver_gpio
    esp_driver_spi
    esp_driver_i2s
    esp_driver_dac
    esp_event
    esp_http_client
    esp_http_server
    esp_hw_support
    esp_lcd
    esp_netif
    esp_timer
    esp_system
    esp_wifi
    esp_ringbuf
    mbedtls
    nvs_flash
    spiffs
    audio_level_led
    native_audio_normalizer
    native_audio_settings
    native_storage
    native_stream
    custom_legacy_codecs
    esp_audio_codec
  PRIV_REQUIRES esp-tls)

include("${CMAKE_CURRENT_LIST_DIR}/compat/httpd_rfc6455/enable.cmake")
native_enable_httpd_rfc6455()

target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_ESP_IDF_NATIVE=1)

if(CONFIG_ESP_TLS_USING_MBEDTLS)
  target_sources(${COMPONENT_LIB} PRIVATE "tls_stream_eof.c")
  idf_component_get_property(tls_dir esp-tls COMPONENT_DIR)
  idf_component_get_property(tls_lib esp-tls COMPONENT_LIB)
  set_property(SOURCE "${tls_dir}/esp_tls_mbedtls.c" TARGET_DIRECTORY ${tls_lib}
    APPEND PROPERTY COMPILE_DEFINITIONS "mbedtls_ssl_read=yoradio_mbedtls_ssl_read")
  target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--undefined=yoradio_mbedtls_ssl_read")
endif()

if(CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC)
  target_include_directories(${COMPONENT_LIB} BEFORE PRIVATE
    "${LEGACY_IDF}/components/driver/deprecated"
    "${LEGACY_IDF}/components/esp_driver_i2s/include")
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_DAC_BACKEND_LEGACY=1
    CONFIG_I2S_SUPPRESS_DEPRECATE_WARN=1
    I2S_MODE_ADC_BUILT_IN=32
    SOC_I2S_NUM=2
    SOC_I2S_SUPPORTS_ADC_DAC=1
    SOC_I2S_SUPPORTS_ADC=0
    SOC_I2S_SUPPORTS_DAC=1)
endif()

spiffs_create_partition_image(spiffs "${YORADIO_ROOT}/data" FLASH_IN_PROJECT)
