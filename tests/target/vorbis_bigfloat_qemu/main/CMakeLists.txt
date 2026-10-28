idf_component_register(SRCS "main.c" INCLUDE_DIRS "."
    REQUIRES freertos esp_system heap native_vorbis_bigfloat)
if(CMAKE_BUILD_EARLY_EXPANSION)
    return()
endif()
if(IDF_TARGET STREQUAL "esp32" AND CONFIG_IDF_TARGET_ESP32)
    set(expected_sdk "6.0.2")
elseif(IDF_TARGET STREQUAL "esp32c3" AND CONFIG_IDF_TARGET_ESP32C3)
    set(expected_sdk "6.1.0")
else()
    message(FATAL_ERROR "Only isolated ESP32/C3 arithmetic qualification")
endif()
if(NOT "${IDF_VERSION_MAJOR}.${IDF_VERSION_MINOR}.${IDF_VERSION_PATCH}" STREQUAL expected_sdk)
    message(FATAL_ERROR "Wrong pinned SDK version")
endif()
file(SHA256 "${CMAKE_CURRENT_LIST_DIR}/corpus.h" actual_header)
file(SHA256 "${CMAKE_CURRENT_LIST_DIR}/vorbis_bigfloat_host.c" actual_fixture)
if(NOT actual_header STREQUAL BFQ_CORPUS_HEADER_SHA256 OR NOT actual_fixture STREQUAL BFQ_FIXTURE_SHA256)
    message(FATAL_ERROR "Frozen corpus/fixture byte mismatch")
endif()
target_compile_options(${COMPONENT_LIB} PRIVATE -UNDEBUG -fno-fast-math -ffp-contract=off -fstack-usage)
idf_component_get_property(arithmetic native_vorbis_bigfloat COMPONENT_LIB)
target_compile_options(${arithmetic} PRIVATE -UNDEBUG -fno-fast-math -ffp-contract=off -fstack-usage)

# Isolated diagnostic policy: retain the creator warnings seen in source-only
# profiles even where SDK defaults suppress them. Only known creator categories
# become nonfatal; adapter and fixture retain the SDK's -Werror policy.
idf_component_get_property(arithmetic_directory native_vorbis_bigfloat COMPONENT_DIR)
foreach(creator "portable/libbf.c" "upstream/cutils.c")
    set_property(SOURCE "${arithmetic_directory}/${creator}" TARGET_DIRECTORY ${arithmetic}
        APPEND PROPERTY COMPILE_OPTIONS -Wsign-compare -Wunused-parameter
        -Wno-error=sign-compare -Wno-error=unused-parameter)
endforeach()
set_property(SOURCE "${arithmetic_directory}/portable/libbf.c" TARGET_DIRECTORY ${arithmetic}
    APPEND PROPERTY COMPILE_OPTIONS -Wno-error=format)
