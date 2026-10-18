
static TaskHandle_t s_task;
static atomic_bool s_ready;
static portMUX_TYPE s_deadline_lock = portMUX_INITIALIZER_UNLOCKED;
static bool s_pending;
static uint32_t s_deadline;
static uint64_t s_reserved_epoch, s_next_epoch;

static void reboot_task(void *argument) {
    (void)argument;
    for (;;) {
        portENTER_CRITICAL(&s_deadline_lock);
        bool pending = s_pending && !s_reserved_epoch;
        uint32_t deadline = s_deadline;
        portEXIT_CRITICAL(&s_deadline_lock);
        if (!pending) {
            (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
            continue;
        }
        int32_t remaining = (int32_t)(deadline - (uint32_t)xTaskGetTickCount());
        if (remaining <= 0) esp_restart();
        else (void)ulTaskNotifyTake(pdTRUE, (TickType_t)remaining);
    }
}

esp_err_t web_reboot_start(void) {
    if (atomic_load(&s_ready)) return ESP_OK;
    if (xTaskCreate(reboot_task, "web_reboot", 2048, NULL, 2, &s_task) != pdPASS) {
        s_task = NULL;
        return ESP_ERR_NO_MEM;
    }
    atomic_store(&s_ready, true);
    return ESP_OK;
}

bool web_reboot_ready(void) {
    return atomic_load(&s_ready);
}

void web_reboot_request(unsigned delay_ms) {
    if (delay_ms > 60000U) delay_ms = 60000U;
    uint32_t deadline = (uint32_t)xTaskGetTickCount() +
                        (uint32_t)pdMS_TO_TICKS(delay_ms);
    portENTER_CRITICAL(&s_deadline_lock);
    if (!atomic_load(&s_ready)) {
        portEXIT_CRITICAL(&s_deadline_lock);
        return;
    }
    if (!s_pending || (int32_t)(deadline - s_deadline) < 0) {
        s_deadline = deadline;
        s_pending = true;
    }
    portEXIT_CRITICAL(&s_deadline_lock);
    xTaskNotifyGive(s_task);
}

esp_err_t web_reboot_reserve(web_reboot_lease_t *lease) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    if (lease->epoch) return ESP_ERR_INVALID_STATE;
    portENTER_CRITICAL(&s_deadline_lock);
    if (!atomic_load(&s_ready) || s_pending || s_reserved_epoch || s_next_epoch == UINT64_MAX) {
        portEXIT_CRITICAL(&s_deadline_lock);
        return ESP_ERR_INVALID_STATE;
    }
    lease->epoch = s_reserved_epoch = ++s_next_epoch;
    portEXIT_CRITICAL(&s_deadline_lock);
    return ESP_OK;
}

esp_err_t web_reboot_cancel(web_reboot_lease_t *lease) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    portENTER_CRITICAL(&s_deadline_lock);
    if (!lease->epoch || lease->epoch != s_reserved_epoch) {
        portEXIT_CRITICAL(&s_deadline_lock);
        return ESP_ERR_INVALID_STATE;
    }
    s_reserved_epoch = lease->epoch = 0;
    portEXIT_CRITICAL(&s_deadline_lock);
    xTaskNotifyGive(s_task);
    return ESP_OK;
}

esp_err_t web_reboot_commit(web_reboot_lease_t *lease, unsigned delay_ms) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    if (delay_ms > 60000U) delay_ms = 60000U;
    uint32_t deadline = (uint32_t)xTaskGetTickCount() + (uint32_t)pdMS_TO_TICKS(delay_ms);
    portENTER_CRITICAL(&s_deadline_lock);
    if (!lease->epoch || lease->epoch != s_reserved_epoch) {
        portEXIT_CRITICAL(&s_deadline_lock);
        return ESP_ERR_INVALID_STATE;
    }
    if (!s_pending || (int32_t)(deadline - s_deadline) < 0) s_deadline = deadline;
    s_pending = true;
    s_reserved_epoch = lease->epoch = 0;
    portEXIT_CRITICAL(&s_deadline_lock);
    xTaskNotifyGive(s_task);
    return ESP_OK;
}

esp_err_t web_reboot_abort(void) {
    // Startup owns this operation; no route may concurrently request reboot.
    portENTER_CRITICAL(&s_deadline_lock);
    if (s_pending || s_reserved_epoch) {
        portEXIT_CRITICAL(&s_deadline_lock);
        return ESP_ERR_INVALID_STATE;
    }
    atomic_store(&s_ready, false);
    TaskHandle_t task = s_task;
    s_task = NULL;
    portEXIT_CRITICAL(&s_deadline_lock);
    if (task) vTaskDelete(task);
    return ESP_OK;
}
