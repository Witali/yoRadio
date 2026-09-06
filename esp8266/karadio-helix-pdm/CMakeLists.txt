cmake_minimum_required(VERSION 3.5)

if(NOT DEFINED SDKCONFIG)
  set(SDKCONFIG "${CMAKE_BINARY_DIR}/sdkconfig" CACHE FILEPATH
      "Per-build ESP8266 Kconfig output")
endif()
if(NOT EXISTS "${SDKCONFIG}")
  file(WRITE "${SDKCONFIG}" "")
endif()

set(EXTRA_COMPONENT_DIRS
    "${CMAKE_CURRENT_LIST_DIR}/../rtos-sdk-native/components")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(karadio_helix_pdm_esp8266)
