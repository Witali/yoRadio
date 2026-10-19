cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED ENV{YORADIO_AUDIO_CODEC_COMPONENT})
  message(FATAL_ERROR
    "YORADIO_AUDIO_CODEC_COMPONENT is not set; use build.ps1")
endif()

set(EXTRA_COMPONENT_DIRS
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_storage"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_stream"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_web_transport"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_ota"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_time"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_wifi_store"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_network_power"
  "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}"
  "${CMAKE_CURRENT_LIST_DIR}/../components/audio_level_led"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_audio_normalizer"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_audio_settings"
  "${CMAKE_CURRENT_LIST_DIR}/../components/custom_codec_support"
  "${CMAKE_CURRENT_LIST_DIR}/../components/custom_flac"
  "${CMAKE_CURRENT_LIST_DIR}/../components/custom_legacy_codecs")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(yoradio_cyd2usb_native)
