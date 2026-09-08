#pragma once
#include <stdint.h>
#include <stdbool.h>
#include "esp_http_server.h"

/* Optional, HTTP-task-owned wall-time diagnostics. These are not CPU times. */
#if YORADIO_ESP8266_WEB_PROFILE
uint32_t httpd_trace_clock(void);
void httpd_trace_begin(void);
void httpd_trace_dispatch(uint32_t select_start, uint32_t select_end, bool readable);
void httpd_trace_request_begin(bool websocket);
void httpd_trace_index_begin(void);
bool httpd_trace_ws_begin(void);
void httpd_trace_ws_end(int result);
void httpd_trace_route(httpd_req_t *request);
void httpd_trace_end(int result);
void httpd_trace_send(uint32_t start, int result, int error);
void httpd_trace_wait(uint32_t start, int error, uint32_t sleep_budget_us);
void httpd_trace_read(uint32_t start);
void httpd_trace_recv(uint32_t start);
#else
static inline uint32_t httpd_trace_clock(void) { return 0; }
static inline void httpd_trace_begin(void) {}
static inline void httpd_trace_dispatch(uint32_t s, uint32_t e, bool r) { (void)s; (void)e; (void)r; }
static inline void httpd_trace_request_begin(bool w) { (void)w; }
static inline void httpd_trace_index_begin(void) {}
static inline bool httpd_trace_ws_begin(void) { return false; }
static inline void httpd_trace_ws_end(int r) { (void)r; }
static inline void httpd_trace_route(httpd_req_t *r) { (void)r; }
static inline void httpd_trace_end(int r) { (void)r; }
static inline void httpd_trace_send(uint32_t s, int r, int e) { (void)s; (void)r; (void)e; }
static inline void httpd_trace_wait(uint32_t s, int e, uint32_t b) { (void)s; (void)e; (void)b; }
static inline void httpd_trace_read(uint32_t s) { (void)s; }
static inline void httpd_trace_recv(uint32_t s) { (void)s; }
#endif
