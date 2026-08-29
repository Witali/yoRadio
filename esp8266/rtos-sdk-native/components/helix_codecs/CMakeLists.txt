set(YORADIO_AUDIO_DIR
    "${CMAKE_CURRENT_LIST_DIR}/../../../../yoRadio/src/audioI2S")

idf_component_register(
  SRCS
    "codec_bridge.cpp"
    "CodecMemoryArena.cpp"
    "${YORADIO_AUDIO_DIR}/mp3_decoder/mp3_decoder.cpp"
    "${YORADIO_AUDIO_DIR}/aac_decoder/aac_decoder.cpp"
  INCLUDE_DIRS
    "."
    "${YORADIO_AUDIO_DIR}"
    "${YORADIO_AUDIO_DIR}/mp3_decoder"
    "${YORADIO_AUDIO_DIR}/aac_decoder"
  REQUIRES esp8266 log)

target_compile_options(${COMPONENT_LIB} PRIVATE -O3 -fno-exceptions -fno-rtti)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1)
