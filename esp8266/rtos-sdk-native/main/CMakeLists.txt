set(YORADIO_AUDIO_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio/src/audioI2S")
set(YORADIO_SOURCES
    "app_main.c"
    "audio_service.c"
    "http_stream_protocol.c"
    "input_service.c"
    "native_state.c"
    "network_service.c"
    "esp8266_nodac_i2s.c"
    "native_audio_output.c"
    "native_audio_normalizer.cpp"
    "${YORADIO_AUDIO_DIR}/AudioNormalizer.cpp"
    "persistent_settings.c"
    "playlist_service.c"
    "radio_control.c"
    "status_led.c"
    "storage_service.c"
    "time_service.c")
list(APPEND YORADIO_SOURCES
    "web_pages_bridge.cpp"
    "web_service.c")
list(APPEND YORADIO_SOURCES "web_upload.c")
option(YORADIO_ESP8266_AUDIO_PROFILE
  "Measure ESP8266 radio decode and output stages" OFF)
option(YORADIO_ESP8266_MEMORY_PROFILE
  "Sample DRAM fragmentation and application stack margins over UART" OFF)
option(YORADIO_ESP8266_WEB_PROFILE
  "Log static HTTP handler read/send timings (no URLs or credentials)" OFF)
if(YORADIO_ESP8266_MEMORY_PROFILE)
  list(APPEND YORADIO_SOURCES "memory_profile.c")
endif()
set(YORADIO_ESP8266_AUDIO_PROFILE_WINDOW_MS "5000" CACHE STRING
  "Audio profile report interval; use 30000 to reduce UART interference")
if(NOT YORADIO_ESP8266_AUDIO_PROFILE_WINDOW_MS MATCHES "^[1-9][0-9]*$")
  message(FATAL_ERROR "Audio profile window must be a positive integer")
endif()
option(YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY
  "Discard decoded PCM instead of converting and sending PDM" OFF)
option(YORADIO_ESP8266_CODEC_RAM_BENCHMARK
  "Run embedded MP3/AAC frames repeatedly from RAM without Wi-Fi" OFF)
option(YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT
  "Include real PCM/PDM/DMA output in the isolated codec RAM benchmark" OFF)
if(YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT AND NOT YORADIO_ESP8266_CODEC_RAM_BENCHMARK)
  message(FATAL_ERROR "RAM audio output requires CODEC_RAM_BENCHMARK")
endif()
option(YORADIO_ESP8266_DMA_COMMITTED_PREFIX
  "Submit safely committed DMA prefixes at EOF (OFF for A/B testing only)" ON)
option(YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
  "Generate PCM in RAM and benchmark physical audio output without codecs" OFF)
option(YORADIO_ESP8266_OUTPUT_COMPARE
  "Compare PDM packers before DMA and force reproducible benchmark settings" OFF)
set(YORADIO_ESP8266_RCPDM_VARIANT "production" CACHE STRING "Diagnostic-only RCPDM candidate")
option(YORADIO_ESP8266_RCPDM_BATCH "Fill RCPDM DMA spans directly at 48 kHz (OFF for A/B)" ON)
option(YORADIO_ESP8266_RCPDM_SIMPLE_UNROLL4 "Use four-bit LX106 assembly groups in the Simple experiment" OFF)
if(CONFIG_YORADIO_RCPDM_FEEDBACK AND NOT YORADIO_ESP8266_RCPDM_VARIANT STREQUAL "production")
  message(FATAL_ERROR "RC-PDM feedback cannot be combined with old bit-exact candidates")
endif()
if(NOT YORADIO_ESP8266_RCPDM_VARIANT MATCHES "^(production|simple|original|limit|unroll4|unroll8|unroll32|mask8|branchless8)$")
  message(FATAL_ERROR "Unknown RCPDM candidate")
endif()
if(NOT YORADIO_ESP8266_RCPDM_VARIANT STREQUAL "production" AND
   NOT (YORADIO_ESP8266_OUTPUT_COMPARE AND CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM))
  message(FATAL_ERROR "RCPDM candidates require the isolated RCPDM output comparison")
endif()
if(YORADIO_ESP8266_OUTPUT_COMPARE)
  if(NOT YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK)
    message(FATAL_ERROR "OUTPUT_COMPARE requires AUDIO_OUTPUT_BENCHMARK")
  endif()
endif()
option(YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
  "Generate a gated full-scale 1 kHz tone in the isolated output firmware" OFF)
if(YORADIO_ESP8266_OUTPUT_COMPARE)
  if(YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST OR
     NOT (CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM OR
          (CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM AND CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32)))
    message(FATAL_ERROR "OUTPUT_COMPARE requires finite generated PCM and I2S PDM32 or RCPDM32")
  endif()
endif()
option(YORADIO_ESP8266_AUDIO_TRACE
  "Log bounded PCM and final DMA PDM samples for physical audio diagnosis" OFF)
option(YORADIO_ESP8266_SPI_PDM_FAST_ISR
  "Bypass the generic SDK SPI dispatcher for continuous PDM output" ON)
option(YORADIO_ESP8266_KARADIO_PIPELINE
  "Use KaRadio-style network producer and compressed-stream ring" OFF)

if(YORADIO_ESP8266_CODEC_RAM_BENCHMARK AND
   YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK)
  message(FATAL_ERROR "Select only one isolated ESP8266 benchmark")
endif()
if(YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST AND
   NOT YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK)
  message(FATAL_ERROR "The tone test requires the audio output benchmark")
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
  REQUIRES app_update esp8266 esp_event esp_http_server freertos heap helix_codecs log
           lwip nvs_flash pthread spiffs tcpip_adapter
  EMBED_FILES ${YORADIO_EMBED_FILES})

