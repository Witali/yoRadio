idf_component_register(SRCS "native_ota_sink.c"
  INCLUDE_DIRS "include"
  REQUIRES app_update bootloader_support esp_app_format esp_partition)
