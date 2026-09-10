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
if(CONFIG_YORADIO_PLAYLIST_WEB_GZIP)
    list(APPEND YORADIO_SOURCES "playlist_web_cache.c" "small_gzip.c")
endif()
list(APPEND YORADIO_SOURCES
    "web_pages_bridge.cpp"
    "web_service.c")
list(APPEND YORADIO_SOURCES "web_upload.c")
option(YORADIO_ESP8266_AUDIO_PROFILE
  "Measure ESP8266 radio decode and output stages" OFF)
option(YORADIO_ESP8266_MEMORY_PROFILE
  "Sample DRAM fragmentation and application stack margins over UART" OFF)
option(YORADIO_ESP8266_SPIFFS_LOG
  "Mirror SDK logs to bounded SPIFFS files (diagnostic flash writes)" OFF)
option(YORADIO_ESP8266_DIAGNOSTIC
  "Enable explicitly requested diagnostic facilities, never for production" OFF)
if(YORADIO_ESP8266_SDK_RX_DIAG)
  if(NOT YORADIO_ESP8266_DIAGNOSTIC)
    message(FATAL_ERROR "SDK RX diagnostics require YORADIO_ESP8266_DIAGNOSTIC=ON")
  endif()
  list(APPEND YORADIO_SOURCES "sdk_rx_diag.c")
endif()
option(YORADIO_ESP8266_OPUS_STREAM_TEST
  "Allow diagnostic live Opus URL requests and init-failure snapshots" OFF)
option(YORADIO_ESP8266_OPUS_BENCHMARK
  "Run raw flash-fixture Opus benchmark on request while preserving WebUI/OTA" OFF)
option(YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
  "Include physical PDM/DMA output in the Opus flash-fixture benchmark" OFF)
if(YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT AND
   (NOT YORADIO_ESP8266_OPUS_BENCHMARK OR NOT CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM OR
    NOT CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32 OR YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY OR
    YORADIO_ESP8266_AUDIO_PROFILE OR YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK OR
    YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT))
  message(FATAL_ERROR "Opus output benchmark requires raw benchmark and physical standard I2S PDM32")
endif()
set(YORADIO_ESP8266_OPUS_BENCHMARK_FIXTURES "" CACHE PATH "Generated Opus board fixture directory")
if(YORADIO_ESP8266_OPUS_BENCHMARK)
  # Preserve the existing benchmark profile without making the cache sticky.
  set(YORADIO_ESP8266_OPUS_STREAM_TEST ON)
endif()
if(YORADIO_ESP8266_OPUS_STREAM_TEST)
  if(NOT YORADIO_ESP8266_DIAGNOSTIC OR NOT CONFIG_YORADIO_OGG_OPUS)
    message(FATAL_ERROR "Opus stream test/benchmark requires diagnostic Opus profile")
  endif()
endif()
if(YORADIO_ESP8266_OPUS_BENCHMARK)
  if(NOT EXISTS "${YORADIO_ESP8266_OPUS_BENCHMARK_FIXTURES}/opus_board_fixtures.h")
    message(FATAL_ERROR "Generate raw Opus fixtures with build_board_fixtures.cjs first")
  endif()
  list(APPEND YORADIO_SOURCES "opus_benchmark.cpp")
endif()
option(YORADIO_ESP8266_SPIFFS_LOG_HTTP
  "Allow read-only LAN download of SPIFFS logs in diagnostic builds" OFF)
if(YORADIO_ESP8266_SPIFFS_LOG AND NOT YORADIO_ESP8266_DIAGNOSTIC)
  message(FATAL_ERROR "SPIFFS logging requires YORADIO_ESP8266_DIAGNOSTIC=ON")
endif()
if(YORADIO_ESP8266_SPIFFS_LOG_HTTP AND NOT YORADIO_ESP8266_SPIFFS_LOG)
  message(FATAL_ERROR "SPIFFS log HTTP requires YORADIO_ESP8266_SPIFFS_LOG=ON")
endif()
if(YORADIO_ESP8266_SPIFFS_LOG)
  list(APPEND YORADIO_SOURCES "spiffs_log.c")
endif()
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
set(YORADIO_ESP8266_CODEC_RAM_FRAMES "200" CACHE STRING
  "Measured RAM codec frames; use 1500 for at least 30 seconds of MP3 and AAC output")
if(NOT YORADIO_ESP8266_CODEC_RAM_FRAMES MATCHES "^[1-9][0-9]*$" OR
   YORADIO_ESP8266_CODEC_RAM_FRAMES GREATER 10000)
  message(FATAL_ERROR "RAM codec frames must be between 1 and 10000")
endif()
if(YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT AND NOT YORADIO_ESP8266_CODEC_RAM_BENCHMARK)
  message(FATAL_ERROR "RAM audio output requires CODEC_RAM_BENCHMARK")
endif()
option(YORADIO_ESP8266_DMA_COMMITTED_PREFIX
  "Submit safely committed DMA prefixes at EOF (OFF for A/B testing only)" ON)
option(YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
  "Generate PCM in RAM and benchmark physical audio output without codecs" OFF)
