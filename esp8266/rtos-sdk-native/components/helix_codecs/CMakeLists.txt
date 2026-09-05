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

idf_component_register(
  SRCS ${YORADIO_HELIX_SOURCES}
  INCLUDE_DIRS ${YORADIO_CODEC_INCLUDES}
  REQUIRES esp8266 log)

target_compile_options(${COMPONENT_LIB} PRIVATE -O3
  $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
  $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1)
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
