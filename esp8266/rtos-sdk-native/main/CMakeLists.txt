idf_component_register(
  SRCS
    "app_main.c"
    "native_state.c"
    "network_service.c"
    "persistent_settings.c"
    "playlist_service.c"
    "storage_service.c"
    "time_service.c"
  INCLUDE_DIRS "."
  REQUIRES esp8266 esp_event freertos heap log lwip nvs_flash pthread
           spiffs tcpip_adapter)

# ESP8266_RTOS_SDK exposes only -Og/-Os in menuconfig. Audio code needs the
# same explicit performance profile used by the ESP32-C3 native build.
target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1
  YORADIO_HTTP_ONLY=1
  YORADIO_HELIX_MP3=1
  YORADIO_HELIX_AAC=1)