option(YORADIO_ESP8266_OUTPUT_COMPARE
  "Compare PDM packers before DMA and force reproducible benchmark settings" OFF)
option(YORADIO_ESP8266_PDM32_IRAM
  "A/B: put PDM32 packer in IRAM and cold signed modulo in flash" OFF)
option(YORADIO_ESP8266_PDM32_BATCH
  "A/B: fill standard PDM32 DMA spans directly at 48 kHz" OFF)
set(YORADIO_ESP8266_PDM32_LOAN_WORDS "512" CACHE STRING "Diagnostic producer publication limit; DMA stays 2x512 words")
if(NOT YORADIO_ESP8266_PDM32_LOAN_WORDS MATCHES "^(64|128|256|512)$")
  message(FATAL_ERROR "PDM32 loan words must be 64, 128, 256 or 512")
endif()
if(NOT YORADIO_ESP8266_PDM32_LOAN_WORDS STREQUAL "512" AND
   (NOT YORADIO_ESP8266_DIAGNOSTIC OR NOT CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM OR
    NOT CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32))
  message(FATAL_ERROR "Short PDM32 loans require diagnostic standard I2S PDM32")
endif()
if(YORADIO_ESP8266_PDM32_BATCH AND
   (NOT CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM OR
    NOT CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32))
  message(FATAL_ERROR "PDM32 batch experiment requires standard I2S PDM32 output")
endif()
set(YORADIO_AUDIO_LDFRAGMENTS "")
if(YORADIO_ESP8266_PDM32_IRAM)
  if(NOT CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM OR
     NOT CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32)
    message(FATAL_ERROR "PDM32 IRAM experiment requires standard I2S PDM32 output")
  endif()
  list(APPEND YORADIO_AUDIO_LDFRAGMENTS "pdm32_iram.lf")
endif()
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
include("${CMAKE_CURRENT_LIST_DIR}/web_audio_pause.cmake")

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
option(YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX
  "Benchmark sequential MP3 64/128/320 from internal flash, without AAC" OFF)
option(YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX
  "Benchmark sequential AAC-LC 48/64/96 from internal flash" OFF)
if(YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX AND
   (NOT YORADIO_ESP8266_CODEC_RAM_BENCHMARK OR
    YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX OR NOT CONFIG_YORADIO_HELIX_AAC))
  message(FATAL_ERROR "AAC matrix requires benchmark, AAC enabled, and MP3 matrix OFF")
endif()
if(YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX AND NOT YORADIO_ESP8266_CODEC_RAM_BENCHMARK)
  message(FATAL_ERROR "MP3 matrix requires CODEC_RAM_BENCHMARK")
endif()
option(YORADIO_ESP8266_NETWORK_BENCHMARK "Run controlled HTTP download/playback matrix" OFF)
option(YORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY "Repeat three unpaced receive-only runs" OFF)
option(YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY "Measure connected baseline and receive-only task runtime" OFF)
set(YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP "0" CACHE STRING "0=single, 1=wait A/B, 2=read sizes, 3=bounded batching, 4=playback wait, 5=playback read-size")
set(YORADIO_ESP8266_NETWORK_BENCHMARK_ROUNDS "10" CACHE STRING "Repeated attempts per fixture and variant")
if(NOT YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP MATCHES "^[0-5]$" OR
   NOT YORADIO_ESP8266_NETWORK_BENCHMARK_ROUNDS MATCHES "^[1-9][0-9]*$")
  message(FATAL_ERROR "Invalid network sweep/round count")
endif()
if(NOT YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP STREQUAL "0" AND
   (NOT YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY OR YORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY))
  message(FATAL_ERROR "Network sweeps require CPU_ONLY and no BULK_ONLY")
endif()
if(YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY AND
   (NOT YORADIO_ESP8266_NETWORK_BENCHMARK OR NOT CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS OR
    NOT CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER))
  message(FATAL_ERROR "Network CPU measurement requires network benchmark and ESP_TIMER runtime stats")
endif()
set(YORADIO_ESP8266_NETWORK_BENCHMARK_URL "" CACHE STRING "Local HTTP fixture server base URL")
if(YORADIO_ESP8266_NETWORK_BENCHMARK AND
   (YORADIO_ESP8266_CODEC_RAM_BENCHMARK OR YORADIO_ESP8266_AUDIO_PROFILE OR
    YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK OR YORADIO_ESP8266_KARADIO_PIPELINE OR
    NOT CONFIG_YORADIO_HELIX_AAC OR NOT YORADIO_ESP8266_NETWORK_BENCHMARK_URL MATCHES "^http://"))
  message(FATAL_ERROR "Network benchmark requires native HTTP URL, AAC, and other benchmarks OFF")
