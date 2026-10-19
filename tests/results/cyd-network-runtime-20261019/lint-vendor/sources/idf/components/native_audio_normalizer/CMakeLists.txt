get_filename_component(YORADIO_AUDIO_ROOT
  "${CMAKE_CURRENT_LIST_DIR}/../../../yoRadio/src/audioI2S" ABSOLUTE)

idf_component_register(
  SRCS "native_audio_normalizer.cpp"
       "${YORADIO_AUDIO_ROOT}/AudioNormalizer.cpp"
  INCLUDE_DIRS "."
  PRIV_INCLUDE_DIRS "${YORADIO_AUDIO_ROOT}")
