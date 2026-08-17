cmake_minimum_required(VERSION 3.16)

foreach(required_env
    YORADIO_ARDUINO_COMPONENT
    YORADIO_ARDUINO_LIBRARIES)
  if(NOT DEFINED ENV{${required_env}})
    message(FATAL_ERROR "${required_env} is not set; use build.ps1")
  endif()
endforeach()

set(YORADIO_DAC_BACKEND "continuous" CACHE STRING
    "Built-in DAC backend: continuous or legacy")
set_property(CACHE YORADIO_DAC_BACKEND PROPERTY STRINGS continuous legacy)
if(NOT YORADIO_DAC_BACKEND STREQUAL "continuous" AND
   NOT YORADIO_DAC_BACKEND STREQUAL "legacy")
  message(FATAL_ERROR
    "YORADIO_DAC_BACKEND must be 'continuous' or 'legacy'")
endif()

# Use the locally installed Arduino core as an ESP-IDF component.  The
# component manager is deliberately disabled: this profile must not pull in
# Arduino's optional Matter, Zigbee, RainMaker and speech dependencies.
set(EXTRA_COMPONENT_DIRS
    "$ENV{YORADIO_ARDUINO_COMPONENT}")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(yoradio_cyd2usb_minimal)

# Arduino 4.0 alpha emits a deliberate #warning when optional TLS-PSK suites
# are disabled.  PSK is not used by Internet radio streams, so keep it out of
# the image and prevent only this warning class from becoming a build error.
idf_component_get_property(arduino_lib arduino COMPONENT_LIB)
target_compile_options(${arduino_lib} PRIVATE -Wno-error=cpp)
