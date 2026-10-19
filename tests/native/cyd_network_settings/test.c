#include "platform.h"
#include "network_settings.h"
#include "network-settings-under-test.c"

static void cold_ram(void) {
    portENTER_CRITICAL(&s_snapshot_lock);
    s_initialized = false; s_revision = 0; memset(&s_settings, 0, sizeof(s_settings));
    portEXIT_CRITICAL(&s_snapshot_lock);
}
static network_settings_t snapshot(uint32_t *revision) {
    network_settings_t settings;
    CHECK(network_settings_snapshot(&settings, revision), "snapshot_available");
    return settings;
}
static void unavailable(void) {
    network_settings_t settings; memset(&settings, 0xa5, sizeof(settings));
    network_settings_t before = settings; uint32_t revision = 0xa5a5a5a5U;
    CHECK(!network_settings_snapshot(&settings, &revision), "uninitialized_snapshot_rejected");
    CHECK(!memcmp(&settings, &before, sizeof(settings)) && revision == 0xa5a5a5a5U,
          "failed_snapshot_preserves_both_outputs");
}
static void defaults(network_settings_t *settings) {
    network_settings_defaults(settings);
    CHECK(network_settings_valid(settings), "valid_defaults");
}
static bool same(const network_settings_t *left, const network_settings_t *right) {
    return !strcmp(left->hostname, right->hostname) && left->ap_timeout_minutes == right->ap_timeout_minutes;
}
static void load_record(const uint8_t *record, size_t size) {
    memcpy(flash_record, record, size); flash_size = size; flash_present = true;
}
static void expect_defaults(void) {
    network_settings_t expected; defaults(&expected); uint32_t revision;
    network_settings_t value = snapshot(&revision);
    CHECK(same(&expected, &value) && revision == 1U, "malformed_record_uses_defaults");
}
typedef struct { network_settings_t *settings; esp_err_t result; } writer_t;
static void *save_thread(void *data) {
    writer_t *writer = data; writer->result = network_settings_save(writer->settings); return NULL;
}
static void *init_thread(void *data) {
    esp_err_t *result = data; *result = network_settings_init(); return NULL;
}
static atomic_bool reader_stop;
static atomic_uint reader_iterations;
static void *reader_thread(void *unused) {
    (void)unused;
    while (!atomic_load(&reader_stop)) {
        uint32_t revision; network_settings_t value = snapshot(&revision);
        CHECK((revision == 1U && !strcmp(value.hostname, "yoradio") && value.ap_timeout_minutes == 0) ||
              (revision == 2U && !strcmp(value.hostname, "First-Radio") && value.ap_timeout_minutes == 1) ||
              (revision == 3U && !strcmp(value.hostname, "Second-Radio") && value.ap_timeout_minutes == 30),
              "coherent_settings_and_revision");
        if (atomic_fetch_add(&reader_iterations, 1) == 0) {
            CHECK(!pthread_mutex_lock(&registry_lock), "registry_lock");
            pthread_cond_broadcast(&registry_cond);
            CHECK(!pthread_mutex_unlock(&registry_lock), "registry_unlock");
        }
    }
    return NULL;
}
static void pause_commit(void) {
    CHECK(!pthread_mutex_lock(&commit_lock), "commit_barrier_lock");
    while (!commit_waiting) pthread_cond_wait(&commit_cond, &commit_lock);
}
static void resume_commit(void) {
    release_commit = true; pthread_cond_broadcast(&commit_cond);
    CHECK(!pthread_mutex_unlock(&commit_lock), "commit_barrier_unlock");
}

