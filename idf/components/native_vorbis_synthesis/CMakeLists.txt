idf_component_register(SRCS "synthesis.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_pcm_exact native_vorbis_timing)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
