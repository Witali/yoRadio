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
