idf_component_register(SRCS "floor0.c" "quant.c" "codebook.c" "setup.c" "floor_packet.c" "residue.c" INCLUDE_DIRS "include")
target_compile_options(${COMPONENT_LIB} PRIVATE -fno-fast-math)
