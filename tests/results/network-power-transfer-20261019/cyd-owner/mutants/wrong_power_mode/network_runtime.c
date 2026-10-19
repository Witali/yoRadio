#include "network_runtime.h"

#include <limits.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>

#include "board_config.h"
#include "esp_event.h"
#include "esp_mac.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "esp_wifi_default.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "native_wifi_store.h"
#include "native_network_power.h"
#include "network_netif.h"
#include "time_service.h"

#define EVENT_SLOTS 16U
#define OWNER_POLL_MS 100U
#define ATTEMPT_US 20000000LL
#define CYCLE_US 300000000LL
#define DISCONNECT_US 2000000LL
#define RETRY_US 250000LL
#define PORTAL_US 20000000LL
#define RSSI_US 2000000LL
#define INITIAL_READY BIT0
#define INITIAL_FAILED BIT1

typedef enum { NOTICE_START, NOTICE_CONNECTED, NOTICE_DISCONNECTED,
               NOTICE_IP, NOTICE_LOST_IP } notice_kind_t;
typedef struct {
    notice_kind_t kind;
    uint16_t reason;
    uint32_t ip;
    esp_netif_t *netif;
} network_notice_t;

typedef struct {
    QueueHandle_t events;
    SemaphoreHandle_t lock;
    EventGroupHandle_t initial;
    TaskHandle_t task;
    esp_event_handler_instance_t wifi_handler, ip_handler;
    bool wifi_registered, ip_registered;
    native_state_t *state;
    esp_netif_t *station;
    network_netif_t ap;
    network_profiles_t profiles;
    network_snapshot_t view, published;
    uint32_t published_link_version;
    uint8_t cycle_first, last_success;
    bool started, cycle_active, manual_cycle, association_seen, time_online;
    bool projection_dirty;
    unsigned ap_attempts;
    int64_t boot_deadline, cycle_deadline, attempt_deadline;
    int64_t disconnect_deadline, next_action, ap_next, rssi_next;
} network_owner_t;

static network_owner_t s_owner;
// Lifecycle and callback references survive object teardown/recreation.
enum { RUNTIME_OFF, RUNTIME_STARTING, RUNTIME_RUNNING, RUNTIME_RETAINED, RUNTIME_STOPPING };
#define GATE_CLOSED (UINT_MAX / 2U + 1U)
// One atomic modification order owns both admission and references: closing
// cannot miss a caller that successfully entered the same object lifetime.
static atomic_uint s_lifecycle, s_gate = ATOMIC_VAR_INIT(GATE_CLOSED);
static atomic_uint s_link_version, s_overflows;
static atomic_bool s_stop, s_exited, s_retry, s_manual_admitted, s_resync;

static int64_t after(int64_t now, int64_t delay) {
    return now > INT64_MAX - delay ? INT64_MAX : now + delay;
}

static bool enter(void) {
    unsigned value = atomic_load_explicit(&s_gate, memory_order_acquire);
    while (!(value & GATE_CLOSED) && value < GATE_CLOSED - 1U) {
        if (atomic_compare_exchange_weak_explicit(&s_gate, &value, value + 1U,
                memory_order_acq_rel, memory_order_acquire)) return true;
    }
    return false;
}

static void leave(void) {
    atomic_fetch_sub_explicit(&s_gate, 1, memory_order_release);
}

static void event_handler(void *arg, esp_event_base_t base, int32_t id, void *data) {
    (void)arg;
    network_notice_t notice = {0};
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) notice.kind = NOTICE_START;
    else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_CONNECTED) notice.kind = NOTICE_CONNECTED;
    else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        notice.kind = NOTICE_DISCONNECTED;
        if (data) notice.reason = ((wifi_event_sta_disconnected_t *)data)->reason;
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        if (!data) return;
        const ip_event_got_ip_t *ip = data;
        notice.kind = NOTICE_IP;
        notice.netif = ip->esp_netif;
        notice.ip = ip->ip_info.ip.addr;
    } else if (base == IP_EVENT && id == IP_EVENT_STA_LOST_IP) notice.kind = NOTICE_LOST_IP;
    else return;
    if (!enter()) return;
    atomic_fetch_add_explicit(&s_link_version, 1, memory_order_release);
    if (xQueueSend(s_owner.events, &notice, 0) != pdTRUE) {
        atomic_fetch_add_explicit(&s_overflows, 1, memory_order_relaxed);
        atomic_store_explicit(&s_resync, true, memory_order_release);
    }
    leave();
}

