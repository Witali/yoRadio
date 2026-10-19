#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "stubs.h"
#include "network_netif.h"

#define CHECK(condition, marker) do { if (!(condition)) { \
    fprintf(stderr, "SEMANTIC_FAILURE:%s:%u\n", marker, __LINE__); exit(80); \
} } while (0)

const esp_netif_inherent_config_t _g_esp_netif_inherent_sta_config = {1};
const esp_netif_inherent_config_t _g_esp_netif_inherent_ap_config = {2};
static const esp_netif_netstack_config_t sta_stack = {1}, ap_stack = {2};
const esp_netif_netstack_config_t *_g_esp_netif_netstack_default_wifi_sta = &sta_stack;
const esp_netif_netstack_config_t *_g_esp_netif_netstack_default_wifi_ap = &ap_stack;

static unsigned cases, netif_creates, netif_destroys, driver_creates, driver_destroys;
static unsigned attach_configs, clear_configs, clear_calls, register_calls, unregister_calls;
static unsigned shutdown_registers, shutdown_unregisters, rx_unregistrations;
static bool fail_new, fail_driver, fail_post_attach, fail_clear;
static unsigned fail_register_at;
static esp_err_t shutdown_result;
static esp_netif_t *netifs[4];
static void *drivers[4];
static esp_event_handler_t handlers[7];
static unsigned handler_count;
static bool shutdown_registered;

esp_netif_t *esp_netif_new(const esp_netif_config_t *config) {
    ++netif_creates;
    bool ap = config->base == &_g_esp_netif_inherent_ap_config;
    CHECK(config->base == (ap ? &_g_esp_netif_inherent_ap_config :
                              &_g_esp_netif_inherent_sta_config) &&
          !config->driver && config->stack == (ap ? &ap_stack : &sta_stack),
          "exact_sdk_default_config_identity");
    if (fail_new) return NULL;
    esp_netif_t *netif = calloc(1, sizeof(*netif));
    CHECK(netif, "fixture_netif_allocation");
    netif->ap = ap;
    for (size_t i = 0; i < 4; ++i) if (!netifs[i]) { netifs[i] = netif; return netif; }
    CHECK(false, "fixture_netif_capacity");
    return NULL;
}

void esp_netif_destroy(esp_netif_t *netif) {
    CHECK(netif && !netif->clear_failed && !netif->driver_handle,
          "never_destroy_after_failed_clear");
    CHECK(netif->clear_called, "checked_driver_clear_before_netif_destroy");
    for (size_t i = 0; i < 4; ++i) if (netifs[i] == netif) {
        netifs[i] = NULL;
        ++netif_destroys;
        free(netif);
        return;
    }
    CHECK(false, "netif_destroy_exactly_once");
}

esp_err_t esp_event_handler_register(esp_event_base_t base, int32_t id,
                                    esp_event_handler_t handler, void *arg) {
    (void)base; (void)id;
    CHECK(handler && !arg, "sdk_default_callback_identity");
    ++register_calls;
    if (register_calls == fail_register_at) return TEST_REGISTER_ERROR;
    CHECK(handler_count < 7, "no_duplicate_default_registration");
    handlers[handler_count++] = handler;
    return ESP_OK;
}

esp_err_t esp_event_handler_unregister(esp_event_base_t base, int32_t id,
                                      esp_event_handler_t handler) {
    (void)base; (void)id;
    ++unregister_calls;
    for (size_t i = 0; i < handler_count; ++i) if (handlers[i] == handler) {
        handlers[i] = handlers[--handler_count];
        return ESP_OK;
    }
    return ESP_ERR_NOT_FOUND;
}

esp_err_t esp_register_shutdown_handler(shutdown_handler_t handler) {
    CHECK(handler, "shutdown_handler_identity");
    ++shutdown_registers;
    if (shutdown_result == ESP_OK || shutdown_result == ESP_ERR_INVALID_STATE)
        shutdown_registered = true;
    return shutdown_result;
}
esp_err_t esp_unregister_shutdown_handler(shutdown_handler_t handler) {
    CHECK(handler, "shutdown_unregister_identity");
    ++shutdown_unregisters;
    shutdown_registered = false;
    return ESP_OK;
}
esp_err_t esp_wifi_stop(void) { return ESP_OK; }
esp_err_t esp_wifi_internal_reg_rxcb(wifi_interface_t interface, void *callback) {
    CHECK((interface == WIFI_IF_STA || interface == WIFI_IF_AP) && !callback,
          "sdk_rx_callback_detach");
    ++rx_unregistrations;
    return ESP_OK;
}

