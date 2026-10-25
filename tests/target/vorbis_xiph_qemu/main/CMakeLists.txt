idf_component_register(SRCS "main.c" INCLUDE_DIRS "."
                      REQUIRES freertos esp_system heap native_vorbis_xiph)
if(CMAKE_BUILD_EARLY_EXPANSION)
    return()
endif()
if(NOT IDF_TARGET STREQUAL "esp32" OR NOT CONFIG_IDF_TARGET_ESP32)
    message(FATAL_ERROR "The first Xiph baseline is ESP32 only")
endif()
if(NOT "${IDF_VERSION_MAJOR}.${IDF_VERSION_MINOR}.${IDF_VERSION_PATCH}" STREQUAL "6.0.2")
    message(FATAL_ERROR "Wrong pinned SDK version")
endif()
file(SHA256 "$ENV{XIPH_COMPONENT}/component-manifest.json" manifest_sha256)
if(NOT manifest_sha256 STREQUAL XIPH_COMPONENT_MANIFEST_SHA256)
    message(FATAL_ERROR "Frozen complete component manifest mismatch")
endif()
target_compile_definitions(${COMPONENT_LIB} PRIVATE
                          XIPH_CASES_SHA256="${XIPH_CASES_SHA256}"
                          XIPH_MANIFEST_SHA256="${XIPH_COMPONENT_MANIFEST_SHA256}")
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off -fstack-usage)
idf_component_get_property(xiph_library native_vorbis_xiph COMPONENT_LIB)
# Compiler frame observations belong only to this isolated fixture.
target_compile_options(${xiph_library} PRIVATE -fstack-usage)