static void offline(network_owner_t *owner) {
    owner->view.online = false;
    owner->view.ipv4 = 0;
    owner->view.rssi = 0;
    owner->view.rssi_valid = false;
    owner->view.rssi_updated_us = 0;
    if (owner->time_online) {
        time_service_notify_network(false);
        owner->time_online = false;
    }
    owner->projection_dirty = true;
}

static bool same_profile(const network_owner_t *owner, const wifi_ap_record_t *ap) {
    if (owner->view.profile_index >= owner->profiles.count) return false;
    const char *ssid = owner->profiles.rows[owner->view.profile_index].ssid;
    size_t size = strlen(ssid);
    return size < sizeof(ap->ssid) && !memcmp(ap->ssid, ssid, size) && !ap->ssid[size];
}

// Read actual association and the live netif, never only cached disconnected IP.
// Default DHCP netif_down clears the address in both pinned SDKs. SDK events do
// not contain our epoch; they are hints and cannot cancel a newer SDK operation.
static bool observe(network_owner_t *owner, wifi_ap_record_t *ap, uint32_t *ip) {
    uint32_t version = atomic_load_explicit(&s_link_version, memory_order_acquire);
    if (esp_wifi_sta_get_ap_info(ap) != ESP_OK || !same_profile(owner, ap) ||
        !esp_netif_is_netif_up(owner->station)) return false;
    esp_netif_ip_info_t info = {0};
    if (esp_netif_get_ip_info(owner->station, &info) != ESP_OK || !info.ip.addr ||
        version != atomic_load_explicit(&s_link_version, memory_order_acquire)) return false;
    *ip = info.ip.addr;
    return true;
}

static void online(network_owner_t *owner, const wifi_ap_record_t *ap,
                   uint32_t ip, int64_t now) {
    owner->view.online = true;
    owner->view.ipv4 = ip;
    owner->view.phase = NETWORK_ONLINE;
    owner->view.rssi = ap->rssi;
    owner->view.rssi_valid = true;
    owner->view.rssi_updated_us = (uint64_t)now;
    owner->view.last_error = ESP_OK;
    owner->last_success = owner->view.profile_index;
    owner->cycle_active = false;
    if (owner->manual_cycle) {
        owner->manual_cycle = false;
        atomic_store_explicit(&s_manual_admitted, false, memory_order_release);
    }
    owner->association_seen = true;
    owner->rssi_next = after(now, RSSI_US);
    if (!owner->time_online) {
        time_service_notify_network(true);
        owner->time_online = true;
    }
    owner->projection_dirty = true;
    xEventGroupSetBits(owner->initial, INITIAL_READY);
}

static esp_err_t prepare_portal(network_owner_t *owner) {
    uint8_t mac[6];
    wifi_config_t config = {0};
    esp_err_t result = esp_read_mac(mac, ESP_MAC_WIFI_SOFTAP);
    if (result == ESP_OK) {
        snprintf((char *)config.ap.ssid, sizeof(config.ap.ssid), "yoRadio-%02X%02X%02X",
                 mac[3], mac[4], mac[5]);
        config.ap.ssid_len = (uint8_t)strlen((char *)config.ap.ssid);
        config.ap.channel = 1;
        config.ap.max_connection = 4;
        config.ap.authmode = WIFI_AUTH_OPEN;
        result = network_netif_create(&owner->ap, true);
    }
    // Prepare the exact AP configuration while Wi-Fi is stopped. Enabling
    // APSTA later must not briefly start a retained/default AP configuration.
    if (result == ESP_OK) result = esp_wifi_set_mode(WIFI_MODE_APSTA);
    if (result == ESP_OK) result = esp_wifi_set_config(WIFI_IF_AP, &config);
    esp_err_t restore = esp_wifi_set_mode(WIFI_MODE_STA);
    return result == ESP_OK ? restore : result;
}

