static void httpd_req_cleanup(httpd_req_t *r)
{
    struct httpd_req_aux *ra = r->aux;

    /* Check if the context has changed and needs to be cleared */
    if ((r->ignore_sess_ctx_changes == false) && (ra->sd->ctx != r->sess_ctx)) {
        httpd_sess_free_ctx(&ra->sd->ctx, ra->sd->free_ctx);
    }

#if CONFIG_HTTPD_WS_SUPPORT
    /* Close the socket when a WebSocket Close request is received */
    if (ra->sd->ws_close) {
        ESP_LOGD(TAG, LOG_FMT("Try closing WS connection at FD: %d"), ra->sd->fd);
        httpd_sess_trigger_close(r->handle, ra->sd->fd);
    }
#endif

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
