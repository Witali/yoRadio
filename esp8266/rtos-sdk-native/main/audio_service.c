#include "audio_service.h"

#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

#include "codec_bridge.h"
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
#define HTTP_HEADER_TIMEOUT_MS 10000U
#define HTTP_OPEN_ATTEMPTS 2U
#define CODEC_HEAP_RESERVE_BYTES 2048U
#define AUDIO_STACK_BYTES 5120U

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
} http_stream_t;

typedef struct {
    uint32_t generation;
    helix_codec_kind_t codec_kind;
    uint32_t decoder_bitrate;
    uint64_t measured_bytes;
    int64_t measured_started_us;
} output_context_t;

static const char *TAG = "audio";
static QueueHandle_t s_commands;
static volatile uint32_t s_generation;
/* Reused for HTTP headers, initial codec detection and ICY metadata. */
static uint8_t s_work[HTTP_HEADER_BYTES];
static char s_host[HTTP_HOST_BYTES];

static bool generation_current(uint32_t generation) {
    return s_generation == generation;
}

static uint32_t advance_generation(void) {
    taskENTER_CRITICAL();
    uint32_t generation = ++s_generation;
    taskEXIT_CRITICAL();
    return generation;
}

static bool parse_http_url(const char *url, uint16_t *port,
                           const char **path) {
    if (!url || strncmp(url, "http://", 7) != 0) return false;
    const char *host = url + 7;
    const char *slash = strchr(host, '/');
    const char *end = slash ? slash : host + strlen(host);
    const char *colon = NULL;
    for (const char *cursor = host; cursor < end; ++cursor)
        if (*cursor == ':') colon = cursor;
    const char *host_end = colon ? colon : end;
    size_t host_length = (size_t)(host_end - host);
    if (!host_length || host_length >= sizeof(s_host)) return false;
    memcpy(s_host, host, host_length);
    s_host[host_length] = '\0';
    unsigned long parsed_port = 80;
    if (colon) {
        char *tail = NULL;
        parsed_port = strtoul(colon + 1, &tail, 10);
        if (tail != end || !parsed_port || parsed_port > 65535) return false;
    }
    *port = (uint16_t)parsed_port;
    *path = slash ? slash : "/";
    return true;
}

static int connect_http(uint16_t port) {
    char port_text[6];
    snprintf(port_text, sizeof(port_text), "%u", port);
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    struct addrinfo *addresses = NULL;
    if (getaddrinfo(s_host, port_text, &hints, &addresses) != 0) return -1;
    int socket_fd = -1;
    for (struct addrinfo *address = addresses; address; address = address->ai_next) {
        socket_fd = socket(address->ai_family, address->ai_socktype,
                           address->ai_protocol);
        if (socket_fd < 0) continue;
        struct timeval timeout = {
            .tv_sec = 0,
            .tv_usec = SOCKET_READ_TIMEOUT_MS * 1000,
        };
        setsockopt(socket_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout,
                   sizeof(timeout));
        if (connect(socket_fd, address->ai_addr, address->ai_addrlen) == 0)
            break;
        close(socket_fd);
        socket_fd = -1;
    }
    freeaddrinfo(addresses);
    return socket_fd;
}

static bool send_all(int socket_fd, const char *text) {
    size_t remaining = strlen(text);
    while (remaining) {
        int sent = send(socket_fd, text, remaining, 0);
        if (sent <= 0) return false;
        text += sent;
        remaining -= (size_t)sent;
    }
    return true;
}

static uint8_t *find_header_end(uint8_t *data, size_t size,
                                size_t *header_size) {
    for (size_t index = 0; index + 3 < size; ++index) {
        if (data[index] == '\r' && data[index + 1] == '\n' &&
            data[index + 2] == '\r' && data[index + 3] == '\n') {
            *header_size = index + 4;
            return data + index;
        }
    }
    for (size_t index = 0; index + 1 < size; ++index) {
        if (data[index] == '\n' && data[index + 1] == '\n') {
            *header_size = index + 2;
            return data + index;
        }
    }
    return NULL;
}

