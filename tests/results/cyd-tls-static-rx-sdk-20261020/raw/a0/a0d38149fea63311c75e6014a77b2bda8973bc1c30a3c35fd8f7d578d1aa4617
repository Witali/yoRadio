# Include/call after idf_component_register(); leave installed SDK unchanged.
function(native_enable_tls_static_rx_reserve)
    if(CMAKE_BUILD_EARLY_EXPANSION OR NOT CONFIG_YORADIO_TLS_STATIC_RX_RESERVE)
        return()
    endif()
    if(NOT "${IDF_VERSION_MAJOR}" STREQUAL "6" OR
       NOT "${IDF_VERSION_MINOR}" STREQUAL "0" OR
       NOT "${IDF_VERSION_PATCH}" STREQUAL "2" OR
       NOT "${IDF_TARGET}" STREQUAL "esp32" OR NOT CONFIG_IDF_TARGET_ESP32)
        message(FATAL_ERROR "CYD static RX reserve requires exact ESP32 IDF6.0.2")
    endif()
    if(NOT CONFIG_ESP_TLS_USING_MBEDTLS OR NOT CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC OR
       NOT CONFIG_MBEDTLS_CERTIFICATE_BUNDLE OR CONFIG_MBEDTLS_CUSTOM_MEM_ALLOC OR
       CONFIG_MBEDTLS_DYNAMIC_BUFFER OR CONFIG_MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH OR
       CONFIG_MBEDTLS_SSL_PROTO_GMTSSL1_1 OR CONFIG_MBEDTLS_SSL_CONTEXT_SERIALIZATION OR
       NOT "${CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN}" STREQUAL "16384")
        message(FATAL_ERROR "CYD static RX reserve rejects unsupported allocator/buffer/config lifetime")
    endif()
    if(NOT TARGET mbedtls OR NOT TARGET ${COMPONENT_LIB})
        message(FATAL_ERROR "CYD static RX reserve requires registered canonical targets")
    endif()
    get_filename_component(reserve_repository
        "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../../../../.." ABSOLUTE)
    set(YORADIO_RX_RESERVE_PATCHER "${reserve_repository}/tools/patch_cyd_tls_static_rx.py")
    set(YORADIO_RX_RESERVE_MODULE "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../../native_tls_rx_reserve.c")
    set(YORADIO_RX_RESERVE_GUARDS "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/sdk-source-guards.json")
    set(reserve_header "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../../native_tls_rx_reserve.h")
    if(NOT EXISTS "${reserve_header}")
        message(FATAL_ERROR "Missing canonical static RX reserve header")
    endif()
    idf_component_get_property(reserve_dir mbedtls COMPONENT_DIR)
    get_filename_component(reserve_sdk_root "${reserve_dir}/../.." REALPATH)
    set(reserve_library_dir "${reserve_dir}/mbedtls/library")
    get_filename_component(reserve_original "${reserve_library_dir}/ssl_tls.c" REALPATH)
    get_target_property(reserve_sources mbedtls SOURCES)
    set(reserve_replaced 0)
    set(reserve_replacements)
    set(reserve_generated "${CMAKE_BINARY_DIR}/native-tls-static-rx/ssl_tls.c")
    foreach(reserve_source IN LISTS reserve_sources)
        get_filename_component(reserve_candidate "${reserve_source}" REALPATH
            BASE_DIR "${reserve_library_dir}")
        if(reserve_candidate STREQUAL reserve_original)
            list(APPEND reserve_replacements "${reserve_generated}")
            math(EXPR reserve_replaced "${reserve_replaced}+1")
        else()
            list(APPEND reserve_replacements "${reserve_source}")
        endif()
    endforeach()
    if(NOT reserve_replaced EQUAL 1)
        message(FATAL_ERROR "Expected exactly one audited static RX source")
    endif()
    if(NOT DEFINED YORADIO_RX_RESERVE_PATCHER OR
       NOT DEFINED YORADIO_RX_RESERVE_MODULE OR
       NOT EXISTS "${YORADIO_RX_RESERVE_PATCHER}" OR
       NOT EXISTS "${YORADIO_RX_RESERVE_MODULE}" OR
       NOT DEFINED YORADIO_RX_RESERVE_GUARDS OR
       NOT EXISTS "${YORADIO_RX_RESERVE_GUARDS}")
        message(FATAL_ERROR "Missing canonical static RX reserve inputs")
    endif()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${reserve_original}" "${YORADIO_RX_RESERVE_PATCHER}" "${YORADIO_RX_RESERVE_GUARDS}")
    execute_process(COMMAND "${PYTHON}" "${YORADIO_RX_RESERVE_PATCHER}"
        --input "${reserve_original}" --output "${reserve_generated}"
        --sdk-root "${reserve_sdk_root}" --guards "${YORADIO_RX_RESERVE_GUARDS}"
        RESULT_VARIABLE reserve_result ERROR_VARIABLE reserve_error)
    if(NOT reserve_result EQUAL 0)
        message(FATAL_ERROR "CYD static RX overlay rejected SDK: ${reserve_error}")
    endif()
    file(READ "${YORADIO_RX_RESERVE_GUARDS}" reserve_guard_json)
    string(JSON reserve_guard_count LENGTH "${reserve_guard_json}")
    math(EXPR reserve_guard_last "${reserve_guard_count}-1")
    foreach(reserve_guard_index RANGE 0 ${reserve_guard_last})
        string(JSON reserve_guard_relative MEMBER "${reserve_guard_json}" ${reserve_guard_index})
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
            "${reserve_sdk_root}/${reserve_guard_relative}")
    endforeach()
    set_property(TARGET mbedtls PROPERTY SOURCES "${reserve_replacements}")
    target_sources(${COMPONENT_LIB} PRIVATE "${YORADIO_RX_RESERVE_MODULE}")
    # No global free wrapper or allocator callback substitution is added.
endfunction()