static void enable_portal(network_owner_t *owner, int64_t now) {
    if (owner->view.ap_enabled || owner->ap_attempts >= 3 || now < owner->ap_next) return;
    ++owner->ap_attempts;
    esp_err_t result = esp_wifi_set_mode(WIFI_MODE_APSTA);
    if (result == ESP_OK) {
        owner->view.ap_enabled = true;
        owner->projection_dirty = true;
        xEventGroupSetBits(owner->initial, INITIAL_READY);
    } else {
        owner->view.last_error = result;
        owner->ap_next = after(now, RETRY_US);
        if (owner->ap_attempts == 3) xEventGroupSetBits(owner->initial, INITIAL_FAILED);
    }
}

static void finish_cycle(network_owner_t *owner, int64_t now) {
    owner->cycle_active = false;
    if (owner->manual_cycle) {
        owner->manual_cycle = false;
        atomic_store_explicit(&s_manual_admitted, false, memory_order_release);
    }
    offline(owner);
    owner->view.phase = NETWORK_AP_IDLE;
    // Cancel our last pending attempt; a later event is still reconciled with
    // actual driver/netif state, not labeled with a made-up SDK generation.
    esp_err_t result = esp_wifi_disconnect();
    if (result != ESP_OK && result != ESP_ERR_WIFI_NOT_CONNECT)
        owner->view.last_error = result;
    enable_portal(owner, now);
}

static void disconnect_before_attempt(network_owner_t *owner, int64_t now) {
    offline(owner);
    owner->association_seen = false;
    owner->view.phase = NETWORK_WAIT_DISCONNECT;
    owner->next_action = after(now, 100000LL);
    owner->disconnect_deadline = after(now, DISCONNECT_US);
    esp_err_t result = esp_wifi_disconnect();
    if (result != ESP_OK && result != ESP_ERR_WIFI_NOT_CONNECT)
        owner->view.last_error = result;
}

static void begin_cycle(network_owner_t *owner, uint8_t first, int64_t now) {
    ++owner->view.epoch;
    owner->view.attempt = 0;
    owner->view.profiles_tried = 0;
    owner->cycle_first = first;
    owner->view.target_profile = first;
    owner->cycle_active = true;
    owner->cycle_deadline = after(now, CYCLE_US);
    disconnect_before_attempt(owner, now);
}

static void failed_attempt(network_owner_t *owner, esp_err_t error, int64_t now) {
    owner->view.last_error = error;
    offline(owner);
    if (owner->view.attempt >= 3) {
        ++owner->view.profiles_tried;
        owner->view.attempt = 0;
        if (owner->view.profiles_tried >= owner->profiles.count) {
            finish_cycle(owner, now);
            return;
        }
        owner->view.target_profile = (uint8_t)((owner->cycle_first +
            owner->view.profiles_tried) % owner->profiles.count);
    }
    owner->view.phase = NETWORK_RETRY_WAIT;
    owner->next_action = after(now, RETRY_US);
}

static void configure_attempt(network_owner_t *owner, int64_t now) {
    wifi_ap_record_t ap;
    esp_err_t result = esp_wifi_sta_get_ap_info(&ap);
    if (result == ESP_OK) {
        if (now < owner->disconnect_deadline) return;
        ++owner->view.attempt;
        failed_attempt(owner, ESP_ERR_TIMEOUT, now);
        return;
    }
    if (result != ESP_ERR_WIFI_NOT_CONNECT) {
        if (now < owner->disconnect_deadline) return;
        ++owner->view.attempt;
        failed_attempt(owner, result, now);
        return;
    }
    wifi_config_t config = {0};
    const network_profile_t *profile = &owner->profiles.rows[owner->view.target_profile];
    memcpy(config.sta.ssid, profile->ssid, sizeof(profile->ssid));
    memcpy(config.sta.password, profile->password, sizeof(profile->password));
    config.sta.threshold.authmode = WIFI_AUTH_OPEN;
    config.sta.pmf_cfg.capable = true;
    config.sta.pmf_cfg.required = false;
    result = esp_wifi_set_config(WIFI_IF_STA, &config);
    native_wifi_erase(&config, sizeof(config));
    if (result == ESP_ERR_WIFI_STATE && now < owner->disconnect_deadline) return;
    ++owner->view.attempt;
    if (result != ESP_OK) { failed_attempt(owner, result, now); return; }
    // A failed set_config must not publish a selection the driver never took.
    owner->view.profile_index = owner->view.target_profile;
    result = esp_wifi_connect();
    if (result != ESP_OK) { failed_attempt(owner, result, now); return; }
    owner->view.phase = NETWORK_CONNECTING;
    owner->attempt_deadline = after(now, ATTEMPT_US);
}

