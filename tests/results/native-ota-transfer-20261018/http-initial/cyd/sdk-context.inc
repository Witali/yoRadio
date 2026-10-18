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
