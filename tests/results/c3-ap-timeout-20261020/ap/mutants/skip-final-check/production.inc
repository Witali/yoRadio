#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAILED_BIT BIT1
#define WIFI_RETRIES_PER_CREDENTIAL 2
#define WIFI_MAX_CREDENTIALS 5
#define WIFI_RSSI_INTERVAL_MS 2000

static const char *const TAG = "network";
static EventGroupHandle_t s_wifi_events;
static esp_netif_t *s_station_netif;
static esp_netif_t *s_ap_netif;
static native_state_t *s_state;
static wifi_config_t s_station_config;
static wifi_config_t s_credentials[WIFI_MAX_CREDENTIALS];
static size_t s_credential_count;
static size_t s_credential_index;
static int s_retries;
static bool s_have_credentials;
static atomic_bool s_stopping_for_sleep;

// AP expiry has one deadline owner: the existing RSSI task. These short facts
// describe concurrent SDK operations; SDK calls never run under this mux.
typedef struct {
    uint64_t version;
    unsigned operations;
    bool valid, started, enabled, online, pending;
    int64_t pending_until;
} softap_facts_t;
typedef struct {
    bool armed, saturated;
    uint32_t revision;
    uint64_t version;
    int64_t deadline;
} softap_policy_t;
static portMUX_TYPE s_softap_lock = portMUX_INITIALIZER_UNLOCKED;
static softap_facts_t s_softap = {.valid = true};

