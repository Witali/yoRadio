#include "audio_service.h"
#include "web_audio_pause_config.h"
#include "memory_profile.h"
#include "opus_benchmark.h"

#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#include "codec_bridge.h"
#include "http_stream_protocol.h"
#include "stream_input_buffer.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "lwip/netdb.h"
#include "native_audio_output.h"
#include "native_state.h"
#include "network_service.h"

#define AUDIO_URL_BYTES 512U
#define HTTP_HEADER_BYTES 1024U
#define HTTP_HOST_BYTES 96U
#define HTTP_MAX_REDIRECTS 3U
#define SOCKET_READ_TIMEOUT_MS 200U
#define STREAM_IDLE_TIMEOUT_MS ((uint32_t)CONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS)
#define SOCKET_CONNECT_TIMEOUT_MS 10000U
#define SOCKET_WRITE_TIMEOUT_MS 2000U
#define ICY_METADATA_TIMEOUT_MS 5000U
#define HTTP_HEADER_TIMEOUT_MS 10000U
#define HTTP_OPEN_ATTEMPTS 2U
#define CODEC_HEAP_RESERVE_BYTES 1152U
#if CONFIG_YORADIO_OGG_OPUS
/* Raw SILK/Hybrid/CELT board test used at most 3356 of 6144 bytes.
 * Keep 1764 bytes above that measured depth for the native stream adapter;
 * HTTP opening has its own non-inlined frame outside decode. */
#define AUDIO_STACK_BYTES 5120U
#else
#define AUDIO_STACK_BYTES 4096U
#endif
#define STREAM_READ_WAIT_MS ((uint32_t)CONFIG_YORADIO_STREAM_READ_WAIT_MS)
#define STREAM_PREFILL_MS ((uint32_t)CONFIG_YORADIO_STREAM_PREFILL_MS)

static codec_type_t state_codec(helix_codec_kind_t kind) {
    if (kind == HELIX_CODEC_MP3) return CODEC_HELIX_MP3;
    if (kind == HELIX_CODEC_AAC) return CODEC_HELIX_AAC;
    if (kind == HELIX_CODEC_OPUS) return CODEC_OPUS;
    return CODEC_NONE;
}

#ifndef YORADIO_ESP8266_KARADIO_PIPELINE
#define YORADIO_ESP8266_KARADIO_PIPELINE 0
#endif

#if YORADIO_ESP8266_KARADIO_PIPELINE
/* KaRadio's most useful property on the ESP8266 is not the VS1053 driver but
 * its producer/consumer split. Keep the compressed stream in a bounded,
 * statically allocated ring so Wi-Fi can run ahead of Helix without allocating
 * or freeing memory while a station is playing. */
#define KARADIO_RING_BYTES 4096U
#define KARADIO_PREBUFFER_BYTES (KARADIO_RING_BYTES * 3U / 4U)
#define KARADIO_NETWORK_STACK_BYTES 2560U
#define KARADIO_NETWORK_PRIORITY 6U
#define KARADIO_AUDIO_PRIORITY 5U
#define KARADIO_READ_BYTES 1460U
#endif

typedef struct {
    uint32_t generation;
    bool play;
    char url[AUDIO_URL_BYTES];
} audio_command_t;

typedef struct {
    int socket;
    size_t body_size;
    uint32_t metadata_interval;
    uint32_t advertised_bitrate;
    TickType_t last_receive_tick;
    bool chunked;
    http_chunk_decoder_t chunk_decoder;
} http_stream_t;

typedef struct {
    uint32_t generation;
    helix_codec_kind_t codec_kind;
    uint32_t decoder_bitrate;
    uint32_t decoder_sample_rate;
    uint8_t decoder_channels;
    uint64_t measured_bytes;
    int64_t measured_started_us;
} output_context_t;

static const char *TAG = "audio";
static QueueHandle_t s_commands;
static TaskHandle_t s_audio_task;
static volatile uint32_t s_generation;
static uint32_t s_rx_bytes, s_pcm_frames, s_pcm_rate;
static TickType_t s_rx_tick, s_pcm_tick;

void audio_service_health(audio_service_health_t *health) {
    if (!health) return;
    taskENTER_CRITICAL();
    TickType_t now = xTaskGetTickCount();
    *health = (audio_service_health_t){
        .generation = s_generation, .uptime_ms = now * portTICK_PERIOD_MS,
        .rx_bytes = s_rx_bytes, .pcm_frames = s_pcm_frames,
        .sample_rate = s_pcm_rate,
        .rx_age_ms = (now - s_rx_tick) * portTICK_PERIOD_MS,
        .pcm_age_ms = (now - s_pcm_tick) * portTICK_PERIOD_MS,
    };
    taskEXIT_CRITICAL();
    /* Scan the watermark only for a health request, never per audio sample.
     * StackType_t is uint8_t in this ESP8266 SDK: the result is bytes. */
    health->stack_free = s_audio_task ? uxTaskGetStackHighWaterMark(s_audio_task) : 0U;
}
/* Reused for HTTP headers, initial codec detection and ICY metadata. */
static uint8_t s_work[HTTP_HEADER_BYTES];
static char s_host[HTTP_HOST_BYTES];

#if YORADIO_ESP8266_KARADIO_PIPELINE
typedef enum {
    KARADIO_PIPELINE_IDLE,
    KARADIO_PIPELINE_OPENING,
    KARADIO_PIPELINE_STREAMING,
    KARADIO_PIPELINE_EOF,
    KARADIO_PIPELINE_ERROR,
} karadio_pipeline_state_t;

static uint8_t s_karadio_ring[KARADIO_RING_BYTES];
static volatile size_t s_karadio_head;
static volatile size_t s_karadio_tail;
static volatile size_t s_karadio_count;
static volatile bool s_karadio_abort;
static volatile karadio_pipeline_state_t s_karadio_state;
static volatile int s_karadio_error;
static uint32_t s_karadio_generation;
static char s_karadio_url[AUDIO_URL_BYTES];
static TaskHandle_t s_karadio_network_task;
static TaskHandle_t s_karadio_audio_task;

static void karadio_wake(TaskHandle_t task) {
    if (task) xTaskNotifyGive(task);
}

static size_t karadio_ring_count(void) {
    taskENTER_CRITICAL();
    size_t count = s_karadio_count;
    taskEXIT_CRITICAL();
    return count;
}

static void karadio_ring_reset(void) {
    taskENTER_CRITICAL();
    s_karadio_head = 0;
    s_karadio_tail = 0;
    s_karadio_count = 0;
    taskEXIT_CRITICAL();
}