static void handle_notice(network_owner_t *owner, const network_notice_t *notice,
                          int64_t now) {
    if (notice->kind == NOTICE_START) {
        if (owner->started) return;
        owner->started = true;
        if (owner->profiles.count) begin_cycle(owner, 0, now);
        else { owner->view.phase = NETWORK_AP_IDLE; enable_portal(owner, now); }
        return;
    }
    wifi_ap_record_t ap = {0};
    uint32_t ip = 0;
    bool valid = observe(owner, &ap, &ip);
    if (notice->kind == NOTICE_IP) {
        if (notice->netif == owner->station && notice->ip && notice->ip == ip && valid &&
            owner->view.phase != NETWORK_WAIT_DISCONNECT &&
            owner->view.phase != NETWORK_RETRY_WAIT) online(owner, &ap, ip, now);
        return;
    }
    if (notice->kind == NOTICE_CONNECTED) {
        if (esp_wifi_sta_get_ap_info(&ap) == ESP_OK && same_profile(owner, &ap))
            owner->association_seen = true;
        return;
    }
    if (notice->kind == NOTICE_DISCONNECTED) owner->view.disconnect_reason = notice->reason;
    if (valid) {
        // An old queued loss cannot invalidate a currently observed live link.
        if (owner->view.online) online(owner, &ap, ip, now);
        return;
    }
    bool was_online = owner->view.online;
    offline(owner);
    // A queued loss from an older attempt can arrive while the currently
    // associated station is still waiting for DHCP. Missing IP is not proof
    // that that association was disconnected, even for duplicate SSIDs.
    if (esp_wifi_sta_get_ap_info(&ap) == ESP_OK && same_profile(owner, &ap)) {
        owner->association_seen = true;
        if (was_online) {
            ++owner->view.epoch;
            owner->cycle_first = owner->last_success;
            owner->view.target_profile = owner->last_success;
            owner->view.attempt = 1;
            owner->view.profiles_tried = 0;
            owner->cycle_active = true;
            owner->cycle_deadline = after(now, CYCLE_US);
            owner->attempt_deadline = after(now, ATTEMPT_US);
            owner->view.phase = NETWORK_CONNECTING;
        }
        return;
    }
    if (was_online) {
        begin_cycle(owner, owner->last_success, now);
    } else if (owner->view.phase == NETWORK_CONNECTING && owner->association_seen) {
        failed_attempt(owner, ESP_FAIL, now);
    }
    // Before first association a disconnect is ambiguous (SDK has no epoch).
    // Keep this attempt's deadline instead of charging a newer attempt for it.
}

static void publish(network_owner_t *owner, int64_t now, uint32_t observed_version) {
    bool fresh = observed_version == atomic_load_explicit(&s_link_version, memory_order_acquire) &&
                 !atomic_load_explicit(&s_resync, memory_order_acquire);
    if (!fresh && owner->view.online) {
        if (owner->time_online) {
            time_service_notify_network(false);
            owner->time_online = false;
        }
        owner->rssi_next = after(now, 100000LL);
        owner->projection_dirty = true;
    }
    owner->view.updated_us = (uint64_t)now;
    owner->view.event_overflows = atomic_load_explicit(&s_overflows, memory_order_relaxed);
    if (xSemaphoreTake(owner->lock, 0) == pdTRUE) {
        owner->published = owner->view;
        owner->published_link_version = observed_version;
        xSemaphoreGive(owner->lock);
    }
    native_network_mode_t mode = owner->view.online && fresh ? NATIVE_NETWORK_CLIENT :
        owner->view.ap_enabled ? NATIVE_NETWORK_ACCESS_POINT : NATIVE_NETWORK_STARTING;
    if (owner->projection_dirty && native_state_set_network_status(owner->state,
        mode, fresh ? owner->view.ipv4 : 0, owner->view.ap_enabled,
        fresh && owner->view.rssi_valid, fresh ? owner->view.rssi : 0)) owner->projection_dirty = false;
}