static int64_t softap_after(int64_t now, int64_t interval) {
    return now > INT64_MAX - interval ? INT64_MAX : now + interval;
}
static void softap_changed_locked(void) {
    if (s_softap.version == UINT64_MAX) s_softap.valid = false;
    else ++s_softap.version;
}
static void softap_operation(bool begin) {
    portENTER_CRITICAL(&s_softap_lock);
    if (begin) ++s_softap.operations; else --s_softap.operations;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
}
static softap_facts_t softap_snapshot(void) {
    portENTER_CRITICAL(&s_softap_lock);
    softap_facts_t facts = s_softap;
    portEXIT_CRITICAL(&s_softap_lock);
    return facts;
}
static void softap_link(bool online, bool pending) {
    int64_t now = esp_timer_get_time();
    portENTER_CRITICAL(&s_softap_lock);
    s_softap.online = online;
    s_softap.pending = pending;
    s_softap.pending_until = softap_after(now, 20000000LL);
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
}
static esp_err_t connect_station(void) {
    softap_link(false, true);
    esp_err_t result = esp_wifi_connect();
    if (result != ESP_OK) softap_link(false, false);
    return result;
}
static bool softap_current(const softap_facts_t *facts, uint32_t revision) {
    softap_facts_t current = softap_snapshot();
    runtime_softap_settings_t desired = runtime_settings_get_softap_snapshot();
    return facts->version == current.version && current.valid &&
        current.started && current.enabled && !current.online && !current.operations &&
        !atomic_load(&s_stopping_for_sleep) && desired.revision == revision && desired.delay_min;
}
static bool softap_disconnected(const softap_facts_t *facts, uint32_t revision) {
    if (!softap_current(facts, revision)) return false;
    wifi_ap_record_t ap = {0};
    wifi_mode_t mode = WIFI_MODE_NULL;
    esp_netif_ip_info_t info = {0};
    return esp_wifi_get_mode(&mode) == ESP_OK && mode == WIFI_MODE_APSTA &&
        esp_wifi_sta_get_ap_info(&ap) == ESP_ERR_WIFI_NOT_CONNECT &&
        !esp_netif_is_netif_up(s_station_netif) &&
        esp_netif_get_ip_info(s_station_netif, &info) == ESP_OK && !info.ip.addr &&
        softap_current(facts, revision);
}
static bool softap_live(const softap_facts_t *facts, uint32_t revision, int64_t now) {
    return now >= 0 && !facts->pending && softap_disconnected(facts, revision);
}
static void softap_cancel_pending(const softap_facts_t *facts, uint32_t revision, int64_t now) {
    // A grace deadline is not proof that the SDK finished an async connect.
    // Cancel only after live disconnected proof, then require a fresh interval.
    if (now < facts->pending_until || !softap_disconnected(facts, revision)) return;
    portENTER_CRITICAL(&s_softap_lock);
    bool admitted = s_softap.version == facts->version && !s_softap.operations &&
        s_softap.started && s_softap.enabled && !s_softap.online &&
        !atomic_load(&s_stopping_for_sleep);
    uint64_t operation = 0;
    if (admitted) {
        ++s_softap.operations;
        softap_changed_locked();
        operation = s_softap.version;
    }
    portEXIT_CRITICAL(&s_softap_lock);
    if (!admitted) return;
    runtime_softap_settings_t desired = runtime_settings_get_softap_snapshot();
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (desired.revision == revision && desired.delay_min && !atomic_load(&s_stopping_for_sleep))
        result = esp_wifi_disconnect();
    portENTER_CRITICAL(&s_softap_lock);
    // A newer callback/retry owns its own intent. Never clear it with the
    // completion of an older SDK cancellation; subsequent RF events remain
    // asynchronous and are reconciled again before any restart admission.
    if (s_softap.version == operation && s_softap.operations == 1 && result == ESP_OK)
        s_softap.pending = false;
    --s_softap.operations;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
}
static void softap_arm(softap_policy_t *policy, const softap_facts_t *facts,
                       runtime_softap_settings_t desired, int64_t now) {
    int64_t interval = (int64_t)desired.delay_min * 60000000LL;
    policy->armed = true;
    policy->revision = desired.revision;
    policy->version = facts->version;
    policy->saturated = now > INT64_MAX - interval;
    policy->deadline = softap_after(now, interval);
}
static void softap_poll(softap_policy_t *policy, int64_t now) {
    softap_facts_t facts = softap_snapshot();
    runtime_softap_settings_t desired = runtime_settings_get_softap_snapshot();
    if (now < 0 || !facts.valid || !facts.started || !facts.enabled || facts.online ||
        facts.operations || !desired.delay_min || atomic_load(&s_stopping_for_sleep)) {
        policy->armed = false;
        return;
    }
    if (!policy->armed || policy->revision != desired.revision || policy->version != facts.version)
        softap_arm(policy, &facts, desired, now);
    if (policy->saturated || now < policy->deadline) return;
    // An active AP decision excludes the deep-sleep activity CAS. OTA already
    // owns activity and its reboot lease; the exact reservation arbitrates it.
    if (deep_sleep_clock_begin_activity()) {
        websocket_reboot_lease_t lease = {0};
        if (facts.pending) softap_cancel_pending(&facts, desired.revision, now);
        else if (softap_live(&facts, desired.revision, now) &&
            websocket_service_reboot_reserve(&lease) == ESP_OK) {
            // Final application arbitration; later RF/config events cannot be
            // atomically excluded by the SDK restart operation.
            if (true)
                (void)websocket_service_reboot_restart_reserved_now(&lease);
            if (lease.epoch) (void)websocket_service_reboot_cancel(&lease);
        }
        deep_sleep_clock_end_activity();
    }
    // Keep no ordinary pending AP reboot. Failed/held admission (including a
    // failed OTA later cancelled) receives a fresh full interval after return.
    int64_t rearm = esp_timer_get_time();
    if (rearm < now || rearm < 0) policy->armed = false;
    else softap_arm(policy, &facts, desired, rearm);
}


static esp_err_t apply_power(void *context, bool active) {
    (void)context;
    return esp_wifi_set_ps(active ? WIFI_PS_NONE : WIFI_PS_MIN_MODEM);
}

