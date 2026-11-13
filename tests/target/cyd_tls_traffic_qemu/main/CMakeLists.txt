set(R "$ENV{TLS_TRAFFIC_REPOSITORY}")
set(M "${R}/idf/esp32-cyd2usb-native/main")
set(A "${R}/idf/components/native_stream")
idf_component_register(SRCS "main.c" "${A}/adaptive_input.c"
    INCLUDE_DIRS "." "${M}" "${A}/include"
    REQUIRES esp_eth esp_netif esp_event nvs_flash esp-tls mbedtls heap esp_system esp_timer esp_http_server
    PRIV_REQUIRES esp_security)
include("${M}/compat/tls_static_rx/enable.cmake")
native_enable_tls_static_rx_reserve()
include("${M}/compat/input_reclaim/enable.cmake")
native_enable_tls_input_reclaim()
include("${M}/compat/early_mpi/enable.cmake")
native_enable_tls_early_mpi()
set(traffic_wrappers native_tls_early_mpi_prepare heap_caps_calloc)
if(CONFIG_YORADIO_TLS_STATIC_RX_RESERVE)
    list(APPEND traffic_wrappers yoradio_tls_static_rx_calloc yoradio_tls_static_rx_free
         yoradio_tls_static_rx_zeroize_free native_tls_rx_reserve_crt_bundle_attach)
else()
    list(APPEND traffic_wrappers esp_crt_bundle_attach)
endif()
foreach(symbol IN LISTS traffic_wrappers)
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=${symbol}")
endforeach()
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror)