static size_t karadio_probe_stream_start(helix_codec_kind_t *detected) {
    taskENTER_CRITICAL();
    size_t count = s_karadio_count < HTTP_HEADER_BYTES
        ? s_karadio_count : HTTP_HEADER_BYTES;
    /* This is only called before the first decoder read after ring_reset.
     * No consumed bytes can be reused by the producer yet, so the published
     * prefix stays contiguous and immutable while detection inspects it. */
    configASSERT(s_karadio_head == 0);
    taskEXIT_CRITICAL();
    *detected = helix_codec_detect(s_karadio_ring, count);
    return count;
}

static size_t karadio_ring_read(uint8_t *destination, size_t capacity) {
    taskENTER_CRITICAL();
    size_t count = s_karadio_count < capacity ? s_karadio_count : capacity;
    size_t head = s_karadio_head;
    taskEXIT_CRITICAL();
    size_t first = KARADIO_RING_BYTES - head;
    if (first > count) first = count;
    memcpy(destination, s_karadio_ring + head, first);
    if (count > first)
        memcpy(destination + first, s_karadio_ring, count - first);
    taskENTER_CRITICAL();
    s_karadio_head = (head + count) % KARADIO_RING_BYTES;
    s_karadio_count -= count;
    taskEXIT_CRITICAL();
    if (count) karadio_wake(s_karadio_network_task);
    return count;
}

static size_t karadio_ring_write(const uint8_t *source, size_t length) {
    size_t written = 0;
    while (written < length) {
        taskENTER_CRITICAL();
        size_t free_bytes = KARADIO_RING_BYTES - s_karadio_count;
        size_t count = length - written;
        if (count > free_bytes) count = free_bytes;
        size_t tail = s_karadio_tail;
        taskEXIT_CRITICAL();
        if (!count) break;
        size_t first = KARADIO_RING_BYTES - tail;
        if (first > count) first = count;
        memcpy(s_karadio_ring + tail, source + written, first);
        if (count > first)
            memcpy(s_karadio_ring, source + written + first, count - first);
        taskENTER_CRITICAL();
        s_karadio_tail = (tail + count) % KARADIO_RING_BYTES;
        s_karadio_count += count;
        taskEXIT_CRITICAL();
        written += count;
    }
    if (written) karadio_wake(s_karadio_audio_task);
    return written;
}

/* The producer owns tail and the consumer owns head. A consumer can only
 * increase the returned free region, so receiving directly into it is safe
 * and avoids a TCP-to-ring staging copy. */
static size_t karadio_ring_write_window(uint8_t **destination) {
    taskENTER_CRITICAL();
    size_t free_bytes = KARADIO_RING_BYTES - s_karadio_count;
    size_t contiguous = KARADIO_RING_BYTES - s_karadio_tail;
    if (contiguous > free_bytes) contiguous = free_bytes;
    *destination = s_karadio_ring + s_karadio_tail;
    taskEXIT_CRITICAL();
    return contiguous;
}

static void karadio_ring_commit(size_t count) {
    taskENTER_CRITICAL();
    s_karadio_tail = (s_karadio_tail + count) % KARADIO_RING_BYTES;
    s_karadio_count += count;
    taskEXIT_CRITICAL();
    karadio_wake(s_karadio_audio_task);
}
#endif

static void log_audio_stack(const char *event) {
#if YORADIO_ESP8266_AUDIO_PROFILE
    ESP_LOGI(TAG, "Profile stack %s: high_water=%u bytes", event,
             (unsigned)uxTaskGetStackHighWaterMark(NULL));
#else
    (void)event;
#endif
}

static void release_codec(helix_codec_t **codec,
                          helix_codec_kind_t *codec_kind,
                          const char *reason) {
    if (!*codec) {
        *codec_kind = 0;
        return;
    }
#if YORADIO_ESP8266_AUDIO_PROFILE
    ESP_LOGI(TAG, "Profile codec release %s: DRAM=%u IRAM=%u heap=%u",
             reason, (unsigned)helix_codec_dram_used(*codec),
             (unsigned)helix_codec_iram_used(*codec),
             (unsigned)esp_get_free_heap_size());
#else
    (void)reason;
#endif
    helix_codec_destroy(*codec);
    *codec = NULL;
    *codec_kind = 0;
}

static bool generation_current(uint32_t generation) {
    return s_generation == generation;
}

#include "stream_read_wait.h"

static void requeue_if_current(const audio_command_t *command) {
    /* Do not let an old retry overwrite Stop or a newer station between the
     * generation check and the nonblocking, single-slot queue update. */
    taskENTER_CRITICAL();
    if (generation_current(command->generation))
        xQueueOverwrite(s_commands, command);
    taskEXIT_CRITICAL();
}

static uint32_t advance_generation(void) {
    taskENTER_CRITICAL();
    uint32_t generation = ++s_generation;
    taskEXIT_CRITICAL();
    return generation;
}

#include "audio_web_pause.inc"

static bool parse_http_url(const char *url, http_stream_url_t *parts) {
    return http_stream_parse_url(url, parts, s_host, sizeof(s_host));
}

static void set_socket_timeout(int socket_fd, int option, uint32_t timeout_ms) {
    struct timeval timeout = {
        .tv_sec = (time_t)(timeout_ms / 1000U),
        .tv_usec = (suseconds_t)((timeout_ms % 1000U) * 1000U),
    };
    setsockopt(socket_fd, SOL_SOCKET, option, &timeout, sizeof(timeout));
}

static int connect_http(uint16_t port) {
    char port_text[6];
    snprintf(port_text, sizeof(port_text), "%u", port);
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    struct addrinfo *addresses = NULL;
    int dns_error = getaddrinfo(s_host, port_text, &hints, &addresses);
    if (dns_error != 0) {
        ESP_LOGE(TAG, "Stream DNS failed: %d, heap %u", dns_error,
                 (unsigned)esp_get_free_heap_size());
        return -1;
    }
    int socket_fd = -1;
    int saved_error = 0;
    for (struct addrinfo *address = addresses; address; address = address->ai_next) {
        socket_fd = socket(address->ai_family, address->ai_socktype,
                           address->ai_protocol);
        if (socket_fd < 0) { saved_error = errno; continue; }
        set_socket_timeout(socket_fd, SO_RCVTIMEO,
                           SOCKET_CONNECT_TIMEOUT_MS);
        set_socket_timeout(socket_fd, SO_SNDTIMEO,
                           SOCKET_CONNECT_TIMEOUT_MS);
        if (connect(socket_fd, address->ai_addr, address->ai_addrlen) == 0) {
            set_socket_timeout(socket_fd, SO_RCVTIMEO,
                               SOCKET_READ_TIMEOUT_MS);
            set_socket_timeout(socket_fd, SO_SNDTIMEO,
                               SOCKET_WRITE_TIMEOUT_MS);
            int flags = fcntl(socket_fd, F_GETFL, 0);
            if (flags >= 0 &&
                fcntl(socket_fd, F_SETFL, flags | O_NONBLOCK) == 0)
                break;
        }
        saved_error = errno;
        close(socket_fd);
        socket_fd = -1;
    }
    freeaddrinfo(addresses);
    if (socket_fd < 0) errno = saved_error;
    return socket_fd;
}

