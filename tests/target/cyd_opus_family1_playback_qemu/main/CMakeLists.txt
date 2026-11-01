idf_component_register(SRCS "main.c" "direct_reference.c" INCLUDE_DIRS "." REQUIRES esp_audio_codec esp_system heap freertos mbedtls)
target_compile_options(${COMPONENT_LIB} PRIVATE -UNDEBUG -fstack-usage -Wall -Wextra -Werror -Wformat=2)
target_add_binary_data(${COMPONENT_LIB} "${CMAKE_CURRENT_LIST_DIR}/fixtures.bin" BINARY)
