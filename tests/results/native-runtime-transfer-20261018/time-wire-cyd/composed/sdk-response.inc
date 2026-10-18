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
esp_err_t httpd_resp_send_err(httpd_req_t *req, httpd_err_code_t error, const char *usr_msg)
{
    esp_err_t ret;
    const char *msg;
    const char *status;

    switch (error) {
    case HTTPD_501_METHOD_NOT_IMPLEMENTED:
        status = "501 Method Not Implemented";
        msg    = "Server does not support this method";
        break;
    case HTTPD_505_VERSION_NOT_SUPPORTED:
        status = "505 Version Not Supported";
        msg    = "HTTP version not supported by server";
        break;
    case HTTPD_400_BAD_REQUEST:
        status = "400 Bad Request";
        msg    = "Bad request syntax";
        break;
    case HTTPD_401_UNAUTHORIZED:
        status = "401 Unauthorized";
        msg    = "No permission -- see authorization schemes";
        break;
    case HTTPD_403_FORBIDDEN:
        status = "403 Forbidden";
        msg    = "Request forbidden -- authorization will not help";
        break;
    case HTTPD_404_NOT_FOUND:
        status = "404 Not Found";
        msg    = "Nothing matches the given URI";
        break;
    case HTTPD_405_METHOD_NOT_ALLOWED:
        status = "405 Method Not Allowed";
        msg    = "Specified method is invalid for this resource";
        break;
    case HTTPD_408_REQ_TIMEOUT:
        status = "408 Request Timeout";
        msg    = "Server closed this connection";
        break;
    case HTTPD_414_URI_TOO_LONG:
        status = "414 URI Too Long";
        msg    = "URI is too long";
        break;
    case HTTPD_411_LENGTH_REQUIRED:
        status = "411 Length Required";
        msg    = "Client must specify Content-Length";
        break;
    case HTTPD_413_CONTENT_TOO_LARGE:
        status = "413 Content Too Large";
        msg    = "Content is too large";
        break;
    case HTTPD_431_REQ_HDR_FIELDS_TOO_LARGE:
        status = "431 Request Header Fields Too Large";
        msg    = "Header fields are too long";
        break;
    case HTTPD_500_INTERNAL_SERVER_ERROR:
    default:
        status = "500 Internal Server Error";
        msg    = "Server has encountered an unexpected error";
    }

    /* If user has provided custom message, override default message */
    msg = usr_msg ? usr_msg : msg;
    ESP_LOGW(TAG, LOG_FMT("%s - %s"), status, msg);

    /* Set error code in HTTP response */
    httpd_resp_set_status(req, status);
    httpd_resp_set_type(req, HTTPD_TYPE_TEXT);

#ifdef CONFIG_HTTPD_ERR_RESP_NO_DELAY
    /* Use TCP_NODELAY option to force socket to send data in buffer
     * This ensures that the error message is sent before the socket
     * is closed */
    struct httpd_req_aux *ra = req->aux;
    int nodelay = 1;
    if (setsockopt(ra->sd->fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        /* If failed to turn on TCP_NODELAY, throw warning and continue */
        ESP_LOGW(TAG, LOG_FMT("error calling setsockopt : %d"), errno);
        nodelay = 0;
    }
#endif

    /* Send HTTP error message */
    ret = httpd_resp_send(req, msg, HTTPD_RESP_USE_STRLEN);

#ifdef CONFIG_HTTPD_ERR_RESP_NO_DELAY
    /* If TCP_NODELAY was set successfully above, time to disable it */
    if (nodelay == 1) {
        nodelay = 0;
        if (setsockopt(ra->sd->fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
            /* If failed to turn off TCP_NODELAY, throw error and
             * return failure to signal for socket closure */
            ESP_LOGE(TAG, LOG_FMT("error calling setsockopt : %d"), errno);
            return ESP_ERR_INVALID_STATE;
        }
    }
#endif
    esp_http_server_dispatch_event(HTTP_SERVER_EVENT_ERROR, &error, sizeof(httpd_err_code_t));

    return ret;
}
esp_err_t httpd_resp_send_custom_err(httpd_req_t *req, const char *status, const char *msg)
{
    ESP_LOGW(TAG, LOG_FMT("%s - %s"), status, msg);

    /* Set error code in HTTP response */
    httpd_resp_set_status(req, status);
    httpd_resp_set_type(req, HTTPD_TYPE_TEXT);

#ifdef CONFIG_HTTPD_ERR_RESP_NO_DELAY
    /* Use TCP_NODELAY option to force socket to send data in buffer
     * This ensures that the error message is sent before the socket
     * is closed */
    struct httpd_req_aux *ra = req->aux;
    int nodelay = 1;
    if (setsockopt(ra->sd->fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        /* If failed to turn on TCP_NODELAY, throw warning and continue */
        ESP_LOGW(TAG, LOG_FMT("error calling setsockopt : %d"), errno);
        nodelay = 0;
    }
#endif

    /* Send HTTP error message */
    esp_err_t ret = httpd_resp_send(req, msg, HTTPD_RESP_USE_STRLEN);

#ifdef CONFIG_HTTPD_ERR_RESP_NO_DELAY
    /* If TCP_NODELAY was set successfully above, time to disable it */
    if (nodelay == 1) {
        nodelay = 0;
        if (setsockopt(ra->sd->fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
            /* If failed to turn off TCP_NODELAY, throw error and
             * return failure to signal for socket closure */
            ESP_LOGE(TAG, LOG_FMT("error calling setsockopt : %d"), errno);
            return ESP_ERR_INVALID_STATE;
        }
    }
#endif
    return ret;
}
esp_err_t httpd_req_handle_err(httpd_req_t *req, httpd_err_code_t error)
{
    struct httpd_data *hd = (struct httpd_data *) req->handle;
    esp_err_t ret;

    /* Invoke custom error handler if configured */
    if (hd->err_handler_fns[error]) {
        ret = hd->err_handler_fns[error](req, error);

        /* If error code is 500, force return failure
         * irrespective of the handler's return value */
        ret = (error == HTTPD_500_INTERNAL_SERVER_ERROR ? ESP_FAIL : ret);
    } else {
        /* If no handler is registered for this error default
         * behavior is to send the HTTP error response and
         * return failure for closure of underlying socket */
        httpd_resp_send_err(req, error, NULL);
        ret = ESP_FAIL;
    }
    return ret;
}
