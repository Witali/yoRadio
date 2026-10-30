// Whole production audio service; synthetic transport and output hardware only.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdio>
#include <cstring>
#include "esp_audio_simple_dec.h"
#include "esp_heap_caps.h"
#include "esp_http_client.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "psa/crypto.h"
extern "C" {
#include "audio_service.h"
#include "native_audio_output.h"
#include "native_network_power.h"
}

#ifdef NDEBUG
#error "The task diagnostic requires assertions"
#endif
extern const uint8_t fixture_start[] asm("_binary_fixture_ogg_start");
extern const uint8_t fixture_end[] asm("_binary_fixture_ogg_end");
static constexpr size_t FULL_PCM = 2112000;
static constexpr char FULL_SHA[] = "e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910";
static constexpr EventBits_t TRANSPORT_HELD = 1, PCM_STARTED = 2, ENDED = 4;
static native_state_t state;
static EventGroupHandle_t events;
static SemaphoreHandle_t output_lock, read_gate;
static TaskHandle_t stream_task_handle, decode_task_handle, output_task_handle;
static std::atomic<unsigned> profiles, opens, closes, live_decoders;
static std::atomic<unsigned> http_cleanup, live_clients, process_calls, resize_requests;
static std::atomic<unsigned> writes, metadata_checks, pauses, discard_generation;
static std::atomic<uint32_t> session_generation;
static std::atomic<size_t> pcm_bytes, client_position;
static std::atomic<bool> hold_after_pcm, hold_reads, cancelling;
static esp_http_client_handle_t current_client;
static esp_audio_simple_dec_handle_t current_decoder;
static unsigned read_index;
static psa_hash_operation_t output_hash = PSA_HASH_OPERATION_INIT;
static bool hash_finished;
static char completed_sha[65];

static void check(bool condition, const char *reason) {
    if (!condition) {
        printf("CYD_VORBIS_TASK_FAILURE %s\n", reason);
        fflush(stdout);
        assert(condition);
    }
}
static void owner(int core, unsigned priority) {
    check(xPortGetCoreID() == core && uxTaskPriorityGet(nullptr) == priority, "actual_owner_profile");
}
template<class Predicate> static void wait_until(Predicate predicate, const char *reason) {
    int64_t deadline = esp_timer_get_time() + 30000000;
    while (!predicate()) {
        check(esp_timer_get_time() < deadline, reason);
        vTaskDelay(1);
    }
}
static native_state_t snapshot() {
    native_state_t result;
    native_state_snapshot(&state, &result);
    return result;
}
static bool input_quiet() {
    auto health = audio_service_input_health();
    return health.available && health.leased && !health.ready && !health.reading && !health.writing;
}
// Caller must first establish EOF, post-Stop output discard, or maintenance HELD.
static void configure(bool hold) {
    check(!live_clients && !live_decoders, "configure_public_owners_quiet");
    xSemaphoreTake(output_lock, portMAX_DELAY);
    check(psa_hash_abort(&output_hash) == PSA_SUCCESS, "abort_previous_hash");
    check(psa_hash_setup(&output_hash, PSA_ALG_SHA_256) == PSA_SUCCESS, "start_output_hash");
    hash_finished = false;
    completed_sha[0] = 0;
    pcm_bytes = 0;
    writes = 0;
    metadata_checks = 0;
    cancelling = false;
    hold_after_pcm = hold;
    hold_reads = false;
    xEventGroupClearBits(events, TRANSPORT_HELD | PCM_STARTED | ENDED);
    xSemaphoreGive(output_lock);
}

extern "C" BaseType_t __real_xTaskCreatePinnedToCore(TaskFunction_t, const char *, uint32_t,
    void *, UBaseType_t, TaskHandle_t *, BaseType_t);