static void rssi_task(void *argument) {
    (void)argument;
    int64_t rssi_next = 0;
    softap_policy_t softap = {0};
    while (true) {
        int64_t now = esp_timer_get_time();
        if (!atomic_load(&s_stopping_for_sleep)) {
            native_network_power_poll(now, apply_power, NULL);
            softap_poll(&softap, now);
            if (now >= rssi_next) {
                wifi_ap_record_t access_point = {0};
                if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK)
                    native_state_set_wifi_rssi(s_state, access_point.rssi);
                rssi_next = now > INT64_MAX - (int64_t)WIFI_RSSI_INTERVAL_MS * 1000
                    ? INT64_MAX : now + (int64_t)WIFI_RSSI_INTERVAL_MS * 1000;
            }
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

static esp_err_t select_credential(size_t index) {
    ESP_RETURN_ON_FALSE(index < s_credential_count, ESP_ERR_INVALID_ARG, TAG,
                        "Wi-Fi network index is invalid");
    s_credential_index = index;
    s_station_config = s_credentials[index];
    return esp_wifi_set_config(WIFI_IF_STA, &s_station_config);
}

static void event_handler(void *arg, esp_event_base_t base, int32_t id,
                          void *event_data) {
    (void)arg;
    if (atomic_load(&s_stopping_for_sleep)) return;
    if (!((base == WIFI_EVENT && (id == WIFI_EVENT_STA_START ||
            id == WIFI_EVENT_STA_CONNECTED || id == WIFI_EVENT_STA_DISCONNECTED)) ||
          (base == IP_EVENT && (id == IP_EVENT_STA_GOT_IP || id == IP_EVENT_STA_LOST_IP)))) return;
    softap_operation(true);
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        if (s_have_credentials) connect_station();
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_CONNECTED) {
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_CONNECTED, 0);
#endif
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        softap_link(false, false);
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
        const wifi_event_sta_disconnected_t *event = event_data;
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_DISCONNECTED,
                                  event ? event->reason : 0);
#endif
        if (s_have_credentials &&
            s_retries++ < WIFI_RETRIES_PER_CREDENTIAL) {
            ESP_LOGW(TAG, "Wi-Fi network %u/%u retry %d/%d",
                     (unsigned)(s_credential_index + 1U),
                     (unsigned)s_credential_count, s_retries,
                     WIFI_RETRIES_PER_CREDENTIAL);
            connect_station();
        } else if (s_have_credentials &&
                   s_credential_index + 1U < s_credential_count) {
            ++s_credential_index;
            s_retries = 0;
            if (select_credential(s_credential_index) == ESP_OK) {
                ESP_LOGI(TAG, "Trying saved Wi-Fi network %u/%u",
                         (unsigned)(s_credential_index + 1U),
                         (unsigned)s_credential_count);
                connect_station();
            } else {
                xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
            }
        } else {
            xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        softap_link(true, false);
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_GOT_IP, 0);
#endif
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        wifi_ap_record_t access_point = {0};
        s_retries = 0;
        native_state_set_network(s_state, NATIVE_NETWORK_CLIENT,
                                 event->ip_info.ip.addr);
        if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK) {
            native_state_set_wifi_rssi(s_state, access_point.rssi);
        }
        time_service_notify_network_ready();
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: " IPSTR, IP2STR(&event->ip_info.ip));
    } else if (base == IP_EVENT && id == IP_EVENT_STA_LOST_IP) {
        softap_link(false, false);
    }
    softap_operation(false);
}

static esp_err_t start_access_point(void) {
    uint8_t mac[6];
    wifi_config_t ap = {0};
    ESP_RETURN_ON_ERROR(esp_read_mac(mac, ESP_MAC_WIFI_SOFTAP), TAG,
                        "MAC read failed");
    snprintf((char *)ap.ap.ssid, sizeof(ap.ap.ssid), "yoRadio-%02X%02X%02X",
             mac[3], mac[4], mac[5]);
    ap.ap.ssid_len = strlen((char *)ap.ap.ssid);
    ap.ap.channel = 1;
    ap.ap.max_connection = 4;
    ap.ap.authmode = WIFI_AUTH_OPEN;
    if (!s_ap_netif) s_ap_netif = esp_netif_create_default_wifi_ap();
    ESP_RETURN_ON_FALSE(s_ap_netif, ESP_ERR_NO_MEM, TAG,
                        "AP network interface allocation failed");
    ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_APSTA), TAG,
                        "AP/client mode failed");
    ESP_RETURN_ON_ERROR(esp_wifi_set_config(WIFI_IF_AP, &ap), TAG,
                        "AP configuration failed");
    portENTER_CRITICAL(&s_softap_lock);
    s_softap.enabled = true;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
    native_state_set_network(s_state, NATIVE_NETWORK_ACCESS_POINT, 0);
    ESP_LOGW(TAG, "Access point enabled: %s", ap.ap.ssid);
    return ESP_OK;
}

