idf_component_register(SRCS "native_wifi_store.c" "native_wifi_file.c"
                       "native_wifi_json.c" "native_wifi_http.c" "native_wifi_request_io.c"
                       INCLUDE_DIRS "include"
                       REQUIRES native_storage esp_http_server native_web_transport
                                esp_timer freertos
                       PRIV_REQUIRES lwip)