extern "C" BaseType_t __wrap_xTaskCreatePinnedToCore(TaskFunction_t run, const char *name,
        uint32_t stack, void *arg, UBaseType_t priority, TaskHandle_t *task, BaseType_t core) {
    const char *role = nullptr;
    TaskHandle_t *observed = nullptr;
    if (!strcmp(name, "radio_stream")) {
        check(core == 0 && priority == 3 && stack == 6144, "stream_creation_profile");
        role = "stream"; observed = &stream_task_handle;
    } else if (!strcmp(name, "audio_decode")) {
        check(core == 1 && priority == 5 && stack == 16384, "decode_creation_profile");
        role = "decode"; observed = &decode_task_handle;
    } else if (!strcmp(name, "audio_output")) {
        check(core == 1 && priority == 6 && stack == 4096, "output_creation_profile");
        role = "output"; observed = &output_task_handle;
    }
    BaseType_t result = __real_xTaskCreatePinnedToCore(run, name, stack, arg, priority, task, core);
    if (role) {
        check(result == pdPASS && task && *task, "actual_pipeline_task_created");
        *observed = *task;
        ++profiles;
        printf("CYD_VORBIS_TASK_PROFILE role=%s core=%d priority=%u stack=%u\n",
            role, (int)core, (unsigned)priority, (unsigned)stack);
    }
    return result;
}

extern "C" esp_http_client_handle_t __real_esp_http_client_init(const esp_http_client_config_t *);
extern "C" esp_err_t __real_esp_http_client_cleanup(esp_http_client_handle_t);
extern "C" esp_http_client_handle_t __wrap_esp_http_client_init(const esp_http_client_config_t *config) {
    owner(0, 3);
    check(!live_clients && !live_decoders, "old_public_owners_released_before_http_init");
    auto client = __real_esp_http_client_init(config);
    check(client, "real_sdk_http_init");
    current_client = client;
    client_position = 0;
    read_index = 0;
    ++live_clients;
    return client;
}
static void client_check(esp_http_client_handle_t client) {
    owner(0, 3);
    check(client == current_client && live_clients == 1, "real_http_identity");
}
extern "C" esp_err_t __wrap_esp_http_client_open(esp_http_client_handle_t client, int write_bytes) {
    client_check(client); check(!write_bytes, "read_only_transport"); return ESP_OK;
}
extern "C" int64_t __wrap_esp_http_client_fetch_headers(esp_http_client_handle_t client) {
    client_check(client); return fixture_end - fixture_start;
}
extern "C" int __wrap_esp_http_client_get_status_code(esp_http_client_handle_t client) {
    client_check(client); return 200;
}
extern "C" int __wrap_esp_http_client_read(esp_http_client_handle_t client, char *buffer, int capacity) {
    client_check(client);
    if (hold_reads) {
        xEventGroupSetBits(events, TRANSPORT_HELD);
        xSemaphoreTake(read_gate, pdMS_TO_TICKS(10));
        return -ESP_ERR_HTTP_EAGAIN;
    }
    static constexpr size_t sizes[] = {1, 257, 17, 1024, 31, 511};
    size_t position = client_position.load();
    size_t count = std::min<size_t>(capacity, sizes[read_index++ % 6]);
    count = std::min(count, (size_t)(fixture_end - fixture_start) - position);
    if (count) memcpy(buffer, fixture_start + position, count);
    client_position = position + count;
    return (int)count;
}
extern "C" esp_err_t __wrap_esp_http_client_get_and_clear_last_tls_error(
        esp_http_client_handle_t client, int *error, int *flags) {
    client_check(client); if (error) *error = 0; if (flags) *flags = 0; return ESP_OK;
}
extern "C" bool __wrap_esp_http_client_is_complete_data_received(esp_http_client_handle_t client) {
    client_check(client); return !hold_reads && client_position == (size_t)(fixture_end - fixture_start);
}
extern "C" esp_err_t __wrap_esp_http_client_cleanup(esp_http_client_handle_t client) {
    client_check(client);
    esp_err_t result = __real_esp_http_client_cleanup(client);
    check(result == ESP_OK, "real_sdk_http_cleanup");
    current_client = nullptr;
    --live_clients;
    ++http_cleanup;
    return result;
}

extern "C" esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *, esp_audio_simple_dec_handle_t *);
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,
    esp_audio_simple_dec_raw_t *, esp_audio_simple_dec_out_t *);
