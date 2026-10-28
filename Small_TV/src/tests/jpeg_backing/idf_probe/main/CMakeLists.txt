idf_component_register(
    SRCS probe.c ../../../../codec/jpeg_decoder.c ../../../../codec/jpeg_memory.c
         ../../../../codec/jpeg_backing.c ../../../../codec/jpeg_coefficients.c
         ../../../../storage/jpeg_scratch.c ../../../../storage/jpeg_nor.c
         ../../../../storage/jpeg_guard.c ../../../../storage/jpeg_provision.c ../../../../storage/jpeg_transport.c
         ../../../../storage/jpeg_espidf.c ../../../../app/media/color_convert.c
    INCLUDE_DIRS ../../../../codec ../../../../storage ../../../../app/include
                 "${JPEG_PROBE_GENERATED}" "${JPEG_PROBE_LIBRARY}/source/src"
                 "${JPEG_PROBE_LIBRARY}/library"
    REQUIRES spi_flash esp_partition bootloader_support esp_timer mbedtls
)
add_library(jpeg_probe_vendor STATIC IMPORTED)
set_target_properties(jpeg_probe_vendor PROPERTIES
    IMPORTED_LOCATION "${JPEG_PROBE_LIBRARY}/library/libjpeg.a")
target_link_libraries(${COMPONENT_LIB} PRIVATE jpeg_probe_vendor)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -fstack-usage)
