#include "native_time_sntp_internal.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "lwip/apps/sntp.h"

static bool s_bound;
static native_time_sntp_config_t s_banks[2];
static unsigned s_bound_bank;

static bool references_bank(const char *name, unsigned bank) {
    uintptr_t pointer = (uintptr_t)name;
    uintptr_t start = (uintptr_t)&s_banks[bank];
    return name && pointer >= start && pointer < start + sizeof(s_banks[bank]);
}

static bool bank_referenced(unsigned bank) {
    for (unsigned index = 0; index < SNTP_MAX_SERVERS; ++index) {
        if (references_bank(sntp_getservername((uint8_t)index), bank))
            return true;
    }
    return false;
}

static bool same_config(const native_time_sntp_config_t *left,
                        const native_time_sntp_config_t *right) {
    if (left->server_count != right->server_count ||
        left->sync_interval_minutes != right->sync_interval_minutes) return false;
    for (unsigned index = 0; index < left->server_count; ++index) {
        if (strcmp(left->servers[index], right->servers[index]) != 0) return false;
    }
    return true;
}

esp_err_t native_time_sntp_context_unused(void *context) {
    (void)context;
    if (sntp_enabled()) return ESP_ERR_INVALID_STATE;
    // This component owns the singleton. Do not silently take a foreign raw
    // client's names; managed init independently rejects foreign storage.
    for (unsigned index = 0; index < SNTP_MAX_SERVERS; ++index) {
        if (sntp_getservername((uint8_t)index)) return ESP_ERR_INVALID_STATE;
    }
    return ESP_OK;
}

esp_err_t native_time_sntp_context_apply(void *context) {
    const native_time_sntp_config_t *config = context;
    if (s_bound && sntp_enabled() &&
        same_config(&s_banks[s_bound_bank], config)) return ESP_OK;

    unsigned bank = s_bound ? (s_bound_bank ^ 1U) : 0U;
    // Check every configured SDK slot, including unused slots after 2 -> 1.
    // DNS copies a hostname synchronously into its own entry on enqueue.
    // No TCP/IP callback can interleave this check/copy/rebind sequence.
    if (bank_referenced(bank)) {
        bank ^= 1U;
        if (bank_referenced(bank)) return ESP_ERR_INVALID_STATE;
    }
    native_time_sntp_config_t *destination = &s_banks[bank];
    memset(destination, 0, sizeof(*destination));
    destination->server_count = config->server_count;
    destination->sync_interval_minutes = config->sync_interval_minutes;
    for (unsigned index = 0; index < config->server_count; ++index) {
        size_t size = strlen(config->servers[index]) + 1U;
        memcpy(destination->servers[index], config->servers[index], size);
    }

    sntp_stop();
    if (sntp_enabled()) return ESP_ERR_INVALID_STATE;
    for (unsigned index = 0; index < SNTP_MAX_SERVERS; ++index) {
        // setservername(NULL) alone leaves a previously resolved IP usable.
        sntp_setserver((uint8_t)index, NULL);
    }
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    native_time_sntp_context_interval((uint32_t)config->sync_interval_minutes * 60000U);
    for (unsigned index = 0; index < config->server_count; ++index) {
        sntp_setservername((uint8_t)index, destination->servers[index]);
    }
    // Track borrowed storage even if the public void init cannot start.
    s_bound_bank = bank;
    s_bound = true;
    sntp_init();
    return sntp_enabled() ? ESP_OK : ESP_ERR_NO_MEM;
}

esp_err_t native_time_sntp_context_restart(void *context) {
    (void)context;
    if (!s_bound) return ESP_ERR_INVALID_STATE;
    sntp_stop();
    sntp_init();
    return sntp_enabled() ? ESP_OK : ESP_ERR_NO_MEM;
}