extern "C" void __real_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t);
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_open(
        esp_audio_simple_dec_cfg_t *config, esp_audio_simple_dec_handle_t *decoder) {
    owner(1, 5);
    check(!live_decoders && config->dec_type == ESP_AUDIO_SIMPLE_DEC_TYPE_OGG && !config->use_frame_dec,
          "one_public_ogg_container");
    esp_audio_err_t result = __real_esp_audio_simple_dec_open(config, decoder);
    check(result == ESP_AUDIO_ERR_OK && *decoder, "real_vendor_open");
    current_decoder = *decoder;
    session_generation = snapshot().audio_generation;
    ++opens; ++live_decoders;
    return result;
}
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t decoder,
        esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *frame) {
    owner(1, 5);
    check(live_decoders == 1 && decoder == current_decoder, "live_public_process");
    esp_audio_err_t result = __real_esp_audio_simple_dec_process(decoder, raw, frame);
    ++process_calls;
    if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) ++resize_requests;
    check(result == ESP_AUDIO_ERR_OK || result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH, "valid_vendor_process_result");
    return result;
}
extern "C" void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t decoder) {
    owner(1, 5);
    check(live_decoders == 1 && decoder == current_decoder, "one_public_close");
    __real_esp_audio_simple_dec_close(decoder);
    current_decoder = nullptr;
    --live_decoders; ++closes;
}

// Only the hardware/backend boundary is synthetic; output_task and its ring are real.
extern "C" bool native_audio_output_supports_pcm(uint8_t bits, uint8_t channels) {
    return channels && (bits == 8 || bits == 16 || bits == 24 || bits == 32);
}
extern "C" esp_err_t native_audio_output_init(void) { return ESP_OK; }
extern "C" const char *native_audio_output_name(void) { return "QEMU vendor PCM integration seam"; }
extern "C" esp_err_t native_audio_output_configure(uint32_t rate) {
    owner(1, 6); check(rate == 48000, "actual_output_rate"); return ESP_OK;
}
extern "C" esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size, uint8_t bits, uint8_t channels) {
    owner(1, 6);
    xSemaphoreTake(output_lock, portMAX_DELAY);
    check(!hash_finished && bits == 16 && channels == 2 && size && size % 4 == 0, "output_pcm_geometry");
    auto info = snapshot();
    if (info.audio_generation == session_generation) {
        check(!strcmp(info.codec, "OGG") && info.sample_rate_hz == 48000 && info.channels == 2 &&
              info.bits_per_sample == 16 && info.pcm_sample_rate_hz == 48000 && info.pcm_channels == 2,
              "actual_source_and_pcm_metadata");
        ++metadata_checks;
    } else check(cancelling, "unexpected_output_generation");
    size_t position = pcm_bytes.load();
    check(position <= FULL_PCM && size <= FULL_PCM - position, "full_output_bounds");
    check(psa_hash_update(&output_hash, data, size) == PSA_SUCCESS, "hash_every_output_byte");
    pcm_bytes = position + size;
    ++writes;
    if (hold_after_pcm.exchange(false)) hold_reads = true;
    xEventGroupSetBits(events, PCM_STARTED);
    xSemaphoreGive(output_lock);
    return ESP_OK;
}
extern "C" esp_err_t native_audio_output_flush_pcm(void) {
    owner(1, 6);
    xSemaphoreTake(output_lock, portMAX_DELAY);
    check(!hash_finished && pcm_bytes == FULL_PCM && metadata_checks > 0, "all_pcm_precedes_eof");
    check(!live_decoders, "decoder_closed_before_output_eof");
    uint8_t digest[32]; size_t size = 0;
    check(psa_hash_finish(&output_hash, digest, sizeof(digest), &size) == PSA_SUCCESS && size == sizeof(digest),
          "finish_complete_output_hash");
    for (unsigned i = 0; i < sizeof(digest); ++i) snprintf(completed_sha + i * 2, 3, "%02x", (unsigned)digest[i]);
    check(!strcmp(completed_sha, FULL_SHA), "exact_vendor_output_sha256");
    hash_finished = true;
    xEventGroupSetBits(events, ENDED);
    xSemaphoreGive(output_lock);
    return ESP_OK;
}
extern "C" void native_audio_output_discard_pcm(void) {
    owner(1, 6);
    xSemaphoreTake(output_lock, portMAX_DELAY);
    discard_generation = snapshot().audio_generation;
    xSemaphoreGive(output_lock);
}
extern "C" esp_err_t native_audio_output_pause(void) {
    owner(1, 6);
    check(!live_clients && !live_decoders, "three_public_owners_released_before_pause");
    ++pauses; return ESP_OK;
}
extern "C" void native_audio_output_request_pause(bool requested) { (void)requested; }
extern "C" void native_audio_output_request_normalizer_reset(void) {}
extern "C" void native_audio_output_idle(void) {}
extern "C" esp_err_t audio_level_led_init(void) { return ESP_OK; }
extern "C" void audio_level_led_update_peak(uint16_t peak) { (void)peak; }
extern "C" void audio_level_led_update_pcm(const uint8_t *data, size_t size, uint8_t bits, uint8_t channels) {
    (void)data; (void)size; (void)bits; (void)channels;
}
extern "C" void network_service_audio_accept(uint32_t generation, bool active) { native_network_power_accept(generation, active); }
extern "C" void network_service_audio_receive(uint32_t generation) { native_network_power_receive(generation); }
extern "C" void network_service_audio_finish(uint32_t generation) { native_network_power_finish(generation); }

