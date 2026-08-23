idf_component_register(
  SRCS "native_audio_settings.c"
  INCLUDE_DIRS "."
  REQUIRES esp_common esp_timer nvs_flash)

target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
