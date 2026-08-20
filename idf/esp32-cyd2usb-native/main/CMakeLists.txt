get_filename_component(YORADIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio" ABSOLUTE)

set(NATIVE_SRCS
  "app_main.c"
  "audio_service.c"
  "cyd_display.c"
  "native_audio_output.c"
  "native_state.c"
  "network_service.c"
  "web_service.c")

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
    esp_wifi
    esp_ringbuf
    mbedtls
    nvs_flash
    spiffs
    audio_level_led
    custom_legacy_codecs
    esp_audio_codec)

target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_ESP_IDF_NATIVE=1)

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
