set(YORADIO_AUDIO_DIR
    "${CMAKE_CURRENT_LIST_DIR}/../../../../yoRadio/src/audioI2S")

idf_component_register(
  SRCS "${YORADIO_AUDIO_DIR}/CodecMemoryArena.cpp"
  INCLUDE_DIRS "." "${YORADIO_AUDIO_DIR}"
  REQUIRES heap log)

target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
