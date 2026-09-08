// Copyright 2018 Espressif Systems (Shanghai) PTE LTD
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <esp_log.h>
#include <esp_err.h>

#include <esp_http_server.h>
#include "esp_httpd_priv.h"
#include "httpd_trace.h"

static const char *TAG = "httpd_txrx";
#ifdef CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS
#define HTTPD_SEND_RETRY_TIMEOUT_MS \
    (CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS * 1000U)
#else
#define HTTPD_SEND_RETRY_TIMEOUT_MS 15000U
#endif

esp_err_t httpd_sess_set_send_override(httpd_handle_t hd, int sockfd, httpd_send_func_t send_func)
{
    struct sock_db *sess = httpd_sess_get(hd, sockfd);
    if (!sess) {
        return ESP_ERR_INVALID_ARG;
    }
    sess->send_fn = send_func;
    return ESP_OK;
}

esp_err_t httpd_sess_set_recv_override(httpd_handle_t hd, int sockfd, httpd_recv_func_t recv_func)
{
    struct sock_db *sess = httpd_sess_get(hd, sockfd);
    if (!sess) {
        return ESP_ERR_INVALID_ARG;
    }
    sess->recv_fn = recv_func;
    return ESP_OK;
}

esp_err_t httpd_sess_set_pending_override(httpd_handle_t hd, int sockfd, httpd_pending_func_t pending_func)
{
    struct sock_db *sess = httpd_sess_get(hd, sockfd);
    if (!sess) {
        return ESP_ERR_INVALID_ARG;
    }
    sess->pending_fn = pending_func;
    return ESP_OK;
}

int httpd_send(httpd_req_t *r, const char *buf, size_t buf_len)
{
    if (r == NULL || buf == NULL) {
        return HTTPD_SOCK_ERR_INVALID;
    }

    if (!httpd_valid_req(r)) {
        return HTTPD_SOCK_ERR_INVALID;
    }

    struct httpd_req_aux *ra = r->aux;
    int ret = ra->sd->send_fn(ra->sd->handle, ra->sd->fd, buf, buf_len, 0);
    if (ret < 0) {
        ESP_LOGD(TAG, LOG_FMT("error in send_fn"));
        return ret;
    }
    return ret;
}

static esp_err_t httpd_send_all(httpd_req_t *r, const char *buf, size_t buf_len)
{
    struct httpd_req_aux *ra = r->aux;
    if (!ra->send_started) {
        ra->send_started = true;
        ra->send_deadline = xTaskGetTickCount() +
                            pdMS_TO_TICKS(HTTPD_SEND_RETRY_TIMEOUT_MS);
    }
    TickType_t deadline = ra->send_deadline;

    while (buf_len > 0) {
        if ((int32_t)(deadline - xTaskGetTickCount()) <= 0) {
            ESP_LOGW(TAG, LOG_FMT("response send deadline, fd=%d"), ra->sd->fd);
            return ESP_FAIL;
        }
        uint32_t trace_start = httpd_trace_clock();
        int ret = ra->sd->send_fn(ra->sd->handle, ra->sd->fd, buf, buf_len,
                                  MSG_DONTWAIT);
        int send_errno = ret < 0 ? errno : 0;
        httpd_trace_send(trace_start, ret, send_errno);
        if (ret > 0) {
            ESP_LOGD(TAG, LOG_FMT("sent = %d"), ret);
            buf += ret;
            buf_len -= (size_t)ret;
            continue;
        }
        bool retryable = ret == HTTPD_SOCK_ERR_TIMEOUT ||
                         (ret < 0 && (send_errno == EAGAIN ||
                                     send_errno == EWOULDBLOCK ||
                                     send_errno == EINTR ||
                                     send_errno == ENOMEM ||
                                     send_errno == ENOBUFS));
        if (retryable &&
            (int32_t)(deadline - xTaskGetTickCount()) > 0) {
            trace_start = httpd_trace_clock();
            vTaskDelay(pdMS_TO_TICKS(1));
            httpd_trace_wait(trace_start, send_errno,
                pdMS_TO_TICKS(1) * portTICK_PERIOD_MS * 1000U);
            continue;
        }
        ESP_LOGD(TAG, LOG_FMT("error in send_fn: ret=%d errno=%d"),
                 ret, errno);
        return ESP_FAIL;
    }
    return ESP_OK;
}
static size_t httpd_recv_pending(httpd_req_t *r, char *buf, size_t buf_len)
{
    struct httpd_req_aux *ra = r->aux;
    size_t offset = sizeof(ra->sd->pending_data) - ra->sd->pending_len;

    /* buf_len must not be greater than remaining_len */
    buf_len = MIN(ra->sd->pending_len, buf_len);
    memcpy(buf, ra->sd->pending_data + offset, buf_len);

    ra->sd->pending_len -= buf_len;
    return buf_len;
}

