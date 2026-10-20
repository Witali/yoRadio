set(M "$ENV{CYD_VORBIS_CANDIDATE}")
idf_component_register(SRCS "main.c" INCLUDE_DIRS "."
 REQUIRES esp_audio_codec freertos heap esp_system esp_rom)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
 BLOCK_MATRIX_PROFILE_CYD=1 BLOCK_MATRIX_MINIMAL_RATE_REBIND_VERIFIED=1)
include("${M}/compat/vorbis_repair/enable.cmake")
native_enable_vorbis_repair()
