#pragma once
#include "esp32c3_ota_mock.h"
typedef void *SemaphoreHandle_t;
typedef void *TaskHandle_t;
typedef struct { size_t content_len; } httpd_req_t;
#define pdTRUE 1
#define pdPASS 1
#define portMAX_DELAY 0xffffffff
#define pdMS_TO_TICKS(ms) (ms)
#define HTTPD_SOCK_ERR_TIMEOUT -3
int httpd_req_get_hdr_value_str(httpd_req_t *, const char *, char *, size_t);
int httpd_req_recv(httpd_req_t *, char *, size_t);
int httpd_resp_set_type(httpd_req_t *, const char *);
int httpd_resp_set_status(httpd_req_t *, const char *);
int httpd_resp_set_hdr(httpd_req_t *, const char *, const char *);
int httpd_resp_sendstr(httpd_req_t *, const char *);
int64_t esp_timer_get_time(void);
void esp_restart(void);
void esp_app_get_elf_sha256(char *, size_t);
void ulTaskNotifyTake(int, unsigned);
void vTaskDelay(unsigned);
int xTaskCreate(void (*)(void *), const char *, unsigned, void *, unsigned, TaskHandle_t *);
void vTaskDelete(TaskHandle_t);
void xTaskNotifyGive(TaskHandle_t);
int httpd_req_to_sockfd(httpd_req_t *);
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