int httpd_recv_with_opt(httpd_req_t *r, char *buf, size_t buf_len, bool halt_after_pending)
{
    ESP_LOGD(TAG, LOG_FMT("requested length = %d"), buf_len);

    size_t pending_len = 0;
    struct httpd_req_aux *ra = r->aux;

    /* First fetch pending data from local buffer */
    if (ra->sd->pending_len > 0) {
        ESP_LOGD(TAG, LOG_FMT("pending length = %d"), ra->sd->pending_len);
        pending_len = httpd_recv_pending(r, buf, buf_len);
        buf     += pending_len;
        buf_len -= pending_len;

        /* If buffer filled then no need to recv.
         * If asked to halt after receiving pending data then
         * return with received length */
        if (!buf_len || halt_after_pending) {
            return pending_len;
        }
    }

    /* Receive data of remaining length */
    uint32_t trace_start = httpd_trace_clock();
    int ret = ra->sd->recv_fn(ra->sd->handle, ra->sd->fd, buf, buf_len, 0);
    httpd_trace_recv(trace_start);
    if (ret < 0) {
        ESP_LOGD(TAG, LOG_FMT("error in recv_fn"));
        if ((ret == HTTPD_SOCK_ERR_TIMEOUT) && (pending_len != 0)) {
            /* If recv() timeout occurred, but pending data is
             * present, return length of pending data.
             * This behavior is similar to that of socket recv()
             * function, which, in case has only partially read the
             * requested length, due to timeout, returns with read
             * length, rather than error */
            return pending_len;
        }
        return ret;
    }

    ESP_LOGD(TAG, LOG_FMT("received length = %d"), ret + pending_len);
    return ret + pending_len;
}

int httpd_recv(httpd_req_t *r, char *buf, size_t buf_len)
{
    return httpd_recv_with_opt(r, buf, buf_len, false);
}

static void httpd_async_wakeup(void *argument)
{
    (void)argument;
}

