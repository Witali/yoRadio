set(M "$ENV{EARLY_MPI_SOURCE_ROOT}")
idf_component_register(SRCS "main.c"
    INCLUDE_DIRS "." "${M}"
    REQUIRES freertos heap esp_system mbedtls esp-tls esp_http_server
    PRIV_REQUIRES esp_security)
include("${M}/compat/early_mpi/enable.cmake")
native_enable_tls_early_mpi()
foreach(symbol _lock_acquire _lock_release xQueueCreateMutex)
    target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=${symbol}")
endforeach()
if(TEST_SKIP_ACQUIRE_CONTROL)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE TEST_SKIP_ACQUIRE_CONTROL=1)
endif()
if(TEST_VOID_OOM)
    target_compile_definitions(${COMPONENT_LIB} PRIVATE TEST_VOID_OOM=1)
endif()
