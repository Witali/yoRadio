idf_component_register(SRCS "main.cpp" INCLUDE_DIRS "."
  REQUIRES custom_flac custom_codec_support esp_partition esp_system esp_hw_support heap freertos esp_timer)
target_compile_definitions(${COMPONENT_LIB} PRIVATE FLAC_OUTPUT_FRAMES=512 FLAC_SEGMENTED_WORKSPACE=1)