endif()
set(YORADIO_EMBED_FILES "../../../yoRadio/data/www/script.js.gz")
if(YORADIO_ESP8266_CODEC_RAM_BENCHMARK)
  list(APPEND YORADIO_SOURCES "codec_ram_benchmark.cpp")
  if(YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX)
    list(APPEND YORADIO_EMBED_FILES
      "../../../tests/fixtures/mp3_composite/mix-064.mp3"
      "../../../tests/fixtures/mp3_composite/mix-128.mp3"
      "../../../tests/fixtures/mp3_composite/mix-320.mp3")
  elseif(YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX)
    list(APPEND YORADIO_EMBED_FILES
      "../../../tests/fixtures/aac_composite/mix-048.aac"
      "../../../tests/fixtures/aac_composite/mix-064.aac"
      "../../../tests/fixtures/aac_composite/mix-096.aac")
  else()
    list(APPEND YORADIO_EMBED_FILES
      "../../../tests/fixtures/helix_golden/stereo-320.mp3"
      "../../../tests/fixtures/helix_golden/stereo-320.aac")
  endif()
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
  LDFRAGMENTS ${YORADIO_AUDIO_LDFRAGMENTS}
  EMBED_FILES ${YORADIO_EMBED_FILES})

set(WEB_BUNDLE_HEADER "${CMAKE_CURRENT_BINARY_DIR}/web_bundle_generated.h")
set(WEB_BUNDLE_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../..")
file(GLOB WEB_BUNDLE_INPUTS "${WEB_BUNDLE_ROOT}/yoRadio/data/www/*.gz")
add_custom_command(OUTPUT "${WEB_BUNDLE_HEADER}"
  COMMAND ${PYTHON} "${WEB_BUNDLE_ROOT}/tools/build_esp8266_web_bundle.py"
          --root "${WEB_BUNDLE_ROOT}" --output "${WEB_BUNDLE_HEADER}"
  DEPENDS "${WEB_BUNDLE_ROOT}/tools/build_esp8266_web_bundle.py"
          "${WEB_BUNDLE_ROOT}/yoRadio/src/core/netserver.h" ${WEB_BUNDLE_INPUTS}
  VERBATIM)
add_custom_target(yoradio_web_bundle DEPENDS "${WEB_BUNDLE_HEADER}")
add_dependencies(${COMPONENT_LIB} yoradio_web_bundle)
target_include_directories(${COMPONENT_LIB} PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
if(YORADIO_ESP8266_OPUS_BENCHMARK)
  target_include_directories(${COMPONENT_LIB} PRIVATE "${YORADIO_ESP8266_OPUS_BENCHMARK_FIXTURES}")
endif()

# ESP8266_RTOS_SDK exposes only -Og/-Os in menuconfig. Audio code needs the
# same explicit performance profile used by the ESP32-C3 native build.
target_compile_options(${COMPONENT_LIB} PRIVATE -O3
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++14>)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1
  YORADIO_ESP8266_SDK_RX_DIAG=$<BOOL:${YORADIO_ESP8266_SDK_RX_DIAG}>
  YORADIO_ESP8266_PDM32_IRAM=$<BOOL:${YORADIO_ESP8266_PDM32_IRAM}>
  YORADIO_ESP8266_PDM32_BATCH=$<BOOL:${YORADIO_ESP8266_PDM32_BATCH}>
  YORADIO_ESP8266_PDM32_LOAN_WORDS=${YORADIO_ESP8266_PDM32_LOAN_WORDS}
  YORADIO_ESP8266_OPUS_STREAM_TEST=$<BOOL:${YORADIO_ESP8266_OPUS_STREAM_TEST}>
  YORADIO_ESP8266_OPUS_BENCHMARK=$<BOOL:${YORADIO_ESP8266_OPUS_BENCHMARK}>
  YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT=$<BOOL:${YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT}>
  YORADIO_ESP8266_WEB_AUDIO_PAUSE=${WEB_AUDIO_PAUSE_MODE}
  YORADIO_ESP8266_WEB_PROFILE=$<BOOL:${YORADIO_ESP8266_WEB_PROFILE}>
  YORADIO_ESP8266_SPIFFS_LOG=$<BOOL:${YORADIO_ESP8266_SPIFFS_LOG}>
  YORADIO_ESP8266_SPIFFS_LOG_HTTP=$<BOOL:${YORADIO_ESP8266_SPIFFS_LOG_HTTP}>
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
if(YORADIO_ESP8266_NETWORK_BENCHMARK)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_NETWORK_BENCHMARK=1
    YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY=$<BOOL:${YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY}>
    YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP=${YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP}
    YORADIO_ESP8266_NETWORK_BENCHMARK_ROUNDS=${YORADIO_ESP8266_NETWORK_BENCHMARK_ROUNDS}
    YORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY=$<BOOL:${YORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY}>
    YORADIO_ESP8266_NETWORK_BENCHMARK_URL=\"${YORADIO_ESP8266_NETWORK_BENCHMARK_URL}\")
endif()
if(YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX=1)
endif()
if(YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX=1)
endif()
if(YORADIO_ESP8266_CODEC_RAM_BENCHMARK)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_CODEC_RAM_BENCHMARK=1
    YORADIO_ESP8266_CODEC_RAM_FRAMES=${YORADIO_ESP8266_CODEC_RAM_FRAMES})
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
