set(M "$ENV{CYD_VORBIS_CANDIDATE}")
idf_component_register(SRCS "main.c" INCLUDE_DIRS "."
 REQUIRES esp_audio_codec freertos heap esp_system esp_rom)
if(NOT DEFINED FORMAT_EXPECT_LOW_RATE_REJECTION OR
   NOT "${FORMAT_EXPECT_LOW_RATE_REJECTION}" MATCHES "^[01]$")
 message(FATAL_ERROR "Explicitly select FORMAT_EXPECT_LOW_RATE_REJECTION=1 (baseline) or 0 (acceptance)")
endif()
target_compile_definitions(${COMPONENT_LIB} PRIVATE
 FORMAT_EXPECT_LOW_RATE_REJECTION=${FORMAT_EXPECT_LOW_RATE_REJECTION})
include("${M}/compat/vorbis_repair/enable.cmake")
native_enable_vorbis_repair()
