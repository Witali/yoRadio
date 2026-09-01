set(YORADIO_AUDIO_DIR
    "${CMAKE_CURRENT_LIST_DIR}/../../../../yoRadio/src/audioI2S")

set(YORADIO_HELIX_SOURCES
    "codec_bridge.cpp"
    "CodecMemoryArena.cpp"
    "${YORADIO_AUDIO_DIR}/mp3_decoder/mp3_decoder.cpp")
if(CONFIG_YORADIO_HELIX_AAC)
  list(APPEND YORADIO_HELIX_SOURCES
      "${YORADIO_AUDIO_DIR}/aac_decoder/aac_decoder.cpp")
endif()

idf_component_register(
  SRCS ${YORADIO_HELIX_SOURCES}
  INCLUDE_DIRS
    "."
    "${YORADIO_AUDIO_DIR}"
    "${YORADIO_AUDIO_DIR}/mp3_decoder"
    "${YORADIO_AUDIO_DIR}/aac_decoder"
  REQUIRES esp8266 log)

target_compile_options(${COMPONENT_LIB} PRIVATE -O3 -fno-exceptions -fno-rtti)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1)
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