static int parse_headers(size_t header_size, char *redirect,
                         size_t redirect_size, uint32_t *metadata_interval,
                         uint32_t *bitrate) {
    s_work[header_size - 1] = '\0';
    char *cursor = (char *)s_work;
    char *line_end = strchr(cursor, '\n');
    if (!line_end) return -1;
    *line_end = '\0';
    int status = 0;
    if (strncmp(cursor, "ICY ", 4) == 0)
        status = atoi(cursor + 4);
    else {
        char *space = strchr(cursor, ' ');
        if (space) status = atoi(space + 1);
    }
    cursor = line_end + 1;
    while (cursor < (char *)s_work + header_size) {
        line_end = strchr(cursor, '\n');
        if (!line_end) break;
        *line_end = '\0';
        size_t length = strlen(cursor);
        if (length && cursor[length - 1] == '\r') cursor[length - 1] = '\0';
        char *colon = strchr(cursor, ':');
        if (colon) {
            *colon++ = '\0';
            while (*colon == ' ' || *colon == '\t') ++colon;
            if (strcasecmp(cursor, "icy-metaint") == 0)
                *metadata_interval = strtoul(colon, NULL, 10);
            else if (strcasecmp(cursor, "icy-br") == 0)
                *bitrate = strtoul(colon, NULL, 10);
            else if (strcasecmp(cursor, "location") == 0) {
                strncpy(redirect, colon, redirect_size - 1);
                redirect[redirect_size - 1] = '\0';
            }
        }
        cursor = line_end + 1;
    }
    return status;
}

static int open_http_stream(char *url, http_stream_t *stream) {
    for (unsigned redirect_count = 0;
         redirect_count <= HTTP_MAX_REDIRECTS; ++redirect_count) {
        uint16_t port;
        const char *path;
        if (!parse_http_url(url, &port, &path)) return -1;
        int socket_fd = connect_http(port);
        if (socket_fd < 0) return -2;
        char host_header[112];
        snprintf(host_header, sizeof(host_header), "Host: %s\r\n", s_host);
        bool sent = send_all(socket_fd, "GET ") &&
                    send_all(socket_fd, path) &&
                    send_all(socket_fd, " HTTP/1.1\r\n") &&
                    send_all(socket_fd, host_header) &&
                    send_all(socket_fd, "User-Agent: yoRadio-esp8266/1\r\n") &&
                    send_all(socket_fd, "Icy-MetaData: 1\r\n") &&
                    send_all(socket_fd, "Connection: close\r\n\r\n");
        if (!sent) {
            close(socket_fd);
            return -3;
        }
        size_t received_total = 0;
        size_t header_size = 0;
        int64_t header_deadline =
            esp_timer_get_time() + HTTP_HEADER_TIMEOUT_MS * 1000LL;
        while (received_total < sizeof(s_work) - 1U &&
               !find_header_end(s_work, received_total, &header_size)) {
            int received = recv(socket_fd, s_work + received_total,
                                sizeof(s_work) - 1U - received_total, 0);
            if (received > 0) {
                received_total += (size_t)received;
                continue;
            }
            if (received < 0 &&
                (errno == EAGAIN || errno == EWOULDBLOCK) &&
                esp_timer_get_time() < header_deadline) {
                continue;
            }
            if (received <= 0) {
                close(socket_fd);
                return -4;
            }
        }
        if (!header_size)
            find_header_end(s_work, received_total, &header_size);
        if (!header_size) {
            close(socket_fd);
            return -5;
        }
        char redirect_url[AUDIO_URL_BYTES];
        redirect_url[0] = '\0';
        uint32_t metadata_interval = 0;
        uint32_t bitrate = 0;
        int status = parse_headers(header_size, redirect_url,
                                   sizeof(redirect_url), &metadata_interval,
                                   &bitrate);
        size_t body_size = received_total - header_size;
        memmove(s_work, s_work + header_size, body_size);
        if (status >= 200 && status < 300) {
            stream->socket = socket_fd;
            stream->body_size = body_size;
            stream->metadata_interval = metadata_interval;
            stream->advertised_bitrate = bitrate;
            ESP_LOGI(TAG, "Stream response %d, ICY interval %u", status,
                     (unsigned)metadata_interval);
            return 0;
        }
        close(socket_fd);
        if ((status != 301 && status != 302 && status != 303 &&
             status != 307 && status != 308) || !redirect_url[0] ||
            redirect_count == HTTP_MAX_REDIRECTS) return -6;
        if (redirect_url[0] == '/') {
            char relative[AUDIO_URL_BYTES];
            size_t needed = 7U + strlen(s_host) + strlen(redirect_url) + 1U;
            if (needed > sizeof(relative)) return -7;
            strcpy(relative, "http://");
            strcat(relative, s_host);
            strcat(relative, redirect_url);
            memcpy(url, relative, needed);
        } else {
            size_t needed = strlen(redirect_url) + 1U;
            if (needed > AUDIO_URL_BYTES) return -7;
            memcpy(url, redirect_url, needed);
        }
        if (strncmp(url, "http://", 7) != 0) return -7;
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

static bool pcm_output(void *opaque, const helix_stream_info_t *info,
                       int16_t *pcm, size_t samples) {
    output_context_t *context = (output_context_t *)opaque;
    if (!generation_current(context->generation)) return false;
    esp_err_t result = native_audio_output_write(
        pcm, samples, info->sample_rate, info->channels);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "PCM output failed: %s",
                 esp_err_to_name(result));
        return false;
    }
    context->decoder_bitrate = info->bitrate;
    native_state_set_stream(context->codec_kind == HELIX_CODEC_MP3
                                ? CODEC_HELIX_MP3 : CODEC_HELIX_AAC,
                            (info->bitrate + 500U) / 1000U,
                            info->sample_rate, info->channels);
    return true;
}