static bool socket_wait_writable(int socket_fd, uint32_t timeout_ms) {
    fd_set write_set;
    fd_set error_set;
    FD_ZERO(&write_set);
    FD_ZERO(&error_set);
    FD_SET(socket_fd, &write_set);
    FD_SET(socket_fd, &error_set);
    struct timeval timeout = {
        .tv_sec = (time_t)(timeout_ms / 1000U),
        .tv_usec = (suseconds_t)((timeout_ms % 1000U) * 1000U),
    };
    int ready = select(socket_fd + 1, NULL, &write_set, &error_set, &timeout);
    if (ready <= 0 || FD_ISSET(socket_fd, &error_set)) return false;
    int socket_error = 0;
    socklen_t length = sizeof(socket_error);
    return getsockopt(socket_fd, SOL_SOCKET, SO_ERROR, &socket_error,
                      &length) == 0 && socket_error == 0;
}

static bool send_all_bytes(int socket_fd, const char *data, size_t length) {
    int64_t deadline =
        esp_timer_get_time() + SOCKET_WRITE_TIMEOUT_MS * 1000LL;
    while (length) {
        int64_t remaining_us = deadline - esp_timer_get_time();
        if (remaining_us <= 0 ||
            !socket_wait_writable(socket_fd,
                                  (uint32_t)((remaining_us + 999LL) / 1000LL)))
            return false;
        int sent = send(socket_fd, data, length, 0);
        if (sent > 0) {
            data += sent;
            length -= (size_t)sent;
            continue;
        }
        if (sent < 0 && errno == EINTR) continue;
        if (sent < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            vTaskDelay(pdMS_TO_TICKS(1));
            continue;
        }
        return false;
    }
    return true;
}

static bool send_all(int socket_fd, const char *text) {
    return send_all_bytes(socket_fd, text, strlen(text));
}
static int stream_receive(http_stream_t *stream, uint8_t *destination,
                          size_t capacity) {
    while (true) {
        if (stream->chunked &&
            http_chunk_decoder_finished(&stream->chunk_decoder))
            return 0;
        int received = recv(stream->socket, destination, capacity, 0);
        if (received > 0) {
            stream->last_receive_tick = xTaskGetTickCount();
            taskENTER_CRITICAL();
            s_rx_bytes += (uint32_t)received;
            s_rx_tick = xTaskGetTickCount();
            taskEXIT_CRITICAL();
        }
        if (received > 0 && stream->chunked) {
            size_t decoded = 0;
            if (!http_chunk_decode(&stream->chunk_decoder, destination,
                                   (size_t)received, &decoded)) {
                errno = EPROTO;
                return -1;
            }
            if (decoded) return (int)decoded;
            if (http_chunk_decoder_finished(&stream->chunk_decoder)) return 0;
            continue;
        }
        if (received < 0 && errno == EINTR) continue;
        if (received < 0 && (errno == EAGAIN || errno == EWOULDBLOCK) &&
            http_stream_idle_expired(xTaskGetTickCount(),
                stream->last_receive_tick, pdMS_TO_TICKS(STREAM_IDLE_TIMEOUT_MS))) {
            ESP_LOGW(TAG, "No stream data for %u ms", STREAM_IDLE_TIMEOUT_MS);
            errno = ETIMEDOUT;
        }
        return received;
    }
}

/* Keep redirect URL scratch off audio_task's persistent frame:
 * HTTP setup finishes before the nested codec decode path needs its stack. */
