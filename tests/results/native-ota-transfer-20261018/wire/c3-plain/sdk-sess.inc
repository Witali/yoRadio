void httpd_sess_free_ctx(void **ctx, httpd_free_ctx_fn_t free_fn)
{
    if ((!ctx) || (!*ctx)) {
        return;
    }
    if (free_fn) {
        free_fn(*ctx);
    } else {
        free(*ctx);
    }
    *ctx = NULL;
}
void httpd_sess_clear_ctx(struct sock_db *session)
{
    if ((!session) || ((!session->ctx) && (!session->transport_ctx))) {
        return;
    }

    // free user ctx
    if (session->ctx) {
        httpd_sess_free_ctx(&session->ctx, session->free_ctx);
        session->free_ctx = NULL;
    }

    // Free 'transport' context
    if (session->transport_ctx) {
        httpd_sess_free_ctx(&session->transport_ctx, session->free_transport_ctx);
        session->free_transport_ctx = NULL;
    }
}
void *httpd_sess_get_ctx(httpd_handle_t handle, int sockfd)
{
    struct sock_db *session = httpd_sess_get(handle, sockfd);
    if (!session) {
        return NULL;
    }

    // Check if the function has been called from inside a
    // request handler, in which case fetch the context from
    // the httpd_req_t structure
    struct httpd_data *hd = (struct httpd_data *) handle;
    if (hd->hd_req_aux.sd == session) {
        return hd->hd_req.sess_ctx;
    }
    return session->ctx;
}
void httpd_sess_set_ctx(httpd_handle_t handle, int sockfd, void *ctx, httpd_free_ctx_fn_t free_fn)
{
    struct sock_db *session = httpd_sess_get(handle, sockfd);
    if (!session) {
        return;
    }

    // Check if the function has been called from inside a
    // request handler, in which case set the context inside
    // the httpd_req_t structure
    struct httpd_data *hd = (struct httpd_data *) handle;
    if (hd->hd_req_aux.sd == session) {
        if (hd->hd_req.sess_ctx != ctx) {
            // Don't free previous context if it is in sockdb
            // as it will be freed inside httpd_req_cleanup()
            if (session->ctx != hd->hd_req.sess_ctx) {
                httpd_sess_free_ctx(&hd->hd_req.sess_ctx, hd->hd_req.free_ctx); // Free previous context
            }
            hd->hd_req.sess_ctx = ctx;
        }
        hd->hd_req.free_ctx = free_fn;
        return;
    }

    // Else set the context inside the sock_db structure
    if (session->ctx != ctx) {
        // Free previous context
        httpd_sess_free_ctx(&session->ctx, session->free_ctx);
        session->ctx = ctx;
    }
    session->free_ctx = free_fn;
}
void *httpd_sess_get_transport_ctx(httpd_handle_t handle, int sockfd)
{
    struct sock_db *session = httpd_sess_get(handle, sockfd);
    return session ? session->transport_ctx : NULL;
}
void httpd_sess_set_transport_ctx(httpd_handle_t handle, int sockfd, void *ctx, httpd_free_ctx_fn_t free_fn)
{
    struct sock_db *session = httpd_sess_get(handle, sockfd);
    if (!session) {
        return;
    }

    if (session->transport_ctx != ctx) {
        // Free previous transport context
        httpd_sess_free_ctx(&session->transport_ctx, session->free_transport_ctx);
        session->transport_ctx = ctx;
    }
    session->free_transport_ctx = free_fn;
}
void httpd_sess_delete(struct httpd_data *hd, struct sock_db *session)
{
    if ((!hd) || (!session) || (session->fd < 0)) {
        return;
    }

    ESP_LOGD(TAG, LOG_FMT("fd = %d"), session->fd);
    if (hd->config.enable_so_linger) {
        struct linger so_linger = {
            .l_onoff = true,
            .l_linger = hd->config.linger_timeout,
        };
        if (setsockopt(session->fd, SOL_SOCKET, SO_LINGER, &so_linger, sizeof(struct linger)) < 0) {
            ESP_LOGW(TAG, LOG_FMT("error enabling SO_LINGER (%d)"), errno);
        }
    }

    // Call close function if defined
    if (hd->config.close_fn) {
        hd->config.close_fn(hd, session->fd);
    } else {
        close(session->fd);
    }
    hd->http_server_state = HTTP_SERVER_EVENT_DISCONNECTED;
    esp_http_server_dispatch_event(HTTP_SERVER_EVENT_DISCONNECTED, &session->fd, sizeof(int));

    // clear all contexts
    httpd_sess_clear_ctx(session);

    // mark session slot as available
    session->fd = -1;

    // decrement number of sessions
    hd->hd_sd_active_count--;
    ESP_LOGD(TAG, LOG_FMT("active sockets: %d"), hd->hd_sd_active_count);
    if (!hd->hd_sd_active_count) {
        hd->lru_counter = 0;
    }
}
esp_err_t httpd_sess_process(struct httpd_data *hd, struct sock_db *session)
{
    if ((!hd) || (!session)) {
        return ESP_FAIL;
    }

    ESP_LOGD(TAG, LOG_FMT("httpd_req_new"));
    if (httpd_req_new(hd, session) != ESP_OK) {
        return ESP_FAIL;
    }
    ESP_LOGD(TAG, LOG_FMT("httpd_req_delete"));
    if (httpd_req_delete(hd) != ESP_OK) {
        return ESP_FAIL;
    }
    ESP_LOGD(TAG, LOG_FMT("success"));
    session->lru_counter = ++hd->lru_counter;
    return ESP_OK;
}
