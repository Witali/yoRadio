idf_component_register(SRCS "consumer_unit.c"
    INCLUDE_DIRS "." "pinned/codec/include" "pinned/codec/include/decoder" "pinned/codec/include/decoder/impl"
    REQUIRES freertos esp_system)
target_compile_options(${COMPONENT_LIB} PRIVATE -ffunction-sections -fdata-sections -fno-inline)
target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--gc-sections")
