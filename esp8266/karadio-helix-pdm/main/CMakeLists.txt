set(NATIVE_MAIN "${CMAKE_CURRENT_LIST_DIR}/../../rtos-sdk-native/main")
set(YORADIO_AUDIO_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio/src/audioI2S")

set(KARADIO_SOURCES
    "${NATIVE_MAIN}/app_main.c"
    "${NATIVE_MAIN}/audio_service.c"
    "${NATIVE_MAIN}/http_stream_protocol.c"
    "${NATIVE_MAIN}/input_service.c"
    "${NATIVE_MAIN}/native_state.c"
    "${NATIVE_MAIN}/network_service.c"
    "${NATIVE_MAIN}/esp8266_nodac_i2s.c"
    "${NATIVE_MAIN}/native_audio_output.c"
    "${NATIVE_MAIN}/native_audio_normalizer.cpp"
    "${YORADIO_AUDIO_DIR}/AudioNormalizer.cpp"
    "${NATIVE_MAIN}/persistent_settings.c"
    "${NATIVE_MAIN}/playlist_service.c"
    "${NATIVE_MAIN}/radio_control.c"
    "${NATIVE_MAIN}/status_led.c"
    "${NATIVE_MAIN}/storage_service.c"
    "${NATIVE_MAIN}/time_service.c"
    "${NATIVE_MAIN}/web_pages_bridge.cpp"
    "${NATIVE_MAIN}/web_service.c")

set(KARADIO_INCLUDE_DIRS "." "${NATIVE_MAIN}")
if(CONFIG_YORADIO_OLED)
  list(APPEND KARADIO_SOURCES "${NATIVE_MAIN}/display_service.c")
  list(APPEND KARADIO_INCLUDE_DIRS
       "${CMAKE_CURRENT_LIST_DIR}/../../../idf/esp32c3-oled-native/main")
endif()

idf_component_register(
  SRCS ${KARADIO_SOURCES}
  INCLUDE_DIRS ${KARADIO_INCLUDE_DIRS}
  REQUIRES esp8266 esp_event esp_http_server freertos heap helix_codecs log
           lwip nvs_flash pthread spiffs tcpip_adapter
  EMBED_FILES "../../../yoRadio/data/www/script.js.gz")

target_compile_options(${COMPONENT_LIB} PRIVATE -O3
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++14>)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1
  YORADIO_HTTP_ONLY=1
  YORADIO_HELIX_MP3=1
  YORADIO_ESP8266_KARADIO_PIPELINE=1
  YORADIO_ESP8266_AUDIO_PROFILE=0
  YORADIO_ESP8266_CODEC_RAM_BENCHMARK=0
  YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=0
  YORADIO_ESP8266_SPI_PDM_FAST_ISR=1)

if(CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM=1
    YORADIO_ESP8266_I2S_PDM=0
    YORADIO_ESP8266_I2S_PCM=0)
elseif(CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PCM)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM=0
    YORADIO_ESP8266_I2S_PDM=0
    YORADIO_ESP8266_I2S_PCM=1)
else()
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM=0
    YORADIO_ESP8266_I2S_PDM=1
    YORADIO_ESP8266_I2S_PCM=0)
endif()

if(CONFIG_YORADIO_HELIX_AAC)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_HELIX_AAC=1)
endif()