__attribute__((noinline))
static int open_http_stream(char *url, http_stream_t *stream) {
    for (unsigned redirect_count = 0;
         redirect_count <= HTTP_MAX_REDIRECTS; ++redirect_count) {
        http_stream_url_t parts;
        if (!parse_http_url(url, &parts)) return -1;
        int socket_fd = connect_http(parts.port);
        if (socket_fd < 0) return -2;
        bool sent = send_all(socket_fd, "GET ") &&
                    (!parts.query_only || send_all(socket_fd, "/")) &&
                    send_all_bytes(socket_fd, parts.target,
                                   parts.target_length) &&
                    send_all(socket_fd, " HTTP/1.1\r\nHost: ") &&
                    send_all_bytes(socket_fd, parts.authority,
                                   parts.authority_length) &&
                    send_all(socket_fd, "\r\n") &&
                    send_all(socket_fd, "User-Agent: yoRadio-esp8266/1\r\n") &&
                    send_all(socket_fd, "Icy-MetaData: 1\r\n") &&
                    send_all(socket_fd, "Connection: keep-alive\r\n\r\n");
        if (!sent) {
            int saved_error = errno;
            close(socket_fd);
            errno = saved_error;
            return -3;
        }
        char redirect_url[AUDIO_URL_BYTES];
        redirect_url[0] = '\0';
        http_response_header_t headers;
        http_response_header_init(&headers);
        size_t body_size = 0;
        int64_t header_deadline =
            esp_timer_get_time() + HTTP_HEADER_TIMEOUT_MS * 1000LL;
        while (!http_response_header_finished(&headers)) {
            /* The deadline also bounds continuously readable trickle headers,
             * not only EAGAIN. No allocation or second receive buffer. */
            if (esp_timer_get_time() >= header_deadline) {
                close(socket_fd);
                errno = ETIMEDOUT;
                return -4;
            }
            size_t input_start = headers.line_bytes;
            int received = recv(socket_fd, s_work + input_start,
                                sizeof(s_work) - input_start, 0);
            if (received > 0) {
#if YORADIO_ESP8266_AUDIO_PROFILE
                if (!headers.total_bytes)
                    ESP_LOGI(TAG, "Profile header RX started: %d bytes",
                             received);
#endif
                size_t consumed = 0;
                int parsed = http_response_header_feed(&headers,
                    s_work, sizeof(s_work), s_work + input_start,
                    (size_t)received, &consumed, redirect_url, sizeof(redirect_url));
                if (parsed == HTTP_RESPONSE_HEADER_ERROR) {
                    close(socket_fd);
                    errno = EPROTO;
                    return -5;
                }
                if (parsed == HTTP_RESPONSE_HEADER_DONE) {
                    body_size = (size_t)received - consumed;
                    memmove(s_work, s_work + input_start + consumed, body_size);
                }
                continue;
            }
            if (received < 0 && errno == EINTR) continue;
            if (received < 0 &&
                (errno == EAGAIN || errno == EWOULDBLOCK) &&
                esp_timer_get_time() < header_deadline) {
                vTaskDelay(pdMS_TO_TICKS(1));
                continue;
            }
#if YORADIO_ESP8266_AUDIO_PROFILE
            ESP_LOGW(TAG,
                     "Profile header RX failed: received=%d total=%u errno=%d",
                     received, (unsigned)headers.total_bytes, errno);
#endif
            int saved_error = received == 0 ? ECONNRESET : errno;
            if (saved_error == EAGAIN || saved_error == EWOULDBLOCK)
                saved_error = ETIMEDOUT;
            close(socket_fd);
            errno = saved_error;
            return -4;
        }
        int status = headers.status;
        bool chunked = http_response_header_chunked(&headers);
        if (status >= 200 && status < 300) {
            if (http_response_header_unsupported_transfer(&headers)) {
                close(socket_fd);
                errno = EPROTO;
                return -9;
            }
            stream->last_receive_tick = xTaskGetTickCount();
            stream->metadata_interval = headers.metadata_interval;
            stream->advertised_bitrate = headers.bitrate;
            stream->chunked = chunked;
            http_chunk_decoder_init(&stream->chunk_decoder);
            if (chunked &&
                !http_chunk_decode(&stream->chunk_decoder, s_work, body_size,
                                   &body_size)) {
                close(socket_fd);
                errno = EPROTO;
                return -9;
            }
            stream->body_size = body_size;
            /* Transfer ownership only after validating the initial body.
             * On failure the caller must not retain a closed/reused fd. */
            stream->socket = socket_fd;
            ESP_LOGI(TAG, "Stream response %d, ICY interval %u%s", status,
                     (unsigned)headers.metadata_interval,
                     chunked ? ", chunked" : "");
            return 0;
        }
        close(socket_fd);
        if ((status != 301 && status != 302 && status != 303 &&
             status != 307 && status != 308) || !redirect_url[0] ||
            redirect_count == HTTP_MAX_REDIRECTS)
            return -6;
        /* A redirect discards its body, so the existing receive scratch can
         * resolve Location without another 512-byte stack buffer. */
        if (!http_stream_resolve_redirect(url, redirect_url, (char *)s_work,
                                          AUDIO_URL_BYTES))
            return -7;
        memcpy(url, s_work, strlen((char *)s_work) + 1U);
    }
    return -8;
}
static void parse_icy_title(size_t size) {
    if (size >= sizeof(s_work)) size = sizeof(s_work) - 1U;
    s_work[size] = '\0';
    const char *key = "StreamTitle='";
    char *start = strstr((char *)s_work, key);
    if (!start) return;
    start += strlen(key);
    char *end = strstr(start, "';");
    if (end) *end = '\0';
    native_state_set_title(start);
}

#if defined(YORADIO_ESP8266_AUDIO_TRACE)
static unsigned s_pcm_trace_count;
static unsigned s_stream_trace_count;

static void trace_pcm_samples(const helix_stream_info_t *info,
                              const int16_t *pcm, size_t samples) {
    if (s_pcm_trace_count >= 4U || !info || !pcm || !samples) return;
    int16_t minimum = INT16_MAX;
    int16_t maximum = INT16_MIN;
    uint32_t hash = 2166136261U;
    for (size_t index = 0; index < samples; ++index) {
        if (pcm[index] < minimum) minimum = pcm[index];
        if (pcm[index] > maximum) maximum = pcm[index];
        hash = (hash ^ (uint16_t)pcm[index]) * 16777619U;
    }
    /* Keep one startup-zero snapshot, then wait for actual decoded audio. */
    if (s_pcm_trace_count && minimum == 0 && maximum == 0) return;
    ESP_LOGI(TAG,
             "AUDIO_TRACE PCM cb=%u rate=%u ch=%u samples=%u "
             "min=%d max=%d fnv=%08x first=%d,%d,%d,%d,%d,%d,%d,%d",
             s_pcm_trace_count++, (unsigned)info->sample_rate,
             (unsigned)info->channels, (unsigned)samples, minimum, maximum,
             (unsigned)hash, pcm[0], samples > 1U ? pcm[1] : 0,
             samples > 2U ? pcm[2] : 0, samples > 3U ? pcm[3] : 0,
             samples > 4U ? pcm[4] : 0, samples > 5U ? pcm[5] : 0,
             samples > 6U ? pcm[6] : 0, samples > 7U ? pcm[7] : 0);
}
#endif

static bool pcm_output(void *opaque, const helix_stream_info_t *info,
                       int16_t *pcm, size_t samples) {
    output_context_t *context = (output_context_t *)opaque;
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
    trace_pcm_samples(info, pcm, samples);
#endif
    if (!generation_current(context->generation)) return false;
    esp_err_t result = native_audio_output_write(
        pcm, samples, info->sample_rate, info->channels);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "PCM output failed: %s",
                 esp_err_to_name(result));
        return false;
    }
    taskENTER_CRITICAL();
    s_pcm_frames += samples / info->channels;
    s_pcm_rate = info->sample_rate;
    s_pcm_tick = xTaskGetTickCount();
    taskEXIT_CRITICAL();
    /* A synthesis callback is now only 32 frames. Publish the first format
     * and actual changes, not the same state/lock work 18 times per granule. */
    if (context->decoder_bitrate != info->bitrate ||
        context->decoder_sample_rate != info->sample_rate ||
        context->decoder_channels != info->channels) {
        context->decoder_bitrate = info->bitrate;
        context->decoder_sample_rate = info->sample_rate;
        context->decoder_channels = info->channels;
        native_state_set_stream(state_codec(context->codec_kind),
                            (info->bitrate + 500U) / 1000U,
                            info->sample_rate, info->channels);
    }
    return true;
}

#if YORADIO_ESP8266_KARADIO_PIPELINE
static bool stream_read_exact(http_stream_t *stream, uint8_t *destination,
                              size_t length, uint32_t generation,
                              int64_t deadline) {
    while (length && generation_current(generation)) {
        int received = stream_receive(stream, destination, length);
        if (received > 0) {
            destination += received;
            length -= (size_t)received;
            continue;
        }
        if (received < 0 &&
            (errno == EAGAIN || errno == EWOULDBLOCK) &&
            esp_timer_get_time() < deadline) {
            if (!stream_wait_after_empty(stream, generation, STREAM_READ_WAIT_MS)) return false;
            continue;
        }
        return false;
    }
    return length == 0 && generation_current(generation);
}

