cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED ENV{YORADIO_AUDIO_CODEC_COMPONENT})
  message(FATAL_ERROR
    "YORADIO_AUDIO_CODEC_COMPONENT is not set; use build.ps1")
endif()

set(EXTRA_COMPONENT_DIRS "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(yoradio_esp32c3_oled_native)
