idf_component_register(SRCS "spectrum.c" "transform.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_floor1_product)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
