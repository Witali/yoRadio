if(NOT EXISTS "${CMAKE_BINARY_DIR}/resources/web_pages.c")
    message(FATAL_ERROR "Run build.ps1 or tools/prepare_resources.py before configuring")
endif()
idf_component_register(
    SRCS app_main.c settings/settings.c settings/factory_settings.c display/st7789.c display/backlight.c
         display/clock_ui.c display/factory_fonts.c display/ui_renderer.c media/assets.c media/photo_upload.c network/wifi.c
         network/dns.c network/dns_packet.c services/time_sync.c services/weather.c services/weather_parser.c web/server.c
         web/settings_api.c web/photo_api.c
         ../third_party/tjpgd/tjpgd.c ../third_party/cjson/cJSON.c
         "${CMAKE_BINARY_DIR}/resources/web_pages.c"
         "${CMAKE_BINARY_DIR}/resources/factory_bitmaps.c"
    INCLUDE_DIRS include ../third_party/tjpgd ../third_party/cjson
                 "${CMAKE_BINARY_DIR}/resources"
    REQUIRES esp_driver_spi esp_driver_gpio esp_driver_ledc esp_timer
             nvs_flash esp_wifi esp_netif esp_event esp_http_server
             esp_http_client mbedtls lwip spi_flash esp_partition
)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror=implicit-function-declaration)
target_compile_definitions(${COMPONENT_LIB} PRIVATE CJSON_NESTING_LIMIT=16)
