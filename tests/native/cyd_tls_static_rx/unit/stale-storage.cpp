/* HOST object-lifetime regression, not an SDK/target ABI declaration. Placement
 * new deterministically reuses storage without weakening ASan quarantine. */
#include <new>
extern "C" {
#include "platform.h"
#include "native_tls_rx_reserve.h"
void registry_host_check(bool condition,const char *name);
}
extern "C" void registry_stale_storage_case(void *reserve) {
    alignas(mbedtls_ssl_config) unsigned char storage[sizeof(mbedtls_ssl_config)];
    auto *old = ::new (static_cast<void *>(storage)) mbedtls_ssl_config;
    mbedtls_ssl_config_init(old);old->max_tls_version=0x303;
    mbedtls_ssl_conf_set_user_data_n(old,UINTPTR_MAX);
    registry_host_check(native_tls_rx_reserve_crt_bundle_attach(old)==0,"stale_storage_initial_attach");
    void *first=yoradio_tls_static_rx_calloc(old,1,MBEDTLS_SSL_IN_BUFFER_LEN);
    registry_host_check(first==reserve,"stale_storage_initial_eligible");yoradio_tls_static_rx_free(first);
    /* This host config owns no crypto allocations. Deliberately end its object
     * lifetime without config_free, leaving only a stale INTEGER identity key. */
    old->~mbedtls_ssl_config();
    auto *fresh=::new (static_cast<void *>(storage)) mbedtls_ssl_config;
    mbedtls_ssl_config_init(fresh);fresh->max_tls_version=0x303;
    mbedtls_ssl_conf_set_user_data_n(fresh,UINTPTR_MAX-17U);
    void *ordinary=yoradio_tls_static_rx_calloc(fresh,1,MBEDTLS_SSL_IN_BUFFER_LEN);
    registry_host_check(ordinary&&ordinary!=reserve,"new_object_init_clears_stale_integer_identity");
    yoradio_tls_static_rx_free(ordinary);
    registry_host_check(native_tls_rx_reserve_crt_bundle_attach(fresh)==0,"new_object_explicit_radio_attach");
    void *next=yoradio_tls_static_rx_calloc(fresh,1,MBEDTLS_SSL_IN_BUFFER_LEN);
    registry_host_check(next==reserve&&mbedtls_ssl_conf_get_user_data_n(fresh)==UINTPTR_MAX-17U,"new_object_radio_data_and_eligibility");
    yoradio_tls_static_rx_free(next);mbedtls_ssl_config_free(fresh);fresh->~mbedtls_ssl_config();
}
