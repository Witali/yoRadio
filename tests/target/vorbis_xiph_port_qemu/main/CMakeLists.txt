idf_component_register(SRCS "main.c" "vorbis_xiph_alloc.c"
                           "vorbis_xiph_arena.c" "vorbis_xiph_books.c" "vorbis_xiph_bits.c"
                      INCLUDE_DIRS "."
                      REQUIRES freertos esp_system heap native_vorbis_xiph_port)
if(CMAKE_BUILD_EARLY_EXPANSION)
    return()
endif()
if(NOT IDF_TARGET STREQUAL "esp32" OR NOT CONFIG_IDF_TARGET_ESP32)
    message(FATAL_ERROR "The resource-port baseline is ESP32 only")
endif()
if(NOT "${IDF_VERSION_MAJOR}.${IDF_VERSION_MINOR}.${IDF_VERSION_PATCH}" STREQUAL "6.0.2")
    message(FATAL_ERROR "Wrong pinned SDK version")
endif()
file(SHA256 "$ENV{XIPH_COMPONENT}/../native_vorbis_xiph/component-manifest.json" base_sha256)
file(SHA256 "$ENV{XIPH_COMPONENT}/port-manifest.json" port_sha256)
if(NOT base_sha256 STREQUAL XIPH_BASE_MANIFEST_SHA256 OR
   NOT port_sha256 STREQUAL XIPH_PORT_MANIFEST_SHA256)
    message(FATAL_ERROR "Frozen base/port manifest mismatch")
endif()
idf_component_get_property(xiph_library native_vorbis_xiph_port COMPONENT_LIB)
get_target_property(xiph_binary_dir ${xiph_library} BINARY_DIR)
set(xiph_generated "${xiph_binary_dir}/xiph-source")
if(NOT EXISTS "${xiph_generated}/PORTING.json")
    message(FATAL_ERROR "The declared exact source materialization did not complete")
endif()
target_include_directories(${COMPONENT_LIB} PRIVATE
                          "${xiph_generated}/base/upstream/libvorbis/lib")
target_compile_definitions(${COMPONENT_LIB} PRIVATE
                          XIPH_CASES_SHA256="${XIPH_CASES_SHA256}"
                          XIPH_MANIFEST_SHA256="${XIPH_BASE_MANIFEST_SHA256}"
                          XIPH_PORT_MANIFEST_SHA256="${XIPH_PORT_MANIFEST_SHA256}")
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off -fstack-usage)
# Allocation instrumentation is test-only and applies to library source only.
target_compile_options(${xiph_library} PRIVATE -fstack-usage
                       -include "${CMAKE_CURRENT_SOURCE_DIR}/vorbis_xiph_alloc_inject.h")