static bool read_icy_metadata(http_stream_t *stream, uint32_t generation) {
    int64_t deadline =
        esp_timer_get_time() + ICY_METADATA_TIMEOUT_MS * 1000LL;
    uint8_t blocks = 0;
    if (!stream_read_exact(stream, &blocks, 1U, generation, deadline))
        return false;
    size_t remaining = (size_t)blocks * 16U;
    size_t retained = 0;
    uint8_t discard[64];
    while (remaining && generation_current(generation)) {
        size_t available = sizeof(s_work) - 1U - retained;
        uint8_t *destination = available ? s_work + retained : discard;
        size_t capacity = available ? available : sizeof(discard);
        size_t count = remaining > capacity ? capacity : remaining;
        if (!stream_read_exact(stream, destination, count, generation,
                               deadline))
            return false;
        if (available) retained += count;
        remaining -= count;
    }
    if (retained && generation_current(generation)) parse_icy_title(retained);
    return remaining == 0;
}

static bool karadio_pipeline_active(void) {
    return s_karadio_state == KARADIO_PIPELINE_OPENING ||
           s_karadio_state == KARADIO_PIPELINE_STREAMING;
}

static void karadio_pipeline_publish(karadio_pipeline_state_t state,
                                     int error) {
    s_karadio_error = error;
    s_karadio_state = state;
    karadio_wake(s_karadio_audio_task);
}

static void karadio_network_worker(void *argument) {
    (void)argument;
    s_karadio_network_task = xTaskGetCurrentTaskHandle();
    for (;;) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        if (s_karadio_state != KARADIO_PIPELINE_OPENING) continue;

        const uint32_t generation = s_karadio_generation;
        http_stream_t stream;
        memset(&stream, 0, sizeof(stream));
        stream.socket = -1;
        int opened = -1;
        for (unsigned attempt = 0;
             attempt < HTTP_OPEN_ATTEMPTS &&
             generation_current(generation) && !s_karadio_abort; ++attempt) {
            opened = open_http_stream(s_karadio_url, &stream);
            if (opened == 0) break;
            if (attempt + 1U < HTTP_OPEN_ATTEMPTS)
                vTaskDelay(pdMS_TO_TICKS(250U));
        }
        if (opened != 0 || !generation_current(generation) ||
            s_karadio_abort) {
            if (stream.socket >= 0) close(stream.socket);
            if (!generation_current(generation) || s_karadio_abort)
                karadio_pipeline_publish(KARADIO_PIPELINE_IDLE, 0);
            else
                karadio_pipeline_publish(KARADIO_PIPELINE_ERROR, opened);
            continue;
        }

        uint32_t audio_until_metadata = stream.metadata_interval;
        if (audio_until_metadata && stream.body_size <= audio_until_metadata)
            audio_until_metadata -= (uint32_t)stream.body_size;
        if (stream.body_size &&
            karadio_ring_write(s_work, stream.body_size) != stream.body_size) {
            close(stream.socket);
            karadio_pipeline_publish(KARADIO_PIPELINE_ERROR, -30);
            continue;
        }
        karadio_pipeline_publish(KARADIO_PIPELINE_STREAMING, 0);

        int stream_result = 0;
        while (generation_current(generation) && !s_karadio_abort) {
            if (stream.metadata_interval && !audio_until_metadata) {
                if (!read_icy_metadata(&stream, generation)) {
                    stream_result = -31;
                    break;
                }
                audio_until_metadata = stream.metadata_interval;
                continue;
            }

            uint8_t *destination = NULL;
            size_t capacity = karadio_ring_write_window(&destination);
            if (!capacity) {
                ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(10));
                continue;
            }
            if (capacity > KARADIO_READ_BYTES) capacity = KARADIO_READ_BYTES;
            if (audio_until_metadata && capacity > audio_until_metadata)
                capacity = audio_until_metadata;
            int received = stream_receive(&stream, destination, capacity);
            if (received > 0) {
                if (!generation_current(generation) || s_karadio_abort) break;
                karadio_ring_commit((size_t)received);
                if (stream.metadata_interval)
                    audio_until_metadata -= (uint32_t)received;
                continue;
            }
            if (received == 0) {
                stream_result = 1;
                break;
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (!stream_wait_after_empty(&stream, generation, STREAM_READ_WAIT_MS)) {
                    stream_result = -32; break;
                }
                continue;
            }
            stream_result = -32;
            break;
        }
        close(stream.socket);
        if (!generation_current(generation) || s_karadio_abort)
            karadio_pipeline_publish(KARADIO_PIPELINE_IDLE, 0);
        else if (stream_result > 0)
            karadio_pipeline_publish(KARADIO_PIPELINE_EOF, 0);
        else
            karadio_pipeline_publish(KARADIO_PIPELINE_ERROR, stream_result);
    }
}

