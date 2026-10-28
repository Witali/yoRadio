idf_component_register(SRCS "pcm.c" "windows.c" INCLUDE_DIRS "include" REQUIRES native_vorbis_window_exact)
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math -ffp-contract=off)
