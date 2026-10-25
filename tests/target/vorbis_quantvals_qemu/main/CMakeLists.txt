set(candidate "$ENV{VORBIS_QUANTVALS_CANDIDATE}")
set(codec "$ENV{VORBIS_QUANTVALS_HEADERS}")
idf_component_register(SRCS "main.c"
    INCLUDE_DIRS "." "${codec}/include" "${codec}/include/decoder"
                 "${codec}/include/decoder/impl"
    REQUIRES freertos esp_system)
if(CMAKE_BUILD_EARLY_EXPANSION)
    return()
endif()
if(IDF_TARGET STREQUAL "esp32" AND CONFIG_IDF_TARGET_ESP32)
    set(expected_sdk "6.0.2")
elseif(IDF_TARGET STREQUAL "esp32c3" AND CONFIG_IDF_TARGET_ESP32C3)
    set(expected_sdk "6.1.0")
else()
    message(FATAL_ERROR "Only the isolated ESP32/C3 quantvals fixture is supported")
endif()
if(NOT "${IDF_VERSION_MAJOR}.${IDF_VERSION_MINOR}.${IDF_VERSION_PATCH}" STREQUAL expected_sdk)
    message(FATAL_ERROR "Wrong pinned SDK version")
endif()
foreach(part setup abi)
    if(part STREQUAL "setup")
        set(source "${candidate}/vorbis_repair/setup.c")
    else()
        set(source "${candidate}/vorbis_repair_abi.h")
    endif()
    file(SHA256 "${source}" actual)
    if(NOT actual STREQUAL "${QUANTVALS_${part}_SHA256}")
        message(FATAL_ERROR "Frozen canonical ${part} hash mismatch")
    endif()
endforeach()
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    QUANTVALS_SETUP_FILE="${candidate}/vorbis_repair/setup.c"
    QUANTVALS_CASES_SHA256="${QUANTVALS_CASES_SHA256}")
# The whole canonical setup TU is included by main.c. Unused parser/decoder
# functions are removed by the SDK's section GC. No codec archive is linked.
