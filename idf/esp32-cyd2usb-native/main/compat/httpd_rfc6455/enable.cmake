# This helper is included after idf_component_register(). Source generation is
# configure-time only and never modifies IDF_PATH. The matched HTTPD target
# supplies its own private headers and configuration to the replacement units.
function(native_enable_httpd_rfc6455)
    if(CMAKE_BUILD_EARLY_EXPANSION)
        return()
    endif()
    idf_component_get_property(native_httpd_target esp_http_server COMPONENT_LIB)
    idf_component_get_property(native_httpd_dir esp_http_server COMPONENT_DIR)
    set(native_overlay_dir "${CMAKE_CURRENT_FUNCTION_LIST_DIR}")
    set(native_generated "${CMAKE_BINARY_DIR}/native-httpd-rfc6455")
    execute_process(COMMAND "${PYTHON}" "${native_overlay_dir}/apply.py"
        --sdk "${IDF_PATH}" --output "${native_generated}"
        RESULT_VARIABLE native_result OUTPUT_VARIABLE native_output ERROR_VARIABLE native_error)
    if(NOT native_result EQUAL 0)
        message(FATAL_ERROR "RFC6455 HTTPD overlay rejected SDK: ${native_output}${native_error}")
    endif()
    get_target_property(native_sources ${native_httpd_target} SOURCES)
    set(native_replaced 0)
    foreach(native_source IN LISTS native_sources)
        if(native_source MATCHES "(^|/)httpd_(ws|parse)\\.c$")
            list(REMOVE_ITEM native_sources "${native_source}")
            math(EXPR native_replaced "${native_replaced}+1")
        endif()
    endforeach()
    if(NOT native_replaced EQUAL 2)
        message(FATAL_ERROR "Expected exactly two original HTTPD sources, found ${native_replaced}")
    endif()
    set_property(TARGET ${native_httpd_target} PROPERTY SOURCES ${native_sources})
    target_sources(${native_httpd_target} PRIVATE "${native_generated}/httpd_ws.c" "${native_generated}/httpd_parse.c")
    target_include_directories(${native_httpd_target} PRIVATE "${native_overlay_dir}" "${native_httpd_dir}/src")
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${native_overlay_dir}/apply.py" "${native_overlay_dir}/native_httpd_headers.h"
        "${native_httpd_dir}/src/httpd_ws.c" "${native_httpd_dir}/src/httpd_parse.c"
        "${native_httpd_dir}/src/esp_httpd_priv.h" "${native_httpd_dir}/include/esp_http_server.h")
endfunction()
