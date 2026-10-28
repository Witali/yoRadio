idf_component_register(SRCS "bigfloat.c" "portable/libbf.c" "upstream/cutils.c"
    INCLUDE_DIRS "include" "upstream")
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
