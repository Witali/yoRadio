set(YORADIO_AUDIO_DIR
    "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio/src/audioI2S")

set(CUSTOM_CODEC_SRCS "custom_legacy_adapter.cpp")
if(CONFIG_YORADIO_AAC_DECODER_HELIX)
  list(APPEND CUSTOM_CODEC_SRCS
       "${YORADIO_AUDIO_DIR}/aac_decoder/aac_decoder.cpp")
endif()
if(CONFIG_YORADIO_MP3_DECODER_HELIX)
  list(APPEND CUSTOM_CODEC_SRCS
       "${YORADIO_AUDIO_DIR}/mp3_decoder/mp3_decoder.cpp")
endif()

idf_component_register(
  SRCS ${CUSTOM_CODEC_SRCS}
  INCLUDE_DIRS
    "."
    "${YORADIO_AUDIO_DIR}"
    "${YORADIO_AUDIO_DIR}/aac_decoder"
    "${YORADIO_AUDIO_DIR}/mp3_decoder"
    "${YORADIO_AUDIO_DIR}/minimp3"
  REQUIRES custom_codec_support esp_timer log)

target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
