get_filename_component(YORADIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio" ABSOLUTE)

idf_component_register(
  SRCS
    "app_main.c"
    "audio_service.c"
    "cyd_display.c"
    "native_state.c"
    "network_service.c"
    "web_service.c"
  INCLUDE_DIRS "."
  REQUIRES
    esp_driver_gpio
    esp_driver_spi
    esp_driver_i2s
    esp_driver_dac
    esp_event
    esp_http_client
    esp_http_server
    esp_lcd
    esp_netif
    esp_timer
    esp_wifi
    esp_ringbuf
    mbedtls
    nvs_flash
    spiffs
    esp_audio_codec)

target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_ESP_IDF_NATIVE=1)

spiffs_create_partition_image(spiffs "${YORADIO_ROOT}/data" FLASH_IN_PROJECT)
