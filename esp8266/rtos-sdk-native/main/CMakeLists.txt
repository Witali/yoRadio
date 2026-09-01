set(YORADIO_AUDIO_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio/src/audioI2S")
set(YORADIO_SOURCES
    "app_main.c"
    "audio_service.c"
    "http_stream_protocol.c"
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
option(YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY
  "Discard decoded PCM instead of converting and sending PDM" OFF)
option(YORADIO_ESP8266_CODEC_RAM_BENCHMARK
  "Run embedded MP3/AAC frames repeatedly from RAM without Wi-Fi" OFF)
option(YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
  "Generate PCM in RAM and benchmark physical audio output without codecs" OFF)
if(YORADIO_ESP8266_CODEC_RAM_BENCHMARK AND
   YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK)
  message(FATAL_ERROR "Select only one isolated ESP8266 benchmark")
endif()
if(YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY AND
   NOT YORADIO_ESP8266_AUDIO_PROFILE)
  message(FATAL_ERROR "Decode-only mode requires the ESP8266 audio profile")
endif()
set(YORADIO_ESP8266_AUDIO_PROFILE_URL "" CACHE STRING
  "Optional HTTP stream automatically started by the audio profile")
set(YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP "" CACHE STRING
  "Optional static IPv4 address for an isolated audio profile")
set(YORADIO_ESP8266_AUDIO_PROFILE_GATEWAY "" CACHE STRING
  "Gateway paired with the profile static IPv4 address")
set(YORADIO_ESP8266_AUDIO_PROFILE_NETMASK "" CACHE STRING
  "Netmask paired with the profile static IPv4 address")
if(YORADIO_ESP8266_AUDIO_PROFILE)
  list(APPEND YORADIO_SOURCES "audio_profile_wrappers.cpp")
endif()
set(YORADIO_EMBED_FILES "../../../yoRadio/data/www/script.js.gz")
if(YORADIO_ESP8266_CODEC_RAM_BENCHMARK)
  list(APPEND YORADIO_SOURCES "codec_ram_benchmark.cpp")
  list(APPEND YORADIO_EMBED_FILES
    "../../../tests/fixtures/helix_golden/stereo-320.mp3"
    "../../../tests/fixtures/helix_golden/stereo-320.aac")
endif()
if(YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK)
  list(APPEND YORADIO_SOURCES "audio_output_benchmark.c")
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
           lwip nvs_flash pthread spiffs tcpip_adapter
  EMBED_FILES ${YORADIO_EMBED_FILES})

# ESP8266_RTOS_SDK exposes only -Og/-Os in menuconfig. Audio code needs the
# same explicit performance profile used by the ESP32-C3 native build.
target_compile_options(${COMPONENT_LIB} PRIVATE -O3
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++14>)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1
  YORADIO_HTTP_ONLY=1
  YORADIO_HELIX_MP3=1)
if(YORADIO_ESP8266_AUDIO_PROFILE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_AUDIO_PROFILE=1)
  if(YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE
      YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY=1)
  endif()
  if(YORADIO_ESP8266_AUDIO_PROFILE_URL)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE
      YORADIO_ESP8266_AUDIO_PROFILE_URL=\"${YORADIO_ESP8266_AUDIO_PROFILE_URL}\")
  endif()
  if(YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP)
    if(NOT YORADIO_ESP8266_AUDIO_PROFILE_GATEWAY OR
       NOT YORADIO_ESP8266_AUDIO_PROFILE_NETMASK)
      message(FATAL_ERROR "Profile static IPv4 requires gateway and netmask")
    endif()
    target_compile_definitions(${COMPONENT_LIB} PRIVATE
      YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP=\"${YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP}\"
      YORADIO_ESP8266_AUDIO_PROFILE_GATEWAY=\"${YORADIO_ESP8266_AUDIO_PROFILE_GATEWAY}\"
      YORADIO_ESP8266_AUDIO_PROFILE_NETMASK=\"${YORADIO_ESP8266_AUDIO_PROFILE_NETMASK}\")
  endif()
  target_link_libraries(${COMPONENT_LIB} INTERFACE
    "-Wl,--wrap=lwip_recv"
    "-Wl,--wrap=helix_codec_create"
    "-Wl,--wrap=helix_codec_switch"
    "-Wl,--wrap=helix_codec_commit"
    "-Wl,--wrap=native_audio_output_write"
    "-Wl,--wrap=native_audio_normalizer_process")
endif()
if(YORADIO_ESP8266_CODEC_RAM_BENCHMARK)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_CODEC_RAM_BENCHMARK=1)
endif()
if(YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=1)
endif()
if(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_HELIX_STAGE_PROFILE=1)
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
