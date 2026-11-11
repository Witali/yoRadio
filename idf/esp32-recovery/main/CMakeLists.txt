idf_component_register(SRCS "recovery.c"
    PRIV_REQUIRES app_update bootloader_support esp_app_format esp_event
                  esp_http_server esp_hw_support esp_netif esp_system esp_timer esp_wifi
    EMBED_TXTFILES "upload.html")
