# Select compile-time SDK logging before ESP-IDF reads sdkconfig. Reapply only
# these managed choices so changing DEBUG in an existing build works both ways.
option(DEBUG "Compile Small TV and ESP-IDF diagnostic logging" OFF)
if(NOT DEFINED SDKCONFIG)
    set(SDKCONFIG "${CMAKE_BINARY_DIR}/sdkconfig" CACHE FILEPATH "SDK configuration")
endif()
get_filename_component(SDKCONFIG "${SDKCONFIG}" ABSOLUTE BASE_DIR "${CMAKE_SOURCE_DIR}")
if(DEBUG)
    set(_small_tv_level DEBUG)
else()
    set(_small_tv_level WARN)
endif()
if(EXISTS "${SDKCONFIG}")
    file(READ "${SDKCONFIG}" _small_tv_previous)
    string(REPLACE "\r\n" "\n" _small_tv_previous "${_small_tv_previous}")
    if(_small_tv_previous MATCHES "(^|\n)CONFIG_LOG_DEFAULT_LEVEL_${_small_tv_level}=y(\n|$)" AND
       _small_tv_previous MATCHES "(^|\n)CONFIG_LOG_MAXIMUM_EQUALS_DEFAULT=y(\n|$)" AND
       _small_tv_previous MATCHES "(^|\n)CONFIG_BOOTLOADER_LOG_LEVEL_${_small_tv_level}=y(\n|$)")
        message(STATUS "Small TV DEBUG=${DEBUG}: log level ${_small_tv_level} already selected")
        return()
    endif()
endif()
set(_small_tv_config "")
if(EXISTS "${SDKCONFIG}")
    file(STRINGS "${SDKCONFIG}" _small_tv_lines)
    foreach(_small_tv_line IN LISTS _small_tv_lines)
        if(NOT _small_tv_line MATCHES "^(# )?CONFIG_(LOG_(DEFAULT_LEVEL|MAXIMUM_LEVEL|MAXIMUM_EQUALS_DEFAULT|BOOTLOADER_LEVEL)|BOOTLOADER_LOG_LEVEL)([=_ ]|$)")
            string(APPEND _small_tv_config "${_small_tv_line}\n")
        endif()
    endforeach()
endif()
string(APPEND _small_tv_config
    "CONFIG_LOG_DEFAULT_LEVEL_${_small_tv_level}=y\n"
    "CONFIG_LOG_MAXIMUM_EQUALS_DEFAULT=y\n"
    "CONFIG_BOOTLOADER_LOG_LEVEL_${_small_tv_level}=y\n")
file(WRITE "${SDKCONFIG}" "${_small_tv_config}")
message(STATUS "Small TV DEBUG=${DEBUG}: application/SDK/bootloader log level ${_small_tv_level}")