#define HANDLER(name) static void name(void *arg, esp_event_base_t base, \
    int32_t id, void *data) { (void)arg; (void)base; (void)id; (void)data; }
HANDLER(wifi_default_action_sta_start)
HANDLER(wifi_default_action_sta_stop)
HANDLER(wifi_default_action_sta_connected)
HANDLER(wifi_default_action_sta_disconnected)
HANDLER(wifi_default_action_ap_start)
HANDLER(wifi_default_action_ap_stop)
HANDLER(wifi_default_action_sta_got_ip)
#undef HANDLER

static esp_err_t wifi_transmit(void *context, void *data, size_t size) {
    (void)context; (void)data; (void)size; return ESP_OK;
}
static esp_err_t wifi_transmit_wrap(void *context, void *data, size_t size, void *buffer) {
    (void)context; (void)data; (void)size; (void)buffer; return ESP_OK;
}
static void wifi_free(void *context, void *data) { (void)context; (void)data; }

// Only the fault injection is wrapped. The real setter and attach bodies run,
// including driver_handle publication before a failing post_attach callback.
#define esp_netif_set_driver_config actual_set_driver_config
#include "sdk-netif.inc"
#undef esp_netif_set_driver_config
esp_err_t esp_netif_set_driver_config(esp_netif_t *netif,
                                     const esp_netif_driver_ifconfig_t *config) {
    if (config && config->handle) {
        ++attach_configs;
        if (fail_post_attach) return TEST_DRIVER_ERROR;
    } else {
        ++clear_configs;
        if (fail_clear) return TEST_DRIVER_ERROR;
    }
    return actual_set_driver_config(netif, config);
}

#include "sdk-driver-struct.inc"
static void *driver_calloc(size_t count, size_t size) {
    ++driver_creates;
    CHECK(count == 1 && size == sizeof(struct wifi_netif_driver), "sdk_driver_allocation_shape");
    if (fail_driver) return NULL;
    void *driver = calloc(count, size);
    CHECK(driver, "fixture_driver_allocation");
    for (size_t i = 0; i < 4; ++i) if (!drivers[i]) { drivers[i] = driver; return driver; }
    CHECK(false, "fixture_driver_capacity");
    return NULL;
}
static void driver_free(void *driver) {
    if (!driver) return;
    for (size_t i = 0; i < 4; ++i) if (drivers[i] == driver) {
        drivers[i] = NULL;
        ++driver_destroys;
        free(driver);
        return;
    }
    CHECK(false, "driver_destroy_exactly_once");
}
static esp_netif_t *wifi_driver_netifs[MAX_WIFI_IFS];
#define s_wifi_netifs wifi_driver_netifs
#define calloc(...) driver_calloc(__VA_ARGS__)
#define free(...) driver_free(__VA_ARGS__)
#include "sdk-driver.inc"
#undef free
#undef calloc
#undef s_wifi_netifs

static esp_netif_t *s_wifi_netifs[MAX_WIFI_IFS];
static bool wifi_default_handlers_set;
static esp_err_t disconnect_and_destroy(esp_netif_t *netif);
#define esp_wifi_clear_default_wifi_driver_and_handlers actual_clear_default_driver
#include "sdk-default.inc"
#undef esp_wifi_clear_default_wifi_driver_and_handlers
esp_err_t esp_wifi_clear_default_wifi_driver_and_handlers(void *handle) {
    esp_netif_t *netif = handle;
    CHECK(!netif->clear_called, "failed_cleanup_never_repeated");
    netif->clear_called = true;
    ++clear_calls;
    esp_err_t result = actual_clear_default_driver(netif);
    netif->clear_failed = result != ESP_OK;
    return result;
}

#include "network_netif-production.c"

