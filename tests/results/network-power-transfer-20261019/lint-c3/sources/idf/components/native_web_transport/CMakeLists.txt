idf_component_register(SRCS "native_web_transport.c"
  INCLUDE_DIRS "include"
  REQUIRES esp_http_server esp-tls mbedtls nvs_flash esp_timer freertos
  PRIV_REQUIRES lwip)
