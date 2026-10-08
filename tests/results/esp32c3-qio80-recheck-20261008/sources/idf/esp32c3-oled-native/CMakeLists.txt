cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED ENV{YORADIO_AUDIO_CODEC_COMPONENT})
  message(FATAL_ERROR
    "YORADIO_AUDIO_CODEC_COMPONENT is not set; use build.ps1")
endif()

set(EXTRA_COMPONENT_DIRS
  "$ENV{YORADIO_AUDIO_CODEC_COMPONENT}"
  "${CMAKE_CURRENT_LIST_DIR}/../components/audio_level_led"
  "${CMAKE_CURRENT_LIST_DIR}/../components/native_audio_settings"
  "${CMAKE_CURRENT_LIST_DIR}/../components/custom_codec_support"
  "${CMAKE_CURRENT_LIST_DIR}/../components/custom_legacy_codecs")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(yoradio_esp32c3_oled_native)

# Optional full-radio flash-mode probe. It reports actual SPI0 registers and
# checks mapped application bytes before starting the ordinary application.
if(YORADIO_FLASH_MODE_PROBE)
    if(YORADIO_HARDWARE_FLAC_CLZ_TEST)
        message(FATAL_ERROR "Select only one app_main laboratory wrapper")
    endif()
    idf_component_get_property(yoradio_main_lib main COMPONENT_LIB)
    target_sources(${yoradio_main_lib} PRIVATE
        "${CMAKE_CURRENT_LIST_DIR}/../../tests/native/flash_mode/boot_probe.c")
    target_link_options(${yoradio_main_lib} INTERFACE "-Wl,--wrap=app_main")
endif()

if(CONFIG_YORADIO_GCM_BYTE_GHASH)
    idf_component_get_property(yoradio_gcm_dir mbedtls COMPONENT_DIR)
    idf_build_get_property(yoradio_gcm_python PYTHON)
    set(yoradio_gcm_original "${yoradio_gcm_dir}/port/aes/esp_aes_gcm.c")
    set(yoradio_gcm_header "${yoradio_gcm_dir}/port/include/aes/esp_aes_gcm.h")
    set(yoradio_gcm_generator "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_gcm_byte_ghash.py")
    set(yoradio_gcm_fixed "${CMAKE_BINARY_DIR}/yoradio_gcm/esp_aes_gcm.c")
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${yoradio_gcm_original}" "${yoradio_gcm_header}" "${yoradio_gcm_generator}")
    execute_process(COMMAND "${yoradio_gcm_python}" "${yoradio_gcm_generator}"
        --input "${yoradio_gcm_original}" --header "${yoradio_gcm_header}"
        --output "${yoradio_gcm_fixed}" RESULT_VARIABLE yoradio_gcm_patch_result)
    if(NOT yoradio_gcm_patch_result EQUAL 0)
        message(FATAL_ERROR "Cannot apply the audited GHASH experiment")
    endif()
    get_target_property(yoradio_gcm_sources tfpsacrypto SOURCES)
    set(yoradio_gcm_replaced 0)
    foreach(yoradio_source IN LISTS yoradio_gcm_sources)
        if(yoradio_source MATCHES "(^|/)port/aes/esp_aes_gcm\\.c$")
            list(REMOVE_ITEM yoradio_gcm_sources "${yoradio_source}")
            math(EXPR yoradio_gcm_replaced "${yoradio_gcm_replaced}+1")
        endif()
    endforeach()
    if(NOT yoradio_gcm_replaced EQUAL 1)
        message(FATAL_ERROR "Expected exactly one AES-GCM source to replace")
    endif()
    list(APPEND yoradio_gcm_sources "${yoradio_gcm_fixed}")
    set_property(TARGET tfpsacrypto PROPERTY SOURCES "${yoradio_gcm_sources}")
    target_include_directories(tfpsacrypto PRIVATE "${CMAKE_CURRENT_LIST_DIR}/main"
        "${CMAKE_BINARY_DIR}/yoradio_gcm")
    set_property(SOURCE "${yoradio_gcm_fixed}" TARGET_DIRECTORY tfpsacrypto
        APPEND PROPERTY COMPILE_OPTIONS "-fstack-usage")