static esp_err_t apply_power(void *context, bool active) {
    (void)context;
    return esp_wifi_set_ps(active ? WIFI_PS_MIN_MODEM : WIFI_PS_NONE);
}

static void owner_step(network_owner_t *owner, int64_t now) {
    uint32_t version = atomic_load_explicit(&s_link_version, memory_order_acquire);
    network_notice_t notice;
    // Bounded drain: an event storm cannot starve deadlines/manual requests.
    for (unsigned i = 0; i < EVENT_SLOTS && xQueueReceive(owner->events, &notice, 0) == pdTRUE; ++i)
        handle_notice(owner, &notice, now);
    if (!owner->started && now >= owner->boot_deadline) {
        wifi_ap_record_t ap = {0};
        esp_err_t result = esp_wifi_sta_get_ap_info(&ap);
        if (result == ESP_OK || result == ESP_ERR_WIFI_NOT_CONNECT) {
            network_notice_t start = {.kind = NOTICE_START};
            handle_notice(owner, &start, now);
        } else {
            owner->view.last_error = result;
            xEventGroupSetBits(owner->initial, INITIAL_FAILED);
        }
    }
    if (atomic_exchange_explicit(&s_resync, false, memory_order_acq_rel)) {
        wifi_ap_record_t ap = {0}; uint32_t ip = 0;
        bool was_online = owner->view.online;
        offline(owner);
        if (observe(owner, &ap, &ip) && owner->view.phase != NETWORK_WAIT_DISCONNECT &&
            owner->view.phase != NETWORK_RETRY_WAIT) online(owner, &ap, ip, now);
        else if (was_online) begin_cycle(owner, owner->last_success, now);
        if (!owner->started && esp_wifi_sta_get_ap_info(&ap) == ESP_ERR_WIFI_NOT_CONNECT) {
            network_notice_t start = {.kind = NOTICE_START};
            handle_notice(owner, &start, now);
        }
    }
    if (owner->started && atomic_exchange_explicit(&s_retry, false, memory_order_acq_rel)) {
        owner->ap_attempts = 0;
        owner->ap_next = now;
        owner->manual_cycle = true;
        if (owner->profiles.count) begin_cycle(owner, 0, now);
    }
    if (owner->started) {
        native_network_power_poll(now, apply_power, NULL);
        if (!owner->view.online && (now >= owner->boot_deadline || !owner->profiles.count))
            enable_portal(owner, now);
        if (owner->cycle_active && now >= owner->cycle_deadline) {
            owner->view.last_error = ESP_ERR_TIMEOUT;
            finish_cycle(owner, now);
        } else if (owner->view.phase == NETWORK_RETRY_WAIT && now >= owner->next_action) {
            disconnect_before_attempt(owner, now);
        } else if (owner->view.phase == NETWORK_WAIT_DISCONNECT && now >= owner->next_action) {
            configure_attempt(owner, now);
        } else if (owner->view.phase == NETWORK_CONNECTING && now >= owner->attempt_deadline) {
            failed_attempt(owner, ESP_ERR_TIMEOUT, now);
        }
        if (owner->view.online && now >= owner->rssi_next) {
            wifi_ap_record_t ap = {0}; uint32_t ip = 0;
            if (observe(owner, &ap, &ip)) online(owner, &ap, ip, now);
            else {
                owner->view.rssi = 0; owner->view.rssi_valid = false;
                owner->projection_dirty = true;
                owner->rssi_next = after(now, RSSI_US);
                // A transient RSSI query error is not an instruction to
                // disconnect a healthy station. Confirm actual link loss.
                esp_err_t result = esp_wifi_sta_get_ap_info(&ap);
                if (result == ESP_ERR_WIFI_NOT_CONNECT ||
                    !esp_netif_is_netif_up(owner->station)) {
                    offline(owner); begin_cycle(owner, owner->last_success, now);
                }
            }
        }
    }
    publish(owner, now, version);
}

static void owner_task(void *argument) {
    network_owner_t *owner = argument;
    while (!atomic_load_explicit(&s_stop, memory_order_acquire)) {
        owner_step(owner, esp_timer_get_time());
        vTaskDelay(pdMS_TO_TICKS(OWNER_POLL_MS));
    }
    offline(owner);
    atomic_store_explicit(&s_exited, true, memory_order_release);
    vTaskDelete(NULL);
}

