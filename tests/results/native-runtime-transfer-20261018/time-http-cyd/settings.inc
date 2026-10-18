
#define TIME_RECORD_SIZE 82U
#define TIME_RECORD_NAMES 12U
#define SETTINGS_WAIT_MS 100U

static _Atomic(SemaphoreHandle_t) s_write_lock;
static portMUX_TYPE s_snapshot_lock = portMUX_INITIALIZER_UNLOCKED;
static bool s_initialized;
static time_settings_t s_settings;
static uint32_t s_revision;

void time_settings_defaults(time_settings_t *settings) {
    if (!settings) return;
    memset(settings, 0, sizeof(*settings));
    settings->sync_interval_minutes = 60U;
    settings->server_count = 2U;
    memcpy(settings->servers[0], "pool.ntp.org", sizeof("pool.ntp.org"));
    memcpy(settings->servers[1], "time.nist.gov", sizeof("time.nist.gov"));
}

static bool valid_host(const char name[NATIVE_TIME_SNTP_NAME_CAPACITY]) {
    const char *end = memchr(name, '\0', NATIVE_TIME_SNTP_NAME_CAPACITY);
    if (!end || end == name) return false;
    bool numeric = true;
    for (const char *at = name; at < end; ++at) {
        if ((*at < '0' || *at > '9') && *at != '.') numeric = false;
    }
    if (numeric) {
        const char *at = name;
        for (unsigned part = 0; part < 4U; ++part) {
            const char *start = at;
            unsigned value = 0;
            while (at < end && *at >= '0' && *at <= '9') {
                value = value * 10U + (unsigned)(*at++ - '0');
                if (value > 255U || at - start > 3) return false;
            }
            if (at == start || (at - start > 1 && *start == '0')) return false;
            if (part == 3U) return at == end;
            if (at == end || *at++ != '.') return false;
        }
        return false;
    }
    const char *label = name;
    for (const char *at = name; at <= end; ++at) {
        if (at == end || *at == '.') {
            if (at == label || at - label > 63 || *label == '-' || at[-1] == '-')
                return false;
            label = at + 1;
        } else {
            unsigned char value = (unsigned char)*at;
            if (!((value >= 'a' && value <= 'z') ||
                  (value >= 'A' && value <= 'Z') ||
                  (value >= '0' && value <= '9') || value == '-')) return false;
        }
    }
    return true;
}

bool time_settings_valid(const time_settings_t *settings) {
    if (!settings || settings->utc_offset_minutes < -720 ||
        settings->utc_offset_minutes > 840 ||
        settings->utc_offset_minutes % 15 != 0 ||
        settings->sync_interval_minutes < 15U ||
        settings->sync_interval_minutes > 1440U ||
        settings->server_count == 0U ||
        settings->server_count > NATIVE_TIME_SNTP_SERVER_COUNT) return false;
    for (unsigned index = 0; index < settings->server_count; ++index) {
        if (!valid_host(settings->servers[index])) return false;
    }
    return true;
}

static void encode_record(const time_settings_t *settings,
                          uint8_t record[TIME_RECORD_SIZE]) {
    memset(record, 0, TIME_RECORD_SIZE);
    memcpy(record, "NTIM", 4U);
    record[4] = 1U;
    record[6] = settings->server_count;
    uint16_t offset = (uint16_t)settings->utc_offset_minutes;
    record[8] = (uint8_t)offset;
    record[9] = (uint8_t)(offset >> 8);
    record[10] = (uint8_t)settings->sync_interval_minutes;
    record[11] = (uint8_t)(settings->sync_interval_minutes >> 8);
    for (unsigned index = 0; index < settings->server_count; ++index) {
        memcpy(record + TIME_RECORD_NAMES + index * NATIVE_TIME_SNTP_NAME_CAPACITY,
               settings->servers[index], strlen(settings->servers[index]));
    }
}

static bool decode_record(const uint8_t record[TIME_RECORD_SIZE],
                           time_settings_t *settings) {
    if (memcmp(record, "NTIM", 4U) || record[4] != 1U || record[5] || record[7])
        return false;
    time_settings_t candidate = {0};
    uint16_t raw_offset = (uint16_t)((unsigned)record[8] | (unsigned)record[9] << 8);
    int32_t offset = raw_offset;
    if (raw_offset >= 0x8000U) offset -= 0x10000L;
    candidate.utc_offset_minutes = (int16_t)offset;
    candidate.sync_interval_minutes =
        (uint16_t)((unsigned)record[10] | (unsigned)record[11] << 8);
    candidate.server_count = record[6];
    memcpy(candidate.servers, record + TIME_RECORD_NAMES, sizeof(candidate.servers));
    if (!time_settings_valid(&candidate)) return false;
    // Canonical padding detects interior NUL + hidden trailing bytes, including
    // inactive slots. The on-flash representation has no C struct padding.
    uint8_t canonical[TIME_RECORD_SIZE];
    encode_record(&candidate, canonical);
    if (memcmp(record, canonical, TIME_RECORD_SIZE)) return false;
    *settings = candidate;
    return true;
}

