set(YORADIO_AUDIO_DIR
    "${CMAKE_CURRENT_LIST_DIR}/../../../../yoRadio/src/audioI2S")

set(YORADIO_HELIX_SOURCES
    "codec_bridge.cpp"
    "CodecMemoryArena.cpp")
set(YORADIO_CODEC_INCLUDES
    "."
    "${YORADIO_AUDIO_DIR}"
    "${YORADIO_AUDIO_DIR}/mp3_decoder"
    "${YORADIO_AUDIO_DIR}/aac_decoder")
if(CONFIG_YORADIO_MP3_DECODER_LIBMAD)
  set(YORADIO_LIBMAD_DIR "../libmad8266/upstream/libmad")
  list(APPEND YORADIO_HELIX_SOURCES
      "${YORADIO_LIBMAD_DIR}/bit.c"
      "${YORADIO_LIBMAD_DIR}/fixed.c"
      "${YORADIO_LIBMAD_DIR}/frame.c"
      "${YORADIO_LIBMAD_DIR}/huffman.c"
      "${YORADIO_LIBMAD_DIR}/layer3.c"
      "${YORADIO_LIBMAD_DIR}/stream.c"
      "${YORADIO_LIBMAD_DIR}/synth.c"
      "${YORADIO_LIBMAD_DIR}/timer.c"
      "${YORADIO_LIBMAD_DIR}/version.c")
  list(APPEND YORADIO_CODEC_INCLUDES
      "../libmad8266"
      "${YORADIO_LIBMAD_DIR}")
else()
  list(APPEND YORADIO_HELIX_SOURCES
      "${YORADIO_AUDIO_DIR}/mp3_decoder/mp3_decoder.cpp")
endif()
if(CONFIG_YORADIO_HELIX_AAC)
  list(APPEND YORADIO_HELIX_SOURCES
      "${YORADIO_AUDIO_DIR}/aac_decoder/aac_decoder.cpp")
endif()

# Dependencies are scanned before Kconfig values are available. The Opus
# component itself has no sources when its experimental option is disabled.
set(YORADIO_CODEC_REQUIRES esp8266 log opus_decoder)
if(YORADIO_ESP8266_OPUS_STREAM_TEST OR YORADIO_ESP8266_OPUS_BENCHMARK)
  list(APPEND YORADIO_HELIX_SOURCES "native_heap_diag.c")
endif()
idf_component_register(
  SRCS ${YORADIO_HELIX_SOURCES}
  INCLUDE_DIRS ${YORADIO_CODEC_INCLUDES}
  REQUIRES ${YORADIO_CODEC_REQUIRES})

target_compile_options(${COMPONENT_LIB} PRIVATE -O3
  $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
  $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1)
if(YORADIO_ESP8266_OPUS_STREAM_TEST OR YORADIO_ESP8266_OPUS_BENCHMARK)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_OPUS_STREAM_TEST=1)
endif()
if(YORADIO_ESP8266_OPUS_PCM_QUEUE)
  set(YORADIO_ESP8266_OPUS_PCM_SLOTS "2" CACHE STRING "Decoder-owned PCM slots (2 or 3)")
  if(NOT YORADIO_ESP8266_OPUS_PCM_SLOTS MATCHES "^(2|3)$")
    message(FATAL_ERROR "Opus PCM slots must be 2 or 3")
  endif()
  if(NOT YORADIO_OPUS_PCM_LEASES OR NOT YORADIO_ESP8266_DIAGNOSTIC OR NOT CONFIG_YORADIO_OGG_OPUS)
    message(FATAL_ERROR "PCM queue bridge requires diagnostic Opus leases")
  endif()
  target_compile_definitions(${COMPONENT_LIB} PUBLIC YORADIO_ESP8266_OPUS_PCM_QUEUE=1
    YORADIO_ESP8266_OPUS_PCM_SLOTS=${YORADIO_ESP8266_OPUS_PCM_SLOTS})
endif()
option(YORADIO_ESP8266_MP3_SHARED_REORDER
  "Reuse IMDCT output as MP3 reorder scratch (OFF for A/B comparison)" ON)
option(YORADIO_ESP8266_AAC_BLOCK_OUTPUT "Stream AAC PCM in bounded blocks" ON)
# 512 mono PCM samples fill one 512-word PDM32 DMA payload. Smaller blocks
# allowed premature partial handoff and underruns in physical AAC tests.
set(YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES "512" CACHE STRING "AAC frames per PCM block (32/64/128/256/512)")
if(NOT YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES MATCHES "^(32|64|128|256|512)$")
  message(FATAL_ERROR "AAC PCM block must be 32, 64, 128, 256 or 512 frames")
endif()
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_AAC_BLOCK_OUTPUT=$<BOOL:${YORADIO_ESP8266_AAC_BLOCK_OUTPUT}>
  YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES=${YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES})
if(YORADIO_ESP8266_MP3_SHARED_REORDER)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_HELIX_MP3_SHARED_REORDER=1)
else()
  target_compile_definitions(${COMPONENT_LIB} PRIVATE YORADIO_HELIX_MP3_SHARED_REORDER=0)
endif()
if(CONFIG_YORADIO_AUDIO_MONO)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_HELIX_MP3_MONO=1)
endif()
if(CONFIG_YORADIO_HELIX_MP3_SSO)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_HELIX_MP3_SSO=1)
endif()
if(CONFIG_YORADIO_HELIX_AAC_SSO)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_HELIX_AAC_SSO=1)
endif()
if(CONFIG_YORADIO_MP3_DECODER_LIBMAD)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_LIBMAD_EXTERNAL_FRAME_WORKSPACE=1)
endif()
option(YORADIO_ESP8266_HELIX_STAGE_PROFILE
  "Measure Helix stages with the ESP microsecond timer" OFF)
if(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_HELIX_STAGE_PROFILE=1)
endif()
option(YORADIO_ESP8266_HELIX_RECIPROCAL_DIVIDE
  "Replace safe MP3 constant divisions with exact Q32 reciprocal multiplies" ON)
if(YORADIO_ESP8266_HELIX_RECIPROCAL_DIVIDE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_HELIX_RECIPROCAL_DIVIDE=1)
endif()
if(YORADIO_ESP8266_AUDIO_PROFILE)
  target_compile_definitions(${COMPONENT_LIB} PRIVATE
    YORADIO_ESP8266_AUDIO_PROFILE=1)
endif()
