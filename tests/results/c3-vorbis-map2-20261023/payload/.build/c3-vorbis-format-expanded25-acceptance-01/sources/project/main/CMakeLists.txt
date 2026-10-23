idf_component_register(SRCS "main.c" INCLUDE_DIRS "."
 REQUIRES esp_audio_codec freertos heap esp_system esp_rom)
include("${CMAKE_CURRENT_LIST_DIR}/../raw-enable.cmake")
native_enable_vorbis_repair()