int main(int argc, char **argv) {
    CHECK(argc == 2, "case_argument"); const char *name = argv[1];
    network_settings_t a; defaults(&a);
    if (!strcmp(name, "defaults")) {
        network_settings_defaults(NULL);
        CHECK(!network_settings_valid(NULL) && network_settings_save(NULL) == ESP_ERR_INVALID_ARG,
              "null_settings_argument");
        uint32_t revision = 17; CHECK(!network_settings_snapshot(NULL, &revision) && revision == 17,
                                     "null_snapshot_argument");
        unavailable();
        CHECK(network_settings_save(&a) == ESP_ERR_INVALID_STATE && !atomic_load(&nvs_opens),
              "save_requires_initialization");
        CHECK(network_settings_init() == ESP_OK, "initialize_defaults"); expect_defaults();
        unsigned opens = atomic_load(&nvs_opens);
        CHECK(network_settings_init() == ESP_OK && atomic_load(&nvs_opens) == opens,
              "initialization_is_idempotent");
        CHECK(!atomic_load(&nvs_sets) && !atomic_load(&nvs_commits), "defaults_never_write_nvs");
    } else if (!strcmp(name, "validation")) {
        const char *valid[] = {"a", "A", "0", "Radio-42", "9-a", "a--b", "abcdefghijklmnopqrstuvw"};
        for (size_t i = 0; i < sizeof(valid) / sizeof(*valid); ++i) {
            defaults(&a); strcpy(a.hostname, valid[i]); CHECK(network_settings_valid(&a), "valid_ascii_label");
        }
        const char *bad[] = {"", "-a", "a-", ".a", "a.", "a.b", "a..b", "a_b", "a b", "a\tb", "a\nb", "a\rb", "a:b", "a/b", "a\\b", "a\"b", "a\x7f", "\xc3\xa9"};
        for (size_t i = 0; i < sizeof(bad) / sizeof(*bad); ++i) {
            defaults(&a); strcpy(a.hostname, bad[i]);
            CHECK(!network_settings_valid(&a) && network_settings_save(&a) == ESP_ERR_INVALID_ARG,
                  "invalid_hostname_rejected");
        }
        for (unsigned value = 1; value <= 255; ++value) {
            defaults(&a); a.hostname[0] = (char)(unsigned char)value; a.hostname[1] = 0;
            bool valid_byte = (value >= 'A' && value <= 'Z') || (value >= 'a' && value <= 'z') || (value >= '0' && value <= '9');
            CHECK(network_settings_valid(&a) == valid_byte, "ascii_bytes_only");
        }
        for (unsigned length = 1; length < 24; ++length) {
            defaults(&a); memset(a.hostname, 'x', length); a.hostname[length] = 0;
            CHECK(network_settings_valid(&a), "bounded_hostname_lengths");
        }
        memset(a.hostname, 'x', sizeof(a.hostname));
        CHECK(!network_settings_valid(&a), "unterminated_hostname_rejected");
        defaults(&a);
        for (unsigned minutes = 0; minutes <= 255; ++minutes) {
            a.ap_timeout_minutes = (uint8_t)minutes;
            CHECK(network_settings_valid(&a) == (minutes <= 30), "bounded_ap_timeout");
        }
        CHECK(!atomic_load(&nvs_opens), "validation_does_not_touch_nvs");
    } else if (!strcmp(name, "roundtrip")) {
        CHECK(network_settings_init() == ESP_OK, "initialize_defaults");
        memset(a.hostname, 0xa5, sizeof(a.hostname)); strcpy(a.hostname, "Radio-42");
        a.ap_timeout_minutes = 30; network_settings_t input = a;
        CHECK(network_settings_save(&a) == ESP_OK && !memcmp(&a, &input, sizeof(a)), "caller_candidate_unchanged");
        uint32_t revision; network_settings_t value = snapshot(&revision);
        CHECK(revision == 2U && same(&a, &value), "successful_save_advances_revision");
        for (size_t i = strlen(value.hostname) + 1U; i < sizeof(value.hostname); ++i)
            CHECK(!value.hostname[i], "canonical_hostname_tail");
        CHECK(flash_size == 32U && !memcmp(flash_record, "NNET", 4) && flash_record[4] == 1 &&
              flash_record[6] == 30 && !flash_record[5] && !flash_record[7], "explicit_nvs_record_layout");
        cold_ram(); CHECK(network_settings_init() == ESP_OK, "reload_persisted_settings");
        value = snapshot(&revision); CHECK(revision == 1 && same(&a, &value), "same_values_after_reboot");
        CHECK(atomic_load(&nvs_sets) == 1 && atomic_load(&nvs_commits) == 1, "reload_never_rewrites_nvs");
    } else if (!strcmp(name, "invalid-record")) {
        uint8_t original[32]; encode_record(&a, original);
        const unsigned offsets[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 31};
        for (size_t i = 0; i < sizeof(offsets) / sizeof(*offsets); ++i) {
            uint8_t record[32]; memcpy(record, original, sizeof(record)); record[offsets[i]] = 0xff;
            network_settings_t output; memset(&output, 0xa5, sizeof(output)); network_settings_t before = output;
            CHECK(!decode_record(record, &output) && !memcmp(&output, &before, sizeof(output)),
                  "invalid_record_rejected_without_publication");
            load_record(record, sizeof(record)); cold_ram();
            CHECK(network_settings_init() == ESP_OK, "invalid_record_defaults_are_available"); expect_defaults();
        }
        uint8_t hidden[32]; memcpy(hidden, original, 32); hidden[31] = 'x';
        CHECK(!decode_record(hidden, &a), "hidden_hostname_tail_rejected");
        memcpy(hidden, original, 32); memset(hidden + 8, 'x', 24);
        CHECK(!decode_record(hidden, &a), "record_hostname_requires_terminator");
        const size_t sizes[] = {0, 1, 31, 33};
        for (size_t i = 0; i < sizeof(sizes) / sizeof(*sizes); ++i) {
            memset(flash_record, 0, sizeof(flash_record)); flash_size = sizes[i]; flash_present = true;
            cold_ram(); CHECK(network_settings_init() == ESP_OK, "unknown_record_size_defaults"); expect_defaults();
        }
        CHECK(!atomic_load(&nvs_sets) && !atomic_load(&nvs_commits), "malformed_records_not_rewritten");
    } else if (!strcmp(name, "read-errors")) {
        fail_open = ESP_FAIL; CHECK(network_settings_init() == ESP_FAIL, "open_error_propagates"); unavailable();
        fail_open = ESP_OK; uint8_t record[32]; encode_record(&a, record); load_record(record, 32);
        fail_get_at = atomic_load(&nvs_reads) + 1U;
        CHECK(network_settings_init() == ESP_FAIL, "size_read_error_propagates"); unavailable();
        fail_get_at = atomic_load(&nvs_reads) + 2U;
        CHECK(network_settings_init() == ESP_FAIL, "blob_read_error_propagates"); unavailable();
        fail_get_at = 0; successful_short_read = true;
        CHECK(network_settings_init() == ESP_OK, "malformed_short_read_defaults"); expect_defaults();
        CHECK(atomic_load(&nvs_live) == 0 && atomic_load(&nvs_closes) == 3, "all_read_handles_closed");
    } else if (!strcmp(name, "wrong-type")) {
        flash_present = wrong_type = true;
        CHECK(network_settings_init() == ESP_OK, "wrong_type_defaults"); expect_defaults();
        CHECK(!atomic_load(&nvs_sets) && !atomic_load(&nvs_commits), "wrong_type_not_rewritten");
    } else if (!strcmp(name, "save-errors")) {
        CHECK(network_settings_init() == ESP_OK && network_settings_save(&a) == ESP_OK, "initial_persisted_settings");
        network_settings_t original = snapshot(NULL); uint8_t saved[32]; memcpy(saved, flash_record, 32);
        strcpy(a.hostname, "New-Radio"); a.ap_timeout_minutes = 5;
        esp_err_t *faults[] = {&fail_open, &fail_set, &fail_commit};
        for (size_t i = 0; i < sizeof(faults) / sizeof(*faults); ++i) {
            *faults[i] = ESP_FAIL; CHECK(network_settings_save(&a) == ESP_FAIL, "save_error_propagates");
            *faults[i] = ESP_OK; uint32_t revision; network_settings_t value = snapshot(&revision);
            CHECK(revision == 2 && same(&value, &original), "failed_commit_never_publishes");
            CHECK(!memcmp(saved, flash_record, 32), "modeled_nvs_failure_preserves_durable_record");
            CHECK(!atomic_load(&nvs_live), "failed_save_handle_closed");
        }
        unsigned opens = atomic_load(&nvs_opens);
        atomic_store(&forced_timeout, atomic_load(&s_write_lock));
        CHECK(network_settings_save(&a) == ESP_ERR_TIMEOUT && atomic_load(&nvs_opens) == opens,
              "writer_timeout_precedes_nvs");
        atomic_store(&forced_timeout, NULL);
        CHECK(network_settings_save(&a) == ESP_OK, "successful_save_after_failures");
    } else if (!strcmp(name, "mutex-oom")) {
        atomic_store(&fail_mutex, true);
        CHECK(network_settings_init() == ESP_ERR_NO_MEM && !atomic_load(&nvs_opens), "mutex_oom_propagates");
        unavailable(); atomic_store(&fail_mutex, false);
        CHECK(network_settings_init() == ESP_OK, "retry_after_mutex_oom"); expect_defaults();
    } else if (!strcmp(name, "revision-limit")) {
        CHECK(network_settings_init() == ESP_OK, "initialize_defaults");
        portENTER_CRITICAL(&s_snapshot_lock); s_revision = UINT32_MAX; portEXIT_CRITICAL(&s_snapshot_lock);
        unsigned opens = atomic_load(&nvs_opens);
        CHECK(network_settings_save(&a) == ESP_ERR_INVALID_STATE && atomic_load(&nvs_opens) == opens,
              "revision_never_wraps");
        uint32_t revision; (void)snapshot(&revision); CHECK(revision == UINT32_MAX, "exhausted_revision_unchanged");
    } else if (!strcmp(name, "concurrent-init")) {
        CHECK(!pthread_barrier_init(&creation_barrier, NULL, 2), "creation_barrier_init");
        barrier_creation = true; esp_err_t first = ESP_FAIL, second = ESP_FAIL; pthread_t t1, t2;
        CHECK(!pthread_create(&t1, NULL, init_thread, &first) && !pthread_create(&t2, NULL, init_thread, &second), "init_threads");
        CHECK(!pthread_join(t1, NULL) && !pthread_join(t2, NULL), "init_threads_join");
        barrier_creation = false; CHECK(!pthread_barrier_destroy(&creation_barrier), "creation_barrier_destroy");
        CHECK(first == ESP_OK && second == ESP_OK && atomic_load(&semaphore_creates) == 2 &&
              atomic_load(&semaphore_deletes) == 1 && atomic_load(&s_write_lock), "one_published_mutex_loser_freed");
        CHECK(atomic_load(&nvs_opens) == 1, "concurrent_init_reads_once"); expect_defaults();
    } else if (!strcmp(name, "concurrent-save") || !strcmp(name, "candidate-owned")) {
        bool owned = !strcmp(name, "candidate-owned");
        CHECK(network_settings_init() == ESP_OK, "initialize_defaults");
        network_settings_t b = a; strcpy(a.hostname, "First-Radio"); a.ap_timeout_minutes = 1;
        strcpy(b.hostname, "Second-Radio"); b.ap_timeout_minutes = 30;
        hold_commit = true; writer_t one = {&a, ESP_FAIL}, two = {&b, ESP_FAIL}; pthread_t first, second, reader;
        CHECK(!pthread_create(&first, NULL, save_thread, &one), "first_writer"); pause_commit();
        uint32_t revision; network_settings_t value = snapshot(&revision);
        CHECK(revision == 1 && !strcmp(value.hostname, "yoradio") && !value.ap_timeout_minutes,
              "commit_must_precede_publication");
        if (owned) {
            strcpy(a.hostname, "Changed-Caller"); a.ap_timeout_minutes = 7;
            resume_commit(); CHECK(!pthread_join(first, NULL) && one.result == ESP_OK, "owned_writer_join");
            value = snapshot(&revision);
            CHECK(revision == 2 && !strcmp(value.hostname, "First-Radio") && value.ap_timeout_minutes == 1,
                  "candidate_owned_before_wait");
        } else {
            CHECK(!pthread_create(&reader, NULL, reader_thread, NULL) &&
                  !pthread_create(&second, NULL, save_thread, &two), "concurrent_read_write_threads");
            CHECK(!pthread_mutex_lock(&registry_lock), "registry_lock");
            while (atomic_load(&semaphore_takes) < 3 || !atomic_load(&reader_iterations))
                pthread_cond_wait(&registry_cond, &registry_lock);
            CHECK(!pthread_mutex_unlock(&registry_lock), "registry_unlock");
            CHECK(atomic_load(&nvs_commits) == 1, "waiting_writer_has_no_nvs_access");
            resume_commit();
            CHECK(!pthread_join(first, NULL) && !pthread_join(second, NULL) &&
                  one.result == ESP_OK && two.result == ESP_OK, "serialized_writers_join");
            atomic_store(&reader_stop, true); CHECK(!pthread_join(reader, NULL), "reader_join");
            value = snapshot(&revision);
            CHECK(revision == 3 && same(&value, &b) && atomic_load(&nvs_commits) == 2,
                  "serialized_final_settings_match_commits");
            CHECK(atomic_load(&reader_iterations) > 0, "actual_concurrent_snapshot_reader");
        }
    } else CHECK(false, "known_case");
    CHECK(!atomic_load(&nvs_live), "all_nvs_handles_closed");
    cleanup_semaphores();
    printf("PASS %s\n", name);
    return 0;
}
