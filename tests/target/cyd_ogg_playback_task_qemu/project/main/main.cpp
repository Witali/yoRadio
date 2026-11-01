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
extern const uint8_t opus20_start[] asm("_binary_fixture20_ogg_start");
extern const uint8_t opus20_end[] asm("_binary_fixture20_ogg_end");
extern const uint8_t opus120_start[] asm("_binary_fixture120_ogg_start");
extern const uint8_t opus120_end[] asm("_binary_fixture120_ogg_end");
extern const uint8_t vorbis_start[] asm("_binary_fixturevorbis_ogg_start");
extern const uint8_t vorbis_end[] asm("_binary_fixturevorbis_ogg_end");
#include "reference.h"
struct link_t { const uint8_t *begin, *end; const char *name, *sha; };
static const link_t opus20={opus20_start,opus20_end,"OPUS20",PCM_OPUS20_SHA};
static const link_t opus120={opus120_start,opus120_end,"OPUS120",PCM_OPUS120_SHA};
static const link_t vorbis={vorbis_start,vorbis_end,"VORBIS",PCM_VORBIS_SHA};
struct fixture_t { const char *name; const link_t *links[3]; size_t count; };
static const fixture_t fixtures[]={
    {"OPUS20",{&opus20,nullptr,nullptr},1},
    {"OPUS120",{&opus120,nullptr,nullptr},1},
    {"VORBIS",{&vorbis,nullptr,nullptr},1},
    {"CHAIN",{&opus20,&vorbis,&opus120},3},
};
static const fixture_t *active;
static size_t fixture_bytes() {
    size_t n=0; for (size_t i=0;i<active->count;++i) n+=(size_t)(active->links[i]->end-active->links[i]->begin);
    return n;
}
static size_t full_pcm() { return active->count*FULL_PCM_SINGLE; }
static unsigned copy_encoded(uint8_t *to,size_t position,size_t bytes) {
    unsigned touched=0;
    for (size_t i=0;i<active->count && bytes;++i) {
        const link_t *link=active->links[i];size_t size=(size_t)(link->end-link->begin);
        if (position>=size) { position-=size;continue; }
        size_t n=std::min(size-position,bytes);
        memcpy(to,link->begin+position,n);to+=n;bytes-=n;position=0;++touched;
    }
    assert(!bytes);return touched;
}
static constexpr EventBits_t TRANSPORT_HELD = 1, PCM_STARTED = 2, ENDED = 4;
static native_state_t state;
static EventGroupHandle_t events;
static SemaphoreHandle_t output_lock, read_gate;
static TaskHandle_t stream_task_handle, decode_task_handle, output_task_handle;
static std::atomic<unsigned> profiles, opens, closes, live_decoders;
static std::atomic<unsigned> http_cleanup, live_clients, process_calls, resize_requests;
static std::atomic<unsigned> writes, metadata_checks, pauses, discard_generation;
static std::atomic<uint32_t> session_generation;
static std::atomic<uint32_t> http_generation;
static std::atomic<size_t> pcm_bytes, client_position;
static std::atomic<bool> hold_after_pcm, hold_reads, cancelling;
static esp_http_client_handle_t current_client;
static esp_audio_simple_dec_handle_t current_decoder;
static unsigned read_index;
// Test-owned observation state; vendor arguments and application state are never changed.
static unsigned observed_instance, handle_calls, handle_resizes, handle_retries, last_capacity;
static bool retry_pending;
static uint8_t *retry_buffer;
static uint32_t retry_length;
static bool retry_eos;
static std::atomic<unsigned> initial_capacity_checks, resize_retry_checks, cross_link_reads, output_flushes;
static uint32_t retry_capacity;
static psa_hash_operation_t segment_hash = PSA_HASH_OPERATION_INIT;
static size_t segment_index, segment_bytes;
static psa_hash_operation_t output_hash = PSA_HASH_OPERATION_INIT;
static bool hash_finished;
static char completed_sha[65];

