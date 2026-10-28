idf_component_register(SRCS "floor0_spectrum.c" "product.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_transform)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
