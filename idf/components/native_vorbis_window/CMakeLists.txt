idf_component_register(SRCS "window.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_transform)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
