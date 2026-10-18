
#define TIME_EVENT_CHANGED (1U << 0)
#define TIME_EVENT_SYNC (1U << 1)
#define TIME_STACK_BYTES 2048U
#define TIME_PRIORITY 1U
#define TIME_WAIT_MS 100U
#define TIME_CONTROL_COOLDOWN_US INT64_C(5000000)
#define TIME_VALID_EPOCH INT64_C(1704067200)

static _Atomic(SemaphoreHandle_t) s_start_lock;
static _Atomic(SemaphoreHandle_t) s_state_lock;
static _Atomic(TaskHandle_t) s_task;
static atomic_bool s_network_ready;
static atomic_uint_least32_t s_connection_epoch;
static bool s_available;
static bool s_synchronized;
static time_t s_last_sync_epoch;
static int64_t s_last_sync_us;
static uint32_t s_applied_revision;
static esp_err_t s_last_apply_error;

static SemaphoreHandle_t ensure_lock(_Atomic(SemaphoreHandle_t) *slot) {
    SemaphoreHandle_t lock = atomic_load(slot);
    if (lock) return lock;
    SemaphoreHandle_t candidate = xSemaphoreCreateMutex();
    if (!candidate) return NULL;
    SemaphoreHandle_t empty = NULL;
    if (!atomic_compare_exchange_strong(slot, &empty, candidate)) {
        vSemaphoreDelete(candidate);
        return empty;
    }
    return candidate;
}

static void notify(uint32_t events) {
    TaskHandle_t task = atomic_load(&s_task);
    if (task) xTaskNotify(task, events, eSetBits);
}

static void sync_notification(void *context, const struct timeval *tv) {
    (void)context;
    (void)tv;
    notify(TIME_EVENT_SYNC);
}

static void time_worker(void *context) {
    (void)context;
    uint32_t completed_connection = 0;
    int64_t next_control_us = 0;
    for (;;) {
        uint32_t events = 0;
        xTaskNotifyWait(0, UINT32_MAX, &events, pdMS_TO_TICKS(1000));
        SemaphoreHandle_t state_lock = atomic_load(&s_state_lock);
        if ((events & TIME_EVENT_SYNC) != 0U) {
            time_t epoch = time(NULL);
            int64_t monotonic = esp_timer_get_time();
            if (xSemaphoreTake(state_lock, pdMS_TO_TICKS(TIME_WAIT_MS)) == pdTRUE) {
                s_synchronized = true;
                s_last_sync_epoch = epoch;
                s_last_sync_us = monotonic;
                xSemaphoreGive(state_lock);
            } else {
                // A bounded snapshot reader cannot permanently lose a sync.
                notify(TIME_EVENT_SYNC);
            }
        }
        if (!atomic_load(&s_network_ready)) continue;
        time_settings_t desired;
        uint32_t revision;
        if (!time_settings_snapshot(&desired, &revision)) continue;
        if (xSemaphoreTake(state_lock, pdMS_TO_TICKS(TIME_WAIT_MS)) != pdTRUE)
            continue;
        uint32_t applied = s_applied_revision;
        xSemaphoreGive(state_lock);
        uint32_t connection = atomic_load(&s_connection_epoch);
        if (revision == applied && connection == completed_connection) continue;
        int64_t now = esp_timer_get_time();
        if (now < next_control_us) continue;
        native_time_sntp_config_t config = {0};
        config.server_count = desired.server_count;
        config.sync_interval_minutes = desired.sync_interval_minutes;
        memcpy(config.servers, desired.servers, sizeof(config.servers));
        esp_err_t result = revision != applied
                               ? native_time_sntp_apply(&config)
                               : native_time_sntp_restart();
        next_control_us = now > INT64_MAX - TIME_CONTROL_COOLDOWN_US
                              ? INT64_MAX : now + TIME_CONTROL_COOLDOWN_US;
        if (xSemaphoreTake(state_lock, pdMS_TO_TICKS(TIME_WAIT_MS)) == pdTRUE) {
            s_last_apply_error = result;
            if (result == ESP_OK) {
                s_applied_revision = revision;
                completed_connection = connection;
            }
            xSemaphoreGive(state_lock);
        }
    }
}

