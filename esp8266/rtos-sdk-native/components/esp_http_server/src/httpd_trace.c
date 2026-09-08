#include "httpd_trace.h"
#include "esp_timer.h"
#include "esp_system.h"
#include "esp_log.h"
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

/* One synchronous request at a time. No ring allocation or packet logging. */
static struct {
    uint32_t start, parse_us, send_us, recv_us, read_us;
    uint32_t tx_wait_us, mem_wait_us, other_wait_us, bytes, calls, retries;
    uint32_t tx_sleep_budget_us;
    uint32_t max_send_us;
    unsigned mem_errors;
    char id[24], path[64];
    bool active;
} trace;
static uint32_t boot_id, sequence;

uint32_t httpd_trace_clock(void) {
    int saved_errno = errno;
    uint32_t now = (uint32_t)esp_timer_get_time();
    errno = saved_errno;
    return now;
}
void httpd_trace_begin(void) {
    if (!sequence) boot_id = esp_random();
    memset(&trace, 0, sizeof(trace));
    snprintf(trace.id, sizeof(trace.id), "%08x-%u", (unsigned)boot_id, (unsigned)++sequence);
    trace.active = true;
    trace.start = httpd_trace_clock();
}
void httpd_trace_route(httpd_req_t *request) {
    if (!trace.active) return;
    trace.parse_us = httpd_trace_clock() - trace.start;
    /* No query, headers, credentials, WebSocket payloads or file contents. */
    size_t i = 0;
    while (i + 1 < sizeof(trace.path) && request->uri[i] && request->uri[i] != '?') {
        unsigned char c = (unsigned char)request->uri[i];
        trace.path[i++] = c >= 32 && c < 127 && c != '"' && c != '\\' ? (char)c : '_';
    }
    (void)httpd_resp_set_hdr(request, "X-YoRadio-Trace", trace.id);
}
void httpd_trace_send(uint32_t start, int result, int error) {
    if (!trace.active) return;
    uint32_t elapsed = httpd_trace_clock() - start;
    trace.send_us += elapsed; ++trace.calls;
    if (elapsed > trace.max_send_us) trace.max_send_us = elapsed;
    if (result > 0) trace.bytes += (uint32_t)result;
    else if (error == ENOMEM || error == ENOBUFS) ++trace.mem_errors;
}
void httpd_trace_wait(uint32_t start, int error, uint32_t sleep_budget_us) {
    if (!trace.active) return;
    uint32_t elapsed = httpd_trace_clock() - start;
    if (error == EAGAIN || error == EWOULDBLOCK) {
        trace.tx_wait_us += elapsed;
        /* Do not attribute late rescheduling after vTaskDelay to the network. */
        trace.tx_sleep_budget_us += elapsed < sleep_budget_us ? elapsed : sleep_budget_us;
    }
    else if (error == ENOMEM || error == ENOBUFS) trace.mem_wait_us += elapsed;
    else trace.other_wait_us += elapsed;
    ++trace.retries;
}
void httpd_trace_read(uint32_t start) {
    if (trace.active) trace.read_us += httpd_trace_clock() - start;
}
void httpd_trace_recv(uint32_t start) {
    if (trace.active) trace.recv_us += httpd_trace_clock() - start;
}
void httpd_trace_end(int result) {
    if (!trace.active) return;
    uint32_t total = httpd_trace_clock() - trace.start;
    trace.active = false;
    /* Logging happens after the handler. Its UART cost is outside total_us
     * but can delay the next request: compare a non-profiled image as well. */
    if (trace.path[0]) ESP_LOGI("http_trace",
        "WEBTRACE {\"id\":\"%s\",\"path\":\"%s\",\"start_us\":%u,\"total_us\":%u,"
        "\"parse_us\":%u,\"read_us\":%u,\"recv_us\":%u,\"send_us\":%u,\"max_send_us\":%u,"
        "\"tx_wait_us\":%u,\"tx_sleep_budget_us\":%u,\"mem_wait_us\":%u,\"other_wait_us\":%u,"
        "\"mem_errors\":%u,\"retries\":%u,\"bytes\":%u,\"calls\":%u,\"result\":%d}",
        trace.id, trace.path, (unsigned)trace.start, (unsigned)total,
        (unsigned)trace.parse_us, (unsigned)trace.read_us, (unsigned)trace.recv_us,
        (unsigned)trace.send_us, (unsigned)trace.max_send_us, (unsigned)trace.tx_wait_us,
        (unsigned)trace.tx_sleep_budget_us, (unsigned)trace.mem_wait_us, (unsigned)trace.other_wait_us, trace.mem_errors,
        (unsigned)trace.retries, (unsigned)trace.bytes, (unsigned)trace.calls, result);
}