static void reset(void) {
    CHECK(!s_wifi_netifs[0] && !s_wifi_netifs[1] && !handler_count &&
          !wifi_default_handlers_set && !shutdown_registered,
          "all_owned_sdk_global_state_released");
    for (size_t i = 0; i < 4; ++i) {
        CHECK(!drivers[i], "all_drivers_released");
        // Deliberately retained netifs are process-lifetime production state.
        // Only the fixture releases their inert model storage at end-of-case,
        // without a second SDK clear or reading the freed driver pointer.
        if (netifs[i]) {
            CHECK(netifs[i]->clear_failed, "only_failed_cleanup_may_be_retained");
            free(netifs[i]); netifs[i] = NULL;
        }
    }
    memset(wifi_driver_netifs, 0, sizeof(wifi_driver_netifs));
    netif_creates = netif_destroys = driver_creates = driver_destroys = 0;
    attach_configs = clear_configs = clear_calls = register_calls = unregister_calls = 0;
    shutdown_registers = shutdown_unregisters = rx_unregistrations = 0;
    fail_new = fail_driver = fail_post_attach = fail_clear = false;
    fail_register_at = 0;
    shutdown_result = ESP_OK;
    ++cases;
}

static void released(const network_netif_t *owner) {
    CHECK(!owner->handle && !owner->cleanup_failed, "failed_create_has_no_usable_owner");
    CHECK(netif_destroys == 1U && clear_calls == 1U, "partial_netif_released_once");
    CHECK(!s_wifi_netifs[0] && !s_wifi_netifs[1] && !handler_count &&
          !wifi_default_handlers_set, "partial_sdk_globals_released");
}

static void retained(network_netif_t *owner) {
    CHECK(owner->handle && owner->cleanup_failed, "failed_cleanup_retains_partial_owner");
    CHECK(netif_destroys == 0 && clear_calls == 1U, "failed_cleanup_not_destroyed");
    unsigned before_clear = clear_calls, before_destroy = netif_destroys;
    CHECK(network_netif_release(owner) == ESP_ERR_INVALID_STATE,
          "retained_release_refuses_second_sdk_clear");
    CHECK(network_netif_create(owner, false) == ESP_ERR_INVALID_STATE,
          "retained_create_refuses_reuse");
    CHECK(clear_calls == before_clear && netif_destroys == before_destroy,
          "retained_owner_is_permanent");
}

