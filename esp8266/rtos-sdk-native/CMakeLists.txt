cmake_minimum_required(VERSION 3.5)

# Keep the mutable Kconfig output local to each build directory. Otherwise
# ESP8266_RTOS_SDK defaults to a source-tree sdkconfig, so an ignored file left
# by a libmad experiment can silently override the tracked production defaults.
if(NOT DEFINED SDKCONFIG)
  set(SDKCONFIG "${CMAKE_BINARY_DIR}/sdkconfig" CACHE FILEPATH
      "Per-build ESP8266 Kconfig output")
endif()
if(NOT EXISTS "${SDKCONFIG}")
  file(WRITE "${SDKCONFIG}" "")
endif()

set(EXTRA_COMPONENT_DIRS "${CMAKE_CURRENT_LIST_DIR}/components")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(yoradio_esp8266_helix_native)

# Instrument the configured SDK through its supported hook, not by modifying
# the downloaded SDK. Nothing is injected into ordinary non-profiled builds.
if(YORADIO_ESP8266_WEB_PROFILE)
  idf_component_get_property(web_trace_lwip lwip COMPONENT_LIB)
  target_compile_definitions(${web_trace_lwip} PRIVATE
    LWIP_HOOK_FILENAME="${CMAKE_CURRENT_LIST_DIR}/components/esp_http_server/include/web_trace_lwip_hook.h")
endif()