endif()

if(CONFIG_YORADIO_TLS_RX_ONLY_RESERVE)
    idf_component_get_property(yoradio_tls_dir mbedtls COMPONENT_DIR)
    idf_build_get_property(yoradio_tls_python PYTHON)
    set(yoradio_tls_original "${yoradio_tls_dir}/port/dynamic/esp_mbedtls_dynamic_impl.c")
    set(yoradio_tls_generator "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_tls_rx_reserve.py")
    set(yoradio_tls_rx_fixed "${CMAKE_BINARY_DIR}/yoradio_mbedtls/esp_mbedtls_dynamic_impl.c")
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${yoradio_tls_original}" "${yoradio_tls_generator}")
    execute_process(COMMAND "${yoradio_tls_python}" "${yoradio_tls_generator}"
        --input "${yoradio_tls_original}" --output "${yoradio_tls_rx_fixed}"
        RESULT_VARIABLE yoradio_tls_patch_result)
    if(NOT yoradio_tls_patch_result EQUAL 0)
        message(FATAL_ERROR "Cannot apply the audited TLS RX allocation routing")
    endif()
    get_target_property(yoradio_tls_sources mbedtls SOURCES)
    set(yoradio_tls_replaced 0)
    foreach(yoradio_source IN LISTS yoradio_tls_sources)
        if(yoradio_source MATCHES "(^|/)port/dynamic/esp_mbedtls_dynamic_impl\\.c$")
            list(REMOVE_ITEM yoradio_tls_sources "${yoradio_source}")
            math(EXPR yoradio_tls_replaced "${yoradio_tls_replaced}+1")
        endif()
    endforeach()
    if(NOT yoradio_tls_replaced EQUAL 1)
        message(FATAL_ERROR "Expected exactly one dynamic TLS source to replace")
    endif()
    list(APPEND yoradio_tls_sources "${yoradio_tls_rx_fixed}")
    set_property(TARGET mbedtls PROPERTY SOURCES "${yoradio_tls_sources}")
    # The generated source no longer sits beside this private SDK header.
    target_include_directories(mbedtls PRIVATE "${yoradio_tls_dir}/port/dynamic")
endif()

# Keep the audited TIME_WAIT ownership fix local to this application. Never
# patch a shared IDF checkout, and fail configuration if its TCP source changes.
idf_component_get_property(yoradio_lwip_lib lwip COMPONENT_LIB)
idf_component_get_property(yoradio_lwip_dir lwip COMPONENT_DIR)
idf_build_get_property(yoradio_python PYTHON)
set(yoradio_tcp_original "${yoradio_lwip_dir}/lwip/src/core/tcp.c")
set(yoradio_tcp_generator "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_lwip_timewait.py")
set(yoradio_tcp_fixed "${CMAKE_BINARY_DIR}/yoradio_lwip/tcp.c")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${yoradio_tcp_original}" "${yoradio_tcp_generator}")
execute_process(COMMAND "${yoradio_python}" "${yoradio_tcp_generator}"
    --input "${yoradio_tcp_original}" --output "${yoradio_tcp_fixed}"
    RESULT_VARIABLE yoradio_tcp_patch_result)
if(NOT yoradio_tcp_patch_result EQUAL 0)
    message(FATAL_ERROR "Cannot apply the audited lwIP TIME_WAIT ownership fix")
endif()
get_target_property(yoradio_lwip_sources ${yoradio_lwip_lib} SOURCES)
set(yoradio_tcp_replaced 0)
foreach(yoradio_source IN LISTS yoradio_lwip_sources)
    if(yoradio_source MATCHES "(^|/)lwip/src/core/tcp\\.c$")
        list(REMOVE_ITEM yoradio_lwip_sources "${yoradio_source}")
        math(EXPR yoradio_tcp_replaced "${yoradio_tcp_replaced}+1")
    endif()
endforeach()
if(NOT yoradio_tcp_replaced EQUAL 1)
    message(FATAL_ERROR "Expected exactly one lwIP TCP source to replace")
