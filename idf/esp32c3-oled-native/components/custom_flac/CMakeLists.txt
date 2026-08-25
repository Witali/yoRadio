set(YORADIO_FLAC_DIR
    "${CMAKE_CURRENT_LIST_DIR}/../../../../yoRadio/src/audioI2S/flac_decoder")

idf_component_register(
  SRCS
    "custom_flac_adapter.cpp"
    "${YORADIO_FLAC_DIR}/flac_decoder.cpp"
  INCLUDE_DIRS
    "."
    "${YORADIO_FLAC_DIR}"
  REQUIRES
    custom_codec_support
    esp_timer
    heap
    log)

target_compile_definitions(${COMPONENT_LIB} PRIVATE
  FLAC_OUTPUT_FRAMES=512
  FLAC_SEGMENTED_WORKSPACE=1)
target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
