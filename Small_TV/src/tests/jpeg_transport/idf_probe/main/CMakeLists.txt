idf_component_register(
    SRCS probe.c ../../../../storage/jpeg_transport.c ../../../../storage/jpeg_guard.c
         ../../../../storage/jpeg_nor.c ../../../../storage/jpeg_espidf.c
    INCLUDE_DIRS ../../../../storage "${JPEG_PROBE_GENERATED}"
    REQUIRES spi_flash esp_partition bootloader_support esp_timer mbedtls
)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror)
