# Include and call after idf_component_register(). Keep the installed SDK intact;
# its own target retains all private headers, configuration and compiler flags.
function(native_enable_http_request_buffer_release)
    if(CMAKE_BUILD_EARLY_EXPANSION OR NOT CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE)
        return()
    endif()
    if(NOT IDF_VERSION_MAJOR EQUAL 6 OR NOT IDF_VERSION_MINOR EQUAL 0 OR
       NOT IDF_VERSION_PATCH EQUAL 2)
        message(FATAL_ERROR "HTTP request-buffer release requires audited ESP-IDF 6.0.2")
    endif()
    idf_component_get_property(native_http_target esp_http_client COMPONENT_LIB)
    idf_component_get_property(native_http_dir esp_http_client COMPONENT_DIR)
    get_filename_component(native_http_original "${native_http_dir}/esp_http_client.c" REALPATH)
    get_filename_component(native_http_root "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../../../../.." ABSOLUTE)
    set(native_http_patcher "${native_http_root}/tools/patch_cyd_http_request_buffer.py")
    set(native_http_generated "${CMAKE_BINARY_DIR}/native-http-request-buffer/esp_http_client.c")
    get_target_property(native_http_sources ${native_http_target} SOURCES)
    set(native_http_replaced 0)
    set(native_http_replacements)
    foreach(native_http_source IN LISTS native_http_sources)
        get_filename_component(native_http_candidate "${native_http_source}" REALPATH
            BASE_DIR "${native_http_dir}")
        if(native_http_candidate STREQUAL native_http_original)
            list(APPEND native_http_replacements "${native_http_generated}")
            math(EXPR native_http_replaced "${native_http_replaced}+1")
        else()
            list(APPEND native_http_replacements "${native_http_source}")
        endif()
    endforeach()
    if(NOT native_http_replaced EQUAL 1)
        message(FATAL_ERROR "Expected exactly one original HTTP client source, found ${native_http_replaced}")
    endif()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${native_http_original}" "${native_http_patcher}")
    execute_process(COMMAND "${PYTHON}" "${native_http_patcher}"
        --input "${native_http_original}" --output "${native_http_generated}"
        RESULT_VARIABLE native_http_result
        OUTPUT_VARIABLE native_http_output ERROR_VARIABLE native_http_error)
    if(NOT native_http_result EQUAL 0)
        message(FATAL_ERROR "HTTP request-buffer overlay rejected SDK: ${native_http_output}${native_http_error}")
    endif()
    set_property(TARGET ${native_http_target} PROPERTY SOURCES ${native_http_replacements})
endfunction()
