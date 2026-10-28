idf_component_register(SRCS "view.c" "product.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_window)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
