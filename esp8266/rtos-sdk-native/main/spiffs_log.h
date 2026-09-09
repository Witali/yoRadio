#pragma once

#include <stdbool.h>
#include <stdint.h>

#if YORADIO_ESP8266_SPIFFS_LOG
#define SPIFFS_LOG_PATH "/spiffs/log/current.txt"
#define SPIFFS_LOG_PREVIOUS_PATH "/spiffs/log/previous.txt"
#define SPIFFS_LOG_QUEUE_BYTES 512U
#define SPIFFS_LOG_FILE_BYTES 8192U

typedef struct {
    uint32_t dropped_bytes;
    uint32_t io_errors;
    uint16_t pending_bytes;
    bool low_space;
    bool storage_fault;
} spiffs_log_status_t;

void spiffs_log_init(void);
void spiffs_log_mount_ready(void);
void spiffs_log_poll(void);
void spiffs_log_get_status(spiffs_log_status_t *status);
#else
static inline void spiffs_log_init(void) {}
static inline void spiffs_log_mount_ready(void) {}
static inline void spiffs_log_poll(void) {}
#endif
