#include "spiffs_log.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "esp_log.h"
#include "esp_spiffs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LOG_FLUSH_MS 1000U
#define LOG_RETRY_MS 30000U
#define LOG_WRITE_BYTES 256U
#define LOG_FREE_RESERVE_BYTES 8192U

/* No task, mutex, malloc, FILE buffering or per-line stack buffer. The SDK
 * serializes log callbacks. Critical sections below also protect the
 * app-task writer, but never contain filesystem or UART operations. */
static char s_queue[SPIFFS_LOG_QUEUE_BYTES];
static uint16_t s_head, s_count;
static uint32_t s_dropped, s_reported_dropped, s_io_errors;
static bool s_installed, s_mounted, s_low_space, s_storage_fault;
static TaskHandle_t s_io_owner;
static TickType_t s_last_poll;
static uint32_t s_interval_ms = LOG_FLUSH_MS;
static putchar_like_t s_previous = putchar;

static void count_drop(void) {
    if (s_dropped != UINT32_MAX) ++s_dropped;
}

static void queue_char(int ch) {
    taskENTER_CRITICAL();
    if (s_count == sizeof(s_queue) ||
        (s_io_owner && s_io_owner == xTaskGetCurrentTaskHandle())) {
        count_drop(); /* Recursive SPIFFS errors must not log themselves. */
    } else {
        s_queue[(s_head + s_count) % sizeof(s_queue)] = (char)ch;
        ++s_count;
    }
    taskEXIT_CRITICAL();
}

static int log_putchar(int ch) {
    queue_char(ch);
    return s_previous(ch); /* Preserve UART and its original return value. */
}

void spiffs_log_init(void) {
    if (s_installed) return; /* Never chain our own hook recursively. */
    s_installed = true;
    s_previous = esp_log_set_putchar(log_putchar);
    static const char marker[] = "\n--- SPIFFS log: application start ---\n";
    for (unsigned i = 0; i < sizeof(marker) - 1U; ++i) queue_char(marker[i]);
}

void spiffs_log_mount_ready(void) { s_mounted = true; }

void spiffs_log_get_status(spiffs_log_status_t *status) {
    taskENTER_CRITICAL();
    *status = (spiffs_log_status_t){s_dropped, s_io_errors, s_count, s_low_space, s_storage_fault};
    taskEXIT_CRITICAL();
}

/* App-task only. Only the two named log files can be rotated/deleted. */
static bool rotate_if_needed(size_t length) {
    struct stat st;
    if (stat(SPIFFS_LOG_PATH, &st) != 0) return errno == ENOENT;
    if (st.st_size >= 0 && (size_t)st.st_size + length <= SPIFFS_LOG_FILE_BYTES)
        return true;
    if (unlink(SPIFFS_LOG_PREVIOUS_PATH) != 0 && errno != ENOENT) return false;
    return rename(SPIFFS_LOG_PATH, SPIFFS_LOG_PREVIOUS_PATH) == 0;
}

void spiffs_log_poll(void) {
    TickType_t now = xTaskGetTickCount();
    if (!s_mounted || s_storage_fault ||
        (TickType_t)(now - s_last_poll) < pdMS_TO_TICKS(s_interval_ms))
        return;
    taskENTER_CRITICAL();
    if (s_io_owner || (!s_count && s_dropped == s_reported_dropped)) {
        taskEXIT_CRITICAL();
        return;
    }
    s_io_owner = xTaskGetCurrentTaskHandle();
    uint32_t dropped = s_dropped;
    taskEXIT_CRITICAL();
    s_last_poll = now;

    /* Report lost bytes once room is available, not recursively through SDK. */
    if (dropped != s_reported_dropped) {
        char marker[64];
        int n = snprintf(marker, sizeof(marker), "\n[spiffs-log: dropped %u bytes total]\n",
                         (unsigned)dropped);
        taskENTER_CRITICAL();
        if (n > 0 && (size_t)n < sizeof(marker) &&
            (size_t)n <= sizeof(s_queue) - s_count) {
            for (int i = 0; i < n; ++i)
                s_queue[(s_head + s_count++) % sizeof(s_queue)] = marker[i];
            s_reported_dropped = dropped;
        }
        taskEXIT_CRITICAL();
    }

    size_t total = 0, used = 0;
    bool failed = esp_spiffs_info("spiffs", &total, &used) != ESP_OK;
    bool low_space = !failed && (used > total || used > total - total / 4U ||
        total - used < LOG_FREE_RESERVE_BYTES + LOG_WRITE_BYTES);
    size_t written = 0;
    bool close_fault = false;
    if (!failed && !low_space) {
        taskENTER_CRITICAL();
        size_t length = s_count;
        if (length > sizeof(s_queue) - s_head) length = sizeof(s_queue) - s_head;
        if (length > LOG_WRITE_BYTES) length = LOG_WRITE_BYTES;
        uint16_t head = s_head;
        taskEXIT_CRITICAL();
        if (length) {
            if (!rotate_if_needed(length)) failed = true;
            else {
                int fd = open(SPIFFS_LOG_PATH, O_WRONLY | O_CREAT | O_APPEND, 0600);
                if (fd < 0) failed = true;
                else {
                    /* Producers cannot overwrite this occupied queue span.
                     * Close after every block flushes the SPIFFS file cache. */
                    ssize_t n = write(fd, s_queue + head, length);
                    if (n > 0) written = (size_t)n;
                    if (n < 0 || (size_t)n != length) failed = true;
                    if (close(fd) != 0) {
                        failed = true;
                        /* SDK VFS discards its fd even when SPIFFS cache flush
                         * fails before returning the internal file handle.
                         * Never retry this fd or open more leaked handles. */
                        close_fault = true;
                    }
                }
            }
        }
    }
    taskENTER_CRITICAL();
    s_head = (uint16_t)((s_head + written) % sizeof(s_queue));
    s_count = (uint16_t)(s_count - written);
    s_low_space = low_space;
    s_storage_fault |= close_fault;
    if (failed && s_io_errors != UINT32_MAX) ++s_io_errors;
    s_io_owner = NULL;
    taskEXIT_CRITICAL();
    s_interval_ms = failed || low_space ? LOG_RETRY_MS : LOG_FLUSH_MS;
}
