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
static esp_err_t httpd_send_all(httpd_req_t *r, const char *buf, size_t buf_len)
{
    struct httpd_req_aux *ra = r->aux;
    int ret;

    while (buf_len > 0) {
        ret = ra->sd->send_fn(ra->sd->handle, ra->sd->fd, buf, buf_len, 0);
        if (ret < 0) {
            ESP_LOGD(TAG, LOG_FMT("error in send_fn"));
            return ESP_FAIL;
        }
        ESP_LOGD(TAG, LOG_FMT("sent = %d"), ret);
        buf     += ret;
        buf_len -= ret;
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
int httpd_recv_with_opt(httpd_req_t *r, char *buf, size_t buf_len, httpd_recv_opt_t opt)
{
    ESP_LOGD(TAG, LOG_FMT("requested length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(buf_len));

    size_t pending_len = 0;
    struct httpd_req_aux *ra = r->aux;

    /* First fetch pending data from local buffer */
    if (ra->sd->pending_len > 0) {
        ESP_LOGD(TAG, LOG_FMT("pending length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(ra->sd->pending_len));
        pending_len = httpd_recv_pending(r, buf, buf_len);
        buf     += pending_len;
        buf_len -= pending_len;

        /* If buffer filled then no need to recv.
         * If asked to halt after receiving pending data then
         * return with received length */
        if (!buf_len || opt == HTTPD_RECV_OPT_HALT_AFTER_PENDING) {
            return pending_len;
        }
    }

    /* Receive data of remaining length */
    size_t recv_len = pending_len;
    do {
        int ret = ra->sd->recv_fn(ra->sd->handle, ra->sd->fd, buf, buf_len, 0);
        if (ret <= 0) {
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

        recv_len += ret;
        buf      += ret;
        buf_len  -= ret;
    } while (buf_len > 0 && opt == HTTPD_RECV_OPT_BLOCKING);

    ESP_LOGD(TAG, LOG_FMT("received length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(recv_len));
    return recv_len;
}
int httpd_recv(httpd_req_t *r, char *buf, size_t buf_len)
{
    return httpd_recv_with_opt(r, buf, buf_len, HTTPD_RECV_OPT_NONE);
}
size_t httpd_unrecv(struct httpd_req *r, const char *buf, size_t buf_len)
{
    struct httpd_req_aux *ra = r->aux;
    /* Truncate if external buf_len is greater than pending_data buffer size */
    ra->sd->pending_len = MIN(sizeof(ra->sd->pending_data), buf_len);

    /* Copy data into internal pending_data buffer with the exact offset
     * such that it is right aligned inside the buffer */
    size_t offset = sizeof(ra->sd->pending_data) - ra->sd->pending_len;
    memcpy(ra->sd->pending_data + offset, buf, ra->sd->pending_len);
    ESP_LOGD(TAG, LOG_FMT("length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(ra->sd->pending_len));
    return ra->sd->pending_len;
}
esp_err_t httpd_resp_set_hdr(httpd_req_t *r, const char *field, const char *value)
{
    if (r == NULL || field == NULL || value == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    /* Reject CRLF in header field or value */
    if (strpbrk(field, "\r\n") || strpbrk(value, "\r\n")) {
        ESP_LOGW(TAG, LOG_FMT("rejecting header with CRLF: %.32s"), field);
        return ESP_ERR_INVALID_ARG;
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
esp_err_t httpd_resp_set_status(httpd_req_t *r, const char *status)
{
    if (r == NULL || status == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    /* Reject CRLF in status */
    if (strpbrk(status, "\r\n")) {
        ESP_LOGW(TAG, LOG_FMT("rejecting status with CRLF: %.32s"), status);
        return ESP_ERR_INVALID_ARG;
    }

    struct httpd_req_aux *ra = r->aux;
    ra->status = (char *)status;
    return ESP_OK;
}
esp_err_t httpd_resp_set_type(httpd_req_t *r, const char *type)
{
    if (r == NULL || type == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    /* Reject CRLF in content type */
    if (strpbrk(type, "\r\n")) {
        ESP_LOGW(TAG, LOG_FMT("rejecting content type with CRLF: %.32s"), type);
        return ESP_ERR_INVALID_ARG;
    }

    struct httpd_req_aux *ra = r->aux;
    ra->content_type = (char *)type;
    return ESP_OK;
}
esp_err_t httpd_resp_send(httpd_req_t *r, const char *buf, ssize_t buf_len)
{
    if (r == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    struct httpd_req_aux *ra = r->aux;
    const char *httpd_hdr_str = "HTTP/1.1 %s\r\nContent-Type: %s\r\nContent-Length: %d\r\n";
    const char *colon_separator = ": ";
    const char *cr_lf_seperator = "\r\n";

    if (buf_len == HTTPD_RESP_USE_STRLEN) {
        buf_len = strlen(buf);
    }

    /* Request headers are no longer available */
    ra->req_hdrs_count = 0;

    /* Calculate the size of the headers. +1 for the null terminator */
    size_t required_size = snprintf(NULL, 0, httpd_hdr_str, ra->status, ra->content_type, buf_len) + 1;
    if (required_size > ra->max_req_hdr_len) {
        return ESP_ERR_HTTPD_RESP_HDR;
    }
    char *res_buf = malloc(required_size); /* Temporary buffer to store the headers */
    if (res_buf == NULL) {
        ESP_LOGE(TAG, "Unable to allocate httpd send buffer");
        return ESP_ERR_HTTPD_ALLOC_MEM;
    }

    esp_err_t ret = snprintf(res_buf, required_size, httpd_hdr_str, ra->status, ra->content_type, buf_len);
    if (ret < 0 || ret >= required_size) {
        free(res_buf);
        return ESP_ERR_HTTPD_RESP_HDR;
    }
    ESP_LOGD(TAG, "httpd send buffer size = %d", strlen(res_buf));
    ret = httpd_send_all(r, res_buf, strlen(res_buf));
    free(res_buf);
    if (ret != ESP_OK) {
        return ESP_ERR_HTTPD_RESP_SEND;
    }

    /* Sending additional headers based on set_header */
    for (unsigned i = 0; i < ra->resp_hdrs_count; i++) {
        /* Send header field */
        if (httpd_send_all(r, ra->resp_hdrs[i].field, strlen(ra->resp_hdrs[i].field)) != ESP_OK) {
            return ESP_ERR_HTTPD_RESP_SEND;
        }
        /* Send ': ' */
        if (httpd_send_all(r, colon_separator, strlen(colon_separator)) != ESP_OK) {
            return ESP_ERR_HTTPD_RESP_SEND;
        }
        /* Send header value */
        if (httpd_send_all(r, ra->resp_hdrs[i].value, strlen(ra->resp_hdrs[i].value)) != ESP_OK) {
            return ESP_ERR_HTTPD_RESP_SEND;
        }
        /* Send CR + LF */
        if (httpd_send_all(r, cr_lf_seperator, strlen(cr_lf_seperator)) != ESP_OK) {
            return ESP_ERR_HTTPD_RESP_SEND;
        }
    }

    /* End header section */
    if (httpd_send_all(r, cr_lf_seperator, strlen(cr_lf_seperator)) != ESP_OK) {
        return ESP_ERR_HTTPD_RESP_SEND;
    }
    struct httpd_data *hd = (struct httpd_data *) r->handle;
    hd->http_server_state = HTTP_SERVER_EVENT_HEADERS_SENT;
    esp_http_server_dispatch_event(HTTP_SERVER_EVENT_HEADERS_SENT, &(ra->sd->fd), sizeof(int));

    /* Sending content */
    if (buf && buf_len) {
        if (httpd_send_all(r, buf, buf_len) != ESP_OK) {
            return ESP_ERR_HTTPD_RESP_SEND;
        }
    }
    esp_http_server_event_data evt_data = {
        .fd = ra->sd->fd,
        .data_len = buf_len,
    };
    hd->http_server_state = HTTP_SERVER_EVENT_SENT_DATA;
    esp_http_server_dispatch_event(HTTP_SERVER_EVENT_SENT_DATA, &evt_data, sizeof(esp_http_server_event_data));
    return ESP_OK;
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
    ESP_LOGD(TAG, LOG_FMT("remaining length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(ra->remaining_len));

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
    struct httpd_data *hd = (struct httpd_data *) r->handle;
    hd->http_server_state = HTTP_SERVER_EVENT_ON_DATA;
    esp_http_server_event_data evt_data = {
        .fd = ra->sd->fd,
        .data_len = ret,
    };
    esp_http_server_dispatch_event(HTTP_SERVER_EVENT_ON_DATA, &evt_data, sizeof(esp_http_server_event_data));
    return ret;
}
