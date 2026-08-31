set(YORADIO_AUDIO_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio/src/audioI2S")
set(YORADIO_SOURCES
    "app_main.c"
    "audio_service.c"
    "input_service.c"
    "native_state.c"
    "network_service.c"
    "native_audio_output.c"
    "native_audio_normalizer.cpp"
    "${YORADIO_AUDIO_DIR}/AudioNormalizer.cpp"
    "persistent_settings.c"
    "playlist_service.c"
    "radio_control.c"
    "storage_service.c"
    "time_service.c")
list(APPEND YORADIO_SOURCES
    "web_pages_bridge.cpp"
    "web_service.c")
option(YORADIO_ESP8266_AUDIO_PROFILE
  "Measure ESP8266 radio decode and output stages" OFF)
if(YORADIO_ESP8266_AUDIO_PROFILE)
  list(APPEND YORADIO_SOURCES "audio_profile_wrappers.cpp")
endif()
set(YORADIO_INCLUDE_DIRS ".")
if(CONFIG_YORADIO_OLED)
  list(APPEND YORADIO_SOURCES "display_service.c")
  list(APPEND YORADIO_INCLUDE_DIRS
    "${CMAKE_CURRENT_LIST_DIR}/../../../idf/esp32c3-oled-native/main")
endif()

idf_component_register(
  SRCS ${YORADIO_SOURCES}
  INCLUDE_DIRS ${YORADIO_INCLUDE_DIRS}
  REQUIRES esp8266 esp_event esp_http_server freertos heap helix_codecs log
           lwip nvs_flash pthread spiffs tcpip_adapter)

# ESP8266_RTOS_SDK exposes only -Og/-Os in menuconfig. Audio code needs the
# same explicit performance profile used by the ESP32-C3 native build.
target_compile_options(${COMPONENT_LIB} PRIVATE -O3
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++14>)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1
  YORADIO_HTTP_ONLY=1
  YORADIO_HELIX_MP3=1)
if(YORADIO_ESP8266_AUDIO_PROFILE)
  target_link_libraries(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=lwip_recv"
    "-Wl,--wrap=helix_codec_switch"
    "-Wl,--wrap=helix_codec_commit"
    "-Wl,--wrap=native_audio_output_write"
    "-Wl,--wrap=native_audio_normalizer_process"
    "-Wl,--wrap=spi_trans")
endif()
option(YORADIO_ESP8266_FIXED_I2S
  "Use fixed ESP8266 I2S GPIO3/15/2 instead of UART-safe SPI-PDM" OFF)
if(YORADIO_ESP8266_FIXED_I2S)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM=0)
else()
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM=1)
endif()
if(CONFIG_YORADIO_HELIX_AAC)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_HELIX_AAC=1)
endif()
