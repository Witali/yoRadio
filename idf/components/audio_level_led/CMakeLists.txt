idf_component_register(
  SRCS "audio_level_led.c"
  INCLUDE_DIRS "."
  REQUIRES esp_common esp_driver_gpio esp_driver_ledc esp_timer)

target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
