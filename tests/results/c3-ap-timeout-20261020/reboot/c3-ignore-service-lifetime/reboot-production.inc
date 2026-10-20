// The status task exists before HTTP routes become available. Reboot requests
// need no late heap allocation; first ordinary request wins. An OTA lease
// defers execution until its owner cancels or commits after the response.
static atomic_bool s_reboot_ready;
static portMUX_TYPE s_reboot_lock = portMUX_INITIALIZER_UNLOCKED;
static uint32_t s_reboot_at;
static bool s_reboot_pending;
static uint64_t s_reboot_reserved_epoch, s_reboot_next_epoch;

bool websocket_service_reboot_ready(void) {
    return atomic_load(&s_reboot_ready);
}
void websocket_service_request_reboot(unsigned delay_ms) {
    if (delay_ms > 60000U) delay_ms = 60000U;
    uint32_t at = (uint32_t)xTaskGetTickCount() + (uint32_t)pdMS_TO_TICKS(delay_ms);
    portENTER_CRITICAL(&s_reboot_lock);
    if (atomic_load(&s_reboot_ready) && !s_reboot_pending) {
        s_reboot_at = at;
        s_reboot_pending = true;
    }
    portEXIT_CRITICAL(&s_reboot_lock);
}
esp_err_t websocket_service_reboot_reserve(websocket_reboot_lease_t *lease) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    if (lease->epoch) return ESP_ERR_INVALID_STATE;
    portENTER_CRITICAL(&s_reboot_lock);
    if (!atomic_load(&s_reboot_ready) || s_reboot_pending || s_reboot_reserved_epoch ||
        s_reboot_next_epoch == UINT64_MAX) {
        portEXIT_CRITICAL(&s_reboot_lock);
        return ESP_ERR_INVALID_STATE;
    }
    lease->epoch = s_reboot_reserved_epoch = ++s_reboot_next_epoch;
    portEXIT_CRITICAL(&s_reboot_lock);
    return ESP_OK;
}
esp_err_t websocket_service_reboot_cancel(websocket_reboot_lease_t *lease) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    portENTER_CRITICAL(&s_reboot_lock);
    if (!lease->epoch || lease->epoch != s_reboot_reserved_epoch) {
        portEXIT_CRITICAL(&s_reboot_lock);
        return ESP_ERR_INVALID_STATE;
    }
    s_reboot_reserved_epoch = lease->epoch = 0;
    portEXIT_CRITICAL(&s_reboot_lock);
    return ESP_OK;
}
esp_err_t websocket_service_reboot_commit(websocket_reboot_lease_t *lease, unsigned delay_ms) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    if (delay_ms > 60000U) delay_ms = 60000U;
    uint32_t at = (uint32_t)xTaskGetTickCount() + (uint32_t)pdMS_TO_TICKS(delay_ms);
    portENTER_CRITICAL(&s_reboot_lock);
    if (!lease->epoch || lease->epoch != s_reboot_reserved_epoch) {
        portEXIT_CRITICAL(&s_reboot_lock);
        return ESP_ERR_INVALID_STATE;
    }
    if (!s_reboot_pending) s_reboot_at = at;
    s_reboot_pending = true;
    s_reboot_reserved_epoch = lease->epoch = 0;
    portEXIT_CRITICAL(&s_reboot_lock);
    return ESP_OK;
}
esp_err_t websocket_service_reboot_restart_reserved_now(websocket_reboot_lease_t *lease) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    portENTER_CRITICAL(&s_reboot_lock);
    if (!lease->epoch || lease->epoch != s_reboot_reserved_epoch) {
        portEXIT_CRITICAL(&s_reboot_lock);
        return ESP_ERR_INVALID_STATE;
    }
    // Retain the reservation while the SDK restarts outside the portMUX: an
    // ordinary pending reboot and a competing OTA admission must stay blocked.
    portEXIT_CRITICAL(&s_reboot_lock);
    esp_restart();
    return ESP_OK; // Only a returning test double can reach this line.
}

static void poll_reboot(void) {
    portENTER_CRITICAL(&s_reboot_lock);
    bool pending = s_reboot_pending && !s_reboot_reserved_epoch;
    uint32_t at = s_reboot_at;
    portEXIT_CRITICAL(&s_reboot_lock);
    if (pending && (int32_t)((uint32_t)xTaskGetTickCount() - at) >= 0) esp_restart();
}

