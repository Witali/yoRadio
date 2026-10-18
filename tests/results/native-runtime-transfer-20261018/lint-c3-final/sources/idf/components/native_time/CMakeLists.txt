idf_component_register(SRCS "native_time_sntp.c" "native_time_sntp_context.c"
                       INCLUDE_DIRS "include"
                       REQUIRES esp_netif lwip freertos)