static void check(bool condition, const char *reason) {
    if (!condition) {
        printf("CYD_OGG_PLAYBACK_TASK_FAILURE %s\n", reason);
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
    check(psa_hash_abort(&segment_hash) == PSA_SUCCESS && psa_hash_setup(&segment_hash,PSA_ALG_SHA_256) == PSA_SUCCESS,"start_segment_hash");
    segment_index=segment_bytes=0;
    cross_link_reads=0;
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
        printf("CYD_OGG_PLAYBACK_TASK_PROFILE role=%s core=%d priority=%u stack=%u\n",
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
    http_generation = snapshot().audio_generation;
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
    client_check(client); return fixture_bytes();
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
    count = std::min(count, (size_t)(fixture_bytes()) - position);
    if (count && copy_encoded((uint8_t *)buffer,position,count)>1) ++cross_link_reads;
    client_position = position + count;
    return (int)count;
}
extern "C" esp_err_t __wrap_esp_http_client_get_and_clear_last_tls_error(
        esp_http_client_handle_t client, int *error, int *flags) {
    client_check(client); if (error) *error = 0; if (flags) *flags = 0; return ESP_OK;
}
extern "C" bool __wrap_esp_http_client_is_complete_data_received(esp_http_client_handle_t client) {
    client_check(client); return !hold_reads && client_position == (size_t)(fixture_bytes());
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
    owner(1,5);
    check(active && !live_decoders && config->dec_type==ESP_AUDIO_SIMPLE_DEC_TYPE_OGG && !config->use_frame_dec,
          "one_public_ogg_container");
    esp_audio_err_t result=__real_esp_audio_simple_dec_open(config,decoder);
    check(result==ESP_AUDIO_ERR_OK && *decoder,"real_vendor_open");
    current_decoder=*decoder;session_generation=snapshot().audio_generation;
    check(session_generation==http_generation,"same_http_generation_for_every_logical_link");
    observed_instance=++opens;handle_calls=handle_resizes=handle_retries=last_capacity=0;
    retry_pending=false;++live_decoders;
    printf("CYD_OGG_PLAYBACK_OBS_OPEN fixture=%s instance=%u generation=%u\n",
           active->name,observed_instance,(unsigned)session_generation.load());
    return result;
}
extern "C" esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t decoder,
        esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *frame) {
    owner(1,5);check(live_decoders==1 && decoder==current_decoder,"live_public_process");
    unsigned call=++handle_calls,global_call=process_calls+1;
    uint32_t capacity=frame->len,raw_length=raw->len;bool eos=raw->eos,was_retry=retry_pending;
    bool unchanged=!was_retry || (raw->buffer==retry_buffer && raw->len==retry_length && raw->eos==retry_eos);
    if (call==1) {
        ++initial_capacity_checks;
        printf("CYD_OGG_PLAYBACK_OBS_INITIAL fixture=%s instance=%u call=%u global_call=%u capacity=%u\n",
               active->name,observed_instance,call,global_call,(unsigned)capacity);
        check(capacity>=12288,"production_initial_capacity_not_reduced");
    }
    esp_audio_err_t result=__real_esp_audio_simple_dec_process(decoder,raw,frame);
    ++process_calls;last_capacity=capacity;retry_pending=false;
    if (was_retry) {
        ++resize_retry_checks;++handle_retries;
        printf("CYD_OGG_PLAYBACK_OBS_RETRY fixture=%s instance=%u call=%u global_call=%u capacity=%u raw_len=%u eos=%u arguments_advanced_once=%u consumed=%u decoded_size=%u needed_size=%u result=%d\n",
               active->name,observed_instance,call,global_call,(unsigned)capacity,(unsigned)raw_length,
               (unsigned)eos,(unsigned)unchanged,(unsigned)raw->consumed,(unsigned)frame->decoded_size,
               (unsigned)frame->needed_size,(int)result);
        check(capacity==retry_capacity && unchanged && result==ESP_AUDIO_ERR_OK,"real_resize_retry");
    }
    if (result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        ++resize_requests;++handle_resizes;
        printf("CYD_OGG_PLAYBACK_OBS_RESIZE fixture=%s instance=%u call=%u global_call=%u raw_len=%u consumed=%u decoded_size=%u needed_size=%u capacity=%u eos=%u result=%d\n",
               active->name,observed_instance,call,global_call,(unsigned)raw_length,(unsigned)raw->consumed,
               (unsigned)frame->decoded_size,(unsigned)frame->needed_size,(unsigned)capacity,(unsigned)eos,(int)result);
        check(raw->consumed<=raw_length && !frame->decoded_size && frame->needed_size>capacity,"actual_public_buffer_error");
        retry_pending=true;retry_buffer=raw->buffer+raw->consumed;retry_length=raw_length-raw->consumed;
        retry_eos=eos;retry_capacity=frame->needed_size;
    }
    check(result==ESP_AUDIO_ERR_OK || result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH,"valid_vendor_process_result");
    return result;
}
extern "C" void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t decoder) {
    owner(1,5);check(live_decoders==1 && decoder==current_decoder,"one_public_close");
    __real_esp_audio_simple_dec_close(decoder);current_decoder=nullptr;--live_decoders;++closes;
    printf("CYD_OGG_PLAYBACK_OBS_CLOSE fixture=%s instance=%u calls=%u resizes=%u retries=%u last_capacity=%u global_calls=%u\n",
           active->name,observed_instance,handle_calls,handle_resizes,handle_retries,last_capacity,process_calls.load());
    check(!retry_pending && handle_retries==handle_resizes,"all_observed_retries_completed_before_close");
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
    check(position <= full_pcm() && size <= full_pcm() - position, "full_output_bounds");
    check(psa_hash_update(&output_hash, data, size) == PSA_SUCCESS, "hash_every_output_byte");
    const uint8_t *at=data;size_t left=size;
    while (left) {
        check(segment_index<active->count,"link_output_bounds");
        size_t n=std::min(left,FULL_PCM_SINGLE-segment_bytes);
        check(psa_hash_update(&segment_hash,at,n)==PSA_SUCCESS,"hash_every_link_byte");
        at+=n;left-=n;segment_bytes+=n;
        if (segment_bytes==FULL_PCM_SINGLE) {
            uint8_t digest[32];size_t bytes=0;char hex[65];
            check(psa_hash_finish(&segment_hash,digest,32,&bytes)==PSA_SUCCESS && bytes==32,"finish_link_hash");
            for (unsigned i=0;i<32;++i) snprintf(hex+2*i,3,"%02x",(unsigned)digest[i]);
            check(!strcmp(hex,active->links[segment_index]->sha),"exact_complete_logical_link_pcm");
            printf("CYD_OGG_PLAYBACK_LINK fixture=%s index=%u codec=%s bytes=%u sha256=%s\n",
                   active->name,(unsigned)segment_index,active->links[segment_index]->name,(unsigned)segment_bytes,hex);
            ++segment_index;segment_bytes=0;
            if (segment_index<active->count) check(psa_hash_setup(&segment_hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"start_next_link_hash");
        }
    }
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
    check(!hash_finished && pcm_bytes == full_pcm() && metadata_checks > 0 && segment_index==active->count && !segment_bytes,"all_logical_links_precede_single_http_eof");
    ++output_flushes;
    check(!live_decoders, "decoder_closed_before_output_eof");
    uint8_t digest[32]; size_t size = 0;
    check(psa_hash_finish(&output_hash, digest, sizeof(digest), &size) == PSA_SUCCESS && size == sizeof(digest),
          "finish_complete_output_hash");
    for (unsigned i = 0; i < sizeof(digest); ++i) snprintf(completed_sha + i * 2, 3, "%02x", (unsigned)digest[i]);
    if (active->count==1) check(!strcmp(completed_sha,active->links[0]->sha),"exact_trimmed_or_vorbis_output_sha256");
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
    check(live_clients == 1 && live_decoders == 1 && pcm_bytes > 0 && pcm_bytes < full_pcm() &&
          client_position < (size_t)(fixture_bytes()), "genuine_partial_stream");
    check(!(xEventGroupGetBits(events) & ENDED), "partial_stream_not_flushed");
}
static void memory_record(const char *stage) {
    printf("CYD_OGG_PLAYBACK_MEMORY fixture=%s stage=%s heap_free=%u heap_min=%u largest_internal=%u\n",
           active->name,stage,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
}
static void print_full_result(const char *prefix) {
    printf("%s fixture=%s pcm_bytes=%u sha256=%s opens=%u closes=%u http_cleanup=%u writes=%u metadata=1\n",
           prefix,active->name,(unsigned)pcm_bytes.load(),completed_sha,opens.load(),closes.load(),http_cleanup.load(),writes.load());
    check(fflush(stdout)==0,"flush_case_record");memory_record("EOF_DONE");
}
static void lifecycle(const fixture_t &fixture) {
    active=&fixture;unsigned base=opens.load(),clients=http_cleanup.load();
    size_t maximum_page=!strcmp(active->name,"OPUS20")?MAX_PAGE_OPUS20:
                        !strcmp(active->name,"OPUS120")?MAX_PAGE_OPUS120:MAX_PAGE_VORBIS;
    printf("CYD_OGG_PLAYBACK_TASK_FIXTURE fixture=%s encoded=%u max_page=%u\n",
           active->name,(unsigned)fixture_bytes(),(unsigned)maximum_page);
    configure(false);play("http://fixture/T0",NATIVE_CODEC_AUTO);complete();
    check(opens==base+1 && closes==base+1 && http_cleanup==clients+1,"first_instance_cleanup");
    print_full_result("CYD_OGG_PLAYBACK_TASK_CASE id=T0 ordered_eof=1");

    configure(true);play("http://fixture/T1-old");held();cancelling=true;audio_service_stop();
    uint32_t stopped_generation=snapshot().audio_generation;
    wait_until([stopped_generation] {return !live_clients && !live_decoders && discard_generation==stopped_generation && input_quiet();},"stop_output_owner_and_public_cleanup");
    uint32_t discarded_generation=discard_generation.load();size_t stopped_pcm=pcm_bytes.load();
    check(stopped_pcm>0 && stopped_pcm<full_pcm() && !strcmp(snapshot().stream_format,"stopped"),"stopped_partial_output");
    memory_record("STOP_QUIET");configure(false);play("http://fixture/T1-reopen");complete();
    check(opens==base+3 && closes==base+3 && http_cleanup==clients+3,"stop_reopen_instance_cleanup");
    char prefix[256];
    snprintf(prefix,sizeof(prefix),"CYD_OGG_PLAYBACK_TASK_CASE id=T1 stop_reopen=1 partial_pcm=%u stop_generation=%u discard_generation=%u",(unsigned)stopped_pcm,(unsigned)stopped_generation,(unsigned)discarded_generation);
    print_full_result(prefix);

    configure(true);play("http://fixture/T2");held();cancelling=true;unsigned previous_pauses=pauses.load();
    audio_maintenance_token_t token={};
    check(audio_service_maintenance_begin(10000,&token)==ESP_OK && token.epoch,"actual_three_owner_maintenance");
    check(!live_clients && !live_decoders && pauses>previous_pauses && input_quiet(),"maintenance_all_owners_quiet");
    size_t held_pcm=pcm_bytes.load();check(held_pcm>0 && held_pcm<full_pcm() && !(xEventGroupGetBits(events)&ENDED),"maintenance_partial_output");
    memory_record("MAINTENANCE_HELD");
    check(audio_service_play("http://fixture/blocked",NATIVE_CODEC_OGG)==ESP_ERR_INVALID_STATE,"play_blocked_while_held");
    auto stale=token;configure(false);
    check(audio_service_maintenance_end(&token,true)==ESP_OK && !token.epoch,"valid_resume_token_consumed");
    check(audio_service_maintenance_end(&stale,true)==ESP_ERR_INVALID_STATE,"stale_resume_token_rejected");complete();
    check(opens==base+5 && closes==base+5 && http_cleanup==clients+5,"resume_instance_cleanup");
    snprintf(prefix,sizeof(prefix),"CYD_OGG_PLAYBACK_TASK_CASE id=T2 maintenance_resume=1 partial_pcm=%u held_quiet=1 play_blocked=1 token_consumed=1 stale_rejected=1",(unsigned)held_pcm);
    print_full_result(prefix);
}
extern "C" void app_main(void) {
    check(xPortGetCoreID()==0 && opus20_end-opus20_start==706319 && opus120_end-opus120_start==707097 && vorbis_end-vorbis_start==703584,"coordinator_and_complete_fixtures");
    printf("CYD_OGG_PLAYBACK_TASK_BOOT actual_audio_service_tu=1 sdk=%s coordinator=0 fixtures=3 chain_links=3 hardware=0\n",esp_get_idf_version());
    events=xEventGroupCreate();output_lock=xSemaphoreCreateMutex();read_gate=xSemaphoreCreateBinary();
    check(events && output_lock && read_gate && psa_crypto_init()==PSA_SUCCESS,"actual_test_sync_and_sha_provider");
    check(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK,"both_idle_watchdogs_enabled");
    native_state_init(&state);check(state.lock && native_health_start() && audio_service_start(&state)==ESP_OK,"actual_audio_service_start");
    check(profiles==3,"three_original_task_profiles");
    for (unsigned i=0;i<3;++i) lifecycle(fixtures[i]);
    active=&fixtures[3];unsigned before_opens=opens.load(),before_clients=http_cleanup.load(),before_flushes=output_flushes.load();
    configure(false);play("http://fixture/chain",NATIVE_CODEC_AUTO);complete();
    check(opens==before_opens+3 && closes==opens && http_cleanup==before_clients+1 && output_flushes==before_flushes+1 && cross_link_reads>0,"three_logical_links_one_http_session_and_eof");
    printf("CYD_OGG_PLAYBACK_TASK_CHAIN links=3 one_http=1 same_generation=1 single_eof=1 cross_link_reads=%u pcm_bytes=%u sha256=%s opens=%u closes=%u http_cleanup=%u\n",cross_link_reads.load(),(unsigned)pcm_bytes.load(),completed_sha,opens.load(),closes.load(),http_cleanup.load());
    memory_record("CHAIN_DONE");
    audio_maintenance_token_t final_token={};check(audio_service_maintenance_begin(10000,&final_token)==ESP_OK,"final_public_quiescence");
    auto faults=native_health_snapshot().faults;
    check(!faults.decoder_failures && !faults.output_failures && !faults.stream_failures && !faults.allocation_failures,"no_actual_pipeline_faults");
    check(opens==18 && closes==18 && http_cleanup==16 && !live_clients && !live_decoders && output_flushes==10 && resize_retry_checks==resize_requests && initial_capacity_checks==opens && input_quiet() && heap_caps_check_integrity_all(true),"final_public_owners_and_heap");
    printf("CYD_OGG_PLAYBACK_TASK_COMPLETE cases=10 actual_audio_service_tu=1 opens=%u closes=%u live_decoders=0 real_http_cleanup=%u live_clients=0 process_calls=%u resize_requests=%u resize_retries=%u initial_capacity_checks=%u output_flushes=%u core_bindings=1 stream_stack_free=%u decode_stack_free=%u output_stack_free=%u heap_free=%u heap_min=%u largest_internal=%u heap_integrity=1 hardware=0\n",
           opens.load(),closes.load(),http_cleanup.load(),process_calls.load(),resize_requests.load(),resize_retry_checks.load(),initial_capacity_checks.load(),output_flushes.load(),
           (unsigned)uxTaskGetStackHighWaterMark(stream_task_handle),(unsigned)uxTaskGetStackHighWaterMark(decode_task_handle),(unsigned)uxTaskGetStackHighWaterMark(output_task_handle),(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
    check(fflush(stdout)==0,"flush_terminal_record");esp_restart();
}