static void read_icy_metadata(int socket_fd, uint32_t generation) {
    uint8_t blocks = 0;
    int result = recv(socket_fd, &blocks, 1, 0);
    if (result != 1) return;
    size_t remaining = (size_t)blocks * 16U;
    size_t retained = 0;
    uint8_t discard[64];
    while (remaining && generation_current(generation)) {
        size_t available = sizeof(s_work) - 1U - retained;
        uint8_t *destination = available ? s_work + retained : discard;
        size_t capacity = available ? available : sizeof(discard);
        size_t chunk = remaining > capacity ? capacity : remaining;
        int received = recv(socket_fd, destination, chunk, 0);
        if (received <= 0) return;
        if (available) retained += (size_t)received;
        remaining -= (size_t)received;
    }
    if (retained) parse_icy_title(retained);
}

static void audio_task(void *argument) {
    (void)argument;
    helix_codec_t *codec = NULL;
    helix_codec_kind_t codec_kind = 0;
    while (true) {
        audio_command_t command;
        xQueueReceive(s_commands, &command, portMAX_DELAY);
        if (!command.play) {
            native_audio_output_silence();
            helix_codec_destroy(codec);
            codec = NULL;
            codec_kind = 0;
            native_state_set_audio(false, false, NULL);
            network_service_set_streaming(false);
            continue;
        }
        native_state_set_audio(false, true, NULL);
        network_service_set_streaming(true);
        http_stream_t stream;
        memset(&stream, 0, sizeof(stream));
        stream.socket = -1;
        int opened = -1;
        for (unsigned attempt = 0;
             attempt < HTTP_OPEN_ATTEMPTS &&
             generation_current(command.generation); ++attempt) {
            opened = open_http_stream(command.url, &stream);
            if (opened == 0) break;
            if (attempt + 1U < HTTP_OPEN_ATTEMPTS) {
                ESP_LOGW(TAG, "Stream open attempt %u failed: %d",
                         attempt + 1U, opened);
                vTaskDelay(pdMS_TO_TICKS(250U));
            }
        }
        if (opened != 0 || !generation_current(command.generation)) {
            if (stream.socket >= 0) close(stream.socket);
            if (generation_current(command.generation)) {
                ESP_LOGW(TAG, "Open stream failed: %d (errno %d)",
                         opened, errno);
                native_state_set_audio(false, false,
                    opened == -7 ? "HTTPS NOT SUPPORTED" : "CONNECTION ERROR");
                network_service_set_streaming(false);
            }
            continue;
        }

        size_t detect_size = stream.body_size;
        uint32_t audio_until_metadata = stream.metadata_interval;
        if (audio_until_metadata && detect_size <= audio_until_metadata)
            audio_until_metadata -= (uint32_t)detect_size;
        while (generation_current(command.generation) &&
               !(codec_kind = helix_codec_detect(s_work, detect_size))) {
            if (detect_size == sizeof(s_work)) break;
            if (stream.metadata_interval && !audio_until_metadata) break;
            size_t wanted = sizeof(s_work) - detect_size;
            if (audio_until_metadata && wanted > audio_until_metadata)
                wanted = audio_until_metadata;
            int received = recv(stream.socket, s_work + detect_size, wanted, 0);
            if (received > 0) {
                detect_size += (size_t)received;
                if (stream.metadata_interval)
                    audio_until_metadata -= (uint32_t)received;
            } else if (errno != EAGAIN && errno != EWOULDBLOCK) {
                break;
            }
        }
        if (!codec_kind || !generation_current(command.generation)) {
            close(stream.socket);
            if (generation_current(command.generation))
                native_state_set_audio(false, false, "UNSUPPORTED STREAM");
            continue;
        }
        bool decoder_ready = true;
        if (!codec) {
            codec = helix_codec_create(codec_kind, CODEC_HEAP_RESERVE_BYTES);
            decoder_ready = codec != NULL;
        } else {
            decoder_ready = helix_codec_switch(codec, codec_kind) == 0;
        }
        if (!decoder_ready) {
            close(stream.socket);
            native_state_set_audio(false, false, "DECODER INIT ERROR");
            network_service_set_streaming(false);
            continue;
        }
        output_context_t output = {
            .generation = command.generation,
            .codec_kind = codec_kind,
            .measured_started_us = esp_timer_get_time(),
        };
        native_state_set_stream(codec_kind == HELIX_CODEC_MP3
                                    ? CODEC_HELIX_MP3 : CODEC_HELIX_AAC,
                                stream.advertised_bitrate, 0, 0);
        int feed = helix_codec_feed(codec, s_work, detect_size, false,
                                    pcm_output, &output);
        native_state_set_audio(true, false, NULL);
        while (feed == 0 && generation_current(command.generation)) {
            if (stream.metadata_interval && !audio_until_metadata) {
                read_icy_metadata(stream.socket, command.generation);
                audio_until_metadata = stream.metadata_interval;
                continue;
            }
            size_t capacity = 0;
            uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
            if (!destination || !capacity) {
                feed = -20;
                break;
            }
            size_t wanted = capacity > 1024U ? 1024U : capacity;
            if (stream.metadata_interval && wanted > audio_until_metadata)
                wanted = audio_until_metadata;
            int received = recv(stream.socket, destination, wanted, 0);
            if (received > 0) {
                output.measured_bytes += (uint32_t)received;
                if (stream.metadata_interval)
                    audio_until_metadata -= (uint32_t)received;
                feed = helix_codec_commit(codec, (size_t)received,
                                          pcm_output, &output);
                int64_t now = esp_timer_get_time();
                if (!output.decoder_bitrate &&
                    now - output.measured_started_us >= 3000000) {
                    uint32_t kbps = (uint32_t)(output.measured_bytes * 8000ULL /
                                              (uint64_t)(now - output.measured_started_us));
                    native_state_set_stream(codec_kind == HELIX_CODEC_MP3
                                                ? CODEC_HELIX_MP3 : CODEC_HELIX_AAC,
                                            kbps, 0, 0);
                    output.measured_bytes = 0;
                    output.measured_started_us = now;
                }
            } else if (received == 0) {
                break;
            } else if (errno != EAGAIN && errno != EWOULDBLOCK) {
                feed = -21;
                break;
            }
        }
        close(stream.socket);
        if (generation_current(command.generation)) {
            native_audio_output_silence();
            if (feed < 0)
                ESP_LOGE(TAG, "Decoder stopped: %d (errno %d)",
                         feed, errno);
            helix_codec_destroy(codec);
            codec = NULL;
            codec_kind = 0;
            native_state_set_audio(false, false,
                                   feed < 0 ? "AUDIO STREAM ERROR" : NULL);
            network_service_set_streaming(false);
        }
    }
}

esp_err_t audio_service_init(void) {
    s_commands = xQueueCreate(1, sizeof(audio_command_t));
    if (!s_commands) return ESP_ERR_NO_MEM;
    if (xTaskCreate(audio_task, "audio", AUDIO_STACK_BYTES, NULL, 5, NULL) !=
        pdPASS) return ESP_ERR_NO_MEM;
    ESP_LOGI(TAG, "Workspace %u bytes; required heap reserve %u bytes",
             (unsigned)helix_codec_workspace_size(),
             (unsigned)CODEC_HEAP_RESERVE_BYTES);
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
