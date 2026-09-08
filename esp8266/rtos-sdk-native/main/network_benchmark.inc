/* Included after the native HTTP/PCM helpers; diagnostic build only.
 * Use the same socket client, decoder memory and existing audio task.
 * Retain normal web services and neutral DMA even for receive-only tests. */
#include "esp_wifi.h"
#include "esp8266_nodac_i2s.h"
#include "persistent_settings.h"

#define NET_BENCH_SECONDS 20U
typedef struct {
    uint32_t bytes, calls, empty_calls, max_rx_gap, max_app_gap;
    uint32_t max_empty_wait, max_recv_us, max_commit_us, ready_max, ready_probes;
    uint32_t minimum_heap, pcm_frames, pcm_rate;
    uint32_t recv_total_us, recv_positive_us, recv_empty_us;
    uint32_t bins[NET_BENCH_SECONDS];
    int8_t rssi_bins[NET_BENCH_SECONDS];
    uint32_t sample_heap_min, rx_gap_tick_ms, wait_calls;
    int64_t started, last_positive, last_recv_end, empty_since;
    bool output;
} network_bench_stats_t;
static network_bench_stats_t s_net_bench;
static uint32_t s_net_wait_ms = STREAM_READ_WAIT_MS;
static size_t s_net_read_limit = 1024U;
static unsigned s_net_batch = 1U;
static bool net_bench_pcm(void *opaque, const helix_stream_info_t *info,
                          int16_t *pcm, size_t samples);

#if YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
/* Diagnostic-only static snapshots; no extra stack or heap allocation.
 * Task accounting includes interrupts in whichever task was interrupted. */
#define NET_CPU_TASKS 24
static TaskStatus_t s_net_tasks[NET_CPU_TASKS];
static char s_net_task_names[NET_CPU_TASKS][configMAX_TASK_NAME_LEN];
static struct { UBaseType_t id; uint32_t runtime; } s_net_cpu_before[NET_CPU_TASKS];
static UBaseType_t s_net_cpu_count;
static uint32_t s_net_cpu_total;
static void net_cpu_begin(void) {
    s_net_cpu_count = uxTaskGetSystemState(s_net_tasks, NET_CPU_TASKS, &s_net_cpu_total);
    for (UBaseType_t n = 0; n < s_net_cpu_count; ++n) {
        s_net_cpu_before[n].id = s_net_tasks[n].xTaskNumber;
        s_net_cpu_before[n].runtime = s_net_tasks[n].ulRunTimeCounter;
    }
}
static void net_cpu_end(int measurement) {
    uint32_t total = 0;
    /* Copy task names while deletion is suspended, before UART logging. */
    vTaskSuspendAll();
    UBaseType_t count = uxTaskGetSystemState(s_net_tasks, NET_CPU_TASKS, &total);
    for (UBaseType_t n = 0; n < count; ++n)
        snprintf(s_net_task_names[n], sizeof(s_net_task_names[n]), "%s", s_net_tasks[n].pcTaskName);
    xTaskResumeAll();
    ESP_LOGI("net_cpu", "case=%d valid=%u total_us=%u tasks_before=%u tasks_after=%u snapshot_bytes=%u",
             measurement, s_net_cpu_count > 0 && count > 0, total-s_net_cpu_total,
             (unsigned)s_net_cpu_count, (unsigned)count,
             (unsigned)(sizeof(s_net_tasks)+sizeof(s_net_task_names)+sizeof(s_net_cpu_before)));
    for (UBaseType_t n = 0; n < count; ++n) {
        uint32_t before = 0;
        bool found = false;
        for (UBaseType_t k = 0; k < s_net_cpu_count; ++k)
            if (s_net_tasks[n].xTaskNumber == s_net_cpu_before[k].id) {
                before = s_net_cpu_before[k].runtime; found = true; break;
            }
        ESP_LOGI("net_cpu", "case=%d task=%s id=%u runtime_us=%u existed=%u",
                 measurement, s_net_task_names[n], (unsigned)s_net_tasks[n].xTaskNumber,
                 s_net_tasks[n].ulRunTimeCounter-before, found);
    }
}
#endif