esp_err_t network_service_prepare_sleep(void) {
    softap_operation(true);
    atomic_store(&s_stopping_for_sleep, true);
    esp_err_t result = esp_wifi_stop();
    if (result != ESP_OK) atomic_store(&s_stopping_for_sleep, false);
    else {
        portENTER_CRITICAL(&s_softap_lock);
        s_softap.started = s_softap.enabled = false;
        portEXIT_CRITICAL(&s_softap_lock);
    }
    softap_operation(false);
    return result;
}

esp_err_t network_service_start(native_state_t *state) {
    ESP_RETURN_ON_ERROR(network_service_storage_init(), TAG,
                        "Wi-Fi credential owner initialization failed");
    s_state = state;
    s_wifi_events = xEventGroupCreate();
    ESP_RETURN_ON_FALSE(s_wifi_events, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi event group allocation failed");
    ESP_RETURN_ON_ERROR(esp_netif_init(), TAG, "TCP/IP stack failed");
    ESP_RETURN_ON_ERROR(esp_event_loop_create_default(), TAG,
                        "Default event loop failed");
    s_station_netif = esp_netif_create_default_wifi_sta();
    ESP_RETURN_ON_FALSE(s_station_netif, ESP_ERR_NO_MEM, TAG,
                        "Station network interface allocation failed");
    char hostname[24];
    runtime_settings_get_mdns_name(hostname, sizeof(hostname));
    if (hostname[0]) {
        ESP_RETURN_ON_ERROR(esp_netif_set_hostname(s_station_netif, hostname),
                            TAG, "Station hostname failed");
    }
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_RETURN_ON_ERROR(esp_wifi_init(&init), TAG, "Wi-Fi init failed");
    // wifi.csv is the only persistent source of credentials. Keep the
    // driver's working copy in RAM so it cannot silently override the file.
    ESP_RETURN_ON_ERROR(esp_wifi_set_storage(WIFI_STORAGE_RAM), TAG,
                        "Wi-Fi RAM storage selection failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            WIFI_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL),
                        TAG, "Wi-Fi event registration failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            IP_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL),
                        TAG, "IP event registration failed");

    memset(&s_station_config, 0, sizeof(s_station_config));
    s_have_credentials = read_credentials(&s_station_config);
    if (s_have_credentials) {
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
        ESP_RETURN_ON_ERROR(select_credential(0), TAG,
                            "Station configuration failed");
    } else {
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
    }
    ESP_RETURN_ON_ERROR(esp_wifi_start(), TAG, "Wi-Fi start failed");
    portENTER_CRITICAL(&s_softap_lock);
    s_softap.started = true;
    softap_changed_locked();
    portEXIT_CRITICAL(&s_softap_lock);
    // Preserve audio intent if it arrived before networking was ready. The
    // existing RSSI task is the sole power-policy driver caller.
    native_network_power_invalidate();

    ESP_RETURN_ON_FALSE(xTaskCreate(rssi_task, "wifi_rssi",
                                    BOARD_TASK_STACK_WIFI_RSSI, NULL, 2,
                                    NULL) == pdPASS,
                        ESP_ERR_NO_MEM, TAG, "RSSI task allocation failed");

    if (s_have_credentials) {
        EventBits_t bits = xEventGroupWaitBits(
            s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT, pdTRUE,
            pdFALSE, pdMS_TO_TICKS(20000));
        if (bits & WIFI_CONNECTED_BIT) return ESP_OK;
    }
    return start_access_point();
}

esp_err_t network_service_retry_client(void) {
    ESP_RETURN_ON_FALSE(s_have_credentials, ESP_ERR_NOT_FOUND, TAG,
                        "No saved Wi-Fi credentials");
    softap_operation(true);
    s_retries = 0;
    s_credential_index = 0;
    xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT);
    esp_err_t result = esp_wifi_set_mode(WIFI_MODE_STA);
    if (result == ESP_OK) {
        portENTER_CRITICAL(&s_softap_lock);
        s_softap.enabled = s_softap.online = false;
        portEXIT_CRITICAL(&s_softap_lock);
        result = select_credential(0);
    }
    if (result == ESP_OK) {
        native_state_set_network(s_state, NATIVE_NETWORK_STARTING, 0);
        result = connect_station();
    }
    softap_operation(false);
    return result;
}
