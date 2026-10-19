#include "platform.h"
#include <limits.h>
#include "board_config.h"

struct test_sem { pthread_mutex_t mutex; pthread_cond_t cond; bool available; };
struct test_queue { pthread_mutex_t mutex; unsigned count, head, used; size_t size; uint8_t data[]; };
struct test_event { pthread_mutex_t mutex; pthread_cond_t cond; unsigned bits; };
struct test_task { pthread_t thread; void (*entry)(void *); void *arg;
    bool created, joined, parked, exited; unsigned lap, permits; };
static struct test_task task;
static _Thread_local bool owner_thread;
static pthread_mutex_t schedule = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t schedule_changed = PTHREAD_COND_INITIALIZER;
static unsigned awaited_lap;
static atomic_int_fast64_t virtual_now;
static pthread_mutex_t driver_lock = PTHREAD_MUTEX_INITIALIZER;
static fixture_stats_t stats;
static unsigned allocation_calls, fail_allocation;
static unsigned fail_at[API_COUNT];
static esp_err_t fail_error[API_COUNT];
static bool task_failure, hold_disconnect;
static wifi_config_t driver_config;
static wifi_ap_record_t observed_ap;
static uint32_t observed_ip;
static SemaphoreHandle_t snapshot_mutex;
static struct { bool active; esp_event_handler_t handler; void *arg;
    esp_event_base_t base; } handlers[2];
static pthread_mutex_t boundary = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t boundary_changed = PTHREAD_COND_INITIALIZER;
static bool block_query, query_blocked, query_release, block_send, send_blocked, send_release;
static bool block_unregister, unregister_blocked, unregister_release;
const char fixture_wifi_base[] = "wifi", fixture_ip_base[] = "ip";

static struct timespec until_ms(unsigned ms) {
    struct timespec t; CHECK(clock_gettime(CLOCK_REALTIME, &t) == 0, "wall_clock");
    t.tv_sec += ms / 1000; t.tv_nsec += (long)(ms % 1000) * 1000000L;
    if (t.tv_nsec >= 1000000000L) { ++t.tv_sec; t.tv_nsec -= 1000000000L; }
    return t;
}
static void wait_changed(pthread_cond_t *cond, pthread_mutex_t *mutex) {
    struct timespec end = until_ms(10000);
    CHECK(pthread_cond_timedwait(cond, mutex, &end) == 0, "fixture_barrier_progress");
}
static bool allocation_ok(void) {
    pthread_mutex_lock(&driver_lock);
    bool ok = ++allocation_calls != fail_allocation;
    pthread_mutex_unlock(&driver_lock); return ok;
}
static esp_err_t api_result_locked(enum fixture_api api) {
    unsigned call = ++stats.api_calls[api];
    return fail_at[api] == UINT_MAX || call == fail_at[api] ? fail_error[api] : ESP_OK;
}
fixture_stats_t fixture_stats(void) {
    pthread_mutex_lock(&driver_lock); fixture_stats_t copy = stats;
    pthread_mutex_unlock(&driver_lock); return copy;
}
void fixture_init(void) { atomic_store(&virtual_now, 1000000); stats.mode = WIFI_MODE_STA; }
int64_t esp_timer_get_time(void) { return atomic_load(&virtual_now); }
void fixture_set_clock(int64_t now) { CHECK(now >= 0, "nonnegative_clock"); atomic_store(&virtual_now, now); }
static void advance_clock(int64_t delta) {
    CHECK(delta >= 0, "monotonic_test_clock");
    int64_t old = atomic_load(&virtual_now);
    atomic_store(&virtual_now, old > INT64_MAX - delta ? INT64_MAX : old + delta);
}
void fixture_fail_alloc(unsigned nth) {
    pthread_mutex_lock(&driver_lock); fail_allocation = nth ? allocation_calls + nth : 0;
    pthread_mutex_unlock(&driver_lock);
}
void fixture_fail_api(enum fixture_api api, unsigned nth, esp_err_t error) {
    pthread_mutex_lock(&driver_lock);
    fail_at[api] = nth == UINT_MAX ? UINT_MAX : nth ? stats.api_calls[api] + nth : 0;
    fail_error[api] = error; pthread_mutex_unlock(&driver_lock);
}
void fixture_fail_task(bool fail) { pthread_mutex_lock(&driver_lock); task_failure = fail; pthread_mutex_unlock(&driver_lock); }
void fixture_hold_disconnect(bool hold) { pthread_mutex_lock(&driver_lock); hold_disconnect = hold; pthread_mutex_unlock(&driver_lock); }
void fixture_driver_stopped(void) {
    pthread_mutex_lock(&driver_lock); stats.started = stats.associated = stats.netif_up = false;
    observed_ip = 0; pthread_mutex_unlock(&driver_lock);
}

