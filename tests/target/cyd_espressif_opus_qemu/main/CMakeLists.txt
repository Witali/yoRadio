idf_component_register(SRCS "main.c" "decoder_registration.c"
    INCLUDE_DIRS "." REQUIRES esp_audio_codec mbedtls esp_system heap freertos)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
    CONFIG_YORADIO_MP3_DECODER_ESPRESSIF=1 CONFIG_YORADIO_AAC_DECODER_ESPRESSIF=1)
target_compile_options(${COMPONENT_LIB} PRIVATE -UNDEBUG -fstack-usage)
target_add_binary_data(${COMPONENT_LIB} "${CMAKE_CURRENT_LIST_DIR}/fixture.ogg" BINARY)
