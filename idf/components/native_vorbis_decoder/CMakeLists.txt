idf_component_register(SRCS "decoder.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_setup_owner native_vorbis_synthesis native_vorbis_floor0_spectrum)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