QueueHandle_t xQueueCreate(unsigned count, size_t size) {
    CHECK(count == 16 && size, "bounded_event_queue");
    if (!allocation_ok()) return NULL;
    QueueHandle_t q = calloc(1, sizeof(*q) + count * size); CHECK(q, "host_queue_allocation");
    pthread_mutex_init(&q->mutex, NULL); q->count = count; q->size = size;
    pthread_mutex_lock(&driver_lock); ++stats.queues; pthread_mutex_unlock(&driver_lock); return q;
}
BaseType_t xQueueSend(QueueHandle_t q, const void *value, TickType_t timeout) {
    CHECK(q && timeout == 0, "nonblocking_callback_queue");
    pthread_mutex_lock(&boundary);
    if (block_send) {
        block_send = false; send_blocked = true; pthread_cond_broadcast(&boundary_changed);
        while (!send_release) wait_changed(&boundary_changed, &boundary);
        send_blocked = false;
    }
    pthread_mutex_unlock(&boundary);
    pthread_mutex_lock(&q->mutex); bool ok = q->used < q->count;
    if (ok) { memcpy(q->data + ((q->head + q->used) % q->count) * q->size, value, q->size); ++q->used; }
    pthread_mutex_unlock(&q->mutex); return ok;
}
BaseType_t xQueueReceive(QueueHandle_t q, void *value, TickType_t timeout) {
    CHECK(q && timeout == 0, "bounded_owner_queue_poll");
    pthread_mutex_lock(&q->mutex); bool ok = q->used > 0;
    if (ok) { memcpy(value, q->data + q->head * q->size, q->size); q->head = (q->head + 1) % q->count; --q->used; }
    pthread_mutex_unlock(&q->mutex); return ok;
}
void vQueueDelete(QueueHandle_t q) {
    CHECK(pthread_mutex_destroy(&q->mutex) == 0, "queue_not_in_use_at_delete"); free(q);
    pthread_mutex_lock(&driver_lock); CHECK(stats.queues, "queue_accounting"); --stats.queues; pthread_mutex_unlock(&driver_lock);
}
SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    if (!allocation_ok()) return NULL;
    SemaphoreHandle_t sem = calloc(1, sizeof(*sem)); CHECK(sem, "host_mutex_allocation");
    pthread_mutex_init(&sem->mutex, NULL); pthread_cond_init(&sem->cond, NULL); sem->available = true;
    pthread_mutex_lock(&driver_lock); ++stats.semaphores; snapshot_mutex = sem;
    pthread_mutex_unlock(&driver_lock); return sem;
}
BaseType_t xSemaphoreTake(SemaphoreHandle_t sem, TickType_t timeout) {
    CHECK(sem, "valid_mutex"); pthread_mutex_lock(&sem->mutex);
    struct timespec end = until_ms(timeout == portMAX_DELAY ? 10000 : timeout);
    int error = 0;
    while (!sem->available && !error) {
        if (!timeout) { error = ETIMEDOUT; break; }
        error = pthread_cond_timedwait(&sem->cond, &sem->mutex, &end);
    }
    CHECK(!error || error == ETIMEDOUT, "mutex_wait_result");
    bool ok = sem->available; if (ok) sem->available = false;
    pthread_mutex_unlock(&sem->mutex); return ok;
}
BaseType_t xSemaphoreGive(SemaphoreHandle_t sem) {
    pthread_mutex_lock(&sem->mutex); CHECK(!sem->available, "mutex_owned_before_give");
    sem->available = true; pthread_cond_broadcast(&sem->cond); pthread_mutex_unlock(&sem->mutex); return pdTRUE;
}
void vSemaphoreDelete(SemaphoreHandle_t sem) {
    CHECK(sem->available, "mutex_unowned_at_delete");
    CHECK(!pthread_mutex_destroy(&sem->mutex) && !pthread_cond_destroy(&sem->cond), "mutex_not_in_use_at_delete"); free(sem);
    pthread_mutex_lock(&driver_lock); CHECK(stats.semaphores, "mutex_accounting"); --stats.semaphores; pthread_mutex_unlock(&driver_lock);
}
void fixture_lock_snapshot(bool lock) {
    if (lock) CHECK(xSemaphoreTake(snapshot_mutex, 0), "fixture_owns_snapshot_mutex");
    else xSemaphoreGive(snapshot_mutex);
}
EventGroupHandle_t xEventGroupCreate(void) {
    if (!allocation_ok()) return NULL;
    EventGroupHandle_t group = calloc(1, sizeof(*group)); CHECK(group, "host_event_allocation");
    pthread_mutex_init(&group->mutex, NULL); pthread_cond_init(&group->cond, NULL);
    pthread_mutex_lock(&driver_lock); ++stats.events; pthread_mutex_unlock(&driver_lock); return group;
}
EventBits_t xEventGroupSetBits(EventGroupHandle_t group, EventBits_t bits) {
    pthread_mutex_lock(&group->mutex); group->bits |= bits; unsigned result = group->bits;
    pthread_cond_broadcast(&group->cond); pthread_mutex_unlock(&group->mutex); return result;
}
EventBits_t xEventGroupWaitBits(EventGroupHandle_t group, EventBits_t bits,
    BaseType_t clear, BaseType_t all, TickType_t timeout) {
    pthread_mutex_lock(&group->mutex); struct timespec end = until_ms(timeout); int error = 0;
    while (!(all ? (group->bits & bits) == bits : (group->bits & bits) != 0) && !error) {
        if (!timeout) break;
        error = pthread_cond_timedwait(&group->cond, &group->mutex, &end);
    }
    CHECK(!error || error == ETIMEDOUT, "event_wait_result");
    unsigned result = group->bits; if (clear) group->bits &= ~bits;
    pthread_mutex_unlock(&group->mutex); return result;
}
void vEventGroupDelete(EventGroupHandle_t group) {
    CHECK(!pthread_mutex_destroy(&group->mutex) && !pthread_cond_destroy(&group->cond), "event_not_in_use_at_delete"); free(group);
    pthread_mutex_lock(&driver_lock); CHECK(stats.events, "event_accounting"); --stats.events; pthread_mutex_unlock(&driver_lock);
}