static SemaphoreHandle_t take_write_lock(void) {
    SemaphoreHandle_t lock = atomic_load(&s_write_lock);
    if (!lock) {
        SemaphoreHandle_t candidate = xSemaphoreCreateMutex();
        if (!candidate) return NULL;
        SemaphoreHandle_t empty = NULL;
        if (!atomic_compare_exchange_strong(&s_write_lock, &empty, candidate)) {
            vSemaphoreDelete(candidate);
            lock = empty;
        } else lock = candidate;
    }
    return xSemaphoreTake(lock, pdMS_TO_TICKS(SETTINGS_WAIT_MS)) == pdTRUE
               ? lock : NULL;
}

esp_err_t time_settings_init(void) {
    SemaphoreHandle_t lock = take_write_lock();
    if (!lock) return atomic_load(&s_write_lock) ? ESP_ERR_TIMEOUT : ESP_ERR_NO_MEM;
    portENTER_CRITICAL(&s_snapshot_lock);
    bool initialized = s_initialized;
    portEXIT_CRITICAL(&s_snapshot_lock);
    if (initialized) {
        xSemaphoreGive(lock);
        return ESP_OK;
    }
    time_settings_t candidate;
    time_settings_defaults(&candidate);
    nvs_handle_t handle;
    esp_err_t result = nvs_open("native_time", NVS_READONLY, &handle);
    if (result == ESP_OK) {
        size_t size = 0;
        result = nvs_get_blob(handle, "cfg", NULL, &size);
        if (result == ESP_OK && size == TIME_RECORD_SIZE) {
            uint8_t record[TIME_RECORD_SIZE];
            result = nvs_get_blob(handle, "cfg", record, &size);
            if (result == ESP_OK && size == TIME_RECORD_SIZE)
                (void)decode_record(record, &candidate);
        } else if (result == ESP_OK) {
            // Unknown or malformed format uses defaults without rewriting NVS.
            result = ESP_OK;
        }
        nvs_close(handle);
    }
    if (result == ESP_ERR_NVS_NOT_FOUND || result == ESP_ERR_NVS_TYPE_MISMATCH)
        result = ESP_OK;
    if (result == ESP_OK) {
        portENTER_CRITICAL(&s_snapshot_lock);
        s_settings = candidate;
        s_revision = 1U;
        s_initialized = true;
        portEXIT_CRITICAL(&s_snapshot_lock);
    }
    xSemaphoreGive(lock);
    return result;
}

bool time_settings_snapshot(time_settings_t *settings, uint32_t *revision) {
    if (!settings) return false;
    portENTER_CRITICAL(&s_snapshot_lock);
    bool available = s_initialized;
    if (available) {
        *settings = s_settings;
        if (revision) *revision = s_revision;
    }
    portEXIT_CRITICAL(&s_snapshot_lock);
    return available;
}

esp_err_t time_settings_save(const time_settings_t *settings) {
    if (!time_settings_valid(settings)) return ESP_ERR_INVALID_ARG;
    // Own the candidate before waiting for another writer/NVS.
    time_settings_t candidate = *settings;
    uint8_t record[TIME_RECORD_SIZE];
    encode_record(&candidate, record);
    // Publish the same canonical representation that a later boot will load.
    if (!decode_record(record, &candidate)) return ESP_ERR_INVALID_ARG;
    SemaphoreHandle_t lock = take_write_lock();
    if (!lock) return atomic_load(&s_write_lock) ? ESP_ERR_TIMEOUT : ESP_ERR_NO_MEM;
    portENTER_CRITICAL(&s_snapshot_lock);
    bool initialized = s_initialized;
    uint32_t revision = s_revision;
    portEXIT_CRITICAL(&s_snapshot_lock);
    esp_err_t result = ESP_ERR_INVALID_STATE;
    if (!initialized || revision == UINT32_MAX) goto done;
    nvs_handle_t handle;
    result = nvs_open("native_time", NVS_READWRITE, &handle);
    if (result != ESP_OK) goto done;
    result = nvs_set_blob(handle, "cfg", record, sizeof(record));
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    if (result == ESP_OK) {
        // Only a bounded RAM copy under the snapshot critical section. No
        // allocation or failing mutex acquisition remains after flash commit.
        portENTER_CRITICAL(&s_snapshot_lock);
        s_settings = candidate;
        s_revision = revision + 1U;
        portEXIT_CRITICAL(&s_snapshot_lock);
    }
done:
    xSemaphoreGive(lock);
    return result;
}