esp_err_t time_service_start(void) {
    SemaphoreHandle_t lock = ensure_lock(&s_start_lock);
    if (!lock) return ESP_ERR_NO_MEM;
    if (xSemaphoreTake(lock, pdMS_TO_TICKS(TIME_WAIT_MS)) != pdTRUE)
        return ESP_ERR_TIMEOUT;
    esp_err_t result = ESP_OK;
    if (atomic_load(&s_task)) goto done;
    result = time_settings_init();
    if (result != ESP_OK) goto done;
    SemaphoreHandle_t state_lock = ensure_lock(&s_state_lock);
    if (!state_lock) {
        result = ESP_ERR_NO_MEM;
        goto done;
    }
    result = native_time_sntp_init(sync_notification, NULL);
    if (result != ESP_OK) goto done;
    if (xSemaphoreTake(state_lock, pdMS_TO_TICKS(TIME_WAIT_MS)) != pdTRUE) {
        result = ESP_ERR_TIMEOUT;
        goto done;
    }
    TaskHandle_t task = NULL;
    if (xTaskCreate(time_worker, "time_sync", TIME_STACK_BYTES, NULL,
                    TIME_PRIORITY, &task) != pdPASS) {
        result = ESP_ERR_NO_MEM;
        xSemaphoreGive(state_lock);
        goto done;
    }
    atomic_store(&s_task, task);
    s_available = true;
    xSemaphoreGive(state_lock);
    notify(TIME_EVENT_CHANGED);
done:
    xSemaphoreGive(lock);
    return result;
}

esp_err_t time_service_get_settings(time_settings_t *settings) {
    return time_settings_snapshot(settings, NULL) ? ESP_OK : ESP_ERR_INVALID_STATE;
}

esp_err_t time_service_save_settings(const time_settings_t *settings) {
    esp_err_t result = time_settings_save(settings);
    if (result == ESP_OK) notify(TIME_EVENT_CHANGED);
    return result;
}

void time_service_notify_network(bool has_station_ip) {
    bool previous = atomic_exchange(&s_network_ready, has_station_ip);
    if (has_station_ip) {
        native_time_sntp_notify_network_ready();
        if (!previous) atomic_fetch_add(&s_connection_epoch, 1U);
    }
    notify(TIME_EVENT_CHANGED);
}

bool time_service_snapshot(time_snapshot_t *snapshot) {
    if (!snapshot) return false;
    SemaphoreHandle_t lock = atomic_load(&s_state_lock);
    if (!lock || xSemaphoreTake(lock, pdMS_TO_TICKS(TIME_WAIT_MS)) != pdTRUE)
        return false;
    time_snapshot_t candidate = {0};
    candidate.available = s_available;
    candidate.synchronized_this_boot = s_synchronized;
    candidate.last_sync_epoch = s_last_sync_epoch;
    int64_t last_sync_us = s_last_sync_us;
    candidate.applied_revision = s_applied_revision;
    candidate.last_apply_error = s_last_apply_error;
    xSemaphoreGive(lock);
    if (!candidate.available ||
        !time_settings_snapshot(&candidate.settings, &candidate.desired_revision))
        return false;
    candidate.network_ready = atomic_load(&s_network_ready);
    candidate.utc_epoch = time(NULL);
    int64_t utc = (int64_t)candidate.utc_epoch;
    int64_t offset = (int64_t)candidate.settings.utc_offset_minutes * 60;
    if (utc >= TIME_VALID_EPOCH &&
        (offset >= 0 ? utc <= INT64_MAX - offset : utc >= INT64_MIN - offset)) {
        int64_t adjusted = utc + offset;
        time_t local = (time_t)adjusted;
        if ((int64_t)local == adjusted && gmtime_r(&local, &candidate.local_time))
            candidate.clock_valid = true;
    }
    int64_t monotonic = esp_timer_get_time();
    candidate.last_sync_age_ms = candidate.synchronized_this_boot
                                    ? (monotonic >= last_sync_us
                                           ? (monotonic - last_sync_us) / 1000 : 0)
                                    : -1;
    *snapshot = candidate;
    return true;
}