static uint32_t net_bench_elapsed(int64_t start) {
    int64_t dt = esp_timer_get_time() - start;
    return dt > 0 ? (uint32_t)dt : 0;
}
static void net_bench_max(uint32_t *value, uint32_t next) {
    if (next > *value) *value = next;
}
static int net_bench_rssi(void) {
    wifi_ap_record_t ap;
    return esp_wifi_sta_get_ap_info(&ap) == ESP_OK ? ap.rssi : -127;
}
/* User-requested recovery, outside measured windows and after closing the
 * stream/decoder. Apply the same rule to every diagnostic variant. */
static void net_bench_recover(unsigned *failures, unsigned next_case) {
    if (*failures < 3U) return;
    ESP_LOGW("net_bench", "recovery begin next_case=%u consecutive_failures=%u", next_case, *failures);
    TickType_t started = xTaskGetTickCount();
    esp_wifi_disconnect();
    vTaskDelay(pdMS_TO_TICKS(250));
    /* The network event handler also reconnects; an already-pending connect
     * is harmless. Do not change credentials, adapter settings or NVS. */
    esp_wifi_connect();
    while (!network_service_connected() &&
           xTaskGetTickCount()-started < pdMS_TO_TICKS(30000))
        vTaskDelay(pdMS_TO_TICKS(250));
    if (!network_service_connected()) {
        ESP_LOGE("net_bench", "recovery failed next_case=%u restarting; retain partial campaign", next_case);
        vTaskDelay(pdMS_TO_TICKS(250));
        esp_restart();
        return;
    }
    vTaskDelay(pdMS_TO_TICKS(1000));
    ESP_LOGW("net_bench", "recovery complete next_case=%u elapsed_ms=%u rssi=%d", next_case,
             (unsigned)((xTaskGetTickCount()-started)*portTICK_PERIOD_MS), net_bench_rssi());
    *failures = 0;
}
#if YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
/* CPU measurement: omit unsupported FIONREAD, repeated gap timestamps and
 * per-poll heap scans. Preserve production read capacity and 1 ms yields. */