static esp_err_t unregister_handlers(network_owner_t *owner) {
    esp_err_t result = ESP_OK, current;
    if (owner->wifi_registered) {
        current = esp_event_handler_instance_unregister(WIFI_EVENT, ESP_EVENT_ANY_ID, owner->wifi_handler);
        if (current == ESP_OK) owner->wifi_registered = false; else result = current;
    }
    if (owner->ip_registered) {
        current = esp_event_handler_instance_unregister(IP_EVENT, ESP_EVENT_ANY_ID, owner->ip_handler);
        if (current == ESP_OK) owner->ip_registered = false; else result = current;
    }
    return result;
}

static esp_err_t release_objects(network_owner_t *owner) {
    esp_err_t result = network_netif_release(&owner->ap);
    if (result != ESP_OK) {
        atomic_store(&s_lifecycle, RUNTIME_RETAINED);
        return result;
    }
    if (owner->events) vQueueDelete(owner->events);
    if (owner->initial) vEventGroupDelete(owner->initial);
    if (owner->lock) vSemaphoreDelete(owner->lock);
    native_wifi_erase(&owner->profiles, sizeof(owner->profiles));
    memset(owner, 0, sizeof(*owner));
    atomic_store_explicit(&s_lifecycle, RUNTIME_OFF, memory_order_release);
    return ESP_OK;
}

esp_err_t network_runtime_start(native_state_t *state, esp_netif_t *station,
                                const network_profiles_t *profiles) {
    if (!state || !state->lock || !station || !profiles || profiles->count > NETWORK_PROFILES_MAX)
        return ESP_ERR_INVALID_ARG;
    for (uint8_t i = 0; i < profiles->count; ++i) {
        if (!profiles->rows[i].ssid[0] ||
            strnlen(profiles->rows[i].ssid, sizeof(profiles->rows[i].ssid)) == sizeof(profiles->rows[i].ssid) ||
            strnlen(profiles->rows[i].password, sizeof(profiles->rows[i].password)) == sizeof(profiles->rows[i].password))
            return ESP_ERR_INVALID_ARG;
    }
    unsigned expected = RUNTIME_OFF;
    if (!atomic_compare_exchange_strong(&s_lifecycle, &expected, RUNTIME_STARTING))
        return ESP_ERR_INVALID_STATE;
    network_owner_t *owner = &s_owner;
    memset(owner, 0, sizeof(*owner));
    owner->state = state; owner->station = station; owner->profiles = *profiles;
    owner->view.profile_count = profiles->count;
    owner->view.profile_index = owner->view.target_profile = NETWORK_NO_PROFILE;
    owner->view.phase = NETWORK_WAIT_START;
    owner->projection_dirty = true;
    owner->boot_deadline = after(esp_timer_get_time(), PORTAL_US);
    owner->published = owner->view;
    owner->published_link_version = atomic_load(&s_link_version);
    owner->events = xQueueCreate(EVENT_SLOTS, sizeof(network_notice_t));
    owner->lock = xSemaphoreCreateMutex();
    owner->initial = xEventGroupCreate();
    esp_err_t result = ESP_ERR_NO_MEM;
    if (!owner->events || !owner->lock || !owner->initial) goto failed;
    result = prepare_portal(owner);
    if (result != ESP_OK) goto failed;
    result = esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL, &owner->wifi_handler);
    if (result != ESP_OK) goto failed;
    owner->wifi_registered = true;
    result = esp_event_handler_instance_register(IP_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL, &owner->ip_handler);
    if (result != ESP_OK) goto failed;
    owner->ip_registered = true;
    atomic_store(&s_stop, false); atomic_store(&s_exited, false);
    atomic_store(&s_retry, false); atomic_store(&s_manual_admitted, false);
    atomic_store(&s_resync, false); atomic_store(&s_overflows, 0);
    native_network_power_invalidate();
    if (xTaskCreatePinnedToCore(owner_task, "wifi_runtime", BOARD_TASK_STACK_WIFI_RUNTIME,
            owner, 2, &owner->task, 0) != pdPASS) { result = ESP_ERR_NO_MEM; goto failed; }
    atomic_store_explicit(&s_gate, 0, memory_order_release);
    atomic_store_explicit(&s_lifecycle, RUNTIME_RUNNING, memory_order_release);
    return ESP_OK;
