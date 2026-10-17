#include "web.h"
#include "esp_timer.h"
#include "lwip/sockets.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BODY_READ_BUDGET_US INT64_C(5000000)

static char *reject_body(httpd_req_t *req, char *body)
{
    /* Stop reads before returning a 400 response. IDF otherwise tries to purge
     * an unread Content-Length after the handler and blocks other sessions again.
     * Leave the write side open so the caller can still send the error response. */
    int socket = httpd_req_to_sockfd(req);
    if (socket >= 0)
        shutdown(socket, SHUT_RD);
    free(body);
    return NULL;
}

char *web_body(httpd_req_t *req, size_t max_length)
{
    /* Read one bounded same-origin request within a shared five-second budget.
     * FIXED_RECONSTRUCTION: three full receive retries, followed by IDF's unread
     * body purge, let one partial JSON hold unrelated clients for over 24 seconds.
     * Progress must not reset the deadline; valid fragmented bodies still work. */
    size_t origin_length = httpd_req_get_hdr_value_len(req, "Origin");
    if (origin_length)
    {
        char origin[160], host[128], expected[160];
        if (origin_length >= sizeof(origin) ||
            httpd_req_get_hdr_value_str(req, "Origin", origin, sizeof(origin)) != ESP_OK ||
            httpd_req_get_hdr_value_str(req, "Host", host, sizeof(host)) != ESP_OK)
            return reject_body(req, NULL);
        snprintf(expected, sizeof(expected), "http://%s", host);
        if (strcmp(origin, expected))
            return reject_body(req, NULL);
    }
    if (req->content_len == 0 || req->content_len > max_length)
        return reject_body(req, NULL);

    int socket = httpd_req_to_sockfd(req);
    struct timeval original_timeout;
    socklen_t timeout_size = sizeof(original_timeout);
    if (socket < 0 || getsockopt(socket, SOL_SOCKET, SO_RCVTIMEO,
                                &original_timeout, &timeout_size) != 0 ||
        timeout_size != sizeof(original_timeout))
        return reject_body(req, NULL);

    char *body = malloc(req->content_len + 1);
    if (!body)
        return reject_body(req, NULL);
    int64_t deadline = esp_timer_get_time() + BODY_READ_BUDGET_US;
    size_t received = 0;
    while (received < req->content_len)
    {
        int64_t remaining = deadline - esp_timer_get_time();
        if (remaining <= 0)
            return reject_body(req, body);
        /* lwIP converts timeval to whole milliseconds, with zero meaning no
         * timeout. Round up so the final sub-millisecond budget cannot disable it. */
        int64_t milliseconds = (remaining + 999) / 1000;
        struct timeval timeout = {.tv_sec = (long)(milliseconds / 1000),
                                  .tv_usec = (long)(milliseconds % 1000) * 1000};
        if (setsockopt(socket, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) != 0)
            return reject_body(req, body);
        int bytes = httpd_req_recv(req, body + received, req->content_len - received);
        if (bytes <= 0 || esp_timer_get_time() > deadline)
            return reject_body(req, body);
        received += (size_t)bytes;
    }
    /* A keep-alive session must retain its original header/next-request timeout. */
    if (setsockopt(socket, SOL_SOCKET, SO_RCVTIMEO,
                   &original_timeout, sizeof(original_timeout)) != 0)
        return reject_body(req, body);
    body[received] = 0;
    return body;
}
