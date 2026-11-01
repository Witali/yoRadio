idf_component_register(SRCS "main.c" INCLUDE_DIRS "." REQUIRES esp_audio_codec esp_system heap freertos)
target_compile_options(${COMPONENT_LIB} PRIVATE -UNDEBUG -fstack-usage)
target_add_binary_data(${COMPONENT_LIB} "${CMAKE_CURRENT_LIST_DIR}/streams.bin" BINARY)
