if(CMAKE_BUILD_EARLY_EXPANSION)
    idf_component_register()
    return()
endif()

set(xiph_base "${CMAKE_CURRENT_LIST_DIR}/../native_vorbis_xiph")
set(xiph_generated "${CMAKE_CURRENT_BINARY_DIR}/xiph-source")
idf_build_get_property(xiph_python PYTHON)
execute_process(COMMAND "${xiph_python}" "${CMAKE_CURRENT_LIST_DIR}/prepare.py"
    --upstream "${xiph_base}" --port "${CMAKE_CURRENT_LIST_DIR}"
    --output "${xiph_generated}"
    RESULT_VARIABLE xiph_prepare_status OUTPUT_VARIABLE xiph_prepare_output
    ERROR_VARIABLE xiph_prepare_error)
if(NOT xiph_prepare_status EQUAL 0)
    message(FATAL_ERROR "Exact Xiph resource port failed: ${xiph_prepare_error}")
endif()
file(GLOB_RECURSE xiph_inputs CONFIGURE_DEPENDS
    "${xiph_base}/*" "${CMAKE_CURRENT_LIST_DIR}/edits/*")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    ${xiph_inputs} "${CMAKE_CURRENT_LIST_DIR}/prepare.py"
    "${CMAKE_CURRENT_LIST_DIR}/edits.json" "${CMAKE_CURRENT_LIST_DIR}/port-manifest.json")

set(vorbis_units
    mdct smallft block envelope window lsp lpc analysis synthesis psy info
    floor1 floor0 res0 mapping0 registry codebook sharedbook lookup bitrate)
set(xiph_sources)
foreach(unit IN LISTS vorbis_units)
    if(unit STREQUAL "block" OR unit STREQUAL "sharedbook" OR unit STREQUAL "codebook")
        list(APPEND xiph_sources "${xiph_generated}/ported/${unit}.c")
    else()
        list(APPEND xiph_sources "${xiph_generated}/base/upstream/libvorbis/lib/${unit}.c")
    endif()
endforeach()
list(APPEND xiph_sources "${xiph_generated}/ported/bitwise.c"
                         "${xiph_generated}/base/upstream/libogg/src/framing.c")
idf_component_register(SRCS ${xiph_sources}
    INCLUDE_DIRS "${xiph_generated}/base/upstream/libvorbis/include"
                 "${xiph_generated}/base/upstream/libogg/include"
                 "${xiph_generated}/base/platform"
    PRIV_INCLUDE_DIRS "${xiph_generated}/base/upstream/libvorbis/lib")
target_compile_definitions(${COMPONENT_LIB} PRIVATE HAVE_ALLOCA_H=1)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off
    -Wno-error=misleading-indentation)
if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    set_source_files_properties(
        "${xiph_generated}/base/upstream/libvorbis/lib/lpc.c"
        "${xiph_generated}/base/upstream/libvorbis/lib/psy.c"
        PROPERTIES COMPILE_OPTIONS "-Wno-error=maybe-uninitialized")
endif()
target_link_libraries(${COMPONENT_LIB} PUBLIC m)