static void play(const char *url, native_codec_t codec = NATIVE_CODEC_OGG) {
    check(audio_service_play(url, codec) == ESP_OK, "actual_public_play");
}
static void complete() {
    wait_until([] { return (xEventGroupGetBits(events) & ENDED) != 0; }, "bounded_full_output_eof");
    wait_until([] { return !live_clients && !live_decoders && input_quiet(); }, "bounded_public_cleanup");
    wait_until([] {
        auto info = snapshot();
        return !info.audio_running && !info.audio_pending && !info.audio_failed && !strcmp(info.stream_format, "stream ended");
    }, "public_final_eof_state");
    check(heap_caps_check_integrity_all(true), "complete_heap_integrity");
}
static void held() {
    wait_until([] { return (xEventGroupGetBits(events) & (TRANSPORT_HELD | PCM_STARTED)) ==
                              (TRANSPORT_HELD | PCM_STARTED); }, "hold_after_actual_pcm");
    check(live_clients == 1 && live_decoders == 1 && pcm_bytes > 0 && pcm_bytes < FULL_PCM &&
          client_position < (size_t)(fixture_end - fixture_start), "genuine_partial_stream");
    check(!(xEventGroupGetBits(events) & ENDED), "partial_stream_not_flushed");
}
static void print_full_result(const char *prefix) {
    printf("%s pcm_bytes=%u sha256=%s opens=%u closes=%u http_cleanup=%u writes=%u metadata=1\n",
           prefix, (unsigned)pcm_bytes.load(), completed_sha, opens.load(), closes.load(), http_cleanup.load(), writes.load());
    check(fflush(stdout) == 0, "flush_case_record");
}

