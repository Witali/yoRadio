static void httpd_sess_close(void *arg)
{
    struct sock_db *sock_db = (struct sock_db *) arg;
    if (!sock_db) {
        return;
    }

    if (!sock_db->lru_counter && !sock_db->lru_socket) {
        ESP_LOGD(TAG, "Skipping session close for %d as it seems to be a race condition", sock_db->fd);
        return;
    }
    sock_db->lru_socket = false;
    struct httpd_data *hd = (struct httpd_data *) sock_db->handle;
    hd->http_server_state = HTTP_SERVER_EVENT_DISCONNECTED;
    httpd_sess_delete(hd, sock_db);
}
esp_err_t httpd_sess_trigger_close_(httpd_handle_t handle, struct sock_db *session)
{
    if (!session) {
        return ESP_ERR_NOT_FOUND;
    }
    return httpd_queue_work(handle, httpd_sess_close, session);
}
esp_err_t httpd_sess_trigger_close(httpd_handle_t handle, int sockfd)
{
    struct sock_db *session = httpd_sess_get(handle, sockfd);
    if (!session) {
        return ESP_ERR_NOT_FOUND;
    }
    return httpd_sess_trigger_close_(handle, session);
}
static void httpd_req_cleanup(httpd_req_t *r)
{
    struct httpd_req_aux *ra = r->aux;

    /* Check if the context has changed and needs to be cleared */
    if ((r->ignore_sess_ctx_changes == false) && (ra->sd->ctx != r->sess_ctx)) {
        httpd_sess_free_ctx(&ra->sd->ctx, ra->sd->free_ctx);
    }

    /* Closing WebSocket sessions are returned to the owning HTTPD loop
     * by httpd_req_new/httpd_req_delete. No deferred session-pointer close. */

    /* Retrieve session info from the request into the socket database. */
    ra->sd->ctx = r->sess_ctx;
    ra->sd->free_ctx = r->free_ctx;
    ra->sd->ignore_sess_ctx_changes = r->ignore_sess_ctx_changes;

    /* Clear out the request and request_aux structures */
    ra->sd = NULL;
    free(ra->scratch);
    ra->scratch = NULL;
    ra->scratch_size_limit = 0;
    ra->scratch_cur_size = 0;
    r->handle = NULL;
    r->aux = NULL;
    r->user_ctx = NULL;
}