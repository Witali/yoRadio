idf_component_register(SRCS "interval.c" "constants.c" "trig.c"
    INCLUDE_DIRS "include" REQUIRES native_vorbis_bigfloat)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