# ESP8266_RTOS_SDK exposes only -Og/-Os in menuconfig. Audio code needs the
# same explicit performance profile used by the ESP32-C3 native build.
target_compile_options(${COMPONENT_LIB} PRIVATE -O3
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++14>)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1
  YORADIO_ESP8266_WEB_PROFILE=$<BOOL:${YORADIO_ESP8266_WEB_PROFILE}>
  YORADIO_HTTP_ONLY=1
  YORADIO_HELIX_MP3=1)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_DMA_COMMITTED_PREFIX=$<BOOL:${YORADIO_ESP8266_DMA_COMMITTED_PREFIX}>
  YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=$<BOOL:${YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT}>)
if(YORADIO_ESP8266_MEMORY_PROFILE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_MEMORY_PROFILE=1)
endif()
if(YORADIO_ESP8266_KARADIO_PIPELINE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_KARADIO_PIPELINE=1)
endif()

if(YORADIO_ESP8266_AUDIO_PROFILE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_AUDIO_PROFILE=1)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_AUDIO_PROFILE_WINDOW_MS=${YORADIO_ESP8266_AUDIO_PROFILE_WINDOW_MS})
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
if(YORADIO_ESP8266_OUTPUT_COMPARE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_ESP8266_OUTPUT_COMPARE=1)
  target_include_directories(${COMPONENT_LIB} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../../tests/native")
  if(YORADIO_ESP8266_RCPDM_VARIANT STREQUAL "simple")
    target_compile_definitions(${COMPONENT_LIB} PRIVATE
      RCPDM_TEST_SIMPLE=1 RCPDM_TEST_SAMPLE=rcpdm_simple_sample)
    if(YORADIO_ESP8266_RCPDM_SIMPLE_UNROLL4)
      target_compile_definitions(${COMPONENT_LIB} PRIVATE RCPDM_SIMPLE_UNROLL4=1)
    else()
      target_compile_definitions(${COMPONENT_LIB} PRIVATE RCPDM_SIMPLE_UNROLL4=0)
    endif()
  elseif(NOT YORADIO_ESP8266_RCPDM_VARIANT STREQUAL "production")
    target_compile_definitions(${COMPONENT_LIB} PRIVATE RCPDM_TEST_SAMPLE=rc_candidate_${YORADIO_ESP8266_RCPDM_VARIANT})
  endif()
endif()
if(NOT YORADIO_ESP8266_RCPDM_BATCH OR NOT YORADIO_ESP8266_RCPDM_VARIANT MATCHES "^(production|simple)$")
  target_compile_definitions(${COMPONENT_LIB} PRIVATE RCPDM_DISABLE_BATCH=1)
endif()
if(YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=1)
endif()
if(YORADIO_ESP8266_AUDIO_TRACE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_AUDIO_TRACE=1)
endif()
if(YORADIO_ESP8266_SPI_PDM_FAST_ISR)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM_FAST_ISR=1)
else()
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM_FAST_ISR=0)
endif()
if(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_HELIX_STAGE_PROFILE=1)
endif()
option(YORADIO_ESP8266_FIXED_I2S
  "Deprecated alias: force standard fixed-pin I2S PCM output" OFF)
if(YORADIO_ESP8266_FIXED_I2S)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_SPI_PDM=0
    YORADIO_ESP8266_I2S_PDM=0
    YORADIO_ESP8266_I2S_PCM=1)
elseif(CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM)
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
    # I2S RCPDM shares the same transport; Kconfig selects its modulator.
    YORADIO_ESP8266_I2S_PDM=1
    YORADIO_ESP8266_I2S_PCM=0)
endif()
if(CONFIG_YORADIO_HELIX_AAC)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_HELIX_AAC=1)
endif()
