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