static int net_cpu_receive(http_stream_t *stream, helix_codec_t *codec,
                           uint32_t generation) {
    const TickType_t start = xTaskGetTickCount();
    TickType_t last_positive = start;
    unsigned sampled = 0, batch = 0;
    s_net_bench.sample_heap_min = esp_get_free_heap_size();
    while (generation_current(generation) &&
           xTaskGetTickCount()-start < pdMS_TO_TICKS(NET_BENCH_SECONDS * 1000U)) {
        size_t capacity = 0;
        uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
        if (!destination || !capacity) return -200;
        if (capacity > s_net_read_limit) capacity = s_net_read_limit;
        int64_t before = esp_timer_get_time();
        int received = stream_receive(stream, destination, capacity);
        int receive_errno = errno;
        uint32_t elapsed = net_bench_elapsed(before);
        s_net_bench.recv_total_us += elapsed;
        net_bench_max(&s_net_bench.max_recv_us, elapsed);
        ++s_net_bench.calls;
        if (received > 0) {
            s_net_bench.recv_positive_us += elapsed;
            s_net_bench.bytes += received;
            unsigned bin = (xTaskGetTickCount()-start)/pdMS_TO_TICKS(1000U);
            if (bin < NET_BENCH_SECONDS) s_net_bench.bins[bin] += received;
            TickType_t positive_tick = xTaskGetTickCount();
            net_bench_max(&s_net_bench.rx_gap_tick_ms, (positive_tick-last_positive)*portTICK_PERIOD_MS);
            last_positive = positive_tick;
            if (s_net_bench.output) {
                before = esp_timer_get_time();
                int decoded = helix_codec_commit(codec, (size_t)received, net_bench_pcm, NULL);
                net_bench_max(&s_net_bench.max_commit_us, net_bench_elapsed(before));
                if (decoded) return decoded;
            }
        } else if (received < 0 && (receive_errno == EAGAIN || receive_errno == EWOULDBLOCK)) {
            s_net_bench.recv_empty_us += elapsed;
            ++s_net_bench.empty_calls;
            ++s_net_bench.wait_calls;
            if (!stream_wait_after_empty(stream, generation, s_net_wait_ms)) return -errno;
            batch = 0;
        } else return received == 0 ? -201 : -receive_errno;
        if (received > 0 && ++batch >= s_net_batch) {
            vTaskDelay(pdMS_TO_TICKS(1)); batch = 0;
        }
        unsigned second = (xTaskGetTickCount()-start)/pdMS_TO_TICKS(1000U);
        if (second >= sampled && second < NET_BENCH_SECONDS) {
            s_net_bench.rssi_bins[second] = (int8_t)net_bench_rssi();
            uint32_t heap = esp_get_free_heap_size();
            if (heap < s_net_bench.sample_heap_min) s_net_bench.sample_heap_min = heap;
            sampled = second + 1U;
        }
    }
    /* A final sample is not the minimum over the measured interval. */
    s_net_bench.minimum_heap = esp_get_free_heap_size();
    return 0;
}
#endif
static bool net_bench_pcm(void *opaque, const helix_stream_info_t *info,
                           int16_t *pcm, size_t samples) {
    (void)opaque;
    if (!info || !info->channels || !info->sample_rate) return false;
    if (native_audio_output_write(pcm, samples, info->sample_rate,
                                  info->channels) != ESP_OK) return false;
    s_net_bench.pcm_frames += samples / info->channels;
    s_net_bench.pcm_rate = info->sample_rate;
    return true;
}
static void network_benchmark_run(void) {
    const char *tag = "net_bench";
    static const struct { const char *path; helix_codec_kind_t codec; bool output; } cases[] = {
        {"/mp3-320?rate=0", HELIX_CODEC_MP3, false},
#if YORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY
        {"/mp3-320?rate=0", HELIX_CODEC_MP3, false},
        {"/mp3-320?rate=0", HELIX_CODEC_MP3, false},
#else
        {"/mp3-128?rate=128", HELIX_CODEC_MP3, YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 4},
        {"/mp3-320?rate=320", HELIX_CODEC_MP3, YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 4},
        {"/aac-64?rate=64", HELIX_CODEC_AAC, YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 4},
#if !YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
        {"/mp3-128?rate=128", HELIX_CODEC_MP3, true},
        {"/mp3-320?rate=320", HELIX_CODEC_MP3, true},
        {"/aac-64?rate=64", HELIX_CODEC_AAC, true},
#endif
#endif
    };
    const unsigned fixtures = sizeof(cases)/sizeof(cases[0]);
#if YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP
    const unsigned variants = YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 2 ? 4U : 2U;
    const unsigned count = fixtures * variants * YORADIO_ESP8266_NETWORK_BENCHMARK_ROUNDS;
#else
    const unsigned variants = 1, count = fixtures;
#endif
    ESP_LOGI(tag, "begin cases=%u sweep=%u", count, YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP);
    const uint32_t generation = s_generation;
    for (unsigned wait = 0; !network_service_connected() && wait < 120; ++wait)
        vTaskDelay(pdMS_TO_TICKS(1000));
    if (!network_service_connected()) {
        ESP_LOGE(tag, "aborted: no DHCP within 120 seconds");
        return;
    }
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    /* Observe, do not overwrite user settings: a later WebUI Stop/OTA can
     * commit the global runtime snapshot even though this benchmark never
     * calls NVS itself. Both variants use the same saved audio settings. */
    ESP_LOGI(tag, "settings volume=%u balance=%d normalization=%u",
             settings.volume, settings.balance, settings.normalization_enabled);
    network_service_set_streaming(true);
#if YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
    helix_codec_t *baseline_codec = helix_codec_create(HELIX_CODEC_MP3, CODEC_HEAP_RESERVE_BYTES);
    if (!baseline_codec) { network_service_set_streaming(false); return; }
    ESP_LOGI(tag, "connected baseline: 20 seconds, decoder retained, no stream");
    net_cpu_begin();
    vTaskDelay(pdMS_TO_TICKS(NET_BENCH_SECONDS * 1000U));
    net_cpu_end(-1);
    helix_codec_destroy(baseline_codec);
#endif
    unsigned consecutive_failures = 0;
    for (unsigned n = 0; n < count &&
                         generation_current(generation); ++n) {
        net_bench_recover(&consecutive_failures, n);
        unsigned round = n / (fixtures * variants);
        unsigned case_index = (n / variants) % fixtures;
        unsigned variant = (n % variants + round) % variants;
#if YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 1 || YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 4
        s_net_wait_ms = variant ? 25U : 0U;
#elif YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 2
        static const size_t read_limits[] = {1024U, 512U, 1536U, 1024U};
        s_net_wait_ms = 25U;
        s_net_read_limit = read_limits[variant];
        s_net_batch = variant == 3U ? 4U : 1U;
#elif YORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP == 3
        s_net_wait_ms = 25U;
        s_net_batch = variant ? 4U : 1U;
#endif
        char url[AUDIO_URL_BYTES];
        snprintf(url, sizeof(url), "%s%s&case=%u&variant=%u",
                 YORADIO_ESP8266_NETWORK_BENCHMARK_URL, cases[case_index].path, n, variant);
        ESP_LOGI(tag, "case=%u path=%s output=%u begin rssi=%d round=%u fixture=%u variant=%u wait_ms=%u read_limit=%u batch=%u", n,
                 cases[case_index].path, cases[case_index].output, net_bench_rssi(),
                 round, case_index, variant, s_net_wait_ms, (unsigned)s_net_read_limit, s_net_batch);
        /* Hold exactly the decoder allocation needed by the matching
         * playback case even when discarding received compressed bytes. */
        helix_codec_t *codec = helix_codec_create(cases[case_index].codec, CODEC_HEAP_RESERVE_BYTES);
        if (!codec) { ESP_LOGE(tag, "case=%u allocation failed", n); ++consecutive_failures; continue; }
        http_stream_t stream = {.socket = -1};
        int64_t open_start = esp_timer_get_time();
        int error = open_http_stream(url, &stream);
        uint32_t open_us = net_bench_elapsed(open_start);
        if (error || stream.metadata_interval) {
            ESP_LOGE(tag, "case=%u open=%d errno=%d open_us=%u metadata=%u",
                     n, error, errno, open_us, stream.metadata_interval);
            if (stream.socket >= 0) close(stream.socket);
            helix_codec_destroy(codec);
            ++consecutive_failures;
            continue;
        }
        memset(&s_net_bench, 0, sizeof(s_net_bench));
        memset(s_net_bench.rssi_bins, -127, sizeof(s_net_bench.rssi_bins));
        s_net_bench.output = cases[case_index].output;
        s_net_bench.minimum_heap = esp_get_free_heap_size();
        native_audio_output_silence();
        native_audio_output_reset_normalizer();
        native_audio_output_reset_spi_stats();
        uint32_t eof_before = esp8266_nodac_i2s_eofs();
#if YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
        net_cpu_begin();
#endif
        s_net_bench.started = esp_timer_get_time();
        s_net_bench.last_positive = s_net_bench.started;
        s_net_bench.last_recv_end = s_net_bench.started;
        s_net_bench.bytes = stream.body_size;
        s_net_bench.bins[0] = stream.body_size;
        if (cases[case_index].output && stream.body_size)
            error = helix_codec_feed(codec, s_work, stream.body_size, false, net_bench_pcm, NULL);
#if YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
        if (!error) error = net_cpu_receive(&stream, codec, generation);
#else
        while (!error && generation_current(generation) &&
               net_bench_elapsed(s_net_bench.started) < NET_BENCH_SECONDS * 1000000U) {
            size_t capacity = 0;
            uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
            if (!destination || !capacity) { error = -200; break; }
            if (capacity > 1024U) capacity = 1024U;
            int available = 0;
            if (ioctl(stream.socket, FIONREAD, &available) == 0) {
                ++s_net_bench.ready_probes;
                if (available > 0) net_bench_max(&s_net_bench.ready_max, (uint32_t)available);
            }
            int64_t before = esp_timer_get_time();
            net_bench_max(&s_net_bench.max_app_gap,
                          net_bench_elapsed(s_net_bench.last_recv_end));
            int received = stream_receive(&stream, destination, capacity);
            int receive_errno = errno;
            uint32_t recv_us = net_bench_elapsed(before);
            s_net_bench.recv_total_us += recv_us;
            if (received > 0) s_net_bench.recv_positive_us += recv_us;
            else if (received < 0 && (receive_errno == EAGAIN || receive_errno == EWOULDBLOCK))
                s_net_bench.recv_empty_us += recv_us;
            ++s_net_bench.calls;
            net_bench_max(&s_net_bench.max_recv_us, net_bench_elapsed(before));
            s_net_bench.last_recv_end = esp_timer_get_time();
            if (received > 0) {
                net_bench_max(&s_net_bench.max_rx_gap,
                              net_bench_elapsed(s_net_bench.last_positive));
                s_net_bench.last_positive = s_net_bench.last_recv_end;
                if (s_net_bench.empty_since)
                    net_bench_max(&s_net_bench.max_empty_wait,
                                  net_bench_elapsed(s_net_bench.empty_since));
                s_net_bench.empty_since = 0;
                s_net_bench.bytes += received;
                unsigned bin = net_bench_elapsed(s_net_bench.started) / 1000000U;
                if (bin < NET_BENCH_SECONDS) s_net_bench.bins[bin] += received;
                if (cases[case_index].output) {
                    before = esp_timer_get_time();
                    error = helix_codec_commit(codec, received, net_bench_pcm, NULL);
                    net_bench_max(&s_net_bench.max_commit_us, net_bench_elapsed(before));
                }
                vTaskDelay(pdMS_TO_TICKS(1)); /* Same successful-read yield as radio. */
            } else if (received < 0 && (receive_errno == EAGAIN || receive_errno == EWOULDBLOCK)) {
                ++s_net_bench.empty_calls;
                if (!s_net_bench.empty_since) s_net_bench.empty_since = esp_timer_get_time();
                vTaskDelay(pdMS_TO_TICKS(1));
            } else { error = received == 0 ? -201 : -receive_errno; break; }
            uint32_t heap = esp_get_free_heap_size();
            if (heap < s_net_bench.minimum_heap) s_net_bench.minimum_heap = heap;
        }
#endif
        uint32_t wall_us = net_bench_elapsed(s_net_bench.started);
        if (s_net_bench.empty_since)
            net_bench_max(&s_net_bench.max_empty_wait, net_bench_elapsed(s_net_bench.empty_since));
#if !YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
        net_bench_max(&s_net_bench.max_rx_gap, net_bench_elapsed(s_net_bench.last_positive));
#endif
        uint32_t eof_after = esp8266_nodac_i2s_eofs();
        native_audio_output_spi_stats_t dma;
        native_audio_output_get_spi_stats(&dma);
#if YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
        net_cpu_end((int)n);
#endif
        close(stream.socket);
        native_audio_output_silence();
        ESP_LOGI(tag, "case=%u output=%u wall_us=%u bytes=%u open_us=%u error=%d rssi=%d heap_min=%u",
                 n, cases[case_index].output, wall_us, s_net_bench.bytes, open_us, error,
                 net_bench_rssi(), s_net_bench.minimum_heap);
        ESP_LOGI(tag, "case=%u recv_total_us=%u recv_positive_us=%u recv_empty_us=%u",
                 n, s_net_bench.recv_total_us, s_net_bench.recv_positive_us, s_net_bench.recv_empty_us);
#if YORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY
        ESP_LOGI(tag, "case=%u cpu_lean=1 gap_metrics_valid=0 heap_is_final=1", n);
        ESP_LOGI(tag, "case=%u sampled_heap_min=%u rx_gap_tick_ms=%u wait_calls=%u",
                 n, s_net_bench.sample_heap_min, s_net_bench.rx_gap_tick_ms, s_net_bench.wait_calls);
#endif
        ESP_LOGI(tag, "case=%u calls=%u empty=%u rx_gap_us=%u app_gap_us=%u empty_wait_us=%u recv_max_us=%u commit_max_us=%u ready_max=%u ready_probes=%u",
                 n, s_net_bench.calls, s_net_bench.empty_calls, s_net_bench.max_rx_gap,
                 s_net_bench.max_app_gap, s_net_bench.max_empty_wait, s_net_bench.max_recv_us,
                 s_net_bench.max_commit_us, s_net_bench.ready_max, s_net_bench.ready_probes);
        ESP_LOGI(tag, "case=%u pcm_frames=%u rate=%u eof=%u underrun=%u stack=%u",
                 n, s_net_bench.pcm_frames, s_net_bench.pcm_rate,
                 eof_after-eof_before, dma.queue_empty_events,
                 (unsigned)uxTaskGetStackHighWaterMark(NULL));
        for (unsigned bin = 0; bin < NET_BENCH_SECONDS; ++bin)
            ESP_LOGI(tag, "case=%u second=%u bytes=%u rssi=%d", n, bin, s_net_bench.bins[bin], s_net_bench.rssi_bins[bin]);
        helix_codec_destroy(codec);
        consecutive_failures = error ? consecutive_failures + 1U : 0U;
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    network_service_set_streaming(false);
    native_state_set_audio(false, false, NULL);
    ESP_LOGI(tag, "complete");
}