esp_err_t httpd_req_async_handler_begin(httpd_req_t *r, httpd_req_t **out)
{
    if (r == NULL || out == NULL || r->aux == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    struct httpd_req_aux *r_aux = r->aux;
    if (r_aux->sd == NULL || r_aux->sd->for_async_req) {
        return ESP_ERR_INVALID_STATE;
    }

    httpd_req_t *async = malloc(sizeof(*async));
    if (async == NULL) {
        return ESP_ERR_NO_MEM;
    }
    memcpy(async, r, sizeof(*async));

    struct httpd_req_aux *async_aux = malloc(sizeof(*async_aux));
    if (async_aux == NULL) {
        free(async);
        return ESP_ERR_NO_MEM;
    }
    memcpy(async_aux, r_aux, sizeof(*async_aux));

    struct httpd_data *hd = (struct httpd_data *)r->handle;
    async_aux->resp_hdrs =
        calloc(hd->config.max_resp_headers, sizeof(struct resp_hdr));
    if (async_aux->resp_hdrs == NULL) {
        free(async_aux);
        free(async);
        return ESP_ERR_NO_MEM;
    }
    memcpy(async_aux->resp_hdrs, r_aux->resp_hdrs,
           hd->config.max_resp_headers * sizeof(struct resp_hdr));
    async->aux = async_aux;

    r_aux->remaining_len = 0;
    r_aux->sd->for_async_req = true;
    *out = async;
    return ESP_OK;
}

esp_err_t httpd_req_async_handler_complete(httpd_req_t *r)
{
    if (r == NULL || r->handle == NULL || r->aux == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    httpd_handle_t handle = r->handle;
    struct httpd_req_aux *ra = r->aux;
    if (ra->sd == NULL || !ra->sd->for_async_req) {
        return ESP_ERR_INVALID_STATE;
    }

    ra->sd->for_async_req = false;
    free(ra->resp_hdrs);
    free(ra);
    free(r);

    return httpd_queue_work(handle, httpd_async_wakeup, NULL);
}

size_t httpd_unrecv(struct httpd_req *r, const char *buf, size_t buf_len)
{
    struct httpd_req_aux *ra = r->aux;
    /* Truncate if external buf_len is greater than pending_data buffer size */
    ra->sd->pending_len = MIN(sizeof(ra->sd->pending_data), buf_len);

    /* Copy data into internal pending_data buffer */
    size_t offset = sizeof(ra->sd->pending_data) - ra->sd->pending_len;
    memcpy(ra->sd->pending_data + offset, buf, buf_len);
    ESP_LOGD(TAG, LOG_FMT("length = %d"), ra->sd->pending_len);
    return ra->sd->pending_len;
}

/**
 * This API appends an additional header field-value pair in the HTTP response.
 * But the header isn't sent out until any of the send APIs is executed.
 */
esp_err_t httpd_resp_set_hdr(httpd_req_t *r, const char *field, const char *value)
{
    if (r == NULL || field == NULL || value == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    struct httpd_req_aux *ra = r->aux;
    struct httpd_data *hd = (struct httpd_data *) r->handle;

    /* Number of additional headers is limited */
    if (ra->resp_hdrs_count >= hd->config.max_resp_headers) {
        return ESP_ERR_HTTPD_RESP_HDR;
    }

    /* Assign header field-value pair */
    ra->resp_hdrs[ra->resp_hdrs_count].field = field;
    ra->resp_hdrs[ra->resp_hdrs_count].value = value;
    ra->resp_hdrs_count++;

    ESP_LOGD(TAG, LOG_FMT("new header = %s: %s"), field, value);
    return ESP_OK;
}

/**
 * This API sets the status of the HTTP response to the value specified.
 * But the status isn't sent out until any of the send APIs is executed.
 */
esp_err_t httpd_resp_set_status(httpd_req_t *r, const char *status)
{
    if (r == NULL || status == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    struct httpd_req_aux *ra = r->aux;
    ra->status = (char *)status;
    return ESP_OK;
}

/**
 * This API sets the method/type of the HTTP response to the value specified.
 * But the method isn't sent out until any of the send APIs is executed.
 */
esp_err_t httpd_resp_set_type(httpd_req_t *r, const char *type)
{
    if (r == NULL || type == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    struct httpd_req_aux *ra = r->aux;
    ra->content_type = (char *)type;
    return ESP_OK;
}

/* Coalesce headers and small chunks in the existing request scratch buffer.
 * With TCP_NODELAY, separate 2-byte writes exhaust lwIP's segment queue and
 * spend more airtime on framing than on the actual payload. No new buffer. */
static esp_err_t httpd_send_headers(httpd_req_t *r, bool chunked, ssize_t length)
{
    struct httpd_req_aux *ra = r->aux;
    ra->req_hdrs_count = 0;
    int n = snprintf(ra->scratch, sizeof(ra->scratch),
                     "HTTP/1.1 %s\r\nContent-Type: %s\r\n",
                     ra->status, ra->content_type);
    if (n < 0 || (size_t)n >= sizeof(ra->scratch)) return ESP_ERR_HTTPD_RESP_HDR;
    size_t used = (size_t)n;
    n = chunked
        ? snprintf(ra->scratch + used, sizeof(ra->scratch) - used,
                   "Transfer-Encoding: chunked\r\n")
        : snprintf(ra->scratch + used, sizeof(ra->scratch) - used,
                   "Content-Length: %d\r\n", (int)length);
    if (n < 0 || (size_t)n >= sizeof(ra->scratch) - used) return ESP_ERR_HTTPD_RESP_HDR;
    used += (size_t)n;
    for (unsigned i = 0; i < ra->resp_hdrs_count; ++i) {
        n = snprintf(ra->scratch + used, sizeof(ra->scratch) - used,
                     "%s: %s\r\n", ra->resp_hdrs[i].field, ra->resp_hdrs[i].value);
        if (n < 0 || (size_t)n >= sizeof(ra->scratch) - used) return ESP_ERR_HTTPD_RESP_HDR;
        used += (size_t)n;
    }
    if (sizeof(ra->scratch) - used < 2U) return ESP_ERR_HTTPD_RESP_HDR;
    memcpy(ra->scratch + used, "\r\n", 2);
    return httpd_send_all(r, ra->scratch, used + 2U) == ESP_OK
               ? ESP_OK : ESP_ERR_HTTPD_RESP_SEND;
}

esp_err_t httpd_resp_send(httpd_req_t *r, const char *buf, ssize_t buf_len)
{
    if (!r) return ESP_ERR_INVALID_ARG;
    if (!httpd_valid_req(r)) return ESP_ERR_HTTPD_INVALID_REQ;
    if (buf_len == -1 && buf) buf_len = strlen(buf);
    if (buf_len < 0 || (!buf && buf_len)) return ESP_ERR_INVALID_ARG;
    esp_err_t result = httpd_send_headers(r, false, buf_len);
    if (result != ESP_OK) return result;
    /* Stage fixed-length bodies through the existing aligned HTTP workspace.
     * In particular, ESP8266 XIP assets must not be passed straight into lwIP
     * byte copies. Bound each send without allocating the complete body. */
    struct httpd_req_aux *ra = r->aux;
    char *stage = (char *)(((uintptr_t)ra->scratch + 3U) & ~(uintptr_t)3U);
    size_t capacity = (sizeof(ra->scratch) - (size_t)(stage - ra->scratch)) & ~(size_t)3U;
    if (capacity > 1024U) capacity = 1024U;
    while (buf_len > 0) {
        size_t n = (size_t)buf_len < capacity ? (size_t)buf_len : capacity;
        memcpy(stage, buf, n);
        if (httpd_send_all(r, stage, n) != ESP_OK)
            return ESP_ERR_HTTPD_RESP_SEND;
        buf += n;
        buf_len -= (ssize_t)n;
    }
    return ESP_OK;
}

esp_err_t httpd_resp_send_chunk(httpd_req_t *r, const char *buf, ssize_t buf_len)
{
    if (!r) return ESP_ERR_INVALID_ARG;
    if (!httpd_valid_req(r)) return ESP_ERR_HTTPD_INVALID_REQ;
    if (buf_len == -1 && buf) buf_len = strlen(buf);
    if (buf_len < 0 || (!buf && buf_len)) return ESP_ERR_INVALID_ARG;
    struct httpd_req_aux *ra = r->aux;
    if (!ra->first_chunk_sent) {
        esp_err_t result = httpd_send_headers(r, true, 0);
        if (result != ESP_OK) return result;
        ra->first_chunk_sent = true;
    }
    char len_str[2 * sizeof(size_t) + 4];
    int n = snprintf(len_str, sizeof(len_str), "%x\r\n", (unsigned)buf_len);
    size_t header = (size_t)n;
    if ((size_t)buf_len <= sizeof(ra->scratch) - header - 2U) {
        if (buf_len) memmove(ra->scratch + header, buf, (size_t)buf_len);
        memcpy(ra->scratch, len_str, header);
        memcpy(ra->scratch + header + buf_len, "\r\n", 2);
        return httpd_send_all(r, ra->scratch, header + buf_len + 2U) == ESP_OK
                   ? ESP_OK : ESP_ERR_HTTPD_RESP_SEND;
    }
    /* Preserve support for larger application chunks without allocating. */
    if (httpd_send_all(r, len_str, header) != ESP_OK ||
        httpd_send_all(r, buf, (size_t)buf_len) != ESP_OK ||
        httpd_send_all(r, "\r\n", 2) != ESP_OK)
        return ESP_ERR_HTTPD_RESP_SEND;
    return ESP_OK;
}

esp_err_t httpd_resp_send_404(httpd_req_t *r)
{
    return httpd_resp_send_err(r, HTTPD_404_NOT_FOUND);
}

esp_err_t httpd_resp_send_408(httpd_req_t *r)
{
    return httpd_resp_send_err(r, HTTPD_408_REQ_TIMEOUT);
}

esp_err_t httpd_resp_send_500(httpd_req_t *r)
{
    return httpd_resp_send_err(r, HTTPD_500_SERVER_ERROR);
}

esp_err_t httpd_resp_send_err(httpd_req_t *req, httpd_err_resp_t error)
{
    const char *msg;
    const char *status;
    switch (error) {
    case HTTPD_501_METHOD_NOT_IMPLEMENTED:
        status = "501 Method Not Implemented";
        msg    = "Request method is not supported by server";
        break;
    case HTTPD_505_VERSION_NOT_SUPPORTED:
        status = "505 Version Not Supported";
        msg    = "HTTP version not supported by server";
        break;
    case HTTPD_400_BAD_REQUEST:
        status = "400 Bad Request";
        msg    = "Server unable to understand request due to invalid syntax";
        break;
    case HTTPD_404_NOT_FOUND:
        status = "404 Not Found";
        msg    = "This URI doesn't exist";
        break;
    case HTTPD_405_METHOD_NOT_ALLOWED:
        status = "405 Method Not Allowed";
        msg    = "Request method for this URI is not handled by server";
        break;
    case HTTPD_408_REQ_TIMEOUT:
        status = "408 Request Timeout";
        msg    = "Server closed this connection";
        break;
    case HTTPD_414_URI_TOO_LONG:
        status = "414 URI Too Long";
        msg    = "URI is too long for server to interpret";
        break;
    case HTTPD_411_LENGTH_REQUIRED:
        status = "411 Length Required";
        msg    = "Chunked encoding not supported by server";
        break;
    case HTTPD_431_REQ_HDR_FIELDS_TOO_LARGE:
        status = "431 Request Header Fields Too Large";
        msg    = "Header fields are too long for server to interpret";
        break;
    case HTTPD_XXX_UPGRADE_NOT_SUPPORTED:
        /* If the server does not support upgrade, or is unable to upgrade
         * it responds with a standard HTTP/1.1 response */
        status = "200 OK";
        msg    = "Upgrade not supported by server";
        break;
    case HTTPD_500_SERVER_ERROR:
    default:
        status = "500 Server Error";
        msg    = "Server has encountered an unexpected error";
    }
    ESP_LOGW(TAG, LOG_FMT("%s - %s"), status, msg);

    httpd_resp_set_status   (req, status);
    httpd_resp_set_type     (req, HTTPD_TYPE_TEXT);
    return httpd_resp_send  (req, msg, strlen(msg));
}

int httpd_req_recv(httpd_req_t *r, char *buf, size_t buf_len)
{
    if (r == NULL || buf == NULL) {
        return HTTPD_SOCK_ERR_INVALID;
    }

    if (!httpd_valid_req(r)) {
        ESP_LOGW(TAG, LOG_FMT("invalid request"));
        return HTTPD_SOCK_ERR_INVALID;
    }

    struct httpd_req_aux *ra = r->aux;
    ESP_LOGD(TAG, LOG_FMT("remaining length = %d"), ra->remaining_len);

    if (buf_len > ra->remaining_len) {
        buf_len = ra->remaining_len;
    }
    if (buf_len == 0) {
        return buf_len;
    }

    int ret = httpd_recv(r, buf, buf_len);
    if (ret < 0) {
        ESP_LOGD(TAG, LOG_FMT("error in httpd_recv"));
        return ret;
    }
    ra->remaining_len -= ret;
    ESP_LOGD(TAG, LOG_FMT("received length = %d"), ret);
    return ret;
}

int httpd_req_to_sockfd(httpd_req_t *r)
{
    if (r == NULL) {
        return -1;
    }

    if (!httpd_valid_req(r)) {
        ESP_LOGW(TAG, LOG_FMT("invalid request"));
        return -1;
    }

    struct httpd_req_aux *ra = r->aux;
    return ra->sd->fd;
}

static int httpd_sock_err(const char *ctx, int sockfd)
{
    int errval;
    int sock_err;
    size_t sock_err_len = sizeof(sock_err);

    if (getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &sock_err, &sock_err_len) < 0) {
        ESP_LOGE(TAG, LOG_FMT("error calling getsockopt : %d"), errno);
        return HTTPD_SOCK_ERR_FAIL;
    }
    ESP_LOGW(TAG, LOG_FMT("error in %s : %d"), ctx, sock_err);

    switch(sock_err) {
    case EAGAIN:
    case EINTR:
        errval = HTTPD_SOCK_ERR_TIMEOUT;
        break;
    case EINVAL:
    case EBADF:
    case EFAULT:
    case ENOTSOCK:
        errval = HTTPD_SOCK_ERR_INVALID;
        break;
    default:
        errval = HTTPD_SOCK_ERR_FAIL;
    }
    return errval;
}

int httpd_default_send(httpd_handle_t hd, int sockfd, const char *buf, size_t buf_len, int flags)
{
    (void)hd;
    if (buf == NULL) {
        return HTTPD_SOCK_ERR_INVALID;
    }

    int ret = send(sockfd, buf, buf_len, flags);
    if (ret < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR ||
            errno == ENOMEM || errno == ENOBUFS) {
            return HTTPD_SOCK_ERR_TIMEOUT;
        }
        return httpd_sock_err("send", sockfd);
    }
    return ret;
}
int httpd_default_recv(httpd_handle_t hd, int sockfd, char *buf, size_t buf_len, int flags)
{
    (void)hd;
    if (buf == NULL) {
        return HTTPD_SOCK_ERR_INVALID;
    }

    int ret = recv(sockfd, buf, buf_len, flags);
    if (ret < 0) {
        return httpd_sock_err("recv", sockfd);
    }
    return ret;
}