extern "C" void app_main(void) {
    check(xPortGetCoreID() == 0 && fixture_end - fixture_start == 703584, "coordinator_and_fixture");
    printf("CYD_VORBIS_TASK_BOOT actual_audio_service_tu=1 sdk=%s coordinator=0 fixture=703584 hardware=0\n", esp_get_idf_version());
    events = xEventGroupCreate(); output_lock = xSemaphoreCreateMutex(); read_gate = xSemaphoreCreateBinary();
    check(events && output_lock && read_gate && psa_crypto_init() == PSA_SUCCESS, "actual_test_sync_and_sha_provider");
    check(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0)) == ESP_OK &&
          esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1)) == ESP_OK, "both_idle_watchdogs_enabled");
    native_state_init(&state);
    check(state.lock && native_health_start() && audio_service_start(&state) == ESP_OK, "actual_audio_service_start");
    check(profiles == 3, "three_original_task_profiles");

    configure(false); play("http://fixture/T0", NATIVE_CODEC_AUTO); complete();
    check(opens == 1 && closes == 1 && http_cleanup == 1, "first_instance_cleanup");
    print_full_result("CYD_VORBIS_TASK_CASE id=T0 ordered_eof=1");

    configure(true); play("http://fixture/T1-old"); held();
    cancelling = true;
    audio_service_stop();
    uint32_t stopped_generation = snapshot().audio_generation;
    wait_until([stopped_generation] {
        return !live_clients && !live_decoders && discard_generation == stopped_generation && input_quiet();
    }, "stop_output_owner_and_public_cleanup");
    uint32_t discarded_generation = discard_generation.load();
    size_t stopped_pcm = pcm_bytes.load();
    check(stopped_pcm > 0 && stopped_pcm < FULL_PCM && !strcmp(snapshot().stream_format, "stopped"), "stopped_partial_output");
    configure(false); play("http://fixture/T1-reopen"); complete();
    check(opens == 3 && closes == 3 && http_cleanup == 3, "stop_reopen_instance_cleanup");
    char prefix[256];
    snprintf(prefix, sizeof(prefix), "CYD_VORBIS_TASK_CASE id=T1 stop_reopen=1 partial_pcm=%u stop_generation=%u discard_generation=%u",
             (unsigned)stopped_pcm, (unsigned)stopped_generation, (unsigned)discarded_generation);
    print_full_result(prefix);

    configure(true); play("http://fixture/T2"); held();
    cancelling = true;
    unsigned previous_pauses = pauses.load();
    audio_maintenance_token_t token = {};
    check(audio_service_maintenance_begin(10000, &token) == ESP_OK && token.epoch, "actual_three_owner_maintenance");
    check(!live_clients && !live_decoders && pauses > previous_pauses && input_quiet(), "maintenance_all_owners_quiet");
    size_t held_pcm = pcm_bytes.load();
    check(held_pcm > 0 && held_pcm < FULL_PCM && !(xEventGroupGetBits(events) & ENDED), "maintenance_partial_output");
    check(audio_service_play("http://fixture/blocked", NATIVE_CODEC_OGG) == ESP_ERR_INVALID_STATE, "play_blocked_while_held");
    auto stale = token;
    configure(false);
    check(audio_service_maintenance_end(&token, true) == ESP_OK && !token.epoch, "valid_resume_token_consumed");
    check(audio_service_maintenance_end(&stale, true) == ESP_ERR_INVALID_STATE, "stale_resume_token_rejected");
    complete();
    check(opens == 5 && closes == 5 && http_cleanup == 5, "resume_instance_cleanup");
    snprintf(prefix, sizeof(prefix), "CYD_VORBIS_TASK_CASE id=T2 maintenance_resume=1 partial_pcm=%u held_quiet=1 play_blocked=1 token_consumed=1 stale_rejected=1",
             (unsigned)held_pcm);
    print_full_result(prefix);

    audio_maintenance_token_t final_token = {};
    check(audio_service_maintenance_begin(10000, &final_token) == ESP_OK, "final_public_quiescence");
    auto faults = native_health_snapshot().faults;
    check(!faults.decoder_failures && !faults.output_failures && !faults.stream_failures && !faults.allocation_failures,
          "no_actual_pipeline_faults");
    check(opens == closes && !live_clients && !live_decoders && resize_requests == 0 && input_quiet() &&
          heap_caps_check_integrity_all(true), "final_public_owners_and_heap");
    printf("CYD_VORBIS_TASK_COMPLETE cases=3 actual_audio_service_tu=1 opens=%u closes=%u live_decoders=0 real_http_cleanup=%u live_clients=0 process_calls=%u resize_requests=%u core_bindings=1 stream_stack_free=%u decode_stack_free=%u output_stack_free=%u heap_free=%u heap_min=%u heap_integrity=1 hardware=0\n",
           opens.load(), closes.load(), http_cleanup.load(), process_calls.load(), resize_requests.load(),
           (unsigned)uxTaskGetStackHighWaterMark(stream_task_handle), (unsigned)uxTaskGetStackHighWaterMark(decode_task_handle),
           (unsigned)uxTaskGetStackHighWaterMark(output_task_handle), (unsigned)esp_get_free_heap_size(),
           (unsigned)esp_get_minimum_free_heap_size());
    check(fflush(stdout) == 0, "flush_terminal_record");
    esp_restart();
}
