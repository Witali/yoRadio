idf_component_register(
  SRCS
    "app_main.c"
    "native_state.c"
  INCLUDE_DIRS "."
  REQUIRES esp8266 freertos heap log pthread)

# ESP8266_RTOS_SDK exposes only -Og/-Os in menuconfig. Audio code needs the
# same explicit performance profile used by the ESP32-C3 native build.
target_compile_options(${COMPONENT_LIB} PRIVATE -O3)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
  YORADIO_ESP8266_NATIVE=1
  YORADIO_HTTP_ONLY=1
  YORADIO_HELIX_MP3=1
  YORADIO_HELIX_AAC=1)