static bool karadio_pipeline_start(const audio_command_t *command) {
    int64_t deadline = esp_timer_get_time() + 11000000LL;
    while (s_karadio_state != KARADIO_PIPELINE_IDLE &&
           esp_timer_get_time() < deadline) {
        karadio_wake(s_karadio_network_task);
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    if (s_karadio_state != KARADIO_PIPELINE_IDLE) return false;
    karadio_ring_reset();
    s_karadio_abort = false;
    s_karadio_error = 0;
    s_karadio_generation = command->generation;
    strncpy(s_karadio_url, command->url, sizeof(s_karadio_url) - 1U);
    s_karadio_url[sizeof(s_karadio_url) - 1U] = '\0';
    s_karadio_state = KARADIO_PIPELINE_OPENING;
    karadio_wake(s_karadio_network_task);
    return true;
}

static void karadio_pipeline_abort(void) {
    if (karadio_pipeline_active()) {
        s_karadio_abort = true;
        karadio_wake(s_karadio_network_task);
        int64_t deadline = esp_timer_get_time() + 11000000LL;
        while (karadio_pipeline_active() && esp_timer_get_time() < deadline)
            vTaskDelay(pdMS_TO_TICKS(1));
    }
    s_karadio_state = KARADIO_PIPELINE_IDLE;
    s_karadio_abort = false;
    karadio_ring_reset();
}

static void audio_task(void *argument) {
    memory_profile_register(MEMORY_AUDIO);
    (void)argument;
    s_karadio_audio_task = xTaskGetCurrentTaskHandle();
    helix_codec_t *codec = NULL;
    helix_codec_kind_t codec_kind = 0;
    log_audio_stack("start");
    while (true) {
        audio_command_t command;
        xQueueReceive(s_commands, &command, portMAX_DELAY);
        if (!command.play) {
            karadio_pipeline_abort();
            native_audio_output_silence();
            release_codec(&codec, &codec_kind, "stop");
            native_state_set_audio(false, false, NULL);
            network_service_set_streaming(false);
            continue;
        }

        native_state_set_audio(false, true, "BUFFERING");
        network_service_set_streaming(true);
        if (!karadio_pipeline_start(&command)) {
            native_state_set_audio(false, false, "NETWORK TASK BUSY");
            network_service_set_streaming(false);
            continue;
        }
        while (generation_current(command.generation) &&
               karadio_pipeline_active() &&
               karadio_ring_count() < KARADIO_PREBUFFER_BYTES)
            ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(10));

        helix_codec_kind_t detected = 0;
        while (generation_current(command.generation)) {
            size_t probe_size = karadio_probe_stream_start(&detected);
            if (detected || probe_size == HTTP_HEADER_BYTES ||
                !karadio_pipeline_active())
                break;
            ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(10));
        }
        if (!detected || !generation_current(command.generation)) {
            bool current = generation_current(command.generation);
            int error = s_karadio_error;
            karadio_pipeline_abort();
            if (current) {
                native_state_set_audio(false, false,
                    error == -7 ? "HTTPS NOT SUPPORTED" :
                    error ? "CONNECTION ERROR" : "UNSUPPORTED STREAM");
                network_service_set_streaming(false);
                release_codec(&codec, &codec_kind, "stream detection error");
            }
            continue;
        }
        codec_kind = detected;
        bool decoder_ready = codec
            ? helix_codec_switch(codec, codec_kind) == 0
            : (codec = helix_codec_create(codec_kind,
                                          CODEC_HEAP_RESERVE_BYTES)) != NULL;
        if (!decoder_ready) {
            karadio_pipeline_abort();
            native_state_set_audio(false, false, "DECODER INIT ERROR");
            network_service_set_streaming(false);
            release_codec(&codec, &codec_kind, "decoder init error");
            continue;
        }

        output_context_t output = {
            .generation = command.generation,
            .codec_kind = codec_kind,
            .measured_started_us = esp_timer_get_time(),
        };
        native_state_set_stream(state_codec(codec_kind),
                                0, 0, 0);
        native_state_set_audio(true, false, NULL);
        int feed = 0;
        while (feed == 0 && generation_current(command.generation)) {
            size_t capacity = 0;
            uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
            if (!destination || !capacity) {
                feed = -20;
                break;
            }
            if (capacity > 1024U) capacity = 1024U;
            size_t received = karadio_ring_read(destination, capacity);
            if (received) {
                output.measured_bytes += received;
                feed = helix_codec_commit(codec, received,
                                          pcm_output, &output);
                int64_t now = esp_timer_get_time();
                if (!output.decoder_bitrate &&
                    now - output.measured_started_us >= 3000000) {
                    uint32_t kbps = (uint32_t)(
                        output.measured_bytes * 8000ULL /
                        (uint64_t)(now - output.measured_started_us));
                    native_state_set_stream(state_codec(codec_kind),
                                            kbps, 0, 0);
                    output.measured_bytes = 0;
                    output.measured_started_us = now;
                }
                continue;
            }
            if (s_karadio_state == KARADIO_PIPELINE_EOF) {
                feed = helix_codec_feed(codec, NULL, 0, true,
                                        pcm_output, &output);
                break;
            }
            if (s_karadio_state == KARADIO_PIPELINE_ERROR) {
                feed = s_karadio_error ? s_karadio_error : -21;
                break;
            }
            ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(5));
        }

        bool current = generation_current(command.generation);
        bool clean_end = current &&
                         s_karadio_state == KARADIO_PIPELINE_EOF && feed == 0;
        karadio_pipeline_abort();
        if (clean_end) {
            native_audio_output_silence();
            native_state_set_audio(false, true, "RECONNECTING");
            vTaskDelay(pdMS_TO_TICKS(250U));
            requeue_if_current(&command);
        } else if (current) {
            native_audio_output_silence();
            if (feed < 0)
                ESP_LOGE(TAG, "KaRadio pipeline stopped: %d", feed);
            release_codec(&codec, &codec_kind,
                          feed < 0 ? "stream error" : "stream end");
            native_state_set_audio(false, false,
                                   feed < 0 ? "AUDIO STREAM ERROR" : NULL);
            network_service_set_streaming(false);
        }
    }
}
#else
#if YORADIO_ESP8266_NETWORK_BENCHMARK
#include "network_benchmark.inc"
#endif
#include "stream_input_refill.inc"
static void audio_task(void *argument) {
    memory_profile_register(MEMORY_AUDIO);
    (void)argument;
#if YORADIO_ESP8266_NETWORK_BENCHMARK
    network_benchmark_run();
#endif
    helix_codec_t *codec = NULL;
    helix_codec_kind_t codec_kind = 0;
    log_audio_stack("start");
    while (true) {
        audio_command_t command;
        audio_web_pause_gate(&codec, &codec_kind);
        if (xQueueReceive(s_commands, &command, AUDIO_WEB_QUEUE_WAIT) != pdPASS)
            continue;
        if (!command.play) {
            native_audio_output_silence();
            release_codec(&codec, &codec_kind, "stop");
            native_state_set_audio(false, false, NULL);
            network_service_set_streaming(false);
            opus_benchmark_run_pending(command.generation, generation_current);
            continue;
        }
        opus_benchmark_cancel_pending();
        native_state_set_audio(false, true, NULL);
        network_service_set_streaming(true);
        http_stream_t stream;
        memset(&stream, 0, sizeof(stream));
        stream.socket = -1;
        if (audio_web_pause_checkpoint(&stream, &command)) continue;
        int opened = -1;
        for (unsigned attempt = 0;
             attempt < HTTP_OPEN_ATTEMPTS &&
             generation_current(command.generation) &&
             !audio_web_pause_requested(); ++attempt) {
            opened = open_http_stream(command.url, &stream);
            if (opened == 0) break;
            /* Reuse a decoder on successful switches, but do not reserve
             * its DRAM throughout repeated failed TCP/DNS handshakes. */
            release_codec(&codec, &codec_kind, "connection retry");
            if (attempt + 1U < HTTP_OPEN_ATTEMPTS) {
                ESP_LOGE(TAG, "Stream open attempt %u failed: stage %d errno %d heap %u",
                         attempt + 1U, opened, errno,
                         (unsigned)esp_get_free_heap_size());
                vTaskDelay(pdMS_TO_TICKS(250U));
            }
        }
        if (audio_web_pause_checkpoint(&stream, &command)) continue;
        if (opened != 0 || !generation_current(command.generation)) {
            if (stream.socket >= 0) close(stream.socket);
            if (generation_current(command.generation)) {
                ESP_LOGE(TAG, "Open stream failed: stage %d errno %d heap %u",
                         opened, errno, (unsigned)esp_get_free_heap_size());
                native_state_set_audio(false, false,
                    opened == -7 ? "HTTPS NOT SUPPORTED" : "CONNECTION ERROR");
                network_service_set_streaming(false);
                release_codec(&codec, &codec_kind, "open error");
            }
            continue;
        }

        size_t detect_size = stream.body_size;
        uint32_t audio_until_metadata = stream.metadata_interval;
        if (audio_until_metadata && detect_size <= audio_until_metadata)
            audio_until_metadata -= (uint32_t)detect_size;
        while (generation_current(command.generation) &&
               !audio_web_pause_requested() &&
               !(codec_kind = helix_codec_detect(s_work, detect_size))) {
            if (detect_size == sizeof(s_work)) break;
            if (stream.metadata_interval && !audio_until_metadata) break;
            size_t wanted = sizeof(s_work) - detect_size;
            if (audio_until_metadata && wanted > audio_until_metadata)
                wanted = audio_until_metadata;
            int received = stream_receive(&stream, s_work + detect_size, wanted);
            if (received > 0) {
                detect_size += (size_t)received;
                if (stream.metadata_interval)
                    audio_until_metadata -= (uint32_t)received;
            } else if (received == 0) {
                break;
            } else if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (!stream_wait_after_empty(&stream, command.generation, STREAM_READ_WAIT_MS)) break;
            } else {
                break;
            }
        }
#if YORADIO_ESP8266_AUDIO_PROFILE
        ESP_LOGI(TAG, "Profile detection: codec=%d bytes=%u free_heap=%u",
                 (int)codec_kind, (unsigned)detect_size,
                 (unsigned)esp_get_free_heap_size());
#endif
        if (audio_web_pause_checkpoint(&stream, &command)) continue;
        if (!codec_kind || !generation_current(command.generation)) {
            close(stream.socket);
            if (generation_current(command.generation)) {
                native_state_set_audio(false, false, "UNSUPPORTED STREAM");
                network_service_set_streaming(false);
                release_codec(&codec, &codec_kind, "unsupported stream");
            }
            continue;
        }
#if YORADIO_ESP8266_AUDIO_PROFILE
        ESP_LOGI(TAG, "Profile decoder switch begin");
#endif
        bool decoder_ready = codec
            ? helix_codec_switch(codec, codec_kind) == 0
            : (codec = helix_codec_create(codec_kind,
                                          CODEC_HEAP_RESERVE_BYTES)) != NULL;
#if YORADIO_ESP8266_AUDIO_PROFILE
        ESP_LOGI(TAG, "Profile decoder switch end: ready=%d free_heap=%u",
                 decoder_ready, (unsigned)esp_get_free_heap_size());
#endif
        if (!decoder_ready) {
            close(stream.socket);
            native_state_set_audio(false, false, "DECODER INIT ERROR");
            network_service_set_streaming(false);
            release_codec(&codec, &codec_kind, "decoder init error");
            continue;
        }
        log_audio_stack("decoder ready");
        output_context_t output = {
            .generation = command.generation,
            .codec_kind = codec_kind,
            .measured_started_us = esp_timer_get_time(),
        };
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
        s_pcm_trace_count = 0;
        s_stream_trace_count = 0;
#endif
        native_state_set_stream(state_codec(codec_kind),
                                stream.advertised_bitrate, 0, 0);
        /* The HTTP prefix aliases the metadata scratch area. Move it to the
         * input queue before stripping ICY, so metadata cannot overwrite audio. */
        stream_icy_t icy = {
            .interval = stream.metadata_interval,
            .audio_left = stream.metadata_interval,
        };
        size_t capacity = 0;
        uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
        int feed = 0;
        if (!destination || detect_size > capacity) {
            feed = -20;
        } else {
            memcpy(destination, s_work, detect_size);
            size_t initial_audio = stream_icy_audio(&icy, destination, detect_size,
                s_work, sizeof(s_work) - 1U, stream_buffer_metadata, &output);
            feed = helix_codec_buffer_commit(codec, initial_audio);
            output.measured_bytes = initial_audio;
        }
        int64_t prefill_started = esp_timer_get_time();
        bool prefill = true, ended = false, playing = false;
        int end_error = 0;
        /* Keep command latency bounded even when a profile uses a longer
         * select() wait. Normal playback never waits just to fill the queue. */
        const uint32_t wait_ms = STREAM_READ_WAIT_MS > 10U ? 10U : STREAM_READ_WAIT_MS;
        while (feed == 0 && generation_current(command.generation) &&
               !audio_web_pause_requested()) {
            int filled = ended ? STREAM_FILL_EOF :
                stream_input_refill(&stream, codec, &icy, &output);
            if (filled == STREAM_FILL_CANCELLED) break;
            if (filled == STREAM_FILL_EOF || filled == STREAM_FILL_TIMEOUT ||
                filled == STREAM_FILL_ERROR) {
                ended = true;
                if (filled == STREAM_FILL_ERROR) end_error = -21;
            }
            if (prefill) {
                if (!stream_prefill_ready(helix_codec_buffered(codec),
                        helix_codec_active_input_capacity(codec), ended,
                        esp_timer_get_time() - prefill_started, STREAM_PREFILL_MS)) {
                    if (filled == STREAM_FILL_AGAIN) {
                        if (!stream_wait_after_empty(&stream, command.generation, wait_ms)) {
                            ended = true;
                            end_error = errno == ETIMEDOUT ? 0 : -21;
                        }
                    } else {
                        vTaskDelay(pdMS_TO_TICKS(1));
                    }
                    continue;
                }
                prefill = false;
                ESP_LOGI(TAG, "Input prefill %u/%u bytes in %u ms",
                         (unsigned)helix_codec_buffered(codec),
                         (unsigned)helix_codec_active_input_capacity(codec),
                         (unsigned)((esp_timer_get_time() - prefill_started) / 1000));
            }

            /* Exactly one compressed frame, then service TCP again. Draining
             * the entire enlarged queue here would defeat read-ahead. */
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
            if (s_stream_trace_count < 24U)
                ESP_LOGI(TAG, "AUDIO_TRACE FRAME begin=%u queued=%u fill=%d",
                         s_stream_trace_count,
                         (unsigned)helix_codec_buffered(codec), filled);
#endif
            int decoded = helix_codec_process_one(codec, pcm_output, &output);
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
            if (s_stream_trace_count < 24U)
                ESP_LOGI(TAG, "AUDIO_TRACE FRAME end=%u queued=%u result=%d",
                         s_stream_trace_count,
                         (unsigned)helix_codec_buffered(codec), decoded);
            ++s_stream_trace_count;
#endif
            if (decoded < 0) {
                feed = decoded;
                break;
            }
            if (!playing && output.decoder_sample_rate &&
                generation_current(command.generation)) {
                playing = true;
                native_state_set_audio(true, false, NULL);
            }
            if (decoded == 0) {
                /* Give idle/watchdog and deferred Wi-Fi work a turn even on
                 * continuously readable streams or malformed input. */
                vTaskDelay(pdMS_TO_TICKS(1));
            } else if (ended) {
                /* Drain all complete queued frames before reconnecting.
                 * Only the final incomplete frame is discarded. */
                feed = end_error;
                /* A transport timeout/EOF is recoverable for live Ogg too.
                 * Reconnect with a reset decoder; do not turn a missing EOS
                 * from a broken TCP connection into a permanent codec error.
                 * Finite-file callers use helix_codec_finish for strict EOS. */
                break;
            } else if (helix_codec_buffered(codec) == helix_codec_active_input_capacity(codec)) {
                feed = -20; /* No progress is possible in a full input queue. */
                break;
            } else if (!stream_wait_after_empty(&stream, command.generation, wait_ms)) {
                ended = true;
                end_error = errno == ETIMEDOUT ? 0 : -21;
            }
            int64_t now = esp_timer_get_time();
            if (!output.decoder_bitrate &&
                now - output.measured_started_us >= 3000000) {
                uint32_t kbps = (uint32_t)(output.measured_bytes * 8000ULL /
                                          (uint64_t)(now - output.measured_started_us));
                native_state_set_stream(state_codec(codec_kind),
                                        kbps, output.decoder_sample_rate,
                                        output.decoder_channels);
                output.measured_bytes = 0;
                output.measured_started_us = now;
            }
        }
        if (audio_web_pause_checkpoint(&stream, &command)) continue;
        int stream_closed = close(stream.socket);
        (void)stream_closed;
        if (feed == 0 && generation_current(command.generation)) {
            ESP_LOGW(TAG,
                     "Radio stream ended or timed out; reconnecting (heap %u)",
                     (unsigned)esp_get_free_heap_size());
            native_audio_output_silence();
            /* Keep Opus's large DRAM blocks after a successful TCP close:
             * rebuilding them after HTTP allocations can fail on fragmentation.
             * The next failed open attempt releases the cached codec,
             * so the existing second attempt still gets a cold handshake.
             * Successful sniffing resets same-kind Opus without allocation;
             * another codec kind still frees the old decoder before its init. */
#if CONFIG_YORADIO_OGG_OPUS
            if (codec_kind != HELIX_CODEC_OPUS || stream_closed != 0)
#endif
            release_codec(&codec, &codec_kind, "stream reconnect");
            native_state_set_audio(false, true, "RECONNECTING");
            vTaskDelay(pdMS_TO_TICKS(250U));
            requeue_if_current(&command);
            continue;
        }
        if (generation_current(command.generation)) {
            native_audio_output_silence();
            if (feed < 0)
                ESP_LOGE(TAG, "Decoder stopped: %d (errno %d)",
                         feed, errno);
            const char *decode_error = helix_codec_error_message(codec_kind, feed);
            release_codec(&codec, &codec_kind,
                          feed < 0 ? "stream error" : "stream end");
            native_state_set_audio(false, false,
                                   decode_error);
            network_service_set_streaming(false);
            log_audio_stack("stream complete");
        }
    }
}
#endif

