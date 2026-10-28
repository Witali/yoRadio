idf_component_register(SRCS "gain.c" INCLUDE_DIRS "include"
    REQUIRES native_vorbis_interval native_vorbis_numeric)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
