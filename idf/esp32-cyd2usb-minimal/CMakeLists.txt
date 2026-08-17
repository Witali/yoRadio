cmake_minimum_required(VERSION 3.16)

foreach(required_env
    YORADIO_ARDUINO_COMPONENT
    YORADIO_ARDUINO_LIBRARIES)
  if(NOT DEFINED ENV{${required_env}})
    message(FATAL_ERROR "${required_env} is not set; use build.ps1")
  endif()
endforeach()

set(YORADIO_DAC_BACKEND "continuous" CACHE STRING
    "Internal audio backend: continuous, legacy, or pdm")
set_property(CACHE YORADIO_DAC_BACKEND PROPERTY STRINGS continuous legacy pdm)
if(NOT YORADIO_DAC_BACKEND STREQUAL "continuous" AND
   NOT YORADIO_DAC_BACKEND STREQUAL "legacy" AND
   NOT YORADIO_DAC_BACKEND STREQUAL "pdm")
  message(FATAL_ERROR
    "YORADIO_DAC_BACKEND must be 'continuous', 'legacy', or 'pdm'")
endif()

# Use the locally installed Arduino core as an ESP-IDF component.  The
# component manager is deliberately disabled: this profile must not pull in
# Arduino's optional Matter, Zigbee, RainMaker and speech dependencies.
set(EXTRA_COMPONENT_DIRS
    "$ENV{YORADIO_ARDUINO_COMPONENT}")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(yoradio_cyd2usb_minimal)

# ESP-IDF 6.0.2 calculates the PCM-to-PDM BCLK after truncating fp/fs to an
# integer.  Espressif's fixed-carrier DAC profile uses fp=960 and
# fs=sample_rate/100, so the truncation turns the documented 6.144 MHz clock
# into 5.6448 MHz for 44.1 kHz PCM.  Generate a build-local corrected source
# instead of modifying the pinned SDK checkout.  The exact-source check makes
# a future IDF update fail visibly if this workaround is no longer applicable.
if(YORADIO_DAC_BACKEND STREQUAL "pdm")
  set(i2s_pdm_source
    "$ENV{IDF_PATH}/components/esp_driver_i2s/i2s_pdm.c")
  file(READ "${i2s_pdm_source}" i2s_pdm_contents)
  set(pdm_bclk_original
    "clk_info->bclk = rate * I2S_LL_PDM_BCK_FACTOR * over_sample_ratio;")
  set(pdm_bclk_corrected
    "clk_info->bclk = (uint32_t)(((uint64_t)rate * I2S_LL_PDM_BCK_FACTOR * pdm_tx_clk->up_sample_fp) /\n                            pdm_tx_clk->up_sample_fs);")
  string(FIND "${i2s_pdm_contents}" "${pdm_bclk_original}"
    pdm_bclk_location)
  if(pdm_bclk_location EQUAL -1)
    message(FATAL_ERROR
      "ESP-IDF PDM clock expression changed; review the local clock fix")
  endif()
  string(REPLACE "${pdm_bclk_original}" "${pdm_bclk_corrected}"
    i2s_pdm_contents "${i2s_pdm_contents}")

  set(patched_i2s_dir "${CMAKE_CURRENT_BINARY_DIR}/yoradio-idf-fixes")
  file(MAKE_DIRECTORY "${patched_i2s_dir}")
  set(patched_i2s_pdm "${patched_i2s_dir}/i2s_pdm.c")
  file(WRITE "${patched_i2s_pdm}" "${i2s_pdm_contents}")

  idf_component_get_property(i2s_driver_lib esp_driver_i2s COMPONENT_LIB)
  get_target_property(i2s_driver_sources ${i2s_driver_lib} SOURCES)
  list(LENGTH i2s_driver_sources i2s_sources_before)
  list(FILTER i2s_driver_sources EXCLUDE REGEX "(^|[/\\\\])i2s_pdm\\.c$")
  list(LENGTH i2s_driver_sources i2s_sources_after)
  math(EXPR removed_i2s_sources
    "${i2s_sources_before} - ${i2s_sources_after}")
  if(NOT removed_i2s_sources EQUAL 1)
    message(FATAL_ERROR
      "Expected one ESP-IDF i2s_pdm.c source, removed ${removed_i2s_sources}")
  endif()
  set_property(TARGET ${i2s_driver_lib} PROPERTY SOURCES
    "${i2s_driver_sources}")
  target_sources(${i2s_driver_lib} PRIVATE "${patched_i2s_pdm}")
  target_include_directories(${i2s_driver_lib} PRIVATE
    "$ENV{IDF_PATH}/components/esp_driver_i2s")
endif()

# Arduino 4.0 alpha emits a deliberate #warning when optional TLS-PSK suites
# are disabled.  PSK is not used by Internet radio streams, so keep it out of
# the image and prevent only this warning class from becoming a build error.
idf_component_get_property(arduino_lib arduino COMPONENT_LIB)
target_compile_options(${arduino_lib} PRIVATE -Wno-error=cpp)
