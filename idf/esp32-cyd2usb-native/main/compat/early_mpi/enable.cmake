# Include and call after idf_component_register(PRIV_REQUIRES esp_security ...).
# No SDK sources, mutex implementation or task profiles are replaced.
function(native_enable_tls_early_mpi)
    if(CMAKE_BUILD_EARLY_EXPANSION OR NOT CONFIG_YORADIO_TLS_EARLY_MPI_LOCK)
        return()
    endif()
    if(NOT CONFIG_IDF_TARGET_ESP32 OR NOT CONFIG_SOC_MPI_SUPPORTED OR
       NOT CONFIG_ESP_TLS_USING_MBEDTLS OR NOT CONFIG_MBEDTLS_HARDWARE_MPI)
        message(FATAL_ERROR "Early MPI requires ESP32, SOC MPI and the mbedTLS hardware MPI profile")
    endif()
    target_sources(${COMPONENT_LIB} PRIVATE
        "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../../native_tls_early_mpi.c")
endfunction()
