# Match Xiph libvorbis 1.3.7's complete base-library target. Encoder callbacks
# share its backend registry; do not trim units before measuring the baseline.
set(vorbis_units
    mdct smallft block envelope window lsp lpc analysis synthesis psy info
    floor1 floor0 res0 mapping0 registry codebook sharedbook lookup bitrate)
set(xiph_sources)
foreach(unit IN LISTS vorbis_units)
    list(APPEND xiph_sources "upstream/libvorbis/lib/${unit}.c")
endforeach()
list(APPEND xiph_sources
    "upstream/libogg/src/bitwise.c"
    "upstream/libogg/src/framing.c")

idf_component_register(
    SRCS ${xiph_sources}
    INCLUDE_DIRS "upstream/libvorbis/include" "upstream/libogg/include" "platform"
    PRIV_INCLUDE_DIRS "upstream/libvorbis/lib")
target_compile_definitions(${COMPONENT_LIB} PRIVATE HAVE_ALLOCA_H=1)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
# GCC 15 diagnoses the release's consecutive free/reset statements in block.c.
# Keep that diagnostic visible without modifying the imported baseline.
target_compile_options(${COMPONENT_LIB} PRIVATE -Wno-error=misleading-indentation)
if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    # Encoder-only routines initialize their arrays for the positive sizes
    # supplied by upstream callers; GCC 15 cannot prove those preconditions.
    set_source_files_properties(
        "upstream/libvorbis/lib/lpc.c" "upstream/libvorbis/lib/psy.c"
        PROPERTIES COMPILE_OPTIONS "-Wno-error=maybe-uninitialized")
endif()
target_link_libraries(${COMPONENT_LIB} PUBLIC m)
