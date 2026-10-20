set(M "$ENV{CYD_VORBIS_CANDIDATE}")
idf_component_register(SRCS "main.c" INCLUDE_DIRS "." "${M}"
 REQUIRES esp_audio_codec freertos heap esp_system esp_rom)
include("${M}/compat/vorbis_repair/enable.cmake")
native_enable_vorbis_repair()