int main(void) {
    reset();
    CHECK(network_netif_create(NULL, false) == ESP_ERR_INVALID_ARG &&
          network_netif_release(NULL) == ESP_ERR_INVALID_ARG, "null_argument_contract");
    network_netif_t empty = {0};
    CHECK(network_netif_release(&empty) == ESP_OK && !clear_calls && !netif_creates,
          "empty_release_idempotent");
    empty.cleanup_failed = true;
    CHECK(network_netif_create(&empty, false) == ESP_ERR_INVALID_STATE &&
          network_netif_release(&empty) == ESP_ERR_INVALID_STATE && !netif_creates,
          "invalid_nonzero_owner_contract");

    for (unsigned interface = 0; interface < 2; ++interface) {
        bool ap = interface != 0;
        reset(); network_netif_t owner = {0};
        fail_new = true;
        CHECK(network_netif_create(&owner, ap) == ESP_ERR_NO_MEM,
              "nullable_allocation_returns_no_memory");
        CHECK(!owner.handle && !owner.cleanup_failed && !clear_calls && !driver_creates,
              "allocation_failure_keeps_zero_owner");

        reset(); owner = (network_netif_t){0};
        CHECK(network_netif_create(&owner, ap) == ESP_OK && owner.handle &&
              !owner.cleanup_failed && owner.handle->ap == ap, "checked_create_success");
        CHECK(driver_creates == 1 && register_calls == 7 && handler_count == 7 &&
              shutdown_registers == 1 && wifi_default_handlers_set,
              "actual_sdk_attach_and_registration_ran");
        CHECK(owner.handle->driver_handle && owner.handle->driver_transmit == wifi_transmit &&
              owner.handle->driver_transmit_wrap == wifi_transmit_wrap &&
              owner.handle->driver_free_rx_buffer == wifi_free, "actual_post_attach_configured_driver");
        CHECK(network_netif_create(&owner, ap) == ESP_ERR_INVALID_STATE && netif_creates == 1,
              "occupied_owner_refuses_replacement");
        CHECK(network_netif_release(&owner) == ESP_OK, "successful_release");
        CHECK(network_netif_release(&owner) == ESP_OK && clear_calls == 1,
              "released_owner_idempotent");
        CHECK(driver_destroys == 1 && rx_unregistrations == 1,
              "actual_driver_destroy_and_rx_detach_ran");
        released(&owner);

        reset(); owner = (network_netif_t){0}; fail_driver = true;
        CHECK(network_netif_create(&owner, ap) == ESP_FAIL,
              "driver_allocation_failure_propagates");
        CHECK(!attach_configs && !driver_destroys && !register_calls,
              "null_driver_cleanup_is_safe");
        released(&owner);

        reset(); owner = (network_netif_t){0}; fail_post_attach = true;
        CHECK(network_netif_create(&owner, ap) == ESP_ERR_ESP_NETIF_DRIVER_ATTACH_FAILED,
              "actual_attach_failure_propagates");
        CHECK(attach_configs == 1 && driver_destroys == 1 && !register_calls,
              "partial_attach_driver_recovered_from_published_handle");
        released(&owner);

        for (unsigned point = 1; point <= 7; ++point) {
            reset(); owner = (network_netif_t){0}; fail_register_at = point;
            CHECK(network_netif_create(&owner, ap) == TEST_REGISTER_ERROR,
                  "registration_failure_propagates_original_error");
            CHECK(register_calls == point && driver_destroys == 1,
                  "actual_registration_rollback_ran");
            released(&owner);
        }

        reset(); owner = (network_netif_t){0}; shutdown_result = TEST_SHUTDOWN_ERROR;
        CHECK(network_netif_create(&owner, ap) == TEST_SHUTDOWN_ERROR,
              "shutdown_registration_failure_propagates");
        released(&owner);

        reset(); owner = (network_netif_t){0}; shutdown_result = ESP_ERR_INVALID_STATE;
        CHECK(network_netif_create(&owner, ap) == ESP_OK,
              "sdk_already_registered_shutdown_is_allowed");
        CHECK(network_netif_release(&owner) == ESP_OK, "already_shutdown_release");
        released(&owner);

        reset(); owner = (network_netif_t){0};
        CHECK(network_netif_create(&owner, ap) == ESP_OK, "setup_clear_failure");
        fail_clear = true;
        CHECK(network_netif_release(&owner) == TEST_DRIVER_ERROR,
              "clear_failure_propagates");
        CHECK(driver_destroys == 1, "sdk_frees_driver_even_when_clear_returns_error");
        retained(&owner);

        reset(); owner = (network_netif_t){0}; fail_post_attach = fail_clear = true;
        CHECK(network_netif_create(&owner, ap) == ESP_ERR_ESP_NETIF_DRIVER_ATTACH_FAILED,
              "create_preserves_original_error_when_cleanup_fails");
        CHECK(driver_destroys == 1, "failed_attach_cleanup_driver_freed_once");
        retained(&owner);

        reset(); owner = (network_netif_t){0}; fail_register_at = 3; fail_clear = true;
        CHECK(network_netif_create(&owner, ap) == TEST_REGISTER_ERROR,
              "register_error_preserved_when_cleanup_fails");
        retained(&owner);
    }

    for (unsigned first = 0; first < 2; ++first) {
        reset(); network_netif_t a = {0}, b = {0};
        CHECK(network_netif_create(&a, first != 0) == ESP_OK &&
              network_netif_create(&b, first == 0) == ESP_OK, "sta_ap_pair_create");
        CHECK(register_calls == 7 && handler_count == 7 && driver_creates == 2,
              "shared_default_handlers_registered_once");
        CHECK(network_netif_release(&a) == ESP_OK && !a.handle && b.handle,
              "release_only_owns_one_netif");
        CHECK(handler_count == 7 && !unregister_calls && wifi_default_handlers_set,
              "other_interface_keeps_default_handlers");
        CHECK(network_netif_release(&b) == ESP_OK && !b.handle,
              "last_interface_releases_default_handlers");
        CHECK(!handler_count && !wifi_default_handlers_set && driver_destroys == 2 &&
              netif_destroys == 2, "pair_fully_released_once");
    }
    unsigned completed = cases;
    reset();
    printf("PASS checked CYD netifs: %u cases; actual pinned SDK attach/post-attach/default-handler rollback/driver cleanup, STA/AP ownership, allocation and registration failures, permanently retained failed cleanup\n", completed);
    return 0;
}
