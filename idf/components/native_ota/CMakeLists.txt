idf_component_register(SRCS "native_ota_sink.c" "native_ota_form.c" "native_ota_http.c"
  INCLUDE_DIRS "include"
  PRIV_INCLUDE_DIRS "../native_stream/include"
  REQUIRES app_update bootloader_support esp_app_format esp_partition
    esp_http_server native_web_transport native_storage esp_timer freertos
  PRIV_REQUIRES lwip)