failed:
    if (unregister_handlers(owner) == ESP_OK) release_objects(owner);
    else atomic_store(&s_lifecycle, RUNTIME_RETAINED);
    return result;
}

esp_err_t network_runtime_wait_initial(uint32_t timeout_ms) {
    if (!enter()) return ESP_ERR_INVALID_STATE;
    EventBits_t bits = xEventGroupWaitBits(s_owner.initial, INITIAL_READY | INITIAL_FAILED,
        pdFALSE, pdFALSE, pdMS_TO_TICKS(timeout_ms));
    leave();
    return bits & INITIAL_READY ? ESP_OK : bits & INITIAL_FAILED ? ESP_FAIL : ESP_ERR_TIMEOUT;
}

esp_err_t network_runtime_retry(void) {
    if (!enter()) return ESP_ERR_INVALID_STATE;
    esp_err_t result;
    bool expected = false;
    if (!s_owner.profiles.count) result = ESP_ERR_NOT_FOUND;
    else if (atomic_compare_exchange_strong(&s_manual_admitted, &expected, true)) {
        atomic_store_explicit(&s_retry, true, memory_order_release);
        result = ESP_OK;
    } else result = ESP_ERR_TIMEOUT;
    leave();
    return result;
}

esp_err_t network_runtime_snapshot(network_snapshot_t *out, uint32_t timeout_ms) {
    if (!out) return ESP_ERR_INVALID_ARG;
    if (!enter()) return ESP_ERR_INVALID_STATE;
    network_snapshot_t snapshot;
    uint32_t version;
    if (xSemaphoreTake(s_owner.lock, pdMS_TO_TICKS(timeout_ms)) != pdTRUE) {
        leave(); return ESP_ERR_TIMEOUT;
    }
    snapshot = s_owner.published; version = s_owner.published_link_version;
    xSemaphoreGive(s_owner.lock);
    if (version != atomic_load_explicit(&s_link_version, memory_order_acquire) ||
        atomic_load_explicit(&s_resync, memory_order_acquire)) {
        snapshot.online = snapshot.rssi_valid = false;
        snapshot.ipv4 = 0; snapshot.rssi = 0; snapshot.reconciling = true;
    }
    int64_t now = esp_timer_get_time();
    snapshot.rssi_age_ms = snapshot.rssi_valid && now >= 0 &&
        (uint64_t)now >= snapshot.rssi_updated_us ? ((uint64_t)now - snapshot.rssi_updated_us) / 1000 : 0;
    native_network_power_snapshot(&snapshot.power);
    *out = snapshot;
    leave();
    return ESP_OK;
}

esp_err_t network_runtime_stop(uint32_t timeout_ms) {
    unsigned lifecycle = atomic_load_explicit(&s_lifecycle, memory_order_acquire);
    if (lifecycle == RUNTIME_OFF) return ESP_OK;
    if (lifecycle == RUNTIME_STARTING || lifecycle == RUNTIME_STOPPING ||
        !atomic_compare_exchange_strong(&s_lifecycle, &lifecycle, RUNTIME_STOPPING))
        return ESP_ERR_INVALID_STATE;
    atomic_fetch_or_explicit(&s_gate, GATE_CLOSED, memory_order_acq_rel);
    int64_t deadline = after(esp_timer_get_time(), (int64_t)timeout_ms * 1000);
    esp_err_t result = unregister_handlers(&s_owner);
    while (atomic_load_explicit(&s_gate, memory_order_acquire) != GATE_CLOSED) {
        if (esp_timer_get_time() >= deadline) {
            atomic_store(&s_lifecycle, RUNTIME_RETAINED); return ESP_ERR_TIMEOUT;
        }
        vTaskDelay(1);
    }
    atomic_store_explicit(&s_stop, true, memory_order_release);
    while (s_owner.task && !atomic_load_explicit(&s_exited, memory_order_acquire)) {
        if (esp_timer_get_time() >= deadline) {
            atomic_store(&s_lifecycle, RUNTIME_RETAINED); return ESP_ERR_TIMEOUT;
        }
        vTaskDelay(1);
    }
    if (result != ESP_OK) { atomic_store(&s_lifecycle, RUNTIME_RETAINED); return result; }
    return release_objects(&s_owner);
}
