# Include and call after idf_component_register(). No SDK sources are replaced.
function(native_enable_tls_input_reclaim)
    if(CMAKE_BUILD_EARLY_EXPANSION OR NOT CONFIG_YORADIO_TLS_INPUT_RECLAIM)
        return()
    endif()
    if(NOT CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER OR NOT CONFIG_ESP_TLS_USING_MBEDTLS OR
       NOT CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC OR CONFIG_MBEDTLS_CUSTOM_MEM_ALLOC OR
       CONFIG_HEAP_ABORT_WHEN_ALLOCATION_FAILS)
        message(FATAL_ERROR "TLS input reclaim requires adaptive input, internal SDK mbedTLS allocation and recoverable allocation failures")
    endif()
    target_sources(${COMPONENT_LIB} PRIVATE
        "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../../native_input_reclaim.c")
    target_link_options(${COMPONENT_LIB} INTERFACE
        "-Wl,--wrap=esp_mbedtls_mem_calloc"
        "-Wl,--undefined=__wrap_esp_mbedtls_mem_calloc")
endfunction()