endif()
list(APPEND yoradio_lwip_sources "${yoradio_tcp_fixed}")
set_property(TARGET ${yoradio_lwip_lib} PROPERTY SOURCES "${yoradio_lwip_sources}")

# The original IDF 6.1 tag lacks the Content-Length guard; the pinned newer
# revision has it. Preserve native guarded sources or generate a local
# backport for audited older SDKs. Reject unknown sources rather than guessing.
idf_component_get_property(yoradio_httpd_lib esp_http_server COMPONENT_LIB)
idf_component_get_property(yoradio_httpd_dir esp_http_server COMPONENT_DIR)
set(yoradio_httpd_original "${yoradio_httpd_dir}/src/httpd_parse.c")
set(yoradio_httpd_generator "${CMAKE_CURRENT_LIST_DIR}/../../tools/patch_httpd_content_length.py")
set(yoradio_httpd_fixed "${CMAKE_BINARY_DIR}/yoradio_httpd/httpd_parse.c")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${yoradio_httpd_original}" "${yoradio_httpd_generator}")
execute_process(COMMAND "${yoradio_python}" "${yoradio_httpd_generator}"
    --input "${yoradio_httpd_original}" --output "${yoradio_httpd_fixed}"
    RESULT_VARIABLE yoradio_httpd_patch_result)
if(NOT yoradio_httpd_patch_result EQUAL 0)
    message(FATAL_ERROR "Cannot preserve the audited HTTP Content-Length guard")
endif()
get_target_property(yoradio_httpd_sources ${yoradio_httpd_lib} SOURCES)
set(yoradio_httpd_replaced 0)
foreach(yoradio_source IN LISTS yoradio_httpd_sources)
    if(yoradio_source MATCHES "(^|/)src/httpd_parse\\.c$")
        list(REMOVE_ITEM yoradio_httpd_sources "${yoradio_source}")
        math(EXPR yoradio_httpd_replaced "${yoradio_httpd_replaced}+1")
    endif()
endforeach()
if(NOT yoradio_httpd_replaced EQUAL 1)
    message(FATAL_ERROR "Expected exactly one HTTP parser source to replace")
endif()
list(APPEND yoradio_httpd_sources "${yoradio_httpd_fixed}")
set_property(TARGET ${yoradio_httpd_lib} PROPERTY SOURCES "${yoradio_httpd_sources}")
target_include_directories(${yoradio_httpd_lib} PRIVATE "${yoradio_httpd_dir}/src")
set_source_files_properties("${yoradio_tcp_fixed}" PROPERTIES COMPILE_OPTIONS "-Wno-type-limits")

set(yoradio_api_original "${yoradio_lwip_dir}/lwip/src/api/api_msg.c")
set(yoradio_api_fixed "${CMAKE_BINARY_DIR}/yoradio_lwip/api_msg.c")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${yoradio_api_original}")
execute_process(COMMAND "${yoradio_python}" "${yoradio_tcp_generator}" --kind api
    --input "${yoradio_api_original}" --output "${yoradio_api_fixed}"
    RESULT_VARIABLE yoradio_api_patch_result)
if(NOT yoradio_api_patch_result EQUAL 0)
    message(FATAL_ERROR "Cannot apply the audited lwIP half-close ownership fix")
endif()
set(yoradio_api_replaced 0)
foreach(yoradio_source IN LISTS yoradio_lwip_sources)
    if(yoradio_source MATCHES "(^|/)lwip/src/api/api_msg\\.c$")
        list(REMOVE_ITEM yoradio_lwip_sources "${yoradio_source}")
        math(EXPR yoradio_api_replaced "${yoradio_api_replaced}+1")
    endif()
endforeach()
if(NOT yoradio_api_replaced EQUAL 1)
    message(FATAL_ERROR "Expected exactly one lwIP netconn API source to replace")
endif()
list(APPEND yoradio_lwip_sources "${yoradio_api_fixed}")
set_property(TARGET ${yoradio_lwip_lib} PROPERTY SOURCES "${yoradio_lwip_sources}")
