idf_component_register(SRCS "floor1_product.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_packet_frame)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
