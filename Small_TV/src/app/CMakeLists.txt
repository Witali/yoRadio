if(NOT EXISTS "${CMAKE_BINARY_DIR}/resources/web_pages.c")
    message(FATAL_ERROR "Run build.ps1 or tools/prepare_resources.py before configuring")
endif()
if(NOT CMAKE_BUILD_EARLY_EXPANSION AND NOT EXISTS "${JPEG_LIBRARY_BUILD}/library/libjpeg.a")
    message(FATAL_ERROR "Run build.ps1 to prepare the pinned offline JPEG dependency")
endif()
idf_component_register(
    SRCS app_main.c settings/settings.c settings/factory_settings.c display/st7789.c display/backlight.c
         display/clock_ui.c display/factory_timer.c display/factory_photo.c display/factory_animation.c display/factory_fonts.c display/ui_renderer.c media/assets.c media/photo_upload.c media/photo_codec.c media/photo_worker.c media/photo_storage.c media/color_convert.c network/wifi.c
         network/dns.c network/dns_packet.c services/time_sync.c services/timezones.c services/weather.c services/weather_parser.c web/server.c
         web/request_body.c web/settings_api.c web/photo_api.c web/photo_async.c text/text.c
         ../third_party/tjpgd/tjpgd.c ../third_party/cjson/cJSON.c
         ../codec/jpeg_privacy.c ../codec/jpeg_baseline.c ../codec/jpeg_decoder.c ../codec/jpeg_memory.c ../codec/jpeg_backing.c ../codec/jpeg_coefficients.c
         ../storage/jpeg_nor.c ../storage/jpeg_guard.c ../storage/jpeg_transport.c ../storage/jpeg_espidf.c
         ../storage/jpeg_scratch.c ../storage/jpeg_journal.c ../storage/jpeg_cache.c
         "${CMAKE_BINARY_DIR}/resources/web_pages.c"
         "${CMAKE_BINARY_DIR}/resources/factory_bitmaps.c"
    INCLUDE_DIRS include ../third_party/tjpgd ../third_party/cjson
                 ../codec ../storage "${JPEG_LIBRARY_BUILD}/source/src" "${JPEG_LIBRARY_BUILD}/library"
                 "${CMAKE_BINARY_DIR}/resources"
    REQUIRES esp_driver_spi esp_driver_gpio esp_driver_ledc esp_driver_gptimer esp_timer
             nvs_flash esp_wifi esp_netif esp_event esp_http_server
             esp_http_client mbedtls lwip spi_flash esp_partition bootloader_support
)
add_library(small_tv_jpeg_vendor STATIC IMPORTED)
set_target_properties(small_tv_jpeg_vendor PROPERTIES
    IMPORTED_LOCATION "${JPEG_LIBRARY_BUILD}/library/libjpeg.a")
target_link_libraries(${COMPONENT_LIB} PRIVATE small_tv_jpeg_vendor)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror=implicit-function-declaration)
target_compile_definitions(${COMPONENT_LIB} PRIVATE CJSON_NESTING_LIMIT=16)
target_compile_definitions(${COMPONENT_LIB} PRIVATE DEBUG=$<BOOL:${DEBUG}>)