static void *task_entry(void *unused) {
    (void)unused; owner_thread = true; task.entry(task.arg);
    CHECK(false, "owner_deleted_itself"); return NULL;
}
BaseType_t xTaskCreatePinnedToCore(void (*entry)(void *), const char *name,
    unsigned stack, void *argument, unsigned priority, TaskHandle_t *out, int core) {
    CHECK(!strcmp(name, "wifi_runtime") && priority == 2 && core == 0 &&
          stack == BOARD_TASK_STACK_WIFI_RUNTIME, "owner_task_profile");
    pthread_mutex_lock(&driver_lock); bool fail = task_failure;
    if (!fail) { ++stats.tasks; stats.requested_stack = stack; stats.requested_priority = priority; stats.requested_core = core; }
    pthread_mutex_unlock(&driver_lock); if (fail) return pdFALSE;
    pthread_mutex_lock(&schedule); CHECK(!task.created || task.joined, "one_owner_thread");
    memset(&task, 0, sizeof(task)); task.created = true; task.entry = entry; task.arg = argument;
    awaited_lap = 1; *out = &task;
    CHECK(pthread_create(&task.thread, NULL, task_entry, NULL) == 0, "owner_pthread_create");
    pthread_mutex_unlock(&schedule); return pdPASS;
}
void vTaskDelay(TickType_t ticks) {
    if (owner_thread) {
        CHECK(ticks == 100, "owner_poll_period"); pthread_mutex_lock(&schedule);
        task.parked = true; ++task.lap; pthread_cond_broadcast(&schedule_changed);
        while (!task.permits) wait_changed(&schedule_changed, &schedule);
        --task.permits; task.parked = false; pthread_mutex_unlock(&schedule);
    } else {
        CHECK(ticks == 1, "cleanup_poll_period");
        pthread_mutex_lock(&schedule); advance_clock(1000);
        if (task.created && !task.exited && task.parked && !task.permits) {
            ++task.permits; pthread_cond_broadcast(&schedule_changed);
        }
        pthread_mutex_unlock(&schedule);
        struct timespec wait = {0, 100000}; nanosleep(&wait, NULL);
    }
}
void vTaskDelete(TaskHandle_t handle) {
    CHECK(!handle && owner_thread, "owner_self_delete"); pthread_mutex_lock(&schedule);
    task.exited = true; task.parked = false; pthread_cond_broadcast(&schedule_changed);
    pthread_mutex_unlock(&schedule); pthread_exit(NULL);
}
void fixture_wait_parked(void) {
    pthread_mutex_lock(&schedule);
    while (!task.exited && !(task.parked && task.lap >= awaited_lap)) wait_changed(&schedule_changed, &schedule);
    pthread_mutex_unlock(&schedule);
}
void fixture_release_step(int64_t delta_us) {
    fixture_wait_parked(); pthread_mutex_lock(&schedule);
    CHECK(!task.exited && !task.permits, "step_has_live_parked_owner");
    awaited_lap = task.lap + 1; advance_clock(delta_us); ++task.permits;
    pthread_cond_broadcast(&schedule_changed); pthread_mutex_unlock(&schedule);
}
void fixture_step(int64_t delta_us) { fixture_release_step(delta_us); fixture_wait_parked(); }
void fixture_join(void) {
    pthread_mutex_lock(&schedule); bool needed = task.created && !task.joined;
    pthread_mutex_unlock(&schedule);
    if (needed) {
        CHECK(pthread_join(task.thread, NULL) == 0, "owner_pthread_join");
        pthread_mutex_lock(&schedule); task.joined = true; pthread_mutex_unlock(&schedule);
        pthread_mutex_lock(&driver_lock); ++stats.joins; pthread_mutex_unlock(&driver_lock);
    }
}