esp_err_t audio_service_init(void) {
    /* Reserve only the shared 32-bit arena while executable-capable IRAM is
     * still available. Input, PCM and decoder state remain lazy and are not
     * allocated until the stream signature has identified its codec. */
    if (!helix_codec_prepare()) return ESP_ERR_NO_MEM;
    s_commands = xQueueCreate(1, sizeof(audio_command_t));
    if (!s_commands) return ESP_ERR_NO_MEM;
#if YORADIO_ESP8266_KARADIO_PIPELINE
    s_karadio_state = KARADIO_PIPELINE_IDLE;
    if (xTaskCreate(karadio_network_worker, "karadio-net",
                    KARADIO_NETWORK_STACK_BYTES, NULL,
                    KARADIO_NETWORK_PRIORITY, &s_karadio_network_task) !=
        pdPASS) {
        vQueueDelete(s_commands);
        s_commands = NULL;
        return ESP_ERR_NO_MEM;
    }
#define AUDIO_TASK_PRIORITY KARADIO_AUDIO_PRIORITY
#else
#define AUDIO_TASK_PRIORITY 5U
#endif
    if (xTaskCreate(audio_task, "audio", AUDIO_STACK_BYTES, NULL,
                    AUDIO_TASK_PRIORITY, &s_audio_task) !=
        pdPASS) {
#if YORADIO_ESP8266_KARADIO_PIPELINE
        vTaskDelete(s_karadio_network_task);
        s_karadio_network_task = NULL;
#endif
        vQueueDelete(s_commands);
        s_commands = NULL;
        return ESP_ERR_NO_MEM;
    }
#undef AUDIO_TASK_PRIORITY
    ESP_LOGI(TAG, "Codec state is lazy; maximum %u bytes, reserve %u",
             (unsigned)helix_codec_workspace_size(),
             (unsigned)CODEC_HEAP_RESERVE_BYTES);
#if YORADIO_ESP8266_KARADIO_PIPELINE
    ESP_LOGI(TAG, "KaRadio pipeline: network priority %u, audio priority %u, "
                  "ring %u bytes, prebuffer %u bytes",
             KARADIO_NETWORK_PRIORITY, KARADIO_AUDIO_PRIORITY,
             KARADIO_RING_BYTES, KARADIO_PREBUFFER_BYTES);
#endif
    return ESP_OK;
}

esp_err_t audio_service_play(const char *url) {
    if (!url || !url[0] || strlen(url) >= AUDIO_URL_BYTES)
        return ESP_ERR_INVALID_ARG;
    if (strncmp(url, "https://", 8) == 0) {
        native_state_set_audio(false, false, "HTTPS NOT SUPPORTED");
        return ESP_ERR_NOT_SUPPORTED;
    }
    if (strncmp(url, "http://", 7) != 0) return ESP_ERR_NOT_SUPPORTED;
    audio_command_t command = {
        .generation = advance_generation(),
        .play = true,
    };
    strncpy(command.url, url, sizeof(command.url) - 1);
    command.url[sizeof(command.url) - 1] = '\0';
    return xQueueOverwrite(s_commands, &command) == pdPASS ? ESP_OK : ESP_FAIL;
}

esp_err_t audio_service_stop(void) {
    audio_command_t command = {
        .generation = advance_generation(),
        .play = false,
    };
    return xQueueOverwrite(s_commands, &command) == pdPASS ? ESP_OK : ESP_FAIL;
}
