get_filename_component(YORADIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio" ABSOLUTE)

set(NATIVE_SRCS
  "app_main.c"
  "audio_service.c"
  "native_audio_output.c"
  "native_state.c"
  "network_service.c"
  "oled_display.c"
  "radio_control.c"
  "web_pages_bridge.cpp"
  "web_service.c"
  "websocket_service.c")

idf_component_register(
  SRCS ${NATIVE_SRCS}
  INCLUDE_DIRS "."
  REQUIRES
    efuse
    esp_adc
    esp_driver_gpio
    esp_driver_i2c
    esp_driver_i2s
    esp_driver_ledc
    esp_event
    esp_http_client
    esp_http_server
    esp_hw_support
    esp_lcd
    esp_netif
    esp_partition
    esp_timer
    esp_wifi
    esp_ringbuf
    mbedtls
    nvs_flash
    spiffs
    custom_flac
    custom_legacy_codecs
    esp_audio_codec)

target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_ESP_IDF_NATIVE=1)
if(YORADIO_CODEC_BENCHMARK)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_CODEC_BENCHMARK=1)
endif()
target_compile_options(${COMPONENT_LIB} PRIVATE -O3)

set(NATIVE_SPIFFS_ROOT "${CMAKE_CURRENT_BINARY_DIR}/spiffs-root")
file(REMOVE_RECURSE "${NATIVE_SPIFFS_ROOT}")
file(MAKE_DIRECTORY "${NATIVE_SPIFFS_ROOT}")
file(COPY "${YORADIO_ROOT}/data/" DESTINATION "${NATIVE_SPIFFS_ROOT}")
configure_file("${YORADIO_ROOT}/../playlist.csv"
               "${NATIVE_SPIFFS_ROOT}/data/playlist.csv" COPYONLY)

spiffs_create_partition_image(spiffs "${NATIVE_SPIFFS_ROOT}" FLASH_IN_PROJECT)