esp_err_t esp_read_mac(uint8_t *mac, int type) {
    CHECK(type == ESP_MAC_WIFI_SOFTAP, "ap_mac_kind"); pthread_mutex_lock(&driver_lock);
    esp_err_t result = api_result_locked(API_MAC); if (!result) memset(mac, 0, 6);
    pthread_mutex_unlock(&driver_lock); return result;
}
esp_netif_t *esp_netif_create_default_wifi_ap(void) {
    if (!allocation_ok()) return NULL;
    esp_netif_t *netif = calloc(1, sizeof(*netif)); CHECK(netif, "host_ap_netif_allocation"); netif->identity = 77;
    pthread_mutex_lock(&driver_lock); ++stats.ap_netifs; pthread_mutex_unlock(&driver_lock); return netif;
}
esp_netif_t *esp_netif_new(const esp_netif_config_t *config) {
    CHECK(config && config->ap, "owner_creates_only_ap_netif");
    return esp_netif_create_default_wifi_ap();
}
void esp_netif_destroy(esp_netif_t *netif) { esp_netif_destroy_default_wifi(netif); }
esp_err_t esp_netif_attach_wifi_ap(esp_netif_t *netif) {
    CHECK(netif && netif->identity == 77, "attach_owned_ap"); pthread_mutex_lock(&driver_lock);
    esp_err_t result = api_result_locked(API_ATTACH); pthread_mutex_unlock(&driver_lock); return result;
}
esp_err_t esp_netif_attach_wifi_station(esp_netif_t *netif) {
    (void)netif; CHECK(false, "runtime_does_not_create_station_netif"); return ESP_FAIL;
}
esp_err_t esp_wifi_set_default_wifi_ap_handlers(void) {
    pthread_mutex_lock(&driver_lock); esp_err_t result = api_result_locked(API_DEFAULT_HANDLERS);
    pthread_mutex_unlock(&driver_lock); return result;
}
esp_err_t esp_wifi_set_default_wifi_sta_handlers(void) {
    CHECK(false, "runtime_does_not_create_station_handlers"); return ESP_FAIL;
}
esp_err_t esp_wifi_clear_default_wifi_driver_and_handlers(esp_netif_t *netif) {
    CHECK(netif && netif->identity == 77, "clear_owned_ap"); pthread_mutex_lock(&driver_lock);
    CHECK(!stats.started, "caller_stopped_driver_before_release");
    esp_err_t result = api_result_locked(API_CLEAR); pthread_mutex_unlock(&driver_lock); return result;
}
void esp_netif_destroy_default_wifi(esp_netif_t *netif) {
    CHECK(netif && netif->identity == 77, "destroy_only_owned_ap_netif"); free(netif);
    pthread_mutex_lock(&driver_lock); CHECK(stats.ap_netifs, "ap_netif_accounting"); --stats.ap_netifs; pthread_mutex_unlock(&driver_lock);
}
bool esp_netif_is_netif_up(esp_netif_t *netif) {
    CHECK(netif && netif->identity == 1, "station_netif_identity"); pthread_mutex_lock(&driver_lock);
    bool up = stats.netif_up; pthread_mutex_unlock(&driver_lock); return up;
}
esp_err_t esp_netif_get_ip_info(esp_netif_t *netif, esp_netif_ip_info_t *info) {
    CHECK(netif && netif->identity == 1, "ip_station_identity"); pthread_mutex_lock(&driver_lock);
    esp_err_t result = api_result_locked(API_IP_INFO); if (!result) info->ip.addr = observed_ip;
    pthread_mutex_unlock(&driver_lock); return result;
}
esp_err_t esp_wifi_set_mode(wifi_mode_t mode) {
    pthread_mutex_lock(&driver_lock); esp_err_t result = api_result_locked(API_MODE);
    if (!result) stats.mode = mode;
    pthread_mutex_unlock(&driver_lock); return result;
}
esp_err_t esp_wifi_set_config(int interface, wifi_config_t *config) {
    CHECK(interface == WIFI_IF_STA || interface == WIFI_IF_AP, "wifi_config_interface");
    pthread_mutex_lock(&driver_lock); esp_err_t result = api_result_locked(interface == WIFI_IF_STA ? API_STA_CONFIG : API_AP_CONFIG);
    if (interface == WIFI_IF_AP) {
        CHECK(!stats.started && config->ap.channel == 1 && config->ap.max_connection == 4 &&
              !strcmp((char *)config->ap.ssid, "yoRadio-000000"), "portal_preconfigured_while_stopped");
    } else {
        CHECK(config->sta.threshold.authmode == WIFI_AUTH_OPEN && config->sta.pmf_cfg.capable &&
              !config->sta.pmf_cfg.required, "station_auth_pmf_policy");
        if (!result) driver_config = *config;
    }
    pthread_mutex_unlock(&driver_lock); return result;
}
esp_err_t esp_wifi_connect(void) {
    pthread_mutex_lock(&driver_lock); esp_err_t result = api_result_locked(API_CONNECT);
    CHECK(stats.started && stats.configs < 512, "bounded_config_trace");
    unsigned row = driver_config.sta.password[3] >= '0' && driver_config.sta.password[3] <= '4'
        ? (unsigned)(driver_config.sta.password[3] - '0') : 99;
    stats.config_rows[stats.configs++] = row; ++stats.connects;
    pthread_mutex_unlock(&driver_lock); return result;
}
esp_err_t esp_wifi_disconnect(void) {
    pthread_mutex_lock(&driver_lock); esp_err_t result = api_result_locked(API_DISCONNECT);
    bool connected = stats.associated;
    if (!result && !hold_disconnect) { stats.associated = stats.netif_up = false; observed_ip = 0; }
    pthread_mutex_unlock(&driver_lock); return result ? result : connected ? ESP_OK : ESP_ERR_WIFI_NOT_CONNECT;
}
esp_err_t esp_wifi_sta_get_ap_info(wifi_ap_record_t *ap) {
    pthread_mutex_lock(&driver_lock); esp_err_t result = api_result_locked(API_AP_INFO);
    if (!result && !stats.associated) result = ESP_ERR_WIFI_NOT_CONNECT;
    if (!result) *ap = observed_ap;
    pthread_mutex_unlock(&driver_lock);
    pthread_mutex_lock(&boundary);
    if (block_query) {
        block_query = false; query_blocked = true; pthread_cond_broadcast(&boundary_changed);
        while (!query_release) wait_changed(&boundary_changed, &boundary);
        query_blocked = false;
    }
    pthread_mutex_unlock(&boundary); return result;
}
void fixture_observe(bool associated, bool up, uint32_t ip, int8_t rssi, unsigned profile) {
    pthread_mutex_lock(&driver_lock); stats.associated = associated; stats.netif_up = up; observed_ip = ip;
    memset(&observed_ap, 0, sizeof(observed_ap));
    memcpy(observed_ap.ssid, driver_config.sta.ssid, sizeof(driver_config.sta.ssid));
    observed_ap.rssi = rssi; observed_ap.bssid[5] = (uint8_t)(profile + 1);
    pthread_mutex_unlock(&driver_lock);
}
esp_err_t esp_event_handler_instance_register(esp_event_base_t base, int32_t id,
    esp_event_handler_t handler, void *arg, esp_event_handler_instance_t *instance) {
    CHECK(id == ESP_EVENT_ANY_ID && (base == WIFI_EVENT || base == IP_EVENT), "event_registration_shape");
    pthread_mutex_lock(&driver_lock); esp_err_t result = api_result_locked(API_REGISTER);
    if (!result) {
        unsigned slot = base == WIFI_EVENT ? 0 : 1; CHECK(!handlers[slot].active, "single_registration");
        handlers[slot].active = true; handlers[slot].handler = handler; handlers[slot].arg = arg; handlers[slot].base = base;
        *instance = &handlers[slot]; ++stats.registrations;
    }
    pthread_mutex_unlock(&driver_lock); return result;
}
esp_err_t esp_event_handler_instance_unregister(esp_event_base_t base, int32_t id,
    esp_event_handler_instance_t instance) {
    CHECK(id == ESP_EVENT_ANY_ID, "event_unregistration_shape"); pthread_mutex_lock(&driver_lock);
    unsigned slot = base == WIFI_EVENT ? 0 : 1;
    CHECK(instance == &handlers[slot] && handlers[slot].active, "unregister_only_owned_handler");
    esp_err_t result = api_result_locked(API_UNREGISTER);
    pthread_mutex_unlock(&driver_lock);
    pthread_mutex_lock(&boundary);
    if (block_unregister) {
        block_unregister = false; unregister_blocked = true; pthread_cond_broadcast(&boundary_changed);
        while (!unregister_release) wait_changed(&boundary_changed, &boundary);
        unregister_blocked = false;
    }
    pthread_mutex_unlock(&boundary);
    pthread_mutex_lock(&driver_lock);
    if (!result) { handlers[slot].active = false; CHECK(stats.registrations, "registration_accounting"); --stats.registrations; }
    pthread_mutex_unlock(&driver_lock); return result;
}
void fixture_emit(esp_event_base_t base, int id, esp_netif_t *netif, uint32_t ip) {
    pthread_mutex_lock(&driver_lock); unsigned slot = base == WIFI_EVENT ? 0 : 1;
    CHECK(handlers[slot].active, "emit_registered_callback");
    esp_event_handler_t callback = handlers[slot].handler; void *argument = handlers[slot].arg;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) stats.started = true;
    pthread_mutex_unlock(&driver_lock);
    ip_event_got_ip_t event = {.esp_netif = netif, .ip_info.ip.addr = ip};
    wifi_event_sta_disconnected_t loss = {.reason = 201};
    callback(argument, base, id, base == IP_EVENT && id == IP_EVENT_STA_GOT_IP ? (void *)&event :
             base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED ? (void *)&loss : NULL);
}
void time_service_notify_network(bool online) {
    pthread_mutex_lock(&driver_lock); stats.time_online = online;
    if (online) ++stats.time_true; else ++stats.time_false; pthread_mutex_unlock(&driver_lock);
}
size_t strlcpy(char *out, const char *in, size_t capacity) {
    size_t size = strlen(in); if (capacity) { size_t copy = size < capacity - 1 ? size : capacity - 1; memcpy(out, in, copy); out[copy] = 0; }
    return size;
}
void fixture_block_ap_info(void) { pthread_mutex_lock(&boundary); block_query = true; query_blocked = query_release = false; pthread_mutex_unlock(&boundary); }
void fixture_wait_ap_info(void) { pthread_mutex_lock(&boundary); while (!query_blocked) wait_changed(&boundary_changed, &boundary); pthread_mutex_unlock(&boundary); }
void fixture_release_ap_info(void) { pthread_mutex_lock(&boundary); query_release = true; pthread_cond_broadcast(&boundary_changed); pthread_mutex_unlock(&boundary); }
void fixture_block_send(void) { pthread_mutex_lock(&boundary); block_send = true; send_blocked = send_release = false; pthread_mutex_unlock(&boundary); }
void fixture_wait_send(void) { pthread_mutex_lock(&boundary); while (!send_blocked) wait_changed(&boundary_changed, &boundary); pthread_mutex_unlock(&boundary); }
void fixture_release_send(void) { pthread_mutex_lock(&boundary); send_release = true; pthread_cond_broadcast(&boundary_changed); pthread_mutex_unlock(&boundary); }
void fixture_block_unregister(void) { pthread_mutex_lock(&boundary); block_unregister = true; unregister_blocked = unregister_release = false; pthread_mutex_unlock(&boundary); }
void fixture_wait_unregister(void) { pthread_mutex_lock(&boundary); while (!unregister_blocked) wait_changed(&boundary_changed, &boundary); pthread_mutex_unlock(&boundary); }
void fixture_release_unregister(void) { pthread_mutex_lock(&boundary); unregister_release = true; pthread_cond_broadcast(&boundary_changed); pthread_mutex_unlock(&boundary); }
